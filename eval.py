"""Deterministic eval harness.

Five cases. Each checks:
- expected_tools: tool names that must appear in the trace
- expected_in_output: substrings that must appear in the final answer

Run after every prompt or tool change. If a case breaks, look at Logfire first.
"""

from dataclasses import dataclass, field

import logfire
from dotenv import load_dotenv
from pydantic_ai.messages import ToolCallPart
from rich.console import Console
from rich.table import Table

from agent import agent

load_dotenv()
logfire.configure(send_to_logfire="if-token-present")


@dataclass
class Case:
    name: str
    prompt: str
    expected_tools: set[str]
    expected_in_output: list[str] = field(default_factory=list)


CASES = [
    Case("weather_direct", "What's the weather in Oslo?", {"get_weather"}, ["Oslo"]),
    Case("places_direct", "What parks are in Oslo?", {"search_places"}, ["park"]),
    Case("population_direct", "How many people live in Bergen?", {"get_population"}, ["Bergen"]),
    Case(
        "multi_tool",
        "Find parks in Oslo and tell me the weather there.",
        {"search_places", "get_weather"},
        ["Oslo"],
    ),
    Case("no_tool_needed", "What does GIS stand for?", set(), ["geographic"]),
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
