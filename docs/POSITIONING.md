# Positioning — CATO and Harness Engineering

Conceptual map of what CATO is aiming at. This is **not** a claim that every
capability below is fully implemented or proven. For maturity labels, see the
tables in `README.md` and the honesty notes in `docs/VALIDATION.md` /
`docs/EVALS.md`.

## Discipline: Harness Engineering

> Harness Engineering is the discipline of designing the system around an AI
> model so it can operate with greater autonomy inside a controlled, verifiable,
> and traceable engineering process.

CATO applies that discipline to **AI software engineering** with coding agents.

## Category: AI Software Engineering Control Plane

Short definition:

> **CATO is the control layer for AI software engineering.**

Value proposition:

> **CATO allows engineering teams to delegate more software development to coding
> agents without losing control of quality, architecture, safety, and
> traceability.**

CATO is **not** primarily: a multi-agent framework, a Claude Code wrapper, an
agent team, a QA tool, an eval platform, an observability platform, or a coding
assistant. Those may appear as *mechanisms inside* the control plane.

## Thesis

> **The model is the worker. The harness is the engineering system around it.**

| | |
|---|---|
| **Model** | Worker that writes and edits software |
| **Harness** | Roles, process, architecture, controls, verification, permissions, memory, traceability, measurement, continuous improvement |

CATO is **not** primarily trying to build an AI that writes better code. It aims
to build the engineering system that lets organizations **delegate more** work to
agents that already can write code.

**Agent capability ≠ delegation confidence.**

## Hotel / construction analogy

| Concept | Analogy |
|---|---|
| Prompt | “Paint this room.” |
| Skill | The painter’s manual |
| Spec | Construction specification (what, what not, done) |
| CATO / harness | The company running the project: PM, inspection, architecture, planning, specialists, permissions, controls, records, improvement |

> The goal is not just to hire a better painter. The goal is to build a company
> capable of managing 100 rooms without the owner personally inspecting every one.

## Prompt ≠ control

| Skill / instruction | Control |
|---|---|
| “Do not remove structural walls.” | Worker lacks permission to remove them |
| “Review your work before finishing.” | The actor who did the work cannot approve it |
| “Respect the architecture.” | A quality gate fails on architectural violations |

> **Instructions influence behavior. Controls constrain what can happen.**

Many CATO gates are still **instruction-level** today (the model must obey). Some
are mechanical (tool allowlists, CI). See `docs/VALIDATION.md`.

## Four layers

1. **DEFINE** — What are we building? (prompt, skills, specs, strategist)
2. **PRODUCE** — How are we building it? (research, architect, planning, orchestrator, implementer, handoffs)
3. **CONTROL** — Can we trust the process and result? (tests, QA, reviewer, guardrails, permissions, memory, logs, CI)
4. **IMPROVE** — How do we make the next run better? (observe → evaluate → patterns → proposal → **human** approval → benchmark)

IMPROVE must not be read as autonomous self-learning. Feedback proposals in this
repo require human approval and **do not** auto-edit `.claude/` or prompts.

## Silent agent failures

Technically successful ≠ semantically correct.

Examples of the failure mode CATO is designed to reduce (not claim to fully
detect automatically today):

- Processes a reservation but applies the wrong price  
- Sends an email successfully to the wrong customer  
- Updates a database successfully under the wrong business rule  

Specs, tests, QA, independent review, post-audits, and evals exist to catch
**semantic** failure — not merely “the tool call returned OK.”

## Safe Delegation

| Term | Meaning |
|---|---|
| **Delegation** | Accepted without exhaustive manual review |
| **Safe Delegation** | Delegated **and** later independent post-audit found no material defect |
| **False Trust** | Delegated, later post-audit found a material defect |

Feeling confident ≠ evidence that confidence was justified. Instrumentation:
`docs/EVALS.md` (experimental).

## CATO PASS

Means only: **internal CATO controls passed.**

Does **not** mean objectively correct, bug-free, safely delegated, or that
post-audit is unnecessary.

## Evals and “observability”

Observability here means **engineering evidence** for the question:

> Can this software engineering work safely be delegated?

It is **not** “Datadog for agents,” and this repo does not ship a complete
enterprise agent-observability platform. Evals v0.1 record task runs, human
supervision, post-audits, and derived rates — see `docs/EVALS.md` for what
actually exists.

## Feedback Loop principle

> Do not improve CATO because an improvement sounds reasonable. Improve CATO when
> evidence shows a recurring problem.

```
RUN → OBSERVE → EVAL → ROOT CAUSE → PROPOSAL → HUMAN APPROVAL → (optional) CATO vNEXT → BENCHMARK
```

Approved proposals are **not** applied automatically. The first experimental
baseline stays frozen while proposals are stored only.

## Execution environment

**Today:** Claude Code is the primary host (full subagent system).

**Conceptually:** CATO → coding agents (Claude Code, and potentially others such
as Codex or future agents). Portable hosts get `AGENTS.md` rules without claiming
feature parity.

Do not read “currently Claude Code” as “CATO is Claude forever.”

## What we are testing

> Can CATO increase the percentage of software development delegated to coding
> agents while reducing human supervision without significantly increasing
> defects, regressions, or false trust?

Until measured: speak in **aims to** / **is testing whether**, not **enables** /
**demonstrates**.

## Business direction (not a result)

Eventually CATO should help answer cost per task, hours saved, agent cost,
defects prevented, escaped defects, rework, productivity, and safe-delegation ROI:

> How much software can an engineering organization safely delegate to AI agents,
> and what is the real economic return?

**Hypothesis and direction — not a demonstrated outcome.**

## What CATO is not

- Another coding model  
- A Claude Code replacement  
- Just prompts or just skills  
- Just a multi-agent framework  
- Just a QA tool  
- An autonomous self-improving system  
- An observability SaaS  
- An AI FinOps platform  

Higher-level objective: **controlled delegation of software engineering to AI
agents.**
