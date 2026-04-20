"""Sub-agent for a sub-domain.

When a task has its own vocabulary and tools (here: spatial analysis), handing
it to a specialist keeps the orchestrator's context small and the specialist's
behavior tight.

Trade-off: one extra model call per delegation. Worth it when the specialist's
prompt and tools would otherwise dominate every turn of the main conversation.

Run with Logfire on — you'll see the parent span with a nested specialist span.
That shape is what to aim for in production: clean, inspectable, isolated.
"""

import os
import sys

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent

from tools import get_population, get_weather, search_places

load_dotenv()
logfire.configure(send_to_logfire="if-token-present")

MODEL = os.getenv("NAVI_MODEL", "openai:gpt-4o-mini")


# ---- Specialist: spatial analysis -------------------------------------------

SPATIAL_PROMPT = """You are the spatial-analysis specialist.

You answer questions that require combining a place with its surroundings:
'how many people live near Y', 'what parks are close to Z'. Use search_places
and get_population. Keep the answer to one sentence."""

spatial_agent = Agent(MODEL, system_prompt=SPATIAL_PROMPT, instrument=True)
spatial_agent.tool_plain(search_places)
spatial_agent.tool_plain(get_population)


# ---- Orchestrator -----------------------------------------------------------

ORCHESTRATOR_PROMPT = """You are Mini-Navi (orchestrator variant).

Route, don't answer. You have two tools:
- get_weather: call directly for weather questions.
- delegate_spatial: hand off any question that needs combining places with
  nearby analysis (proximity, population-near, parks-near-X).

After a tool call you may respond directly to the user."""

orchestrator = Agent(MODEL, system_prompt=ORCHESTRATOR_PROMPT, instrument=True)
orchestrator.tool_plain(get_weather)


@orchestrator.tool_plain
async def delegate_spatial(question: str) -> str:
    result = await spatial_agent.run(question)
    return result.output


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "How many people live near Central Park?"
    result = orchestrator.run_sync(prompt)
    print(result.output)


if __name__ == "__main__":
    main()
