"""NDS 2024 member-check kernels from the approved equation-level v2 handoff.

Internal units: inch, lbf, psi. No reference material database or implicit
engineering factors. These are component checks, not whole-member certification.
CivilPy corrections: adjusted properties, both column axes, full-precision
utilization, strict applicability and no interaction denominator clamping.
"""
from __future__ import annotations

import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DURATION = {"permanent": .90, "normal": 1., "2-month": 1.15,
            "7-day": 1.25, "10-min": 1.60, "impact": 2.}
TIME_EFFECT = {"permanent": .60, "normal": .80, "2-month": .80,
               "7-day": .80, "10-min": 1., "impact": 1.}
FORMAT = {"Fb": (2.54, .85), "Ft": (2.70, .80), "Fv": (2.88, .75),
          "Fc_perp": (1.67, .90), "Fc": (2.40, .90), "Emin": (1.76, .85)}
SPEC = "Wood Engineering Calculation Specification — APPROVED Equation-Level v2 (2026-08-25)"


def number(value, name: str, *, zero: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite numeric")
    if value < 0 or (value == 0 and not zero):
        raise ValueError(f"{name} must be {'nonnegative' if zero else 'positive'}")
    return float(value)


def stability_ratio(critical: float, adjusted: float, coefficient: float) -> float:
    """NDS-F-034/062. Rationalized root avoids cancellation for stiff columns."""
    ratio = number(critical, "critical") / number(adjusted, "adjusted")
    c = number(coefficient, "coefficient")
    if c > 1:
        raise ValueError("Stability coefficient must not exceed one")
    if not math.isfinite(ratio) or ratio <= 0:
        raise ValueError("Stability ratio is outside the representable range")
    # Solve c*x^2 - (1+r)*x + r = 0 for the smaller root.
    # Scaling by r above one prevents overflow without clamping the result.
    if ratio >= 1:
        inverse = 1 / ratio
        return 2 / (1 + inverse + math.sqrt((1 + inverse)**2 - 4*c*inverse))
    return 2*ratio / (1 + ratio + math.sqrt((1 + ratio)**2 - 4*c*ratio))



def beam_stability(b: float, d: float, effective_length: float,
                   fb_star: float, emin_adjusted: float) -> dict:
    b, d = number(b, "b"), number(d, "d")
    le = number(effective_length, "beam effective length")
    number(fb_star, "Fb*"), number(emin_adjusted, "Emin adjusted")
    rb = math.sqrt(le * d / b**2)
    if not math.isfinite(rb):
        raise ValueError("Beam slenderness is outside the representable range")
    if rb > 50:
        return {"status": "invalid", "RB": rb, "CL": None,
                "reason": "BEAM_SLENDERNESS_EXCEEDS_50", "formula_id": "NDS-F-060"}
    fbe = 1.20 * emin_adjusted / rb**2
    cl = stability_ratio(fbe, fb_star, .95)
    return {"status": "checked", "RB": rb, "FbE_psi": fbe, "CL": cl,
            "Fb_adjusted_psi": fb_star * cl, "formula_id": "NDS-F-060..063"}


def column_axis(dimension: float, effective_length: float, fc_star: float,
                emin_adjusted: float, *, coefficient: float = .8,
                built_up_factor: float = 1.) -> dict:
    dimension, le = number(dimension, "axis dimension"), number(effective_length, "column effective length")
    fc_star, emin_adjusted = number(fc_star, "Fc*"), number(emin_adjusted, "Emin adjusted")
    kf = number(built_up_factor, "built-up Kf")
    if kf > 1:
        raise ValueError("Built-up Kf must not exceed one")
    slenderness = le / dimension
    if slenderness > 50:
        return {"status": "invalid", "slenderness": slenderness, "Cp": None,
                "reason": "COLUMN_SLENDERNESS_EXCEEDS_50", "formula_id": "NDS-F-032"}
    fce = .822 * emin_adjusted / slenderness**2
    cp = kf * stability_ratio(fce, fc_star, coefficient)
    return {"status": "checked", "slenderness": slenderness, "FcE_psi": fce,
            "Cp": cp, "Fc_adjusted_psi": fc_star * cp, "Kf": kf,
            "formula_id": "NDS-F-031..036"}


def combined_compression(fc: float, fcp: float, fbx: float, fby: float,
                         fbxp: float, fbyp: float, fce1: float,
                         fce2: float, fbe: float) -> dict:
    for name, value in [("fc", fc), ("fbx", fbx), ("fby", fby)]:
        number(value, name, zero=True)
    for name, value in [("Fc'", fcp), ("Fbx'", fbxp), ("Fby'", fbyp),
                        ("FcE1", fce1), ("FcE2", fce2), ("FbE", fbe)]:
        number(value, name)
    d1 = 1 - fc / fce1
    aux = fc / fce2 + (fbx / fbe)**2
    d2 = 1 - aux
    if d1 <= 0 or d2 <= 0:
        return {"status": "fail", "reason": "INSTABILITY", "D1": d1,
                "D2": d2, "auxiliary": aux, "utilization": None,
                "formula_id": "NDS-F-090..092"}
    utilization = (fc / fcp)**2 + fbx / (fbxp * d1) + fby / (fbyp * d2)
    return {"status": "pass" if utilization <= 1 and aux < 1 else "fail",
            "utilization": utilization, "D1": d1, "D2": d2, "auxiliary": aux,
            "formula_id": "NDS-F-090..092"}


def bearing_factor(length: float, distance_from_end: float, interior: bool) -> float:
    length = number(length, "bearing length")
    distance = number(distance_from_end, "bearing distance from end", zero=True)
    return (length + .375) / length if interior and length < 6 and distance >= 3 else 1.


def adjusted_property(reference: float, property_name: str, factors: dict[str, float],
                      method: str, duration: str) -> dict:
    """External adjustment factors require explicit provenance in the request.

    CD / KF / phi / time-effect are controlled here and cannot be overridden.
    CL, Cp and Cb are computed separately from geometry and adjusted values.
    """
    reference = number(reference, property_name)
    if property_name not in ("Fb", "Ft", "Fv", "Fc", "Fc_perp", "E", "Emin"):
        raise ValueError("Unsupported property")
    if method not in ("ASD", "LRFD") or duration not in DURATION:
        raise ValueError("Unknown design method or duration")
    allowed = {
        "Fb": {"CM", "Ct", "CF", "Cfu", "Ci"},
        "Ft": {"CM", "Ct", "CF", "Ci"}, "Fv": {"CM", "Ct", "Ci"},
        "Fc": {"CM", "Ct", "CF", "Ci"}, "Fc_perp": {"CM", "Ct"},
        "E": {"CM", "Ct", "Ci"}, "Emin": {"CM", "Ct", "Ci", "CT"},
    }[property_name]
    if set(factors) - allowed:
        raise ValueError("Unknown or internally calculated adjustment factor")
    values = {key: number(value, key) for key, value in factors.items()}
    result = reference * math.prod(values.values())
    trace = dict(values)
    if method == "ASD" and property_name in ("Fb", "Ft", "Fv", "Fc"):
        trace["CD"] = DURATION[duration]
        result *= trace["CD"]
    elif method == "LRFD" and property_name in FORMAT:
        kf, phi = FORMAT[property_name]
        trace.update(KF=kf, phi=phi)
        result *= kf * phi
        # Emin has format/resistance adjustment but no load-duration time effect.
        if property_name != "Emin":
            trace["lambda"] = TIME_EFFECT[duration]
            result *= trace["lambda"]
    if not math.isfinite(result) or result <= 0:
        raise ValueError("Adjusted property is nonfinite or nonpositive")
    return {"reference_psi": reference, "factors": trace, "adjusted_psi": result}


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, strict=True)


