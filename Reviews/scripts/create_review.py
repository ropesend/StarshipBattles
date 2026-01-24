#!/usr/bin/env python3
"""
Create a new review with the correct directory structure.

Usage:
    python create_review.py <type> "<description>"

Examples:
    python create_review.py general "game logic health check"
    python create_review.py test-coverage "fleet module tests"
    python create_review.py focused "error handling patterns"
    python create_review.py migration "callback to async events"
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import (
    RESULTS_DIR,
    INDEX_FILE,
    VALID_REVIEW_TYPES,
    REVIEW_TYPE_NAMES,
)


# Templates
SCOPE_TEMPLATE = '''# Review Scope: {review_name}

## Metadata
- **Date:** {date}
- **Type:** {review_type}
- **Description:** {description}

## Scope Definition
[Define what will be reviewed]

### Target
- [ ] Entire codebase
- [ ] Specific directory: `path/to/dir/`
- [ ] Specific module: `module_name`
- [ ] Other: ___

### Priorities
[User priorities from Phase A]

### Exclusions
[Areas to exclude from review]

## Agent Configuration
**Recommended Agents:** TBD
**Confirmed Agent Count:** TBD

### Selected Agents
| Agent | Role | Status |
|-------|------|--------|
| [Agent Name] | [Role] | Pending |

## Notes
[Any additional context or notes]
'''


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    # Lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    # Limit length
    return text[:50]


def get_next_review_number() -> int:
    """Get the next review number by checking existing folders."""
    if not RESULTS_DIR.exists():
        return 1

    existing = list(RESULTS_DIR.iterdir())
    return len(existing) + 1


def update_index(review_name: str, review_type: str, description: str, folder_path: Path):
    """Add review to reviews_index.md."""
    date = datetime.now().strftime("%Y-%m-%d")
    type_display = REVIEW_TYPE_NAMES.get(review_type, review_type.title())

    # Read existing index
    if INDEX_FILE.exists():
        content = INDEX_FILE.read_text(encoding='utf-8')
    else:
        # Create new index if doesn't exist
        content = '''# Reviews Index

## Active Reviews
| Date | Type | Description | Status | Link |
|------|------|-------------|--------|------|

## Completed Reviews
| Date | Type | Description | Key Findings | Link |
|------|------|-------------|--------------|------|

## Reviews Leading to Projects
| Review | Project | Description |
|--------|---------|-------------|
'''

    # Find the Active Reviews table and add new row
    new_row = f"| {date} | {type_display} | {description} | In Progress | [{review_name}](results/{review_name}/) |"

    # Insert after the Active Reviews header row
    lines = content.split('\n')
    new_lines = []
    found_active = False
    inserted = False

    for i, line in enumerate(lines):
        new_lines.append(line)
        if '## Active Reviews' in line and not inserted:
            found_active = True
        elif found_active and line.startswith('|---') and not inserted:
            # Insert after the separator row
            new_lines.append(new_row)
            inserted = True

    if not inserted:
        # Fallback: just append
        new_lines.append(new_row)

    INDEX_FILE.write_text('\n'.join(new_lines), encoding='utf-8')


def create_review(review_type: str, description: str) -> Path:
    """Create a new review with directory structure.

    Returns the review folder path.
    """
    # Validate review type
    if review_type not in VALID_REVIEW_TYPES:
        print(f"ERROR: Invalid review type '{review_type}'")
        print(f"Valid types: {', '.join(VALID_REVIEW_TYPES)}")
        sys.exit(1)

    # Create folder name
    date = datetime.now().strftime("%Y-%m-%d")
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    slug = slugify(description)
    review_name = f"{date}_{review_type}_{slug}"

    print(f"\n{'=' * 50}")
    print(f"Creating New Review: {review_name}")
    print('=' * 50)

    # Create review directory
    review_dir = RESULTS_DIR / review_name
    findings_dir = review_dir / "findings"

    print(f"\nSTEP 1: Create directory structure")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    review_dir.mkdir(parents=True, exist_ok=True)
    findings_dir.mkdir(exist_ok=True)
    print(f"  Created: {review_dir}")
    print(f"  Created: {findings_dir}")

    # Create scope.md
    print(f"\nSTEP 2: Create review files")
    type_display = REVIEW_TYPE_NAMES.get(review_type, review_type.title())
    scope_content = SCOPE_TEMPLATE.format(
        review_name=review_name,
        date=date_time,
        review_type=type_display,
        description=description,
    )
    (review_dir / "scope.md").write_text(scope_content, encoding='utf-8')
    print(f"  Created: scope.md")

    # Create empty report.md placeholder
    report_placeholder = f'''# Review Report: {review_name}

> **THIS REPORT WILL BE GENERATED**
> Run `python Reviews/scripts/compile_findings.py {review_name}` after agents complete.

## Status
Awaiting agent findings...
'''
    (review_dir / "report.md").write_text(report_placeholder, encoding='utf-8')
    print(f"  Created: report.md (placeholder)")

    # Update index
    print(f"\nSTEP 3: Update reviews_index.md")
    try:
        update_index(review_name, review_type, description, review_dir)
        print(f"  Added {review_name} to index")
    except Exception as e:
        print(f"  [WARN] Could not update index: {e}")
        print(f"         Please add manually to reviews_index.md")

    print(f"\n{'=' * 50}")
    print(f"REVIEW CREATED")
    print(f"  Name: {review_name}")
    print(f"  Directory: {review_dir}")
    print(f"\nNext steps:")
    print(f"  1. Define scope in scope.md")
    print(f"  2. Launch review agents")
    print(f"  3. Agents write to findings/")
    print(f"  4. Run compile_findings.py to generate report")
    print('=' * 50)

    return review_dir


def main():
    parser = argparse.ArgumentParser(
        description='Create a new review with directory structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Review Types:
  general       - Broad codebase health check
  test-coverage - Test completeness analysis
  focused       - Answer specific question
  migration     - System conversion analysis
  security      - Security audit
  performance   - Performance analysis
  tech-debt     - Technical debt assessment
  consistency   - Pattern consistency check

Examples:
  python create_review.py general "game logic health check"
  python create_review.py test-coverage "fleet module tests"
  python create_review.py focused "why does combat freeze"
  python create_review.py migration "callback to async"
        """
    )
    parser.add_argument('type', choices=VALID_REVIEW_TYPES,
                        help='Type of review')
    parser.add_argument('description',
                        help='Brief description of the review')

    args = parser.parse_args()

    create_review(args.type, args.description)
    sys.exit(0)


if __name__ == '__main__':
    main()
