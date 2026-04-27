# navi-workshop

Three tracks. Pick one. Each is self-contained inside `tracks/`.

| Track | What you build | Where it lives |
|---|---|---|
| **01 · Build an agent** | A tiny Navi-style AI agent with Pydantic AI + Logfire. Tools, evals, dynamic tool opening, sub-agents. | [`tracks/agent/`](tracks/agent/README.md) |
| **02 · Build a presentation** | A deck on a topic of your choice using the Atlas slide template. Open it in your browser. | [`tracks/presentation/`](tracks/presentation/README.md) |
| **03 · Build a starter CLI** | Three to five verbs of your daily dev loop, wrapped in one command. 40 lines of bash to start. | [`tracks/cli/`](tracks/cli/README.md) |

Each track has its own README, setup, and challenge ladder. Pick the one
that's most useful to your day-to-day, ship something small, show it at the
end (optional — local is fine).

## Working with worktrees (optional)

If you want to run multiple agents in parallel on different branches, use
git worktrees. Each worktree is a separate working copy bound to a different
branch — same `.git`, different filesystem path, no checkout dance.

```bash
# create a new worktree on a new branch (off main)
git worktree add ../navi-feature-A -b feature-A

# create a worktree on an existing branch
git worktree add ../navi-bugfix existing-branch-name

# what's running
git worktree list

# clean up after merging
git worktree remove ../navi-feature-A
git worktree prune
```

Open each worktree's directory in its own Claude Code session (or terminal).
Three independent branches, three agents, no stepping on each other. This is
exactly what the team CLI in track 3 wraps into one verb.
