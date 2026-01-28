#!/usr/bin/env python3
"""
Generate a project from review findings with full directory structure.

Usage:
    python review_to_project.py <review_folder> [options]

Examples:
    # Create project automatically (default)
    python review_to_project.py 2026-01-23_general_game-logic

    # Create project with custom title
    python review_to_project.py 2026-01-23_security_api --title "Security Fixes"

    # Select specific findings
    python review_to_project.py 2026-01-23_security_api --findings SEC-01,SEC-02,IV-01

    # Generate handoff document only (no project creation)
    python review_to_project.py 2026-01-23_general_game-logic --no-create-project
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
# We need to temporarily manipulate sys.path to import Projects utils
HAS_PROJECT_UTILS = False
PROJECTS_ACTIVE_DIR = None
get_next_project_id = None
add_project_to_index = None

try:
    projects_scripts = Path(__file__).parent.parent.parent / "Projects" / "scripts"
    if (projects_scripts / "utils").exists():
        # Save current utils module if any
        old_utils = sys.modules.pop('utils', None)
        old_utils_config = sys.modules.pop('utils.config', None)
        old_utils_index = sys.modules.pop('utils.index_manager', None)

        # Temporarily add Projects scripts to path (at front)
        sys.path.insert(0, str(projects_scripts))

        try:
            # Import Projects utilities
            from utils.index_manager import get_next_project_id, add_project_to_index
            from utils.config import ACTIVE_DIR as PROJECTS_ACTIVE_DIR
            HAS_PROJECT_UTILS = True
        finally:
            # Remove Projects scripts from path
            sys.path.remove(str(projects_scripts))

            # Restore Reviews utils module
            if old_utils is not None:
                sys.modules['utils'] = old_utils
            else:
                sys.modules.pop('utils', None)

            if old_utils_config is not None:
                sys.modules['utils.config'] = old_utils_config

            if old_utils_index is not None:
                sys.modules['utils.index_manager'] = old_utils_index

except Exception as e:
    # Import failed, project creation will not be available
    HAS_PROJECT_UTILS = False


# Templates for project creation
PLAN_TEMPLATE = '''# {project_id}: {title}

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py {project_id}` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py {project_id} [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
{phase_table}

## Current State
**Last Updated:** {date}
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
{overview}

## Goals
{goals}

## Scope
**In:**
{in_scope}

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
{key_files}

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
'''

DESIGN_TEMPLATE = '''# {project_id}: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [{review_name}]({review_link})
- **Type:** {review_type}
- **Date:** {review_date}
- **Report:** [View Full Report]({report_link})

## Initial Analysis
Findings from review - {total_findings} total findings identified.
- **Critical:** {critical_count}
- **Major:** {major_count}
- **Selected for remediation:** {selected_count}

## Selected Findings Summary

{findings_summary}

## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
'''

DECISIONS_TEMPLATE = '''# {project_id}: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| {date} | Project created from review | Review identified {total_findings} findings; {selected_count} selected for remediation |
| {date} | Severity-based phasing | Critical findings in Phase 1, Major in Phase 2, etc. |
'''

PHASE_TEMPLATE = '''# Phase {phase_num}: {phase_name}

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py {project_id} {phase_num}`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** {objective}
**Priority:** {priority}

---

## Tasks

{tasks}

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
'''

TASK_TEMPLATE = '''### Task {phase_num}.{task_num}: {finding_id} - {title} [{effort}]
**File:** `{location}`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]
'''

# Legacy handoff-only template (used with --no-create-project)
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


def normalize_severity(severity: str) -> str:
    """Normalize severity string to standard values."""
    severity = severity.strip().lower()
    if severity == 'critical':
        return 'Critical'
    elif severity in ('major', 'high'):
        # 'High' is often used as a priority/effort indicator, map to Major
        return 'Major'
    elif severity in ('minor', 'medium', 'low'):
        return 'Minor'
    elif severity in ('info', 'information'):
        return 'Info'
    return 'Unknown'


def normalize_effort(effort: str) -> str:
    """Normalize effort string to standard values."""
    effort = effort.strip().lower()
    if effort in ('simple', 'low', 'easy'):
        return 'Simple'
    elif effort in ('medium', 'moderate'):
        return 'Medium'
    elif effort in ('high', 'complex', 'hard', 'major', 'critical'):
        return 'Complex'
    return effort.title()  # Return as-is with title case


def extract_findings_section(content: str) -> str:
    """Extract the 'Findings by Category' or 'Findings by Severity' section from report.

    This avoids parsing 'Top 10' or 'Quick Wins' sections which have different formats.
    """
    # Look for "## Findings by" section
    section_match = re.search(
        r'## Findings by (Category|Severity)\s*\n',
        content
    )
    if not section_match:
        return content  # Fall back to full content

    start = section_match.end()

    # Find the end - next ## section that's not a subsection (###)
    # We want to stop at "## Module-Specific", "## Quick Wins", "## Recommended", etc.
    end_match = re.search(r'\n## [A-Z]', content[start:])
    if end_match:
        end = start + end_match.start()
    else:
        end = len(content)

    return content[start:end]


def parse_report(report_path: Path) -> dict:
    """Parse the review report to extract findings.

    Supports multiple formats:
    1. 5-column table: | ID | Severity | Title | Location | Effort |
    2. 4-column table: | ID | Title | `location` | Effort | (with section-based severity)
    3. Top 10 / Priority tables (fallback)
    4. Numbered recommendations (fallback)
    """
    content = report_path.read_text(encoding='utf-8')
    findings = []

    # First, try to extract findings from the dedicated "Findings by" section
    findings_section = extract_findings_section(content)

    # Format 1 (PRIMARY): 5-column findings table from compile_findings.py
    # | ID | Severity | Title | Location | Effort |
    table_5col_pattern = re.compile(
        r'\|\s*([A-Z]+-\d+)\s*\|'           # ID: AR-01, MOD-SIM-04, etc.
        r'\s*([^|]+)\|'                      # Severity: Critical, Major, etc.
        r'\s*([^|]+)\|'                      # Title: description
        r'\s*([^|]+)\|'                      # Location: file.py:line or file.py
        r'\s*([^|]+)\|',                     # Effort: Simple, Medium, High, etc.
        re.IGNORECASE
    )

    for match in table_5col_pattern.finditer(findings_section):
        finding_id = match.group(1).strip()
        severity_raw = match.group(2).strip()
        title = match.group(3).strip()
        location = match.group(4).strip()
        effort_raw = match.group(5).strip()

        # Skip table header rows
        if finding_id.upper() == 'ID' or severity_raw.lower() == 'severity':
            continue

        findings.append({
            'id': finding_id,
            'severity': normalize_severity(severity_raw),
            'title': title,
            'location': location.strip('`'),  # Remove backticks if present
            'effort': normalize_effort(effort_raw),
        })

    # Format 2 (FALLBACK): 4-column table (older format)
    # | ID | Title | `location` | Effort |
    if not findings:
        table_4col_pattern = re.compile(
            r'\|\s*([A-Z]+-\d+)\s*\|\s*([^|]+)\|\s*`?([^|`]+)`?\s*\|\s*(\w+)\s*\|'
        )

        for match in table_4col_pattern.finditer(findings_section):
            finding_id = match.group(1).strip()
            title = match.group(2).strip()
            location = match.group(3).strip()
            effort = match.group(4).strip()

            # Skip table header rows
            if finding_id.upper() == 'ID':
                continue

            findings.append({
                'id': finding_id,
                'title': title,
                'location': location,
                'effort': normalize_effort(effort),
            })

        # For 4-column format, determine severity from section headers
        current_severity = None
        for line in findings_section.split('\n'):
            # Match headers like "### Critical (12)" or "### Major"
            header_match = re.match(r'###\s*(Critical|Major|Minor|Info)', line, re.IGNORECASE)
            if header_match:
                current_severity = normalize_severity(header_match.group(1))
            elif current_severity:
                # Check if this line contains a finding ID
                for f in findings:
                    if f['id'] in line and 'severity' not in f:
                        f['severity'] = current_severity

    # Format 3 (FALLBACK): Top 10 / Priority table
    if not findings:
        top10_pattern = re.compile(
            r'\|\s*\*?\*?(\d+)\*?\*?\s*\|\s*([^|]+)\|\s*\*?\*?([^|]+)\*?\*?\s*\|\s*([^|]+)\|\s*([A-Z]+)\s*\|',
            re.IGNORECASE
        )
        for match in top10_pattern.finditer(content):
            rank = match.group(1).strip()
            area = match.group(2).strip()
            coverage = match.group(3).strip()
            detail = match.group(4).strip()
            priority = match.group(5).strip().upper()

            if rank.isdigit() and priority in ('CRITICAL', 'MAJOR', 'MINOR', 'INFO'):
                findings.append({
                    'id': f'GAP-{rank.zfill(2)}',
                    'title': area,
                    'location': f'[Multiple files - see {area}]',
                    'effort': 'Complex' if priority == 'CRITICAL' else 'Medium',
                    'severity': priority.capitalize(),
                })

    # Format 4 (FALLBACK): Numbered priority recommendations
    if not findings:
        priority_pattern = re.compile(
            r'^(\d+)\.\s+\*\*([^*]+)\*\*\s*[-–]\s*(.+)$',
            re.MULTILINE
        )

        for match in priority_pattern.finditer(content):
            num = match.group(1).strip()
            title = match.group(2).strip()
            description = match.group(3).strip()

            # Determine severity from position
            int_num = int(num) if num.isdigit() else 99
            if int_num <= 4:
                severity = 'Critical'
                effort = 'Complex'
            elif int_num <= 8:
                severity = 'Major'
                effort = 'Medium'
            else:
                severity = 'Minor'
                effort = 'Simple'

            findings.append({
                'id': f'REC-{num.zfill(2)}',
                'title': title,
                'location': f'[See report - {description[:50]}...]' if len(description) > 50 else f'[See report - {description}]',
                'effort': effort,
                'severity': severity,
            })

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


def validate_parsed_findings(findings: list, min_expected: int = 5) -> tuple:
    """Validate that parsing produced reasonable results.

    Returns (is_valid, warnings, errors) tuple.
    """
    warnings = []
    errors = []

    if len(findings) == 0:
        errors.append("No findings were parsed from the report")
        return False, warnings, errors

    if len(findings) < min_expected:
        warnings.append(f"Only {len(findings)} findings parsed (expected >= {min_expected})")

    # Check severity distribution
    unknown_severity = [f for f in findings if f.get('severity') in ('Unknown', None)]
    if len(unknown_severity) > len(findings) * 0.5:
        warnings.append(f"{len(unknown_severity)}/{len(findings)} findings have Unknown severity")

    # Check for missing locations
    no_location = [f for f in findings if not f.get('location') or f.get('location') == 'Unknown']
    if len(no_location) > len(findings) * 0.3:
        warnings.append(f"{len(no_location)} findings missing specific locations")

    # Check for duplicate IDs
    ids = [f['id'] for f in findings]
    duplicates = set([x for x in ids if ids.count(x) > 1])
    if duplicates:
        warnings.append(f"Duplicate finding IDs: {', '.join(duplicates)}")

    is_valid = len(errors) == 0
    return is_valid, warnings, errors


def print_parsing_summary(findings: list) -> None:
    """Print a summary of parsed findings for verification."""
    print(f"\n  Parsed {len(findings)} findings:")

    # Count by severity
    by_severity = {}
    for f in findings:
        sev = f.get('severity', 'Unknown')
        by_severity[sev] = by_severity.get(sev, 0) + 1

    for sev in ['Critical', 'Major', 'Minor', 'Info', 'Unknown']:
        count = by_severity.get(sev, 0)
        if count > 0:
            print(f"    {sev}: {count}")

    # Show first few findings as sample
    if findings:
        print(f"\n  Sample findings:")
        for f in findings[:3]:
            print(f"    - {f['id']}: {f['title'][:40]}... ({f.get('severity', 'Unknown')})")


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


def create_project_from_review(
    review_folder: Path,
    selected_ids: list = None,
    title: str = None
) -> tuple[str, Path]:
    """Create a full project structure from review findings.

    Returns tuple of (project_id, project_dir).
    """
    if not HAS_PROJECT_UTILS:
        print("ERROR: Projects utilities not available. Cannot create project.")
        print("       Use --no-create-project to generate handoff only.")
        sys.exit(1)

    report_path = review_folder / "report.md"
    if not report_path.exists():
        print(f"ERROR: Report not found: {report_path}")
        print("Run compile_findings.py first.")
        sys.exit(1)

    # Parse report
    parsed = parse_report(report_path)
    all_findings = parsed['findings']

    # Validate parsing results
    print_parsing_summary(all_findings)
    is_valid, warnings, errors = validate_parsed_findings(all_findings)

    if errors:
        print("\n[ERROR] Parsing failed:")
        for err in errors:
            print(f"  - {err}")
        print("\nPossible causes:")
        print("  - Report format doesn't match expected table structure")
        print("  - No 'Findings by Category/Severity' section in report")
        print("\nCheck report.md format and try again.")
        sys.exit(1)

    if warnings:
        print("\n[WARNING] Parsing completed with warnings:")
        for warn in warnings:
            print(f"  - {warn}")

    # Filter to selected findings
    selected = filter_findings(all_findings, selected_ids)
    if not selected:
        print("\nWARNING: No findings selected. Using all Critical and Major findings.")
        selected = filter_findings(all_findings, None)

    if not selected:
        print("ERROR: No findings to create project from.")
        sys.exit(1)

    # Generate title if not provided
    review_name = review_folder.name
    if title is None:
        parts = review_name.split('_')
        if len(parts) >= 3:
            review_type_short = parts[1]
            description = ' '.join(parts[2:]).replace('-', ' ').title()
            title = f"{review_type_short.title()} Remediation: {description}"
        else:
            title = f"Review Remediation: {review_name}"

    # Get project ID and create directory
    project_id = get_next_project_id()
    date = datetime.now().strftime("%Y-%m-%d")
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    project_dir = PROJECTS_ACTIVE_DIR / project_id
    findings_dir = project_dir / "findings"

    # Safety check: fail if directory already exists (prevents overwrites)
    if project_dir.exists():
        print(f"\n[ERROR] Directory already exists: {project_dir}")
        print("        This suggests the index is out of sync with the filesystem.")
        print("        Run: python Projects/scripts/sync_index.py --fix")
        print("        Or manually remove the directory if it's orphaned.")
        sys.exit(1)

    print(f"\nSTEP 1: Create directory structure")
    project_dir.mkdir(parents=True, exist_ok=False)
    findings_dir.mkdir(exist_ok=True)
    print(f"  Created: {project_dir}")
    print(f"  Created: {findings_dir}")

    # Group findings by severity for phasing
    critical = [f for f in selected if f.get('severity') == 'Critical']
    major = [f for f in selected if f.get('severity') == 'Major']
    other = [f for f in selected if f.get('severity') not in ('Critical', 'Major')]

    # Build phases list
    phases = []
    if critical:
        phases.append({
            'name': 'Critical Fixes',
            'priority': 'Immediate',
            'objective': 'Address critical severity findings that pose immediate risk',
            'findings': critical
        })
    if major:
        phases.append({
            'name': 'Major Issues',
            'priority': 'High',
            'objective': 'Address major severity findings that significantly impact quality',
            'findings': major
        })
    if other:
        phases.append({
            'name': 'Cleanup',
            'priority': 'Normal',
            'objective': 'Address remaining findings for overall improvement',
            'findings': other
        })

    # Generate phase table for plan.md
    phase_table_lines = []
    for i, phase in enumerate(phases, 1):
        phase_table_lines.append(
            f"| {i}. {phase['name']} | Not Started | [phase_{i}_checklist.md](phase_{i}_checklist.md) |"
        )

    # Generate goals
    goals_lines = []
    for f in selected[:10]:  # Limit to first 10 for readability
        goals_lines.append(f"- Address {f['id']}: {f['title']}")
    if len(selected) > 10:
        goals_lines.append(f"- ...and {len(selected) - 10} more findings")

    # Generate scope
    locations = set()
    for f in selected:
        loc = f['location'].split(':')[0] if ':' in f['location'] else f['location']
        locations.add(loc)
    in_scope_lines = [f"- {loc}" for loc in sorted(locations)[:15]]
    if len(locations) > 15:
        in_scope_lines.append(f"- ...and {len(locations) - 15} more files")

    # Generate key files table
    key_files_lines = []
    for loc in sorted(locations)[:10]:
        key_files_lines.append(f"| [TBD] | `{loc}` |")
    if not key_files_lines:
        key_files_lines.append("| [Name] | `path/to/file.py` |")

    # Create plan.md
    print(f"\nSTEP 2: Create project files")
    plan_content = PLAN_TEMPLATE.format(
        project_id=project_id,
        title=title,
        date=date_time,
        phase_table='\n'.join(phase_table_lines) if phase_table_lines else "| 1. TBD | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |",
        overview=f"Systematic remediation of findings from review: {review_name}. "
                 f"Total findings selected: {len(selected)} "
                 f"(Critical: {len(critical)}, Major: {len(major)}, Other: {len(other)}).",
        goals='\n'.join(goals_lines),
        in_scope='\n'.join(in_scope_lines),
        key_files='\n'.join(key_files_lines),
    )
    (project_dir / "plan.md").write_text(plan_content, encoding='utf-8')
    print(f"  Created: plan.md")

    # Create design.md with review findings
    findings_summary_lines = []
    for f in selected:
        severity = f.get('severity', 'Unknown')
        findings_summary_lines.append(f"### {f['id']}: {f['title']}")
        findings_summary_lines.append(f"- **Severity:** {severity}")
        findings_summary_lines.append(f"- **Location:** `{f['location']}`")
        findings_summary_lines.append(f"- **Effort:** {f['effort']}")
        findings_summary_lines.append("")

    design_content = DESIGN_TEMPLATE.format(
        project_id=project_id,
        review_name=review_name,
        review_link=f"../../Reviews/results/{review_name}/",
        review_type=parsed['review_type'],
        review_date=parsed['review_date'],
        report_link=f"../../Reviews/results/{review_name}/report.md",
        total_findings=len(all_findings),
        critical_count=len(critical),
        major_count=len(major),
        selected_count=len(selected),
        findings_summary='\n'.join(findings_summary_lines),
    )
    (project_dir / "design.md").write_text(design_content, encoding='utf-8')
    print(f"  Created: design.md")

    # Create decisions.md
    decisions_content = DECISIONS_TEMPLATE.format(
        project_id=project_id,
        date=date,
        total_findings=len(all_findings),
        selected_count=len(selected),
    )
    (project_dir / "decisions.md").write_text(decisions_content, encoding='utf-8')
    print(f"  Created: decisions.md")

    # Create phase checklist files
    for i, phase in enumerate(phases, 1):
        tasks_lines = []
        for j, f in enumerate(phase['findings'], 1):
            task = TASK_TEMPLATE.format(
                phase_num=i,
                task_num=j,
                finding_id=f['id'],
                title=f['title'],
                effort=f.get('effort', 'Medium'),
                location=f['location'],
            )
            tasks_lines.append(task)

        phase_content = PHASE_TEMPLATE.format(
            project_id=project_id,
            phase_num=i,
            phase_name=phase['name'],
            objective=phase['objective'],
            priority=phase['priority'],
            tasks='\n'.join(tasks_lines) if tasks_lines else "### Task {}.1: [Task Name] [Medium]\n**File:** `path/to/file.py`\n**Tests:** `pytest tests/`\n\n- [ ] Subtask\n\n**Notes:**".format(i),
        )
        (project_dir / f"phase_{i}_checklist.md").write_text(phase_content, encoding='utf-8')
        print(f"  Created: phase_{i}_checklist.md")

    # Update projects_index.md
    print(f"\nSTEP 3: Update projects_index.md")
    try:
        add_project_to_index(project_id, title, "Planning")
        print(f"  Added {project_id} to index")
    except Exception as e:
        print(f"  [WARN] Could not update index: {e}")
        print(f"         Please add manually to projects_index.md")

    return project_id, project_dir


def dry_run_report(review_folder: Path, selected_ids: list = None, title: str = None) -> None:
    """Show what would be parsed and created without making changes."""
    report_path = review_folder / "report.md"
    if not report_path.exists():
        print(f"ERROR: Report not found: {report_path}")
        return

    print("\n--- DRY RUN: No files will be created ---\n")

    # Parse report
    parsed = parse_report(report_path)
    all_findings = parsed['findings']

    print(f"Report Type: {parsed['review_type']}")
    print(f"Report Date: {parsed['review_date']}")

    # Show parsing summary
    print_parsing_summary(all_findings)

    # Validate
    is_valid, warnings, errors = validate_parsed_findings(all_findings)
    if errors:
        print("\n[ERRORS]:")
        for err in errors:
            print(f"  - {err}")
    if warnings:
        print("\n[WARNINGS]:")
        for warn in warnings:
            print(f"  - {warn}")

    # Show what would be filtered
    selected = filter_findings(all_findings, selected_ids)
    if not selected:
        selected = filter_findings(all_findings, None)

    print(f"\n  Would select {len(selected)} findings for project:")

    # Group by severity
    by_sev = {}
    for f in selected:
        sev = f.get('severity', 'Unknown')
        by_sev.setdefault(sev, []).append(f)

    for sev in ['Critical', 'Major', 'Minor', 'Info', 'Unknown']:
        findings = by_sev.get(sev, [])
        if findings:
            print(f"\n  {sev} ({len(findings)}):")
            for f in findings[:5]:
                print(f"    - {f['id']}: {f['title'][:50]}...")
            if len(findings) > 5:
                print(f"    ... and {len(findings) - 5} more")

    # Show what phases would be created
    critical = [f for f in selected if f.get('severity') == 'Critical']
    major = [f for f in selected if f.get('severity') == 'Major']
    other = [f for f in selected if f.get('severity') not in ('Critical', 'Major')]

    print("\n  Would create phases:")
    phase_num = 0
    if critical:
        phase_num += 1
        print(f"    Phase {phase_num}: Critical Fixes ({len(critical)} tasks)")
    if major:
        phase_num += 1
        print(f"    Phase {phase_num}: Major Issues ({len(major)} tasks)")
    if other:
        phase_num += 1
        print(f"    Phase {phase_num}: Cleanup ({len(other)} tasks)")

    # Generate title
    review_name = review_folder.name
    if title is None:
        parts = review_name.split('_')
        if len(parts) >= 3:
            review_type_short = parts[1]
            description = ' '.join(parts[2:]).replace('-', ' ').title()
            title = f"{review_type_short.title()} Remediation: {description}"
        else:
            title = f"Review Remediation: {review_name}"

    print(f"\n  Would create project with title: {title}")
    print("\n--- END DRY RUN ---")


def main():
    parser = argparse.ArgumentParser(
        description='Create a project from review findings with full directory structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Create project automatically (default)
    python review_to_project.py 2026-01-23_general_game-logic

    # Create project with custom title
    python review_to_project.py 2026-01-23_security_api --title "Security Fixes"

    # Select specific findings
    python review_to_project.py 2026-01-23_security_api --findings SEC-01,SEC-02,IV-01

    # Generate handoff document only (no project creation)
    python review_to_project.py 2026-01-23_general_game-logic --no-create-project

    # Dry run - show what would be parsed without creating files
    python review_to_project.py 2026-01-23_general_game-logic --dry-run

If --findings is not specified, all Critical and Major findings are used.
        """
    )
    parser.add_argument('review_folder',
                        help='Review folder name or path')
    parser.add_argument('--findings', '-f',
                        help='Comma-separated list of finding IDs to include')
    parser.add_argument('--title', '-t',
                        help='Custom project title (default: auto-generated from review name)')
    parser.add_argument('--create-project', dest='create_project',
                        action='store_true', default=True,
                        help='Create full project structure (default)')
    parser.add_argument('--no-create-project', dest='create_project',
                        action='store_false',
                        help='Generate handoff document only, do not create project')
    parser.add_argument('--dry-run', '-n',
                        action='store_true',
                        help='Show what would be parsed without creating any files')

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

    # Handle dry-run mode
    if args.dry_run:
        print(f"\n{'=' * 60}")
        print("DRY RUN: Analyzing Report")
        print('=' * 60)
        print(f"\nReview: {folder_path.name}")
        dry_run_report(folder_path, selected_ids, args.title)
        sys.exit(0)

    print(f"\n{'=' * 60}")
    if args.create_project:
        print("Creating Project from Review Findings")
    else:
        print("Generating Project Handoff (no project creation)")
    print('=' * 60)
    print(f"\nReview: {folder_path.name}")
    if selected_ids:
        print(f"Selected findings: {', '.join(selected_ids)}")
    else:
        print("Selected findings: All Critical and Major")

    if args.create_project:
        # Create full project structure
        if not HAS_PROJECT_UTILS:
            print("\nERROR: Projects utilities not available.")
            print("       Make sure Projects/scripts/utils/ exists.")
            print("       Or use --no-create-project for handoff-only mode.")
            sys.exit(1)

        project_id, project_dir = create_project_from_review(
            folder_path,
            selected_ids,
            args.title
        )

        print(f"\n{'=' * 60}")
        print("PROJECT CREATED SUCCESSFULLY")
        print('=' * 60)
        print(f"\n  Project ID:  {project_id}")
        print(f"  Directory:   {project_dir}")
        print(f"\n  Files created:")
        print(f"    - plan.md")
        print(f"    - design.md (with review findings)")
        print(f"    - decisions.md")
        print(f"    - phase_N_checklist.md files")
        print(f"    - findings/ directory")
        print(f"\nNext steps:")
        print(f"  1. Review the generated plan.md")
        print(f"  2. Run 'Continue Project' prompt with {project_id}")
        print(f"  3. Or manually refine the phase checklists first")
        print('=' * 60)

    else:
        # Legacy handoff-only mode
        handoff = generate_handoff(folder_path, selected_ids)

        # Write handoff document
        handoff_file = folder_path / "project_handoff.md"
        handoff_file.write_text(handoff, encoding='utf-8')

        print(f"\n{'=' * 60}")
        print("HANDOFF GENERATED")
        print('=' * 60)
        print(f"\n  File: {handoff_file}")
        print(f"\nNext steps:")
        print(f"  1. Review and edit the handoff document")
        print(f"  2. Run 'Start Project' prompt with the handoff as context")
        print(f"  3. Or use: python Projects/scripts/create_project.py \"<title>\"")
        print('=' * 60)


if __name__ == '__main__':
    main()
