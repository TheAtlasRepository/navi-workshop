"""Mock demographics. Real versions hit census APIs or enriched tilesets."""

import hashlib


def get_population(location: str) -> dict:
    """Population estimate for a location.

    Args:
        location: free-text place name (city, neighborhood, etc.)
    """
    h = int(hashlib.md5(location.lower().encode()).hexdigest(), 16)
    population = 10_000 + (h % 5_000_000)
    median_age = 25 + (h % 30)
    return {
        "location": location,
        "population": population,
        "median_age": median_age,
    }
