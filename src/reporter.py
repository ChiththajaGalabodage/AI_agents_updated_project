import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_pytest_counts(output: str) -> dict[str, int]:
    def extract(pattern: str) -> int:
        match = re.search(pattern, output, flags=re.IGNORECASE)
        return int(match.group(1)) if match else 0

    passed = extract(r"(\d+)\s+passed")
    failed = extract(r"(\d+)\s+failed")
    errors = extract(r"(\d+)\s+errors?")
    skipped = extract(r"(\d+)\s+skipped")
    xfailed = extract(r"(\d+)\s+xfailed")
    xpassed = extract(r"(\d+)\s+xpassed")
    total = passed + failed + errors + skipped + xfailed + xpassed
    return {
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "xfailed": xfailed,
        "xpassed": xpassed,
        "total": total,
    }


def build_report(
    analysis: dict[str, Any],
    test_run: dict[str, Any],
    heal_attempts: int,
    test_file: str,
    pipeline_events: list[dict[str, Any]] | None = None,
    predictive_selection: dict[str, Any] | None = None,
    heal_history: list[dict[str, Any]] | None = None,
    generation_explanation: list[str] | None = None,
) -> dict[str, Any]:
    """Build a JSON-serializable pipeline report."""
    events = pipeline_events or []

    def _parse_iso(ts: str | None):
        if not ts:
            return None
        try:
            return datetime.fromisoformat(ts)
        except Exception:
            return None

    # Compute per-stage durations from the recorded events
    durations: dict[str, float] = {}
    by_stage: dict[str, list[dict[str, Any]]] = {}
    for ev in events:
        stage = ev.get("stage")
        by_stage.setdefault(stage, []).append(ev)

    for stage, evs in by_stage.items():
        # find earliest 'running' timestamp and latest 'completed' timestamp
        start_ts = None
        end_ts = None
        for e in evs:
            if e.get("status") == "running":
                start_ts = _parse_iso(e.get("timestamp_utc")) or start_ts
            if e.get("status") in ("completed", "finished", "passed", "failed"):
                end_ts_candidate = _parse_iso(e.get("timestamp_utc"))
                if end_ts_candidate:
                    if end_ts is None or end_ts_candidate > end_ts:
                        end_ts = end_ts_candidate

        if start_ts and end_ts:
            durations[stage] = round((end_ts - start_ts).total_seconds(), 3)

    # total pipeline duration (best-effort from events)
    total_duration = None
    if events:
        first = _parse_iso(events[0].get("timestamp_utc"))
        last = _parse_iso(events[-1].get("timestamp_utc"))
        if first and last:
            total_duration = round((last - first).total_seconds(), 3)

    selection = predictive_selection or {
        "enabled": False,
        "changed_files": [],
        "selected_tests": [],
    }
    selected_tests = selection.get("selected_tests", []) if isinstance(selection, dict) else []
    if not isinstance(selected_tests, list):
        selected_tests = []
    test_counts = parse_pytest_counts(str(test_run.get("output", "")))
    defects_detected = test_counts["failed"] + test_counts["errors"]
    execution_time = float(test_run.get("duration_seconds", 0.0) or 0.0)
    execution_efficiency = round(test_counts["total"] / execution_time, 3) if execution_time > 0 else 0.0

    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "analysis": analysis,
        "test_file": test_file,
        "heal_attempts": heal_attempts,
        "test_run": test_run,
        "pipeline_events": events,
        "predictive_selection": selection,
        "heal_history": heal_history or [],
        "generation_explanation": generation_explanation or [],
        "metrics": {
            "functions": analysis.get("function_count", 0),
            "classes": analysis.get("class_count", 0),
            "passed": bool(test_run.get("passed", False)),
            "test_counts": test_counts,
            "defects_detected": defects_detected,
            "test_execution_time_seconds": execution_time,
            "execution_efficiency_tests_per_second": execution_efficiency,
            "selected_tests_count": len(selected_tests),
            "durations_seconds": durations,
        },
    }

    if total_duration is not None:
        report["metrics"]["pipeline_total_seconds"] = total_duration

    return report


def write_report(report: dict[str, Any], output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
