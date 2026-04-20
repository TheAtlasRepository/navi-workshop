#!/usr/bin/env bash
set -euo pipefail

# Demo: create three git worktrees, each with one task. Open three Claude Code
# sessions (or three terminals) on them and watch them work in parallel.

ROOT="$(git rev-parse --show-toplevel)"
WT_DIR="${ROOT}/../wt"
TASKS=(task-1 task-2 task-3)

cmd="${1:-up}"

up() {
  mkdir -p "${WT_DIR}"
  for t in "${TASKS[@]}"; do
    local branch="demo/${t}"
    local path="${WT_DIR}/${t}"
    if [[ -d "${path}" ]]; then
      echo "skip ${path} (exists)"
      continue
    fi
    git worktree add -b "${branch}" "${path}"
    cp "${ROOT}/worktrees-demo/tasks/${t}.md" "${path}/TASK.md"
    echo "→ ${path} — branch ${branch}"
  done
  echo
  echo "Open each directory in its own Claude Code session:"
  for t in "${TASKS[@]}"; do
    echo "  cd ${WT_DIR}/${t} && claude"
  done
}

clean() {
  for t in "${TASKS[@]}"; do
    local branch="demo/${t}"
    local path="${WT_DIR}/${t}"
    if [[ -d "${path}" ]]; then
      git worktree remove --force "${path}"
    fi
    if git show-ref --verify --quiet "refs/heads/${branch}"; then
      git branch -D "${branch}"
    fi
  done
  rmdir "${WT_DIR}" 2>/dev/null || true
  echo "cleaned."
}

case "${cmd}" in
  up)    up ;;
  clean) clean ;;
  *)     echo "usage: $0 [up|clean]" ; exit 1 ;;
esac
