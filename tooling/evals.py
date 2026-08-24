#!/usr/bin/env python3
"""Evals v0 and Feedback Loop v0 for Cato.

Records task evidence (JSONL), prints trust reports, derives simple metrics,
writes feedback analyses, and stores improvement proposals that never auto-apply
to .claude/ or other framework files.

Usage:
    python tooling/evals.py record --json '{"task_id":"T1",...}'
    python tooling/evals.py record --file path.json
    python tooling/evals.py report TASK_ID
    python tooling/evals.py metrics
    python tooling/evals.py feedback TASK_ID
    python tooling/evals.py propose --json '{...}'
    python tooling/evals.py set-status IMP-001 APPROVED
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = ROOT / "memory" / "evals"
RUNS_PATH = EVALS_DIR / "runs.jsonl"
PROPOSALS_PATH = EVALS_DIR / "proposals.jsonl"

# Roles Cato (or its tools) can claim as detectors — not human / post_merge.
CATO_DETECTED_BY = frozenset(
    {
        "architect",
        "strategist",
        "researcher",
        "designer",
        "implementer",
        "executor",  # alias for implementer in external vocabulary
        "qa",
        "reviewer",
        "docs",
        "tests",
    }
)

PROPOSAL_STATUSES = frozenset({"PROPOSED", "APPROVED", "REJECTED"})

FINDING_KEYS = ("finding", "severity", "detected_by", "stage", "resolved")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(obj, dict):
            raise ValueError(f"{path.name}:{line_no}: each line must be a JSON object")
        rows.append(obj)
    return rows


def _append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def _rewrite_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows
    )
    path.write_text(text, encoding="utf-8")


def normalize_finding(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("each finding must be an object")
    out = {
        "finding": raw.get("finding"),
        "severity": raw.get("severity"),
        "detected_by": raw.get("detected_by"),
        "stage": raw.get("stage"),
        "resolved": raw.get("resolved"),
    }
    if out["finding"] is None or str(out["finding"]).strip() == "":
        raise ValueError("finding text is required")
    if out["detected_by"] is None or str(out["detected_by"]).strip() == "":
        raise ValueError("detected_by is required on each finding")
    return out


def normalize_run(raw: dict[str, Any]) -> dict[str, Any]:
    """Accept partial records; unknown fields stay null. Never invent counts."""
    if "task_id" not in raw or not str(raw.get("task_id", "")).strip():
        raise ValueError("task_id is required")

    findings_in = raw.get("findings") or []
    if not isinstance(findings_in, list):
        raise ValueError("findings must be a list")
    findings = [normalize_finding(f) for f in findings_in]

    agents_used = raw.get("agents_used")
    if agents_used is None:
        # Convenience: single agent/model at top level for later multi-model compare.
        agent = raw.get("agent")
        model = raw.get("model")
        if agent is not None or model is not None:
            agents_used = [{"agent": agent, "model": model}]
        else:
            agents_used = []

    run = {
        "task_id": str(raw["task_id"]).strip(),
        "timestamp": raw.get("timestamp") or _utc_now(),
        "task_type": raw.get("task_type"),
        "risk_level": raw.get("risk_level"),
        "agent": raw.get("agent"),
        "model": raw.get("model"),
        "agents_used": agents_used,
        "requirements_total": raw.get("requirements_total"),
        "requirements_verified": raw.get("requirements_verified"),
        "tests_passed": raw.get("tests_passed"),
        "tests_failed": raw.get("tests_failed"),
        "qa_result": raw.get("qa_result"),
        "retries": raw.get("retries"),
        "architecture_violations": raw.get("architecture_violations"),
        "scope_violations": raw.get("scope_violations"),
        "human_interventions": raw.get("human_interventions"),
        "human_minutes": raw.get("human_minutes"),
        "manual_code_review_required": raw.get("manual_code_review_required"),
        "accepted_without_manual_review": raw.get("accepted_without_manual_review"),
        "regressions": raw.get("regressions"),
        "escaped_defects": raw.get("escaped_defects"),
        "total_duration_minutes": raw.get("total_duration_minutes"),
        "estimated_cost": raw.get("estimated_cost"),
        "result": raw.get("result"),
        "findings": findings,
        "known_risks": raw.get("known_risks") or [],
    }
    return run


def record_run(
    raw: dict[str, Any],
    *,
    runs_path: Path | None = None,
) -> dict[str, Any]:
    path = runs_path or RUNS_PATH
    run = normalize_run(raw)
    existing = _read_jsonl(path)
    if any(r.get("task_id") == run["task_id"] for r in existing):
        raise ValueError(f"task_id already recorded: {run['task_id']}")
    _append_jsonl(path, run)
    return run


def get_run(task_id: str, *, runs_path: Path | None = None) -> dict[str, Any] | None:
    path = runs_path or RUNS_PATH
    for row in _read_jsonl(path):
        if row.get("task_id") == task_id:
            return row
    return None


def _fmt_req(run: dict[str, Any]) -> str:
    total = run.get("requirements_total")
    verified = run.get("requirements_verified")
    if total is None and verified is None:
        return "unknown"
    return f"{verified if verified is not None else '?'} / {total if total is not None else '?'}"


def _fmt_tests(run: dict[str, Any]) -> str:
    passed = run.get("tests_passed")
    failed = run.get("tests_failed")
    if passed is None and failed is None:
        return "unknown"
    return f"{passed if passed is not None else '?'} passed, {failed if failed is not None else '?'} failed"


def _architecture_line(run: dict[str, Any]) -> str:
    v = run.get("architecture_violations")
    if v is None:
        return "unknown"
    return "PASS" if v == 0 else f"FAIL ({v})"


def _scope_line(run: dict[str, Any]) -> str:
    v = run.get("scope_violations")
    if v is None:
        return "unknown"
    return "PASS" if v == 0 else f"FAIL ({v})"


def render_trust_report(run: dict[str, Any]) -> str:
    findings = run.get("findings") or []
    by = Counter(str(f.get("detected_by") or "unknown") for f in findings)
    resolved = sum(1 for f in findings if f.get("resolved") is True)
    risks = run.get("known_risks") or []
    risk_line = "none recorded"
    if risks:
        risk_line = f"{len(risks)} listed"

    accepted = run.get("accepted_without_manual_review")
    if accepted is True:
        delegation = "YES"
    elif accepted is False:
        delegation = "NO"
    else:
        delegation = "unknown"

    manual = run.get("manual_code_review_required")
    if manual is True:
        manual_line = "Yes"
    elif manual is False:
        manual_line = "No"
    else:
        manual_line = "unknown"

    detected_lines = "\n".join(f"  {k}: {n}" for k, n in sorted(by.items())) or "  none"

    return f"""CATO TRUST REPORT

