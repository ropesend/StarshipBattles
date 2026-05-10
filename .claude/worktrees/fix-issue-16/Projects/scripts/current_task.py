#!/usr/bin/env python3
"""
Show the current task to work on next.

Usage:
    python current_task.py PROJ-08
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.markdown_parser import parse_project_file, find_incomplete_tasks


def show_current_task(project_id: str) -> bool:
    """Show the current task to work on."""
    try:
        project_data = parse_project_file(project_id)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return False

    print(f"\n{'=' * 60}")
    print(f"Current Task: {project_id}")
    print('=' * 60)

    incomplete = find_incomplete_tasks(project_data)

    if not incomplete:
        print("\nNO TASKS REMAINING")
        print("Project is 100% complete!")

        if project_data.current_state:
            print(f"\nCurrent Status: {project_data.current_state.active_phase}")
            if project_data.current_state.next_action:
                print(f"Next Action: {project_data.current_state.next_action}")

        print()
        return True

    # Get first incomplete task
    phase, task, unchecked = incomplete[0]

    print(f"\nNEXT TASK: Phase {phase.number} > Task {task.id}: {task.name} [{task.complexity}]")
    print()

    if task.file_path:
        print(f"File: {task.file_path}")
    if task.tests:
        print(f"Tests: {task.tests}")

    print(f"\nSubtasks remaining ({len(unchecked)}):")
    for subtask_text in unchecked:
        # Truncate very long text
        text = subtask_text[:70] + "..." if len(subtask_text) > 70 else subtask_text
        print(f"  [ ] {text}")

    # Show context from Current State
    if project_data.current_state:
        cs = project_data.current_state
        print(f"\nContext from Current State:")
        if cs.last_action:
            print(f"  Last Action: {cs.last_action[:70]}...")
        if cs.blockers and cs.blockers.lower() not in ['none', 'no', '']:
            print(f"  Blockers: {cs.blockers}")
        if cs.context:
            # Show first part of context
            context_preview = cs.context[:150] + "..." if len(cs.context) > 150 else cs.context
            print(f"  Context: {context_preview}")

    # Show relevant decisions (if we can find any that mention this task or phase)
    # This would require parsing decisions.md - simplified for now

    print(f"\n{'=' * 60}")
    print(f"Run validation after completing this task:")
    print(f"  python Projects/scripts/validate_phase.py {project_id} {phase.number}")
    print('=' * 60)
    print()

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Show the current task to work on',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python current_task.py PROJ-08
        """
    )
    parser.add_argument('project_id', help='Project ID (e.g., PROJ-08)')

    args = parser.parse_args()

    success = show_current_task(args.project_id)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
