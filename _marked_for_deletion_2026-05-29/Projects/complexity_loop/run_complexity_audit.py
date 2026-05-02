#!/usr/bin/env python3
"""
Run radon cyclomatic complexity analysis and output structured JSON results.

Parses radon CC output for all functions above a given threshold,
sorted by complexity descending. Maintains a skip list of functions
that have been attempted and deemed irreducible.

Usage:
    python Projects/complexity_loop/run_complexity_audit.py
    python Projects/complexity_loop/run_complexity_audit.py --threshold 20
    python Projects/complexity_loop/run_complexity_audit.py --threshold 20 --top 1
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.parent
SKIP_LIST_FILE = WORKSPACE / "Projects" / "complexity_loop" / "skip_list.json"
HISTORY_FILE = WORKSPACE / "Projects" / "complexity_loop" / "complexity_history.jsonl"


def load_skip_list() -> dict:
    """Load the skip list of functions to ignore.

    Returns dict mapping "file:function" -> {reason, attempts, last_attempt, original_cc}.
    """
    if SKIP_LIST_FILE.exists():
        try:
            return json.loads(SKIP_LIST_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_skip_list(skip_list: dict):
    """Persist the skip list."""
    SKIP_LIST_FILE.parent.mkdir(parents=True, exist_ok=True)
    SKIP_LIST_FILE.write_text(
        json.dumps(skip_list, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def add_to_skip_list(file_path: str, function_name: str, reason: str, cc: int):
    """Add a function to the skip list."""
    skip_list = load_skip_list()
    key = f"{file_path}:{function_name}"
    entry = skip_list.get(key, {"attempts": 0, "original_cc": cc})
    entry["reason"] = reason
    entry["attempts"] = entry.get("attempts", 0) + 1
    entry["last_attempt"] = datetime.now().isoformat(timespec="seconds")
    entry["original_cc"] = entry.get("original_cc", cc)
    skip_list[key] = entry
    save_skip_list(skip_list)


def run_radon(threshold: int) -> list[dict]:
    """Run radon cc and parse output into structured results.

    Returns list of dicts sorted by complexity descending:
        [{file, function, line, cc, grade, class_name}, ...]
    """
    # Run radon with grade B+ (CC >= 6) to get broad data, then filter
    # Using -n B ensures we capture everything above trivial
    cmd = ["radon", "cc", "game/", "-s", "-n", "B", "-j"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE),
            timeout=120,
        )
    except FileNotFoundError:
        print("ERROR: radon not installed. Run: pip install radon", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("ERROR: radon timed out after 120 seconds", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0 and not result.stdout:
        print(f"ERROR: radon failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse radon JSON output", file=sys.stderr)
        print(f"stdout: {result.stdout[:500]}", file=sys.stderr)
        sys.exit(1)

    findings = []
    for file_path, blocks in data.items():
        for block in blocks:
            cc = block.get("complexity", 0)
            if cc < threshold:
                continue

            # Normalize path separators
            norm_path = file_path.replace("\\", "/")

            findings.append({
                "file": norm_path,
                "function": block.get("name", "unknown"),
                "line": block.get("lineno", 0),
                "end_line": block.get("endline", 0),
                "cc": cc,
                "grade": _cc_to_grade(cc),
                "class_name": block.get("classname", None),
                "type": block.get("type", "function"),
                "length": (block.get("endline", 0) - block.get("lineno", 0) + 1)
                if block.get("endline")
                else 0,
            })

    # Sort by complexity descending
    findings.sort(key=lambda x: x["cc"], reverse=True)
    return findings


def _cc_to_grade(cc: int) -> str:
    """Map cyclomatic complexity to radon grade."""
    if cc <= 5:
        return "A"
    elif cc <= 10:
        return "B"
    elif cc <= 15:
        return "C"
    elif cc <= 20:
        return "D"
    elif cc <= 30:
        return "E"
    else:
        return "F"


def filter_skipped(findings: list[dict], skip_list: dict) -> list[dict]:
    """Remove findings that are in the skip list."""
    filtered = []
    for f in findings:
        key = f"{f['file']}:{f['function']}"
        if key not in skip_list:
            filtered.append(f)
    return filtered


def compute_file_aggregate(findings: list[dict]) -> dict:
    """Compute per-file aggregate complexity stats.

    Returns dict mapping file -> {total_cc, max_cc, count, functions}.
    """
    by_file = {}
    for f in findings:
        fp = f["file"]
        if fp not in by_file:
            by_file[fp] = {"total_cc": 0, "max_cc": 0, "count": 0, "functions": []}
        by_file[fp]["total_cc"] += f["cc"]
        by_file[fp]["max_cc"] = max(by_file[fp]["max_cc"], f["cc"])
        by_file[fp]["count"] += 1
        by_file[fp]["functions"].append(f)
    return by_file


def select_target(findings: list[dict]) -> dict | None:
    """Select the best refactoring target.

    Strategy: pick the file with the highest single-function CC.
    Ties are broken by total file complexity.
    """
    if not findings:
        return None
    # The findings are already sorted by CC descending, so index 0 is worst
    return findings[0]


def append_history(findings: list[dict], threshold: int):
    """Append a snapshot to the history JSONL file for trend tracking."""
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "threshold": threshold,
        "total_above_threshold": len(findings),
        "worst_cc": findings[0]["cc"] if findings else 0,
        "worst_function": f"{findings[0]['file']}:{findings[0]['function']}"
        if findings
        else None,
        "distribution": {
            "extreme_40plus": sum(1 for f in findings if f["cc"] >= 40),
            "very_high_30_39": sum(1 for f in findings if 30 <= f["cc"] < 40),
            "high_20_29": sum(1 for f in findings if 20 <= f["cc"] < 29),
            "elevated_15_19": sum(1 for f in findings if 15 <= f["cc"] < 20),
        },
    }

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Run complexity audit and output structured results"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=20,
        help="Minimum CC to include (default: 20)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        help="Only output top N results (default: all)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of human-readable summary",
    )
    parser.add_argument(
        "--include-skipped",
        action="store_true",
        help="Include functions on the skip list",
    )
    args = parser.parse_args()

    # Run audit
    all_findings = run_radon(args.threshold)

    # Filter skip list
    skip_list = load_skip_list()
    if not args.include_skipped:
        findings = filter_skipped(all_findings, skip_list)
    else:
        findings = all_findings

    skipped_count = len(all_findings) - len(findings)

    # Limit results
    if args.top > 0:
        findings = findings[: args.top]

    # Append history
    append_history(all_findings, args.threshold)

    # Output
    if args.json:
        output = {
            "threshold": args.threshold,
            "total_above_threshold": len(all_findings),
            "skipped": skipped_count,
            "results": findings,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"Complexity Audit (CC >= {args.threshold})")
        print(f"  Total functions above threshold: {len(all_findings)}")
        print(f"  Skipped (in skip list): {skipped_count}")
        print(f"  Actionable: {len(findings)}")
        print()

        if findings:
            target = findings[0]
            print(f"  WORST: {target['file']}:{target['line']} "
                  f"{target['function']} (CC={target['cc']}, grade={target['grade']})")
            print()

            # Tier breakdown
            for tier_name, lo, hi in [
                ("Extreme (CC >= 40)", 40, 999),
                ("Very High (CC 30-39)", 30, 39),
                ("High (CC 20-29)", 20, 29),
                ("Elevated (CC 15-19)", 15, 19),
            ]:
                tier = [f for f in findings if lo <= f["cc"] <= hi]
                if tier:
                    print(f"  {tier_name}: {len(tier)} functions")
                    for f in tier[:5]:
                        cn = f"{f['class_name']}." if f["class_name"] else ""
                        print(f"    CC={f['cc']:3d}  {f['file']}:{f['line']}  {cn}{f['function']}")
                    if len(tier) > 5:
                        print(f"    ... and {len(tier) - 5} more")
                    print()

        if skip_list:
            print(f"  Skip list: {len(skip_list)} functions excluded")

    return 0


if __name__ == "__main__":
    sys.exit(main())
