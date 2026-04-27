# Challenges

A ladder. Do them in order; each builds on the last. If you finish, switch to
one of the other tracks: presentation builder (`tracks/presentation/`) or the
starter CLI (`tracks/cli/`).

Every challenge has a ✓ **Success criteria** line so you know when to move on.
Click the 💡 **Hint** blocks if you get stuck.

---

## 1. Add a tool

Add a `get_elevation` tool that returns a mock elevation in meters. Follow
the pattern in `tools/weather.py`:

- A `GetElevationParams(BaseModel)` for the input — pydantic-ai turns this
  into the function-call schema the model sees, with `Field(description=...)`
  showing up as the tool's parameter docs.
- An `ElevationResult(BaseModel)` for the return — typed, validated, and
  serialized back to the model as JSON.
- `def get_elevation(params: GetElevationParams) -> ElevationResult: ...`
- Decorate it with **`@register_tool`** (imported from `tools`). The agent
  picks up every `@register_tool` function automatically — no list to edit.

Add a one-line import in `tools/__init__.py` (`from tools import elevation`
near the other tool-module imports) so the decorator runs at import time.
Optionally also re-export your function and models alongside the others.

Ask the app *"what's the elevation of Mount Everest?"* and watch the Logfire
trace.

**What you're learning:** the tool-call loop, Pydantic AI's BaseModel
pattern, and the simplest registration pattern (decorator + collector). The
model picks a tool, pydantic-ai validates the args into your model, you run,
you return a model, it goes back as JSON, the model answers.

✓ **Done when**: the app answers the Everest question with a number, and
Logfire shows a `get_elevation` span in the trace.

---

## 2. Fix the system prompt

Run `uv run python eval.py`. **6/7 pass; one fails:** `chain_landmark_elevation`.
Open the Logfire trace on that case and look at what the model actually did.

You'll see the model called `get_elevation` directly on a landmark name it
picked from training (something like "Holmenkollen Ski Jump") — never
calling `search_places` to ground in our database first. Mock returns a
plausible-looking number, model reports it as fact. **Two failures stacked:
no chaining, no sanity check on absurd values.**

Fix the `SYSTEM_PROMPT` in `agent.py` so the agent stops doing this. The
existing rule *"Chain tools when needed"* is too vague — be specific. Try
a rule that names the failure mode: *for "highest/largest/oldest X in Y"
questions, ground the X in `search_places` first, then chain other tools
on the results.* Or: *don't pick place names from training; only use
names returned by `search_places` or names the user explicitly mentioned.*

Rerun the eval. All seven should pass. **Bonus**: confirm you didn't
regress the easy cases by reading their tool-call columns — they should
still call the obvious tool, not a redundant chain.

**What you're learning:** prompts are code. Generic rules get generic
behavior; specific rules that name the failure mode get specific
behavior. The eval suite is what tells you whether your edit helped or
hurt — vibes aren't enough.

✓ **Done when**: 7/7 pass. Bonus: read the trace on
`chain_landmark_elevation` after the fix and confirm the model actually
called `search_places` first.

> **Note on the *meta* lesson**: with gpt-4o-mini and crisp `Field`
> descriptions, the agent is hard to break with prompt changes alone.
> Most red-baseline failures at this scale come from *missing structural
> guidance* (chaining, grounding) rather than *missing rules of thumb*.
> Your prompt rule for this case earns its keep because it teaches a
> sequence, not a preference. Hold this in mind when you write Challenge 5
> later — *the case you write* is what catches the next bug, not the
> prompt that fixed this one.

---

## 3. Convert `agent.py` to dynamic tool opening

Right now every tool's JSON schema is in the request on every turn, whether
the model uses it or not. With four tiny tools that's nothing — but Navi has
~20 real tools and would be burning ~10k tokens per turn on overhead.

You're going to convert `agent.py` so that closed tools are *absent* from
the schemas the model sees. The model gets a one-line teaser of what's
available, opens the tool it wants, then calls it. The pre-shipped tools
(`search_places`, `get_weather`, `get_population`) already have their
prompt files at `prompts/<tool>/{minimized,maximized}.md` — you just need
to wire them up.

**Write prompts for any tool you added in Challenge 1.** Your `get_elevation`
tool needs `prompts/get_elevation/minimized.md` (one-line teaser the model
sees in the system menu) and `prompts/get_elevation/maximized.md` (the full
manual that gets swapped in once the tool is opened). Copy
`prompts/get_weather/` as a shape and edit. Without these, the dynamic
agent's menu will list `get_elevation` with an empty teaser.

**Capture the baseline first.** Run `uv run python agent.py "what's the
weather and population in Oslo?"` and note the **input token count** on the
first turn in Logfire. After the conversion, the same question's first turn
should be much smaller.

