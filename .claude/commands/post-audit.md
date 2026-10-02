---
description: Audits a closed run's PASS deliveries after the fact against today's code and data, classifies them (safe_delegation / false_trust / unverifiable) and records the result in memory/evals/. Never fixes what it finds.
---

Independently audit a run that is already closed and leave the result in the
evals ledgers.

With an argument (`/post-audit run-04`) audit that run. Without one, audit every
run in `memory/evals/runs.jsonl` that has no entry in
`memory/evals/post-audits.jsonl`. A run already audited is never audited again
or rewritten: the ledger is append-only.

## Precondition: clean session

If the current session produced any of the HANDOFFs it is about to audit — as
orchestrator, or by launching the subagents that signed them — the post-audit
**does not run**. Report that a clean session is needed and stop, without
verifying or recording anything.

Same logic as no-self-approval: the problem isn't that the auditor doesn't
know, it's that it cannot verify what it remembers having done well.

Check this before anything else, comparing the dates of the run's HANDOFFs in
`memory/agent-log.md` against what was done in this session. If it can't be
ruled out (for example, a summarised session that no longer knows what it
produced), stop anyway.

## 1. List the deliveries to audit

Read `memory/agent-log.md` and `memory/evals/runs.jsonl` and list, for the run,
every HANDOFF with `status: PASS`, including the orchestrator's. Split them
into two groups:

- **Reversed**: the PASS was overturned inside the run by a later `reviewer`
  FAIL on that same delivery (annotated `reversed`, or evident in the log). The
  internal control worked; list them and leave them out of the count.
- **Not reversed**: everything else. These are the ones audited.

## 2. Verify each delivery TODAY

