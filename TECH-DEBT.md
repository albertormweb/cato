# Tech Debt — Cato

> Known gaps in the framework itself, plus shortcuts harvested from project code
> via `/harvest-debt`. Not bugs — missing or deliberately deferred design.

Latest integrity re-validation: `docs/VALIDATION.md` (2026-08-20; honesty
follow-up 2026-08-21). Template tests green; product E2E still open.

## Framework debt

**Never used on a real product end to end.** Rules are reasoned, not observed.
Budgets, retries, loop caps and the trust-score floor in `.claude/config.md` are
starting guesses. `/calibrate` exists to check them against a real session log.
Master-prompt path to close this: `/init-project` → approve genesis →
`Build PLANNING.md Now; work in a loop`. Until that runs, treat utility claims as
hypothesis.

**Agent write tools aligned (template blocker closed).** `architect` /
`strategist` (and editors) have Write/Edit; `reviewer` has Bash for diffs; CI
asserts writers include Write. This does **not** replace a product E2E run.

**No benchmark results.** `benchmarks/` has method and fairness traps only. A
loss against plain Claude Code belongs in `benchmarks/results/` too.

**Budgets and approval gates are instruction-level.** Invocation caps and
`PENDING_APPROVAL` are orchestrator discipline, not a scripted lock. Optional
follow-up: log-based budget checker. The contradictory heading “Approval gates
are mechanical” in `rules-hard.md` was reworded (2026-08-21) so hard rules match
the README; the gates themselves remain instruction-level — that debt is open.

**Trust-score annotation depends on discipline.** Script derives the table, but
only if `avoidable` / `reversed` appear in the log. Structured fields would harden
this.

**`trust_score.py` hardcodes sample size and discusses the floor in prose.**
Should eventually read `.claude/config.md` (or a tiny shared constant) so
calibration cannot drift from the scorer.

**Content production has no dedicated agent.** Non-software output may use
`domain/` notes; a `content-producer` role is unresolved on purpose.

**Language-agnostic products, Python-only tooling.** Integrity checks need Python;
the markdown framework works without it.

**Portability is partial.** Non-Claude-Code hosts get `AGENTS.md` rules only — no
isolated subagents or slash commands.

**Evals / feedback v0.1 is evidence-only.** `memory/evals/` + `tooling/evals.py`
record runs, human interventions, post-audits, and proposals; approving a
proposal does not apply it to `.claude/`. CATO PASS ≠ objective correctness;
Catch-rate / escaped defects stay honest about unknowns — see `docs/EVALS.md`.

## Harvested shortcuts

<!-- /harvest-debt appends dated sections here -->
