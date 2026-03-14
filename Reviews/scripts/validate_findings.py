#!/usr/bin/env python3
"""
Parse findings from an original review for validation in update reviews.

Usage:
    python validate_findings.py <original_review_folder>
    python validate_findings.py <original_review_folder> --output findings.json
    python validate_findings.py <original_review_folder> --format markdown

Examples:
    python validate_findings.py 2026-01-24_general_full-codebase-maintainability
    python validate_findings.py 2026-01-24_general_full-codebase-maintainability --output findings.json
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import RESULTS_DIR, SEVERITY_LEVELS


def _normalize_severity(raw: str) -> str:
    """Normalize severity string to one of: Critical, Major, Minor, Info."""
    raw = raw.upper()
    if raw in ('HIGH', 'CRITICAL'):
        return 'Critical'
    elif raw in ('MAJOR', 'MEDIUM'):
        return 'Major'
    elif raw in ('MINOR', 'LOW'):
        return 'Minor'
    else:
        return 'Info'


# Severity words the parser recognizes
_SEVERITY_WORDS = r'CRITICAL|HIGH|MAJOR|MEDIUM|MINOR|LOW|INFO'

# Patterns for finding headers, ordered from most specific to least.
# Each pattern captures (severity, title) in groups 1 and 2.
_FINDING_PATTERNS = [
    # Standard: #### SEVERITY: Title  (or ### — accept h3 and h4)
    re.compile(
        rf'#{{3,4}}\s+({_SEVERITY_WORDS}):\s*(.+?)(?=\n)',
        re.IGNORECASE,
    ),
    # ID-first with colon: #### PC-01: SEVERITY - Title  (or ###)
    re.compile(
        rf'#{{3,4}}\s+\S+:\s*({_SEVERITY_WORDS})\s*[-–—]\s*(.+?)(?=\n)',
        re.IGNORECASE,
    ),
    # ID-first with double-dash: ### CE-01 -- SEVERITY: Title  (or ####)
    re.compile(
        rf'#{{3,4}}\s+\S+\s*--\s*({_SEVERITY_WORDS}):\s*(.+?)(?=\n)',
        re.IGNORECASE,
    ),
]


def parse_finding_from_content(content: str) -> list:
    """Parse findings from markdown content.

    Handles multiple heading formats that agents may produce:
      - #### SEVERITY: Title           (canonical)
      - ### SEVERITY: Title            (h3 instead of h4)
      - #### ID: SEVERITY - Title      (ID prefix with colon)
      - ### ID -- SEVERITY: Title      (ID prefix with double-dash)

    All patterns accept both ### and #### heading levels.
    """
    findings = []

    # Collect all matches from all patterns, deduplicating by position
    all_matches = []  # list of (start_pos, end_pos, severity, title)
    seen_positions = set()

    for pattern in _FINDING_PATTERNS:
        for match in pattern.finditer(content):
            pos = match.start()
            if pos not in seen_positions:
                seen_positions.add(pos)
                all_matches.append((
                    pos,
                    match.end(),
                    match.group(1),
                    match.group(2).strip(),
                ))

    # Sort by position in the document
    all_matches.sort(key=lambda m: m[0])

    for i, (start_pos, end_pos, raw_severity, title) in enumerate(all_matches):
        severity = _normalize_severity(raw_severity)

        # Get the content until next finding or end
        next_start = all_matches[i + 1][0] if i + 1 < len(all_matches) else len(content)
        finding_content = content[end_pos:next_start]

        # Extract ID
        id_match = re.search(r'\*\*ID:\*\*\s*(\S+)', finding_content)
        finding_id = id_match.group(1) if id_match else f"UNK-{i+1:02d}"

        # Extract location
        loc_match = re.search(r'\*\*Location:\*\*\s*`([^`]+)`', finding_content)
        location = loc_match.group(1) if loc_match else "Unknown"

        # Extract issue description
        issue_match = re.search(r'\*\*Issue:\*\*\s*(.+?)(?=\n\*\*|\n\n|$)', finding_content, re.DOTALL)
        issue = issue_match.group(1).strip() if issue_match else ""

        # Extract effort
        effort_match = re.search(r'\*\*Effort:\*\*\s*\[?(\w+)\]?', finding_content)
        effort = effort_match.group(1) if effort_match else "Unknown"

        # Extract recommendation
        rec_match = re.search(r'\*\*Recommendation:\*\*\s*(.+?)(?=\n\*\*|\n\n|$)', finding_content, re.DOTALL)
        recommendation = rec_match.group(1).strip() if rec_match else ""

        findings.append({
            'id': finding_id,
            'title': title,
            'severity': severity,
            'location': location,
            'issue': issue,
            'recommendation': recommendation,
            'effort': effort,
            'full_content': finding_content.strip()[:500]  # Truncate for validation
        })

    return findings


def parse_findings_from_agent_reports(findings_dir: Path) -> list:
    """Extract detailed findings from individual agent reports."""
    all_findings = []

    if not findings_dir.exists():
        return []

    for report_file in sorted(findings_dir.glob("*.md")):
        agent_name = report_file.stem.replace("_report", "").replace("_", " ").title()
        content = report_file.read_text(encoding='utf-8')

        findings = parse_finding_from_content(content)
        for f in findings:
            f['agent'] = agent_name
            all_findings.append(f)

    return all_findings


def parse_findings_from_report(report_path: Path) -> list:
    """Fallback: extract findings from the compiled report.md if findings/ not available."""
    if not report_path.exists():
        return []

    content = report_path.read_text(encoding='utf-8')
    return parse_finding_from_content(content)


def format_as_json(result: dict) -> str:
    """Format findings as JSON."""
    return json.dumps(result, indent=2)


def format_as_markdown(result: dict) -> str:
    """Format findings as markdown for validation agents."""
    output = f"# Findings from {result['original_review']}\n\n"
    output += f"**Total Findings:** {result['finding_count']}\n"
    output += f"**Parsed:** {result['parsed_date']}\n\n"

    output += "## Findings by Severity\n\n"
    for severity in SEVERITY_LEVELS:
        count = result['by_severity'].get(severity, 0)
        output += f"- **{severity}:** {count}\n"

    output += "\n---\n\n## All Findings\n\n"

    for finding in result['findings']:
        output += f"### {finding['id']}: {finding['title']}\n"
        output += f"- **Severity:** {finding['severity']}\n"
        output += f"- **Location:** `{finding['location']}`\n"
        output += f"- **Agent:** {finding.get('agent', 'Unknown')}\n"
        output += f"- **Effort:** {finding['effort']}\n"
        if finding.get('issue'):
            output += f"- **Issue:** {finding['issue'][:200]}{'...' if len(finding.get('issue', '')) > 200 else ''}\n"
        output += "\n"

    return output


def format_as_summary(result: dict) -> str:
    """Format findings as a brief summary."""
    output = f"""Original Review: {result['original_review']}
