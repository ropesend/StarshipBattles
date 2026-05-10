import json
import os
from datetime import datetime


def load(reviews_dir):
    """Load the shrink tracker from disk. Returns empty state if missing."""
    tracker_path = os.path.join(reviews_dir, "shrink_tracker.json")
    try:
        with open(tracker_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"runs": []}


def save(reviews_dir, data):
    tracker_path = os.path.join(reviews_dir, "shrink_tracker.json")
    with open(tracker_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_run(reviews_dir, run_data):
    tracker = load(reviews_dir)
    tracker["runs"].append(run_data)
    save(reviews_dir, tracker)
    return tracker


def get_previous_run(reviews_dir):
    tracker = load(reviews_dir)
    runs = tracker.get("runs", [])
    return runs[-1] if runs else None


def compute_trend(reviews_dir, current):
    previous = get_previous_run(reviews_dir)
    if not previous:
        return {"direction": "first_run", "delta": {}, "previous_date": None}

    delta = {}
    for key in ["production_loc", "dead_code_files", "dead_code_functions",
                "dead_code_imports", "duplication_clusters"]:
        prev_val = previous.get(key, 0)
        curr_val = current.get(key, 0)
        if isinstance(prev_val, (int, float)) and isinstance(curr_val, (int, float)):
            delta[key] = {"previous": prev_val, "current": curr_val, "change": curr_val - prev_val}

    total_shrink = sum(v.get("estimated_shrinkable_loc", 0) for v in [previous, current])
    if previous.get("estimated_shrinkable_loc", 0) > current.get("estimated_shrinkable_loc", 0):
        direction = "improving"
    elif previous.get("estimated_shrinkable_loc", 0) < current.get("estimated_shrinkable_loc", 0):
        direction = "worsening"
    else:
        direction = "stable"

    return {
        "direction": direction,
        "delta": delta,
        "previous_date": previous.get("date"),
    }


def generate_comparison_text(trend):
    if trend["direction"] == "first_run":
        return "First run — no trend data available."

    lines = [f"Trend direction: **{trend['direction'].upper()}**"]
    lines.append(f"Compared to previous run ({trend['previous_date']}):")

    for key, d in trend["delta"].items():
        label = key.replace("_", " ").title()
        direction = "+" if d["change"] > 0 else ""
        lines.append(f"  {label}: {d['previous']} -> {d['current']} ({direction}{d['change']})")

    return "\n".join(lines)
