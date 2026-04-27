"""Mock weather. Replace with OpenWeatherMap/MET Norway for real calls."""

import hashlib

from pydantic import BaseModel, Field

from tools import register_tool

_CONDITIONS = ["sunny", "cloudy", "rainy", "snowy", "foggy"]


class GetWeatherParams(BaseModel):
    location: str = Field(description="Place name (city, neighborhood, or landmark).")


class WeatherResult(BaseModel):
    location: str
    condition: str
    temperature_c: int
    wind_kph: int


@register_tool
def get_weather(params: GetWeatherParams) -> WeatherResult:
    """Current weather for one location. Deterministic from the name (mock)."""
    h = int(hashlib.md5(params.location.lower().encode()).hexdigest(), 16)
    return WeatherResult(
        location=params.location,
        condition=_CONDITIONS[h % len(_CONDITIONS)],
        temperature_c=(h % 35) - 5,
        wind_kph=h % 40,
    )
