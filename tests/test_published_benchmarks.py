"""Published Calcs.com resistance values; not full NDS-2024 verification.

The examples are explicitly NDS 2018. Adjusted material properties are inputs;
these tests do NOT infer unprinted grade or adjustment-factor chains.
"""
import pytest
from wooddessign.engineering.nds2024 import MemberRequest,check_member,adjusted_property
from test_nds2024 import fixture

URL="https://calcs.com/docs/calculators/us/beams/timberBeamLRFDNDS-2024"

def published_section(fb, fv, bearing):
    data=fixture()
    data.update(width_in=1.5,depth_in=5.5,net_tension_area_in2=8.25,bearing_net_area_in2=4.5,
                compression_edge_continuously_braced=True)
    data['actions'][0].update(compression_lbf=0.,moment_x_lbf_in=10000.)
    # Comparison at the adjusted-property boundary, not a grade database test.
    for key,value in [('Fb_x',fb),('Fv',fv),('Fc_perp',bearing)]:
        data['material'][key]['reference_psi']=value
        data['material'][key]['source']='Published adjusted-property boundary: '+URL
    return check_member(MemberRequest.model_validate(data))

def checks(r):return {x['check_id']:x for x in r['checks']}

def test_published_asd_example_6_18():
    r=published_section(1870.,225.,625.)
    # Published S=7.56 rounded; exact 1.5*5.5^2/6 = 7.5625.
    # Calcs moment1177.7 lbft and shear1237.5lbf; 0.1% rounding allowance.
    moment=checks(r)['bending_x']['capacity']*r['geometry']['Sx_in3']/12
    shear=checks(r)['shear']['capacity']*r['geometry']['area_in2']/1.5
    assert moment == pytest.approx(1177.7,rel=.001)
    assert shear == pytest.approx(1237.5,rel=1e-12)
    assert checks(r)['bearing']['capacity']==625.
    assert r['beam_stability']['CL']==1.
    assert r['whole_member_status']=='not-checked'

def test_published_lrfd_example_6_19_adjusted_boundary():
    # Source prints adjusted Fb=2582psi, Fv=311psi, bearing939psi.
    # Compare geometry/stress arithmetic, not a second LRFD factor application.
    r=published_section(2582.,311.,939.)
    moment=checks(r)['bending_x']['capacity']*r['geometry']['Sx_in3']/12
    shear=checks(r)['shear']['capacity']*r['geometry']['area_in2']/1.5
    assert moment==pytest.approx(1627.3,rel=.001)
    assert shear==pytest.approx(1710.,rel=.001)
    assert checks(r)['bearing']['capacity']==939.

def test_lrfd_shear_factor_chain_matches_published_adjusted_value():
    # Reference Fv=180 psi follows from printed ASD225 / CD1.25.
    assert adjusted_property(180.,'Fv',{},'LRFD','normal')['adjusted_psi']==pytest.approx(311.,abs=.05)

def test_continuous_bracing_override_cannot_hide_axial_instability():
    d=fixture(); d['compression_edge_continuously_braced']=True
    with pytest.raises(ValueError): MemberRequest.model_validate(d)
