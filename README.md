# CATO

**AI Software Engineering Control Plane**

> Delegate more software development to coding agents without losing control of
> quality, architecture, safety, and traceability.

**The model is the worker. The harness is the engineering system around it.**

CATO applies **Harness Engineering** to AI software development: it is the
control layer around coding agents — roles, process, architecture, permissions,
verification, memory, traceability, and measurement — so teams can increase
**delegation** without relying on hope.

**Status.** Template integrity is tested (`docs/VALIDATION.md`). Product
end-to-end outcomes and whether CATO improves safe delegation are **not yet
demonstrated**. The frozen experimental baseline is `CATO-experimental-v0.1`
(measurement-ready). See `TECH-DEBT.md`, `docs/EVALS.md`, `docs/POSITIONING.md`.

CATO currently uses **Claude Code** as its primary execution environment
(orchestrator + subagents). That is an implementation detail: conceptually CATO
sits above coding agents, not inside one vendor forever.

---

## The problem

Coding agents can already write a lot of software. Capability alone does not
create **delegation confidence**.

Without an engineering system around the model, projects tend to:

- lose decisions between sessions;
- contradict earlier architecture;
- expand scope nobody asked for;
- claim “done” without independent checks;
- fail **silently** — technically successful, semantically wrong
  (wrong price, wrong customer, wrong business rule).

**Agent capability ≠ delegation confidence.**

A better model is a more capable worker. That still leaves the question: how much
software can you safely hand off without the owner inspecting every change?

---

## Why prompt + skills are not enough

| Layer | Role |
|---|---|
| **Prompt** | A concrete instruction (“paint this room”) |
| **Skill** | A procedure manual (how this kind of work is usually done) |
| **Spec** | What to build, what not to change, what “done” means |
| **Harness (CATO)** | The company that runs the construction project: planning, specialists, permissions, inspection, records, improvement |

> A better prompt gives a clearer instruction. A better skill gives a better
> procedure. A harness builds the engineering system that lets the worker operate
> with autonomy **and** control.

**Instructions influence behavior. Controls constrain what can happen.**

Example: “Do not modify the database schema” is an instruction. A control
withholds permission or requires explicit authorization. “Review your work” is a
skill; “the implementer cannot approve its own work” is a control.

---

## Harness Engineering

> Harness Engineering is the discipline of designing the system around an AI
> model so it can operate with greater autonomy inside a controlled, verifiable,
> and traceable engineering process.

CATO is an instance of that discipline for software engineering with coding
agents. Longer thesis, hotel analogy, and “what CATO is not”: `docs/POSITIONING.md`.

---

## How CATO works (four layers)

| Layer | Question | Examples in this repo |
|---|---|---|
| **1 — DEFINE** | What are we building? | Master prompt, skills, specs, `strategist` |
| **2 — PRODUCE** | How are we building it? | Researcher, architect, planning, orchestrator, implementer, HANDOFFs |
| **3 — CONTROL** | Can we trust the process and result? | Tests, QA, reviewer, guardrails, permissions, memory, logs, CI |
| **4 — IMPROVE** | How do we make the next run better? | Session/agent logs, Evals (experimental), Feedback Loop (human-approved), benchmarks |

CONTROL exists so one actor cannot effectively: interpret → decide → implement →
verify → approve itself.

**Honest map of maturity** (do not read the table as “all of this is proven”):

| Area | State today |
|---|---|
| Roles, HANDOFF, hard rules, master-prompt bootstrap | **Implemented** (instruction framework; many gates are instruction-level) |
| Tool allowlists, CI structure/sync, trust-score math | **Implemented** (mechanical) |
| Budgets / `PENDING_APPROVAL` honouring | **Partial** (orchestrator discipline, not a filesystem lock) |
| Evals v0.1 + post-audit metrics | **Experimental** (measurement instrument) |
| Feedback Loop | **Experimental** — proposals need humans; **no** auto-apply to `.claude/` |
| Autonomous self-learning / enterprise observability SaaS | **Not present** |
| Proof that CATO improves safe delegation | **Not yet** — hypothesis under test |

---

## Experimental status

**Hypothesis CATO is testing:**

> Can CATO increase the share of software development delegated to coding agents
> while reducing human supervision, without significantly increasing defects,
> regressions, or false trust?

**Metrics currently instrumented** (see `docs/EVALS.md`): Human Supervision,
Delegation Rate, Safe Delegation Rate, False Trust Rate, escaped defects
(unknown until post-audit evidence).

| Term | Meaning |
|---|---|
| **Delegation** | Human accepted without exhaustive manual review |
| **Safe Delegation** | Delegated **and** later independent post-audit found no material defect |
| **CATO PASS** | Internal CATO controls passed — **not** objective correctness |

