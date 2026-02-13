#!/usr/bin/env python3
"""
Filter a compiled sweep report using validation verdicts.

Reads 5 per-shard validation reports from the validation/ subdirectory,
applies CONFIRMED/DOWNGRADED/REJECTED verdicts to findings in report.md,
and writes a filtered report.md (original saved as report_unvalidated.md).

Usage:
    python filter_validated_findings.py <review_folder>

Examples:
    python filter_validated_findings.py 2026-02-12_sweep_full-codebase-sweep
    python filter_validated_findings.py Reviews/results/2026-02-12_sweep_full-codebase-sweep
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import RESULTS_DIR, SEVERITY_LEVELS

# Shard IDs that validators produce reports for
SHARD_IDS = ['FND', 'SIM', 'STR', 'UI1', 'UI2']


def parse_validation_report(content: str) -> dict:
    """Parse a single validation report into a dict of finding_id -> verdict.

    Returns dict with:
        verdicts: {finding_id: {verdict, new_severity, reason, duplicate_of}}
        cross_shard_duplicates: [(this_id, duplicate_of_id, reason)]
        summary: {reviewed, confirmed, downgraded, rejected}
    """
    verdicts = {}
    cross_shard_duplicates = []

    # Parse individual finding verdicts
    # Pattern: #### Finding: {ID}
    finding_blocks = re.split(r'####\s+Finding:\s*', content)

    for block in finding_blocks[1:]:  # skip preamble before first finding
        # Extract finding ID (first line or first word)
        id_match = re.match(r'(\S+)', block.strip())
        if not id_match:
            continue
        finding_id = id_match.group(1).rstrip('*').strip()

        # Extract verdict
        verdict_match = re.search(
            r'\*\*Verdict:\*\*\s*(CONFIRMED|DOWNGRADED\([^)]+\)|REJECTED)',
            block
        )
        if not verdict_match:
            continue

        verdict_raw = verdict_match.group(1)

        # Parse verdict type
        if verdict_raw == 'CONFIRMED':
            verdict_type = 'CONFIRMED'
            new_severity = None
        elif verdict_raw.startswith('DOWNGRADED'):
            verdict_type = 'DOWNGRADED'
            sev_match = re.search(r'DOWNGRADED\((\w+)\)', verdict_raw)
            new_severity = sev_match.group(1) if sev_match else None
        else:
            verdict_type = 'REJECTED'
            new_severity = None

        # Extract new severity (explicit field, takes precedence)
        new_sev_match = re.search(
            r'\*\*New Severity:\*\*\s*(\w+)', block
        )
        if new_sev_match:
            new_severity = new_sev_match.group(1)

        # Extract reason
        reason_match = re.search(
            r'\*\*Reason:\*\*\s*(.+?)(?=\n\*\*|\n####|\n##|\Z)',
            block, re.DOTALL
        )
        reason = reason_match.group(1).strip() if reason_match else ''

        # Extract duplicate reference
        dup_match = re.search(
            r'\*\*Duplicate Of:\*\*\s*(\S+)', block
        )
        duplicate_of = dup_match.group(1) if dup_match else None

        verdicts[finding_id] = {
            'verdict': verdict_type,
            'new_severity': new_severity,
            'reason': reason,
            'duplicate_of': duplicate_of,
        }

    # Parse cross-shard duplicate table
    table_match = re.search(
        r'## Cross-Shard Duplicates\s*\n(.*?)(?=\n##|\Z)',
        content, re.DOTALL
    )
    if table_match:
        table_text = table_match.group(1)
        # Parse table rows: | this_id | other_id | reason |
        for row_match in re.finditer(
            r'\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(.+?)\s*\|',
            table_text
        ):
            this_id = row_match.group(1).strip()
            other_id = row_match.group(2).strip()
            reason = row_match.group(3).strip()
            # Skip header row
            if this_id in ('This Finding', '---', '-'):
                continue
            cross_shard_duplicates.append((this_id, other_id, reason))

    # Parse summary counts
    summary = {
        'reviewed': len(verdicts),
        'confirmed': sum(
            1 for v in verdicts.values() if v['verdict'] == 'CONFIRMED'
        ),
        'downgraded': sum(
            1 for v in verdicts.values() if v['verdict'] == 'DOWNGRADED'
        ),
        'rejected': sum(
            1 for v in verdicts.values() if v['verdict'] == 'REJECTED'
        ),
    }

    return {
        'verdicts': verdicts,
        'cross_shard_duplicates': cross_shard_duplicates,
        'summary': summary,
    }


def load_validation_reports(validation_dir: Path) -> dict:
    """Load all validation reports from the validation/ directory.

    Returns combined dict of all verdicts, cross-shard duplicates, and
    per-shard summaries.
    """
    all_verdicts = {}
    all_cross_shard = []
    by_shard = {}

    for shard_id in SHARD_IDS:
        report_file = validation_dir / f'validation_{shard_id.lower()}_report.md'
        if not report_file.exists():
            # Try alternate naming
            report_file = validation_dir / f'validation_{shard_id}_report.md'

        if not report_file.exists():
            print(f"  [WARNING] Validation report missing: {report_file.name}")
            by_shard[shard_id] = {
                'reviewed': 0, 'confirmed': 0,
                'downgraded': 0, 'rejected': 0,
            }
            continue

        content = report_file.read_text(encoding='utf-8')
        parsed = parse_validation_report(content)

        all_verdicts.update(parsed['verdicts'])
        all_cross_shard.extend(parsed['cross_shard_duplicates'])
        by_shard[shard_id] = parsed['summary']

        print(
            f"  {shard_id}: {parsed['summary']['reviewed']} reviewed, "
            f"{parsed['summary']['confirmed']} confirmed, "
            f"{parsed['summary']['downgraded']} downgraded, "
            f"{parsed['summary']['rejected']} rejected"
        )

    return {
        'verdicts': all_verdicts,
        'cross_shard_duplicates': all_cross_shard,
        'by_shard': by_shard,
    }


def resolve_cross_shard_duplicates(
    cross_shard: list, verdicts: dict
) -> set:
    """Resolve cross-shard duplicate clusters.

    For each duplicate pair, keep the finding with the lowest ID
    (alphabetically) and mark the other for rejection.

    Returns set of finding IDs to reject as cross-shard duplicates.
    """
    reject_ids = set()

    # Build duplicate clusters
    clusters = defaultdict(set)
    for this_id, other_id, _reason in cross_shard:
        # Create a cluster key from the pair
        cluster_key = tuple(sorted([this_id, other_id]))
        clusters[cluster_key].add(this_id)
        clusters[cluster_key].add(other_id)

    # For each cluster, keep the lowest ID
    for _key, members in clusters.items():
        sorted_members = sorted(members)
        # Keep first (lowest), reject rest
        for member in sorted_members[1:]:
            # Only reject if not already rejected by its own validator
            if member in verdicts:
                if verdicts[member]['verdict'] != 'REJECTED':
                    reject_ids.add(member)
            else:
                reject_ids.add(member)

    return reject_ids


def parse_report_findings(report_content: str) -> list:
    """Parse findings from report.md using the same format as compile_findings.

    Returns list of dicts with all finding metadata preserved.
    """
    from compile_findings import parse_finding

    # The report has two sections with findings:
    # 1. "Priority Findings (Top 10)" - detailed format
    # 2. "Findings by Severity" - table format
    # We need to parse from the agent report files directly,
    # but since we're working with report.md, we extract from tables.

    findings = []

    # Parse from "Findings by Severity" tables
    # Format: | ID | Title | Location | Effort |
    for severity in SEVERITY_LEVELS:
        section_match = re.search(
            rf'### {severity} \(\d+\)\n'
            r'\| ID \| Title \| Location \| Effort \|\n'
            r'\|[-|]+\|\n'
            r'((?:\|.+\|\n)*)',
            report_content
        )
        if not section_match:
            continue

        table_rows = section_match.group(1)
        for row_match in re.finditer(
            r'\|\s*(\S+)\s*\|\s*(.+?)\s*\|\s*`([^`]*)`\s*\|\s*(\w+)\s*\|',
            table_rows
        ):
            findings.append({
                'id': row_match.group(1).strip(),
                'title': row_match.group(2).strip(),
                'location': row_match.group(3).strip(),
                'effort': row_match.group(4).strip(),
                'severity': severity,
            })

    return findings


def apply_verdicts(
    findings: list,
    verdicts: dict,
    cross_shard_rejects: set,
) -> tuple:
    """Apply validation verdicts to findings.

    Returns (filtered_findings, stats) where filtered_findings excludes
    rejected findings and has severity updated for downgraded ones.
    """
    filtered = []
    no_verdict_count = 0
    rejected_ids = []
    downgraded_ids = {}

    for finding in findings:
        fid = finding['id']

        # Cross-shard duplicate rejection takes priority
        if fid in cross_shard_rejects:
            rejected_ids.append(fid)
            continue

        verdict_info = verdicts.get(fid)

        if verdict_info is None:
            # No verdict — validator missed this finding, keep as-is
            no_verdict_count += 1
            filtered.append(finding)
            continue

        if verdict_info['verdict'] == 'REJECTED':
            rejected_ids.append(fid)
            continue

        if verdict_info['verdict'] == 'DOWNGRADED':
            new_sev = verdict_info.get('new_severity')
            if new_sev and new_sev in SEVERITY_LEVELS:
                finding = dict(finding)  # copy to avoid mutating original
                finding['severity'] = new_sev
                downgraded_ids[fid] = new_sev

        filtered.append(finding)

    stats = {
        'original_count': len(findings),
        'confirmed': len(filtered) - no_verdict_count,
        'downgraded': len(downgraded_ids),
        'rejected': len(rejected_ids),
        'no_verdict': no_verdict_count,
        'filtered_count': len(filtered),
        'rejected_ids': rejected_ids,
        'downgraded_ids': downgraded_ids,
    }

    return filtered, stats


def generate_filtered_report(
    original_report: str,
    filtered_findings: list,
    stats: dict,
    review_folder: Path,
) -> str:
    """Regenerate report.md with only filtered findings.

    Reuses the compile_findings.generate_report() approach but with
    filtered data.
    """
    from compile_findings import generate_report

    # Build a compiled dict in the format generate_report expects
    by_severity = defaultdict(list)
    for f in filtered_findings:
        # generate_report expects 'content' and 'agent' fields
        if 'content' not in f:
            f['content'] = f"**Location:** `{f.get('location', 'Unknown')}`"
        if 'agent' not in f:
            f['agent'] = 'Validated'
        by_severity[f['severity']].append(f)

    compiled = {
        'findings': filtered_findings,
        'by_severity': dict(by_severity),
        'by_agent': {},
        'stats': {
            'total': len(filtered_findings),
            'critical': len(by_severity.get('Critical', [])),
            'major': len(by_severity.get('Major', [])),
            'minor': len(by_severity.get('Minor', [])),
            'info': len(by_severity.get('Info', [])),
            'agents': 25,
            'agents_with_findings': 0,
            'empty_agents': 0,
        },
    }

    report = generate_report(review_folder, compiled)

    # Inject validation summary after Executive Summary
    validation_note = (
        f"\n### Validation Summary\n"
        f"- **Original Findings:** {stats['original_count']}\n"
        f"- **Confirmed:** "
        f"{stats['confirmed']} | "
        f"**Downgraded:** {stats['downgraded']} | "
        f"**Rejected:** {stats['rejected']}\n"
        f"- **Rejection Rate:** "
        f"{stats['rejected'] / max(stats['original_count'], 1) * 100:.1f}%\n"
        f"- **Findings Without Verdict:** {stats['no_verdict']}\n"
    )

    # Insert after "## Executive Summary" section
    insert_point = report.find('\n## Priority Findings')
    if insert_point == -1:
        insert_point = report.find('\n## Findings by Severity')
    if insert_point != -1:
        report = report[:insert_point] + validation_note + report[insert_point:]

    return report


def write_validation_summary(
    validation_dir: Path,
    stats: dict,
    by_shard: dict,
) -> None:
    """Write machine-readable validation_summary.json."""
    summary = {
        'original_count': stats['original_count'],
        'confirmed': stats['confirmed'],
        'downgraded': stats['downgraded'],
        'rejected': stats['rejected'],
        'no_verdict': stats['no_verdict'],
        'filtered_count': stats['filtered_count'],
        'rejection_rate_pct': round(
            stats['rejected'] / max(stats['original_count'], 1) * 100, 1
        ),
        'by_shard': by_shard,
        'rejected_ids': stats['rejected_ids'],
        'downgraded_ids': stats['downgraded_ids'],
    }

    summary_file = validation_dir / 'validation_summary.json'
    summary_file.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding='utf-8',
    )
    print(f"  Written: {summary_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Filter compiled report using validation verdicts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python filter_validated_findings.py 2026-02-12_sweep_full-codebase-sweep
    python filter_validated_findings.py Reviews/results/2026-02-12_sweep_full-codebase-sweep
        """
    )
    parser.add_argument(
        'review_folder',
        help='Review folder name or path',
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

    report_file = folder_path / 'report.md'
    validation_dir = folder_path / 'validation'

    print(f"\n{'=' * 50}")
    print(f"Filtering Validated Findings: {folder_path.name}")
    print('=' * 50)

    # Verify inputs exist
    if not report_file.exists():
        print(f"ERROR: report.md not found in {folder_path}")
        sys.exit(1)

    if not validation_dir.exists():
        print(f"ERROR: validation/ directory not found in {folder_path}")
        sys.exit(1)

    # Step 1: Load validation reports
    print("\nStep 1: Loading validation reports...")
    validation_data = load_validation_reports(validation_dir)
    verdicts = validation_data['verdicts']
    print(f"  Total verdicts loaded: {len(verdicts)}")

    # Safety check: warn if any shard has >90% rejection rate
    for shard_id, shard_stats in validation_data['by_shard'].items():
        if shard_stats['reviewed'] > 0:
            rejection_rate = (
                shard_stats['rejected'] / shard_stats['reviewed'] * 100
            )
            if rejection_rate > 90:
                print(
                    f"  [WARNING] Shard {shard_id} has "
                    f"{rejection_rate:.0f}% rejection rate — "
                    f"validator may be too aggressive"
                )

    # Step 2: Resolve cross-shard duplicates
    print("\nStep 2: Resolving cross-shard duplicates...")
    cross_shard_rejects = resolve_cross_shard_duplicates(
        validation_data['cross_shard_duplicates'],
        verdicts,
    )
    if cross_shard_rejects:
        print(
            f"  {len(cross_shard_rejects)} cross-shard "
            f"duplicate(s) will be rejected"
        )
    else:
        print("  No cross-shard duplicates to resolve")

    # Step 3: Parse existing report.md
    print("\nStep 3: Parsing report.md...")
    report_content = report_file.read_text(encoding='utf-8')
    findings = parse_report_findings(report_content)
    print(f"  Parsed {len(findings)} findings from report.md")

    if not findings:
        print("ERROR: No findings could be parsed from report.md")
        sys.exit(1)

    # Step 4: Apply verdicts
    print("\nStep 4: Applying validation verdicts...")
    filtered_findings, stats = apply_verdicts(
        findings, verdicts, cross_shard_rejects
    )

    print(f"  Original:   {stats['original_count']}")
    print(f"  Confirmed:  {stats['confirmed']}")
    print(f"  Downgraded: {stats['downgraded']}")
    print(f"  Rejected:   {stats['rejected']}")
    print(f"  No verdict: {stats['no_verdict']}")
    print(f"  Remaining:  {stats['filtered_count']}")
    print(
        f"  Rejection rate: "
        f"{stats['rejected'] / max(stats['original_count'], 1) * 100:.1f}%"
    )

    # Step 5: Save original report, write filtered
    print("\nStep 5: Writing filtered report...")
    backup_file = folder_path / 'report_unvalidated.md'
    backup_file.write_text(report_content, encoding='utf-8')
    print(f"  Saved original as: {backup_file.name}")

    filtered_report = generate_filtered_report(
        report_content, filtered_findings, stats, folder_path
    )
    report_file.write_text(filtered_report, encoding='utf-8')
    print(f"  Written filtered: {report_file.name}")

    # Step 6: Write validation summary JSON
    print("\nStep 6: Writing validation summary...")
    write_validation_summary(
        validation_dir, stats, validation_data['by_shard']
    )

    # Final summary
    print(f"\n{'=' * 50}")
    print("VALIDATION FILTERING COMPLETE")
    print(
        f"  {stats['original_count']} -> {stats['filtered_count']} findings "
        f"({stats['rejected']} rejected, "
        f"{stats['downgraded']} downgraded)"
    )
    print('=' * 50)


if __name__ == '__main__':
    main()
