# Task 3 — Add a fourth category to the dynamic-tools example

Extend `examples/dynamic_tools.py` to expose a new domain without growing the
base prompt.

Steps:
1. Add a `get_traffic(location: str) -> dict` mock (follow the weather pattern).
   Put it in `tools/traffic.py`, export from `tools/__init__.py`.
2. Register it in the REGISTRY in `dynamic_tools.py`.
3. Don't touch the SYSTEM_PROMPT of the dynamic agent.
4. Ask the dynamic agent "is there traffic in Oslo?" and confirm it discovers
   the tool via list_tools → get_tool_docs → invoke_tool.
5. Compare the Logfire trace for this vs. running the same question through
   `agent.py` (after registering the tool there too). Write your observations
   as comments at the top of `dynamic_tools.py`.

The point: adding a capability to the dynamic variant costs one REGISTRY entry;
adding it to the static variant grows every turn's input forever.
