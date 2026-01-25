#!/usr/bin/env python3
"""
Validate that a project is ready for audit.

Usage:
    python validate_audit_ready.py PROJ-08
    python validate_audit_ready.py PROJ-08 --run-tests  # Also run pytest
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.markdown_parser import parse_project_file, find_incomplete_tasks
from utils.index_manager import get_project_entry


class ValidationResult:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passes: List[str] = []

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


def validate_audit_ready(project_id: str, run_tests: bool = False) -> ValidationResult:
    """Validate that a project is ready for audit."""
    result = ValidationResult()

    try:
        project_data = parse_project_file(project_id)
    except FileNotFoundError as e:
        result.errors.append(str(e))
        return result

    # Check 1: All phases complete or deferred
    for phase in project_data.phases:
        status_lower = phase.status.lower()
        if "complete" in status_lower:
            result.passes.append(f"Phase {phase.number}: {phase.status}")
        elif "deferred" in status_lower or "skipped" in status_lower:
            result.warnings.append(f"Phase {phase.number}: {phase.status} (acceptable)")
        elif "not started" in status_lower:
            result.errors.append(f"Phase {phase.number}: {phase.status} - not started")
        else:
            result.errors.append(f"Phase {phase.number}: {phase.status} - not complete")

    # Check 2: All tasks complete
    incomplete = find_incomplete_tasks(project_data)
    if incomplete:
        total_incomplete = len(incomplete)
        result.errors.append(f"{total_incomplete} tasks have incomplete subtasks:")
        for phase, task, unchecked in incomplete[:5]:  # Show first 5
            result.errors.append(f"  Phase {phase.number} > Task {task.id}: {len(unchecked)} unchecked")
        if total_incomplete > 5:
            result.errors.append(f"  ... and {total_incomplete - 5} more")
    else:
        total_tasks = sum(len(phase.tasks) for phase in project_data.phases)
        result.passes.append(f"All {total_tasks} tasks complete")

    # Check 3: No blockers
    if project_data.current_state:
        blockers = project_data.current_state.blockers
        if blockers and blockers.lower() not in ['none', 'no', '']:
            result.errors.append(f"Blockers reported: {blockers}")
        else:
            result.passes.append("No blockers reported")

    # Check 4: Project status in index
    entry = get_project_entry(project_id)
    if entry:
        if entry.status == "Awaiting Verification":
            result.passes.append(f"Index status: {entry.status}")
        elif entry.status == "In Progress":
            result.warnings.append(f"Index status is '{entry.status}', expected 'Awaiting Verification'")
        else:
            result.warnings.append(f"Index status: {entry.status}")

    # Check 5: Run tests if requested
    # NOTE: Audit ALWAYS runs full test suite (no --testmon)
    # This ensures complete verification regardless of testmon state
    if run_tests:
        print("\nRunning pytest (FULL SUITE - no testmon)...")
        try:
            proc = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if proc.returncode == 0:
                result.passes.append("All tests passed")
            else:
                result.errors.append(f"Tests failed (exit code {proc.returncode})")
                # Show last few lines of output
                lines = proc.stdout.split('\n')[-10:]
                for line in lines:
                    if line.strip():
                        result.errors.append(f"  {line}")
        except subprocess.TimeoutExpired:
            result.errors.append("Tests timed out after 5 minutes")
        except FileNotFoundError:
            result.warnings.append("pytest not found - skipping test run")

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Validate project is ready for audit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python validate_audit_ready.py PROJ-08
    python validate_audit_ready.py PROJ-08 --run-tests
        """
    )
    parser.add_argument('project_id', help='Project ID (e.g., PROJ-08)')
    parser.add_argument('--run-tests', action='store_true',
                        help='Also run pytest to verify tests pass')

    args = parser.parse_args()

    print(f"\n{'=' * 50}")
    print(f"Audit Readiness Check: {args.project_id}")
    print('=' * 50)

    result = validate_audit_ready(args.project_id, args.run_tests)

    print("\nCHECKING: Phase completion")
    for msg in [m for m in result.passes if 'Phase' in m]:
        print(f"  [PASS] {msg}")
    for msg in [m for m in result.warnings if 'Phase' in m]:
        print(f"  [WARN] {msg}")
    for msg in [m for m in result.errors if 'Phase' in m]:
        print(f"  [FAIL] {msg}")

    print("\nCHECKING: Task completion")
    for msg in [m for m in result.passes if 'task' in m.lower()]:
        print(f"  [PASS] {msg}")
    for msg in [m for m in result.errors if 'task' in m.lower()]:
        print(f"  [FAIL] {msg}")

    print("\nCHECKING: Blockers and status")
    for msg in result.passes:
        if 'Phase' not in msg and 'task' not in msg.lower() and 'test' not in msg.lower():
            print(f"  [PASS] {msg}")
    for msg in result.warnings:
        if 'Phase' not in msg:
            print(f"  [WARN] {msg}")
    for msg in result.errors:
        if 'Phase' not in msg and 'task' not in msg.lower() and 'test' not in msg.lower():
            print(f"  [FAIL] {msg}")

    if args.run_tests:
        print("\nCHECKING: Tests")
        for msg in [m for m in result.passes if 'test' in m.lower()]:
            print(f"  [PASS] {msg}")
        for msg in [m for m in result.errors if 'test' in m.lower()]:
            print(f"  [FAIL] {msg}")

    print(f"\n{'=' * 50}")
    print(f"RESULT: {'PASSED' if result.passed else 'FAILED'}")
    if result.passed:
        print("Project is ready for audit.")
    else:
        print(f"{len(result.errors)} errors, {len(result.warnings)} warnings")
        print("Fix errors before proceeding with audit.")
    print('=' * 50)

    sys.exit(0 if result.passed else 1)


if __name__ == '__main__':
    main()
