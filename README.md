# navi-workshop

A tiny Navi-style AI agent you can grow. Built on Pydantic AI + Logfire.

Mini-Navi is a GIS-flavored assistant with three mock tools (places, weather,
demographics). It's deliberately small so you can read every line, break it,
and add your own tools in minutes.

## Before the workshop

Create these accounts (5 min total). See `SETUP.md` for step-by-step.

1. **OpenAI API key** — we use `gpt-4o-mini`, costs ~$0.50 for the whole day.
2. **Logfire account + write token** — optional but strongly recommended.
3. **uv** installed + Python 3.11+.

## Setup (5 minutes)

```bash
# 1. clone, enter
cd navi-workshop

# 2. install (uv is fastest; pip works fine)
uv sync            # or: python -m venv .venv && .venv/bin/pip install -e .

# 3. env
cp .env.example .env
# add your OPENAI_API_KEY. LOGFIRE_TOKEN is optional but recommended.

# 4. run — pick one
uv run python server.py                       # web UI: http://localhost:8000
uv run python agent.py "what parks are in Oslo?"   # CLI
```

If Logfire is configured you'll see a link in the terminal to the trace —
click it and watch the tool-call timeline.

### Web UI vs CLI

You're going to modify `agent.py`, `tools/`, `eval.py`, and the `examples/`.
How you *trigger* the agent is up to you:

- **Web UI** (`server.py` + `frontend/`) — prebuilt chat interface with visible
  tool-call cards. Reload the page after editing `agent.py` or `tools/`. You
  shouldn't need to restart the server for Python changes if `--reload` is on,
  but explicit restarts are safer.
- **CLI** — `uv run python agent.py "your prompt"`. Faster for tight loops.
- **Eval** — `uv run python eval.py`. The source of truth for "is my change
  better or worse."

The frontend is a black box for the workshop. Don't feel obligated to touch it.

## What's here

| File | What it teaches |
|------|-----------------|
| `agent.py` | The core agent. Three tools, one system prompt, 50 lines. |
| `tools/` | Mock tool implementations. Swap for real APIs whenever. |
| `eval.py` | Deterministic eval harness. Five cases. Run it before and after every prompt change. |
| `examples/dynamic_tools.py` | Pattern: start with a small tool set, load more on demand. Context control. |
| `examples/subagent.py` | Pattern: orchestrator delegates to a specialist agent. Context isolation. |
| `server.py` | FastAPI wrapping the agent. You don't need to modify this. |
| `frontend/` | Prebuilt chat UI. You don't need to modify this. |
| `worktrees-demo/` | Live-demo script for running 3 agents in parallel via git worktrees. |
| `docs/team-cli-pattern.md` | Why a team CLI multiplies agent leverage. Starter script. |
| `CHALLENGES.md` | The ladder — pick your next stretch. |

## Run the eval

```bash
uv run python eval.py
```

Five cases. Pass/fail per case. Run it after every change you'd call "done."

## The patterns we teach

1. **Tools are cheap, context isn't.** Every tool you register costs tokens on
   every turn, forever. Curate them.
2. **Dynamic tool opening.** Start with a discovery tool; load specialist tools
   only when the agent asks. See `examples/dynamic_tools.py`.
3. **Sub-agents for isolation.** When a sub-task has its own domain (e.g.
   spatial analysis), give it its own agent with its own prompt and tools.
   See `examples/subagent.py`.
4. **Evals before vibes.** Deterministic checks > reading the output and
   squinting. LLM judges are useful for fuzzy correctness but they also lie.
5. **Iterate with traces.** Logfire shows the exact tool sequence. Read it.
   Most "the model is dumb" moments are actually prompt or schema problems.

## Next

Open `CHALLENGES.md`.
