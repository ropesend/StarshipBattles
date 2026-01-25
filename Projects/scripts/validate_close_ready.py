#!/usr/bin/env python3
"""
Validate that a project is ready to be closed/archived.

Usage:
    python validate_close_ready.py PROJ-08
    python validate_close_ready.py PROJ-08 --run-tests  # Also run pytest
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.markdown_parser import parse_project_file, find_incomplete_tasks
from utils.index_manager import get_project_entry
from utils.config import ACTIVE_DIR, ARCHIVED_DIR


class ValidationResult:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passes: List[str] = []

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


def validate_close_ready(project_id: str, run_tests: bool = False) -> ValidationResult:
    """Validate that a project is ready to be archived."""
    result = ValidationResult()

    try:
        project_data = parse_project_file(project_id)
    except FileNotFoundError as e:
        result.errors.append(str(e))
        return result

    # Check 1: All phases complete
    incomplete_phases = []
    for phase in project_data.phases:
        status_lower = phase.status.lower()
        if "complete" not in status_lower and "deferred" not in status_lower and "skipped" not in status_lower:
            incomplete_phases.append(f"Phase {phase.number}: {phase.status}")

    if incomplete_phases:
        result.errors.append(f"Incomplete phases: {', '.join(incomplete_phases)}")
    else:
        result.passes.append("All phases complete or deferred")

    # Check 2: All tasks complete
    incomplete = find_incomplete_tasks(project_data)
    if incomplete:
        result.errors.append(f"{len(incomplete)} tasks have incomplete subtasks")
    else:
        result.passes.append("All tasks complete")

    # Check 3: Check for audit passed in content
    content = project_data.content.lower()
    audit_patterns = [
        r'audit.*pass',
        r'\[x\].*audit',
        r'audit log.*pass',
    ]
    audit_found = any(re.search(p, content) for p in audit_patterns)

    if audit_found:
        result.passes.append("Audit appears to have passed")
    else:
        result.warnings.append("Could not confirm audit passed - verify manually")

    # Check 4: Check for user verified
    user_verified_patterns = [
        r'\[x\].*user verif',
        r'user.*verified',
    ]
    verified_found = any(re.search(p, content) for p in user_verified_patterns)

    if verified_found:
        result.passes.append("User verification appears complete")
    else:
        result.errors.append("User verification not found - checkbox may be unchecked")

    # Check 5: File location check
    # Check for directory structure (new) or flat file (old)
    dir_path = ACTIVE_DIR / project_id
    file_path = ACTIVE_DIR / f"{project_id}.md"

    if dir_path.is_dir():
        result.passes.append(f"Project directory exists at: {dir_path}")
        archive_target = ARCHIVED_DIR / project_id
    elif file_path.exists():
        result.passes.append(f"Project file exists at: {file_path}")
        archive_target = ARCHIVED_DIR / f"{project_id}.md"
    else:
        result.errors.append(f"Project not found in active_projects/")
        return result

    # Check archive target doesn't already exist
    if archive_target.exists():
        result.errors.append(f"Archive target already exists: {archive_target}")
    else:
        result.passes.append(f"Archive path available: {archive_target}")

    # Check 6: Project status in index
    entry = get_project_entry(project_id)
    if entry:
        if entry.status == "Awaiting Verification":
            result.passes.append(f"Index status: {entry.status}")
        elif entry.status == "Archived":
            result.errors.append("Project already marked as Archived in index")
        else:
            result.warnings.append(f"Index status is '{entry.status}', expected 'Awaiting Verification'")

    # Check 7: Run full test suite if requested
    # NOTE: Close ALWAYS runs full test suite (no --testmon)
    # This ensures complete verification before archival
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
                result.passes.append("Full test suite passed")
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
        description='Validate project is ready for archival',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python validate_close_ready.py PROJ-08
    python validate_close_ready.py PROJ-08 --run-tests
        """
    )
    parser.add_argument('project_id', help='Project ID (e.g., PROJ-08)')
    parser.add_argument('--run-tests', action='store_true',
                        help='Run pytest to verify tests pass before close')

    args = parser.parse_args()

    print(f"\n{'=' * 50}")
    print(f"Close Readiness Check: {args.project_id}")
    print('=' * 50)

    result = validate_close_ready(args.project_id, args.run_tests)

    print("\nCHECKING: Completion status")
    for msg in result.passes:
        if 'phase' in msg.lower() or 'task' in msg.lower():
            print(f"  [PASS] {msg}")
    for msg in result.errors:
        if 'phase' in msg.lower() or 'task' in msg.lower():
            print(f"  [FAIL] {msg}")

    print("\nCHECKING: Audit and verification")
    for msg in result.passes:
        if 'audit' in msg.lower() or 'verif' in msg.lower():
            print(f"  [PASS] {msg}")
    for msg in result.warnings:
        if 'audit' in msg.lower() or 'verif' in msg.lower():
            print(f"  [WARN] {msg}")
    for msg in result.errors:
        if 'audit' in msg.lower() or 'verif' in msg.lower():
            print(f"  [FAIL] {msg}")

    print("\nCHECKING: File locations")
    for msg in result.passes:
        if 'path' in msg.lower() or 'exist' in msg.lower() or 'directory' in msg.lower():
            print(f"  [PASS] {msg}")
    for msg in result.errors:
        if 'path' in msg.lower() or 'exist' in msg.lower() or 'found' in msg.lower():
            print(f"  [FAIL] {msg}")

    print("\nCHECKING: Index status")
    for msg in result.passes:
        if 'index' in msg.lower():
            print(f"  [PASS] {msg}")
    for msg in result.warnings:
        if 'index' in msg.lower():
            print(f"  [WARN] {msg}")
    for msg in result.errors:
        if 'index' in msg.lower():
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
        print("Project is ready for archival.")
        print(f"Run: python archive_project.py {args.project_id}")
    else:
        print(f"{len(result.errors)} errors, {len(result.warnings)} warnings")
        print("Fix errors before archiving.")
    print('=' * 50)

    sys.exit(0 if result.passed else 1)


if __name__ == '__main__':
    main()
