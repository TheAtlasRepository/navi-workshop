"""Tool registry.

Define a tool in any file in this package and decorate with `@register_tool`.
It'll be picked up by `all_tools()` automatically — no list to maintain.

Example:

    # tools/elevation.py
    from tools import register_tool

    @register_tool
    def get_elevation(params: GetElevationParams) -> ElevationResult:
        ...

Then in the agent:

    from tools import all_tools
    agent = Agent(MODEL, tools=all_tools(), ...)
"""

_TOOLS: list = []


def register_tool(fn):
    """Mark a function as a workshop tool. Returned unchanged."""
    _TOOLS.append(fn)
    return fn


def all_tools() -> list:
    """Snapshot of every tool registered with `@register_tool`."""
    return list(_TOOLS)


# Import each tool module so its decorators run. Order doesn't matter.
from tools import demographics, elevation, places, weather  # noqa: E402, F401

# Convenience re-exports so callers can `from tools import search_places`.
from tools.demographics import GetPopulationParams, PopulationResult, get_population  # noqa: E402
from tools.elevation import ElevationResult, GetElevationParams, get_elevation  # noqa: E402
from tools.places import Place, SearchPlacesParams, search_places  # noqa: E402
from tools.weather import GetWeatherParams, WeatherResult, get_weather  # noqa: E402

__all__ = [
    "ElevationResult",
    "GetElevationParams",
    "GetPopulationParams",
    "GetWeatherParams",
    "Place",
    "PopulationResult",
    "SearchPlacesParams",
    "WeatherResult",
    "all_tools",
    "get_elevation",
    "get_population",
    "get_weather",
    "register_tool",
    "search_places",
]
