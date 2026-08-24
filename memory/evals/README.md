# Evals storage (v0.1)

Append-only JSONL evidence for whether Cato can be trusted with delegated work,
and whether process changes are worth proposing.

| File | Contents |
|---|---|
| `runs.jsonl` | One JSON object per completed task |
| `interventions.jsonl` | Human supervision events (`task_id`, timestamp, type, duration_minutes, note) |
| `post-audits.jsonl` | Independent experimental audits (`CLEAN` / `MATERIAL_DEFECT`) |
| `proposals.jsonl` | Improvement proposals (`PROPOSED` / `APPROVED` / `REJECTED`) |

**Source of truth for numbers:** these files + `tooling/evals.py`.

**Human-owned:** supervision minutes and delegation flags come from the human
(intervention log), never invented by Cato.

**Post-audit time** is experimental verification — it must not increase
`human_minutes`.

**Human gate:** proposals never rewrite `.claude/`, prompts, or rules. Approval
only updates proposal status. Applying an approved change is a separate human
step (disabled for the frozen experiment).

**CATO PASS** = internal controls only, not objective correctness.

Schema and usage: `docs/EVALS.md`. CLI: `python tooling/evals.py --help`.
