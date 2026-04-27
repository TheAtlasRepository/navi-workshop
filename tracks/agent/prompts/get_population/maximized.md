Population and median-age estimate for one location.

## Parameters
- `location` (str, required): place name. City, neighborhood, or any free-text identifier.

## Returns
A dict: `{location, population, median_age}`. Population is between 10k and 5M;
median_age is between 25 and 55.

## Examples
- `get_population(location="Bergen")` → `{population: 312_405, median_age: 38}`
- `get_population(location="Frogner")` → still works; treated as a generic name.

## Rules
- Mock data; numbers are deterministic per name (hash-derived). Don't claim accuracy.
- For real demographics, you'd combine a geocoder + a census tileset.