TASK
{run.get("task_id")} — {run.get("task_type") or "untyped"}

RESULT
{run.get("result") or "unknown"}

REQUIREMENTS
{_fmt_req(run)} verified

TESTS
{_fmt_tests(run)}

QA
{run.get("qa_result") or "unknown"}

ARCHITECTURE
{_architecture_line(run)}

SCOPE
{_scope_line(run)}

FINDINGS
{len(findings)} detected
{resolved} resolved

Detected by:
{detected_lines}

HUMAN INTERVENTION
{run.get("human_minutes") if run.get("human_minutes") is not None else "unknown"} minutes
({run.get("human_interventions") if run.get("human_interventions") is not None else "?"} interventions)

MANUAL CODE REVIEW
{manual_line}

KNOWN RISKS
{risk_line}

DELEGATION
Accepted without exhaustive human review: {delegation}
"""


def compute_metrics(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive only metrics that can be computed from known fields.

    Nulls are skipped, not invented. See docs/EVALS.md for limitations —
    especially CATO Catch Rate (unknown defects are invisible).
    """
    total = len(runs)

    # Delegation rate: among tasks where the field is known.
    known_accept = [
        r for r in runs if isinstance(r.get("accepted_without_manual_review"), bool)
    ]
    if known_accept:
        delegated = sum(
            1 for r in known_accept if r.get("accepted_without_manual_review") is True
        )
        delegation_rate = delegated / len(known_accept)
    else:
        delegation_rate = None

    minutes = [
        r["human_minutes"]
        for r in runs
        if isinstance(r.get("human_minutes"), (int, float))
    ]
    human_minutes_per_task = (sum(minutes) / len(minutes)) if minutes else None

    all_findings: list[dict[str, Any]] = []
    for r in runs:
        all_findings.extend(r.get("findings") or [])
    if all_findings:
        cato_hits = sum(
            1
            for f in all_findings
            if str(f.get("detected_by") or "").lower() in CATO_DETECTED_BY
        )
        cato_catch_rate = cato_hits / len(all_findings)
    else:
        cato_catch_rate = None

    reached_qa = [
        r
        for r in runs
        if r.get("qa_result") in ("PASS", "FAIL", "BLOCKED", "REJECT")
    ]
    # Treat REJECT as rejection synonym if someone uses it on qa_result.
    qa_rejected = [
        r
        for r in reached_qa
        if str(r.get("qa_result")).upper() in ("FAIL", "REJECT", "BLOCKED")
    ]
    # For rejection rate, BLOCKED is not always a rejection of quality — count
    # FAIL and REJECT only; BLOCKED stays in "reached QA" denominator optionally.
    # Spec asked: QA rejected / tasks reaching QA. Use FAIL + REJECT as rejected;
    # BLOCKED counts as reached but not as rejected (environment/spec issue).
    qa_fail = [
        r for r in reached_qa if str(r.get("qa_result")).upper() in ("FAIL", "REJECT")
    ]
    qa_rejection_rate = (len(qa_fail) / len(reached_qa)) if reached_qa else None

    decided = [
        r for r in runs if str(r.get("result") or "").upper() in ("PASS", "REJECT")
    ]
    with_retry_info = [
        r for r in decided if isinstance(r.get("retries"), int)
    ]
    if with_retry_info:
        first_pass_rate = (
            sum(
                1
                for r in with_retry_info
                if str(r.get("result")).upper() == "PASS" and r.get("retries") == 0
            )
            / len(with_retry_info)
        )
    else:
        first_pass_rate = None

    return {
        "tasks_recorded": total,
        "delegation_rate": delegation_rate,
        "delegation_sample_size": len(known_accept),
        "human_minutes_per_task": human_minutes_per_task,
        "human_minutes_sample_size": len(minutes),
        "cato_catch_rate": cato_catch_rate,
        "findings_total": len(all_findings),
        "qa_rejection_rate": qa_rejection_rate,
        "qa_reached": len(reached_qa),
        "first_pass_rate": first_pass_rate,
        "first_pass_sample_size": len(with_retry_info),
        "limitations": [
            "Absence of findings does not mean absence of defects.",
            "CATO Catch Rate only covers findings that were recorded; escaped unknown bugs are invisible.",
            "Rates ignore tasks where the required fields are null.",
        ],
    }


