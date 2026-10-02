# Changelog

All notable changes to Cato — the framework itself, not projects built with it.

Already-cloned projects don't get upgrades automatically. This changelog exists
so you can apply them by hand: compare your project's `.framework-version`
against the entries below and apply only the intervening changes.

## Upgrading an already-cloned project

1. Check your project's `.framework-version`. It holds the version without the
   `v` (`0.3`). A value of `0.0.1` predates this numbering: the file was not
   bumped for v0.2, so treat it as v0.1 and read the v0.2 entry too.
2. Read the entries below newer than that version.
3. Copy the new `.claude/` and root files that apply. Never overwrite
   `PLANNING.md`, `DESIGN.md`, `specs/`, `domain/`, `design/`, `memory/` or
   `CHANGELOG.md` — those are project-owned content, not framework files. In a
   cloned project `CHANGELOG.md` is the product's own changelog, kept by
   `docs`: read the framework's entries in the Cato repository instead of
   copying this file over it.
4. Run `python tooling/sync_rules.py --fix` if `AGENTS.md` changed.
5. Run `python -m pytest tooling/ -c tooling/pytest.ini` to catch broken
   references introduced by a partial copy.
6. Update your project's `.framework-version` when done.

## v0.3.1 — Bias-direction corrections (2026-10-02)

Documentation only, no code. v0.3 shipped imprecise claims about which way
runs without a post-audit entry bias the False Trust rates; step 5 of
`.claude/commands/post-audit.md` and `TECH-DEBT.md` now state each direction
with the definition it holds under, for the per-delivery and the per-run rate.
It took five review passes over those claims, across v0.3 and this release:
every flaw was in prose — most in text dictated by the human, two in the
orchestrator's own wording — and none in code. The `v0.3` tag stays where it
is, so the history stays visible: published, imprecision found, corrected.
`.framework-version` is now `0.3.1`.

## v0.3 — Post-audit (2026-10-02)

Source: run 04 of the Míticos FC pilot and its post-audit on 2026-10-02.

### Added

- **`/post-audit`** (`.claude/commands/post-audit.md`). Audits a closed run's
  PASS deliveries against today's code and data, classifies each one
  (`safe_delegation` / `false_trust` / `unverifiable`) and records the result
  in `memory/evals/`. Never fixes what it finds, and refuses to run in the
  session that produced what it audits. Ported from the pilot repo. Validated
  on Míticos FC run 04 on 2026-10-02: on its first execution it found a
  material defect that four runs and every inline control had missed — players
  with `primera_verificada = True` who had only played in the second division
  (Segunda) for the attributed club, about 4% of the pool.
- **Attribution rule for defects that come from another run** (same file). The
  defect goes to the run whose scope should have closed it, not the run where
  it originated; if that run is already audited, or not audited yet and not
  part of this audit, it goes to the most recent run being audited. It is
  recorded in that run's `material_defects` and forces `MATERIAL_DEFECT`, so a
  known defect never ends up unrecorded; it counts in the per-run rate, not
  the per-delivery one. The notes name the run of origin and the run that
  should have closed it, a later audit checks `post-audits.jsonl` before
  counting so the defect is never counted twice, and closed ledgers are never
  rewritten. No run a defect escaped from is recorded as `CLEAN`: if every
  defect it passed is already counted elsewhere and it has none of its own
  and none charged to it, no entry is recorded and `escaped_defects` stays
  `null`. Such a run loses its `false_trust` and its `safe_delegation`
  deliveries at once, so computed from the ledger the `false_trust` count is
  a lower bound and the per-delivery rate is incomplete, with a bias that can
  go either way (recorded in `TECH-DEBT.md`). Missing in the pilot version,
  where it had to be improvised during the run 04 audit.

Pilot False Trust rates after this audit, as reported by the command:

| Measure | Rate |
|---|---|
| Per delivery, run 04 | 1/10 |
| Per delivery, pilot cumulative | 4/25 (16%) |
| Per run, with a material defect | 4/4 |

The pilot figures are not affected by that incompleteness: all four runs have
an entry, so 4/25 is exact.

The official False Trust rate of `docs/EVALS.md` is still n/a:
`accepted_without_manual_review` is `null` in all four runs.

### Fixed

- **`tooling/evals.py` on Windows consoles.** `post-audit`, `record`,
  `intervention` and `set-status` wrote their entry and then crashed with
  `UnicodeEncodeError` when printing `→`. Those messages now use `->`, and any
  other character the output encoding can't represent (ledger text in
  `report` or `feedback`) is written as a backslash escape instead of crashing
  or being dropped. No `PYTHONIOENCODING` needed.

### Changed

- **One changelog.** `FRAMEWORK-CHANGELOG.md` is gone; its upgrade
  instructions live at the top of this file and its description of the first
  release is now the v0.1 entry.
- **`.framework-version`** 0.0.1 → 0.3. It now follows this changelog's
  numbering (v0.2 → v0.3), not SemVer.
- **Tags** `v0.2` (on the v0.2 commit, `873bc59`) and `v0.3`. The earlier
  `CATO-experimental-v0` and `CATO-experimental-v0.1` tags stay as they are.

## v0.2 — Pilot calibration (2026-08-30)

First revision backed by evidence rather than reasoning. Source: a three-run
pilot on a real product (Míticos FC), runs 01-03. Each change names the run
that motivated it and, where applicable, the run that validated it.

### Added

- **Asking the human at `PENDING_APPROVAL`** (`.claude/process.md`). Agents now
  present the artifact's options directly in-session via the input tool instead
  of parking the run until the human returns with a new prompt. The artifact
  stays the record; no-self-approval is untouched. Motivated by run 02 (six
  gates, six session exits). Validated in run 03: nine decisions taken
  in-session, zero exits.
- **`/close-run`** (`.claude/commands/close-run.md`). Dumps objective run
  metrics to `memory/evals/`, scaffolds the human observation notes, updates the
  run index. Never writes the judgment sections. Ported from the pilot repo. On
  first execution it detected there was no run to close, found the objective
  records for runs 01-02 missing, and backfilled them unprompted, respecting the
  judgment-section constraint.

### Changed

- **Agent budgets** (`.claude/config.md`): medium 5 → 6, large 8 → 14. At 8,
  the budget ran out before `reviewer`'s second pass — the pass that caught a
  production-breaking blocker after `implementer` and `qa` had both returned
  PASS. Motivated by run 02 (closed at 13/14 and still needed an extension).
  Applied in run 03.
- **Progressive validation note** (`.claude/config.md`): iteration 2 requires
  coverage, so the tool must be installed and `tests/README.md` must not forbid
  it. Run 02: `qa` ended `BLOCKED` on that contradiction.
- **Trust-score note** (`.claude/config.md`): the 70% floor confirmed working
  in run 02 — orchestrator flagged two agents under the floor without touching
  `.claude/`.

### Tried and not adopted

- **Raising `qa` from Mechanical to Judgment tier** with a reinforced prompt.
  Tested in run 03: no improvement, trust score fell from 75% to 63.6%. Tier
  stays Mechanical. The open hypotheses (role badly defined vs. structurally
  redundant) are recorded in `TECH-DEBT.md`.

## v0.1 — Experimental

Initial framework: orchestrator, personas, hard rules, config, minimalism
ladder, trust score, evals v0.1. Reasoned, not measured. See `docs/VALIDATION.md`.

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

First released as `0.0.1` in `.framework-version`.
