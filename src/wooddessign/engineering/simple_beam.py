"""Explicit simply supported prismatic beam under a full-span UDL."""
from typing import Literal

from pydantic import Field
from .nds2024 import Model, Material, MemberRequest, check_member


class SimpleBeamRequest(Model):
    method: Literal["ASD", "LRFD"]
    duration: Literal["permanent", "normal", "2-month", "7-day", "10-min", "impact"]
    span_in: float = Field(gt=0)
    width_in: float = Field(gt=0)
    depth_in: float = Field(gt=0)
    beam_effective_length_in: float = Field(gt=0)
    combination_udl_lbf_per_in: float = Field(ge=0)
    total_sls_udl_lbf_per_in: float = Field(ge=0)
    live_sls_udl_lbf_per_in: float = Field(ge=0)
    bearing_length_in: float = Field(gt=0)
    total_limit_divisor: float = Field(gt=0)
    live_limit_divisor: float = Field(gt=0)
    material: Material
    engineer_confirmed_inputs_and_factors: Literal[True]


def evaluate_simple_beam(r: SimpleBeamRequest):
    if r.live_sls_udl_lbf_per_in > r.total_sls_udl_lbf_per_in:
        raise ValueError("Live-load UDL cannot exceed total service UDL in this positive downward-load workflow")
    moment = r.combination_udl_lbf_per_in*r.span_in**2/8
    reaction = r.combination_udl_lbf_per_in*r.span_in/2
    request = MemberRequest.model_validate({
        "standard":"NDS_2024", "method":r.method, "unit_system":"in_lbf_psi", "member_type":"beam",
        "width_in":r.width_in, "depth_in":r.depth_in, "net_tension_area_in2":r.width_in*r.depth_in,
        "beam_effective_length_in":r.beam_effective_length_in,
        "column_effective_length_x_in":r.span_in,"column_effective_length_y_in":r.span_in,
        "bearing_length_in":r.bearing_length_in,"bearing_net_area_in2":r.width_in*r.bearing_length_in,
        "bearing_distance_from_end_in":0.,"bearing_is_interior":False,
        "duration":r.duration,"material":r.material.model_dump(),
        "actions":[{"case_id":"SUPPLIED_COMBINATION_UDL","compression_lbf":0.,"tension_lbf":0.,
                    "moment_x_lbf_in":moment,"moment_y_lbf_in":0.,"shear_lbf":reaction,"bearing_reaction_lbf":reaction}],
        "serviceability":{"support_and_loading":"simply_supported_udl","span_in":r.span_in,
            "total_udl_lbf_per_in":r.total_sls_udl_lbf_per_in,"live_udl_lbf_per_in":r.live_sls_udl_lbf_per_in,
            "total_limit_divisor":r.total_limit_divisor,"live_limit_divisor":r.live_limit_divisor},
        "unnotched_prismatic":True,"connections_checked_separately":True,
        "no_composite_action_assumed":True,"minor_axis_restraint_verified":True,
    })
    result=check_member(request)
    result["analysis"]={"support_and_loading":"simply_supported_udl","moment_max_lbf_in":moment,
                        "shear_max_lbf":reaction,"reaction_each_lbf":reaction,
                        "formula_ids":["MECH-UDL-MAX-M","MECH-UDL-REACTION"]}
    result["inputs"]=r.model_dump()
    return result
