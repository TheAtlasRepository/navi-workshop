# Challenges

A ladder for the starter-CLI track. The goal is to leave the workshop with a
small `mycli` that runs at least three commands you actually use.

Read `README.md` for the *why*. This file is the *how* — start at the top,
build up.

---

## 1. The simplest possible CLI — three lines, one minute

A CLI tool is just **a file with a shebang that you can run from the terminal**.
Nothing more. Build the minimum:

```bash
mkdir -p ~/bin
cat > ~/bin/mycli <<'EOF'
#!/usr/bin/env bash
echo "hello, $USER"
EOF
chmod +x ~/bin/mycli
~/bin/mycli
```

You should see `hello, jesper` (or whatever your username is). **You just
shipped a CLI tool.** It does one thing — but it works.

✓ **Done when**: `~/bin/mycli` runs and prints "hello, <your name>".

---

## 2. Take an argument

A CLI takes commands. Make `mycli` accept one argument:

```bash
cat > ~/bin/mycli <<'EOF'
#!/usr/bin/env bash
echo "you ran: $1"
EOF
~/bin/mycli hello
~/bin/mycli something-else
```

`$1` is the first argument the user typed. `$2` is the second, and so on.

✓ **Done when**: `mycli foo` prints `you ran: foo`.

---

## 3. Branch on the argument (the case statement)

This is the heart of a CLI: based on what the user typed, do different things.
The shape is `case <variable> in <pattern>) <command> ;; esac`.

```bash
cat > ~/bin/mycli <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

cmd="${1:-help}"   # if no arg, default to "help"

case "${cmd}" in
  date)   date ;;
  user)   echo "you are $USER" ;;
  pwd)    pwd ;;
  help|*) echo "usage: mycli [date|user|pwd]" ;;
esac
EOF
~/bin/mycli date     # prints today's date
~/bin/mycli user     # prints "you are jesper"
~/bin/mycli pwd      # prints current directory
~/bin/mycli          # falls through to help
```

What's happening:
- `cmd="${1:-help}"` reads `$1`, falls back to `"help"` if empty.
- `case "${cmd}" in ... esac` is bash's switch statement.
- Each `pattern) command ;;` is one branch.
- `help|*)` is the catch-all.

You now have **three real verbs**. The pattern scales to ten or twenty.

✓ **Done when**: each of `mycli date`, `mycli user`, `mycli pwd` produces the
expected output, and `mycli` (no arg) prints help.

---

## 4. Replace the toy verbs with your own

Open your shell history and find what you actually type:

```bash
history | awk '{$1=""; print substr($0,2)}' | sort | uniq -c | sort -rn | head -20
```

Pick three commands you run repeatedly. Examples by stack:

| If you use… | Try wrapping… |
|---|---|
| Docker Compose | `docker compose up -d`, `docker compose down`, `docker compose logs -f <svc>` |
| Python + pytest | `pytest`, `pytest path/to/file.py`, `pytest -x --pdb` |
| Git worktrees | `git worktree add -b feat/<name> ../wt/<name>`, `git worktree list`, `git worktree prune` |
| Node | `pnpm install`, `pnpm dev`, `pnpm test` |
| Cloud / SSH | `ssh dev.mycompany.io`, `aws s3 ls s3://my-bucket`, `kubectl get pods -n staging` |

Pick three. Edit `~/bin/mycli`'s `case` block — replace the toy verbs:

```bash
cat > ~/bin/mycli <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

cmd="${1:-help}"; shift || true   # shift removes $1 so $@ holds the rest

case "${cmd}" in
  up)       docker compose up -d ;;
  down)     docker compose down ;;
  logs)     docker compose logs -f "$@" ;;             # mycli logs api → forwards "api"
  test)     pytest "$@" ;;                             # mycli test path/file.py
  wtt)
    name="${1:?usage: mycli wtt <name>}"               # require an arg
    git worktree add -b "feat/${name}" "../wt/${name}"
    ;;
  help|*)
    cat <<HELP
mycli — your team workflow CLI

  up           docker compose up
  down         docker compose down
  logs <svc>   tail one service
  test [path]  run pytest
  wtt <name>   create worktree + branch
HELP
    ;;
esac
EOF
chmod +x ~/bin/mycli
```

The `"$@"` after the verb forwards any extra args you typed — so
`mycli logs api` runs `docker compose logs -f api`.

✓ **Done when**: three of your own verbs run correctly.

---

## 5. Make it callable from anywhere

So far you've been typing `~/bin/mycli`. Add `~/bin` to `PATH` so just `mycli`
works:

```bash
# zsh (macOS default)
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# verify
which mycli       # → /Users/you/bin/mycli
mycli help        # works from any directory
```

✓ **Done when**: `mycli help` runs from any directory.

---

## 6. Make Claude Code aware of it

The point of a team CLI is that *humans and agents both inherit it*. Tell
Claude Code your CLI exists. Add to `~/.claude/CLAUDE.md`:

```markdown
## Local commands

- `mycli up` — bring my dev stack up
- `mycli down` — tear it down
- `mycli logs <svc>` — tail one service's logs
- `mycli test [path]` — run pytest, optionally on a path
- `mycli wtt <name>` — create a worktree on a new feature branch
```

Open a fresh Claude Code session, say *"bring up my dev stack"* — Claude
should now reach for `mycli up` instead of inventing `docker compose ...`.

✓ **Done when**: in a new Claude Code session, asking *"bring up my dev
stack"* invokes `mycli up`. (If it doesn't, your CLAUDE.md description was
too vague — name the verbs explicitly.)

---

## 7. Add a verb the moment you need it

Pay attention to what you type during the rest of the workshop. The first
time you run a multi-word command twice, **stop and add it**:

1. Open `~/bin/mycli`.
2. Add a new branch to the `case` block.
3. Add a line to your `CLAUDE.md` so the agent picks it up too.
4. Save. No restart needed.

Adding verbs has to be near-zero friction or the CLI dies. This is the
muscle to build.

✓ **Done when**: you've added a verb that wasn't in the original list,
during the workshop.

---

## 8. Stretch — graduate to Python (optional)

When bash starts hurting (nested args, validation, testability) graduate
to Python with [`typer`](https://typer.tiangolo.com/) and uv's single-file
script mode:

```python
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["typer>=0.12"]
# ///
import subprocess
import typer

app = typer.Typer(no_args_is_help=True)

@app.command()
def up():
    """Bring the dev stack up."""
    subprocess.run(["docker", "compose", "up", "-d"], check=True)

@app.command()
def wtt(name: str):
    """Create a worktree on a new feature branch."""
    subprocess.run(
        ["git", "worktree", "add", "-b", f"feat/{name}", f"../wt/{name}"],
        check=True,
    )

if __name__ == "__main__":
    app()
```

`uv run --script` ([PEP 723](https://peps.python.org/pep-0723/)) means deps
are inlined in a comment block — no `pyproject.toml` needed. Save as
`~/bin/mycli` (still chmod +x, still in PATH). You get free `--help`,
type-checked args, real error messages.

✓ **Done when**: at least one verb is in Python and `mycli --help` shows it.

---

## What you take home

A CLI you actually use. The compounding starts at verb #5 — every new verb
saves keystrokes for you and tokens for every Claude Code session that
reads your `CLAUDE.md`.

Grow it when three teammates have each written the same shell snippet.
Don't grow it before then.
