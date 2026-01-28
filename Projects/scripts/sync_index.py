#!/usr/bin/env python3
"""
Validate and sync projects_index.md with the filesystem.

This utility detects discrepancies between the index and actual directories,
and can optionally fix them.

Usage:
    python sync_index.py              # Report discrepancies only
    python sync_index.py --fix        # Fix discrepancies automatically
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import ACTIVE_DIR, ARCHIVED_DIR, INDEX_FILE
from utils.index_manager import read_projects_index, write_projects_index


def get_disk_projects(directory: Path) -> set:
    """Get all PROJ-XX directories from a directory."""
    projects = set()
    if directory.exists():
        for item in directory.iterdir():
            if item.is_dir() and re.match(r'^PROJ-\d+$', item.name):
                projects.add(item.name)
    return projects


def get_index_projects(content: str, section: str) -> set:
    """Extract project IDs from a section of the index."""
    projects = set()

    # Find the section
    if section == "Active":
        section_match = re.search(r'## Active Projects.*?(?=## |$)', content, re.DOTALL)
    elif section == "Archived":
        section_match = re.search(r'## Archived Projects.*?(?=## |$)', content, re.DOTALL)
    else:
        return projects

    if section_match:
        section_text = section_match.group(0)
        # Extract PROJ-XX from table rows
        for match in re.finditer(r'\|\s*(PROJ-\d+)\s*\|', section_text):
            projects.add(match.group(1))

    return projects


def get_next_id_from_index(content: str) -> int:
    """Get the 'Next Project ID' number from the index."""
    match = re.search(r'Next Project ID:\s*PROJ-(\d+)', content)
    if match:
        return int(match.group(1))
    return None


def find_highest_project_num(active: set, archived: set) -> int:
    """Find the highest project number from sets of project IDs."""
    all_projects = active | archived
    if not all_projects:
        return 0

    nums = []
    for proj in all_projects:
        match = re.match(r'PROJ-(\d+)', proj)
        if match:
            nums.append(int(match.group(1)))
    return max(nums) if nums else 0


def add_orphan_to_index(content: str, project_id: str, location: str) -> str:
    """Add an orphaned project to the appropriate section of the index."""
    today = datetime.now().strftime("%Y-%m-%d")

    if location == "active":
        # Add to Active Projects section
        new_row = f"| {project_id} | [ORPHANED - needs title] | Planning | {today} | {today} |"
        active_match = re.search(r'(## Active Projects.*?\n\|[^\n]+\|\n\|[-| ]+\|\n)', content, re.DOTALL)
        if active_match:
            insert_pos = active_match.end()
            content = content[:insert_pos] + new_row + "\n" + content[insert_pos:]
    else:
        # Add to Archived Projects section
        new_row = f"| {project_id} | [ORPHANED - needs title] | Archived | {today} | {today} |"
        archived_match = re.search(r'(## Archived Projects.*?\n\|[^\n]+\|\n\|[-| ]+\|\n)', content, re.DOTALL)
        if archived_match:
            insert_pos = archived_match.end()
            content = content[:insert_pos] + new_row + "\n" + content[insert_pos:]

    return content


def update_next_project_id(content: str, next_num: int) -> str:
    """Update the 'Next Project ID' line in the index."""
    return re.sub(
        r'Next Project ID:\s*PROJ-\d+',
        f'Next Project ID: PROJ-{next_num:02d}',
        content
    )


def main():
    parser = argparse.ArgumentParser(
        description='Validate and sync projects_index.md with filesystem',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python sync_index.py          # Report discrepancies
    python sync_index.py --fix    # Fix discrepancies
        """
    )
    parser.add_argument('--fix', action='store_true',
                        help='Automatically fix discrepancies')

    args = parser.parse_args()

    print(f"\n{'=' * 60}")
    print("Project Index Sync Validation")
    print('=' * 60)

    # Get projects from disk
    active_on_disk = get_disk_projects(ACTIVE_DIR)
    archived_on_disk = get_disk_projects(ARCHIVED_DIR)

    print(f"\nFilesystem:")
    print(f"  Active projects on disk:   {len(active_on_disk)}")
    print(f"  Archived projects on disk: {len(archived_on_disk)}")

    # Get projects from index
    content = read_projects_index()
    active_in_index = get_index_projects(content, "Active")
    archived_in_index = get_index_projects(content, "Archived")
    next_id_in_index = get_next_id_from_index(content)

    print(f"\nIndex (projects_index.md):")
    print(f"  Active projects in index:   {len(active_in_index)}")
    print(f"  Archived projects in index: {len(archived_in_index)}")
    print(f"  Next Project ID:            PROJ-{next_id_in_index:02d}" if next_id_in_index else "  Next Project ID:            [NOT FOUND]")

    # Find discrepancies
    orphaned_active = active_on_disk - active_in_index - archived_in_index
    orphaned_archived = archived_on_disk - archived_in_index - active_in_index
    missing_active = active_in_index - active_on_disk - archived_on_disk
    missing_archived = archived_in_index - archived_on_disk - active_on_disk

    print(f"\n{'=' * 60}")
    print("Discrepancies Found")
    print('=' * 60)

    has_issues = False

    if orphaned_active:
        has_issues = True
        print(f"\n[WARNING] Orphaned directories in active_projects/ (not in index):")
        for proj in sorted(orphaned_active):
            print(f"  - {proj}")

    if orphaned_archived:
        has_issues = True
        print(f"\n[WARNING] Orphaned directories in archived_projects/ (not in index):")
        for proj in sorted(orphaned_archived):
            print(f"  - {proj}")

    if missing_active:
        has_issues = True
        print(f"\n[WARNING] Missing directories for active index entries:")
        for proj in sorted(missing_active):
            print(f"  - {proj}")

    if missing_archived:
        has_issues = True
        print(f"\n[WARNING] Missing directories for archived index entries:")
        for proj in sorted(missing_archived):
            print(f"  - {proj}")

    # Check if Next Project ID is correct
    all_disk = active_on_disk | archived_on_disk
    highest_on_disk = find_highest_project_num(active_on_disk, archived_on_disk)
    expected_next = highest_on_disk + 1

    if next_id_in_index and next_id_in_index <= highest_on_disk:
        has_issues = True
        print(f"\n[WARNING] Next Project ID is too low:")
        print(f"  Current: PROJ-{next_id_in_index:02d}")
        print(f"  Should be at least: PROJ-{expected_next:02d}")

    if not has_issues:
        print("\n[OK] No discrepancies found. Index is in sync with filesystem.")
        print('=' * 60)
        return

    print('=' * 60)

    if not args.fix:
        print("\nRun with --fix to automatically repair these issues:")
        print("  python Projects/scripts/sync_index.py --fix")
        return

    # Apply fixes
    print("\nApplying fixes...")
    modified = False

    # Add orphaned active projects to index
    for proj in sorted(orphaned_active):
        print(f"  Adding {proj} to Active Projects section...")
        content = add_orphan_to_index(content, proj, "active")
        modified = True

    # Add orphaned archived projects to index
    for proj in sorted(orphaned_archived):
        print(f"  Adding {proj} to Archived Projects section...")
        content = add_orphan_to_index(content, proj, "archived")
        modified = True

    # Update Next Project ID if needed
    all_projects = active_on_disk | archived_on_disk | active_in_index | archived_in_index
    highest_all = find_highest_project_num(all_projects, set())
    correct_next = highest_all + 1

    if next_id_in_index is None or next_id_in_index <= highest_all:
        print(f"  Updating Next Project ID to PROJ-{correct_next:02d}...")
        content = update_next_project_id(content, correct_next)
        modified = True

    if modified:
        write_projects_index(content)
        print("\n[SUCCESS] Index updated successfully.")
        print("\nNOTE: Orphaned projects were added with placeholder titles.")
        print("      Please update them in projects_index.md with correct titles.")
    else:
        print("\n[INFO] No fixes were needed.")

    print('=' * 60)


if __name__ == '__main__':
    main()
