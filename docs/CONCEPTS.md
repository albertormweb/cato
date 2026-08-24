# Concepts

Cato uses some vocabulary that's obvious if you've worked in software teams and
opaque if you haven't. This explains the terms and why each thing exists. You
don't need it to start — see `FIRST-PROJECT.md` — but it helps when behaviour
surprises you.

## The basic idea

Left alone, an AI agent on a project tends to forget last week's decisions, build
things nobody asked for, and claim "done" without checking. That's missing
structure, not a model failure.

Cato adds structure: specialised roles, a written record, and someone whose job is
to check someone else's work. Intended internal use: **master prompt → approve
once → build**.

## Agent

A role with instructions and a limited tool set. In Claude Code, subagents run in
**isolated context** (clean slate). The test runner does not inherit the strategy
debate — only what it must run. That keeps cost down.

Eight agents; each has an explicit *doesn't*. Tool lists must match write jobs:
file owners get Write/Edit; `reviewer` gets Bash for `git diff`.

## Orchestrator

Coordinates; does not implement by default. When you talk to Cato, you talk to the
orchestrator.

## Handoff

Fixed return block:

```
status: PASS | FAIL | BLOCKED
summary: two or three lines
artifacts: which files were touched
next_action: what should happen now
```

Only this crosses between agents. Empty `artifacts` after a write job is
suspicious.

## BLOCKED

"I need something I don't have." Not a failure. Ambiguous specs should BLOCK
rather than guess.

## ADR

One file per decision in `memory/adr/` — why, and what was ruled out — so agents
don't relitigate settled choices.

## Spec

What a feature should do, plus **out of scope** and why. The out-of-scope half
stops platform sprawl.

## MVP / V2 / FUTURE

`strategist` taxonomy. MVP = needed to test the main hypothesis. Burden of proof
is on the feature.

## Minimalism ladder

Seven rungs before writing code (`.claude/minimalism-ladder.md`). Validation and
error handling are never the thing you cut.

## SHORTCUT marker

Inline deferral comment; `/harvest-debt` collects into `TECH-DEBT.md`.

## PENDING_APPROVAL

Label in `PLANNING.md`. Dependent work stops. Only the human moves it to
`APPROVED`. This is durable state, not chat vibes — but it is still a convention
agents must honour, not a filesystem lock.

## Autonomy / hard stops

Trivial and medium work continues between agents without asking. Large work gets
one plan pause. Always stop for hard rules (secrets, merge to `master`,
`.claude/`, new deps), `PENDING_APPROVAL`, `BLOCKED`, budget exceeded, or
repeated loop failure.
See `.claude/process.md`.

## Loop mode

Repeated `implementer → qa` with a rising bar. Caps and identical-failure early
exit live in `config.md`.

## Dry-run

`--dry-run`: plan only, no writes, no subagent invocations.

## Master-prompt build

One descriptive `/init-project` prompt → genesis at `PENDING_APPROVAL` → human
approves → `Build PLANNING.md Now; work in a loop`. That is the default product
path for this template.

## Decision ledger

`memory/decisions.md` lists undeliberated choices from a session — places the
spec was silent and someone picked anyway — ranked least-confident first. It
reports; it does not block or auto-fix. Deliberate decisions belong in
`memory/adr/`, not here.

## Evals / feedback (v0.1)

`memory/evals/` stores per-task evidence, human intervention logs, post-audits,
and improvement proposals. Tooling prints trust reports and metrics (Delegation,
Safe Delegation, False Trust). **CATO PASS** = internal controls only — not
objective correctness. Human supervision minutes are human-owned; post-audit
time is experimental verification and must not inflate them. Proposals need
human approval and never auto-edit Cato. See `docs/EVALS.md`.

## Trust score

Table in `memory/trust-score.md`, generated from `agent-log.md` by
`tooling/trust_score.py`. Needs honest `avoidable` / `reversed` labels.

## Calibration

`/calibrate` compares `config.md` guesses to a real log and proposes edits at
`PENDING_APPROVAL`.

## Enforcement honesty

**Mechanical today:** CI structure tests, ruleset sync, trust-score math, Claude
Code tool allowlists. **Instruction-level today:** budgets, honouring
`PENDING_APPROVAL`, qa actually running tests. See `docs/VALIDATION.md`.

## Where things live

| You want | Look at |
|---|---|
| What's happening now | `PLANNING.md` |
| How it's built | `DESIGN.md` |
| Why it's built that way | `memory/adr/` |
| Undeliberated session choices | `memory/decisions.md` |
| Task eval evidence / proposals | `memory/evals/` (`docs/EVALS.md`) |
| What a feature should do | `specs/` |
| Latest template validation | `docs/VALIDATION.md` |
| What each agent may do | `.claude/agents/` |
| Which numbers to adjust | `.claude/config.md` |
| What can never happen without you | `.claude/rules-hard.md` |
| What went wrong and when | `memory/agent-log.md` |
| What's known to be missing | `TECH-DEBT.md` |
