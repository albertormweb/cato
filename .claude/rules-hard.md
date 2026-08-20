# Hard rules

Constraints, not parameters. Nothing in this file is tuneable — no thresholds, no
budgets, no numbers to adjust after a calibration run. Those live in `config.md`.

The separation matters: `/calibrate` and the human edit `config.md` routinely.
This file changes only by deliberate decision, never as a side effect of tuning.

## Never without explicit human approval

- Merging to `main`/`master`
- Deleting files outside scratch/tmp directories
- Modifying anything inside `.claude/`
- Installing new dependencies without justifying it in the HANDOFF
- Touching credentials, `.env`, secrets, or any sensitive configuration

## Always required

- No `implementer` closes a task without `qa: PASS`
- No architectural change without going through `architect`
- Every non-trivial design decision gets recorded as an ADR in `memory/adr/`
- If an agent finds the spec ambiguous, it answers `BLOCKED` — it never assumes
- When an agent stops because information is missing, it says so plainly and the
  task parks. Stopping is correct; inventing the missing information is not.

## No self-approval

No agent validates its own output. `implementer` doesn't decide its code passes,
`qa` decides. `qa` doesn't decide the change is mergeable, `reviewer` does. And
no agent — not `strategist`, not `architect`, not the orchestrator — moves an
artifact from `PENDING_APPROVAL` to `APPROVED`. Only the human does that.

This is the constraint the rest of the system rests on. If it erodes, everything
else is theatre.

## Approval gates are mechanical

A verbal "sounds good" in chat isn't the record. State lives in `PLANNING.md`:

- Artifacts needing human approval (DESIGN.md after a structural change,
  `designer` mockups, DEPLOYMENT.md) are marked `STATUS: PENDING_APPROVAL`.
- The orchestrator cannot delegate to `implementer` over an artifact sitting at
  `PENDING_APPROVAL`. It asks and waits.
- Only the human moves `PENDING_APPROVAL` → `APPROVED`.

## Tie-breaking between agents

When two agents contradict each other, authority runs:

1. **Human** — always wins.
2. **`reviewer`** — its rejection blocks even if `qa` gave `PASS`. Tests validate
   behaviour, not judgment.
3. **`strategist`** — if it calls something over-engineering, `architect` doesn't
   design it, however good the idea is technically.
4. **`architect`** — over `implementer` on any design question.
5. **`qa`** — its `FAIL` always blocks `implementer`.

If the hierarchy doesn't settle it (say `reviewer` and `strategist` disagree),
it's `BLOCKED` for the human. The orchestrator doesn't arbitrate.

## Verification is not optional

- `qa` never marks `PASS` without actually running the tests. If it can't run
  them, that's `BLOCKED`, never `PASS` by default.
- A HANDOFF claiming `PASS` with no verifiable `artifacts` is treated as
  suspicious and sent back for re-verification.

## `/init-project` scope

May only create or edit `DESIGN.md`, `PLANNING.md`, `specs/` and the genesis ADR.
It doesn't touch `.claude/` and doesn't write application code.
