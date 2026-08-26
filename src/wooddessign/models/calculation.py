"""Transport contracts for calculation requests.

These contracts deliberately avoid engineering-specific constants or formulas.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CalculationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str | None = None
    design_standard: str = Field(min_length=1)
    design_standard_edition: str = Field(min_length=1)
    inputs: dict[str, Any]


class CalculationUnavailable(BaseModel):
    code: str
    message: str
    hold_points: list[str]
