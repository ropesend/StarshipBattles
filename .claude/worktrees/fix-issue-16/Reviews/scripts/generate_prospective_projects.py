#!/usr/bin/env python3
"""
Scaffold prospective projects from a compiled sweep report.

Parses the compiled report.md, exports all findings as structured JSON,
checks for overlapping existing projects, and prepares the directory
structure for the project-generation agent.

Usage:
    python generate_prospective_projects.py <review_folder>
    python generate_prospective_projects.py <review_folder> --dry-run
    python generate_prospective_projects.py <review_folder> --force

Examples:
    python generate_prospective_projects.py 2026-02-10_sweep_full-codebase-sweep
    python generate_prospective_projects.py 2026-02-10_sweep_full-codebase-sweep --dry-run
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import RESULTS_DIR

# Import parse_report from review_to_project (same directory)
from review_to_project import parse_report, validate_parsed_findings, print_parsing_summary

# Try to import Projects index utilities for overlap checking
HAS_PROJECT_UTILS = False
_parse_project_entries = None
_projects_index_file = None

try:
    projects_scripts = Path(__file__).parent.parent.parent / "Projects" / "scripts"
    if (projects_scripts / "utils").exists():
        old_utils = sys.modules.pop('utils', None)
        old_utils_config = sys.modules.pop('utils.config', None)
        old_utils_index = sys.modules.pop('utils.index_manager', None)

        sys.path.insert(0, str(projects_scripts))
        try:
            from utils.index_manager import parse_project_entries, read_projects_index
            from utils.config import INDEX_FILE as PROJECTS_INDEX_FILE
            _parse_project_entries = parse_project_entries
            _projects_index_file = PROJECTS_INDEX_FILE
            HAS_PROJECT_UTILS = True
        finally:
            sys.path.remove(str(projects_scripts))
            if old_utils is not None:
                sys.modules['utils'] = old_utils
            else:
                sys.modules.pop('utils', None)
            if old_utils_config is not None:
                sys.modules['utils.config'] = old_utils_config
            if old_utils_index is not None:
                sys.modules['utils.index_manager'] = old_utils_index
except Exception:
    HAS_PROJECT_UTILS = False


# Known sweep type prefixes and their display names
SWEEP_TYPE_PREFIXES = {
    'ADR': 'Architecture Drift',
    'CON': 'Consistency Violations',
    'DUP': 'Duplication & Fragmentation',
    'LEG': 'Legacy System Holdovers',
    'TCG': 'Test Coverage Gaps',
}

# Known shard suffixes and their display names
SHARD_SUFFIXES = {
    'FND': 'Foundation',
    'SIM': 'Simulation',
    'STR': 'Strategy',
    'UI1': 'UI-Screens',
    'UI2': 'UI-Framework',
}


def extract_sweep_type(finding_id: str) -> str:
    """Extract sweep type prefix from a finding ID like ADR-FND-001."""
    parts = finding_id.split('-')
    if parts and parts[0] in SWEEP_TYPE_PREFIXES:
        return parts[0]
    return 'UNK'


def extract_shard(finding_id: str) -> str:
    """Extract shard suffix from a finding ID like ADR-FND-001."""
    parts = finding_id.split('-')
    if len(parts) >= 2 and parts[1] in SHARD_SUFFIXES:
        return parts[1]
    return 'UNK'


def enrich_findings(findings: list) -> list:
    """Add sweep_type and shard fields to each finding based on its ID."""
    for f in findings:
        fid = f.get('id', '')
        f['sweep_type'] = extract_sweep_type(fid)
        f['sweep_type_name'] = SWEEP_TYPE_PREFIXES.get(f['sweep_type'], 'Unknown')
        f['shard'] = extract_shard(fid)
        f['shard_name'] = SHARD_SUFFIXES.get(f['shard'], 'Unknown')
    return findings


def check_overlap_with_existing_projects(findings: list) -> str:
    """Check projects_index.md for existing projects that may overlap.

    Returns a markdown document describing potential overlaps.
    """
    if not HAS_PROJECT_UTILS or _parse_project_entries is None:
        return (
            "# Overlap Check\n\n"
            "Could not check for overlapping projects "
            "(Projects utilities not available).\n"
        )

    try:
        index_content = _projects_index_file.read_text(encoding='utf-8')
        entries = _parse_project_entries(index_content)
    except Exception as e:
        return (
            "# Overlap Check\n\n"
            f"Could not read projects index: {e}\n"
        )

    # Only check active (non-archived) projects
    active_entries = [
        e for e in entries
        if e.status not in ('Archived', 'Completed')
    ]

    # Keywords to match against project titles
    overlap_keywords = {
        'ADR': ['architecture', 'layer', 'violation', 'coupling', 'dependency'],
        'CON': ['consistency', 'naming', 'type', 'annotation', 'standardiz'],
        'DUP': ['duplication', 'duplicate', 'dry', 'fragmentation'],
        'LEG': ['legacy', 'cleanup', 'backward', 'deprecated', 'dead code'],
        'TCG': ['test', 'coverage', 'testing', 'untested'],
    }

    overlaps = []
    for entry in active_entries:
        title_lower = entry.title.lower()
        matching_types = []
        for sweep_type, keywords in overlap_keywords.items():
            if any(kw in title_lower for kw in keywords):
                matching_types.append(sweep_type)

        if matching_types:
            overlaps.append({
                'project_id': entry.project_id,
                'title': entry.title,
                'status': entry.status,
                'matching_types': matching_types,
            })

    # Build markdown
    lines = ["# Overlap Check", ""]
    lines.append(
        f"Checked {len(active_entries)} active projects in projects_index.md."
    )
    lines.append("")

    if not overlaps:
        lines.append("**No overlapping projects found.**")
    else:
        lines.append(
            f"**{len(overlaps)} potentially overlapping project(s) found:**"
        )
        lines.append("")
        lines.append("| Project | Title | Status | Overlaps With |")
        lines.append("|---------|-------|--------|---------------|")
        for o in overlaps:
            types_str = ', '.join(
                SWEEP_TYPE_PREFIXES.get(t, t) for t in o['matching_types']
            )
            lines.append(
                f"| {o['project_id']} | {o['title']} "
                f"| {o['status']} | {types_str} |"
            )
        lines.append("")
        lines.append(
            "> **Note:** Overlap detection is keyword-based and may produce "
            "false positives. The project generation agent should review "
            "these overlaps and note them in project proposals."
        )

    lines.append("")
    lines.append(
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
    )

    return '\n'.join(lines)


def generate_scaffolding(
    review_folder: Path,
    dry_run: bool = False,
    force: bool = False,
) -> bool:
    """Generate the prospective projects scaffolding.

    Creates:
    - prospective_projects/ directory
    - prospective_projects/all_findings.json
    - prospective_projects/overlap_check.md
    - rejected_projects/ directory

    Returns True if successful, False otherwise.
    """
    report_path = review_folder / "report.md"
    if not report_path.exists():
        print(f"ERROR: Report not found: {report_path}")
        print("Run compile_findings.py first.")
        return False

    prospective_dir = review_folder / "prospective_projects"
    rejected_dir = review_folder / "rejected_projects"

    # Check for existing prospective_projects directory
    if prospective_dir.exists() and not force:
        print(
            f"\nERROR: Prospective projects directory already exists: "
            f"{prospective_dir}"
        )
        print("Use --force to overwrite.")
        return False

    # Parse report
    print("\nSTEP 1: Parse report")
    parsed = parse_report(report_path)
    all_findings = parsed['findings']

    # Validate parsing results
    print_parsing_summary(all_findings)
    is_valid, warnings, errors = validate_parsed_findings(
        all_findings, min_expected=5
    )

    if errors:
        print("\n[ERROR] Parsing failed:")
        for err in errors:
            print(f"  - {err}")
        return False

    if warnings:
        print("\n[WARNING] Parsing completed with warnings:")
        for warn in warnings:
            print(f"  - {warn}")

    # Enrich findings with sweep type and shard
    print("\nSTEP 2: Enrich findings with sweep type and shard metadata")
    enriched = enrich_findings(all_findings)

    # Count by sweep type
    by_type = {}
    for f in enriched:
        st = f['sweep_type']
        by_type.setdefault(st, []).append(f)

    print("  Findings by sweep type:")
    for st in sorted(by_type.keys()):
        name = SWEEP_TYPE_PREFIXES.get(st, 'Unknown')
        findings = by_type[st]
        sev_counts = {}
        for f in findings:
            sev = f.get('severity', 'Unknown')
            sev_counts[sev] = sev_counts.get(sev, 0) + 1
        sev_str = ', '.join(
            f"{s}: {c}" for s, c in sorted(sev_counts.items())
        )
        print(f"    {name} ({st}): {len(findings)} ({sev_str})")

    # Count by shard
    by_shard = {}
    for f in enriched:
        sh = f['shard']
        by_shard.setdefault(sh, []).append(f)

    print("  Findings by shard:")
    for sh in sorted(by_shard.keys()):
        name = SHARD_SUFFIXES.get(sh, 'Unknown')
        print(f"    {name} ({sh}): {len(by_shard[sh])}")

    # Check overlaps
    print("\nSTEP 3: Check for overlapping existing projects")
    overlap_md = check_overlap_with_existing_projects(enriched)
    overlap_count = overlap_md.count('PROJ-')
    if overlap_count > 0:
        print(f"  Found {overlap_count} potentially overlapping project(s)")
    else:
        print("  No overlapping projects found")

    # Build JSON export
    print("\nSTEP 4: Prepare findings JSON")
    findings_json = []
    for f in enriched:
        findings_json.append({
            'id': f['id'],
            'severity': f.get('severity', 'Unknown'),
            'title': f['title'],
            'location': f.get('location', 'Unknown'),
            'effort': f.get('effort', 'Unknown'),
            'sweep_type': f['sweep_type'],
            'sweep_type_name': f['sweep_type_name'],
            'shard': f['shard'],
            'shard_name': f['shard_name'],
        })

    if dry_run:
        print(f"\n--- DRY RUN: Would create ---")
        print(f"  Directory: {prospective_dir}")
        print(f"  Directory: {rejected_dir}")
        print(f"  File: {prospective_dir / 'all_findings.json'} "
              f"({len(findings_json)} findings)")
        print(f"  File: {prospective_dir / 'overlap_check.md'}")
        print(f"\n--- END DRY RUN ---")
        return True

    # Create directories
    print("\nSTEP 5: Create directory structure")
    if prospective_dir.exists():
        import shutil
        shutil.rmtree(prospective_dir)
        print(f"  Removed existing: {prospective_dir}")

    prospective_dir.mkdir(parents=True, exist_ok=True)
    rejected_dir.mkdir(parents=True, exist_ok=True)
    print(f"  Created: {prospective_dir}")
    print(f"  Created: {rejected_dir}")

    # Write findings JSON
    print("\nSTEP 6: Write findings data")
    findings_file = prospective_dir / "all_findings.json"
    findings_file.write_text(
        json.dumps(findings_json, indent=2, ensure_ascii=False),
        encoding='utf-8',
    )
    print(f"  Written: {findings_file} ({len(findings_json)} findings)")

    # Write overlap check
    overlap_file = prospective_dir / "overlap_check.md"
    overlap_file.write_text(overlap_md, encoding='utf-8')
    print(f"  Written: {overlap_file}")

    print(f"\n{'=' * 50}")
    print("SCAFFOLDING COMPLETE")
    print(f"  Directory: {prospective_dir}")
    print(f"  Findings:  {len(findings_json)}")
    print(f"\nNext step: Run the project generation agent to analyze")
    print(f"findings and create project proposals.")
    print('=' * 50)

    return True


def main():
    parser = argparse.ArgumentParser(
        description=(
            'Scaffold prospective projects from a compiled sweep report'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python generate_prospective_projects.py 2026-02-10_sweep_full-codebase-sweep
    python generate_prospective_projects.py 2026-02-10_sweep_full-codebase-sweep --dry-run
    python generate_prospective_projects.py 2026-02-10_sweep_full-codebase-sweep --force
        """
    )
    parser.add_argument(
        'review_folder',
        help='Review folder name or path',
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be created without making changes',
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Overwrite existing prospective_projects directory',
    )

    args = parser.parse_args()

    # Resolve folder path
    folder_path = Path(args.review_folder)
    if not folder_path.is_absolute():
        if (RESULTS_DIR / args.review_folder).exists():
            folder_path = RESULTS_DIR / args.review_folder
        elif not folder_path.exists():
            print(f"ERROR: Review folder not found: {args.review_folder}")
            sys.exit(1)

    print(f"\n{'=' * 60}")
    print("Generating Prospective Projects Scaffolding")
    print('=' * 60)
    print(f"\nReview: {folder_path.name}")

    success = generate_scaffolding(folder_path, args.dry_run, args.force)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