class Property(Model):
    reference_psi: float = Field(gt=0)
    adjustments: dict[str, float]
    source: str = Field(min_length=3, max_length=500)


class Material(Model):
    designation: str = Field(min_length=1, max_length=120)
    category: Literal["sawn_lumber"]
    Fb_x: Property
    Fb_y: Property
    Fv: Property
    Fc: Property
    Ft: Property
    Fc_perp: Property
    E: Property
    Emin: Property


class Actions(Model):
    case_id: str = Field(min_length=1, max_length=120)
    compression_lbf: float = Field(ge=0)
    tension_lbf: float = Field(ge=0)
    moment_x_lbf_in: float
    moment_y_lbf_in: float
    shear_lbf: float
    bearing_reaction_lbf: float = Field(ge=0)

    @model_validator(mode="after")
    def exclusive_axial(self):
        if self.compression_lbf and self.tension_lbf:
            raise ValueError("A paired action cannot be simultaneous compression and tension")
        return self


class Serviceability(Model):
    support_and_loading: Literal["simply_supported_udl"]
    span_in: float = Field(gt=0)
    total_udl_lbf_per_in: float = Field(ge=0)
    live_udl_lbf_per_in: float = Field(ge=0)
    total_limit_divisor: float = Field(gt=0)
    live_limit_divisor: float = Field(gt=0)


