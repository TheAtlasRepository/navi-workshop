"""Mock place search. Swap for a real Mapbox/OSM/Google call whenever."""

from pydantic import BaseModel, Field

from tools import register_tool


class SearchPlacesParams(BaseModel):
    """Tool input. Becomes the function-call schema the model sees."""

    query: str = Field(
        description="Free-text search. Matches name OR category, case-insensitive."
    )
    near: str | None = Field(
        default=None,
        description="Optional city filter (case-insensitive substring on city).",
    )


class Place(BaseModel):
    name: str
    category: str
    city: str
    lat: float
    lon: float


_PLACES: list[Place] = [
    Place(name="Frogner Park", category="park", city="Oslo", lat=59.9267, lon=10.7039),
    Place(name="Vigeland Sculpture Garden", category="park", city="Oslo", lat=59.9267, lon=10.7039),
    Place(name="Oslo Opera House", category="landmark", city="Oslo", lat=59.9076, lon=10.7531),
    Place(name="Fløyen", category="landmark", city="Bergen", lat=60.3939, lon=5.3290),
    Place(name="Bryggen", category="landmark", city="Bergen", lat=60.3975, lon=5.3241),
    Place(name="Tim Wendelboe", category="cafe", city="Oslo", lat=59.9235, lon=10.7540),
    Place(name="Kaffemisjonen", category="cafe", city="Bergen", lat=60.3931, lon=5.3245),
    Place(name="Central Park", category="park", city="New York", lat=40.7829, lon=-73.9654),
    Place(name="Prospect Park", category="park", city="New York", lat=40.6602, lon=-73.9690),
    Place(name="Mount Everest", category="landmark", city="Khumbu", lat=27.9881, lon=86.9250),
]


@register_tool
def search_places(params: SearchPlacesParams) -> list[Place]:
    """Search the curated places database."""
    q = params.query.lower()
    results = [p for p in _PLACES if q in p.name.lower() or q in p.category.lower()]
    if params.near:
        n = params.near.lower()
        results = [p for p in results if n in p.city.lower()]
    return results
