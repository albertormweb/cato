"""Tests for Evals v0.1 and Feedback Loop v0 (measurement instrument)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import evals as ev


@pytest.fixture
def eval_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    runs = tmp_path / "runs.jsonl"
    props = tmp_path / "proposals.jsonl"
    interventions = tmp_path / "interventions.jsonl"
    post_audits = tmp_path / "post-audits.jsonl"
    for p in (runs, props, interventions, post_audits):
        p.write_text("", encoding="utf-8")
    monkeypatch.setattr(ev, "RUNS_PATH", runs)
    monkeypatch.setattr(ev, "PROPOSALS_PATH", props)
    monkeypatch.setattr(ev, "INTERVENTIONS_PATH", interventions)
    monkeypatch.setattr(ev, "POST_AUDITS_PATH", post_audits)
    return {
        "runs": runs,
        "props": props,
        "interventions": interventions,
        "post_audits": post_audits,
    }


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
        "human_intervention_log": [
            {
                "timestamp": "2026-08-24T10:14:00+00:00",
                "type": "requirement_clarification",
                "duration_minutes": 4,
                "note": "Clarified cancelled contracts",
            }
        ],
        "manual_code_review_required": False,
        "accepted_without_manual_review": True,
        "regressions": 0,
        # escaped_defects omitted → null until post-audit
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
    recorded = ev.record_run(_sample_run())
    assert recorded["task_id"] == "DEV-142"
    lines = [
        ln
        for ln in eval_paths["runs"].read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
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
    assert run["human_minutes"] is None
    assert run["human_interventions"] is None
    assert run["escaped_defects"] is None
    assert run["accepted_without_manual_review"] is None
    assert run["manual_code_review_required"] is None
    report = ev.render_trust_report(run)
    assert "unknown" in report
    metrics = ev.compute_metrics([run], post_audits=[])
    assert metrics["delegation_rate"] is None
    assert metrics["safe_delegation_rate"] is None
    assert metrics["false_trust_rate"] is None
    assert metrics["tasks_recorded"] == 1


def test_cato_does_not_invent_human_fields_or_escaped_zero(eval_paths):
    run = ev.record_run({"task_id": "T-no-human", "result": "PASS", "findings": []})
    assert run["human_minutes"] is None
    assert run["human_interventions"] is None
    assert run["human_intervention_log"] is None
    assert run["manual_code_review_required"] is None
    assert run["accepted_without_manual_review"] is None
    assert run["escaped_defects"] is None
    report = ev.render_trust_report(run)
    assert "HUMAN SUPERVISION\nunknown" in report
    assert "ESCAPED DEFECTS\nunknown" in report


def test_human_minutes_derived_from_intervention_log(eval_paths):
    run = ev.record_run(
        {
            "task_id": "T-iv",
            "human_intervention_log": [
                {
                    "timestamp": "10:14",
                    "type": "requirement_clarification",
                    "duration_minutes": 2,
                    "note": "Clarified cancelled contracts",
                },
                {
                    "timestamp": "10:40",
                    "type": "blocker_answer",
                    "duration_minutes": 3,
                    "note": "Chose storage option",
                },
            ],
            "accepted_without_manual_review": True,
            "manual_code_review_required": False,
        }
    )
    assert run["human_minutes"] == 5
    assert run["human_interventions"] == 2


def test_intervention_cli_ledger_merges_into_run(eval_paths):
    ev.record_intervention(
        {
            "task_id": "T-ledger",
            "timestamp": "2026-08-24T10:14:00+00:00",
            "type": "requirement_clarification",
            "duration_minutes": 2,
            "note": "clarified",
        }
    )
    run = ev.record_run({"task_id": "T-ledger", "result": "PASS"})
    assert run["human_minutes"] == 2
    assert run["human_interventions"] == 1


def test_empty_intervention_log_is_known_zero_not_unknown(eval_paths):
    run = ev.record_run(
        {"task_id": "T-zero", "human_intervention_log": [], "result": "PASS"}
    )
    assert run["human_minutes"] == 0
    assert run["human_interventions"] == 0


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
            human_intervention_log=[
                {
                    "timestamp": "11:00",
                    "type": "manual_review",
                    "duration_minutes": 20,
                    "note": "full review",
                }
            ],
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
    m = ev.compute_metrics(ev._read_jsonl(eval_paths["runs"]), post_audits=[])
    assert m["tasks_recorded"] == 2
    assert m["delegation_rate"] == 0.5
    assert m["human_minutes_per_task"] == 12.0
    assert m["findings_total"] == 4
    assert m["cato_catch_rate"] == 0.75
    assert m["qa_reached"] == 2
    assert m["qa_rejection_rate"] == 0.5
    assert m["first_pass_rate"] == 0.5
    # No post-audits yet → safe/false trust unknown
    assert m["safe_delegation_rate"] is None
    assert m["false_trust_rate"] is None


def test_post_audit_clean_and_material_defect(eval_paths):
    ev.record_run(
        _sample_run(
            task_id="T-clean",
            accepted_without_manual_review=True,
            human_intervention_log=[
                {
                    "timestamp": "t",
                    "type": "accept",
                    "duration_minutes": 1,
                    "note": "trusted",
                }
            ],
        )
    )
    ev.record_run(
        _sample_run(
            task_id="T-bad",
            accepted_without_manual_review=True,
            human_intervention_log=[
                {
                    "timestamp": "t",
                    "type": "accept",
                    "duration_minutes": 1,
                    "note": "trusted",
                }
            ],
        )
    )
    ev.record_run(
        _sample_run(
            task_id="T-reviewed",
            accepted_without_manual_review=False,
            human_intervention_log=[
                {
                    "timestamp": "t",
                    "type": "review",
                    "duration_minutes": 30,
                    "note": "full",
                }
            ],
        )
    )
    # Unaudited delegated task must not count as CLEAN or in false trust.
    ev.record_run(
        _sample_run(
            task_id="T-pending-audit",
            accepted_without_manual_review=True,
            human_intervention_log=[
                {
                    "timestamp": "t",
                    "type": "accept",
                    "duration_minutes": 2,
                    "note": "trusted",
                }
            ],
        )
    )

    before_clean = ev.get_run("T-clean")["human_minutes"]
    audit_clean = ev.record_post_audit(
        {
            "task_id": "T-clean",
            "audit_result": "CLEAN",
            "material_defects": [],
            "notes": "spot-checked requirements",
        }
    )
    assert audit_clean["audit_result"] == "CLEAN"
    assert ev.get_run("T-clean")["human_minutes"] == before_clean
    assert ev.get_run("T-clean")["escaped_defects"] == 0

    ev.record_post_audit(
        {
            "task_id": "T-bad",
            "audit_result": "MATERIAL_DEFECT",
            "material_defects": ["wrong fee for cancelled contracts"],
            "notes": "spec unmet",
        }
    )
    assert ev.get_run("T-bad")["escaped_defects"] == 1

    # Non-delegated audit exists but must not enter safe/false trust denominators alone.
    ev.record_post_audit(
        {
            "task_id": "T-reviewed",
            "audit_result": "CLEAN",
            "material_defects": [],
        }
    )

    audits = ev._read_jsonl(eval_paths["post_audits"])
    m = ev.compute_metrics(ev._read_jsonl(eval_paths["runs"]), post_audits=audits)
    # Delegated with known decision: T-clean, T-bad, T-pending-audit, (+ sample none)
    # known_accept includes all four with bool + T-reviewed = 4 delegated decisions true/false
    assert m["delegation_rate"] == 0.75  # 3 of 4 accepted_without=true
    # Only T-clean and T-bad are delegated AND audited
    assert m["delegated_post_audit_sample_size"] == 2
    assert m["safe_delegation_rate"] == 0.5
    assert m["false_trust_rate"] == 0.5


def test_post_audit_does_not_increase_human_minutes(eval_paths):
    ev.record_run(
        {
            "task_id": "T-hm",
            "result": "PASS",
            "accepted_without_manual_review": True,
            "human_intervention_log": [
                {
                    "timestamp": "t",
                    "type": "accept",
                    "duration_minutes": 3,
                    "note": "go",
                }
            ],
        }
    )
    assert ev.get_run("T-hm")["human_minutes"] == 3
    ev.record_post_audit(
        {
            "task_id": "T-hm",
            "audit_result": "CLEAN",
            "material_defects": [],
            "notes": "spent 45 minutes auditing — must not land in human_minutes",
        }
    )
    assert ev.get_run("T-hm")["human_minutes"] == 3


def test_unaudited_not_counted_as_clean_or_false_trust(eval_paths):
    ev.record_run(
        {
            "task_id": "T-only",
            "accepted_without_manual_review": True,
            "human_intervention_log": [],
            "result": "PASS",
        }
    )
    m = ev.compute_metrics(ev._read_jsonl(eval_paths["runs"]), post_audits=[])
    assert m["safe_delegation_rate"] is None
    assert m["false_trust_rate"] is None
    assert m["delegated_post_audit_sample_size"] == 0


def test_proposal_persists_and_unapproved_does_not_modify_claude(
    eval_paths, tmp_path: Path
):
    props = eval_paths["props"]
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


def test_trust_report_contains_detector_breakdown_and_pass_semantics(eval_paths):
    ev.record_run(_sample_run())
    text = ev.render_trust_report(ev.get_run("DEV-142"))
    assert "CATO TRUST REPORT" in text
    assert "architect: 1" in text
    assert "tests: 1" in text
    assert "qa: 1" in text
    assert "Accepted without exhaustive human review: YES" in text
    assert "Internal Cato controls passed." in text
    assert "not proof of objective correctness" in text
    assert "independent post-audit evidence" in text
    assert "AI/task execution; not human supervision" in text
    assert "Post-audit time must not be included here." in text


def test_pass_semantics_constant():
    assert "not proof of objective correctness" in ev.PASS_SEMANTICS.lower() or (
        "not proof of objective correctness" in ev.PASS_SEMANTICS
    )
    assert "post-audit" in ev.PASS_SEMANTICS.lower()


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
    assert "objective correctness" in fb["what_failed"]


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


def test_human_owned_fields_documented():
    assert "human_minutes" in ev.HUMAN_OWNED_FIELDS
    assert "accepted_without_manual_review" in ev.HUMAN_OWNED_FIELDS