Feeling confident ≠ having evidence that confidence was justified.

Frozen tag for the first pilot: **`CATO-experimental-v0.1`**.

---

## What CATO is not

- Another coding model or a Claude Code replacement  
- Just prompts, just skills, or “just a multi-agent framework”  
- Just a QA tool, eval platform, or observability SaaS  
- An autonomous self-improving system  
- An AI FinOps / “Datadog for agents” product  

Pieces of those appear inside the harness. The objective is **controlled
delegation of software engineering to coding agents**.

---

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

Intended loop: **master prompt → scope cut → approve once → agents build**.
Details: `.claude/process.md`. Walkthrough: `docs/FIRST-PROJECT.md`. Vocabulary:
`docs/CONCEPTS.md`. Positioning: `docs/POSITIONING.md`. Evals: `docs/EVALS.md`.
Integrity: `docs/VALIDATION.md`.

---

## Current architecture (roles)

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

---

## The minimalism ladder

`implementer` walks a seven-rung checklist before writing code (full text:
`.claude/minimalism-ladder.md`). Lazy about the solution, never about reading.
Validation, error handling, security and accessibility are never cut.
`reviewer` treats a skipped simpler rung as a finding. Deliberate deferrals use
`SHORTCUT:`; `/harvest-debt` sweeps them into `TECH-DEBT.md`.

---

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

Tuneable numbers live only in `.claude/config.md`. Human-only: merge to
`master`, deletes outside scratch, `.claude/` edits, new dependencies, secrets,
and `PENDING_APPROVAL` → `APPROVED`.

---

## Loop mode, trust score, dry-run, calibration

**Loop mode.** `implementer → qa` with a rising bar each iteration. Caps:
`config.md`.

**Trust score.** Generated by `tooling/trust_score.py` from `memory/agent-log.md`
(agent reliability annotations — separate from task Evals).

**Dry-run.** `--dry-run` plans only; writes nothing.

**Calibration.** `/calibrate` proposes `config.md` edits from a real log
(`PENDING_APPROVAL`). `benchmarks/` is the method for Cato vs plain Claude Code;
results stay empty until a fair run exists.

**Evals / Feedback (v0.1).** Task evidence, human intervention logs, post-audits,
proposals that never auto-edit Cato. Frozen for the pilot — store proposals, do
not apply them. Details: `docs/EVALS.md`.

---

## Other agent hosts

`AGENTS.md` (+ synced Cursor / Cline / Copilot copies) carries phases and hard
rules without subagents. Claude Code gets the full subagent system today.

---

## Commands

| Command | What it does |
|---|---|
| `/init-project "<master prompt>"` | Bootstrap design, plan, specs, genesis ADR |
| `/init-project "..." --interview` | Interview gaps first |
| `/init-project "..." --dry-run` | Preview only |
| `/harvest-debt` | Collect `SHORTCUT:` into `TECH-DEBT.md` |
| `/calibrate` | Propose `config.md` edits from a real session log |

---

## Structure

```
CLAUDE.md                    # entrypoint (@-imports .claude/)
AGENTS.md                    # portable ruleset
docs/                        # POSITIONING, CONCEPTS, FIRST-PROJECT, EVALS, VALIDATION
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

---

## Testing & tooling

Product tests: fill `tests/README.md` (fast + full). `qa` reads it literally.
Framework tests: `python -m pytest tooling/ -c tooling/pytest.ini`.

```bash
python tooling/trust_score.py --write
python tooling/sync_rules.py
python tooling/evals.py metrics
python -m pytest tooling/ -c tooling/pytest.ini
```

---

## Versioning & adapting

`.framework-version` + `FRAMEWORK-CHANGELOG.md`. Upgrades are manual; never
overwrite project-owned `PLANNING.md`, `DESIGN.md`, `specs/`, `domain/`, `memory/`.

- Fill `claude-brand-style.md` before user-facing output.
- Fill `tests/README.md` before treating `qa: PASS` as meaningful.
- Map model tiers in `config.md` to your host’s aliases.
- Run `/calibrate` after real sessions.
- Add skills under `.claude/skills/` when a workflow repeats.

---

## Direction (hypothesis, not a result)

Long-term, CATO should help engineering orgs answer cost per task, human hours
saved, agent cost, defects prevented, escaped defects, rework, productivity, and
**safe delegation** ROI:

> How much software can an organization safely delegate to AI agents, and what is
> the real economic return?

That is a **direction**. CATO does **not** claim to have demonstrated this ROI yet.

---

## About the name

Cato the Censor reviewed, approved, and could veto — nothing moves without
someone authorised to stop it. Fitting for a control plane.

## License

MIT — see `LICENSE`.
