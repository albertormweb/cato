# Tooling

Scripts that maintain the **framework template**. Optional for building a product
with Cato; used by CI and anyone who cares that instructions stay consistent.

They exist because some jobs should not rely on an LLM being honest with itself:
deriving the trust score from the audit log, keeping portable rule copies in
sync, and computing eval metrics / proposal status from JSONL without inventing
numbers. Structure tests catch silent instruction rot (stale tools, broken refs,
duplicated ladders, writers without Write).

## `trust_score.py`

```bash
python tooling/trust_score.py           # print the table
python tooling/trust_score.py --write   # rewrite memory/trust-score.md
```

Labels (`avoidable`, `reversed`) in `memory/agent-log.md` matter — see
`.claude/process.md`.

## `evals.py`

Evals v0 + Feedback Loop v0 — append task evidence, trust reports, metrics,
feedback text, and improvement proposals that never auto-apply to `.claude/`.

```bash
python tooling/evals.py record --file run.json
python tooling/evals.py report TASK_ID
python tooling/evals.py metrics
python tooling/evals.py feedback TASK_ID
python tooling/evals.py propose --file proposal.json
python tooling/evals.py set-status IMP-001 APPROVED
```

See `docs/EVALS.md` and `memory/evals/`.

## `sync_rules.py`

```bash
python tooling/sync_rules.py          # check; exit 1 if stale
python tooling/sync_rules.py --fix    # rewrite copies from AGENTS.md
```

Copies: `.cursor/rules/cato.md`, `.clinerules/cato.md`,
`.github/copilot-instructions.md`.

## Tests

```bash
python -m pytest tooling/ -c tooling/pytest.ini
```

Covers: roster + frontmatter, **writers must include Write**, reviewer Bash,
internal `` `*.md` `` references, tuneable literals not restated under `.claude/`
(except `config.md` / `calibrate.md`), ladder not duplicated outside the accepted
pair, docs linked from README, hard rules free of percentage knobs, `CLAUDE.md`
imports the split files, ruleset sync, trust-score parsing.

Requires `pytest` only.
