# Challenges

A ladder. Do them in order; each builds on the last. If you finish, start the
presentation-builder track instead.

Every challenge has a ✓ **Success criteria** line so you know when to move on.
Click the 💡 **Hint** blocks if you get stuck.

---

## 1. Add a tool (15 min)

Add `get_elevation(location: str) -> dict` that returns a mock elevation in
meters (follow the pattern in `tools/weather.py`). Export from `tools/__init__.py`,
register on the agent in `agent.py`. Ask the app *"what's the elevation of
Mount Everest?"* and watch the Logfire trace.

**What you're learning:** the tool-call loop. The model picks a tool, you run
it, the result goes back, the model answers.

✓ **Done when**: the app answers the Everest question with a number, and
Logfire shows a `get_elevation` span in the trace.

---

## 2. Break and fix the system prompt (15 min)

Run `uv run python eval.py` — note the pass count (should be 5/5).

Now edit `SYSTEM_PROMPT` in `agent.py` to something vague like `"You are a
helpful assistant."`. Rerun the eval. Watch cases fail.

Finally, rewrite the prompt sharper than the original: concrete rules, scoped,
opinionated about when to use which tool. Rerun. All cases should pass again.

**What you're learning:** prompts are code. Vibes aren't enough — the eval
tells you if your edit helped or hurt.

✓ **Done when**: baseline 5/5 → at least 2 failures with vague prompt → 5/5
with your rewrite.

---

## 3. Dynamic tool opening (30 min)

Ask the same question of both `agent.py` (static) and `examples/dynamic_tools.py`
(dynamic). In the Logfire traces, compare the **input token count** on the
first turn.

Then: add a fourth tool category (`get_traffic`) to the dynamic variant
**without growing the base system prompt**.

**What you're learning:** tools cost tokens even when idle. Dynamic opening
scales tool count without burning context per turn.

✓ **Done when**: dynamic variant uses meaningfully fewer input tokens on turn 1;
you added `get_traffic` to the REGISTRY and confirmed the dynamic agent
discovers + uses it via `list_tools` → `get_tool_docs` → `invoke_tool`.

<details>
<summary>💡 Hint — where does a tool live in the dynamic variant?</summary>

In `examples/dynamic_tools.py`, tools live in the `REGISTRY` dict, not as
`@agent.tool` decorators. Adding a tool = adding an entry:

```python
REGISTRY["get_traffic"] = {
    "fn": get_traffic,
    "summary": "Current traffic for a named location.",
    "signature": "get_traffic(location: str) -> dict",
}
```

No prompt changes needed — the agent finds it via `list_tools()`.
</details>

---

## 4. Sub-agent for a sub-domain (45 min)

`examples/subagent.py` has an orchestrator + a spatial-analysis specialist.
Add a second specialist — a **demographics-analyst** — with its own prompt
and its own tool set. Route to it from the orchestrator.

Measure: trace depth, total tokens per query, end-to-end latency. Compare to
the monolithic `agent.py`.

**What you're learning:** sub-agents trade latency for context discipline.
The orchestrator stays small; specialists do the heavy lifting in isolation.

