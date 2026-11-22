import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from wooddessign.api.app import app
from wooddessign.engineering.csa_o86_2024 import CanadianBeamRequest,evaluate_canadian_beam,sawn_bending_capacity

def payload():
    return dict(grade_category='visual_structural',country='CA',standard='CSA_O86_2024',unit_system='mm_N_MPa',width_mm=38.,depth_mm=235.,span_mm=3000.,bearing_length_mm=89.,factored_udl_kn_per_m=1.,dead_service_udl_kn_per_m=.2,live_service_udl_kn_per_m=.4,sustained_live_fraction=0.,duration='standard',fb_mpa=12.,fv_mpa=1.5,fcp_mpa=5.,e_mpa=10000.,material_designation='Synthetic test material',material_source='Arithmetic fixture only; not a grade table',live_limit_divisor=360.,total_limit_divisor=240.,dry_untreated_visually_graded=True,continuously_braced_single_member=True,no_notches_holes_or_composite_action=True,engineer_confirmed_inputs_and_factors=True)

def test_cwc2025_published_beam_example_bending_arithmetic():
    # Official additional example1 SPFNo2 38x235, KH1.4, KZ1.1.
    # Tests supplied KL arithmetic, not automatic unbraced/cantilever analysis.
    assert sawn_bending_capacity(38,235,11.8,kh=1.4,kz=1.1,kl=.583)==pytest.approx(3.33,abs=.02)
    assert sawn_bending_capacity(38,235,11.8,kh=1.4,kz=1.1,kl=.851)==pytest.approx(4.87,abs=.02)

def test_synthetic_uniform_beam_hand_arithmetic_and_creep():
    r=evaluate_canadian_beam(CanadianBeamRequest(**payload()))
    checks={x['check_id']:x for x in r['checks']}
    assert r['analysis']['moment_max_knm']==1.125
    assert r['analysis']['reaction_each_kn']==1.5
    assert checks['bending']['capacity']==pytest.approx(4.155129)
    assert checks['shear']['capacity']==pytest.approx(8.8407)
    assert checks['end_bearing_basic']['capacity']==pytest.approx(13.528)
    expected_live=5*.4*3000**4/(384*10000*(38*235**3/12))
    assert r['deflections']['live_immediate_mm']==pytest.approx(expected_live)
    assert r['deflections']['total_with_creep_mm']==pytest.approx(2*expected_live)
    assert r['parameters']['KL']==1 and r['parameters']['KH']==1
    assert r['whole_member_status']=='not-checked' and r['engineering_approval'] is False

@pytest.mark.parametrize('duration,dead,live,expected',[('standard',1.,.1,.65),('standard',.2,.1,.8494850021680094),('long_term',.2,.4,.65),('short_term',.2,.4,1.15),('standard',.2,0.,.65)])
def test_duration_combination_rules(duration,dead,live,expected):
    p={**payload(),'duration':duration,'dead_service_udl_kn_per_m':dead,'live_service_udl_kn_per_m':live}
    assert evaluate_canadian_beam(CanadianBeamRequest(**p))['parameters']['KD']==pytest.approx(expected)

@pytest.mark.parametrize('changes',[{'country':'US'},{'standard':'NDS_2024'},{'width_mm':89.},{'depth_mm':200.},{'width_mm':True},{'continuously_braced_single_member':False},{'e_mpa':float('nan')},{'sustained_live_fraction':1.01}])
def test_unsupported_scope_never_falls_back(changes):
    with pytest.raises((ValueError,ValidationError)):CanadianBeamRequest(**{**payload(),**changes})

def test_sustained_live_fraction_affects_creep():
    p=payload();p['sustained_live_fraction']=1.
    r=evaluate_canadian_beam(CanadianBeamRequest(**p))
    assert r['deflections']['total_with_creep_mm']==pytest.approx(2*(r['deflections']['dead_immediate_mm']+r['deflections']['live_immediate_mm']))

def test_country_gateway_gated_and_both_countries_dispatch(monkeypatch):
    client=TestClient(app)
    assert client.post('/api/v1/beam/check',json={}).status_code==401
    monkeypatch.setattr('wooddessign.api.tool_auth.verify_access',lambda _:(200,'test-verified'))
    r=client.post('/api/v1/beam/check',json=payload());assert r.status_code==200,r.text
    assert r.json()['country']=='CA'
    material=json.loads((Path(__file__).resolve().parents[1]/'examples/synthetic-member-check.json').read_text())['material']
    us=dict(country='US',standard='NDS_2024',unit_system='in_lbf_psi',method='ASD',duration='normal',span_in=120,width_in=2,depth_in=12,beam_effective_length_in=120,combination_udl_lbf_per_in=10,total_sls_udl_lbf_per_in=8,live_sls_udl_lbf_per_in=4,bearing_length_in=3,total_limit_divisor=240,live_limit_divisor=360,material=material,engineer_confirmed_inputs_and_factors=True)
    r=client.post('/api/v1/beam/check',json=us);assert r.status_code==200,r.text
    assert r.json()['country']=='US' and r.json()['analysis']['reaction_each_lbf']==600
    us['standard']='CSA_O86_2024'
    assert client.post('/api/v1/beam/check',json=us).status_code==422


def test_light_framing_never_receives_structural_size_increase():
    p=payload();p['grade_category']='light_framing'
    r=evaluate_canadian_beam(CanadianBeamRequest(**p))
    assert r['parameters']['KZb']==1 and r['parameters']['KZv']==1
    p.pop('grade_category')
    assert evaluate_canadian_beam(CanadianBeamRequest(**p))['parameters']['KZb']==1

def test_deepest_framing_requires_additional_blocking_confirmation():
    p=payload();p['depth_mm']=286.
    with pytest.raises(ValueError,match='bridging'):CanadianBeamRequest(**p)
    p['blocking_at_most_2280_mm']=True
    assert CanadianBeamRequest(**p).depth_mm==286
