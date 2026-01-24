#!/usr/bin/env python3
"""
Compile agent findings into a unified review report.

Usage:
    python compile_findings.py <review_folder>

Examples:
    python compile_findings.py 2026-01-23_general_game-logic-health
    python compile_findings.py results/2026-01-23_general_game-logic-health
"""

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import RESULTS_DIR, SEVERITY_LEVELS


def parse_finding(content: str) -> list:
    """Parse findings from a markdown file.

    Looks for patterns like:
    #### CRITICAL: Title
    **ID:** XXX-01
    **Location:** `file:lines`
    ...
    """
    findings = []

    # Pattern to match finding blocks
    finding_pattern = re.compile(
        r'####\s+(CRITICAL|HIGH|MAJOR|MEDIUM|MINOR|LOW|INFO|Info):\s*(.+?)(?=\n)',
        re.IGNORECASE
    )

    # Find all finding headers
    matches = list(finding_pattern.finditer(content))

    for i, match in enumerate(matches):
        severity = match.group(1).upper()
        title = match.group(2).strip()

        # Normalize severity
        if severity in ('HIGH', 'CRITICAL'):
            severity = 'Critical'
        elif severity in ('MAJOR', 'MEDIUM'):
            severity = 'Major'
        elif severity in ('MINOR', 'LOW'):
            severity = 'Minor'
        else:
            severity = 'Info'

        # Get the content until next finding or end
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        finding_content = content[start:end]

        # Extract ID
        id_match = re.search(r'\*\*ID:\*\*\s*(\S+)', finding_content)
        finding_id = id_match.group(1) if id_match else f"UNK-{i+1:02d}"

        # Extract location
        loc_match = re.search(r'\*\*Location:\*\*\s*`([^`]+)`', finding_content)
        location = loc_match.group(1) if loc_match else "Unknown"

        # Extract effort
        effort_match = re.search(r'\*\*Effort:\*\*\s*\[?(\w+)\]?', finding_content)
        effort = effort_match.group(1) if effort_match else "Unknown"

        findings.append({
            'severity': severity,
            'title': title,
            'id': finding_id,
            'location': location,
            'effort': effort,
            'content': finding_content.strip(),
        })

    return findings


def verify_agent_outputs(findings_dir: Path, min_content_size: int = 100) -> tuple:
    """Verify that agent output files exist and have content.

    Returns tuple of (found_agents, empty_agents, missing_count).
    """
    found_agents = []
    empty_agents = []

    if not findings_dir.exists():
        return [], [], 0

    for finding_file in findings_dir.glob("*.md"):
        agent_name = finding_file.stem.replace("_report", "").replace("_", " ").title()
        file_size = finding_file.stat().st_size

        if file_size < min_content_size:
            empty_agents.append({
                'name': agent_name,
                'file': finding_file.name,
                'size': file_size
            })
        else:
            found_agents.append({
                'name': agent_name,
                'file': finding_file.name,
                'size': file_size
            })

    return found_agents, empty_agents, 0


def compile_findings(review_folder: Path) -> dict:
    """Compile all findings from a review folder.

    Returns a dict with:
    - findings: list of all findings
    - by_severity: dict of findings grouped by severity
    - by_agent: dict of findings grouped by agent
    - stats: summary statistics
    """
    findings_dir = review_folder / "findings"

    if not findings_dir.exists():
        print(f"ERROR: Findings directory not found: {findings_dir}")
        sys.exit(1)

    # Verify agent outputs first
    found_agents, empty_agents, _ = verify_agent_outputs(findings_dir)

    if empty_agents:
        print(f"\n[WARNING] {len(empty_agents)} agent(s) produced empty or minimal output:")
        for agent in empty_agents:
            print(f"  - {agent['name']}: {agent['file']} ({agent['size']} bytes)")
        print("")

    if not found_agents:
        print(f"ERROR: No valid agent output files found in {findings_dir}")
        print("       Agents may have failed to write their reports.")
        print("       Check that agents completed successfully before compiling.")
        sys.exit(1)

    all_findings = []
    by_agent = defaultdict(list)
    by_severity = defaultdict(list)

    # Read all finding files (only those with content)
    for agent in found_agents:
        finding_file = findings_dir / agent['file']
        agent_name = agent['name']
        content = finding_file.read_text(encoding='utf-8')

        findings = parse_finding(content)
        if not findings:
            print(f"  [INFO] {agent_name}: No findings parsed (file may use unexpected format)")

        for f in findings:
            f['agent'] = agent_name
            all_findings.append(f)
            by_agent[agent_name].append(f)
            by_severity[f['severity']].append(f)

    # Calculate stats
    stats = {
        'total': len(all_findings),
        'critical': len(by_severity.get('Critical', [])),
        'major': len(by_severity.get('Major', [])),
        'minor': len(by_severity.get('Minor', [])),
        'info': len(by_severity.get('Info', [])),
        'agents': len(by_agent),
        'agents_with_findings': len([a for a in by_agent if by_agent[a]]),
        'empty_agents': len(empty_agents),
    }

    return {
        'findings': all_findings,
        'by_severity': dict(by_severity),
        'by_agent': dict(by_agent),
        'stats': stats,
    }


