Current weather for one location.

## Parameters
- `location` (str, required): place name. City, neighborhood, or landmark.

## Returns
A dict: `{location, condition, temperature_c, wind_kph}`. `condition` is one of
`sunny | cloudy | rainy | snowy | foggy`.

## Examples
- `get_weather(location="Oslo")` → `{condition: "rainy", temperature_c: 8, ...}`
- `get_weather(location="Mount Everest")` → still works; the mock is deterministic.

## Rules
- One location per call. Don't try to batch — chain calls instead.
- The mock derives weather from a hash of the name. Same name → same answer.
