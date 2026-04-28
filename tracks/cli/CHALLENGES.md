# Challenges

A ladder for the starter-CLI track. Aim to leave the workshop with a `mycli`
(or whatever you name it) that runs at least three real verbs you can use
on Monday.

Read `README.md` first for the *why*. This file is the *how*.

---

## 1. Pick three verbs

Open your shell history and look at what you've actually been running:

```bash
history | awk '{print $2}' | sort | uniq -c | sort -rn | head -20
```

Pick the three you'd like to type as one word. Common starters:

- `up` / `down` / `clean` — bring your dev stack up, down, or reset volumes
- `logs <service>` — tail logs from one container
- `test [path]` — run the test slice for a directory
- `pr` — open a PR with your team's template
- `wtt <name>` — create a git worktree on a new branch
- `sshdev` — ssh into the dev box

If you don't have a dev stack handy, copy these literally — they're useful
on any project with `docker compose` and `git`.

✓ **Done when**: three verbs and one-line descriptions written down.

---

## 2. Write the bash router

Create the file:

```bash
mkdir -p ~/bin
cat > ~/bin/mycli <<'EOF'
#!/usr/bin/env bash
# mycli — replace with your own verbs.
set -euo pipefail

cmd="${1:-help}"; shift || true

case "${cmd}" in
  up)     docker compose up -d ;;
  down)   docker compose down ;;
  logs)   docker compose logs -f "$@" ;;
  wtt)
    name="${1:?usage: mycli wtt <name>}"
    git worktree add -b "feat/${name}" "../wt/${name}"
    echo "cd ../wt/${name}"
    ;;
  test)   pytest "$@" ;;
  help|*)
    cat <<HELP
mycli — your team workflow CLI

  up          docker compose up
  down        docker compose down
  logs <svc>  tail one service
  wtt <name>  create worktree + branch
  test [path] run pytest

HELP
    ;;
esac
EOF
chmod +x ~/bin/mycli
```

Replace the verbs in the `case` block with your own from Challenge 1.

✓ **Done when**: `~/bin/mycli` exists and is executable.

---

## 3. Make it callable from anywhere

Add `~/bin` to your `PATH` if it isn't already. For zsh:

```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

For bash, the same line in `~/.bashrc`. Verify:

```bash
which mycli       # → /Users/you/bin/mycli
mycli help        # prints your help text
mycli up          # runs your "up" verb
```

✓ **Done when**: `mycli help` works from any directory.

---

## 4. Make Claude Code aware of it

The whole point of a team CLI is that *humans and agents both inherit it*.
Tell Claude Code your CLI exists by adding a line to `~/.claude/CLAUDE.md`
(or your project's `CLAUDE.md`):

```markdown
## Local commands

- `mycli up` — bring my dev stack up (docker compose up -d)
- `mycli down` — tear it down
- `mycli logs <svc>` — tail one service
- `mycli wtt <name>` — create a worktree at `../wt/<name>` on a new branch
- `mycli test [path]` — run pytest
```

Now in any Claude Code session, *"bring the stack up"* will reach for
`mycli up` instead of inventing a four-line `docker compose ...` snippet.

✓ **Done when**: in a fresh Claude Code session, asking *"bring my dev
stack up"* invokes `mycli up`. (If it doesn't, your `CLAUDE.md` reference
is too vague — name the verbs explicitly.)

---

## 5. Add a tab-completion stub (optional)

Even four-line completions feel professional. For zsh, add to `~/.zshrc`:

```bash
_mycli() {
    local verbs=(up down logs wtt test help)
    compadd -- "${verbs[@]}"
}
compdef _mycli mycli
```

Reload (`source ~/.zshrc`) and `mycli <TAB>` now lists your verbs.

✓ **Done when**: `mycli <TAB>` autocompletes your verbs.

---

## 6. Stretch — graduate to Python (optional)

Once you have ~10 verbs and bash starts hurting (nested args, errors,
testability), graduate to Python with [`typer`](https://typer.tiangolo.com/)
or [`click`](https://click.palletsprojects.com/). Skeleton:

```python
# ~/bin/mycli (still chmod +x; shebang on first line)
#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["typer>=0.12"]
# ///
import subprocess, typer
app = typer.Typer(no_args_is_help=True)

@app.command()
def up():
    """Bring the dev stack up."""
    subprocess.run(["docker", "compose", "up", "-d"], check=True)

@app.command()
def wtt(name: str):
    """Create a worktree + branch."""
    subprocess.run(["git", "worktree", "add", "-b", f"feat/{name}", f"../wt/{name}"], check=True)

if __name__ == "__main__":
    app()
```

`uv run --script` is uv's [PEP 723](https://peps.python.org/pep-0723/)
single-file script mode — no `pyproject.toml`, deps inlined in a comment.
You get rich `--help`, type-checked args, and proper exit codes for free.

✓ **Done when**: at least one verb is in Python with `--help` text.

---

## What you take home

A starter CLI you actually use. Grow it when three different teammates
write the same shell snippet. Tell your agents about every new verb in
`CLAUDE.md`. The compounding starts at verb #5.
