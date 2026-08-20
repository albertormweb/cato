# Process

How work moves through the system. Constraints live in `rules-hard.md`, tuneable
numbers in `config.md`. This file covers the modes of operation that reference both.

## Autonomy by task size

Designed for an internal loop: pass a master prompt, then let agents build with
as few human interruptions as safety allows.

| Size | Human pauses | Behaviour |
|---|---|---|
| **Trivial** | None between agents | `implementer` → `qa` only. No `strategist`. Not for new feature proposals. |
| **Medium** | None between agents | Run the needed specialists end to end. Do not ask permission each handoff. |
| **Large** | One summary pause **before** execution | Show the plan (agents, files, budget, approval needs); wait for go-ahead; then run without further pauses until a hard stop. |

Sizing definitions and invocation budgets are in `config.md`.

**New business prompts and new feature proposals are never trivial.** They start
at medium (or large). That keeps `strategist` inside the budget: trivial's
two-invocation cap is for small implementation tasks only.

### Hard stops (always — any size)

Pause and ask the human when any of these fire. Autonomy never overrides them:

- Anything listed under "Never without explicit human approval" in `rules-hard.md`
- An artifact at `PENDING_APPROVAL` that the next step depends on
- `status: BLOCKED` from any agent
- Agent budget exceeded (see `config.md`)
- Two consecutive identical loop-mode failures, or the loop iteration cap

Verbal "sounds good" in chat is not approval. State lives in `PLANNING.md`.

## Master-prompt build

Intended path for greenfield (and the default mental model for this framework):

1. Human pastes one master prompt into `/init-project "..."` (optional
   `--interview`, optional `--dry-run`).
2. `strategist` cuts MVP/V2/FUTURE; `architect` writes `DESIGN.md`,
   `PLANNING.md`, genesis ADR; specs are created. Genesis `DESIGN.md` (and any
   first mockups later) land at `PENDING_APPROVAL`.
3. Human moves those rows to `APPROVED` in `PLANNING.md` — **one gate**, then
   build autonomy.
4. Human says build (e.g. "Build PLANNING.md Now; work in a loop"). The
   orchestrator drains `Now` / the agreed backlog using medium/trivial rules
   above, looping `implementer → qa` with rising thresholds when asked to loop.
5. Stop only on a hard stop. When `Now` is empty, summarise and close the
   session (session log + trust score script).

Do not invent scope beyond the approved MVP cut. Park new ideas as V2/FUTURE
via `strategist` instead of silently expanding the build.

## Loop mode

When the human asks to work "in a loop" until something closes, the orchestrator
iterates `implementer → qa` without asking permission each round, **but the bar
rises**. The orchestrator tells `qa` which iteration it's on; `qa` applies the
matching threshold from `config.md`.

- At the iteration cap without a `PASS` under the strictest threshold: stop and
  escalate. More iterations don't fix a design problem, they hide it.
- On repeated identical failures: stop earlier. The problem is upstream.
- The per-task agent budget still applies. Loop mode doesn't suspend it, it only
  skips asking for human confirmation between rounds.
- On exit, record the outcome in `memory/agent-log.md` including iteration count.

## Dry-run

Any command or task can be requested with `--dry-run`: the orchestrator produces
the plan (agents, files, estimated budget, what would need approval) and **writes
and invokes nothing**. Useful before large tasks to see the cost before paying it.

## Observability

- Every HANDOFF is appended, without editing prior entries, to
  `memory/agent-log.md` with date and agent. It's an audit log, not a summary — it
  lets you reconstruct what each agent did and when without rereading the whole
  conversation.
- Annotate as you file: write `avoidable` in the summary of a `BLOCKED` whose
  answer was already in `specs/` or `DESIGN.md`, and `reversed` on an entry whose
  `PASS` a later agent overturned. The trust score is only as good as these labels.

## Trust score

`memory/trust-score.md` is **generated**, not hand-written. Run
`python tooling/trust_score.py --write` at session close; it derives the table from
`memory/agent-log.md`. Don't edit the file directly — asking an agent to keep honest books
on its own team is a weak control, so the numbers come from the record instead.

Thresholds are in `config.md`. A sustained low score isn't a reason to stop using
an agent — it's a signal its prompt needs revision. The fix goes in the agent's
`.md`, not the model.

## Calibration

Cato's numbers are reasoned starting points, not measurements. After a real
working session, `/calibrate` compares them against `memory/agent-log.md` and proposes
adjustments to `.claude/config.md`. Proposals go to `PENDING_APPROVAL` — the orchestrator
never silently retunes its own limits.
