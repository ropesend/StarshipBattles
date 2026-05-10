"""Per-audit run history tracker.

Each audit skill (ocode-*-audit) maintains a history of its runs in
``Reviews/results/<audit_name>_history.json``. After a run completes, the
skill calls :func:`add_run` with a structured summary. The next run reads
the previous entry via :func:`get_previous_run` and renders a trend
comparison section in the report.

Modeled on Tools/audit_shrink/shrink_tracker.py but generalized: each audit
maintains its own history file keyed by ``audit_name`` (e.g. "error",
"pattern", "state", "type", "docs", "testcoverage", "test", "shrink",
"legacy"). The schema is open — each audit decides which fields are
meaningful — but the runner enforces a minimal envelope (date, review_dir,
findings counts) so cross-audit dashboards are possible.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


HISTORY_FILENAME_TEMPLATE = "{audit_name}_history.json"


def _history_path(reviews_dir: str | Path, audit_name: str) -> Path:
    return Path(reviews_dir) / HISTORY_FILENAME_TEMPLATE.format(audit_name=audit_name)


def load(reviews_dir: str | Path, audit_name: str) -> dict[str, Any]:
    """Load the history file for an audit. Returns empty state if missing."""
    path = _history_path(reviews_dir, audit_name)
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"audit_name": audit_name, "runs": []}


def save(reviews_dir: str | Path, audit_name: str, data: dict[str, Any]) -> None:
    path = _history_path(reviews_dir, audit_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=False)


def add_run(
    reviews_dir: str | Path,
    audit_name: str,
    run_data: dict[str, Any],
) -> dict[str, Any]:
    """Append a run summary to the audit's history file.

    ``run_data`` should include at minimum:
      - ``date`` (str, ISO date)
      - ``review_dir`` (str, path to the run's directory)
      - ``findings`` (dict with at least ``critical``, ``major``, ``minor`` counts)

    Audit-specific fields (e.g. ``by_category``, ``by_layer``) are stored
    verbatim so the audit can render trend tables for its own categories.
    """
    history = load(reviews_dir, audit_name)
    history["runs"].append(run_data)
    save(reviews_dir, audit_name, history)
    return history


def get_previous_run(reviews_dir: str | Path, audit_name: str) -> dict[str, Any] | None:
    history = load(reviews_dir, audit_name)
    runs = history.get("runs", [])
    return runs[-1] if runs else None


def compute_trend(
    reviews_dir: str | Path,
    audit_name: str,
    current: dict[str, Any],
) -> dict[str, Any]:
    """Compare the current run to the previous one.

    Returns a structure like::

        {
          "direction": "improving" | "worsening" | "stable" | "first_run",
          "previous_date": "2026-04-12" | None,
          "deltas": {
            "critical": {"previous": 8, "current": 5, "change": -3},
            "major": {"previous": 22, "current": 24, "change": 2},
            ...
          },
          "by_category": {<category>: {"previous": N, "current": N, "change": N}, ...},
        }

    Direction is computed from the total weighted finding count
    (CRITICAL*10 + MAJOR*5 + MINOR*1). Lower = better.
    """
    previous = get_previous_run(reviews_dir, audit_name)
    if not previous:
        return {
            "direction": "first_run",
            "previous_date": None,
            "deltas": {},
            "by_category": {},
        }

    deltas: dict[str, dict[str, int]] = {}
    cur_findings = current.get("findings", {})
    prev_findings = previous.get("findings", {})
    for key in {"critical", "major", "minor", "advisory", "info"} | set(cur_findings) | set(prev_findings):
        prev_v = int(prev_findings.get(key, 0) or 0)
        cur_v = int(cur_findings.get(key, 0) or 0)
        if prev_v == 0 and cur_v == 0:
            continue
        deltas[key] = {"previous": prev_v, "current": cur_v, "change": cur_v - prev_v}

    by_category: dict[str, dict[str, int]] = {}
    cur_cat = current.get("by_category", {}) or {}
    prev_cat = previous.get("by_category", {}) or {}
    for key in set(cur_cat) | set(prev_cat):
        prev_v = int(prev_cat.get(key, 0) or 0)
        cur_v = int(cur_cat.get(key, 0) or 0)
        by_category[key] = {"previous": prev_v, "current": cur_v, "change": cur_v - prev_v}

    weights = {"critical": 10, "major": 5, "minor": 1, "advisory": 0.5, "info": 0.25}
    prev_score = sum(weights.get(k, 0) * int(prev_findings.get(k, 0) or 0) for k in weights)
    cur_score = sum(weights.get(k, 0) * int(cur_findings.get(k, 0) or 0) for k in weights)

    if cur_score < prev_score:
        direction = "improving"
    elif cur_score > prev_score:
        direction = "worsening"
    else:
        direction = "stable"

    return {
        "direction": direction,
        "previous_date": previous.get("date"),
        "deltas": deltas,
        "by_category": by_category,
    }


def render_trend_markdown(trend: dict[str, Any]) -> str:
    """Render a trend dict as a Markdown section for inclusion in audit reports."""
    if trend["direction"] == "first_run":
        return "## Trend Comparison\n\nFirst run for this audit — no trend data yet.\n"

    lines = [
        "## Trend Comparison",
        "",
        f"Compared to previous run ({trend['previous_date']}): **{trend['direction'].upper()}**",
        "",
        "| Severity | Previous | Current | Change |",
        "|----------|----------|---------|--------|",
    ]
    for sev in ["critical", "major", "minor", "advisory", "info"]:
        d = trend["deltas"].get(sev)
        if not d:
            continue
        change = d["change"]
        sign = "+" if change > 0 else ""
        lines.append(f"| {sev.title()} | {d['previous']} | {d['current']} | {sign}{change} |")

    if trend.get("by_category"):
        lines.extend(["", "### By Category", "", "| Category | Previous | Current | Change |", "|----------|----------|---------|--------|"])
        for cat, d in sorted(trend["by_category"].items()):
            change = d["change"]
            sign = "+" if change > 0 else ""
            lines.append(f"| {cat} | {d['previous']} | {d['current']} | {sign}{change} |")

    return "\n".join(lines) + "\n"
