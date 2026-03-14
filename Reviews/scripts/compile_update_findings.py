#!/usr/bin/env python3
"""
Compile update review findings into a progress report.

Usage:
    python compile_update_findings.py <update_folder>

Examples:
    python compile_update_findings.py 2026-01-28_update_full-codebase-maintainability
    python compile_update_findings.py results/2026-01-28_update_full-codebase-maintainability
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import RESULTS_DIR, SEVERITY_LEVELS, VALIDATION_STATUSES


def parse_validation_report(validation_file: Path) -> dict:
    """Parse validation results from validation_report.md.

    Returns dict mapping finding_id -> {status, evidence}
    """
    if not validation_file.exists():
        return {}

    content = validation_file.read_text(encoding='utf-8')
    validations = {}

    # Pattern for validation entries - looking for status in the detailed section
    # #### AR-001: Title
    # **Status:** FIXED
    pattern = re.compile(
        r'####\s+(\S+):\s*.+?\n'
        r'.*?\*\*Status:\*\*\s*(\w+)'
        r'(?:.*?\*\*Evidence:\*\*\s*(.+?))?(?=\n####|\n---|\Z)',
        re.DOTALL
    )

    for match in pattern.finditer(content):
        finding_id = match.group(1)
        status = match.group(2).upper()
        evidence = match.group(3).strip() if match.group(3) else ""

        # Normalize status
        status_normalized = status.replace(" ", "_")
        if status_normalized in VALIDATION_STATUSES:
            validations[finding_id] = {
                'status': status_normalized,
                'evidence': evidence[:200] if evidence else ""
            }

    # Also try parsing from summary table format
    # | ID | Original Severity | Status | Evidence |
    table_pattern = re.compile(
        r'\|\s*(\S+)\s*\|\s*\w+\s*\|\s*(\w+)\s*\|\s*([^|]*)\s*\|'
    )

    for match in table_pattern.finditer(content):
        finding_id = match.group(1)
        if finding_id.startswith('--') or finding_id == 'ID':
            continue
        status = match.group(2).upper().replace(" ", "_")
        evidence = match.group(3).strip()

        if status in VALIDATION_STATUSES and finding_id not in validations:
            validations[finding_id] = {
                'status': status,
                'evidence': evidence[:200] if evidence else ""
            }

    return validations


def parse_regression_report(regression_file: Path) -> list:
    """Parse regressions from regression_report.md."""
    if not regression_file.exists():
        return []

    content = regression_file.read_text(encoding='utf-8')
    regressions = []

    # Pattern for regression entries
    pattern = re.compile(
        r'####\s*REG-(\d+):\s*(.+?)\n'
        r'.*?\*\*Related Finding:\*\*\s*(\S+)'
        r'.*?\*\*Location:\*\*\s*`([^`]+)`'
        r'(?:.*?\*\*Severity:\*\*\s*(\w+))?',
        re.DOTALL
    )

    for match in pattern.finditer(content):
        regressions.append({
            'id': f'REG-{match.group(1)}',
            'title': match.group(2).strip(),
            'related_finding': match.group(3),
            'location': match.group(4),
            'severity': match.group(5) if match.group(5) else 'Major'
        })

    return regressions


def parse_new_issues_report(new_issues_file: Path) -> list:
    """Parse new findings from new_issues_report.md."""
    if not new_issues_file.exists():
        return []

    content = new_issues_file.read_text(encoding='utf-8')
    new_issues = []

    # Pattern for new issue entries — accept both ### and #### headings
    pattern = re.compile(
        r'#{3,4}\s+(CRITICAL|HIGH|MAJOR|MEDIUM|MINOR|LOW|INFO):\s*(.+?)\n'
        r'.*?\*\*ID:\*\*\s*(NEW-\d+)'
        r'.*?\*\*Location:\*\*\s*`([^`]+)`',
        re.IGNORECASE | re.DOTALL
    )

    for match in pattern.finditer(content):
        severity = match.group(1).capitalize()
        if severity == 'Info':
            severity = 'Info'
        new_issues.append({
            'id': match.group(3),
            'title': match.group(2).strip(),
            'severity': severity,
            'location': match.group(4)
        })

    return new_issues


def parse_original_findings(original_folder: Path) -> list:
    """Parse findings from the original review."""
    # Import the validate_findings module's parsing function
    from validate_findings import parse_findings_from_agent_reports, parse_findings_from_report

    findings_dir = original_folder / "findings"
    report_file = original_folder / "report.md"

    if findings_dir.exists() and list(findings_dir.glob("*.md")):
        return parse_findings_from_agent_reports(findings_dir)
    elif report_file.exists():
        return parse_findings_from_report(report_file)

    return []


def calculate_progress(original_findings: list, validations: dict) -> dict:
    """Calculate progress metrics."""
    status_counts = defaultdict(int)
    severity_progress = defaultdict(lambda: {'original': 0, 'fixed': 0, 'remaining': 0})
    category_progress = defaultdict(lambda: {'original': 0, 'fixed': 0, 'remaining': 0})

    for finding in original_findings:
        fid = finding['id']
        severity = finding['severity']

        # Extract category from ID prefix (e.g., "AR" from "AR-001")
        category = fid.split('-')[0] if '-' in fid else 'UNK'

        severity_progress[severity]['original'] += 1
        category_progress[category]['original'] += 1

        if fid in validations:
            status = validations[fid]['status']
            status_counts[status] += 1
            if status == 'FIXED':
                severity_progress[severity]['fixed'] += 1
                category_progress[category]['fixed'] += 1
            else:
                severity_progress[severity]['remaining'] += 1
                category_progress[category]['remaining'] += 1
        else:
            status_counts['NOT_VALIDATED'] += 1
            severity_progress[severity]['remaining'] += 1
            category_progress[category]['remaining'] += 1

    total = len(original_findings)
    fixed = status_counts.get('FIXED', 0)

    return {
        'total': total,
        'status_counts': dict(status_counts),
        'severity_progress': dict(severity_progress),
        'category_progress': dict(category_progress),
        'fix_rate': (fixed / total * 100) if total > 0 else 0,
        'fixed': fixed
    }


def generate_progress_bar(percentage: float, width: int = 20) -> str:
    """Generate a text-based progress bar."""
    filled = int(width * percentage / 100)
    empty = width - filled
    return '█' * filled + '░' * empty


def generate_update_report(
    update_folder: Path,
    original_folder: Path,
    original_findings: list,
    validations: dict,
    regressions: list,
    new_issues: list,
    progress: dict
) -> str:
    """Generate the update review report."""
    date = datetime.now().strftime("%Y-%m-%d")
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Calculate days since original
    try:
        original_date_str = original_folder.name.split('_')[0]
        original_date = datetime.strptime(original_date_str, "%Y-%m-%d")
        days_since = (datetime.now() - original_date).days
    except (ValueError, IndexError):
        days_since = "Unknown"

    # Read scope to get update number
    scope_file = update_folder / "scope.md"
    update_number = 1
    if scope_file.exists():
        scope_content = scope_file.read_text(encoding='utf-8')
        match = re.search(r'\*\*Update Number:\*\*\s*(\d+)', scope_content)
        if match:
            update_number = int(match.group(1))

    total = progress['total']
    status_counts = progress['status_counts']

    report = f'''# Update Review Report: {update_folder.name}

## Metadata
- **Date:** {date}
- **Type:** Update Review
- **Original Review:** [{original_folder.name}](../{original_folder.name}/)
- **Original Date:** {original_folder.name.split('_')[0]}
- **Days Since Original:** {days_since}
- **Update Number:** {update_number}

---

## Executive Summary

### Progress Overview
| Metric | Count | Percentage | Progress |
|--------|-------|------------|----------|
| Original Findings | {total} | 100% | {generate_progress_bar(100)} |
'''

    for status in VALIDATION_STATUSES:
        count = status_counts.get(status, 0)
        pct = (count / total * 100) if total > 0 else 0
        status_display = status.replace('_', ' ').title()
        report += f"| {status_display} | {count} | {pct:.0f}% | {generate_progress_bar(pct)} |\n"

    # Add not validated if any
    not_validated = status_counts.get('NOT_VALIDATED', 0)
    if not_validated > 0:
        pct = (not_validated / total * 100) if total > 0 else 0
        report += f"| Not Validated | {not_validated} | {pct:.0f}% | {generate_progress_bar(pct)} |\n"

    report += f'''
### Severity Progress
| Severity | Original | Fixed | Remaining | Fix Rate |
|----------|----------|-------|-----------|----------|
'''

    for severity in SEVERITY_LEVELS:
        if severity in progress['severity_progress']:
            sp = progress['severity_progress'][severity]
            rate = (sp['fixed'] / sp['original'] * 100) if sp['original'] > 0 else 0
            report += f"| {severity} | {sp['original']} | {sp['fixed']} | {sp['remaining']} | {rate:.0f}% |\n"

    # Alerts section
    worse_count = status_counts.get('WORSE', 0)
    new_critical_major = len([i for i in new_issues if i['severity'] in ['Critical', 'Major']])

    if worse_count > 0 or regressions or new_critical_major > 0:
        report += "\n### Alerts\n"
        if worse_count > 0:
            report += f"- **{worse_count} finding(s) got WORSE** - requires attention\n"
        if regressions:
            report += f"- **{len(regressions)} regression(s) detected**\n"
        if new_critical_major > 0:
            report += f"- **{new_critical_major} new Critical/Major issue(s) found**\n"

    # Category progress
    if progress['category_progress']:
        report += f'''
### Progress by Category
| Category | Original | Fixed | Remaining | Fix Rate |
|----------|----------|-------|-----------|----------|
'''
        for category, cp in sorted(progress['category_progress'].items()):
            rate = (cp['fixed'] / cp['original'] * 100) if cp['original'] > 0 else 0
            report += f"| {category} | {cp['original']} | {cp['fixed']} | {cp['remaining']} | {rate:.0f}% |\n"

    # Detailed finding status
    report += "\n---\n\n## Detailed Finding Status\n\n"

    # Group findings by validation status
    by_status = defaultdict(list)
    for finding in original_findings:
        fid = finding['id']
        if fid in validations:
            status = validations[fid]['status']
            by_status[status].append({
                **finding,
                'evidence': validations[fid]['evidence']
            })
        else:
            by_status['NOT_VALIDATED'].append(finding)

    for status in ['FIXED', 'PARTIALLY_FIXED', 'STILL_PRESENT', 'WORSE', 'OBSOLETE', 'CANNOT_VERIFY', 'NOT_VALIDATED']:
        findings_list = by_status.get(status, [])
        if findings_list:
            status_display = status.replace('_', ' ').title()
            report += f"### {status_display} Findings ({len(findings_list)})\n"
            report += "| ID | Title | Severity | Evidence |\n"
            report += "|----|-------|----------|----------|\n"
            for f in findings_list:
                title = f['title'][:40] + '...' if len(f['title']) > 40 else f['title']
                evidence = f.get('evidence', '')[:50]
                report += f"| {f['id']} | {title} | {f['severity']} | {evidence} |\n"
            report += "\n"

    # Regressions section
    if regressions:
        report += "---\n\n## Regressions\n\n"
        for reg in regressions:
            report += f"### {reg['id']}: {reg['title']}\n"
            report += f"- **Related to:** {reg['related_finding']}\n"
            report += f"- **Location:** `{reg['location']}`\n"
            report += f"- **Severity:** {reg['severity']}\n\n"

    # New issues section
    if new_issues:
        report += "---\n\n## New Issues\n\n"
        report += "| ID | Severity | Title | Location |\n"
        report += "|----|----------|-------|----------|\n"
        for issue in new_issues:
            title = issue['title'][:40] + '...' if len(issue['title']) > 40 else issue['title']
            report += f"| {issue['id']} | {issue['severity']} | {title} | `{issue['location'][:30]}` |\n"
        report += "\n"

    # Recommendations
    report += "---\n\n## Recommendations\n\n"
    report += "### Immediate Actions\n"
    if regressions:
        reg_ids = ', '.join(r['id'] for r in regressions)
        report += f"1. Address regressions: {reg_ids}\n"
    if worse_count > 0:
        report += f"2. Investigate and re-fix {worse_count} finding(s) that got worse\n"
    if new_critical_major > 0:
        report += f"3. Review {new_critical_major} new Critical/Major issue(s)\n"

    remaining_critical = progress['severity_progress'].get('Critical', {}).get('remaining', 0)
    if remaining_critical > 0:
        report += f"4. Continue work on {remaining_critical} remaining Critical finding(s)\n"

    report += "\n### For Next Update\n"
    low_fix_categories = [
        cat for cat, cp in progress['category_progress'].items()
        if cp['original'] > 2 and (cp['fixed'] / cp['original'] if cp['original'] > 0 else 0) < 0.3
    ]
    if low_fix_categories:
        report += f"- Focus areas (low fix rate): {', '.join(low_fix_categories)}\n"
    report += "- Schedule next update review after remediation sprint\n"

    # Agent reports
    report += "\n---\n\n## Agent Reports\n\n"
    findings_dir = update_folder / "findings"
    if findings_dir.exists():
        for report_file in sorted(findings_dir.glob("*.md")):
            name = report_file.stem.replace("_", " ").title()
            report += f"- [{name}](findings/{report_file.name})\n"

    report += f'''
## Links
- [Original Review](../{original_folder.name}/)
- [Original Report](../{original_folder.name}/report.md)

---
*Update report generated: {date_time}*
'''

    return report


def main():
    parser = argparse.ArgumentParser(
        description='Compile update review findings into progress report',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python compile_update_findings.py 2026-01-28_update_full-codebase-maintainability
    python compile_update_findings.py results/2026-01-28_update_full-codebase-maintainability
        """
    )
    parser.add_argument('update_folder', help='Update review folder name or path')

    args = parser.parse_args()

    # Resolve folder path
    folder = Path(args.update_folder)
    if not folder.is_absolute():
        if (RESULTS_DIR / args.update_folder).exists():
            folder = RESULTS_DIR / args.update_folder
        elif not folder.exists():
            print(f"ERROR: Update folder not found: {args.update_folder}")
            sys.exit(1)

    if not folder.exists():
        print(f"ERROR: Update folder not found: {folder}")
        sys.exit(1)

    print(f"\n{'=' * 50}")
    print(f"Compiling Update Review: {folder.name}")
    print('=' * 50)

    # Read scope.md to get original review reference
    scope_file = folder / "scope.md"
    if not scope_file.exists():
        print(f"ERROR: scope.md not found in {folder}")
        sys.exit(1)

    scope_content = scope_file.read_text(encoding='utf-8')
    original_match = re.search(r'\*\*Original Review:\*\*\s*\[([^\]]+)\]', scope_content)

    if not original_match:
        print("ERROR: Could not find original review reference in scope.md")
        print("       Expected: **Original Review:** [folder_name](../folder_name/)")
        sys.exit(1)

    original_name = original_match.group(1).strip()
    original_folder = RESULTS_DIR / original_name

    if not original_folder.exists():
        print(f"ERROR: Original review not found: {original_folder}")
        sys.exit(1)

    print(f"\nOriginal review: {original_folder.name}")

    # Parse original findings
    print("Parsing original findings...")
    original_findings = parse_original_findings(original_folder)
    print(f"  Original findings: {len(original_findings)}")

    # Parse validation results
    validation_file = folder / "findings" / "validation_report.md"
    print("Parsing validation results...")
    validations = parse_validation_report(validation_file)
    print(f"  Validations parsed: {len(validations)}")

    # Parse regressions
    regression_file = folder / "findings" / "regression_report.md"
    regressions = parse_regression_report(regression_file)
    print(f"  Regressions: {len(regressions)}")

    # Parse new findings
    new_file = folder / "findings" / "new_issues_report.md"
    new_issues = parse_new_issues_report(new_file)
    print(f"  New issues: {len(new_issues)}")

    # Calculate progress
    print("\nCalculating progress metrics...")
    progress = calculate_progress(original_findings, validations)
    print(f"  Fix rate: {progress['fix_rate']:.1f}%")
    print(f"  Fixed: {progress['fixed']}/{progress['total']}")

    # Generate report
    print("\nGenerating update report...")
    report = generate_update_report(
        folder, original_folder, original_findings,
        validations, regressions, new_issues, progress
    )

    # Write report
    report_file = folder / "report.md"
    report_file.write_text(report, encoding='utf-8')
    print(f"  Written: {report_file}")

    print(f"\n{'=' * 50}")
    print("COMPILATION COMPLETE")
    print(f"Report: {report_file}")
    print(f"\nProgress Summary:")
    print(f"  Original Findings: {progress['total']}")
    print(f"  Fixed: {progress['fixed']} ({progress['fix_rate']:.0f}%)")
    if regressions:
        print(f"  Regressions: {len(regressions)}")
    if new_issues:
        print(f"  New Issues: {len(new_issues)}")
    print('=' * 50)


if __name__ == '__main__':
    main()
