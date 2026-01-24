#!/usr/bin/env python3
"""
Validate that a project phase is ready for completion.

Usage:
    python validate_phase.py PROJ-08 2         # Validate Phase 2
    python validate_phase.py PROJ-08 all       # Validate all phases
    python validate_phase.py PROJ-08 2 --strict  # Fail on warnings too
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.markdown_parser import parse_project_file, get_phases, get_current_state, Phase
from utils.config import FRESHNESS_THRESHOLD_HOURS


class ValidationResult:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passes: List[str] = []

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def passed_strict(self) -> bool:
        return len(self.errors) == 0 and len(self.warnings) == 0


def validate_phase(project_id: str, phase_num: int, strict: bool = False) -> ValidationResult:
    """Validate a specific phase."""
    result = ValidationResult()

    try:
        project_data = parse_project_file(project_id)
    except FileNotFoundError as e:
        result.errors.append(str(e))
        return result

    # Find the target phase
    target_phase: Optional[Phase] = None
    for phase in project_data.phases:
        if phase.number == phase_num:
            target_phase = phase
            break

    if not target_phase:
        result.errors.append(f"Phase {phase_num} not found in project")
        return result

    # Check 1: Checkbox completion
    for task in target_phase.tasks:
        checked = sum(1 for c, _ in task.subtasks if c)
        total = len(task.subtasks)

        if total == 0:
            result.warnings.append(f"Task {task.id}: No subtasks defined")
        elif checked < total:
            unchecked = [text[:50] + "..." if len(text) > 50 else text
                        for c, text in task.subtasks if not c]
            result.errors.append(
                f"Task {task.id}: {checked}/{total} subtasks complete. "
                f"Missing: {unchecked[:2]}{'...' if len(unchecked) > 2 else ''}"
            )
        else:
            result.passes.append(f"Task {task.id}: {checked}/{total} subtasks complete")

    # Check 2: Phase status consistency
    all_tasks_complete = all(
        all(c for c, _ in task.subtasks)
        for task in target_phase.tasks
        if task.subtasks  # Only check tasks that have subtasks
    )

    status_lower = target_phase.status.lower()
    if "complete" in status_lower and not all_tasks_complete:
        result.errors.append(
            f"Phase {phase_num} status is '{target_phase.status}' but has incomplete tasks"
        )
    elif all_tasks_complete and "complete" not in status_lower and target_phase.tasks:
        result.warnings.append(
            f"Phase {phase_num} has all tasks complete but status is '{target_phase.status}'"
        )
    else:
        result.passes.append(f"Phase status '{target_phase.status}' is consistent")

    # Check 3: Current State freshness
    current_state = project_data.current_state
    if current_state and current_state.last_updated:
        try:
            # Try common date formats
            date_str = current_state.last_updated
            for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%d"]:
                try:
                    last_updated = datetime.strptime(date_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                result.warnings.append(f"Could not parse Last Updated date: {date_str}")
                last_updated = None

            if last_updated:
                age = datetime.now() - last_updated
                if age > timedelta(hours=FRESHNESS_THRESHOLD_HOURS):
                    result.warnings.append(
                        f"Current State last updated {age.days}d {age.seconds // 3600}h ago"
                    )
                else:
                    result.passes.append(f"Current State freshness OK ({date_str})")
        except Exception as e:
            result.warnings.append(f"Error checking date: {e}")

    # Check 4: Notes filled for completed tasks
    for task in target_phase.tasks:
        if task.subtasks and all(c for c, _ in task.subtasks):  # All complete
            if not task.notes:
                result.warnings.append(f"Task {task.id} is complete but has empty Notes")

    return result


def print_result(result: ValidationResult, phase_num: int) -> None:
    """Print validation result in formatted output."""
    print(f"\nCHECKING: Phase {phase_num} validation")

    if result.passes:
        for msg in result.passes:
            print(f"  [PASS] {msg}")

    if result.errors:
        for msg in result.errors:
            print(f"  [FAIL] {msg}")

    if result.warnings:
        for msg in result.warnings:
            print(f"  [WARN] {msg}")

    if not result.errors and not result.warnings and not result.passes:
        print("  [INFO] No tasks found to validate")


def main():
    parser = argparse.ArgumentParser(
        description='Validate project phase completion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python validate_phase.py PROJ-08 2         # Validate Phase 2
    python validate_phase.py PROJ-08 all       # Validate all phases
    python validate_phase.py PROJ-08 2 --strict  # Fail on warnings too
        """
    )
    parser.add_argument('project_id', help='Project ID (e.g., PROJ-08)')
    parser.add_argument('phase', help='Phase number or "all"')
    parser.add_argument('--strict', action='store_true',
                        help='Fail on warnings too')

    args = parser.parse_args()

    print(f"\n{'=' * 50}")
    print(f"Phase Validation: {args.project_id}")
    print('=' * 50)

    try:
        if args.phase.lower() == 'all':
            project_data = parse_project_file(args.project_id)
            all_passed = True

            for phase in project_data.phases:
                result = validate_phase(args.project_id, phase.number, args.strict)
                print(f"\n--- Phase {phase.number}: {phase.name} ---")
                print_result(result, phase.number)

                if args.strict:
                    if not result.passed_strict():
                        all_passed = False
                else:
                    if not result.passed:
                        all_passed = False

            print(f"\n{'=' * 50}")
            print(f"RESULT: {'PASSED' if all_passed else 'FAILED'}")
            print('=' * 50)
            sys.exit(0 if all_passed else 1)
        else:
            phase_num = int(args.phase)
            result = validate_phase(args.project_id, phase_num, args.strict)
            print_result(result, phase_num)

            if args.strict:
                passed = result.passed_strict()
            else:
                passed = result.passed

            print(f"\n{'=' * 50}")
            print(f"RESULT: {'PASSED' if passed else 'FAILED'}")
            if result.errors or result.warnings:
                print(f"{len(result.errors)} errors, {len(result.warnings)} warnings")
            print('=' * 50)

            sys.exit(0 if passed else 1)

    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        sys.exit(2)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(2)


if __name__ == '__main__':
    main()
