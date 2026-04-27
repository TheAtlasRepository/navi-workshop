"""Mock POI finder. A real-shaped tool: ~80 categories, nested filters and
sort, multi-page results.

Shipped without `@register_tool` on purpose — Challenge 4 asks you to
activate it and then *see* in Logfire how much it inflates every request,
even when the user asks something unrelated like "what's the weather?".

Challenge 5 then teaches you to fix that with dynamic tool opening.
"""

from typing import Literal

from pydantic import BaseModel, Field

# from tools import register_tool  # ← Challenge 4: uncomment this and the
                                    # @register_tool below to activate.


# ---- The bloat: ~80 POI categories from the Overture Maps schema. ------------

POICategory = Literal[
    "airport", "amusement_park", "aquarium", "art_gallery", "atm",
    "bakery", "bank", "bar", "beauty_salon", "bicycle_store",
    "book_store", "bowling_alley", "bus_station", "cafe", "campground",
    "car_dealer", "car_rental", "car_repair", "cemetery", "church",
    "city_hall", "clothing_store", "convenience_store", "courthouse", "dentist",
    "department_store", "doctor", "electrician", "electronics_store", "embassy",
    "fire_station", "florist", "funeral_home", "furniture_store", "gas_station",
    "grocery_store", "gym", "hair_care", "hardware_store", "hindu_temple",
    "hospital", "insurance_agency", "jewelry_store", "laundry", "lawyer",
    "library", "liquor_store", "local_government_office", "locksmith", "lodging",
    "meal_delivery", "meal_takeaway", "mosque", "movie_theater", "moving_company",
    "museum", "night_club", "park", "parking", "pet_store",
    "pharmacy", "physiotherapist", "police", "post_office", "primary_school",
    "real_estate_agency", "restaurant", "roofing_contractor", "rv_park", "school",
    "secondary_school", "shoe_store", "shopping_mall", "spa", "stadium",
    "store", "subway_station", "supermarket", "synagogue", "taxi_stand",
    "tourist_attraction", "train_station", "transit_station", "travel_agency",
    "university", "veterinary_care", "zoo",
]


# ---- Nested filter and sort sub-models. --------------------------------------

class POIFilters(BaseModel):
    """Optional filters narrowing the result set. All default to no filtering."""

    open_now: bool = Field(
        default=False,
        description=(
            "If true, only return POIs currently open according to their hours. "
            "Uses the local timezone of the city. Hours are mocked in this "
            "dataset, so the effective filter is approximate."
        ),
    )
    accepts_credit_cards: bool = Field(
        default=False,
        description="If true, only POIs that accept credit cards. Mock data.",
    )
    has_outdoor_seating: bool = Field(
        default=False,
        description=(
            "Restaurant/cafe/bar only. If true, filter to POIs with outdoor "
            "seating. Has no effect for categories without seating."
        ),
    )
    wheelchair_accessible: bool = Field(
        default=False,
        description=(
            "If true, only POIs with documented wheelchair access. Conservative "
            "filter — POIs without explicit accessibility data are excluded."
        ),
    )
    family_friendly: bool = Field(
        default=False,
        description="If true, exclude bars, night_clubs, and adult-oriented venues.",
    )
    price_max: Literal["$", "$$", "$$$", "$$$$"] | None = Field(
        default=None,
        description=(
            "Maximum price tier. $ is cheapest, $$$$ most expensive. None "
            "means no price filter. Most categories don't have price data; "
            "this filter is best-effort."
        ),
    )


class POISort(BaseModel):
    """How to order results before pagination."""

    by: Literal["distance", "rating", "price", "popularity", "alphabetical"] = Field(
        default="distance",
        description=(
            "Field to sort by. 'distance' is from the city center coordinate. "
            "'popularity' is a composite of recent reviews and check-ins, mocked "
            "as a deterministic hash of the POI name."
        ),
    )
    direction: Literal["asc", "desc"] = Field(
        default="asc",
        description="Sort direction. 'asc' = ascending; 'desc' = descending.",
    )


# ---- The tool's input model. -------------------------------------------------

class FindPOIsParams(BaseModel):
    """Search parameters for finding points of interest in a city."""

    category: POICategory = Field(
        description=(
            "POI category to search for. Must be exactly one of the listed "
            "values — these follow the Overture Maps schema. If the user's "
            "query is ambiguous (e.g. 'food'), pick the most likely category "
            "from the list rather than asking the user. For nested categories "
            "(e.g. 'cafe' is a subset of 'restaurant'), prefer the more "
            "specific one. For categories that span multiple types (e.g. a "
            "'movie_theater' could also be a 'tourist_attraction'), pick the "
            "primary use."
        )
    )
    city: str = Field(
        description=(
            "City name. Case-insensitive substring match on the city field. "
            "For ambiguous city names (e.g. 'Springfield'), use the country "
            "context if available, otherwise the most populous match wins."
        ),
    )
    radius_m: int = Field(
        default=1000,
        ge=100,
        le=50000,
        description=(
            "Search radius in meters from the city center. Default 1000m. "
            "Use larger radii (5000m+) for sparse rural categories like "
            "campground, rv_park, or cemetery; smaller radii (500m) for "
            "dense urban categories like cafe or bar. Capped at 50000m."
        ),
    )
    filters: POIFilters | None = Field(
        default=None,
        description=(
            "Optional filters to narrow results. See POIFilters. Filters "
            "stack — e.g. open_now AND wheelchair_accessible returns only "
            "POIs matching both. Most filters are best-effort against mock data."
        ),
    )
    sort: POISort | None = Field(
        default=None,
        description="How to order results before pagination. Defaults to distance ascending.",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of POIs to return. Capped at 100.",
    )
    page: int = Field(
        default=0,
        ge=0,
        description=(
            "Zero-indexed page number for pagination. Combine with limit "
            "to walk large result sets — e.g. limit=20, page=2 returns "
            "results 41-60."
        ),
    )


# ---- Output model. -----------------------------------------------------------

class POI(BaseModel):
    name: str
    category: str
    city: str


class FindPOIsResult(BaseModel):
    pois: list[POI]
    total_count: int = Field(description="Total POIs before pagination.")
    page: int
    has_more: bool


# ---- The tool itself (mock). -------------------------------------------------

# @register_tool   ← Challenge 4: uncomment this line.
def find_pois(params: FindPOIsParams) -> FindPOIsResult:
    """Find points of interest by category in a city. Mock data."""
    sample = POI(
        name=f"Sample {params.category} in {params.city}",
        category=params.category,
        city=params.city,
    )
    return FindPOIsResult(
        pois=[sample],
        total_count=1,
        page=params.page,
        has_more=False,
    )
