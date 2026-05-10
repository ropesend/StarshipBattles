#!/usr/bin/env python3
"""
Manage the deep archive for completed projects.

Keeps archived_projects/ lean (max 20 recent) by sweeping older projects
into deep_archive/ organized by numeric range (PROJ-001-050, etc.).

Usage:
    python deep_archive_manager.py sweep              # Move excess archived to deep archive
    python deep_archive_manager.py sweep --dry-run     # Preview what would happen
    python deep_archive_manager.py status              # Show archive statistics
    python deep_archive_manager.py lookup PROJ-42      # Find a deep-archived project
"""

import argparse
import shutil
import re
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import (
    ARCHIVED_DIR, DEEP_ARCHIVE_DIR, MAX_ARCHIVED_PROJECTS,
)
from utils.index_manager import (
    get_archived_entries_from_index,
    remove_entries_from_archived_section,
    append_to_deep_archive_index,
    read_deep_archive_index,
    ProjectEntry,
)


def _project_sort_key(entry: ProjectEntry) -> int:
    """Extract numeric ID for sorting."""
    match = re.search(r'PROJ-(\d+)', entry.project_id)
    return int(match.group(1)) if match else 0


def _range_dir_name(proj_num: int) -> str:
    """Get the range directory name for a project number (e.g., PROJ-001-050)."""
    range_start = ((proj_num - 1) // 50) * 50 + 1
    range_end = range_start + 49
    return f"PROJ-{range_start:03d}-{range_end:03d}"


def sweep(dry_run: bool = False) -> int:
    """Move excess archived projects to deep archive.

    Keeps the most recent MAX_ARCHIVED_PROJECTS in archived_projects/.
    Returns the number of projects moved.
    """
    entries = get_archived_entries_from_index()

    if len(entries) <= MAX_ARCHIVED_PROJECTS:
        print(f"Archive has {len(entries)} projects (max {MAX_ARCHIVED_PROJECTS}). Nothing to sweep.")
        return 0

    # Sort by project number — keep the highest-numbered (most recent) ones
    entries.sort(key=_project_sort_key)
    to_sweep = entries[:-MAX_ARCHIVED_PROJECTS]
    keeping = entries[-MAX_ARCHIVED_PROJECTS:]

    print(f"Archive has {len(entries)} projects (max {MAX_ARCHIVED_PROJECTS}).")
    print(f"  Sweeping: {len(to_sweep)} projects to deep archive")
    print(f"  Keeping:  {len(keeping)} most recent in archived_projects/")
    print()

    if to_sweep:
        print(f"  Oldest to sweep: {to_sweep[0].project_id} ({to_sweep[0].title})")
        print(f"  Newest to sweep: {to_sweep[-1].project_id} ({to_sweep[-1].title})")
        print(f"  Oldest to keep:  {keeping[0].project_id} ({keeping[0].title})")
        print()

    if dry_run:
        print("DRY RUN - would move these projects:")
        for entry in to_sweep:
            proj_num = _project_sort_key(entry)
            range_name = _range_dir_name(proj_num)
            print(f"  {entry.project_id} -> deep_archive/{range_name}/{entry.project_id}")
        return len(to_sweep)

    # Create deep archive root
    DEEP_ARCHIVE_DIR.mkdir(exist_ok=True)

    moved = []
    for entry in to_sweep:
        proj_num = _project_sort_key(entry)
        range_name = _range_dir_name(proj_num)
        range_dir = DEEP_ARCHIVE_DIR / range_name
        range_dir.mkdir(exist_ok=True)

        # Move the directory from archived_projects to deep_archive
        source = ARCHIVED_DIR / entry.project_id
        dest = range_dir / entry.project_id

        if source.is_dir():
            shutil.move(str(source), str(dest))
            moved.append(entry)
            print(f"  Moved {entry.project_id} -> deep_archive/{range_name}/")
        else:
            # Try as single file
            source_file = ARCHIVED_DIR / f"{entry.project_id}.md"
            if source_file.exists():
                dest_file = range_dir / f"{entry.project_id}.md"
                shutil.move(str(source_file), str(dest_file))
                moved.append(entry)
                print(f"  Moved {entry.project_id}.md -> deep_archive/{range_name}/")
            else:
                print(f"  WARN: {entry.project_id} not found on disk, removing from index only")
                moved.append(entry)

    # Update the index: remove swept entries from Archived section
    if moved:
        remove_entries_from_archived_section([e.project_id for e in moved])
        append_to_deep_archive_index(moved)

    print(f"\nSwept {len(moved)} projects to deep archive.")
    return len(moved)


def status() -> None:
    """Show archive statistics."""
    # Count archived projects
    archived_entries = get_archived_entries_from_index()

    # Count deep-archived projects
    deep_count = 0
    range_dirs = []
    if DEEP_ARCHIVE_DIR.exists():
        for range_dir in sorted(DEEP_ARCHIVE_DIR.iterdir()):
            if range_dir.is_dir() and range_dir.name.startswith("PROJ-"):
                projects_in_range = [
                    p for p in range_dir.iterdir()
                    if p.is_dir() and p.name.startswith("PROJ-")
                ]
                deep_count += len(projects_in_range)
                range_dirs.append((range_dir.name, len(projects_in_range)))

    print(f"Archive Status")
    print(f"{'=' * 45}")
    print(f"  Active projects:          {_count_active()}")
    print(f"  Archived (recent):        {len(archived_entries)} / {MAX_ARCHIVED_PROJECTS} max")
    print(f"  Deep-archived:            {deep_count}")
    print(f"  Total completed:          {len(archived_entries) + deep_count}")
    print()

    if range_dirs:
        print(f"Deep Archive Ranges:")
        for name, count in range_dirs:
            print(f"  {name}: {count} projects")

    if len(archived_entries) > MAX_ARCHIVED_PROJECTS:
        excess = len(archived_entries) - MAX_ARCHIVED_PROJECTS
        print(f"\n  ** {excess} projects over limit — run 'sweep' to clean up **")


def _count_active() -> int:
    """Count active project directories."""
    from utils.config import ACTIVE_DIR
    if not ACTIVE_DIR.exists():
        return 0
    return len([p for p in ACTIVE_DIR.iterdir() if p.is_dir() and p.name.startswith("PROJ-")])


def lookup(project_id: str) -> None:
    """Find where a project lives (active, archived, or deep-archived)."""
    from utils.config import ACTIVE_DIR

    # Check active
    if (ACTIVE_DIR / project_id).exists():
        print(f"{project_id}: ACTIVE at active_projects/{project_id}/")
        return

    # Check archived
    if (ARCHIVED_DIR / project_id).exists():
        print(f"{project_id}: ARCHIVED at archived_projects/{project_id}/")
        return

    # Check deep archive
    if DEEP_ARCHIVE_DIR.exists():
        for range_dir in sorted(DEEP_ARCHIVE_DIR.iterdir()):
            if range_dir.is_dir():
                proj_path = range_dir / project_id
                if proj_path.exists():
                    print(f"{project_id}: DEEP ARCHIVED at deep_archive/{range_dir.name}/{project_id}/")
                    return

    # Check deep archive index for entries without directories
    content = read_deep_archive_index()
    if project_id in content:
        match = re.search(
            rf'\|\s*{re.escape(project_id)}\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|',
            content,
        )
        if match:
            print(f"{project_id}: Listed in deep archive index")
            print(f"  Title:     {match.group(1).strip()}")
            print(f"  Completed: {match.group(2).strip()}")
            print(f"  Range:     {match.group(3).strip()}")
            return

    print(f"{project_id}: NOT FOUND in any project location")


def main():
    parser = argparse.ArgumentParser(
        description='Manage the deep archive for completed projects',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
    sweep               Move excess archived projects to deep archive
    status              Show archive statistics
    lookup PROJ-XX      Find where a project lives

Examples:
    python deep_archive_manager.py sweep --dry-run
    python deep_archive_manager.py sweep
    python deep_archive_manager.py status
    python deep_archive_manager.py lookup PROJ-42
        """
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # sweep
    sweep_parser = subparsers.add_parser('sweep', help='Move excess archived projects to deep archive')
    sweep_parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')

    # status
    subparsers.add_parser('status', help='Show archive statistics')

    # lookup
    lookup_parser = subparsers.add_parser('lookup', help='Find where a project lives')
    lookup_parser.add_argument('project_id', help='Project ID (e.g., PROJ-42)')

    args = parser.parse_args()

    if args.command == 'sweep':
        sweep(dry_run=args.dry_run)
    elif args.command == 'status':
        status()
    elif args.command == 'lookup':
        lookup(args.project_id)


if __name__ == '__main__':
    main()
