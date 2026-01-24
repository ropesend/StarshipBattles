#!/usr/bin/env python3
"""
Show project status summary.

Usage:
    python project_status.py PROJ-08           # Detailed status
    python project_status.py PROJ-08 --brief   # One-line summary
    python project_status.py --all             # All active projects
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.markdown_parser import parse_project_file, find_incomplete_tasks
from utils.index_manager import read_projects_index, parse_project_entries
from utils.config import ACTIVE_DIR


def get_progress_bar(completed: int, total: int, width: int = 6) -> str:
    """Generate a simple progress bar."""
    if total == 0:
        return "[" + " " * width + "]"

    filled = int(width * completed / total)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def show_project_status(project_id: str, brief: bool = False) -> bool:
    """Show status for a single project."""
    try:
        project_data = parse_project_file(project_id)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return False

    # Calculate totals
    total_tasks = 0
    completed_tasks = 0

    for phase in project_data.phases:
        for task in phase.tasks:
            total_tasks += 1
            if task.subtasks and all(c for c, _ in task.subtasks):
                completed_tasks += 1

    # Get status from current state
    status = "Unknown"
    if project_data.current_state and project_data.current_state.active_phase:
        status = project_data.current_state.active_phase

    if brief:
        pct = 100 * completed_tasks // max(1, total_tasks)
        print(f"{project_id} | {project_data.title} | {status} | {pct}% ({completed_tasks}/{total_tasks})")
        return True

    # Detailed output
    print(f"\n{'=' * 60}")
    print(f"Project Status: {project_id}")
    print('=' * 60)

    print(f"\nTitle: {project_data.title}")
    print(f"Status: {status}")

    if project_data.current_state:
        cs = project_data.current_state
        if cs.last_updated:
            print(f"Last Updated: {cs.last_updated}")

    print(f"\nProgress:")
    for phase in project_data.phases:
        phase_tasks = len(phase.tasks)
        phase_complete = sum(1 for t in phase.tasks
                           if t.subtasks and all(c for c, _ in t.subtasks))
        pct = 100 * phase_complete // max(1, phase_tasks) if phase_tasks > 0 else 0
        bar = get_progress_bar(phase_complete, phase_tasks)

        # Pad phase name
        name = f"Phase {phase.number}: {phase.name}"[:40]
        print(f"  {name:<42} {bar} {pct:3}% ({phase_complete}/{phase_tasks} tasks)")

    overall_pct = 100 * completed_tasks // max(1, total_tasks)
    print(f"\nOverall: {completed_tasks}/{total_tasks} tasks complete ({overall_pct}%)")

    # Current state summary
    if project_data.current_state:
        cs = project_data.current_state
        print(f"\nCurrent State Summary:")
        if cs.last_action:
            print(f"  Last Action: {cs.last_action[:60]}...")
        if cs.next_action:
            print(f"  Next Action: {cs.next_action[:60]}...")
        if cs.blockers and cs.blockers.lower() not in ['none', 'no', '']:
            print(f"  Blockers: {cs.blockers}")

    print()
    return True


def show_all_projects(brief: bool = False) -> bool:
    """Show status for all active projects."""
    if brief:
        print("\n=== Active Projects ===")

    # Find all projects in active_projects directory
    project_ids = []

    for item in ACTIVE_DIR.iterdir():
        if item.is_dir() and item.name.startswith("PROJ-"):
            project_ids.append(item.name)
        elif item.is_file() and item.name.startswith("PROJ-") and item.suffix == ".md":
            project_ids.append(item.stem)

    project_ids = sorted(set(project_ids))

    if not project_ids:
        print("No active projects found.")
        return True

    for project_id in project_ids:
        show_project_status(project_id, brief=True)

    if not brief:
        print(f"\nTotal: {len(project_ids)} active projects")

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Show project status summary',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python project_status.py PROJ-08
    python project_status.py PROJ-08 --brief
    python project_status.py --all
        """
    )
    parser.add_argument('project_id', nargs='?', help='Project ID (e.g., PROJ-08)')
    parser.add_argument('--brief', action='store_true',
                        help='Show one-line summary')
    parser.add_argument('--all', action='store_true',
                        help='Show all active projects')

    args = parser.parse_args()

    if args.all:
        success = show_all_projects(args.brief)
    elif args.project_id:
        success = show_project_status(args.project_id, args.brief)
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
