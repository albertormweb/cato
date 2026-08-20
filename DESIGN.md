# Design

> Framework design for **Cato** (this repository). Edited only by the `architect`
> agent for structural changes, with an ADR when non-trivial. Product apps
> generated from this template replace this file via `/init-project`.

## Stack

- **Product surface:** Markdown instructions consumed by Claude Code (and a
  portable subset via `AGENTS.md`).
- **Optional enforcement:** Python 3 + pytest under `tooling/` (trust score,
  ruleset sync, structure tests). CI runs those checks.
- **Not in scope as a runtime:** no application server, no package to install for
  end users of generated products.

## Main modules

| Area | Responsibility |
|---|---|
| `.claude/rules-hard.md` | Non-tuneable constraints (approvals, no self-validation) |
| `.claude/config.md` | Single place for budgets, retries, loop caps, coverage floors |
| `.claude/process.md` | Autonomy, master-prompt build, loop mode, dry-run, observability |
| `.claude/claude-orchestrator.md` | Coordinator behaviour and HANDOFF protocol |
| `.claude/agents/*.md` | Eight specialists with tools matching their write/read jobs |
| `.claude/commands/` | `/init-project`, `/harvest-debt`, `/calibrate` |
| `memory/` | ADRs, session log, agent audit log, generated trust score |
| `tooling/` | Scripts + tests that enforce what prose cannot |
| `docs/` | Concepts, first-project walkthrough, validation report |
| `domain/`, `.claude/skills/` | Per-project fill (stubs only in the template) |

## Key architectural decisions

1. **Instructions are the product.** Judge markdown as code: cohesion, SSOT,
   tool/frontmatter consistency.
2. **Hard vs config vs process.** Calibration may retune numbers; it must not
   quietly rewrite constraints.
3. **No self-approval.** Implementer ≠ qa ≠ reviewer; only the human moves
   `PENDING_APPROVAL` → `APPROVED`.
4. **Master-prompt build.** One descriptive prompt bootstraps MVP cut + design;
   one human gate; then agents drain `PLANNING.md` with hard stops only.
5. **Isolated subagent context + summary HANDOFFs.** Cost control and role
   separation; full transcripts do not cross agents.
6. **Mechanical where we can, honest where we cannot.** CI/tool allowlists/scripts
   for sync, structure, score math; budgets and approval labels remain
   orchestrator discipline until proven otherwise.

## Out of scope (for now)

- Selling Cato as a hosted product
- Guaranteeing unattended merge-to-`master` without a human
- Non-Claude-Code hosts getting full subagent isolation
- Published benchmark numbers (method only, in `benchmarks/`)
- A dedicated content-production agent (see `TECH-DEBT.md`)
