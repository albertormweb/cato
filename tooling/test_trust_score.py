"""Tests for trust_score.py.

The trust score is only useful if it's derived from the log rather than from an
agent's self-report, so the parsing is worth testing.
"""

from trust_score import MIN_SAMPLE, parse


def test_counts_deliveries_per_agent():
    log = """
## 2026-01-01 10:00 — agent: qa
status: PASS
summary: green

## 2026-01-01 11:00 — agent: qa
status: PASS
summary: still green

## 2026-01-01 12:00 — agent: implementer
status: PASS
summary: shipped
"""
    tallies = parse(log)
    assert tallies["qa"].deliveries == 2
    assert tallies["implementer"].deliveries == 1


def test_distinguishes_avoidable_from_legitimate_blocks():
    log = """
## 2026-01-01 10:00 — agent: researcher
status: BLOCKED
summary: genuinely missing information only the human has

## 2026-01-01 11:00 — agent: implementer
status: BLOCKED
summary: avoidable, the answer was already in specs/0001
"""
    tallies = parse(log)
    assert tallies["researcher"].legitimate_blocks == 1
    assert tallies["researcher"].avoidable_blocks == 0
    assert tallies["implementer"].avoidable_blocks == 1
    assert tallies["implementer"].legitimate_blocks == 0


def test_counts_reversals():
    log = """
## 2026-01-01 10:00 — agent: qa
status: PASS
summary: reversed later by reviewer, coverage gap
"""
    assert parse(log)["qa"].reversals == 1


def test_score_needs_minimum_sample():
    log = "\n".join(
        f"## 2026-01-0{i} 10:00 — agent: qa\nstatus: PASS\nsummary: ok\n"
        for i in range(1, MIN_SAMPLE)
    )
    assert parse(log)["qa"].score is None


def test_score_penalises_reversals():
    entries = []
    for i in range(1, MIN_SAMPLE + 1):
        note = "reversed by reviewer" if i == 1 else "ok"
        entries.append(f"## 2026-01-0{i} 10:00 — agent: qa\nstatus: PASS\nsummary: {note}\n")
    tally = parse("\n".join(entries))["qa"]
    assert tally.deliveries == MIN_SAMPLE
    assert tally.reversals == 1
    assert tally.score < 100


def test_empty_log_yields_no_agents():
    assert parse("# Agent Log\n\nNothing yet.\n") == {}
