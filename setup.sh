#!/usr/bin/env bash
# Initialises the template: fills in placeholders and optionally bootstraps the
# project architecture from a descriptive prompt, via Claude Code headless mode.
set -euo pipefail

read -rp "Project name: " PROJECT_NAME
read -rp "Default stack (e.g. FastAPI + PostgreSQL + Docker): " STACK
read -rp "Project description (prompt for /init-project, optional, Enter to skip): " PROMPT

INTERVIEW_FLAG=""
if [ -n "${PROMPT}" ]; then
  read -rp "Run a short interview about the prompt's gaps first? (y/N): " WANT_INTERVIEW
  case "${WANT_INTERVIEW}" in
    [yY]*) INTERVIEW_FLAG=" --interview" ;;
  esac
fi

sed -i.bak "s/<PROJECT_NAME>/${PROJECT_NAME}/g; s/<STACK>/${STACK}/g" CLAUDE.md
rm -f CLAUDE.md.bak

echo "CLAUDE.md updated with project name and stack."

if [ -n "${PROMPT}" ]; then
  if ! command -v claude &> /dev/null; then
    echo "Warning: 'claude' not found on PATH."
    echo "Install Claude Code and run manually:"
    echo "  claude -p \"/init-project \\\"${PROMPT}\\\"${INTERVIEW_FLAG}\""
    exit 0
  fi
  if [ -n "${INTERVIEW_FLAG}" ]; then
    echo "Starting in interview mode (interactive session)..."
    claude "/init-project \"${PROMPT}\"${INTERVIEW_FLAG}"
  else
    echo "Bootstrapping architecture from the descriptive prompt (headless)..."
    claude -p "/init-project \"${PROMPT}\"" --allowedTools "Read,Write,Grep,Glob"
  fi
  echo "Done. Review DESIGN.md, PLANNING.md and specs/ before implementing."
else
  echo "No description given: fill in DESIGN.md and PLANNING.md by hand, or run"
  echo "later inside 'claude': /init-project \"<project description>\""
fi

cat <<'NEXT'

Two files need filling in before agents produce anything real:
  .claude/claude-brand-style.md   tone, naming, visual direction
  tests/README.md                 the commands that run your tests

New to this? Read docs/FIRST-PROJECT.md.
NEXT
