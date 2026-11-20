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
    description="NDS 2024 component-check Beta. Complete member design is not available.",
)


app.middleware("http")(protect_api)

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version", tags=["system"])
def version() -> dict[str, str]:
    return {"version": __version__, "engineering_engine": "nds-2024-component-beta", "complete_design_engine": "not-integrated"}


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
