# Cato — agent rules

Portable version of the Cato ruleset, for agent hosts that read `AGENTS.md`
(Codex, Amp, Jules, OpenCode, Qoder, CodeWhale, Junie, and others).

Claude Code users get the full system — subagents with isolated context, slash
commands, per-agent model selection — from `CLAUDE.md` and `.claude/`. What
follows is the part that survives without subagent support: the roles become
modes you switch between, and the guardrails stay as hard rules.

This file deliberately restates the ladder rather than linking to it, because
hosts reading this have no access to `.claude/`. It's the one duplication the
framework accepts, and CI checks it doesn't spread further.

## Where to look

- Current state, next task, anything at `PENDING_APPROVAL` → `PLANNING.md`
- Architecture and high-level decisions → `DESIGN.md`
- Wireframes and mockups → `design/`
- Infrastructure and deployment → `DEPLOYMENT.md`
- Requirements per feature → `specs/`
- Closed decisions → `memory/adr/`
- Session history → `memory/session-log.md`
- Known technical debt → `TECH-DEBT.md`

Don't read outside this list unless the task requires it.

## Master-prompt style

When the human gives one product description: cut MVP vs later work first, write
design and a concrete `PLANNING.md → Now`, then build that backlog. Prefer
continuing without asking permission every step. Stop for secrets, merges to
`master`, dependency installs, `.claude/` edits, `PENDING_APPROVAL`, true
ambiguity (`BLOCKED`), or the same failure twice.

## Work in phases, not all at once

Even without separate subagents, run the work in distinct passes and don't blur
them together:

1. **Strategy** — is this worth building now? Sort into MVP / V2 / FUTURE. The
   burden of proof is on the feature, not on its absence. If it isn't needed to
   validate the main hypothesis, it waits.
2. **Research** — read the existing code and trace the real flow before designing.
3. **Design** — non-trivial decisions get an ADR in `memory/adr/` before
   `DESIGN.md` changes.
4. **Implementation** — walk the minimalism ladder (below). Write the test in the
   same change as the logic.
5. **Validation** — actually run the tests. Report the exact failure; never claim
   passing without running.
6. **Review** — reread the diff critically, including for over-building.

## The minimalism ladder

Before writing code, stop at the first rung that holds:

```
1. Does this need to exist?      → no: skip it
2. Already in this codebase?     → reuse it
3. Does the stdlib do it?        → use it
4. Native platform feature?      → use it
5. Already-installed dependency? → use it
6. Fits in one line?             → one line
7. Only then: the minimum that works
```

The ladder runs *after* understanding the problem, not instead of it. Lazy about
the solution, never about reading. Validation at trust boundaries, error handling,
security and accessibility are never on the chopping block — code ends up small
because it's what the task needs, not because it's golfed.

## Deferred shortcuts

Mark deliberate shortcuts inline so they don't vanish:

```python
# SHORTCUT: no pagination — fine under ~200 rows, revisit if the table grows
```

These get collected into `TECH-DEBT.md`. Don't use the marker to excuse skipping
validation or error handling — those aren't shortcuts, they're omissions.

## Never without explicit human approval

- Merging to `master`
- Deleting files outside scratch/tmp
- Modifying anything in `.claude/` or this file
- Installing new dependencies without justifying it
- Touching credentials, `.env`, or secrets

## Always

- Don't call a task done without running the tests and reporting the result.
- Ambiguity in the spec means stop and ask — never assume.
- Record non-trivial design decisions as ADRs.
- Artifacts marked `PENDING_APPROVAL` in `PLANNING.md` block implementation until
  the human approves them. You don't self-approve.
- When you stop because information is missing, say so plainly and park the task.
  Stopping is correct; inventing the missing information is not.

## Don't grind

If the same approach fails twice, stop and escalate rather than trying variations
indefinitely. A repeated failure usually means the spec or the design is wrong,
not the implementation.
