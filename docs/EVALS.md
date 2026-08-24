# Evals v0 and Feedback Loop v0

Evidence that Cato can (or cannot) take delegated development work with less
human supervision — and a small loop that proposes process changes without
applying them.

## Evals v0 — what it measures

Per completed task, Cato can append one JSON object to
`memory/evals/runs.jsonl` via `python tooling/evals.py record`.

Fields (all optional except `task_id`; use `null` when unknown):

- identity: `task_id`, `timestamp`, `task_type`, `risk_level`
- who ran it: `agent`, `model`, `agents_used` (for later multi-model compare)
- requirements / tests / QA: counts and `qa_result`
- process: `retries`, architecture/scope violation counts
- human cost: `human_interventions`, `human_minutes`, review flags
- outcome: `result`, `regressions`, `escaped_defects`, duration/cost if known
- `findings[]`: each with `finding`, `severity`, `detected_by`, `stage`, `resolved`

**Trust report:** `python tooling/evals.py report <task_id>` — compact PASS/FAIL
summary including who detected findings.

**Derived metrics:** `python tooling/evals.py metrics`

| Metric | Definition (v0) |
|---|---|
| Delegation rate | tasks with `accepted_without_manual_review=true` / tasks where that field is known |
| Human supervision | mean `human_minutes` over tasks where it is known |
| CATO catch rate | findings with `detected_by` in Cato roles or `tests` / all recorded findings |
| QA rejection rate | `qa_result` in {FAIL, REJECT} / tasks that reached QA |
| First-pass rate | `result=PASS` and `retries=0` / tasks with known `result` and `retries` |

### What Evals v0 does **not** measure

- Absolute product quality or security.
- Defects nobody recorded (see Catch Rate limitation below).
- Whether Cato beats plain Claude Code (that stays in `benchmarks/`).
- Model quality rankings (fields are stored; no leaderboard yet).
- Magical “trust scores” beyond the existing agent trust-score from HANDOFFs.

## Feedback Loop v0

```text
Task → record run → report / feedback → (optional) propose → human status
```

1. After a task, record the run (orchestrator or human).
2. `python tooling/evals.py feedback <task_id>` prints what happened, what
   failed, where it was detected, a **hypothesis** (not a causal claim), and
   whether a process change might be worth considering. Clean passes do not nag.
3. If a pattern has enough evidence, create a proposal:

   `python tooling/evals.py propose --json '{...}'`

   Status starts as `PROPOSED`. Language must stay associative
   (“appears associated in N tasks”), with `evidence_count`, `confidence`, and
   `counterexamples` when known.
4. Human decides: `python tooling/evals.py set-status IMP-001 APPROVED|REJECTED`

### Human approval

`PROPOSED` proposals **never** modify `.claude/`, prompts, `CLAUDE.md`, or
rules. `set-status` only updates `memory/evals/proposals.jsonl`. Applying an
`APPROVED` change is a separate, deliberate human edit (or a future tool) —
not built in v0.

## Limitations (read this)

> **Absence of findings does not mean absence of errors.**

CATO Catch Rate only uses findings that were written down. Unknown escaped
defects never enter the denominator. Do not treat a high catch rate as proof
that production is safe.

Null fields are skipped in rates; they are not filled with guesses. Incomplete
records must not crash the tooling (they render as `unknown` / `n/a`).

## Commands

```bash
python tooling/evals.py record --file run.json
python tooling/evals.py report DEV-142
python tooling/evals.py metrics
python tooling/evals.py feedback DEV-142
python tooling/evals.py propose --file proposal.json
python tooling/evals.py set-status IMP-001 APPROVED --note "apply manually"
```