### The conversion (six edits to `agent.py`)

1. **Add a `Deps` model** to hold the per-run set of opened tools:
   ```python
   from pydantic import BaseModel, Field

   class Deps(BaseModel):
       opened_tools: set[str] = Field(default_factory=set)
   ```

2. **Add a markdown loader** for the per-tool prompt files in `prompts/`:
   ```python
   from pathlib import Path
   PROMPTS_DIR = Path(__file__).parent / "prompts"

   def _load_md(tool: str, kind: str) -> str:
       p = PROMPTS_DIR / tool / f"{kind}.md"
       return p.read_text().strip() if p.exists() else ""
   ```

3. **Add a `prepare_tools` hook.** Pydantic AI calls it before every model
   turn; whatever you return is what the model sees:
   ```python
   import dataclasses
   from pydantic_ai import RunContext
   from pydantic_ai.tools import ToolDefinition

   ALWAYS_OPEN = {"open_tool"}

   async def prepare_tools(ctx: RunContext[Deps], tool_defs: list[ToolDefinition]):
       out = []
       for t in tool_defs:
           if t.name in ALWAYS_OPEN:
               out.append(t)
           elif t.name in ctx.deps.opened_tools:
               manual = _load_md(t.name, "maximized")
               out.append(dataclasses.replace(t, description=manual) if manual else t)
           # closed → silently dropped from the request
       return out
   ```

4. **Wire `prepare_tools` and `Deps` into the `Agent` constructor**:
   ```python
   agent = Agent(
       MODEL,
       deps_type=Deps,
       system_prompt=SYSTEM_PROMPT,
       prepare_tools=prepare_tools,
       tools=all_tools(),
       instrument=True,
   )
   ```

5. **Add an `open_tool` meta-tool** so the model can move a name into
   `opened_tools` and get the full manual back:
   ```python
   TOOL_NAMES = {fn.__name__ for fn in all_tools()}

   @agent.tool
   async def open_tool(ctx: RunContext[Deps], name: str) -> str:
       """Open a tool so you can call it. Returns its full manual."""
       if name not in TOOL_NAMES:
           return f"unknown tool: {name}"
       ctx.deps.opened_tools.add(name)
       return _load_md(name, "maximized") or f"opened {name}"
   ```

6. **Add a dynamic `@agent.system_prompt`** so the model sees the menu of
   *closed* tools each run:
   ```python
   @agent.system_prompt
   def closed_tool_menu(ctx: RunContext[Deps]) -> str:
       closed = sorted(TOOL_NAMES - ctx.deps.opened_tools)
       if not closed:
           return ""
       lines = [f"- **{n}** — {_load_md(n, 'minimized')}" for n in closed]
       return "Available tools (call `open_tool(name)` to open):\n" + "\n".join(lines)
   ```

7. **Pass deps when running**:
   ```python
   def main():
       prompt = " ".join(sys.argv[1:]) or "What parks are in Oslo?"
       result = agent.run_sync(prompt, deps=Deps())
       print(result.output)
   ```

You'll also want to tighten the system prompt so the model knows it has to
call `open_tool` before using anything.

**What you're learning:** pydantic-ai's two key hooks (`prepare_tools` for
filtering schemas per turn, dynamic `@agent.system_prompt` for refreshing
the prompt each run) and how Navi keeps its tool surface from blowing up
the context. The minimized/maximized markdown files mean prompt iteration
is a git diff, not a Python edit.

✓ **Done when**: same question's first turn uses meaningfully fewer input
tokens (in Logfire), and the trace shows `open_tool("get_weather")` →
`get_weather(...)` instead of all tools' schemas in the initial request.

<details>
<summary>📎 Full reference solution (peek if stuck)</summary>

