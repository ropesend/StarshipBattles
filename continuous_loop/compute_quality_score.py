#!/usr/bin/env python3
"""
Compute quality scores for a sweep cycle and append to the archive.

Reads findings from a sweep review folder, computes a 0-100 quality score
(overall + per-shard), and appends the result to quality_scores.jsonl.

Usage:
    python continuous_loop/compute_quality_score.py <review_folder>
    python continuous_loop/compute_quality_score.py <review_folder> --cycle 3
    python continuous_loop/compute_quality_score.py Reviews/results/2026-02-11_sweep_full-codebase-sweep

Called by SWEEP_WORKER.md after Step 11 (scaffold prospective projects).
"""

import argparse
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
QUALITY_SCORES_FILE = WORKSPACE / "continuous_loop" / "quality_scores.jsonl"
RESULTS_DIR = WORKSPACE / "Reviews" / "results"

# ═══════════════════════════════════════════════════════
# SCORING FORMULA
# ═══════════════════════════════════════════════════════

SEVERITY_WEIGHTS = {
    'Critical': 10.0,
    'Major': 3.0,
    'Minor': 1.0,
    'Info': 0.2,
}
DECAY_CONSTANT = 0.5

GRADE_THRESHOLDS = [
    (90, "Excellent"),
    (75, "Good"),
    (60, "Fair"),
    (40, "Needs Improvement"),
    (20, "Poor"),
    (0, "Critical"),
]

# Shard directory definitions (must match SWEEP_WORKER.md)
SHARD_DIRS = {
    'FND': ['game/core/', 'game/ai/', 'game/research/', 'game/engine/'],
    'SIM': ['game/simulation/'],
    'STR': ['game/strategy/'],
    'UI1': ['game/ui/screens/', 'game/ui/panels/'],
    'UI2': ['game/ui/'],
}
UI2_EXCLUDE_PREFIXES = ['game/ui/screens/', 'game/ui/panels/']

SHARD_ORDER = ['FND', 'SIM', 'STR', 'UI1', 'UI2']


def compute_score(critical, major, minor, info, file_count):
    """Compute 0-100 quality score from finding counts.

    Returns (score, demerits_per_file).
    """
    weighted = (
        critical * SEVERITY_WEIGHTS['Critical']
        + major * SEVERITY_WEIGHTS['Major']
        + minor * SEVERITY_WEIGHTS['Minor']
        + info * SEVERITY_WEIGHTS['Info']
    )
    dpf = weighted / max(file_count, 1)
    raw = 100 * math.exp(-DECAY_CONSTANT * dpf)
    return max(0, min(100, round(raw))), round(dpf, 2)


def grade_label(score):
    """Map score to human-readable grade."""
    for threshold, label in GRADE_THRESHOLDS:
        if score >= threshold:
            return label
    return "Critical"


# ═══════════════════════════════════════════════════════
# FILE COUNTING
# ═══════════════════════════════════════════════════════

def count_shard_files(shard_id):
    """Count .py files belonging to a shard."""
    total = 0
    for d in SHARD_DIRS[shard_id]:
        dir_path = WORKSPACE / d
        if not dir_path.exists():
            continue
        for py_file in dir_path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            if shard_id == 'UI2':
                rel = py_file.relative_to(WORKSPACE).as_posix()
                if any(rel.startswith(ex) for ex in UI2_EXCLUDE_PREFIXES):
                    continue
            total += 1
    return total


def count_all_files():
    """Count total .py files across all shards."""
    return sum(count_shard_files(sid) for sid in SHARD_ORDER)


# ═══════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════

def load_overall_stats(review_folder):
    """Parse report.md Executive Summary for severity counts."""
    report = review_folder / 'report.md'
    if not report.exists():
        print(f"ERROR: report.md not found in {review_folder}")
        return None

    content = report.read_text(encoding='utf-8')

    total_match = re.search(r'\*\*Total Findings:\*\*\s*(\d+)', content)
    severity_line = re.search(
        r'\*\*Critical:\*\*\s*(\d+)\s*\|\s*\*\*Major:\*\*\s*(\d+)\s*\|\s*'
        r'\*\*Minor:\*\*\s*(\d+)\s*\|\s*\*\*Info:\*\*\s*(\d+)',
        content
    )

    if not severity_line:
        print("ERROR: Could not parse severity counts from report.md")
        return None

    stats = {
        'critical': int(severity_line.group(1)),
        'major': int(severity_line.group(2)),
        'minor': int(severity_line.group(3)),
        'info': int(severity_line.group(4)),
    }
    stats['total'] = int(total_match.group(1)) if total_match else sum(stats.values())
    return stats


