---
description: After a real working session, review whether Cato's own numbers (budgets, retry limits, thresholds) matched reality, and propose adjustments.
---

Cato's limits are starting guesses, not measurements: 2/5/8 agent invocations by
task size, 2 retries before escalating, 5 loop iterations, 70% trust-score floor.
This command checks them against what actually happened.

Run it after a real working session, not after a trivial one.

1. Read `memory/agent-log.md` and `memory/session-log.md` for this project.
2. Run `python tooling/trust_score.py` and read the current table.
3. For each number below, report what the log actually shows:

   | Setting | Current | What the log shows |
   |---|---|---|
   | Trivial task budget | 2 invocations | <observed range> |
   | Medium task budget | 5 invocations | <observed range> |
   | Large task budget | 8 invocations | <observed range> |
   | Retry limit before escalating | 2 | <how many were actually needed> |
   | Loop iteration cap | 5 | <how many rounds tasks actually took> |
   | Trust score floor | 70% | <observed scores> |

4. Flag any setting where reality and the guess diverge meaningfully:
   - **Budget hit repeatedly** → the tier is too tight, or tasks are being
     misclassified by size.
   - **Budget never approached** → the tier is loose; tightening it would save
     tokens with no cost.
   - **Retries never used** → either the limit is irrelevant or agents aren't
     escalating when they should. Check whether any `BLOCKED` should have been one.
   - **Loop always hitting the cap** → the specs are underspecified; the fix is
     upstream, not more iterations.

5. Propose concrete edits to `.claude/config.md`, with the observed evidence for
   each. Don't apply them — mark the proposal `PENDING_APPROVAL` in `PLANNING.md`
   and let the human decide.

6. Note anything the framework got wrong that isn't a number: a role that never
   got used, a guardrail that fired constantly for no benefit, a file nobody read.
   Add these to `TECH-DEBT.md` under framework debt.

Be blunt. A framework that reports itself as well-calibrated after one session is
not being useful. If the honest answer is "not enough data yet", say that instead
of manufacturing a conclusion.
