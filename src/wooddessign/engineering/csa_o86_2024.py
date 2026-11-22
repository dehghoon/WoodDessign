"""CSA O86:24 component pilot: dry untreated 38mm visually graded framing.

Reference: TPIC2024 updated public document explicitly referencing O86:24,
sections6.4.4 /6.5; CWC2025 additional beam examples. No truss factors,
plate enhancements, glulam or built-up-member assumptions are imported.
"""
from math import log10,isfinite
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,model_validator

SIZE={64.:1.7,89.:1.7,114.:1.5,140.:1.4,184.:1.2,235.:1.1,286.:1.0}

class CanadianBeamRequest(BaseModel):
    model_config=ConfigDict(extra="forbid",allow_inf_nan=False,strict=True)
    country:Literal["CA"]
    standard:Literal["CSA_O86_2024"]
    unit_system:Literal["mm_N_MPa"]
    grade_category:Literal["visual_structural","light_framing"]="light_framing"
    blocking_at_most_2280_mm:bool=False
    width_mm:float=Field(gt=0,le=1000)
    depth_mm:float=Field(gt=0,le=2000)
    span_mm:float=Field(gt=0,le=50000)
    bearing_length_mm:float=Field(gt=0,le=1000)
    factored_udl_kn_per_m:float=Field(ge=0,le=10000)
    dead_service_udl_kn_per_m:float=Field(ge=0,le=10000)
    live_service_udl_kn_per_m:float=Field(ge=0,le=10000)
    sustained_live_fraction:float=Field(ge=0,le=1)
    duration:Literal["standard","long_term","short_term"]
    fb_mpa:float=Field(gt=0,le=200)
    fv_mpa:float=Field(gt=0,le=50)
    fcp_mpa:float=Field(gt=0,le=100)
    e_mpa:float=Field(ge=100,le=50000)
    material_designation:str=Field(min_length=3,max_length=120)
    material_source:str=Field(min_length=10,max_length=1000)
    live_limit_divisor:float=Field(gt=0,le=2000)
    total_limit_divisor:float=Field(gt=0,le=2000)
    dry_untreated_visually_graded:Literal[True]
    continuously_braced_single_member:Literal[True]
    no_notches_holes_or_composite_action:Literal[True]
    engineer_confirmed_inputs_and_factors:Literal[True]

    @model_validator(mode="after")
    def geometry(self):
        if self.width_mm!=38 or self.depth_mm not in SIZE:
            raise ValueError("Canadian pilot supports 38mm visually graded framing at listed standard depths only; no size-factor extrapolation")
        if self.depth_mm==286 and not self.blocking_at_most_2280_mm:
            raise ValueError("286mm framing requires confirmed adequate bridging/blocking at <=2280mm")
        if self.bearing_length_mm>self.span_mm/2:raise ValueError("Bearing length is inconsistent with clear span")
        return self


def sawn_bending_capacity(width,depth,fb,kd=1.,kh=1.,kz=1.,kl=1.):
    # Reusable arithmetic also tested against the CWC2025 published example.
    for x in (width,depth,fb,kd,kh,kz,kl):
        if isinstance(x,bool) or not isinstance(x,(float,int)) or not isfinite(x) or x<=0:raise ValueError("Invalid bending input")
    if kl>1:raise ValueError("Lateral stability factor must not exceed1")
    return .9*fb*kd*kh*(width*depth**2/6)*kz*kl/1e6


