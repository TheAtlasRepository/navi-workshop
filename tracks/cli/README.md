# Track 3 — Build a starter CLI

Wrap 3–5 verbs of your daily dev loop into one command. The deck pitched the
pattern (slide 28); now you ship a minimum viable version.

> **Goal**: leave the workshop with a `mycli` (or whatever you name it) that
> runs at least three commands and saves you keystrokes from day one. Grow it
> at home as repetition shows you which verbs to add next.

## The problem

Every team has ~20 workflows people run daily: bring up the dev stack, SSH to
staging, check logs, create a worktree, run the right slice of tests, open a
PR with the right template. Left as tribal knowledge, each of these is:

- a shell snippet in someone's notes, subtly different per person
- a README someone has to find
- a Slack thread from 2022

Agents have the exact same problem, amplified. Every Claude session that has
to reinvent "how do I start the dev stack" wastes tokens and gets it wrong
sometimes.

## The fix

Codify the 10–20 verbs your team runs daily into one CLI. Ours is `atlas`:

```
atlas upd           # bring up local services
atlas down          # tear down
atlas clean         # reset volumes
atlas wtt my-task   # create a worktree named my-task
atlas run logs      # tail the current env's logs
atlas run ssh       # ssh into the current env
atlas run remote    # switch to an EC2 dev env
```

One verb per workflow. Completions. Good `--help`. That's it.

## Why agents love it

- **Predictable commands.** `atlas wtt foo` is one line to get right. The
  open-coded version is four, with opinions.
- **Wrappable by skills/slash commands.** Your house workflows become
  `/create-worktree`, `/open-pr`, `/reset-stack`. Every agent session starts
  with the same leverage.
- **Auditable.** You can grep across agent traces for `atlas ` and see what
  the agents are actually doing.

## Starter: ~40 lines of bash + argparse

Don't over-engineer. Start with a shell router. Graduate to Python when you
need completions or rich help.

```bash
#!/usr/bin/env bash
# mycli — the starter version. Drop in ~/bin, chmod +x.
set -euo pipefail

cmd="${1:-help}"; shift || true

case "${cmd}" in
  upd)    docker compose up -d ;;
  down)   docker compose down ;;
  logs)   docker compose logs -f "$@" ;;
  wtt)
    name="${1:?usage: mycli wtt <name>}"
    git worktree add -b "feat/${name}" "../wt/${name}"
    echo "cd ../wt/${name}"
    ;;
  test)   pytest "$@" ;;
  help|*)
    cat <<EOF
mycli — team workflow CLI

  upd         bring services up
  down        tear services down
  logs        tail service logs (pass service name as arg)
  wtt <name>  create git worktree + branch
  test        run pytest
EOF
    ;;
esac
```

## Rules for growing it

1. **Add a verb when three people have each written their own snippet for it.**
   Not before. Premature CLI wrappers are worse than no CLI.
2. **Wrap, don't rewrite.** `atlas upd` shells out to `docker compose up -d`.
   Keep the underlying tool discoverable.
3. **Don't hide footguns.** If a command can nuke data, make it say so. `atlas
   clean` should prompt unless `--yes`.
4. **Short help, longer `--help-verb`.** One-line per verb at the top; deep
   details behind `atlas wtt --help`.
5. **Shell completions pay for themselves.** Worth the hour once the CLI has
   ten verbs.
6. **Tell your agents it exists.** Put a one-line reference in `CLAUDE.md` or
   equivalent so every session knows to reach for it.

