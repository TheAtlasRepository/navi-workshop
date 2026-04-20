# Live demo cheat sheet

For the devex talk. Rehearse once before the session — the timing is tight.

## Setup (do before the talk)

```bash
cd path/to/navi-workshop
./worktrees-demo/demo.sh up
```

Open 4 terminals, arranged side-by-side if possible:
- `main`: the root repo
- `task-1`, `task-2`, `task-3`: one per worktree, each with `claude` open

## Script

1. **(20s) Show `git worktree list`** — "one branch, one working tree, one
   agent. They don't stomp on each other."

2. **(40s) Prompt task-1 agent**: "Read TASK.md and implement it. Run the eval
   before and after. Commit when green." Hit enter.

3. **(20s) Switch to task-2 terminal**, same treatment. Same for task-3.

4. **(2 min) Narrate** while they work:
   - "All three are running. My context is clean — I'm not holding their code
     in my head."
   - "The eval is the handshake. Green eval = ready to review."
   - Point at the trees they're generating in real time.

5. **(1 min) Show the PR loop** — once one finishes, show `gh pr create`
   from the worktree, review the diff in main.

6. **(30s) Honest caveats**:
   - "This only works when tasks are genuinely independent. If task-1 and
     task-2 would touch the same file, they'd conflict and you'd have saved
     nothing."
   - "You are the bottleneck now — review. That's actually the point. You
     spend your attention on what matters."

## Cleanup

```bash
./worktrees-demo/demo.sh clean
```

## If something goes sideways

- Agent gets stuck: tell it "check TASK.md again and narrow the scope."
- Worktree won't create: `git worktree prune` then re-run `demo.sh up`.
- Nothing is working: skip to the `git worktree list` + slide explanation. The
  idea is what matters, not a perfect live demo.