def evaluate_canadian_beam(r:CanadianBeamRequest):
    b,d,L=r.width_mm,r.depth_mm,r.span_mm
    if r.duration=="short_term":kd=1.15
    elif r.duration=="long_term":kd=.65
    elif r.live_service_udl_kn_per_m==0:kd=.65 if r.dead_service_udl_kn_per_m else 1.
    else:kd=max(.65,1-.5*log10(r.dead_service_udl_kn_per_m/r.live_service_udl_kn_per_m)) if r.dead_service_udl_kn_per_m>r.live_service_udl_kn_per_m else 1.
    kz=SIZE[d] if r.grade_category=="visual_structural" else 1.;area=b*d;inertia=b*d**3/12
    moment=r.factored_udl_kn_per_m*(L/1000)**2/8
    reaction=r.factored_udl_kn_per_m*(L/1000)/2
    mr=sawn_bending_capacity(b,d,r.fb_mpa,kd=kd,kz=kz)
    vr=.9*r.fv_mpa*kd*(2*area/3)*kz/1000
    qr=.8*r.fcp_mpa*kd*b*r.bearing_length_mm/1000 # KB=KZcp=1; no enhancement
    coefficient=5*L**4/(384*r.e_mpa*inertia)
    dd=coefficient*r.dead_service_udl_kn_per_m
    dl=coefficient*r.live_service_udl_kn_per_m
    long_total=(1-r.sustained_live_fraction)*dl+2*(dd+r.sustained_live_fraction*dl)
    checks=[]
    def add(name,demand,capacity,unit,ref):
        if not all(isfinite(x) for x in (demand,capacity)) or capacity<=0:raise ValueError("Invalid component resistance")
        checks.append(dict(check_id=name,demand=demand,capacity=capacity,unit=unit,utilization=demand/capacity,status="pass" if demand<=capacity else "fail",reference=ref))
    add("bending",moment,mr,"kN·m","O86:24 sawn-lumber bending; TPIC6.5.1")
    add("shear",reaction,vr,"kN","O86:24 sawn-lumber shear; TPIC6.5.2; full reaction")
    add("end_bearing_basic",reaction,qr,"kN","Basic bearing only; no KB or plate increase")
    add("deflection_live",dl,L/r.live_limit_divisor,"mm","Uniform simple span; bending only")
    add("deflection_total_with_creep",long_total,L/r.total_limit_divisor,"mm","Dry sawn creep multiplier2; declared sustained live fraction")
    return dict(country="CA",standard=r.standard,profile_version="csa-o86-24-framing-pilot-2026-11-22",method="LSD",
        checked_scope_status="fail" if any(x['status']=='fail' for x in checks) else "pass",whole_member_status="not-checked",engineering_approval=False,
        inputs=r.model_dump(),parameters=dict(phi_bending=.9,phi_shear=.9,phi_bearing=.8,KD=kd,KH=1.,KS=1.,KT=1.,KL=1.,KZb=kz,KZv=kz,KB=1.,KZcp=1.,creep_multiplier=2.),
        analysis=dict(moment_max_knm=moment,shear_max_kn=reaction,reaction_each_kn=reaction,support_and_loading="simply_supported_udl"),
        geometry=dict(area_mm2=area,section_modulus_mm3=b*d**2/6,inertia_mm4=inertia),
        checks=checks,deflections=dict(dead_immediate_mm=dd,live_immediate_mm=dl,total_with_creep_mm=long_total),
        limitations=["CANADIAN_COMPONENT_PILOT_NOT_COMPLETE_CODE_APPROVAL","DRY_UNTREATED_38MM_FRAMING_ONLY","CONTINUOUS_COMPRESSION_EDGE_AND_SUPPORT_RESTRAINT_REQUIRED","NO_SYSTEM_FACTOR_OR_TRUSS_PLATE_ENHANCEMENT","LOCAL_NEAR_SUPPORT_BEARING_LOAD_EFFECTS_NOT_CHECKED","CONNECTIONS_FIRE_VIBRATION_NOT_CHECKED","NO_GLULAM_SCL_BUILTUP_OR_CSA2019_FALLBACK"],
        source_urls=["https://tpic.ca/wp-content/uploads/2024/08/tpic_2024_updated.pdf","https://cwc.ca/wp-content/uploads/2026/09/WDM_additional_design_examples.pdf"])
