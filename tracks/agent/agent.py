"""Mini-Navi — the simplest agent shape we can teach.

Three tools, one system prompt, one model call loop (handled by Pydantic AI).
Read top to bottom. Then break it.
"""

import os
import sys

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent

from tools import get_population, get_weather, search_places

load_dotenv()

# Logfire is optional. If no token is set, this is a no-op.
logfire.configure(send_to_logfire="if-token-present")

MODEL = os.getenv("NAVI_MODEL", "openai:gpt-4o-mini")

SYSTEM_PROMPT = """You are Mini-Navi, a GIS assistant.

You help users answer spatial questions about places, weather, and demographics.

Rules:
- Prefer tools over guessing. If a user asks about a place's weather, call get_weather.
- Chain tools when needed. "Schools near rainy areas in Bergen" = search_places + get_weather.
- Keep answers short. One or two sentences unless the user asks for detail.
- If a tool returns nothing useful, say so plainly. Don't hallucinate data.
"""

agent = Agent(MODEL, system_prompt=SYSTEM_PROMPT, instrument=True)

agent.tool_plain(search_places)
agent.tool_plain(get_weather)
agent.tool_plain(get_population)


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "What parks are in Oslo?"
    result = agent.run_sync(prompt)
    print(result.output)


if __name__ == "__main__":
    main()
