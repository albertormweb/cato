# Evals storage (v0)

Append-only JSONL evidence for whether Cato can be trusted with delegated work,
and whether process changes are worth proposing.

| File | Contents |
|---|---|
| `runs.jsonl` | One JSON object per completed task |
| `proposals.jsonl` | Improvement proposals (`PROPOSED` / `APPROVED` / `REJECTED`) |

**Source of truth for numbers:** these files + `tooling/evals.py`.  
**Human gate:** proposals never rewrite `.claude/`, prompts, or rules. Approval
only updates proposal status. Applying an approved change is a separate human
(or later) step.

Schema and usage: `docs/EVALS.md`. CLI: `python tooling/evals.py --help`.
