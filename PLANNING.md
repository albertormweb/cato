# Planning

> Living document for **this framework repo**. Product clones rewrite it via
> `/init-project`. History belongs in `memory/session-log.md`.

## Now

- Keep template docs and integrity tests aligned with master-prompt build.
- Next human action for proving the system: run a real product through
  `/init-project` → approve genesis → build loop (see `docs/VALIDATION.md`).

## Next

- First end-to-end product run; file results under `benchmarks/results/` or
  session notes + `/calibrate`.
- Structured trust-score annotations (`reversed` / `avoidable` as fields).
- Optionally parse `config.md` from `trust_score.py` instead of hardcoded floors.

## Blocked

- Measuring whether Cato beats plain Claude Code — blocked on a real dual-arm
  run (`benchmarks/README.md`).

## Pending approval

Artifacts waiting on a human decision. While something sits here, work depending
on it is blocked and the orchestrator cannot delegate around it.

Only the human moves an entry from `PENDING_APPROVAL` to `APPROVED`. No agent
does, including the orchestrator.

| Artifact | Status | Waiting since | What it blocks |
|---|---|---|---|
| First product E2E of this template | PENDING_APPROVAL (human schedules run) | 2026-08-20 | Closing “unvalidated” in `TECH-DEBT.md` |
