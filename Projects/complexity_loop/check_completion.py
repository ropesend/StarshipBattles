#!/usr/bin/env python3
"""
Check if all tasks in a cycle_plan.md are complete.
Returns exit code 0 if all complete, 1 if incomplete tasks remain.

Usage:
    python Projects/complexity_loop/check_completion.py
    python Projects/complexity_loop/check_completion.py --plan-file path/to/plan.md
"""

import argparse
import re
import sys
from pathlib import Path

DEFAULT_PLAN = (
    Path(__file__).parent.parent.parent
    / "Projects"
    / "complexity_loop"
    / "cycle_plan.md"
)


def check_completion(plan_file: Path) -> bool:
    """Check if all tasks in the plan file are complete.

    Returns True if all tasks complete, False otherwise.
    """
    if not plan_file.exists():
        print(f"Error: Plan file not found: {plan_file}", file=sys.stderr)
        sys.exit(2)

    content = plan_file.read_text(encoding="utf-8")

    # Extract Master Task List section
    task_list_match = re.search(
        r"## Master Task List\s*\n(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL,
    )

    if not task_list_match:
        print("Error: Could not find Master Task List section", file=sys.stderr)
        sys.exit(2)

    task_list_section = task_list_match.group(1)

    # Find all project checkboxes: - [x] **PROJ-...
    checkbox_pattern = r"^- \[([xX~/ ])\]\s+\*\*PROJ-\d+:"
    checkboxes = re.findall(checkbox_pattern, task_list_section, re.MULTILINE)

    if not checkboxes:
        print("Warning: No project tasks found in Master Task List", file=sys.stderr)
        return True

    total = len(checkboxes)
    completed = sum(1 for s in checkboxes if s.lower() == "x")
    skipped = sum(1 for s in checkboxes if s == "~")
    in_progress = sum(1 for s in checkboxes if s == "/")
    not_started = sum(1 for s in checkboxes if s == " ")

    print(f"Project Status:")
    print(f"  Total: {total}")
    print(f"  Completed: {completed} [x]")
    print(f"  Skipped: {skipped} [~]")
    print(f"  In Progress: {in_progress} [/]")
    print(f"  Not Started: {not_started} [ ]")

    if not_started > 0 or in_progress > 0:
        print(f"\nStatus: {not_started + in_progress} projects remaining")
        return False
    else:
        print(f"\nStatus: All projects complete!")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Check if all cycle plan tasks are complete"
    )
    parser.add_argument(
        "--plan-file",
        default=str(DEFAULT_PLAN),
        help=f"Path to cycle_plan.md (default: {DEFAULT_PLAN})",
    )
    args = parser.parse_args()

    all_complete = check_completion(Path(args.plan_file))
    sys.exit(0 if all_complete else 1)


if __name__ == "__main__":
    main()
