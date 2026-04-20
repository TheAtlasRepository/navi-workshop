# Task 1 — Add an elevation tool

Add a mock `get_elevation(location: str) -> dict` tool that returns something
like `{"location": "Mount Everest", "elevation_m": 8848}`.

Steps:
1. Create `tools/elevation.py` following the pattern in `tools/weather.py`
   (hash-based mock, no real API).
2. Export it from `tools/__init__.py`.
3. Register it on the agent in `agent.py`.
4. Add a case to `eval.py` exercising it (e.g. "how high is Mount Everest?").
5. Run `uv run python eval.py` and make sure your new case passes and none of
   the existing cases break.

Keep the diff small. Match the style of the existing files.