✓ **Done when**: a demographics-flavored question (e.g. *"how many people
live in Bergen?"*) produces a nested span in Logfire for the demographics
agent, and a weather question does *not* touch either specialist.

<details>
<summary>💡 Hint — the delegation pattern</summary>

Copy the `spatial_agent` + `delegate_spatial` pattern:

```python
demographics_agent = Agent(MODEL, system_prompt=DEMOGRAPHICS_PROMPT, instrument=True)
demographics_agent.tool_plain(get_population)

@orchestrator.tool_plain
async def delegate_demographics(question: str) -> str:
    result = await demographics_agent.run(question)
    return result.output
```

Update the orchestrator system prompt so it knows when to route to which
specialist. The routing rule is the whole point — make it explicit.
</details>

---

## 5. Write a real eval case (30 min)

Add a case to `eval.py` that the current agent **fails**. Confirm the eval
catches it. Now fix the prompt or a tool until it passes — without breaking
the other cases.

**What you're learning:** regression tests for prompts. The loop is
*reproduce → assert → fix → confirm*, same as any other bug.

✓ **Done when**: your new case starts red, ends green; all previously-passing
cases still pass.

<details>
<summary>📎 Concrete starter — a case that actually fails today</summary>

Try this one. It's subtle: the user asks a multi-step question and the agent
often skips one of the steps:

```python
Case(
    "bergen_chain",
    "What's the weather in Bergen and how many people live there?",
    {"get_weather", "get_population"},   # must call both
    ["Bergen"],
)
```

If this passes on first run, congratulations — your agent is better than most
agents in the wild. Try:

```python
Case(
    "oslo_parks_weather",
    "Find parks in Oslo and tell me the weather at the first one.",
    {"search_places", "get_weather"},
    ["Oslo"],
)
```

To fix, tighten the system prompt with a rule like *"When a user asks about
multiple facts for a place, call every relevant tool before answering — don't
skip tools because one answer is 'obvious'."*
</details>

---

## 6. LLM-as-judge (optional, 30 min)

Add a judge function at the bottom of `eval.py`. For one case, instead of a
substring check, call a small LLM with a rubric and ask it to score the
output 1–5. Run it **10 times on the same input**. Note the variance.

**What you're learning:** why we're careful with LLM judges. They're useful
for fuzzy correctness but noisy and occasionally wrong. Use deterministic
checks first; reach for a judge only when you can't express correctness as
a rule.

✓ **Done when**: you have 10 scores for the same (input, output) pair, and
at least one score differs from the mode. Write your variance observation
as a comment at the end of `eval.py`.

<details>
<summary>💡 Hint — a minimal judge</summary>

A tiny Pydantic AI agent is the cleanest shape:

```python
from pydantic_ai import Agent

judge_agent = Agent(
    MODEL,
    output_type=int,
    system_prompt=(
        "Score the assistant's answer to the user's question on a 1-5 scale "
        "for clarity and friendliness. Reply with only the integer."
    ),
)

async def judge(prompt: str, output: str) -> int:
    msg = f"User asked: {prompt}\nAssistant answered: {output}"
    result = await judge_agent.run(msg)
    return result.output
```

Call it 10 times in a loop, print the scores. Don't worry about aggregating —
the variance *is* the lesson.
</details>

---

## 7. Stretch: parallelize with git worktrees

See `worktrees-demo/`. Pick three improvements from above (or any 3 of the
7-challenge ladder). Open three worktrees with `./worktrees-demo/demo.sh up`.
Assign one to each (you, or three Claude Code sessions). Merge them back.

Notice what slows you down and what speeds you up.

**What you're learning:** the orchestration pattern. You are the planner;
the agents do the work. The bottleneck becomes review, not code.

✓ **Done when**: three branches merged back into main, all evals green on
the merged result.

---

## 8. Stretch: real data via Overpass (45 min)

All the tools so far are mocks. Real Navi hits Overture Maps via DuckDB
— too heavy for a workshop. But **Overpass** is the lightweight cousin:
the OpenStreetMap query API, free, no auth, returns JSON.

Write a new tool `find_places_nearby(category: str, city: str, radius_m: int = 1000)`
that hits Overpass and returns real OSM places. Register it, ask
*"find cafes in Oslo"*, and see real data come back.

**What you're learning:** async HTTP in a tool, result trimming so you
don't blow the context, error handling that the agent can actually recover
from, and what a production tool body looks like.

✓ **Done when**: the agent answers *"find cafes in Oslo"* with real cafe
names (you can verify them on openstreetmap.org), and the tool returns
at most 15 results so the agent's context doesn't explode.

<details>
<summary>💡 Hint — Overpass query shape</summary>

Overpass QL is its own language, but the query for "cafes near a lat/lon"
is short:

```
[out:json][timeout:15];
(
  node["amenity"="cafe"](around:1000,59.9139,10.7522);
);
out center 15;
```

You POST that string (as form data `data=...` or as the raw body) to
`https://overpass-api.de/api/interpreter`. Response shape:

```json
{"elements": [{"type": "node", "id": 123, "lat": 59.9, "lon": 10.7,
               "tags": {"name": "Tim Wendelboe", "amenity": "cafe"}}, ...]}
```

Iterate `elements`, pull `tags.name`, return a list of dicts.
</details>

<details>
<summary>💡 Hint — turning "Oslo" into lat/lon</summary>

Two options, in order of effort:

1. **Hardcode a few cities** for the workshop. Oslo is 59.9139, 10.7522;
   Bergen is 60.3939, 5.3290. A dict lookup is fine for demo purposes.
2. **Real geocoding**: hit Nominatim
   (`https://nominatim.openstreetmap.org/search?q=Oslo&format=json&limit=1`).
   Respect their usage policy — set a real `User-Agent` header.

Option 1 is the right teaching choice. The point of the challenge is
**real data from a real API**, not building a geocoder.
</details>

<details>
<summary>💡 Hint — async HTTP with httpx</summary>

`httpx` is already in the deps. Pattern:

```python
import httpx

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

async def find_places_nearby(
    category: str, city: str, radius_m: int = 1000
) -> list[dict]:
    lat, lon = _CITY_COORDS.get(city.lower(), (None, None))
    if lat is None:
        return []  # or raise — see below

    query = f"""
    [out:json][timeout:15];
    (
      node["amenity"="{category}"](around:{radius_m},{lat},{lon});
    );
    out center 15;
    """
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(OVERPASS_URL, data={"data": query})
        r.raise_for_status()
        data = r.json()

    return [
        {"name": e["tags"].get("name", "unnamed"),
         "lat": e["lat"], "lon": e["lon"]}
        for e in data.get("elements", [])
    ][:15]
```

Register on the agent with `@agent.tool_plain` (async is fine,
pydantic-ai awaits tools automatically).
</details>

<details>
<summary>💡 Hint — be nice to the free API</summary>

Overpass is free but rate-limited. For a workshop you're fine, but:

- Set a timeout (`[out:json][timeout:15]` + `httpx` timeout).
- Send one request per turn, not a loop.
- If you get a 429 or a 504, let the tool raise — the agent's retry
  budget will handle it. Don't add a retry loop inside the tool; that's
  what `@agent.tool(retries=2)` is for.
- Set `User-Agent: navi-workshop/1.0` as a courtesy header.
</details>
