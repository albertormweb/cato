# Cato

> A team of agents for Claude Code.

**Status: 0.0.1.** Template integrity is tested; a full product run end to end has
not been measured yet. Budget numbers and thresholds are starting guesses. See
`TECH-DEBT.md` and `docs/VALIDATION.md`.

Cato is an **internal** template: Claude Code as an **orchestrator of subagents**.
You paste a **master prompt**, it bootstraps architecture and an MVP cut, you
approve once, then it builds through `PLANNING.md` with specialists, verification,
and isolated context so token cost stays bounded across sessions.

## Why this exists

Claude Code out of the box is a single agent with session memory. That works well
for one-off tasks and worse as a project grows: context is lost between sessions,
decisions contradict earlier ones, features nobody asked for get built, and
there's no way to audit what happened or why.

The premise: the edge is everything around the model — tools, memory, context,
permissions, evaluation, and checks that what the agent did is actually correct.

In concrete pieces:

- **Separate roles** with different tool permissions — nobody validates their own work.
- **Split guardrails** — hard constraints vs tuneable numbers vs process
  (`.claude/rules-hard.md`, `config.md`, `process.md`).
- **Compressed memory** — ADRs, `session-log.md`, append-only `agent-log.md`.
- **Cost budget** — invocation limits by task size (orchestrator-enforced; see honesty below).
- **Master-prompt bootstrap** — describe the product; generate design + plan; build.

## Quickstart

```bash
git clone https://github.com/albertormweb/cato.git my-project && cd my-project
./setup.sh
```

`setup.sh` asks for a name, a stack and (optionally) a master prompt. Or in Claude Code:

```
/init-project "SaaS for monitoring public tenders, FastAPI + PostgreSQL, multi-tenant"
/init-project "..." --interview
/init-project "..." --dry-run
```

Output: `DESIGN.md`, `PLANNING.md`, `specs/0001-*.md`, genesis ADR. Non-MVP work is
parked as V2/FUTURE. Genesis design sits at `PENDING_APPROVAL`. After you approve:

```
Build PLANNING.md Now; work in a loop until the first milestone ships.
```

That is the intended loop: **master prompt → scope cut → approve once → agents build**.
Details: `.claude/process.md`. Walkthrough: `docs/FIRST-PROJECT.md`. Vocabulary:
`docs/CONCEPTS.md`. Latest integrity audit: `docs/VALIDATION.md`.

## The agents

| Agent | Does | Doesn't |
|---|---|---|
| `strategist` | MVP/V2/FUTURE cut; kickoff interview; may write planning/spec notes | Architecture or app code |
| `researcher` | Context from code, docs, prior art | Design or implement |
| `architect` | Owns and **writes** `DESIGN.md`, kickoff `PLANNING.md`, ADRs, `DEPLOYMENT.md` | Application code |
| `designer` | Wireframes/mockups in `design/` | Business or technical architecture |
| `implementer` | Code + test in the same change | Architecture; self-validate |
| `qa` | Runs tests, coverage, reports gaps | Write tests; fix failures |
| `reviewer` | Critical review (`git diff`); flags over-building | Quiet rewrites |
| `docs` | README / CHANGELOG / user-facing docs | Application code |

Default flow:

```
strategist → researcher → architect → designer (if UI)
          → implementer → qa → reviewer → docs
```

Every agent returns a fixed `HANDOFF` (status, summary, artifacts, next_action).
Only the summary crosses agents — that bounds token use.

## The minimalism ladder

`implementer` walks a seven-rung checklist before writing code (full text:
`.claude/minimalism-ladder.md`). Lazy about the solution, never about reading.
Validation, error handling, security and accessibility are never cut.
`reviewer` treats a skipped simpler rung as a finding. Deliberate deferrals use
`SHORTCUT:`; `/harvest-debt` sweeps them into `TECH-DEBT.md`.

## Autonomy and guardrails

**Autonomy (master-prompt build):** on trivial/medium work, do not pause between
agents. On large work, one plan summary then run. Stop only for hard stops
(secrets, merge to `master`, `.claude/` edits, new deps, `PENDING_APPROVAL`,
`BLOCKED`, budget exceeded, loop failure). See `.claude/process.md`.

**What is mechanically checked today**