class MemberRequest(Model):
    standard: Literal["NDS_2024"]
    method: Literal["ASD", "LRFD"]
    unit_system: Literal["in_lbf_psi"]
    member_type: Literal["beam", "column"]
    width_in: float = Field(gt=0)
    depth_in: float = Field(gt=0)
    net_tension_area_in2: float = Field(gt=0)
    beam_effective_length_in: float = Field(gt=0)
    column_effective_length_x_in: float = Field(gt=0)
    column_effective_length_y_in: float = Field(gt=0)
    bearing_length_in: float = Field(gt=0)
    bearing_net_area_in2: float = Field(gt=0)
    bearing_distance_from_end_in: float = Field(ge=0)
    bearing_is_interior: bool
    duration: Literal["permanent", "normal", "2-month", "7-day", "10-min", "impact"]
    material: Material
    actions: list[Actions] = Field(min_length=1, max_length=100)
    serviceability: Serviceability | None
    # Scope declarations are mandatory; unsupported conditions are not assumed absent.
    unnotched_prismatic: Literal[True]
    connections_checked_separately: Literal[True]
    no_composite_action_assumed: Literal[True]
    minor_axis_restraint_verified: Literal[True]

    @model_validator(mode="after")
    def geometry(self):
        if self.depth_in < self.width_in:
            raise ValueError("This scope requires depth >= width; flatwise members are not supported")
        if self.net_tension_area_in2 > self.width_in * self.depth_in:
            raise ValueError("Net tension area exceeds gross area")
        if self.bearing_net_area_in2 > self.width_in * self.bearing_length_in:
            raise ValueError("Net bearing area exceeds available contact area")
        if self.member_type == "beam" and self.serviceability is None:
            raise ValueError("Beam serviceability inputs are required")
        ids = [case.case_id for case in self.actions]
        if len(set(ids)) != len(ids):
            raise ValueError("Action case IDs must be unique")
        return self