For each non-reversed delivery, extract the checkable claims from the HANDOFF
(figures, "X is out", "Y is still in", "the suite passes", "the file did not
change") and check them one by one against the current code and data, by
running the check: the suite, the query, a read of the code as it stands.

**The HANDOFF is the claim under audit, not the evidence.** Never reread a
HANDOFF, an ADR or a session note and accept it. Another agent's PASS on the
same delivery isn't evidence either.

Beyond what the delivery claims, check what the task was supposed to achieve:
the acceptance criteria of the spec or the ADR, literally, against today's
state. A delivery can be truthful in every figure and still leave the
criterion unmet.

Where the domain allows it, verify against external sources and cite them (URL
or identifier, and date consulted). If verification is by sampling, declare the
coverage: what was looked at, how much, and what was left unlooked.

## 3. Classify

| Class | When |
|---|---|
| `safe_delegation` | Everything checkable was checked today and holds. |
| `false_trust` | What the delivery passed as good contains a material defect that no control in the run detected. |
| `unverifiable` | It can't be checked with the information available: state already overwritten, a source that has changed, a claim with no trace. |

Every classification carries its concrete evidence: the command or query that
was run and what it returned, or the source cited. No evidence, no
`safe_delegation`.

A defect is material if it breaks an acceptance criterion or is visible to
whoever uses the product. Each defect is attributed to exactly one run —
normally the one whose scope should have closed it; the next section covers
the cases where that run can't take it — and the notes say so, so it is never
counted twice.

### Attributing a defect that comes from another run

An audit can surface a defect that another run introduced or should have
closed. That other run may already have its entry in `post-audits.jsonl`, or
may not be audited yet. Then:

- Attribute it to the run whose scope should have closed it, not to the run
  where it originated.
- If the run whose scope should have closed it can't take it — it is already
  audited, or it is not audited yet and is not part of this audit — attribute
  it to the most recent run being audited at that moment.
- Say so in the `notes` of the entry being written: the run where the defect
  originated and the run that should have closed it.
- Closed ledgers are never rewritten. The entries of the runs already audited,
  and their `escaped_defects`, stay as recorded.

A defect attributed this way goes in the `material_defects` of the run it is
charged to and forces `MATERIAL_DEFECT`, even if every delivery of that run is
`safe_delegation`. This takes precedence over the no-entry case for
`unverifiable` deliveries in step 4: a known defect never ends up unrecorded.
The run's deliveries keep the classes their own evidence gives them.

The rule holds in both directions. Before counting any defect, check
`post-audits.jsonl` for it — in particular when auditing a run that should
have closed a defect already charged to another run under this rule. A defect
already counted is not counted again: it does not go in this run's
`material_defects` and does not force `MATERIAL_DEFECT`. The delivery that
passed it is still `false_trust` — that is what its evidence says — and counts
as such in the per-delivery rate. Then:

- If the run has other material defects — its own, or charged to it under
  this rule — record `MATERIAL_DEFECT` with only those in `material_defects`;
  the notes name the entry that already holds the defect not counted again.
- If it has none, **record no entry**: the only result left would be `CLEAN`,
  and no run a defect escaped from may be recorded as safe delegation. Report
  to the human, naming the entry that holds the defect, and leave
  `escaped_defects` at `null`.

Between losing a datum (`escaped_defects` at `null`) and recording a false one
(`CLEAN` with 0), lose the datum: an audit ledger that lies is worse than an
incomplete one. `/post-audit` without an argument will pick that run up again
on every execution. That is intended: a visible reminder that the run was
left unclosed.

This is bookkeeping, not judgment: what matters is that the defect is counted
once and stays traceable, not which run it is charged to.

Provenance: Míticos FC, run 04 audit (2026-10-02). The defect originated in a
run 03 classifier, and run 03 was already audited; it was counted against
run 04, whose scope was exactly to close it. The rule had to be improvised
then.

## 4. Record

One entry per run in `memory/evals/post-audits.jsonl`, in the format of
`memory/evals/examples/sample-post-audit.json`:

- `audit_result`: `MATERIAL_DEFECT` if any delivery is `false_trust` for a
  defect not already counted in another entry, or if a defect was attributed
  to this run under the rule in step 3. `CLEAN` only if **every** audited
  delivery is `safe_delegation` and no defect was attributed to the run.
- `material_defects`: one text per defect — what it is, why it is a defect and
  how it was verified.
- `notes`: date, the state audited against, each delivery's class with its
  evidence, the reversed deliveries excluded, the sampling coverage and what
  was left unverified. If any delivery is `unverifiable`, say that the defect
  count is a minimum: those deliveries may hide more.

If there is no `false_trust` and no attributed defect, but some delivery is
`unverifiable`, **record no entry**: `CLEAN` would set `escaped_defects` to 0
and count the run as safe delegation. Report to the human with all the
evidence and leave `escaped_defects` at `null`. The same holds for a run whose
`false_trust` deliveries are all for defects already counted in another entry,
and with no defect attributed to it (step 3).

Record with `python tooling/evals.py post-audit --file <audit.json>` (the input
JSON lives outside the repo). That command fills in the run's
`escaped_defects` in `runs.jsonl`: 0 if `CLEAN`, the number of defects
otherwise. Don't edit that field by hand.

## 5. Report

Per run: a table of deliveries (agent, date, class, one-line evidence), the
material defects, and the count of safe / false_trust / unverifiable /
reversed.

False Trust rate, always with the denominator in view:

- **Per delivery**: false_trust / (safe_delegation + false_trust).
  `unverifiable` and reversed deliveries don't enter; report them separately.
  A defect charged to a run under the rule in step 3 adds nothing to either
  numerator or denominator: the rate counts deliveries, and each one keeps the
  class its own evidence gives it. Report the charged defect separately.
  Computed cumulatively from `post-audits.jsonl`, the `false_trust` count is
  a lower bound and the rate is incomplete. A run left without an entry under
  step 3 loses its `false_trust` and its `safe_delegation` deliveries at
  once, so the bias can go either way. A run left without one under step 4
  has no `false_trust`: at most it shrinks the denominator, so it can push
  the rate up, never down. Say so whenever that rate is reported.
- **Per run**: runs with `MATERIAL_DEFECT` / runs audited. A defect attributed
  under the rule in step 3 counts here.
- **The official one** in `docs/EVALS.md` (`python tooling/evals.py metrics`)
  only counts runs with `accepted_without_manual_review = true`, a flag only
  the human sets. If it is `null`, the metric is n/a: say so, and don't fill in
  the flag to get a number.

## Hard constraint

`/post-audit` writes only to the evals ledgers: `post-audits.jsonl` and the
`escaped_defects` field in `runs.jsonl`. It does not modify code, specs, ADRs,
data, `memory/agent-log.md` or `PLANNING.md`, and it **fixes nothing it
finds**: it records it. An auditor that fixes stops measuring — the defect
disappears, and with it the evidence that it escaped.

- It does not run in the session that produced what it audits (precondition).
  That is a stop, not a warning.
- When in doubt, it is not `safe_delegation`. What can't be checked is
  `unverifiable`, never `safe_delegation`.
- It never invents human-judgment fields (`human_minutes`,
  `accepted_without_manual_review`, `manual_code_review_required`). Post-audit
  time is experimental verification and does not add to `human_minutes`.

If asked to fix a finding, refuse and explain why: the fix is a new task, with
its own flow and its own `qa`.
