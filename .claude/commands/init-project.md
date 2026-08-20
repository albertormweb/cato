---
description: Generates PLANNING.md, DESIGN.md, specs/ and the genesis ADR from a master prompt. Accepts --interview (short interview first) and --dry-run (preview without writing).
---

You receive a **master prompt** — one project description that should be enough to
bootstrap and later build: $ARGUMENTS

Accepted flags:

- `--interview`: short interview about the prompt's gaps before generating.
- `--dry-run`: preview the whole plan without writing a single file.

This command only bootstraps. Application code comes after the human approves
genesis artifacts and asks to build (see `.claude/process.md` → Master-prompt build).

## Step 0 — Dry-run (only with `--dry-run`)

Write nothing. Invoke no subagents. Produce a preview only:

1. Which agents would be invoked, in what order.
2. Which files would be created or modified (concrete paths).
3. What questions `strategist` would ask if `--interview` were also passed.
4. Estimated subagent invocations and which budget tier that falls in
   (trivial/medium/large, see `.claude/config.md`). Kickoff is never trivial.
5. What would end up marked `PENDING_APPROVAL`.

Stop there. Don't generate file contents, just the plan. The human reruns without
the flag if convinced.

## Step 1 — Interview (only with `--interview`)

`strategist` runs a short conversation, not a form:

1. Read the whole prompt and extract everything inferable. **Don't ask anything
   already in the prompt** — it's irritating and shows you didn't read it.
2. Identify the gaps that genuinely shape the design. Common categories (not all
   apply every time):
   - **Real constraints**: budget, deadline, solo or with a team?
   - **Definition of success**: a concrete number, not "it works".
   - **What NOT to build**: often more informative than what to build.
   - **Current state**: greenfield, or something inherited?
   - **Reversibility**: which decisions would be expensive to undo?
3. Ask **one at a time**, at most 5-7 total, ordered by impact on the design.
   Justify each in half a line ("asking because it decides whether the MVP needs X").
4. If the human says "I don't know": **don't push**. `strategist` writes it under
   `PLANNING.md → Blocked` with the reason and moves on. A documented open question
   beats an answer invented under pressure.
5. Close the interview with a summary of what was learned and what's still open,
   before generating anything.

## Step 2 — Generation

Kickoff is sized **large** (or at least medium if the prompt is tiny). Invoke
subagents; they write their own files — do not "summarise design into chat"
instead of writing.

1. Invoke `strategist` (with whatever the interview surfaced, if it ran). Sort
   everything in the prompt into MVP/V2/FUTURE and pass only the MVP scope
   downstream. What's excluded gets documented in `specs/` as out of scope, not
   designed.
2. If the MVP scope involves integrations, a stack to validate, or relevant prior
   art, invoke `researcher`.
3. Invoke `architect` to **write**, over the filtered scope only:
   - `DESIGN.md`: stack, main modules, key architectural decisions.
   - `PLANNING.md`: "Now" with the first milestone, "Next" with the immediate
     backlog, "Blocked" with whatever went unanswered.
   - Mark genesis `DESIGN.md` as `PENDING_APPROVAL` in the Pending approval table.
4. Generate `specs/0001-<project-slug>.md` (objective, MVP scope, out of scope
   with reasons, success criteria). Orchestrator or `architect` may write this;
   it must exist on disk before you finish.
5. `architect` creates `memory/adr/0001-project-genesis.md` with the kickoff
   decision.
6. If there's a user-facing component: fill in (or ask the human to fill in)
   `claude-brand-style.md`, and note in `PLANNING.md` that `designer` mockups are
   the next step, marked `STATUS: PENDING_APPROVAL` once they exist.
7. Leave `DEPLOYMENT.md` with placeholders — not this step's job.
8. Optionally seed `domain/` with a short note on domain language if the master
   prompt implies it; leave `.claude/skills/` alone unless the human asked for a
   reusable skill.

Don't implement application code or design UI here — strategy, architecture and
planning only.

## Step 3 — Hand off to build

Finish with a short summary:

1. What was generated (paths).
2. What is out of scope (V2/FUTURE).
3. What sits at `PENDING_APPROVAL` (must list genesis DESIGN at minimum).
4. Exact next human action, e.g.:

   > Approve the Pending approval rows in `PLANNING.md`, fill
   > `tests/README.md` (and brand-style if UI), then say:
   > `Build PLANNING.md Now; work in a loop until the first milestone ships.`

Do not start `implementer` until those approvals are in place.