- Agent frontmatter / roster / write-tool alignment, reference integrity, ladder
  duplication, and (inside `.claude/`) restated tuneable literals — `tooling/` + CI
- Portable ruleset copies match `AGENTS.md` — `sync_rules.py` + CI
- Trust-score **arithmetic** from the audit log — `trust_score.py`

**What still depends on the orchestrator / model obeying instructions**

- Invocation budgets and retry caps
- Moving or honouring `PENDING_APPROVAL`
- Annotating `avoidable` / `reversed` for a meaningful trust score
- Actually running tests before `qa: PASS` (enforced by instruction + review, not a binary gate)

Tuneable numbers live only in `.claude/config.md` as the source of truth. CI fails
if selected literals are restated elsewhere **under `.claude/`** (except
`calibrate.md`). Narrative docs may say “starting guesses” and point here — they
must not invent a second authoritative table.

Human-only: merge to `master`, deletes outside scratch, `.claude/` edits, new
dependencies, secrets, and `PENDING_APPROVAL` → `APPROVED`.

## Loop mode, trust score and dry-run

**Loop mode.** `implementer → qa` with a rising bar each iteration (fast → full +
coverage → prior edge cases). Caps and early exit on identical failures: see
`config.md` (do not hardcode the numbers in other files).

**Trust score.** Generated by `tooling/trust_score.py` from `memory/agent-log.md`.
Labels must be honest or every agent looks perfect.

**Dry-run.** `--dry-run` prints agents, files, budget tier, and approvals — writes
nothing.

## Calibration

Numbers in `config.md` are guesses until `/calibrate` compares them to a real
`agent-log.md`. Proposals go to `PENDING_APPROVAL`. `benchmarks/` holds the method
for comparing Cato to plain Claude Code; results folders stay empty until a fair
run exists.

## Other agent hosts

`AGENTS.md` (+ synced Cursor / Cline / Copilot copies) carries phases and hard
rules without subagents. Claude Code gets the full system.

## Commands

| Command | What it does |
|---|---|
| `/init-project "<master prompt>"` | Bootstrap design, plan, specs, genesis ADR |
| `/init-project "..." --interview` | Interview gaps first |
| `/init-project "..." --dry-run` | Preview only |
| `/harvest-debt` | Collect `SHORTCUT:` into `TECH-DEBT.md` |
| `/calibrate` | Propose `config.md` edits from a real session log |

## Structure

```
CLAUDE.md                    # entrypoint (@-imports .claude/)
AGENTS.md                    # portable ruleset
docs/                        # CONCEPTS, FIRST-PROJECT, VALIDATION
.claude/
  rules-hard.md | config.md | process.md
  claude-orchestrator.md | claude-personas.md | minimalism-ladder.md
  claude-brand-style.md      # fill per product
  commands/ | agents/ | skills/   # skills start empty (README stub)
PLANNING.md | DESIGN.md | DEPLOYMENT.md
design/ | specs/ | domain/   # domain starts empty (README stub)
tests/ | memory/ | tooling/ | benchmarks/
TECH-DEBT.md | FRAMEWORK-CHANGELOG.md
```

## Testing

Product tests: fill `tests/README.md` (fast + full). `qa` reads it literally.
Framework tests: `python -m pytest tooling/ -c tooling/pytest.ini`.

## Tooling

```bash
python tooling/trust_score.py --write
python tooling/sync_rules.py
python -m pytest tooling/ -c tooling/pytest.ini
```

Optional for day-to-day building; required for CI / template health.

## Versioning

`.framework-version` + `FRAMEWORK-CHANGELOG.md`. Upgrades are manual; never
overwrite project-owned `PLANNING.md`, `DESIGN.md`, `specs/`, `domain/`, `memory/`.

## Adapting it

- Fill `claude-brand-style.md` before user-facing output.
- Fill `tests/README.md` before trusting `qa: PASS`.
- Map model tiers in `config.md` to your Claude Code aliases.
- Run `/calibrate` after real sessions.
- Add skills under `.claude/skills/` when a workflow repeats; add domain notes
  under `domain/` as the product language firms up.

## About the name

Cato the Censor reviewed, approved, and could veto — nothing moves without someone
authorised to stop it.

## License

MIT — see `LICENSE`.
