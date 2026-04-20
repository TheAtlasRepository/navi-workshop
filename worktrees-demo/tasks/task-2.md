# Task 2 — Add an LLM-as-judge eval

Add a judge function at the bottom of `eval.py` that uses a separate Pydantic AI
agent to grade one free-form case.

Steps:
1. Add a new case `Case("friendly_tone", "Where is Bergen?", {"search_places"}, [])`
   — no substring check, tone is the criterion.
2. Write `judge(prompt, output) -> int` that runs a tiny Pydantic AI agent with
   a rubric (1–5, clarity and friendliness). Model string can be the same as
   the main agent.
3. Integrate it into `run_case` so the judge runs only on cases that opt in
   (add a `judge: bool = False` field to `Case`).
4. Print the judge score alongside pass/fail.
5. Run the eval five times on the same case. Note the variance in scores.
   Add a comment at the bottom of `eval.py` with what you observed.

The point of the exercise isn't a perfect judge — it's *seeing* why judges are
noisier than substring checks.
