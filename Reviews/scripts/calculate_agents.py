#!/usr/bin/env python3
"""
Calculate recommended agent count for a review based on scope.

Usage:
    python calculate_agents.py <scope_path> <review_type>

Examples:
    python calculate_agents.py game/strategy general
    python calculate_agents.py tests/ test-coverage
    python calculate_agents.py . security
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import VALID_REVIEW_TYPES, REVIEW_TYPE_NAMES, AGENT_SCALING

# Agent recommendations by review type
REVIEW_TYPE_AGENTS = {
    "general": {
        "required": ["Code Quality Analyst", "Architecture Reviewer", "Test Coverage Analyst"],
        "recommended": ["Error Handling Auditor", "Dead Code Hunter"],
        "optional": ["Documentation Reviewer", "Security Auditor", "Performance Profiler"],
    },
    "test-coverage": {
        "required": ["Test Coverage Analyst", "Test Behavior Analyst"],
        "recommended": [],
        "optional": ["Architecture Reviewer", "Code Quality Analyst"],
        "scalable": "Module Specialist",  # Add more of these for large test suites
    },
    "focused": {
        "required": ["Question Investigator"],
        "recommended": [],
        "optional": ["Error Handling Auditor", "Data Flow Tracer", "Architecture Reviewer", "Module Specialist"],
    },
    "migration": {
        "required": ["Migration Analyst", "Architecture Reviewer", "Dependency Mapper", "Test Impact Analyst"],
        "recommended": ["Code Quality Analyst", "Data Flow Tracer"],
        "optional": ["Performance Profiler", "Security Auditor"],
    },
    "security": {
        "required": ["Security Auditor", "Input Validation Analyst", "Auth/Access Reviewer"],
        "recommended": ["Data Flow Tracer", "Error Handling Auditor"],
        "optional": ["Code Quality Analyst", "Architecture Reviewer"],
    },
    "performance": {
        "required": ["Performance Profiler", "Algorithm Analyst"],
        "recommended": ["Memory/Resource Analyst", "Hot Path Identifier"],
        "optional": ["Data Flow Tracer", "Architecture Reviewer"],
    },
    "tech-debt": {
        "required": ["Debt Cataloguer", "Complexity Analyst", "Maintenance Cost Estimator"],
        "recommended": ["Refactoring Opportunity Finder", "Code Quality Analyst"],
        "optional": ["Architecture Reviewer", "Test Coverage Analyst"],
    },
    "consistency": {
        "required": ["Pattern Cataloguer", "Inconsistency Hunter"],
        "recommended": ["Style Analyzer", "Convention Enforcer"],
        "optional": ["Code Quality Analyst", "Architecture Reviewer"],
    },
}


def count_files(scope_path: Path, extensions: list = None) -> dict:
    """Count files in scope and return stats."""
    if extensions is None:
        extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs']

    stats = {
        'total_files': 0,
        'total_lines': 0,
        'by_extension': {},
    }

    if not scope_path.exists():
        return stats

    for ext in extensions:
        files = list(scope_path.rglob(f'*{ext}'))
        if files:
            stats['by_extension'][ext] = len(files)
            stats['total_files'] += len(files)

            # Count lines (sample if too many)
            sample_files = files[:50] if len(files) > 50 else files
            for f in sample_files:
                try:
                    stats['total_lines'] += len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
                except OSError:
                    pass

            # Extrapolate if sampled
            if len(files) > 50:
                stats['total_lines'] = int(stats['total_lines'] * len(files) / 50)

    return stats


def determine_scope_size(stats: dict) -> str:
    """Determine scope size category."""
    files = stats['total_files']

    if files <= 20:
        return 'small'
    elif files <= 100:
        return 'medium'
    elif files <= 500:
        return 'large'
    else:
        return 'comprehensive'


def calculate_agents(scope_path: Path, review_type: str) -> dict:
    """Calculate recommended agent configuration.

    Returns a dict with:
    - scope_stats: file/line counts
    - scope_size: small/medium/large/comprehensive
    - recommended_count: total agent count
    - agents: list of recommended agents
    """
    # Get scope stats
    stats = count_files(scope_path)
    scope_size = determine_scope_size(stats)

    # Get base agent configuration for review type
    type_agents = REVIEW_TYPE_AGENTS.get(review_type, REVIEW_TYPE_AGENTS['general'])

    # Start with required agents
    agents = list(type_agents['required'])

    # Add recommended based on scope
    if scope_size in ('medium', 'large', 'comprehensive'):
        agents.extend(type_agents['recommended'])

    # Add optional based on scope
    if scope_size == 'comprehensive':
        agents.extend(type_agents['optional'][:2])  # Add first 2 optional

    # Add scalable agents for large scopes
    if 'scalable' in type_agents and scope_size in ('large', 'comprehensive'):
        scalable_agent = type_agents['scalable']
        if scope_size == 'large':
            for i in range(3):
                agents.append(f"{scalable_agent} (Area {i+1})")
        elif scope_size == 'comprehensive':
            for i in range(6):
                agents.append(f"{scalable_agent} (Area {i+1})")

    # Get recommended count range
    scaling = AGENT_SCALING[scope_size]

    return {
        'scope_stats': stats,
        'scope_size': scope_size,
        'recommended_count': len(agents),
        'min_agents': scaling['min'],
        'max_agents': scaling['max'],
        'agents': agents,
    }


def main():
    parser = argparse.ArgumentParser(
        description='Calculate recommended agent count for a review',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Review Types:
  {chr(10).join(f'  {t:<15} - {REVIEW_TYPE_NAMES[t]}' for t in VALID_REVIEW_TYPES)}

Examples:
    python calculate_agents.py game/strategy general
    python calculate_agents.py tests/ test-coverage
    python calculate_agents.py . security
        """
    )
    parser.add_argument('scope_path',
                        help='Path to directory to review')
    parser.add_argument('review_type', choices=VALID_REVIEW_TYPES,
                        help='Type of review')

    args = parser.parse_args()

    scope_path = Path(args.scope_path)
    if not scope_path.exists():
        print(f"ERROR: Path not found: {scope_path}")
        sys.exit(1)

    print(f"\n{'=' * 50}")
    print(f"Agent Calculation: {args.review_type}")
    print('=' * 50)

    result = calculate_agents(scope_path, args.review_type)

    print(f"\nScope Analysis:")
    print(f"  Path: {scope_path.absolute()}")
    print(f"  Total files: {result['scope_stats']['total_files']}")
    print(f"  Estimated lines: {result['scope_stats']['total_lines']:,}")
    print(f"  Scope size: {result['scope_size'].upper()}")

    if result['scope_stats']['by_extension']:
        print(f"\n  By extension:")
        for ext, count in sorted(result['scope_stats']['by_extension'].items(),
                                  key=lambda x: -x[1]):
            print(f"    {ext}: {count} files")

    print(f"\nRecommendation:")
    print(f"  Agent count: {result['recommended_count']} (range: {result['min_agents']}-{result['max_agents']})")
    print(f"\n  Recommended agents:")
    for i, agent in enumerate(result['agents'], 1):
        print(f"    {i}. {agent}")

    print(f"\n{'=' * 50}")
    print("Adjust as needed based on:")
    print("  - User priorities")
    print("  - Time constraints")
    print("  - Specific focus areas")
    print('=' * 50)


if __name__ == '__main__':
    main()
