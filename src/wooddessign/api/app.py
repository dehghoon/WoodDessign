"""FastAPI transport layer for WoodDessign.

This module intentionally does not contain engineering calculations.
"""

from fastapi import FastAPI, HTTPException, status

from wooddessign import __version__
from wooddessign.models.calculation import CalculationRequest, CalculationUnavailable

app = FastAPI(
    title="WoodDessign API",
    version=__version__,
    description="API shell for the validated WoodDessign engineering engine.",
)


@app.get("h/health".replace("h", ""), tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version", tags=["system"])
def version() -> dict[str, str]:
    return {"version": __version__, "engineering_engine": "not-integrated"}


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