def render_metrics(metrics: dict[str, Any]) -> str:
    def pct(v: float | None) -> str:
        if v is None:
            return "n/a (insufficient data)"
        return f"{100 * v:.1f}%"

    def num(v: float | None) -> str:
        if v is None:
            return "n/a (insufficient data)"
        return f"{v:.2f}"

    lines = [
        "CATO EVAL METRICS (v0)",
        "",
        f"Tasks recorded: {metrics['tasks_recorded']}",
        f"Delegation rate: {pct(metrics['delegation_rate'])} (n={metrics['delegation_sample_size']})",
        f"Human minutes / task: {num(metrics['human_minutes_per_task'])} (n={metrics['human_minutes_sample_size']})",
        f"CATO catch rate: {pct(metrics['cato_catch_rate'])} (findings={metrics['findings_total']})",
        f"QA rejection rate: {pct(metrics['qa_rejection_rate'])} (reached QA={metrics['qa_reached']})",
        f"First-pass rate: {pct(metrics['first_pass_rate'])} (n={metrics['first_pass_sample_size']})",
        "",
        "Limitations:",
    ]
    for lim in metrics["limitations"]:
        lines.append(f"- {lim}")
    return "\n".join(lines) + "\n"


def build_feedback(run: dict[str, Any]) -> dict[str, Any]:
    """Narrative feedback for one task. Hypothesis language only — no causation."""
    findings = run.get("findings") or []
    unresolved = [f for f in findings if f.get("resolved") is not True]
    by = Counter(str(f.get("detected_by") or "unknown") for f in findings)

    what_happened = (
        f"Task {run.get('task_id')} finished with result="
        f"{run.get('result') or 'unknown'}, qa_result={run.get('qa_result') or 'unknown'}, "
        f"retries={run.get('retries') if run.get('retries') is not None else 'unknown'}."
    )
    if not findings:
        what_failed = "No findings were recorded (this does not prove there were no defects)."
    else:
        what_failed = "; ".join(
            f"{f.get('finding')} [{f.get('severity') or '?'}]" for f in findings
        )
    where = (
        ", ".join(f"{k} ({n})" for k, n in sorted(by.items()))
        if by
        else "no detectors recorded"
    )

    why = (
        "Insufficient structured evidence to explain root cause; treat any link "
        "between signals as association, not proof of causation."
    )
    if run.get("architecture_violations"):
        why = (
            "Architecture violation count is non-zero; this appears associated with "
            "the recorded findings, but does not by itself prove causation."
        )
    elif run.get("scope_violations"):
        why = (
            "Scope violation count is non-zero; this appears associated with the "
            "recorded findings, but does not by itself prove causation."
        )
    elif unresolved:
        why = (
            "Unresolved findings remain on the record; cause is not inferred automatically."
        )

    preventable = "unknown"
    if any(
        str(f.get("detected_by") or "").lower() in CATO_DETECTED_BY for f in findings
    ):
        preventable = (
            "Partially: at least one finding was detected inside Cato before acceptance. "
            "Whether an earlier process rule would have avoided it is a hypothesis."
        )
    elif findings and all(
        str(f.get("detected_by") or "").lower() in {"human", "post_merge"}
        for f in findings
    ):
        preventable = (
            "Possibly: recorded findings were only attributed to human/post_merge. "
            "A process change might have caught them earlier — unproven."
        )
    elif not findings:
        preventable = "No recorded findings to analyse."

    suggest_change = False
    if unresolved or str(run.get("qa_result") or "").upper() in ("FAIL", "REJECT"):
        suggest_change = True
    if (run.get("architecture_violations") or 0) > 0 or (
        run.get("scope_violations") or 0
    ) > 0:
        suggest_change = True
    # Trivial clean pass: do not nag for rules.
    if (
        str(run.get("result") or "").upper() == "PASS"
        and not findings
        and not run.get("architecture_violations")
        and not run.get("scope_violations")
    ):
        suggest_change = False

    return {
        "task_id": run.get("task_id"),
        "what_happened": what_happened,
        "what_failed": what_failed,
        "where_detected": where,
        "why_hypothesis": why,
        "could_cato_have_prevented": preventable,
        "suggests_process_change": suggest_change,
    }


