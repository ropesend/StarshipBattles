#!/usr/bin/env python3
"""
List incomplete tasks in a project.

Usage:
    python list_incomplete.py PROJ-08
    python list_incomplete.py PROJ-08 --phase 2
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.markdown_parser import parse_project_file, find_incomplete_tasks


def list_incomplete(project_id: str, phase_num: int = None) -> bool:
    """List all incomplete tasks in a project."""
    try:
        project_data = parse_project_file(project_id)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return False

    print(f"\n{'=' * 50}")
    print(f"Incomplete Tasks: {project_id}")
    print('=' * 50)

    incomplete = find_incomplete_tasks(project_data)

    # Filter by phase if specified
    if phase_num is not None:
        incomplete = [(p, t, u) for p, t, u in incomplete if p.number == phase_num]

    if not incomplete:
        if phase_num:
            print(f"\nNo incomplete tasks in Phase {phase_num}!")
        else:
            print("\nNo incomplete tasks found! Project is 100% complete.")

        # Count deferred/skipped
        deferred_count = sum(
            1 for phase in project_data.phases
            if "deferred" in phase.status.lower() or "skipped" in phase.status.lower()
        )
        if deferred_count > 0:
            print(f"\nDeferred phases: {deferred_count}")

        print()
        return True

    # Group by phase
    current_phase = None
    total_incomplete_tasks = 0
    total_unchecked = 0

    for phase, task, unchecked in incomplete:
        if current_phase != phase.number:
            current_phase = phase.number
            status = phase.status
            print(f"\nPhase {phase.number}: {phase.name} [{status}]")

        total_incomplete_tasks += 1
        total_unchecked += len(unchecked)

        print(f"\n  Task {task.id}: {task.name} [{task.complexity}]")
        if task.file_path:
            print(f"    File: {task.file_path}")
        if task.tests:
            print(f"    Tests: {task.tests}")

        print(f"    Unchecked subtasks:")
        for i, subtask_text in enumerate(unchecked[:5]):  # Show first 5
            # Truncate long text
            text = subtask_text[:60] + "..." if len(subtask_text) > 60 else subtask_text
            print(f"      [ ] {text}")
        if len(unchecked) > 5:
            print(f"      ... and {len(unchecked) - 5} more")

    print(f"\n{'=' * 50}")
    print(f"Summary")
    print('=' * 50)
    print(f"  Incomplete tasks: {total_incomplete_tasks}")
    print(f"  Unchecked subtasks: {total_unchecked}")

    if incomplete:
        first_phase, first_task, _ = incomplete[0]
        print(f"\n  Next task: Phase {first_phase.number} > Task {first_task.id}")

    print()
    return True


def main():
    parser = argparse.ArgumentParser(
        description='List incomplete tasks in a project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python list_incomplete.py PROJ-08
    python list_incomplete.py PROJ-08 --phase 2
        """
    )
    parser.add_argument('project_id', help='Project ID (e.g., PROJ-08)')
    parser.add_argument('--phase', type=int,
                        help='Only show tasks from specific phase')

    args = parser.parse_args()

    success = list_incomplete(args.project_id, args.phase)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
