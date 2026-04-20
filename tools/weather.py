"""Mock weather. Replace with OpenWeatherMap/MET Norway for real calls."""

import hashlib

_CONDITIONS = ["sunny", "cloudy", "rainy", "snowy", "foggy"]


def get_weather(location: str) -> dict:
    """Current weather for a location.

    Args:
        location: free-text place name (e.g. "Oslo")
    """
    h = int(hashlib.md5(location.lower().encode()).hexdigest(), 16)
    return {
        "location": location,
        "condition": _CONDITIONS[h % len(_CONDITIONS)],
        "temperature_c": (h % 35) - 5,
        "wind_kph": h % 40,
    }
