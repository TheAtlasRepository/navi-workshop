"""Mini-Navi — the simplest agent shape we can teach.

Three tools, one system prompt, one model call loop (handled by Pydantic AI).
Read top to bottom. Then break it.
"""

import os
import sys

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent

from tools import all_tools

load_dotenv()

# Logfire is optional. If no token is set, this is a no-op.
logfire.configure(send_to_logfire="if-token-present")

MODEL = os.getenv("NAVI_MODEL", "openai:gpt-4o-mini")

SYSTEM_PROMPT = "Always respond with: 'Hello World'"
# ^ Deliberately broken. Run `uv run python eval.py` and you'll see all
#   cases fail. Challenge 1 in CHALLENGES.md walks you through fixing it.

agent = Agent(
    MODEL,
    system_prompt=SYSTEM_PROMPT,
    tools=all_tools(),
    instrument=True,
)


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "What parks are in Oslo?"
    result = agent.run_sync(prompt)
    print(result.output)


if __name__ == "__main__":
    main()