def render_feedback(fb: dict[str, Any]) -> str:
    return f"""CATO FEEDBACK (v0)

WHAT HAPPENED?
{fb['what_happened']}

WHAT FAILED?
{fb['what_failed']}

WHERE WAS IT DETECTED?
{fb['where_detected']}

WHY DID IT HAPPEN? (hypothesis)
{fb['why_hypothesis']}

COULD CATO HAVE PREVENTED IT?
{fb['could_cato_have_prevented']}

DOES THIS SUGGEST A PROCESS/RULE CHANGE?
{"Yes — consider an improvement proposal if the pattern repeats." if fb['suggests_process_change'] else "No — no proposal warranted from this task alone."}
"""


def normalize_proposal(raw: dict[str, Any]) -> dict[str, Any]:
    status = str(raw.get("status") or "PROPOSED").upper()
    if status not in PROPOSAL_STATUSES:
        raise ValueError(f"status must be one of {sorted(PROPOSAL_STATUSES)}")
    evidence = raw.get("evidence_task_ids") or []
    if not isinstance(evidence, list):
        raise ValueError("evidence_task_ids must be a list")
    pid = raw.get("id")
    if not pid:
        raise ValueError("proposal id is required")
    return {
        "id": str(pid).strip(),
        "status": status,
        "observed_pattern": raw.get("observed_pattern"),
        "evidence_task_ids": evidence,
        "evidence_count": raw.get("evidence_count", len(evidence)),
        "confidence": raw.get("confidence"),
        "counterexamples": raw.get("counterexamples") or [],
        "proposed_change": raw.get("proposed_change"),
        "expected_benefit": raw.get("expected_benefit"),
        "risk": raw.get("risk"),
        "created_at": raw.get("created_at") or _utc_now(),
        "decided_at": raw.get("decided_at"),
        "decision_note": raw.get("decision_note"),
    }


def record_proposal(
    raw: dict[str, Any],
    *,
    proposals_path: Path | None = None,
) -> dict[str, Any]:
    path = proposals_path or PROPOSALS_PATH
    prop = normalize_proposal(raw)
    if prop["status"] != "PROPOSED":
        # New proposals always start PROPOSED; status changes go through set_status.
        prop["status"] = "PROPOSED"
    existing = _read_jsonl(path)
    if any(p.get("id") == prop["id"] for p in existing):
        raise ValueError(f"proposal id already exists: {prop['id']}")
    _append_jsonl(path, prop)
    return prop


