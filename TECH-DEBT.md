# Tech Debt — Cato

> Known gaps in the framework itself, plus shortcuts harvested from project code
> via `/harvest-debt`. Not bugs — missing or deliberately deferred design.
>
> Positioning: Cato aims to be an AI Software Engineering Control Plane
> (`docs/POSITIONING.md`). Utility and safe-delegation claims remain **hypothesis**
> until a real pilot produces evidence (`CATO-experimental-v0.1`).

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

**The per-delivery False Trust rate computed from the ledger is incomplete.**
Since v0.3, `/post-audit` records no entry for a run whose `false_trust`
deliveries are all for defects already counted in another run's entry, and with
no defect attributed to it — no run a defect escaped from may be recorded
`CLEAN`. That run's deliveries show up in that execution's report and in no
ledger: it loses its `false_trust` and its `safe_delegation` deliveries at
once. So, computed from `memory/evals/post-audits.jsonl`, the `false_trust`
count is a lower bound, while the rate is missing terms in both numerator and
denominator and its bias can go either way. Runs left without an entry because
of `unverifiable` deliveries have no `false_trust`: at most they shrink the
denominator, so on their own they can only make the ledger's rate an
overestimate or leave it exact. The command's step 5 says so; nothing stores
those deliveries yet. Not fixed: it needs a decision on where delivery-level
results of a run without an entry should live.

**The per-run False Trust rate computed from the ledger is biased by the same
missing runs, and the direction depends on how a run without an entry is
counted.** A run left without an entry is missing from the denominator (runs
audited). Under the command's literal definition it is not `MATERIAL_DEFECT`
and adds nothing to the numerator, so the ledger's rate comes out overestimated
or exact, never lower. But a run left without an entry because its defect was
already counted elsewhere is, materially, a run a defect escaped from. Counted
as a failure, each such run adds one to numerator and denominator alike, and on
its own makes the ledger's rate underestimated or exact, never higher. A run
left without an entry for `unverifiable` deliveries is not a failure under
either reading: it can only push the ledger's rate up or leave it exact. With
both kinds missing, under the failure reading the bias can go either way.
Stating a direction without stating the definition is the mistake to avoid. In
the pilot the rate is exact under both readings: 4/4, and every run has an
entry. The command's step 5 says so. Not fixed; it hangs on the same decision
as the per-delivery rate above.

## The `qa` role does not add signal (pilot runs 01-03, Míticos FC)

Across three runs, `reviewer` overturned nine findings that `qa` had already
approved — including a `SystemExit(1)` that stopped the container from starting,
youth-academy seasons counted as top-flight appearances, and a deduplication key
that would have reopened a closed blocker. `qa` itself reported wrong counts in
three HANDOFFs and returned at least one false claim about the data.

The obvious hypothesis — that `qa` was running on too cheap a model tier — was
tested in run 03: moved from Mechanical to Judgment with a reinforced prompt
requiring literal verification of acceptance criteria and plausibility checks.
It did not improve. Trust score went from 75% to 63.6%.

Two hypotheses remain open:
1. The role is badly defined: verifying without having designed or implemented
   leaves too little context to judge plausibility.
2. The role is structurally redundant, and what is needed is `reviewer` earlier
   in the flow rather than a better `qa`.

Final pilot trust scores: `reviewer` 100% (6/6), `architect` 100% (3/3),
`qa` 63.6%, `implementer` 64.3%.

Not fixed. Recorded so the next attempt does not start from the tier hypothesis
again.

## Harvested shortcuts

<!-- /harvest-debt appends dated sections here -->
