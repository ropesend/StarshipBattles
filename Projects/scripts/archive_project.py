#!/usr/bin/env python3
"""
Safely archive a completed project.

Usage:
    python archive_project.py PROJ-08
    python archive_project.py PROJ-08 --dry-run     # Show what would happen
    python archive_project.py PROJ-08 --force       # Skip validation (dangerous)
"""

import argparse
import shutil
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import ACTIVE_DIR, ARCHIVED_DIR, MAX_ARCHIVED_PROJECTS
from utils.index_manager import archive_project_in_index, get_archived_entries_from_index
from validate_close_ready import validate_close_ready
from deep_archive_manager import sweep as deep_archive_sweep


def archive_project(project_id: str, dry_run: bool = False, force: bool = False) -> bool:
    """Archive a project to the archived_projects directory.

    Returns True if successful, False otherwise.
    """
    print(f"\n{'=' * 50}")
    print(f"Archiving Project: {project_id}")
    print('=' * 50)

    # Step 1: Validation (unless forced)
    if not force:
        print("\nSTEP 1: Validation")
        print("  Running validate_close_ready.py...")
        result = validate_close_ready(project_id)

        if not result.passed:
            print(f"  [FAIL] Validation failed with {len(result.errors)} errors")
            for err in result.errors[:3]:
                print(f"         {err}")
            print("\n  Use --force to skip validation (not recommended)")
            return False
        print("  [PASS] Project ready for closure")
    else:
        print("\nSTEP 1: Validation")
        print("  [SKIP] Validation skipped (--force)")

    # Determine source and destination paths
    dir_source = ACTIVE_DIR / project_id
    file_source = ACTIVE_DIR / f"{project_id}.md"

    if dir_source.is_dir():
        source = dir_source
        dest = ARCHIVED_DIR / project_id
        is_directory = True
    elif file_source.exists():
        source = file_source
        dest = ARCHIVED_DIR / f"{project_id}.md"
        is_directory = False
    else:
        print(f"\n  [FAIL] Project not found: {project_id}")
        return False

    # Step 2: Move project
    print("\nSTEP 2: Move project")
    print(f"  FROM: {source}")
    print(f"  TO:   {dest}")

    if dry_run:
        print("  [DRY-RUN] Would move project")
    else:
        # Ensure archived_projects directory exists
        ARCHIVED_DIR.mkdir(exist_ok=True)

        if is_directory:
            shutil.move(str(source), str(dest))
        else:
            shutil.move(str(source), str(dest))
        print("  [DONE]")

    # Step 3: Update index
    print("\nSTEP 3: Update projects_index.md")
    if dry_run:
        print("  [DRY-RUN] Would update index:")
        print(f"    - Remove {project_id} from Active Projects")
        print(f"    - Add {project_id} to Archived Projects")
    else:
        try:
            archive_project_in_index(project_id)
            print("  [DONE] Index updated")
        except Exception as e:
            print(f"  [WARN] Could not update index: {e}")
            print("         Please update projects_index.md manually")

    # Step 4: Auto-sweep deep archive if over limit
    archived_count = len(get_archived_entries_from_index())
    if archived_count > MAX_ARCHIVED_PROJECTS:
        print(f"\nSTEP 4: Deep archive sweep ({archived_count} > {MAX_ARCHIVED_PROJECTS} max)")
        if dry_run:
            print("  [DRY-RUN] Would sweep excess projects to deep archive")
            deep_archive_sweep(dry_run=True)
        else:
            deep_archive_sweep(dry_run=False)
    else:
        print(f"\nSTEP 4: Deep archive sweep (not needed, {archived_count} <= {MAX_ARCHIVED_PROJECTS})")

    print(f"\n{'=' * 50}")
    if dry_run:
        print("DRY RUN COMPLETE - No changes made")
    else:
        print("ARCHIVE COMPLETE")
        print(f"Project {project_id} successfully archived.")
    print('=' * 50)

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Archive a completed project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python archive_project.py PROJ-08
    python archive_project.py PROJ-08 --dry-run
    python archive_project.py PROJ-08 --force
        """
    )
    parser.add_argument('project_id', help='Project ID (e.g., PROJ-08)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would happen without making changes')
    parser.add_argument('--force', action='store_true',
                        help='Skip validation checks (dangerous)')

    args = parser.parse_args()

    success = archive_project(args.project_id, args.dry_run, args.force)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
