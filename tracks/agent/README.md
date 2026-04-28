# Track 1 — Build an agent

A tiny Navi-style AI agent you can grow. Built on Pydantic AI + Logfire.

Mini-Navi is a GIS-flavored assistant with three mock tools (places, weather,
demographics). It's deliberately small so you can read every line, break it,
and add your own tools quickly.

## Before the workshop

Create these accounts. See `SETUP.md` for step-by-step.

1. **OpenAI API key** — we use `gpt-4o-mini`, low single-digit-dollar cost.
2. **Logfire account + write token** — optional but strongly recommended.
3. **Python 3.11+** and **uv** installed (next section).

## Install uv

[uv](https://docs.astral.sh/uv/) is the fastest Python package manager and what
the commands below assume. Install once:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# or with Homebrew
brew install uv

# verify
uv --version
```

If `uv: command not found` after install, restart your shell — uv adds itself
to `~/.local/bin` (or `~/.cargo/bin`).

If you already use pip / poetry / pdm those work too — `uv` is just the
default in this README.

## Setup

```bash
cd tracks/agent
uv sync                                            # creates .venv, installs deps
cp .env.example .env
# add your OPENAI_API_KEY. LOGFIRE_TOKEN is optional but recommended.

# run — pick one
uv run python server.py                            # web UI: http://localhost:8000
uv run python agent.py "what parks are in Oslo?"   # CLI
```

If Logfire is configured you'll see a link in the terminal to the trace —
click it and watch the tool-call timeline.

### Web UI vs CLI

You're going to modify `agent.py`, `tools/`, `eval.py`, and the `examples/`.
How you *trigger* the agent is up to you:

- **Web UI** (`server.py` + `frontend/`) — prebuilt chat interface with visible
  tool-call cards. Reload the page after editing `agent.py` or `tools/`.
- **CLI** — `uv run python agent.py "your prompt"`. Faster for tight loops.
- **Eval** — `uv run python eval.py`. The source of truth for "is my change
  better or worse."

The frontend is a black box for the workshop. Don't feel obligated to touch it.

## What's here

| File | What it teaches |
|------|-----------------|
| `agent.py` | The core agent. Three tools, one system prompt, 50 lines. |
| `tools/` | Mock tool implementations. Decorate with `@register_tool` and they're picked up automatically. |
| `prompts/<tool>/` | `minimized.md` (teaser) + `maximized.md` (full manual) per tool. Used after Challenge 3 converts the agent to dynamic tool opening. |
| `eval.py` | Deterministic eval harness. Run it before and after every prompt change. |
| `examples/subagent.py` | Pattern: orchestrator delegates to a specialist agent. Context isolation. |
| `server.py` | FastAPI wrapping the agent. You don't need to modify this. |
| `frontend/` | Prebuilt chat UI. You don't need to modify this. |
| `CHALLENGES.md` | The ladder — pick your next stretch. |

## Run the eval

```bash
uv run python eval.py
```

Run it after every change you'd call "done."

## The patterns we teach

1. **Pydantic for everything the model touches.** Tool params and returns are
   `BaseModel`s. Field descriptions become the tool's JSON schema. Validation
   is free.
2. **Tools are cheap, context isn't.** Every tool you register costs tokens on
   every turn, forever. Curate them.
3. **Dynamic tool opening.** Start with a discovery tool; load specialist tools
   only when the agent asks. Challenge 3 walks you through converting the
   static agent to this pattern.
4. **Sub-agents for isolation.** When a sub-task has its own domain (e.g.
   spatial analysis), give it its own agent with its own prompt and tools.
   See `examples/subagent.py`.
5. **Evals before vibes.** Deterministic checks > reading the output and
   squinting. LLM judges are useful for fuzzy correctness but they also lie.
6. **Iterate with traces.** Logfire shows the exact tool sequence. Read it.
   Most "the model is dumb" moments are actually prompt or schema problems.

## Next

Open `CHALLENGES.md`.
