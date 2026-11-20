import pytest
from wooddessign.engineering.simple_beam import SimpleBeamRequest, evaluate_simple_beam
from test_nds2024 import fixture


def test_simple_beam_reactions_equilibrium_moment_and_deflection():
    material=fixture()['material']
    r=SimpleBeamRequest.model_validate(dict(method='ASD',duration='normal',span_in=120.,width_in=2.,depth_in=12.,
        beam_effective_length_in=120.,combination_udl_lbf_per_in=10.,total_sls_udl_lbf_per_in=8.,
        live_sls_udl_lbf_per_in=4.,bearing_length_in=3.,total_limit_divisor=240.,live_limit_divisor=360.,
        material=material,engineer_confirmed_inputs_and_factors=True))
    result=evaluate_simple_beam(r)
    assert result['analysis']['reaction_each_lbf']==600.
    assert result['analysis']['moment_max_lbf_in']==18000.
    assert result['analysis']['reaction_each_lbf']*2==1200.
    assert result['whole_member_status']=='not-checked'
    r.live_sls_udl_lbf_per_in=9.
    with pytest.raises(ValueError):evaluate_simple_beam(r)
