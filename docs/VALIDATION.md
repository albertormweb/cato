# Validation report — Cato 0.0.1

> Re-run of the engineering audit after the master-prompt / tool-alignment work.
> Date: 2026-08-20. Scope: this template repository, not a generated product.

## Mechanical checks (this run)

| Check | Result |
|---|---|
| `python -m pytest tooling/ -c tooling/pytest.ini` | **19 passed** |
| `python tooling/sync_rules.py` | **All 3 copies match `AGENTS.md`** |
| `python tooling/trust_score.py --write` | OK (0 handoffs — expected on blank template) |

These prove the **template integrity**, not that Claude Code + subagents ship a
product end to end. That run is still open in `TECH-DEBT.md`.

## What changed since the prior audit

| Prior finding | Status |
|---|---|
| `architect` / `strategist` instructed to write without Write tools | **Fixed** — Write/Edit in frontmatter; CI asserts writers have Write |
| `reviewer` asked for diffs without Bash | **Fixed** |
| Trivial budget (2) vs strategist-always-first | **Fixed in process** — new features never trivial |
| Empty `domain/` / `skills/` looked like dead weight | **Clarified** — README stubs; fill per project |
| Master-prompt → build path underspecified | **Documented** in `process.md`, `/init-project`, README, FIRST-PROJECT |
| README claimed all limits are “mechanical” / global SSOT via CI | **Fixed in README** (2026-08-20); **`rules-hard.md` heading closed 2026-08-21** — now “durable state, not chat” / instruction-level, matching README |
| Clone URL still placeholder `cato-ai-framework` | **Fixed** (2026-08-21) → `https://github.com/albertormweb/cato.git` |

## Scores (critical, out of 10)

| Dimension | Score | One-line |
|---|---|---|
| Instruction quality | 7 | Prompts match tools; master-prompt path is explicit |
| Architecture & cohesion | 8 | Hard / config / process + role split still strong |
| DRY / single source of truth | 6 | `.claude/` guarded; prose may paraphrase guesses (see config) |
| Enforceability | 5 | Tool allowlists + CI real; budgets/approvals still model-polite |
| Safety & permissions | 6 | Writers can write; hard stops listed; PENDING_APPROVAL still convention |
| Tooling code quality | 7 | 19 tests; config floors still hardcoded in `trust_score.py` |
| Usability | 7 | Clear master-prompt → approve → build loop |
| Documentation | 8 | Aligned this pass; E2E still honestly absent |
| Self-honesty | 9 | Unvalidated E2E and empty benchmarks remain explicit |
| Practical utility | 5 | Template ready for first product run; not yet proven |

**Overall (judgment): 6 / 10** — usable as an internal bootstrap for a first real
product run; not proven for unattended shipping.

**Would use on an internal product now?** Yes as the operating system for Claude
Code, with one human gate after `/init-project`, then build loop. Not as
set-and-forget automation until that E2E run exists.

## Remaining top problems (impact order)

1. **No product E2E yet** — only integrity tests. Fix: run master-prompt path on a real app.
2. **Budgets / PENDING_APPROVAL are not script-enforced** — Fix: keep claims honest; optionally log-based budget check later.
3. **Trust-score labels are free text** — Fix: structured `reversed:` / `avoidable:` fields when logs get real data.
4. **`trust_score.py` hardcodes sample/floor** — Fix: read from `config.md` or a tiny shared constant file.
5. **Portable hosts still get rules only** — Acceptable for Claude-Code-first internal use.

## What “good” means for this repo

Cato is an **instruction framework**, not an application. Success = agents can
execute the written jobs, humans approve the few hard gates, and a master prompt
can drive build without the template contradicting itself. Product correctness
is measured on generated projects, via `benchmarks/` when someone runs them.
