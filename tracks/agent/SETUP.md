# Setup

Do this before the workshop.

## 1. OpenAI API key

The workshop defaults to `openai:gpt-4o-mini` — capable, cheap (~$0.15 per million input tokens). A full day of hacking costs well under $1.

1. Go to [platform.openai.com](https://platform.openai.com/signup) and sign up.
2. Add **$5** of credit under Billing → Payment methods. (New accounts sometimes get free credit; if so, skip this.)
3. API keys → **Create new secret key**. Copy it. Save it somewhere you won't commit to git.

Heads up: OpenAI keys start with `sk-...`. If you see one in a PR diff, rotate it.

## 2. Logfire (optional but strongly recommended)

Half the workshop is about reading traces. Without Logfire the code still runs — you just miss the payoff.

1. Go to [logfire.pydantic.dev](https://logfire.pydantic.dev) and sign up (GitHub login works).
2. Create a new project. Any name.
3. **Write tokens** → create one. Copy it.

## 3. Tooling

```bash
# Python 3.11+ — check with:
python3 --version

# uv (fastest Python package manager):
curl -LsSf https://astral.sh/uv/install.sh | sh
# restart your shell or: source ~/.zshrc

# verify
uv --version
```

If you already use pip/poetry/pdm those will work too — `uv` is just what the commands in README.md assume.

## 4. Git + editor

- Git. You already have it.
- An editor with **[Claude Code](https://claude.ai/code)** installed (or Cursor, or whichever AI-first editor you prefer). The afternoon practical uses it for the hands-on tracks.

## 5. Wire it up

```bash
cd navi-workshop
cp .env.example .env
# paste your keys into .env
uv sync
uv run python agent.py "what parks are in Oslo?"
```

Expected output: a short natural-language answer + a link to a Logfire trace in the terminal. Click the link — you should see a tool-call timeline.

If you see a link but the trace is empty, the Logfire token isn't wired. If you see no link at all, double-check `OPENAI_API_KEY` is set.

Now run the web UI:

```bash
uv run python server.py
```

Open [http://localhost:8000](http://localhost:8000). Click one of the example prompts. You should see a chat response with expandable tool-call cards.

## 6. Presentation track (no keys needed)

If you're doing the presentation track instead: just open `presentation-starter/index.html` in a browser. That's the whole setup.

---

## Troubleshooting

**`uv: command not found` after install** — restart your shell. On macOS it adds itself to `~/.local/bin`.

**`Error: missing API key`** — `.env` must be in the repo root, not in a subfolder. Check `ls -la` shows it.

**Model name errors** — Pydantic AI occasionally renames model identifiers between versions. If `openai:gpt-4o-mini` fails, try `openai:gpt-4.1-mini` or check the [Pydantic AI models docs](https://ai.pydantic.dev/models/).

**Logfire not showing traces** — make sure `logfire.configure()` has run (it's at the top of `agent.py`). Check `LOGFIRE_TOKEN` is in `.env` and starts with `pylf_`.
