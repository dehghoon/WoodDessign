"""FastAPI transport layer for WoodDessign.

This module intentionally does not contain engineering calculations.
"""

from fastapi import FastAPI, HTTPException, status

from wooddessign import __version__
from wooddessign.api.tool_auth import protect_api
from wooddessign.engineering.nds2024 import MemberRequest, check_member
from wooddessign.engineering.simple_beam import SimpleBeamRequest, evaluate_simple_beam
from wooddessign.models.calculation import CalculationRequest, CalculationUnavailable

app = FastAPI(
    title="WoodDessign API",
    version=__version__,
    description="USA NDS 2024 and limited Canadian CSA O86:24 component Beta; no complete member approval.",
)


app.middleware("http")(protect_api)

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version", tags=["system"])
def version() -> dict[str, str]:
    return {"version": __version__, "engineering_engine": "country-component-pilot-2026-11-22", "complete_design_engine": "not-integrated"}


@app.post(
    "/api/v1/calculate",
    tags=["calculations"],
    responses={503: {"model": CalculationUnavailable}},
)
def calculate(_: CalculationRequest) -> None:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": "ENGINEERING_ENGINE_NOT_VALIDATED",
            "message": (
                "Calculation is unavailable until the governing engineering specification "
                "and validated Agent #2 engine are integrated."
            ),
            "hold_points": ["HP-01", "HP-05"],
        },
    )


@app.post("/api/v1/nds2024/member-check")
def member_check(request: MemberRequest) -> dict:
    try:
        return check_member(request)
    except (ValueError, ArithmeticError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/api/v1/nds2024/simple-beam")
def simple_beam(request: SimpleBeamRequest) -> dict:
    try:
        return evaluate_simple_beam(request)
    except (ValueError, ArithmeticError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


from typing import Annotated,Literal,Union
from pydantic import Field
from wooddessign.engineering.csa_o86_2024 import CanadianBeamRequest,evaluate_canadian_beam

class UnitedStatesBeamRequest(SimpleBeamRequest):
    country:Literal["US"]
    standard:Literal["NDS_2024"]
    unit_system:Literal["in_lbf_psi"]

CountryBeamRequest=Annotated[Union[UnitedStatesBeamRequest,CanadianBeamRequest],Field(discriminator="country")]

@app.post("/api/v1/beam/check")
def country_beam(request:CountryBeamRequest):
    try:
        if isinstance(request,CanadianBeamRequest):return evaluate_canadian_beam(request)
        original=SimpleBeamRequest.model_validate(request.model_dump(exclude={"country","standard","unit_system"}))
        result=evaluate_simple_beam(original)
        return {**result,"country":"US","standard":"NDS_2024","unit_system":"in_lbf_psi"}
    except (ValueError,ArithmeticError) as e:raise HTTPException(status_code=422,detail=str(e)) from e
