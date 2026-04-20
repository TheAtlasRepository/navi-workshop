# Worktrees demo

Live-demo material for the devex talk. Shows three independent tasks running
in three git worktrees, each one suitable for its own agent session.

## The point

One branch = one agent. When tasks are genuinely independent (no shared files,
no overlapping migrations), you can fan out across worktrees and collect PRs
back. You become the orchestrator; the bottleneck moves to review.

## What's here

- `demo.sh` — creates 3 worktrees from this repo, pre-loaded with one task each
- `tasks/task-1.md` — add an elevation tool
- `tasks/task-2.md` — add an LLM-as-judge eval
- `tasks/task-3.md` — add a fourth category to the dynamic-tools example
- `cheat-sheet.md` — what to say live, in order

## Run it

From this directory:

```bash
./demo.sh
```

This creates `../wt/task-1`, `../wt/task-2`, `../wt/task-3` as worktrees on
branches `demo/task-1`, `demo/task-2`, `demo/task-3`. Each worktree has the
task description dropped into `TASK.md` so an agent opened in that directory
starts with full context.

## Cleanup

```bash
./demo.sh clean
```

Removes the worktrees and branches.