def generate_report(review_folder: Path, compiled: dict) -> str:
    """Generate the final report markdown."""
    # Read scope.md for metadata
    scope_file = review_folder / "scope.md"
    scope_content = scope_file.read_text(encoding='utf-8') if scope_file.exists() else ""

    # Extract metadata from scope
    date_match = re.search(r'\*\*Date:\*\*\s*(.+)', scope_content)
    type_match = re.search(r'\*\*Type:\*\*\s*(.+)', scope_content)
    desc_match = re.search(r'\*\*Description:\*\*\s*(.+)', scope_content)

    date = date_match.group(1).strip() if date_match else datetime.now().strftime("%Y-%m-%d")
    review_type = type_match.group(1).strip() if type_match else "Review"
    description = desc_match.group(1).strip() if desc_match else ""

    stats = compiled['stats']
    findings = compiled['findings']
    by_severity = compiled['by_severity']

    # Sort findings by severity for top 10
    severity_order = {'Critical': 0, 'Major': 1, 'Minor': 2, 'Info': 3}
    sorted_findings = sorted(findings, key=lambda x: severity_order.get(x['severity'], 4))

    report = f'''# Review Report: {review_folder.name}

## Metadata
- **Date:** {date}
- **Type:** {review_type}
- **Description:** {description}
- **Agents Used:** {stats['agents']}

## Executive Summary
- **Total Findings:** {stats['total']}
- **Critical:** {stats['critical']} | **Major:** {stats['major']} | **Minor:** {stats['minor']} | **Info:** {stats['info']}
'''

    # Health assessment
    if stats['critical'] > 0:
        report += "- **Overall Assessment:** Requires Immediate Attention\n"
    elif stats['major'] > 3:
        report += "- **Overall Assessment:** Needs Improvement\n"
    elif stats['major'] > 0:
        report += "- **Overall Assessment:** Generally Healthy with Issues\n"
    else:
        report += "- **Overall Assessment:** Healthy\n"

    # Priority Findings (Top 10)
    report += "\n## Priority Findings (Top 10)\n\n"

    for i, finding in enumerate(sorted_findings[:10], 1):
        report += f'''### {i}. {finding['severity'].upper()}: {finding['title']}
**ID:** {finding['id']}
**Agent:** {finding['agent']}
**Location:** `{finding['location']}`
**Effort:** {finding['effort']}

{finding['content'][:500]}{'...' if len(finding['content']) > 500 else ''}

---

'''

    # Findings by Severity
    report += "\n## Findings by Severity\n\n"

    for severity in SEVERITY_LEVELS:
        sev_findings = by_severity.get(severity, [])
        if sev_findings:
            report += f"### {severity} ({len(sev_findings)})\n"
            report += "| ID | Title | Location | Effort |\n"
            report += "|----|-------|----------|--------|\n"
            for f in sev_findings:
                report += f"| {f['id']} | {f['title'][:40]} | `{f['location'][:30]}` | {f['effort']} |\n"
            report += "\n"

    # Agent Reports
    report += "\n## Agent Reports\n\n"
    findings_dir = review_folder / "findings"
    for finding_file in sorted(findings_dir.glob("*.md")):
        agent_name = finding_file.stem.replace("_report", "").replace("_", " ").title()
        report += f"- [{agent_name} Report](findings/{finding_file.name})\n"

    # Appendix
    report += f'''
## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | {stats['total']} |
| Critical | {stats['critical']} |
| Major | {stats['major']} |
| Minor | {stats['minor']} |
| Info | {stats['info']} |
| Agents Used | {stats['agents']} |

---
*Report generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}*
'''

    return report


def main():
    parser = argparse.ArgumentParser(
        description='Compile agent findings into a unified review report',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python compile_findings.py 2026-01-23_general_game-logic-health
    python compile_findings.py results/2026-01-23_general_game-logic-health
        """
    )
    parser.add_argument('review_folder',
                        help='Review folder name or path')

    args = parser.parse_args()

    # Resolve folder path
    folder_path = Path(args.review_folder)
    if not folder_path.is_absolute():
        # Try as relative to results dir
        if (RESULTS_DIR / args.review_folder).exists():
            folder_path = RESULTS_DIR / args.review_folder
        elif not folder_path.exists():
            print(f"ERROR: Review folder not found: {args.review_folder}")
            sys.exit(1)

    print(f"\n{'=' * 50}")
    print(f"Compiling Findings: {folder_path.name}")
    print('=' * 50)

    # Check findings directory
    findings_dir = folder_path / "findings"
    finding_files = list(findings_dir.glob("*.md")) if findings_dir.exists() else []

    if not finding_files:
        print(f"\nWARNING: No finding files found in {findings_dir}")
        print("Agents should write their reports to the findings/ directory.")
        sys.exit(1)

    print(f"\nFound {len(finding_files)} agent report(s):")
    for f in finding_files:
        print(f"  - {f.name}")

    # Compile findings
    print("\nCompiling findings...")
    compiled = compile_findings(folder_path)

    print(f"\nStatistics:")
    print(f"  Total findings: {compiled['stats']['total']}")
    print(f"  Critical: {compiled['stats']['critical']}")
    print(f"  Major: {compiled['stats']['major']}")
    print(f"  Minor: {compiled['stats']['minor']}")
    print(f"  Info: {compiled['stats']['info']}")

    # Generate report
    print("\nGenerating report...")
    report = generate_report(folder_path, compiled)

    # Write report
    report_file = folder_path / "report.md"
    report_file.write_text(report, encoding='utf-8')
    print(f"  Written: {report_file}")

    print(f"\n{'=' * 50}")
    print("COMPILATION COMPLETE")
    print(f"Report: {report_file}")
    print('=' * 50)


if __name__ == '__main__':
    main()
