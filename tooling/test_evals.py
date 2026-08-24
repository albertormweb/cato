"""Tests for Evals v0 and Feedback Loop v0."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import evals as ev


@pytest.fixture
def eval_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    runs = tmp_path / "runs.jsonl"
    props = tmp_path / "proposals.jsonl"
    runs.write_text("", encoding="utf-8")
    props.write_text("", encoding="utf-8")
    monkeypatch.setattr(ev, "RUNS_PATH", runs)
    monkeypatch.setattr(ev, "PROPOSALS_PATH", props)
    return runs, props


def _sample_run(**overrides):
    base = {
        "task_id": "DEV-142",
        "task_type": "feature",
        "risk_level": "medium",
        "agent": "implementer",
        "model": "sonnet",
        "requirements_total": 8,
        "requirements_verified": 8,
        "tests_passed": 142,
        "tests_failed": 0,
        "qa_result": "PASS",
        "retries": 0,
        "architecture_violations": 0,
        "scope_violations": 0,
        "human_interventions": 1,
        "human_minutes": 4,
        "manual_code_review_required": False,
        "accepted_without_manual_review": True,
        "regressions": 0,
        "escaped_defects": 0,
        "total_duration_minutes": 40,
        "estimated_cost": None,
        "result": "PASS",
        "findings": [
            {
                "finding": "missing edge case in return fee",
                "severity": "medium",
                "detected_by": "architect",
                "stage": "design",
                "resolved": True,
            },
            {
                "finding": "flaky assertion",
                "severity": "low",
                "detected_by": "tests",
                "stage": "tests",
                "resolved": True,
            },
            {
                "finding": "unclear error message",
                "severity": "low",
                "detected_by": "qa",
                "stage": "qa",
                "resolved": True,
            },
        ],
        "known_risks": ["low: fee rounding in other currencies"],
    }
    base.update(overrides)
    return base


def test_record_run_persists_and_keeps_detected_by(eval_paths):
    runs, _ = eval_paths
    recorded = ev.record_run(_sample_run())
    assert recorded["task_id"] == "DEV-142"
    lines = [ln for ln in runs.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1
    loaded = json.loads(lines[0])
    assert [f["detected_by"] for f in loaded["findings"]] == [
        "architect",
        "tests",
        "qa",
    ]


def test_incomplete_run_does_not_break(eval_paths):
    ev.record_run({"task_id": "T-sparse", "findings": []})
    run = ev.get_run("T-sparse")
    assert run is not None
    assert run["tests_passed"] is None
    report = ev.render_trust_report(run)
    assert "unknown" in report
    metrics = ev.compute_metrics([run])
    assert metrics["delegation_rate"] is None
    assert metrics["tasks_recorded"] == 1


def test_duplicate_task_id_rejected(eval_paths):
    ev.record_run(_sample_run())
    with pytest.raises(ValueError, match="already recorded"):
        ev.record_run(_sample_run())


def test_finding_requires_detected_by(eval_paths):
    with pytest.raises(ValueError, match="detected_by"):
        ev.record_run(
            {
                "task_id": "T-bad",
                "findings": [{"finding": "x", "severity": "low", "stage": "qa"}],
            }
        )


def test_metrics_calculations(eval_paths):
    ev.record_run(_sample_run())
    ev.record_run(
        _sample_run(
            task_id="DEV-143",
            accepted_without_manual_review=False,
            human_minutes=20,
            qa_result="FAIL",
            result="REJECT",
            retries=2,
            findings=[
                {
                    "finding": "bug escaped to human",
                    "severity": "high",
                    "detected_by": "human",
                    "stage": "review",
                    "resolved": True,
                }
            ],
        )
    )
    m = ev.compute_metrics(ev._read_jsonl(eval_paths[0]))
    assert m["tasks_recorded"] == 2
    assert m["delegation_rate"] == 0.5
    assert m["human_minutes_per_task"] == 12.0
    # 3 Cato findings + 1 human = 4; catch rate 3/4
    assert m["findings_total"] == 4
    assert m["cato_catch_rate"] == 0.75
    assert m["qa_reached"] == 2
    assert m["qa_rejection_rate"] == 0.5
    assert m["first_pass_rate"] == 0.5


def test_proposal_persists_and_unapproved_does_not_modify_claude(
    eval_paths, tmp_path: Path
):
    _, props = eval_paths
    claude = tmp_path / ".claude"
    claude.mkdir()
    marker = claude / "rules-hard.md"
    before = "do not touch\n"
    marker.write_text(before, encoding="utf-8")

    prop = ev.record_proposal(
        {
            "id": "IMP-001",
            "observed_pattern": "billing + contracts without reading contracts.md",
            "evidence_task_ids": ["TASK-32", "TASK-41", "TASK-48"],
            "evidence_count": 3,
            "confidence": "MEDIUM",
            "counterexamples": ["TASK-50"],
            "proposed_change": "Require contracts.md when billing+contracts touched",
            "expected_benefit": "Fewer architecture/requirement errors",
            "risk": "Extra context overhead",
        }
    )
    assert prop["status"] == "PROPOSED"
    assert props.read_text(encoding="utf-8").strip()

    updated = ev.set_proposal_status(
        "IMP-001",
        "APPROVED",
        note="ok to apply manually later",
        proposals_path=props,
        framework_root=tmp_path,
    )
    assert updated["status"] == "APPROVED"
    assert marker.read_text(encoding="utf-8") == before
    assert ev.proposal_modifies_framework(status_update_only=True) is False


def test_rejected_proposal_also_leaves_framework_alone(eval_paths, tmp_path: Path):
    claude_file = tmp_path / ".claude" / "config.md"
    claude_file.parent.mkdir()
    claude_file.write_text("70%\n", encoding="utf-8")
    ev.record_proposal(
        {
            "id": "IMP-002",
            "observed_pattern": "noise",
            "evidence_task_ids": ["T1"],
            "proposed_change": "change config",
        }
    )
    ev.set_proposal_status("IMP-002", "REJECTED", framework_root=tmp_path)
    assert claude_file.read_text(encoding="utf-8") == "70%\n"


def test_trust_report_contains_detector_breakdown(eval_paths):
    ev.record_run(_sample_run())
    text = ev.render_trust_report(ev.get_run("DEV-142"))
    assert "CATO TRUST REPORT" in text
    assert "architect: 1" in text
    assert "tests: 1" in text
    assert "qa: 1" in text
    assert "Accepted without exhaustive human review: YES" in text


def test_feedback_clean_pass_does_not_suggest_change(eval_paths):
    ev.record_run(
        {
            "task_id": "T-clean",
            "result": "PASS",
            "qa_result": "PASS",
            "findings": [],
            "architecture_violations": 0,
            "scope_violations": 0,
        }
    )
    fb = ev.build_feedback(ev.get_run("T-clean"))
    assert fb["suggests_process_change"] is False


def test_feedback_qa_fail_suggests_change(eval_paths):
    ev.record_run(
        {
            "task_id": "T-fail",
            "result": "REJECT",
            "qa_result": "FAIL",
            "findings": [
                {
                    "finding": "regression",
                    "severity": "high",
                    "detected_by": "qa",
                    "stage": "qa",
                    "resolved": False,
                }
            ],
        }
    )
    fb = ev.build_feedback(ev.get_run("T-fail"))
    assert fb["suggests_process_change"] is True
    assert "hypothesis" in fb["why_hypothesis"].lower() or "not" in fb["why_hypothesis"].lower()
