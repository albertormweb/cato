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

## Asking the human at PENDING_APPROVAL

When an agent reaches a `PENDING_APPROVAL` gate, it writes the artifact as
usual **and** asks the human directly in the session, using the available input
tool, presenting the options the artifact itself has already worked out. The
artifact remains the record; the question is only the interface.

This does not weaken the no-self-approval rule: the agent presents options and
their measured trade-offs, never picks one, and never proceeds on silence or on
an ambiguous answer. If the answer doesn't map cleanly onto one of the options,
it asks again instead of interpreting.

The agent that asks must not be the one that wrote the artifact.

Provenance: added after pilot run 02 (six approval gates in one run, each
costing a session exit and a return with a new prompt). Validated in run 03:
nine decisions taken in-session, zero exits.

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
   session (session log, decision ledger, trust score script — see below).

Do not invent scope beyond the approved MVP cut. Park new ideas as V2/FUTURE
via `strategist` instead of silently expanding the build.

## Decision ledger

`memory/decisions.md` records choices made during a session where the spec did
not decide — ranked least-confident first so the human starts with the shaky
ones. Read from the top; stop when the rest looks fine.

It reports only. It does not block closing a session and does not start fixes.
ADRs in `memory/adr/` are out of scope here (those were deliberate). The
orchestrator writes the ledger at session close; see `claude-orchestrator.md`.

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

## Evals and feedback (v0.1)

Task-level evidence lives in `memory/evals/` (JSONL), managed by
`tooling/evals.py`. It answers: can we delegate with less supervision, and should
we propose a process change?

- **Human interventions** during the task (human-owned; never invented).
- **Record** after a task completes (known fields only; `escaped_defects` stays
  null until later evidence).
- **Trust report** / **feedback** — CATO PASS = internal controls only.
- **Post-audit** later (experimental verification; does not add to
  `human_minutes`) → Safe Delegation / False Trust.
- **Improvement proposals** start as `PROPOSED` and need human
  `APPROVED` / `REJECTED`. Status updates never rewrite `.claude/` or prompts.
  During the frozen experiment, do not apply approved proposals.

Details: `docs/EVALS.md`. Separate from `memory/trust-score.md` and `benchmarks/`.