```python
"""Mini-Navi — dynamic tool opening variant."""
from __future__ import annotations

import dataclasses
import os
import sys
from pathlib import Path

import logfire
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import ToolDefinition

from tools import all_tools

load_dotenv()
logfire.configure(send_to_logfire="if-token-present")

MODEL = os.getenv("NAVI_MODEL", "openai:gpt-4o-mini")
PROMPTS_DIR = Path(__file__).parent / "prompts"

ALWAYS_OPEN = {"open_tool"}
TOOL_NAMES = {fn.__name__ for fn in all_tools()}


def _load_md(tool: str, kind: str) -> str:
    p = PROMPTS_DIR / tool / f"{kind}.md"
    return p.read_text().strip() if p.exists() else ""


class Deps(BaseModel):
    opened_tools: set[str] = Field(default_factory=set)


SYSTEM_PROMPT = """You are Mini-Navi, a GIS assistant.

You start with one tool — `open_tool(name)` — and a menu of others below.
Open a tool only when you're about to use it, then call it directly.

Rules:
- Prefer tools over guessing.
- Chain tools when needed.
- Keep answers short. One or two sentences unless the user asks for detail.
"""


async def prepare_tools(ctx: RunContext[Deps], tool_defs: list[ToolDefinition]):
    out = []
    for t in tool_defs:
        if t.name in ALWAYS_OPEN:
            out.append(t)
        elif t.name in ctx.deps.opened_tools:
            manual = _load_md(t.name, "maximized")
            out.append(dataclasses.replace(t, description=manual) if manual else t)
    return out


agent = Agent(
    MODEL,
    deps_type=Deps,
    system_prompt=SYSTEM_PROMPT,
    prepare_tools=prepare_tools,
    tools=all_tools(),
    instrument=True,
)


@agent.tool
async def open_tool(ctx: RunContext[Deps], name: str) -> str:
    """Open a tool so you can call it. Returns its full manual."""
    if name not in TOOL_NAMES:
        return f"unknown tool: {name}"
    ctx.deps.opened_tools.add(name)
    return _load_md(name, "maximized") or f"opened {name}"


@agent.system_prompt
def closed_tool_menu(ctx: RunContext[Deps]) -> str:
    closed = sorted(TOOL_NAMES - ctx.deps.opened_tools)
    if not closed:
        return ""
    lines = [f"- **{n}** — {_load_md(n, 'minimized')}" for n in closed]
    return "Available tools (call `open_tool(name)` to open):\n" + "\n".join(lines)


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "What parks are in Oslo?"
    result = agent.run_sync(prompt, deps=Deps())
    print(result.output)


if __name__ == "__main__":
    main()
```
</details>

---

## 4. Sub-agent for a sub-domain

`examples/subagent.py` has an orchestrator + a spatial-analysis specialist.
First, run it to see the current shape:

```bash
uv run python examples/subagent.py "How many people live near Central Park?"
```

Open the Logfire trace — you'll see the orchestrator span with a nested
`delegate_spatial` → `spatial_agent` span underneath.

Now: add a second specialist — a **demographics-analyst** — with its own
prompt and its own tool set. Route to it from the orchestrator.

Measure: trace depth, total tokens per query, end-to-end latency. Compare
to the monolithic `agent.py`.

**What you're learning:** sub-agents trade latency for context discipline.
The orchestrator stays small; specialists do the heavy lifting in isolation.

✓ **Done when**: a demographics-flavored question produces a nested span
in Logfire for the demographics agent, and a weather question does *not*
touch either specialist. Verify with:

```bash
uv run python examples/subagent.py "How many people live in Bergen?"
uv run python examples/subagent.py "What's the weather in Oslo?"
```

<details>
<summary>💡 Hint — the delegation pattern</summary>

Copy the `spatial_agent` + `delegate_spatial` pattern. Use the `tools=[...]`
constructor arg, like the existing specialist:

```python
demographics_agent = Agent(
    MODEL,
    system_prompt=DEMOGRAPHICS_PROMPT,
    tools=[get_population],
    instrument=True,
)

@orchestrator.tool_plain
async def delegate_demographics(question: str) -> str:
    """Hand a demographics question to the demographics specialist."""
    result = await demographics_agent.run(question)
    return result.output
```

Update the orchestrator system prompt so it knows when to route to which
specialist. The routing rule is the whole point — make it explicit.
</details>

---

## 5. Write a real eval case

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
    name="bergen_chain",
    prompt="What's the weather in Bergen and how many people live there?",
    expected_tools={"get_weather", "get_population"},  # must call both
    expected_in_output=["Bergen"],
)
```

If this passes on first run, congratulations — your agent is better than most
agents in the wild. Try one with an *implicit* chain:

```python
Case(
    name="implicit_chain",
    prompt="I'm visiting Bergen tomorrow — anything I should know?",
    expected_tools={"get_weather", "get_population"},
    expected_in_output=["Bergen"],
)
```

To fix, tighten the system prompt with a rule like *"When a user asks about
a place, call every relevant tool before answering — don't skip tools because
one answer is 'obvious'."*
</details>

> **Production note**: this hand-rolled `eval.py` is here to *show* what an
> eval is — five readable cases, a substring check, a tool-call check, a Rich
> table. In production you'd reach for [`pydantic-evals`](https://ai.pydantic.dev/evals/),
> the official sister package: typed `Dataset` + `Case`, parallel runs,
> built-in evaluators (`Contains`, `LLMJudge`, `IsInstance`), structured
> reports (markdown / JSON), and clean integration with pydantic-ai's run
> history. Same idea, more battle-tested. Skip the harness — keep the
> mindset.

---

## 6. LLM-as-judge (optional)

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

## 7. Stretch: real data via Overpass

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
