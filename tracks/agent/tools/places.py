"""Mock place search. Swap for a real Mapbox/OSM/Google call whenever."""

from dataclasses import dataclass


@dataclass
class Place:
    name: str
    category: str
    city: str
    lat: float
    lon: float


_PLACES: list[Place] = [
    Place("Frogner Park", "park", "Oslo", 59.9267, 10.7039),
    Place("Vigeland Sculpture Garden", "park", "Oslo", 59.9267, 10.7039),
    Place("Oslo Opera House", "landmark", "Oslo", 59.9076, 10.7531),
    Place("Fløyen", "landmark", "Bergen", 60.3939, 5.3290),
    Place("Bryggen", "landmark", "Bergen", 60.3975, 5.3241),
    Place("Tim Wendelboe", "cafe", "Oslo", 59.9235, 10.7540),
    Place("Kaffemisjonen", "cafe", "Bergen", 60.3931, 5.3245),
    Place("Central Park", "park", "New York", 40.7829, -73.9654),
    Place("Prospect Park", "park", "New York", 40.6602, -73.9690),
    Place("Mount Everest", "landmark", "Khumbu", 27.9881, 86.9250),
]


def search_places(query: str, near: str | None = None) -> list[dict]:
    """Search mock place database.

    Args:
        query: free-text search (matches name or category, case-insensitive)
        near: optional city filter (case-insensitive)
    """
    q = query.lower()
    results = [
        p for p in _PLACES
        if q in p.name.lower() or q in p.category.lower()
    ]
    if near:
        n = near.lower()
        results = [p for p in results if n in p.city.lower()]
    return [
        {"name": p.name, "category": p.category, "city": p.city, "lat": p.lat, "lon": p.lon}
        for p in results
    ]
