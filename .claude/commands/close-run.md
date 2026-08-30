---
description: Closes a run. Dumps objective metrics to memory/evals/, scaffolds the human observation notes, and updates the run index. Never writes the judgment sections.
---

Close the current run and leave the observation record ready for the human.

## 1. Objective metrics → `memory/evals/runs.jsonl`

Read `memory/agent-log.md` for this run and append one JSON line with, per agent:
invocations, PASS returned, PASS reversed by `reviewer`, BLOCKED (and whether the
block was legitimate), `implementer → qa` rounds, commits produced, and duration
if available.

**Only facts verifiable from the log.** Never a quality judgment, never a
narrative summary of how the run went.

Append any human intervention you can identify from the transcript to
`memory/evals/interventions.jsonl` — what was asked, at which gate. Not whether
it was justified.

## 2. Scaffold `memory/run-NN-notes.md`

Create the next run's notes file with the objective data already filled in
(dates, spec, branch, starting and ending state, config changes, commits) and
these sections **empty**, waiting for the human:

- Interventions
- Contained impulses
- Review time and confidence
- Escaped defects
- Framework findings
- Conclusion

## 3. Update `memory/runs.md`

Append one line: date · spec · duration · escaped defects · main finding.
Create the file with a header row if it does not exist.

## Hard constraint

`/close-run` **never writes the judgment sections**, never summarises findings,
and never assesses whether the run went well. Those sections exist precisely
because the system cannot evaluate itself: `trust_score.py` already depends on
agents labelling their own reversals honestly, and that is as far as
self-assessment can be trusted.

An agent whose PASS verdicts were later reversed would not write "my PASS
verdicts were reversed".

If asked to fill those sections, refuse and explain why.
