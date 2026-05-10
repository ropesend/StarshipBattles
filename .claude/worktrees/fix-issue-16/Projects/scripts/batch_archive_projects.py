#!/usr/bin/env python3
"""
Archive multiple projects at once.
By default, this script skips validation/audit checks.

Usage:
    python Projects/scripts/batch_archive_projects.py PROJ-01 PROJ-02 PROJ-03
    python Projects/scripts/batch_archive_projects.py PROJ-01 PROJ-02 --dry-run
    python Projects/scripts/batch_archive_projects.py PROJ-01 PROJ-02 --check    # Enable validation
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from archive_project import archive_project

def batch_archive(project_ids: list[str], dry_run: bool = False, force: bool = True):
    """Archive a list of projects. Defaults to force=True (skip audits)."""
    results = []
    
    print(f"\nBATCH ARCHIVE: {len(project_ids)} projects")
    if force:
        print("NOTE: Defaulting to SKIP validation/audits.")
    
    for project_id in project_ids:
        # We pass force=force to skip validation if force is True
        success = archive_project(project_id, dry_run=dry_run, force=force)
        results.append((project_id, success))
    
    # Summary
    print(f"\n{'=' * 50}")
    print("BATCH SUMMARY")
    print(f"{'=' * 50}")
    
    success_count = sum(1 for _, s in results if s)
    fail_count = len(results) - success_count
    
    for project_id, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {project_id}")
    
    print(f"\nTOTAL: {len(results)} | SUCCESS: {success_count} | FAIL: {fail_count}")
    print(f"{'=' * 50}")
    
    return fail_count == 0

def main():
    parser = argparse.ArgumentParser(
        description='Archive multiple projects at once (defaults to skipping audits)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('project_ids', nargs='+', help='List of Project IDs (e.g., PROJ-01 PROJ-02)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would happen without making changes')
    parser.add_argument('--check', action='store_false', dest='force',
                        help='Perform validation checks before archiving (default is to skip)')
    parser.set_defaults(force=True)

    args = parser.parse_args()

    success = batch_archive(args.project_ids, args.dry_run, args.force)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
