"""Mock elevation. Real versions hit terrain DEMs / OpenTopography."""

import hashlib

from pydantic import BaseModel, Field

from tools import register_tool


class GetElevationParams(BaseModel):
    location: str = Field(description="Place name (city, neighborhood, or landmark).")


class ElevationResult(BaseModel):
    location: str
    elevation_m: int


@register_tool
def get_elevation(params: GetElevationParams) -> ElevationResult:
    """Elevation in meters above sea level for one location (mock)."""
    h = int(hashlib.md5(params.location.lower().encode()).hexdigest(), 16)
    return ElevationResult(
        location=params.location,
        elevation_m=(h % 10000) + 1,
    )
