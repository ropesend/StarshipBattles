#!/usr/bin/env python3
"""
Generate a project handoff document from review findings.

Usage:
    python review_to_project.py <review_folder> [--findings ID1,ID2,ID3]

Examples:
    python review_to_project.py 2026-01-23_general_game-logic
    python review_to_project.py 2026-01-23_security_api --findings SEC-01,SEC-02,IV-01
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import RESULTS_DIR

# Try to import from Projects scripts if available
try:
    projects_scripts = Path(__file__).parent.parent.parent / "Projects" / "scripts"
    sys.path.insert(0, str(projects_scripts))
    from utils.index_manager import get_next_project_id
    HAS_PROJECT_UTILS = True
except ImportError:
    HAS_PROJECT_UTILS = False


HANDOFF_TEMPLATE = '''# Project Handoff: From Review {review_name}

## Source Review
- **Review:** [{review_name}](../Reviews/results/{review_name}/)
- **Type:** {review_type}
- **Date:** {review_date}
- **Report:** [View Full Report](../Reviews/results/{review_name}/report.md)

## Selected Findings to Address

{findings_section}

## Proposed Project

### Title
[Suggested: {suggested_title}]

### Goals
Based on the selected findings:
{goals_section}

### Scope
**In Scope:**
{in_scope}

**Out of Scope:**
- Other review findings not selected
- [Add any additional exclusions]

### Estimated Effort
- Critical findings: {critical_count}
- Major findings: {major_count}
- Total findings: {total_count}
- Estimated complexity: {complexity}

## Recommended Phases

{phases_section}

## Next Steps

1. **Refine this document** with user input
2. **Run "Start Project" prompt** with this context
3. Protocol 01 will use these findings to:
   - Skip redundant exploration (already done in review)
   - Create detailed task breakdown
   - Assign complexity tags

## User Questions to Clarify

Before creating the project, consider:
- [ ] Is the suggested title appropriate?
- [ ] Should all selected findings be addressed, or prioritize some?
- [ ] Any constraints on the implementation approach?
- [ ] Timeline or effort budget?

---
*Generated: {generated_date}*
'''


def parse_report(report_path: Path) -> dict:
    """Parse the review report to extract findings."""
    content = report_path.read_text(encoding='utf-8')

    findings = []

    # Parse the findings table sections
    # Look for patterns like | ID | Title | Location | Effort |
    table_pattern = re.compile(
        r'\|\s*([A-Z]+-\d+)\s*\|\s*([^|]+)\|\s*`([^`]+)`\s*\|\s*(\w+)\s*\|'
    )

    for match in table_pattern.finditer(content):
        findings.append({
            'id': match.group(1).strip(),
            'title': match.group(2).strip(),
            'location': match.group(3).strip(),
            'effort': match.group(4).strip(),
        })

    # Determine severity from section headers
    severity_map = {}
    current_severity = None

    for line in content.split('\n'):
        if '### Critical' in line:
            current_severity = 'Critical'
        elif '### Major' in line:
            current_severity = 'Major'
        elif '### Minor' in line:
            current_severity = 'Minor'
        elif '### Info' in line:
            current_severity = 'Info'
        elif current_severity:
            # Check if this line contains a finding ID
            for f in findings:
                if f['id'] in line:
                    f['severity'] = current_severity

    # Extract metadata
    type_match = re.search(r'\*\*Type:\*\*\s*(.+)', content)
    date_match = re.search(r'\*\*Date:\*\*\s*(.+)', content)

    return {
        'findings': findings,
        'review_type': type_match.group(1).strip() if type_match else "Review",
        'review_date': date_match.group(1).strip() if date_match else "",
    }


def filter_findings(findings: list, selected_ids: list = None) -> list:
    """Filter findings to selected IDs, or all Critical/Major if none specified."""
    if selected_ids:
        return [f for f in findings if f['id'] in selected_ids]
    else:
        # Default: all Critical and Major
        return [f for f in findings if f.get('severity') in ('Critical', 'Major')]


def generate_handoff(review_folder: Path, selected_ids: list = None) -> str:
    """Generate a project handoff document from review findings."""
    report_path = review_folder / "report.md"

    if not report_path.exists():
        print(f"ERROR: Report not found: {report_path}")
        print("Run compile_findings.py first.")
        sys.exit(1)

    # Parse report
    parsed = parse_report(report_path)
    all_findings = parsed['findings']

    # Filter to selected findings
    selected = filter_findings(all_findings, selected_ids)

    if not selected:
        print("WARNING: No findings selected. Using all Critical and Major findings.")
        selected = filter_findings(all_findings, None)

    if not selected:
        print("ERROR: No findings to create project from.")
        sys.exit(1)

    # Generate findings section
    findings_lines = []
    for f in selected:
        severity = f.get('severity', 'Unknown')
        findings_lines.append(f"### {f['id']}: {f['title']}")
        findings_lines.append(f"- **Severity:** {severity}")
        findings_lines.append(f"- **Location:** `{f['location']}`")
        findings_lines.append(f"- **Effort:** {f['effort']}")
        findings_lines.append("")

    # Generate goals
    goals_lines = []
    for f in selected:
        goals_lines.append(f"- Address {f['id']}: {f['title']}")

    # Generate scope
    in_scope_lines = []
    locations = set()
    for f in selected:
        loc = f['location'].split(':')[0] if ':' in f['location'] else f['location']
        if loc not in locations:
            locations.add(loc)
            in_scope_lines.append(f"- {loc}")

    # Count by severity
    critical_count = len([f for f in selected if f.get('severity') == 'Critical'])
    major_count = len([f for f in selected if f.get('severity') == 'Major'])
    total_count = len(selected)

    # Estimate complexity
    if critical_count > 2 or total_count > 10:
        complexity = "Complex"
    elif critical_count > 0 or total_count > 5:
        complexity = "Medium"
    else:
        complexity = "Simple"

    # Generate phases
    phases_lines = []
    if critical_count > 0:
        phases_lines.append("### Phase 1: Critical Fixes")
        phases_lines.append("**Priority:** Immediate")
        phases_lines.append("")
        for f in selected:
            if f.get('severity') == 'Critical':
                phases_lines.append(f"- [ ] {f['id']}: {f['title']}")
        phases_lines.append("")

    if major_count > 0:
        phase_num = 2 if critical_count > 0 else 1
        phases_lines.append(f"### Phase {phase_num}: Major Issues")
        phases_lines.append("**Priority:** High")
        phases_lines.append("")
        for f in selected:
            if f.get('severity') == 'Major':
                phases_lines.append(f"- [ ] {f['id']}: {f['title']}")
        phases_lines.append("")

    other = [f for f in selected if f.get('severity') not in ('Critical', 'Major')]
    if other:
        phase_num = 1 + (1 if critical_count > 0 else 0) + (1 if major_count > 0 else 0)
        phases_lines.append(f"### Phase {phase_num}: Cleanup")
        phases_lines.append("**Priority:** Normal")
        phases_lines.append("")
        for f in other:
            phases_lines.append(f"- [ ] {f['id']}: {f['title']}")
        phases_lines.append("")

    # Suggest title
    review_name = review_folder.name
    parts = review_name.split('_')
    if len(parts) >= 3:
        review_type_short = parts[1]
        description = ' '.join(parts[2:]).replace('-', ' ').title()
        suggested_title = f"{review_type_short.title()} Remediation: {description}"
    else:
        suggested_title = f"Review Remediation: {review_name}"

    # Generate handoff
    handoff = HANDOFF_TEMPLATE.format(
        review_name=review_name,
        review_type=parsed['review_type'],
        review_date=parsed['review_date'],
        findings_section='\n'.join(findings_lines),
        suggested_title=suggested_title,
        goals_section='\n'.join(goals_lines),
        in_scope='\n'.join(in_scope_lines) if in_scope_lines else "- [Specify scope]",
        critical_count=critical_count,
        major_count=major_count,
        total_count=total_count,
        complexity=complexity,
        phases_section='\n'.join(phases_lines) if phases_lines else "[Define phases based on findings]",
        generated_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    return handoff


def main():
    parser = argparse.ArgumentParser(
        description='Generate a project handoff from review findings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python review_to_project.py 2026-01-23_general_game-logic
    python review_to_project.py 2026-01-23_security_api --findings SEC-01,SEC-02,IV-01

If --findings is not specified, all Critical and Major findings are used.
        """
    )
    parser.add_argument('review_folder',
                        help='Review folder name or path')
    parser.add_argument('--findings', '-f',
                        help='Comma-separated list of finding IDs to include')

    args = parser.parse_args()

    # Resolve folder path
    folder_path = Path(args.review_folder)
    if not folder_path.is_absolute():
        if (RESULTS_DIR / args.review_folder).exists():
            folder_path = RESULTS_DIR / args.review_folder
        elif not folder_path.exists():
            print(f"ERROR: Review folder not found: {args.review_folder}")
            sys.exit(1)

    # Parse finding IDs
    selected_ids = None
    if args.findings:
        selected_ids = [f.strip() for f in args.findings.split(',')]

    print(f"\n{'=' * 50}")
    print(f"Generating Project Handoff")
    print('=' * 50)
    print(f"\nReview: {folder_path.name}")
    if selected_ids:
        print(f"Selected findings: {', '.join(selected_ids)}")
    else:
        print("Selected findings: All Critical and Major")

    # Generate handoff
    handoff = generate_handoff(folder_path, selected_ids)

    # Write handoff document
    handoff_file = folder_path / "project_handoff.md"
    handoff_file.write_text(handoff, encoding='utf-8')

    print(f"\n{'=' * 50}")
    print("HANDOFF GENERATED")
    print(f"  File: {handoff_file}")
    print(f"\nNext steps:")
    print(f"  1. Review and edit the handoff document")
    print(f"  2. Run 'Start Project' prompt with the handoff as context")
    print(f"  3. Or use: python Projects/scripts/create_project.py \"<title>\"")
    print('=' * 50)


if __name__ == '__main__':
    main()
