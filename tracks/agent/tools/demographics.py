"""Mock demographics. Real versions hit census APIs or enriched tilesets."""

import hashlib

from pydantic import BaseModel, Field

from tools import register_tool


class GetPopulationParams(BaseModel):
    location: str = Field(description="Place name (city, neighborhood, etc.).")


class PopulationResult(BaseModel):
    location: str
    population: int
    median_age: int


@register_tool
def get_population(params: GetPopulationParams) -> PopulationResult:
    """Population estimate for one location. Deterministic from the name (mock)."""
    h = int(hashlib.md5(params.location.lower().encode()).hexdigest(), 16)
    return PopulationResult(
        location=params.location,
        population=10_000 + (h % 5_000_000),
        median_age=25 + (h % 30),
    )
