"""Dynamic tool opening.

Context is expensive. Every tool schema you register costs tokens on every turn
of every conversation, forever. For large tool sets this dominates. The trick
is to expose a tiny *discovery* surface and let the model pull in specific
tools on demand.

Run this and agent.py side by side. Same prompt, different token usage.
The trace in Logfire will show which tools were called per turn.

Pattern:
    list_tools        → cheap catalog call, one-line summaries
    get_tool_docs     → full signature for a specific tool
    invoke_tool       → runs the real thing

Trade-off: more turns per answer (discovery → docs → invoke), but dramatically
smaller per-turn schema cost. Wins when the tool catalog is large or rarely
needed in full.
"""

import json
import os
import sys
from typing import Any

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent

from tools import get_population, get_weather, search_places

load_dotenv()
logfire.configure(send_to_logfire="if-token-present")

MODEL = os.getenv("NAVI_MODEL", "openai:gpt-4o-mini")


REGISTRY: dict[str, dict[str, Any]] = {
    "search_places": {
        "fn": search_places,
        "summary": "Search for parks, cafes, landmarks by name or category.",
        "signature": "search_places(query: str, near: str | None = None) -> list[dict]",
    },
    "get_weather": {
        "fn": get_weather,
        "summary": "Current weather for a named location.",
        "signature": "get_weather(location: str) -> dict",
    },
    "get_population": {
        "fn": get_population,
        "summary": "Population and median age for a named location.",
        "signature": "get_population(location: str) -> dict",
    },
}


SYSTEM_PROMPT = """You are Mini-Navi (dynamic variant).

You have three meta-tools:
- list_tools(): returns all available tools with one-line summaries.
- get_tool_docs(name): returns the full signature for one tool.
- invoke_tool(name, arguments_json): runs the tool. arguments_json must be valid JSON.

Procedure: call list_tools first to discover capabilities, get_tool_docs only
for tools you plan to use, then invoke_tool. Minimize discovery calls — don't
fetch docs you won't use.
"""

agent = Agent(MODEL, system_prompt=SYSTEM_PROMPT, instrument=True)


@agent.tool_plain
def list_tools() -> list[dict]:
    return [{"name": n, "summary": v["summary"]} for n, v in REGISTRY.items()]


@agent.tool_plain
def get_tool_docs(name: str) -> str:
    if name not in REGISTRY:
        return f"no such tool: {name}"
    return REGISTRY[name]["signature"]


@agent.tool_plain
def invoke_tool(name: str, arguments_json: str) -> Any:
    if name not in REGISTRY:
        return f"no such tool: {name}"
    try:
        args = json.loads(arguments_json)
    except json.JSONDecodeError as e:
        return f"invalid JSON: {e}"
    return REGISTRY[name]["fn"](**args)


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "What's the weather in Oslo?"
    result = agent.run_sync(prompt)
    print(result.output)


if __name__ == "__main__":
    main()
