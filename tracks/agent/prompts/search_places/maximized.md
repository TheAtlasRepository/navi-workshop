Search the curated places database.

## Parameters
- `query` (str, required): free-text search. Matches name OR category, case-insensitive.
- `near` (str, optional): city filter. Case-insensitive substring match on the city field.

## Returns
A list of dicts: `{name, category, city, lat, lon}`. Empty list if nothing matches.

## Examples
- `search_places(query="park", near="Oslo")` → all Oslo parks.
- `search_places(query="Tim Wendelboe")` → exact name match.
- `search_places(query="cafe")` → cafes in any city.

## Rules
- Don't guess coordinates if `near` returns no matches — say the place isn't in the database.
- The DB is curated and small (Norway + a few NYC entries). Real Navi hits Overture/OSM.