def check_member(request: MemberRequest) -> dict:
    r = request
    b, d = r.width_in, r.depth_in
    area, sx, sy, ix = b * d, b * d*d/6, d*b*b/6, b*d**3/12
    if any(not math.isfinite(x) or x <= 0 for x in (area, sx, sy, ix)):
        raise ValueError("Section properties are outside the representable range")
    properties = {}
    for key, value in r.material:
        if isinstance(value, Property):
            name = "Fb" if key.startswith("Fb_") else key
            properties[key] = {**adjusted_property(value.reference_psi, name, value.adjustments, r.method, r.duration), "source": value.source}
    adjusted = {key: value["adjusted_psi"] for key, value in properties.items()}
    beam = beam_stability(b, d, r.beam_effective_length_in, adjusted["Fb_x"], adjusted["Emin"])
    axes = [column_axis(d, r.column_effective_length_x_in, adjusted["Fc"], adjusted["Emin"]),
            column_axis(b, r.column_effective_length_y_in, adjusted["Fc"], adjusted["Emin"])]
    checks = []
    def add(check_id, formula, demand, capacity, case_id):
        if not math.isfinite(demand) or not math.isfinite(capacity) or capacity <= 0:
            raise ValueError("Nonfinite demand or invalid capacity")
        utilization = demand / capacity
        if not math.isfinite(utilization):
            raise ValueError("Utilization is outside the representable range")
        checks.append({"check_id": check_id, "formula_id": formula, "case_id": case_id,
                       "demand": demand, "capacity": capacity, "utilization": utilization,
                       "unit": "in" if check_id.startswith("deflection_") else "1" if check_id.startswith("tension_bending") else "psi",
                       "status": "pass" if utilization <= 1 else "fail"})
    beam_ok = beam["status"] == "checked"
    columns_ok = all(axis["status"] == "checked" for axis in axes)
    for action in r.actions:
        case = action.case_id
        fbx, fby = abs(action.moment_x_lbf_in)/sx, abs(action.moment_y_lbf_in)/sy
        fc, ft = action.compression_lbf/area, action.tension_lbf/r.net_tension_area_in2
        if fbx:
            if beam_ok:
                add("bending_x", "NDS-F-010..011", fbx, beam["Fb_adjusted_psi"], case)
            else:
                checks.append({"check_id": "bending_x", "case_id": case, **beam})
        if fby:
            # Weak-axis adjusted value is used only as supplied; weak-axis restraint is not inferred.
            add("bending_y", "NDS-F-010..011", fby, adjusted["Fb_y"], case)
        add("shear", "NDS-F-020..021", 1.5*abs(action.shear_lbf)/area, adjusted["Fv"], case)
        if fc:
            if columns_ok:
                fcp = min(axis["Fc_adjusted_psi"] for axis in axes)
                add("compression", "NDS-F-030..036", fc, fcp, case)
                if fbx or fby:
                    if beam_ok:
                        combined = combined_compression(fc, fcp, fbx, fby,
                            beam["Fb_adjusted_psi"], adjusted["Fb_y"], axes[0]["FcE_psi"], axes[1]["FcE_psi"], beam["FbE_psi"])
                        checks.append({"check_id": "compression_bending", "case_id": case, **combined})
                    else:
                        checks.append({"check_id": "compression_bending", "case_id": case, **beam})
            else:
                checks.append({"check_id": "compression", "case_id": case, "status": "invalid", "reason": "COLUMN_SLENDERNESS_EXCEEDS_50"})
        if fbx and fby and not fc and not ft:
            if beam_ok and columns_ok:
                interaction = combined_compression(0., min(axis["Fc_adjusted_psi"] for axis in axes), fbx, fby,
                    beam["Fb_adjusted_psi"], adjusted["Fb_y"], axes[0]["FcE_psi"], axes[1]["FcE_psi"], beam["FbE_psi"])
                checks.append({"check_id": "biaxial_bending", "case_id": case, **interaction})
            else:
                checks.append({"check_id": "biaxial_bending", "case_id": case, "status": "invalid", "reason": "STABILITY_NOT_APPLICABLE"})
        if ft:
            add("tension", "NDS-F-040..041", ft, adjusted["Ft"], case)
            if fbx or fby:
                if fby:
                    checks.append({"check_id": "tension_biaxial", "case_id": case, "status": "not-checked", "reason": "BIAXIAL_TENSION_INTERACTION_OUT_OF_SCOPE"})
                elif beam_ok:
                    # Eq 3.9-1 excludes CL; Eq 3.9-2 includes stability via Fb**.
                    add("tension_bending_1", "NDS-F-080", ft/adjusted["Ft"]+fbx/adjusted["Fb_x"], 1., case)
                    add("tension_bending_2", "NDS-F-081", (fbx-ft)/beam["Fb_adjusted_psi"], 1., case)
                else:
                    checks.append({"check_id": "tension_bending", "case_id": case, **beam})
        cb = bearing_factor(r.bearing_length_in, r.bearing_distance_from_end_in, r.bearing_is_interior)
        add("bearing", "NDS-F-050..052", action.bearing_reaction_lbf/r.bearing_net_area_in2, adjusted["Fc_perp"]*cb, case)
    deflections = {}
    if r.serviceability:
        s = r.serviceability
        for kind, load, divisor in [("total", s.total_udl_lbf_per_in, s.total_limit_divisor), ("live", s.live_udl_lbf_per_in, s.live_limit_divisor)]:
            delta = 5*load*s.span_in**4/(384*adjusted["E"]*ix)
            limit = s.span_in/divisor
            deflections[kind] = {"deflection_in": delta, "limit_in": limit}
            add("deflection_"+kind, "NDS-F-070..071", delta, limit, "SLS_"+kind)
    checked_status = "fail" if any(x["status"] in ("fail", "invalid") for x in checks) else "not-checked" if any(x["status"] == "not-checked" for x in checks) else "pass"
    ratios = [x for x in checks if x.get("utilization") is not None]
    return {"standard": "NDS_2024", "method": r.method, "scope": "component_checks",
            "checked_scope_status": checked_status, "whole_member_status": "not-checked",
            "engineering_approval": False, "source_specification": SPEC,
            "geometry": {"area_in2": area, "Sx_in3": sx, "Sy_in3": sy, "Ix_in4": ix},
            "adjusted_properties": properties, "beam_stability": beam,
            "column_axes": axes, "column_governing_axis": None if not columns_ok else ("x" if axes[0]["Fc_adjusted_psi"] <= axes[1]["Fc_adjusted_psi"] else "y"),
            "checks": checks, "governing_check": max(ratios, key=lambda x:x["utilization"]) if ratios else None,
            "deflections": deflections,
            "limitations": ["BETA_COMPONENT_CHECKS_NOT_PROFESSIONAL_APPROVAL", "ENGINEER_SUPPLIED_MATERIAL_AND_ADJUSTMENT_FACTORS",
                            "CONNECTIONS_FIRE_DURABILITY_AND_NOTCHES_NOT_CHECKED", "SINGLE_PRISMATIC_SAWN_MEMBER_ONLY",
                            "BUILT_UP_GLULAM_SCL_CSA_O86_NOT_IMPLEMENTED", "MINOR_AXIS_RESTRAINT_REQUIRES_SEPARATE_VERIFICATION",
                            "DEFLECTION_IS_BENDING_ONLY_NO_SHEAR_OR_CREEP"]}
