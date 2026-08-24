# Spec: Cato framework (template)

> Describes this repository as the product under development. Generated app
> projects get their own `specs/0001-*.md` from `/init-project`.

## Objective

Provide an internal **AI Software Engineering Control Plane** (Harness Engineering
for coding agents): paste a master prompt, get an MVP cut and design, approve
once, then have specialised agents build with verification and bounded autonomy.
Primary host today: Claude Code; portable rules via `AGENTS.md`. Outcome claims
(safe delegation) are **hypothesis** until measured — see `docs/POSITIONING.md`,
`docs/EVALS.md`.

## MVP scope

- Eight agents with tools matching their jobs
- Orchestrator + HANDOFF protocol
- Hard / config / process split
- `/init-project` (interview, dry-run) and master-prompt build path
- Loop mode with progressive validation
- Memory layers (ADR, session log, agent log, generated trust score)
- Optional `tooling/` integrity scripts and CI
- Portable `AGENTS.md` (+ synced host copies)

## Out of scope (with reasons)

- Hosted SaaS / observability platform for Cato — internal template, not a sellable runtime
- Autonomous self-improvement (feedback proposals never auto-apply)
- Automatic merge to `master` — hard rule requires human
- Full parity on non-Claude-Code hosts — no isolated subagents there
- Benchmark results — method only until a fair run exists
- Demonstrated ROI / safe-delegation proof — experimental pilot required
- Content-industry editorial agent — unresolved; may live under `domain/` notes

## Success criteria

1. Framework integrity tests stay green (`tooling/` + sync).
2. A human can follow `docs/FIRST-PROJECT.md` without contradictory instructions.
3. After one real product E2E, `TECH-DEBT.md` can retire “never used end to end”
   or list concrete failures instead of guesses.
4. Agents that own files can write them (enforced by structure test).