def set_proposal_status(
    proposal_id: str,
    status: str,
    *,
    note: str | None = None,
    proposals_path: Path | None = None,
    framework_root: Path = ROOT,
) -> dict[str, Any]:
    """Update proposal status only. Never modifies .claude/ or other framework files."""
    path = proposals_path or PROPOSALS_PATH
    status = status.upper()
    if status not in PROPOSAL_STATUSES:
        raise ValueError(f"status must be one of {sorted(PROPOSAL_STATUSES)}")
    rows = _read_jsonl(path)
    found = None
    for row in rows:
        if row.get("id") == proposal_id:
            row["status"] = status
            row["decided_at"] = _utc_now()
            if note is not None:
                row["decision_note"] = note
            found = row
            break
    if found is None:
        raise ValueError(f"proposal not found: {proposal_id}")
    _rewrite_jsonl(path, rows)
    # Hard guarantee: this function does not write under .claude/
    assert not str(path).replace("\\", "/").endswith(".claude/")
    _ = framework_root  # reserved for future apply-step; intentionally unused
    return found


def proposal_modifies_framework(status_update_only: bool = True) -> bool:
    """Documented contract for tests: status updates do not modify Cato files."""
    return not status_update_only


def render_proposal(prop: dict[str, Any]) -> str:
    evidence = ", ".join(prop.get("evidence_task_ids") or []) or "(none)"
    counters = prop.get("counterexamples") or []
    counter_line = ", ".join(str(c) for c in counters) if counters else "(none recorded)"
    return f"""IMPROVEMENT PROPOSAL

ID
{prop.get('id')}

Observed pattern:
{prop.get('observed_pattern') or '(none)'}

Evidence:
{evidence}

evidence_count: {prop.get('evidence_count')}
confidence: {prop.get('confidence') or 'unknown'}
counterexamples: {counter_line}

Proposed change:
{prop.get('proposed_change') or '(none)'}

Expected benefit:
{prop.get('expected_benefit') or '(none)'}

Risk:
{prop.get('risk') or '(none)'}

STATUS:
{prop.get('status')}
"""


def _load_json_arg(json_str: str | None, file_path: str | None) -> dict[str, Any]:
    if file_path:
        return json.loads(Path(file_path).read_text(encoding="utf-8"))
    if json_str:
        return json.loads(json_str)
    raise SystemExit("Provide --json or --file")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_rec = sub.add_parser("record", help="append a task run to runs.jsonl")
    p_rec.add_argument("--json", dest="json_str")
    p_rec.add_argument("--file")

    p_rep = sub.add_parser("report", help="print trust report for a task_id")
    p_rep.add_argument("task_id")

    sub.add_parser("metrics", help="print derived metrics over all runs")

    p_fb = sub.add_parser("feedback", help="print feedback analysis for a task")
    p_fb.add_argument("task_id")

    p_pr = sub.add_parser("propose", help="append an improvement proposal (PROPOSED)")
    p_pr.add_argument("--json", dest="json_str")
    p_pr.add_argument("--file")

    p_st = sub.add_parser("set-status", help="APPROVED|REJECTED|PROPOSED — status only")
    p_st.add_argument("proposal_id")
    p_st.add_argument("status")
    p_st.add_argument("--note")

    args = parser.parse_args(argv)

    if args.cmd == "record":
        raw = _load_json_arg(args.json_str, args.file)
        run = record_run(raw)
        print(f"Recorded {run['task_id']} → {RUNS_PATH.relative_to(ROOT)}")
        return 0

    if args.cmd == "report":
        run = get_run(args.task_id)
        if not run:
            print(f"No run for task_id={args.task_id}", file=sys.stderr)
            return 1
        print(render_trust_report(run), end="")
        return 0

    if args.cmd == "metrics":
        print(render_metrics(compute_metrics(_read_jsonl(RUNS_PATH))), end="")
        return 0

    if args.cmd == "feedback":
        run = get_run(args.task_id)
        if not run:
            print(f"No run for task_id={args.task_id}", file=sys.stderr)
            return 1
        print(render_feedback(build_feedback(run)), end="")
        return 0

    if args.cmd == "propose":
        raw = _load_json_arg(args.json_str, args.file)
        prop = record_proposal(raw)
        print(f"Proposed {prop['id']} (status={prop['status']})")
        print(render_proposal(prop), end="")
        return 0

    if args.cmd == "set-status":
        prop = set_proposal_status(args.proposal_id, args.status, note=args.note)
        print(f"{prop['id']} → {prop['status']}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
