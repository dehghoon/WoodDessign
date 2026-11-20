import math
from copy import deepcopy

import pytest
from pydantic import ValidationError

from wooddessign.engineering.nds2024 import (
    MemberRequest, adjusted_property, beam_stability, bearing_factor,
    check_member, column_axis, combined_compression,
)


def fixture():
    props = {key: {"reference_psi": value, "adjustments": {}, "source": "Independent test material, not a lumber catalog"}
             for key, value in {"Fb_x":1200., "Fb_y":1200., "Fv":150., "Fc":1000., "Ft":700., "Fc_perp":500., "E":1200000., "Emin":400000.}.items()}
    return {"standard":"NDS_2024", "method":"ASD", "unit_system":"in_lbf_psi", "member_type":"beam",
            "width_in":3.5, "depth_in":11.25, "net_tension_area_in2":39.375,
            "beam_effective_length_in":144., "column_effective_length_x_in":96., "column_effective_length_y_in":96.,
            "bearing_length_in":3., "bearing_net_area_in2":10.5, "bearing_distance_from_end_in":0., "bearing_is_interior":False,
            "duration":"normal", "material":{"designation":"test", "category":"sawn_lumber", **props},
            "actions":[{"case_id":"C1", "compression_lbf":2000., "tension_lbf":0., "moment_x_lbf_in":10000., "moment_y_lbf_in":0., "shear_lbf":1000., "bearing_reaction_lbf":1000.}],
            "serviceability":{"support_and_loading":"simply_supported_udl", "span_in":144., "total_udl_lbf_per_in":10., "live_udl_lbf_per_in":6., "total_limit_divisor":240., "live_limit_divisor":360.},
            "unnotched_prismatic":True, "connections_checked_separately":True, "no_composite_action_assumed":True,
            "minor_axis_restraint_verified":True}


def test_b_nds_01_06_07_geometry_stress_and_bearing():
    r = check_member(MemberRequest.model_validate(fixture()))
    assert r["geometry"]["area_in2"] == 39.375
    assert r["geometry"]["Sx_in3"] == 73.828125
    checks = {check["check_id"]:check for check in r["checks"]}
    assert checks["shear"]["demand"] == pytest.approx(38.095238095238095)
    assert checks["bearing"]["demand"] == pytest.approx(95.23809523809524)
    assert r["whole_member_status"] == "not-checked"
    assert r["engineering_approval"] is False


def test_b_nds_02_adjusted_stability_inputs_are_used():
    # Hand benchmark: r=FbE/Fb*=1 gives the smaller quadratic root
    # (1-sqrt(1-.95))/.95, with independently tabulated value below.
    b = beam_stability(2., 8., 60., 1200., 120000.)
    assert b["FbE_psi"] == pytest.approx(1200.)
    assert b["CL"] == pytest.approx(0.8172560023684432)
    assert b["Fb_adjusted_psi"] == pytest.approx(980.7072028421318)
    changed = beam_stability(2., 8., 60., 2400., 120000.)
    assert changed["CL"] < b["CL"]


def test_b_nds_03_column_polynomial_reference():
    # FcE=Fc*=1000; c=.8; independently solved smaller root.
    le = math.sqrt(.822 * 400000 / 1000) * 4
    result = column_axis(4., le, 1000., 400000.)
    assert result["FcE_psi"] == pytest.approx(1000.)
    assert result["Cp"] == pytest.approx(0.6909830056250525)


def test_b_nds_04_weak_axis_governs_even_with_same_effective_length():
    result = check_member(MemberRequest.model_validate(fixture()))
    x, y = result["column_axes"]
    assert y["slenderness"] > x["slenderness"]
    assert y["Fc_adjusted_psi"] < x["Fc_adjusted_psi"]
    assert result["column_governing_axis"] == "y"


def test_b_nds_05_interaction_hand_benchmark_and_instability_boundary():
    args = dict(fc=100., fcp=500., fbx=200., fby=100., fbxp=1000., fbyp=800., fce1=1000., fce2=800., fbe=2000.)
    value = combined_compression(**args)
    # .04 + .2/.9 + .125/.865
    assert value["utilization"] == pytest.approx(0.4067308927424534)
    assert value["status"] == "pass"
    args["fc"] = 1000.
    unstable = combined_compression(**args)
    assert unstable["status"] == "fail" and unstable["utilization"] is None
    assert unstable["reason"] == "INSTABILITY"


