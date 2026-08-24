# Evals v0.1 and Feedback Loop v0

Experimental measurement for CATO’s control-plane hypothesis: whether structured
Harness Engineering can increase **delegation** to coding agents while reducing
**human supervision** without raising defects, regressions, or **false trust**.

This is **not** an observability SaaS, not “Datadog for agents,” and not proof
that Cato already improves outcomes. It records evidence so a pilot can test the
hypothesis. Conceptual framing: `docs/POSITIONING.md`.

**v0.1 is a measurement instrument**, not a Cato capability upgrade. It fixes
three experimental blockers: human-owned supervision data, post-audit / false
trust, and unambiguous CATO PASS semantics.

## CATO PASS semantics

`result: PASS` (and a green Trust Report) means only:

> **Internal Cato controls passed.**

It does **not** mean the implementation is objectively correct, that there are
no bugs, that it is safe to delegate, or that experimental post-audit is
unnecessary. Safe delegation is evidenced only by independent post-audit.

## Human supervision (KPI)

`human_minutes` / task is the primary supervision KPI. These fields are
**human-owned** — Cato must not invent or autocomplete them:

- `human_intervention_log[]` — preferred source
- `human_interventions` / `human_minutes` — derived from the log when present
- `manual_code_review_required`
- `accepted_without_manual_review`

Each intervention:

```json
{
  "task_id": "DEV-142",
  "timestamp": "2026-08-24T10:14:00+00:00",
  "type": "requirement_clarification",
  "duration_minutes": 2,
  "note": "Clarified whether cancelled contracts should be included."
}
```

Record during the task:

```bash
python tooling/evals.py intervention --json '{...}'
```

When you `record` the run, ledger interventions for that `task_id` are merged
and `human_minutes` is the sum of `duration_minutes`. Missing information stays
`null` / renders as `unknown` — **never invent `0`**. An explicit empty log
`[]` means the human recorded zero interventions → `0` minutes (known zero).

Separate clocks:

| Clock | Field | Counts |
|---|---|---|
| AI / task execution | `total_duration_minutes` | Wall / agent work |
| Human supervision | `human_minutes` | Interventions while deciding/delegating |
| Experimental verification | post-audit (separate ledger) | **Must not** add to `human_minutes` |

## Delegation vs Safe Delegation vs False Trust

| Metric | Definition |
|---|---|
| **Delegation rate** | `accepted_without_manual_review=true` / tasks where that field is known |
| **Safe delegation rate** | post-audit `CLEAN` / delegated tasks **with a completed post-audit** |
| **False trust rate** | post-audit `MATERIAL_DEFECT` / delegated tasks **with a completed post-audit** |

Unaudited delegated tasks are **excluded** from Safe Delegation and False Trust
denominators. Delegation alone only shows the human chose to trust.

### Post-audit

After Cato finishes, the Trust Report is produced, and the human accepts or
rejects (possibly without exhaustive review), record an independent audit later:

```bash
python tooling/evals.py post-audit --file audit.json
```

Minimal record (`memory/evals/post-audits.jsonl`):

```json
{
  "task_id": "DEV-142",
  "timestamp": "...",
  "audit_result": "CLEAN",
  "material_defects": [],
  "notes": "Spot-checked requirements vs diff"
}
```

or `"audit_result": "MATERIAL_DEFECT"` with `material_defects: ["..."]`.

Post-audit time is **experimental verification**, not supervision required to
delegate.

### Escaped defects

`escaped_defects` stays `null` / unknown until there is later evidence. Do not
store `0` merely because Cato found nothing. A completed post-audit updates the
run: `CLEAN` → `0`, `MATERIAL_DEFECT` → defect count (or 1 if the list is empty
but the result is MATERIAL_DEFECT).

## Evals — what is stored

Per completed task, append one JSON object to `memory/evals/runs.jsonl` via
`python tooling/evals.py record`.

Fields (all optional except `task_id`; use `null` when unknown):

- identity: `task_id`, `timestamp`, `task_type`, `risk_level`
- who ran it: `agent`, `model`, `agents_used`
- requirements / tests / QA: counts and `qa_result`
- process: `retries`, architecture/scope violation counts
- human (owned): intervention log / derived minutes, review flags
- outcome: `result`, `regressions`, `escaped_defects` (null until evidence)
- duration/cost: `total_duration_minutes` = AI/task execution
- `findings[]`: each with `finding`, `severity`, `detected_by`, `stage`, `resolved`

**Trust report:** `python tooling/evals.py report <task_id>` — compact summary
plus PASS disclaimer and separate AI vs human clocks.

**Derived metrics:** `python tooling/evals.py metrics`

Also still reported: CATO catch rate, QA rejection rate, first-pass rate (same
definitions as v0).

### What Evals do **not** measure

- Absolute product quality or security from a CATO PASS alone.
- Defects nobody recorded (see Catch Rate limitation).
- Whether Cato beats plain Claude Code (`benchmarks/`).
- Model quality rankings.

## Feedback Loop v0

```text
Task → record run → report / feedback → (optional) propose → human status
```

1. After a task, record the run (orchestrator or human). Human fields must come
   from the human (intervention log / explicit flags).
2. `python tooling/evals.py feedback <task_id>` — hypothesis language only.
3. Pattern with enough evidence → `propose` (`PROPOSED` only).
4. Human: `set-status IMP-001 APPROVED|REJECTED`

### Human approval / freeze

`PROPOSED` proposals **never** modify `.claude/`, prompts, `CLAUDE.md`, or
rules. `set-status` only updates `memory/evals/proposals.jsonl`. Applying an
`APPROVED` change is a separate deliberate human edit — **not** built in.
During the first experiment, store proposals but **do not apply** them (Cato
frozen).

## Limitations (read this)

> **Absence of findings does not mean absence of errors.**
> **CATO PASS does not mean objectively correct.**

CATO Catch Rate only uses findings that were written down. Unknown escaped
defects never enter that denominator until post-audit (or other evidence)
updates `escaped_defects`.

Null fields are skipped in rates; they are not filled with guesses.

## Commands

```bash
python tooling/evals.py intervention --file intervention.json
python tooling/evals.py record --file run.json
python tooling/evals.py report DEV-142
python tooling/evals.py post-audit --file audit.json
python tooling/evals.py metrics
python tooling/evals.py feedback DEV-142
python tooling/evals.py propose --file proposal.json
python tooling/evals.py set-status IMP-001 APPROVED --note "apply manually later — not now"
```