def load_findings_by_shard(review_folder):
    """Load per-shard finding counts from all_findings.json."""
    findings_file = review_folder / 'prospective_projects' / 'all_findings.json'
    if not findings_file.exists():
        return None

    data = json.loads(findings_file.read_text(encoding='utf-8'))
    by_shard = {}
    for f in data:
        shard = f.get('shard', 'UNK')
        if shard == 'UNK':
            continue
        if shard not in by_shard:
            by_shard[shard] = {
                'Critical': 0, 'Major': 0, 'Minor': 0, 'Info': 0, 'total': 0
            }
        sev = f.get('severity', 'Info')
        if sev not in by_shard[shard]:
            sev = 'Info'
        by_shard[shard][sev] += 1
        by_shard[shard]['total'] += 1
    return by_shard


def load_findings_by_shard_from_report(review_folder):
    """Fallback: extract per-shard counts from report.md finding IDs."""
    report = review_folder / 'report.md'
    if not report.exists():
        return None

    content = report.read_text(encoding='utf-8')
    by_shard = {}

    # Match finding blocks: #### SEVERITY: Title\n**ID:** XXX-YYY-NNN
    finding_pattern = re.compile(
        r'####\s+(Critical|Major|Minor|Info):\s+.+?\n\*\*ID:\*\*\s+(\S+)',
        re.IGNORECASE
    )

    known_shards = set(SHARD_ORDER)
    for match in finding_pattern.finditer(content):
        severity = match.group(1).capitalize()
        if severity == 'Critical':
            pass
        elif severity == 'Major':
            pass
        elif severity == 'Minor':
            pass
        else:
            severity = 'Info'

        finding_id = match.group(2)
        parts = finding_id.split('-')
        shard = parts[1] if len(parts) >= 2 and parts[1] in known_shards else 'UNK'
        if shard == 'UNK':
            continue

        if shard not in by_shard:
            by_shard[shard] = {
                'Critical': 0, 'Major': 0, 'Minor': 0, 'Info': 0, 'total': 0
            }
        by_shard[shard][severity] += 1
        by_shard[shard]['total'] += 1

    return by_shard if by_shard else None


def load_validation_summary(review_folder):
    """Load validation_summary.json if it exists."""
    vs_file = review_folder / 'validation' / 'validation_summary.json'
    if not vs_file.exists():
        return None
    return json.loads(vs_file.read_text(encoding='utf-8'))


def load_previous_scores():
    """Load the last entry from quality_scores.jsonl."""
    if not QUALITY_SCORES_FILE.exists():
        return None
    content = QUALITY_SCORES_FILE.read_text(encoding='utf-8').strip()
    if not content:
        return None
    lines = content.splitlines()
    for line in reversed(lines):
        line = line.strip()
        if line:
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return None


# ═══════════════════════════════════════════════════════
# OUTPUT FORMATTING
# ═══════════════════════════════════════════════════════

def format_summary_line(result):
    """Format the single-line human-readable summary."""
    o = result['overall']
    delta_str = ""
    if o['delta'] is not None:
        sign = "+" if o['delta'] >= 0 else ""
        delta_str = f" [{sign}{o['delta']}]"

    shard_parts = []
    for sid in SHARD_ORDER:
        if sid not in result['shards']:
            continue
        s = result['shards'][sid]
        sd = ""
        if s['delta'] is not None:
            sign = "+" if s['delta'] >= 0 else ""
            sd = f"({sign}{s['delta']})"
        shard_parts.append(f"{sid}:{s['score']}{sd}")

    shards_str = " ".join(shard_parts)

    return (
        f"Quality: {o['score']}/100 ({o['grade']}){delta_str} | "
        f"{shards_str} | "
        f"{o['findings']} findings "
        f"({o['critical']}C/{o['major']}M/{o['minor']}m/{o['info']}I) | "
        f"{result['file_count']} files"
    )


# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Compute quality scores for a sweep cycle'
    )
    parser.add_argument(
        'review_folder',
        help='Review folder name or full path',
    )
    parser.add_argument(
        '--cycle', type=int, default=None,
        help='Cycle number (auto-increments from previous if omitted)',
    )
    args = parser.parse_args()

    # Resolve folder path
    folder_path = Path(args.review_folder)
    if not folder_path.is_absolute():
        candidate = RESULTS_DIR / args.review_folder
        if candidate.exists():
            folder_path = candidate
        elif not folder_path.exists():
            print(f"ERROR: Review folder not found: {args.review_folder}")
            sys.exit(1)

    if not folder_path.exists():
        print(f"ERROR: Review folder not found: {folder_path}")
        sys.exit(1)

    # Load data
    overall_stats = load_overall_stats(folder_path)
    if not overall_stats:
        sys.exit(1)

    shard_findings = load_findings_by_shard(folder_path)
    if not shard_findings:
        shard_findings = load_findings_by_shard_from_report(folder_path)
    if not shard_findings:
        print("WARNING: No per-shard data available. Only overall score computed.")
        shard_findings = {}

    validation = load_validation_summary(folder_path)
    previous = load_previous_scores()

    # Determine cycle number
    cycle = args.cycle
    if cycle is None:
        cycle = (previous['cycle'] + 1) if previous else 1

    # Count files
    total_files = count_all_files()
    if total_files == 0:
        print("ERROR: No Python files found under game/")
        sys.exit(1)

    # Compute overall score
    overall_score, overall_dpf = compute_score(
        overall_stats['critical'],
        overall_stats['major'],
        overall_stats['minor'],
        overall_stats['info'],
        total_files,
    )

    prev_overall = previous['overall']['score'] if previous else None
    overall_delta = overall_score - prev_overall if prev_overall is not None else None

    # Compute per-shard scores
    shards_result = {}
    for sid in SHARD_ORDER:
        shard_files = count_shard_files(sid)
        if shard_files == 0:
            continue

        sf = shard_findings.get(sid, {
            'Critical': 0, 'Major': 0, 'Minor': 0, 'Info': 0, 'total': 0
        })

        s_score, _ = compute_score(
            sf.get('Critical', 0),
            sf.get('Major', 0),
            sf.get('Minor', 0),
            sf.get('Info', 0),
            shard_files,
        )

        prev_shard_score = None
        if previous and 'shards' in previous and sid in previous['shards']:
            prev_shard_score = previous['shards'][sid]['score']

        delta = s_score - prev_shard_score if prev_shard_score is not None else None

        shards_result[sid] = {
            'score': s_score,
            'grade': grade_label(s_score),
            'files': shard_files,
            'findings': sf.get('total', 0),
            'critical': sf.get('Critical', 0),
            'major': sf.get('Major', 0),
            'minor': sf.get('Minor', 0),
            'info': sf.get('Info', 0),
            'delta': delta,
        }

    # Build result
    result = {
        'cycle': cycle,
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'review_folder': folder_path.name,
        'file_count': total_files,
        'overall': {
            'score': overall_score,
            'grade': grade_label(overall_score),
            'findings': overall_stats['total'],
            'critical': overall_stats['critical'],
            'major': overall_stats['major'],
            'minor': overall_stats['minor'],
            'info': overall_stats['info'],
            'demerits_per_file': overall_dpf,
            'delta': overall_delta,
        },
        'shards': shards_result,
        'validation': {
            'original_count': validation.get('original_count'),
            'confirmed': validation.get('confirmed'),
            'downgraded': validation.get('downgraded'),
            'rejected': validation.get('rejected'),
            'rejection_rate_pct': validation.get('rejection_rate_pct'),
        } if validation else None,
    }

    # Append to JSONL archive
    QUALITY_SCORES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUALITY_SCORES_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False) + '\n')

    # Print summary
    summary = format_summary_line(result)
    print(summary)

    return 0


if __name__ == '__main__':
    sys.exit(main())
