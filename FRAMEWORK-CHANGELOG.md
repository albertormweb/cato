# Cato changelog

Already-cloned projects don't get upgrades automatically. This changelog exists so
you can apply them by hand: compare your project's `.framework-version` against
the latest template and apply only the intervening changes.

Format: SemVer. `MAJOR` = breaking change to the agent flow or the hard rules;
`MINOR` = new agent, command or file; `PATCH` = wording and fixes.

## 0.0.1

First release. Nothing shipped before this, so there's no upgrade path yet — this
section exists to be compared against once there is one.

**Orchestration.** A coordinator that plans and delegates rather than implementing,
with a fixed `HANDOFF` block (status, summary, artifacts, next_action) as the only
thing passed between agents. Full context never crosses from one agent to another.

**Eight subagents.** `strategist`, `researcher`, `architect`, `designer`,
`implementer`, `qa`, `reviewer`, `docs` — each with declared tools and an explicit
list of what it doesn't do.

**Rules split three ways.** `rules-hard.md` for constraints that change only by
decision, `config.md` for every tuneable number in one place, `process.md` for
modes of operation. Calibration touches only `config.md`.

**Memory in four layers.** ADRs for decisions, `session-log.md` for narrative
continuity, `agent-log.md` as an append-only audit trail, `trust-score.md`
generated from that trail rather than hand-written.

**Loop mode with progressive validation.** `qa`'s threshold rises each iteration,
with caps and early exit on repeated identical failures.

**Commands.** `/init-project` (with `--interview` and `--dry-run`),
`/harvest-debt` for the `SHORTCUT:` ledger, `/calibrate` for checking the
framework's own numbers against a real session.

**Portability.** `AGENTS.md` carries the ruleset to hosts that read it, with
copies for Cursor, Cline and Copilot kept in sync by `tooling/sync_rules.py`.

**Tooling.** Optional Python in `tooling/`: score derivation, rule-copy sync, and
tests that validate the framework's own structure — agent frontmatter, internal
references, and guards against config values or the minimalism ladder being
restated in more than one place.

**0.0.1 follow-ups (same version).** Agent Write/Edit aligned with file ownership;
reviewer Bash for diffs; master-prompt build + autonomy hard-stops in
`process.md`; `domain/` and `.claude/skills/` README stubs; structure test for
writers; documentation pass + `docs/VALIDATION.md` re-audit (overall 6/10:
template ready, product E2E still open); `DESIGN.md` / `PLANNING.md` /
`specs/0001-cato-framework.md` describe the template itself; genesis ADR
`memory/adr/0001-cato-as-instruction-framework.md`.

## Upgrading an already-cloned project

1. Check your project's `.framework-version`.
2. Read the entries above newer than that version.
3. Copy the new `.claude/` and root files that apply. Never overwrite
   `PLANNING.md`, `DESIGN.md`, `specs/`, `domain/`, `design/` or `memory/` —
   those are project-owned content, not framework files.
4. Run `python tooling/sync_rules.py --fix` if `AGENTS.md` changed.
5. Run `python -m pytest tooling/ -c tooling/pytest.ini` to catch broken
   references introduced by a partial copy.
6. Update your project's `.framework-version` when done.