def test_b_nds_06_cb_only_for_eligible_interior_bearings():
    assert bearing_factor(3., 3., True) == 1.125
    assert bearing_factor(3., 2.999, True) == 1.
    assert bearing_factor(6., 3., True) == 1.
    assert bearing_factor(3., 3., False) == 1.
    with pytest.raises(ValueError): bearing_factor(0., 3., True)


def test_b_nds_08_simple_span_udl_closed_form():
    data = fixture();data["width_in"]=2.;data["depth_in"]=12.;data["net_tension_area_in2"]=24.;data["bearing_net_area_in2"]=6.
    data["material"]["E"]["reference_psi"] = 1000000.
    data["serviceability"].update(span_in=120.,total_udl_lbf_per_in=10.,live_udl_lbf_per_in=5.)
    r = check_member(MemberRequest.model_validate(data))
    # I=288 in4; independent beam-table reference delta=0.09375 in.
    assert r["deflections"]["total"]["deflection_in"] == pytest.approx(.09375, rel=1e-12)
    assert r["deflections"]["live"]["deflection_in"] == pytest.approx(.046875, rel=1e-12)


def test_b_nds_09_asd_and_lrfd_property_specific_factor_chains():
    assert adjusted_property(1000., "Fb", {"CM":.85}, "ASD", "10-min")["adjusted_psi"] == 1360.
    assert adjusted_property(1000., "Fc_perp", {}, "ASD", "impact")["adjusted_psi"] == 1000.
    assert adjusted_property(1000., "Fb", {}, "LRFD", "normal")["adjusted_psi"] == pytest.approx(1727.2)
    assert adjusted_property(1000., "Emin", {}, "LRFD", "permanent")["adjusted_psi"] == pytest.approx(1496.)
    assert adjusted_property(1000., "E", {}, "LRFD", "normal")["adjusted_psi"] == 1000.


@pytest.mark.parametrize("property_name,factor", [("Fc_perp","CD"),("Fv","CF"),("E","CL"),("Fb","unknown")])
def test_err_01_no_silent_factor_or_property_fallback(property_name, factor):
    with pytest.raises(ValueError): adjusted_property(1000., property_name, {factor:1.}, "ASD", "normal")


@pytest.mark.parametrize("duration",["earthquake", "unknown", ""])
def test_err_01_unknown_duration_rejected(duration):
    with pytest.raises(ValueError): adjusted_property(1000., "Fb", {}, "ASD", duration)


def test_slenderness_limits_are_invalid_without_extrapolation():
    assert beam_stability(1., 1., 2501., 1000., 400000.)["status"] == "invalid"
    assert column_axis(1., 50.001, 1000., 400000.)["status"] == "invalid"
    assert column_axis(1., 50., 1000., 400000.)["status"] == "checked"


@pytest.mark.parametrize("change", [
    {"width_in":True}, {"width_in":float("nan")}, {"standard":"CSA_O86_2024"},
    {"width_in":20., "depth_in":2.}, {"net_tension_area_in2":1000.}, {"serviceability":None}, {"unnotched_prismatic":False},
])
def test_request_rejects_unsupported_or_missing_inputs(change):
    data = fixture(); data.update(change)
    with pytest.raises(ValidationError): MemberRequest.model_validate(data)


def test_overcapacity_is_not_rounded_into_a_pass():
    data=fixture();data["actions"][0]["shear_lbf"]=data["width_in"]*data["depth_in"]*150./1.5*(1+1e-10)
    result=check_member(MemberRequest.model_validate(data))
    assert next(x for x in result["checks"] if x["check_id"]=="shear")["status"] == "fail"


def test_duplicate_cases_and_simultaneous_axial_signs_are_rejected():
    data=fixture();data["actions"].append(deepcopy(data["actions"][0]))
    with pytest.raises(ValidationError): MemberRequest.model_validate(data)
    data=fixture();data["actions"][0]["tension_lbf"]=1.
    with pytest.raises(ValidationError): MemberRequest.model_validate(data)


def test_stiff_stability_limit_does_not_lose_precision_or_overflow():
    from wooddessign.engineering.nds2024 import stability_ratio
    assert stability_ratio(1e200, 1000., .95) == pytest.approx(1.)
    assert stability_ratio(1e-100, 1000., .8) > 0
