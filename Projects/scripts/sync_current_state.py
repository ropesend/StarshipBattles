#!/usr/bin/env python3
"""
Synchronize Current State section based on actual project progress.

Usage:
    python sync_current_state.py PROJ-08
    python sync_current_state.py PROJ-08 --dry-run   # Preview changes
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.markdown_parser import parse_project_file, find_incomplete_tasks, get_project_path
from utils.config import ACTIVE_DIR


def analyze_project_state(project_id: str) -> dict:
    """Analyze actual project state from checkboxes and phases."""
    project_data = parse_project_file(project_id)

    # Count phases and their status
    total_phases = len(project_data.phases)
    completed_phases = 0
    in_progress_phase = None
    not_started_phases = []

    for phase in project_data.phases:
        status_lower = phase.status.lower()
        if "complete" in status_lower:
            completed_phases += 1
        elif "in progress" in status_lower:
            in_progress_phase = phase
        elif "not started" in status_lower:
            not_started_phases.append(phase)

    # Count tasks
    total_tasks = sum(len(phase.tasks) for phase in project_data.phases)
    completed_tasks = 0
    for phase in project_data.phases:
        for task in phase.tasks:
            if task.subtasks and all(c for c, _ in task.subtasks):
                completed_tasks += 1

    # Find incomplete tasks
    incomplete = find_incomplete_tasks(project_data)

    # Determine current phase and next action
    if not incomplete:
        # All complete
        current_phase = "Complete - Awaiting Verification"
        next_action = "User verification required"
        next_task = None
    elif in_progress_phase:
        # There's an in-progress phase
        current_phase = f"Phase {in_progress_phase.number} - In Progress"
        # Find first incomplete task in this phase
        for phase, task, unchecked in incomplete:
            if phase.number == in_progress_phase.number:
                next_action = f"Continue Task {task.id}: {task.name}"
                next_task = task
                break
        else:
            next_action = f"Complete Phase {in_progress_phase.number}"
            next_task = None
    elif completed_phases < total_phases:
        # Find first incomplete phase
        for phase in project_data.phases:
            if "complete" not in phase.status.lower():
                current_phase = f"Phase {phase.number} - {phase.status}"
                # Find first task
                if phase.tasks:
                    task = phase.tasks[0]
                    next_action = f"Begin Task {task.id}: {task.name}"
                    next_task = task
                else:
                    next_action = f"Begin Phase {phase.number}"
                    next_task = None
                break
    else:
        current_phase = "Unknown"
        next_action = "Review project state"
        next_task = None

    return {
        'total_phases': total_phases,
        'completed_phases': completed_phases,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'current_phase': current_phase,
        'next_action': next_action,
        'next_task': next_task,
        'incomplete_count': len(incomplete),
        'project_data': project_data,
    }


def generate_current_state(analysis: dict) -> str:
    """Generate the Current State section content."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"**Last Updated:** {now}",
        f"**Active Phase:** {analysis['current_phase']}",
        f"**Last Agent Action:** [Synced by sync_current_state.py]",
        f"**Next Action:** {analysis['next_action']}",
        "**Blockers:** None",
    ]

    # Add context
    if analysis['incomplete_count'] == 0:
        context = f"All {analysis['total_tasks']} tasks complete across {analysis['total_phases']} phases."
    else:
        context = f"{analysis['completed_tasks']}/{analysis['total_tasks']} tasks complete. {analysis['incomplete_count']} tasks remaining."

    lines.append(f"**Context for Next Agent:** {context}")

    return "\n".join(lines)


def sync_current_state(project_id: str, dry_run: bool = False) -> bool:
    """Sync the Current State section with actual project state."""
    print(f"\n{'=' * 50}")
    print(f"Syncing Current State: {project_id}")
    print('=' * 50)

    try:
        analysis = analyze_project_state(project_id)
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        return False

    print(f"\nAnalyzing project structure...")
    print(f"  Total Phases: {analysis['total_phases']}")
    print(f"  Completed Phases: {analysis['completed_phases']} ({100 * analysis['completed_phases'] // max(1, analysis['total_phases'])}%)")
    print(f"  Total Tasks: {analysis['total_tasks']}")
    print(f"  Completed Tasks: {analysis['completed_tasks']} ({100 * analysis['completed_tasks'] // max(1, analysis['total_tasks'])}%)")

    print(f"\nDetected State:")
    print(f"  Current Phase: {analysis['current_phase']}")
    print(f"  Next Action: {analysis['next_action']}")

    new_state = generate_current_state(analysis)

    print(f"\nProposed Current State update:")
    for line in new_state.split('\n'):
        print(f"  {line}")

    if dry_run:
        print(f"\n{'=' * 50}")
        print("DRY RUN - No changes made")
        print('=' * 50)
        return True

    # Get the project file path
    filepath = get_project_path(project_id)
    content = filepath.read_text(encoding='utf-8')

    # Replace Current State section
    pattern = r'(## Current State\s*\n)(.+?)(?=\n## |\Z)'

    def replacement(match):
        return match.group(1) + new_state + "\n"

    new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)

    if count == 0:
        print("\n  [WARN] Could not find Current State section to update")
        return False

    filepath.write_text(new_content, encoding='utf-8')

    print(f"\n{'=' * 50}")
    print("SYNC COMPLETE")
    print(f"Updated: {filepath}")
    print('=' * 50)

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Sync Current State with actual project progress',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python sync_current_state.py PROJ-08
    python sync_current_state.py PROJ-08 --dry-run
        """
    )
    parser.add_argument('project_id', help='Project ID (e.g., PROJ-08)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview changes without modifying files')

    args = parser.parse_args()

    success = sync_current_state(args.project_id, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
