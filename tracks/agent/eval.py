"""Deterministic eval harness.

Five cases. Each checks:
- expected_tools: tool names that must appear in the trace
- expected_in_output: substrings that must appear in the final answer

Run after every prompt or tool change. If a case breaks, look at Logfire first.
"""

import logfire
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai.messages import ToolCallPart
from rich.console import Console
from rich.table import Table

from agent import agent

load_dotenv()
logfire.configure(send_to_logfire="if-token-present")


class Case(BaseModel):
    name: str
    prompt: str
    expected_tools: set[str]
    expected_in_output: list[str] = Field(default_factory=list)


CASES = [
    Case(
        name="weather_direct",
        prompt="What's the weather in Oslo?",
        expected_tools={"get_weather"},
        expected_in_output=["Oslo"],
    ),
    Case(
        name="places_direct",
        prompt="What parks are in Oslo?",
        expected_tools={"search_places"},
        expected_in_output=["park"],
    ),
    Case(
        name="population_direct",
        prompt="How many people live in Bergen?",
        expected_tools={"get_population"},
        expected_in_output=["Bergen"],
    ),
    Case(
        name="multi_tool",
        prompt="Find parks in Oslo and tell me the weather there.",
        expected_tools={"search_places", "get_weather"},
        expected_in_output=["Oslo"],
    ),
    Case(
        name="no_tool_needed",
        prompt="What does GIS stand for?",
        expected_tools=set(),
        expected_in_output=["geographic"],
    ),
    Case(
        name="prefers_tool_over_training",
        prompt="What's the elevation of Mount Everest?",
        expected_tools={"get_elevation"},
        expected_in_output=["Everest"],
    ),
    Case(
        name="chain_landmark_elevation",
        prompt="What's the elevation of the highest landmark in Oslo?",
        expected_tools={"search_places", "get_elevation"},  # must ground via DB before elevation
        expected_in_output=["Oslo"],
    ),
]


def tools_used(result) -> set[str]:
    called: set[str] = set()
    for msg in result.all_messages():
        for part in getattr(msg, "parts", []):
            if isinstance(part, ToolCallPart):
                called.add(part.tool_name)
    return called


def run_case(case: Case) -> dict:
    result = agent.run_sync(case.prompt)
    called = tools_used(result)
    out_lower = result.output.lower()
    tool_ok = case.expected_tools.issubset(called)
    output_ok = all(s.lower() in out_lower for s in case.expected_in_output)
    return {
        "case": case.name,
        "called": called,
        "output": result.output[:80],
        "tool_ok": tool_ok,
        "output_ok": output_ok,
        "pass": tool_ok and output_ok,
    }


def main() -> None:
    console = Console()
    results = [run_case(c) for c in CASES]
    table = Table(title="Mini-Navi eval")
    for col in ["case", "tool_ok", "output_ok", "called", "output"]:
        table.add_column(col)
    for r in results:
        style = "green" if r["pass"] else "red"
        table.add_row(
            r["case"],
            "pass" if r["tool_ok"] else "fail",
            "pass" if r["output_ok"] else "fail",
            ", ".join(sorted(r["called"])) or "-",
            r["output"],
            style=style,
        )
    console.print(table)
    passed = sum(r["pass"] for r in results)
    console.print(f"\n{passed}/{len(results)} passed")


if __name__ == "__main__":
    main()
