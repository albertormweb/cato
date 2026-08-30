# Changelog

All notable changes to Cato — the framework itself, not projects built with it.

## v0.2 — Pilot calibration (2026-08-30)

First revision backed by evidence rather than reasoning. Source: a three-run
pilot on a real product (Míticos FC), runs 01-03. Each change names the run
that motivated it and, where applicable, the run that validated it.

### Added

- **Asking the human at `PENDING_APPROVAL`** (`.claude/process.md`). Agents now
  present the artifact's options directly in-session via the input tool instead
  of parking the run until the human returns with a new prompt. The artifact
  stays the record; no-self-approval is untouched. Motivated by run 02 (six
  gates, six session exits). Validated in run 03: nine decisions taken
  in-session, zero exits.
- **`/close-run`** (`.claude/commands/close-run.md`). Dumps objective run
  metrics to `memory/evals/`, scaffolds the human observation notes, updates the
  run index. Never writes the judgment sections. Ported from the pilot repo. On
  first execution it detected there was no run to close, found the objective
  records for runs 01-02 missing, and backfilled them unprompted, respecting the
  judgment-section constraint.

### Changed

- **Agent budgets** (`.claude/config.md`): medium 5 → 6, large 8 → 14. At 8,
  the budget ran out before `reviewer`'s second pass — the pass that caught a
  production-breaking blocker after `implementer` and `qa` had both returned
  PASS. Motivated by run 02 (closed at 13/14 and still needed an extension).
  Applied in run 03.
- **Progressive validation note** (`.claude/config.md`): iteration 2 requires
  coverage, so the tool must be installed and `tests/README.md` must not forbid
  it. Run 02: `qa` ended `BLOCKED` on that contradiction.
- **Trust-score note** (`.claude/config.md`): the 70% floor confirmed working
  in run 02 — orchestrator flagged two agents under the floor without touching
  `.claude/`.

### Tried and not adopted

- **Raising `qa` from Mechanical to Judgment tier** with a reinforced prompt.
  Tested in run 03: no improvement, trust score fell from 75% to 63.6%. Tier
  stays Mechanical. The open hypotheses (role badly defined vs. structurally
  redundant) are recorded in `TECH-DEBT.md`.

## v0.1 — Experimental

Initial framework: orchestrator, personas, hard rules, config, minimalism
ladder, trust score, evals v0.1. Reasoned, not measured. See `docs/VALIDATION.md`.
