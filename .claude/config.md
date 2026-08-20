# Cato configuration

Every tuneable number in Cato lives here, and only here. Other files reference
this one rather than restating values, so there's a single place to change them
and no chance of two files disagreeing.

**These are starting guesses, not measurements.** Nothing here was derived from
data. `/calibrate` compares them against a real session's log and proposes
adjustments; `benchmarks/` documents how to test whether the framework earns its
overhead at all.

Editing this file is safe and expected. Editing `rules-hard.md` is not — that's
the separation: this file holds parameters, that one holds constraints.

## Agent budget per task

Maximum subagent invocations before the orchestrator stops and reports:

| Task size | Max invocations | Expected flow |
|---|---|---|
| Trivial | 2 | `implementer` → `qa` only |
| Medium | 5 | `strategist` → `architect` → `implementer` → `qa` → `reviewer` (drop or add `researcher`/`designer` as needed; if that would exceed 5, size large or ask to raise budget) |
| Large | 8 | full flow |

Task sizing: **trivial** is under one file with no business logic and is **never**
a new feature proposal; **medium** is anything else that isn't large; **large**
touches more than 3 modules or any infrastructure. New business / feature
prompts start at medium or large so `strategist` fits the budget.

Exceeding a budget requires explicit human approval.

## Retries

| Setting | Value |
|---|---|
| Max reinvocations of the same agent on the same task | 2 |

On the third, the orchestrator escalates to the human and parks the task under
`Blocked` in `PLANNING.md`. A repeated `BLOCKED` means information is missing that
only the human has — rephrasing and retrying won't produce it.

## Loop mode

| Setting | Value |
|---|---|
| Max `implementer → qa` iterations | 5 |
| Consecutive identical failures before early exit | 2 |

Two identical failures mean the problem is the spec or the design, not the
implementation. More iterations hide that rather than fixing it.

### Progressive validation thresholds

The bar `qa` applies rises with each iteration:

| Iteration | Threshold for PASS |
|---|---|
| 1 | Fast suite passes |
| 2 | Full suite passes + minimum coverage met |
| 3+ | The above, plus previously reported edge cases are covered |

## Testing

| Setting | Value |
|---|---|
| Minimum coverage, domain logic | 80% |
| Minimum coverage, glue code | none |

Glue code means adapters, configuration, and bootstrap scripts.

## Trust score

| Setting | Value |
|---|---|
| Minimum deliveries before a score is calculated | 5 |
| Score floor before an agent's prompt needs review | 70% |

Score = `(deliveries - reversals - avoidable_blocks) / deliveries`.

## Model selection per agent

| Work type | Model tier | Agents |
|---|---|---|
| Judgment | most capable | `strategist`, `architect`, `reviewer` |
| Structured | mid-tier | `implementer`, `researcher`, `designer` |
| Mechanical | fast/cheap | `qa`, `docs` |

Set the actual `model:` value in each `.claude/agents/*.md` to whatever your
install accepts. Don't pay for reasoning capacity where running a command and
reporting the result is all that's needed.