Total Findings: {result['finding_count']}
Parsed: {result['parsed_date']}

By Severity:
"""
    for severity in SEVERITY_LEVELS:
        count = result['by_severity'].get(severity, 0)
        output += f"  {severity}: {count}\n"

    return output


def main():
    parser = argparse.ArgumentParser(
        description='Parse findings from original review for validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output Formats:
  json     - Structured JSON (default)
  markdown - Formatted for validation agents
  summary  - Brief counts only

Examples:
    python validate_findings.py 2026-01-24_general_full-codebase-maintainability
    python validate_findings.py 2026-01-24_general_full-codebase-maintainability --output findings.json
    python validate_findings.py 2026-01-24_general_full-codebase-maintainability --format markdown
        """
    )
    parser.add_argument('review_folder', help='Original review folder name or path')
    parser.add_argument('--output', '-o', help='Output file path (default: stdout)')
    parser.add_argument('--format', '-f', choices=['json', 'markdown', 'summary'],
                        default='json', help='Output format (default: json)')

    args = parser.parse_args()

    # Resolve folder path
    folder = Path(args.review_folder)
    if not folder.is_absolute():
        if (RESULTS_DIR / args.review_folder).exists():
            folder = RESULTS_DIR / args.review_folder
        elif not folder.exists():
            print(f"ERROR: Review folder not found: {args.review_folder}", file=sys.stderr)
            sys.exit(1)

    if not folder.exists():
        print(f"ERROR: Review folder not found: {folder}", file=sys.stderr)
        sys.exit(1)

    # Parse findings
    findings_dir = folder / "findings"
    report_file = folder / "report.md"

    if findings_dir.exists() and list(findings_dir.glob("*.md")):
        findings = parse_findings_from_agent_reports(findings_dir)
        source = "agent_reports"
    elif report_file.exists():
        findings = parse_findings_from_report(report_file)
        source = "compiled_report"
    else:
        print(f"ERROR: No findings found in {folder}", file=sys.stderr)
        print("       Expected: findings/*.md or report.md", file=sys.stderr)
        sys.exit(1)

    # Build result
    result = {
        'original_review': folder.name,
        'parsed_date': datetime.now().isoformat(),
        'source': source,
        'finding_count': len(findings),
        'by_severity': {
            sev: len([f for f in findings if f['severity'] == sev])
            for sev in SEVERITY_LEVELS
        },
        'findings': findings
    }

    # Format output
    if args.format == 'json':
        output = format_as_json(result)
    elif args.format == 'markdown':
        output = format_as_markdown(result)
    else:
        output = format_as_summary(result)

    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output, encoding='utf-8')
        print(f"Written to: {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
