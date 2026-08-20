# Benchmarks

Cato claims that structured delegation produces better outcomes than a single
agent working unstructured. **That claim is currently untested.** This directory
holds the method for testing it, so the claim can either be backed or dropped.

Template integrity (not product outcomes) is reported in `docs/VALIDATION.md`.
Before dual-arm benchmarks, run one master-prompt product E2E and note where it
stalls — that closes the top item in `TECH-DEBT.md`.

No results are published here yet. When they are, they go in `results/` with the
raw data, not just a summary.

## Why this is empty

Publishing a framework with confident numbers nobody can reproduce is worse than
publishing one that says plainly it hasn't been measured. If you run this and the
numbers don't favour Cato, that's the more useful result — open an issue with it.

## What to measure

The honest comparison is the same real task, on the same real repository, with
and without Cato. Suggested metrics, in rough order of how much they matter:

| Metric | Why | How to capture |
|---|---|---|
| Correctness | A cheaper wrong answer is not an improvement | Task-specific acceptance tests, written before the run |
| Rework | Structure should reduce work thrown away | Lines added then deleted across the session |
| Over-building | The minimalism ladder's whole purpose | Diff size vs. a minimal reference solution |
| Token cost | Delegation adds overhead; does it pay for itself? | Provider usage reporting |
| Wall-clock time | Sequential agents are slower per task | Session duration |
| Human interventions | Fewer course-corrections is the real win | Count of times the human had to redirect |

Cato adds coordination overhead by design, so it should *lose* on raw token count
for trivial tasks and win on correctness and rework for non-trivial ones. If it
loses on both, the framework isn't earning its keep and should be simplified.

## Method

1. **Pick a real repository**, not a toy. Something with existing conventions the
   agent has to respect.
2. **Write acceptance tests first**, before either arm runs, so neither run can
   influence what counts as success.
3. **Define the task set**: at least 10 tickets spanning trivial, medium and
   large. Fewer than that and variance swamps the signal.
4. **Run both arms**: baseline (plain Claude Code, no Cato) and Cato, from the
   same starting commit, same model, same prompt text.
5. **Repeat.** n=1 tells you almost nothing. n=4 per task is a reasonable floor.
6. **Score the diff**, not the transcript. What landed in the repo is the outcome.

## Fairness traps

Worth naming, because they're easy to fall into and they inflate results:

- **Unfair baseline.** A bare model padding its answer with prose and options
  isn't a fair comparison for an agent doing real work. Compare agent to agent.
- **Cherry-picked tasks.** Tasks with an obvious over-building trap flatter the
  minimalism ladder. Include tasks where the correct solution is already minimal —
  the gain there should be near zero, and reporting that is what makes the rest
  credible.
- **Scoring what you optimised for.** If you only count lines of code, you'll
  reward deleting error handling. Correctness has to gate everything else.
- **Ignoring variance.** Report the spread, not just the mean.

## Reporting

Results go in `results/<YYYY-MM-DD>-<description>.md` and must include: model and
version, task list, n, both arms' raw numbers, the spread, and an explicit
limitations section. If a result is later shown to be unfair, correct the number
downward in place rather than quietly leaving it up.
