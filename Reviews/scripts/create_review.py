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
UPDATE_SCOPE_TEMPLATE = '''# Update Review Scope: {review_name}

## Metadata
- **Date:** {date}
- **Type:** Update Review
- **Description:** {description}
- **Original Review:** [{original_review}](../{original_review}/)
- **Original Date:** {original_date}
- **Days Since Original:** {days_since}

## Update Chain
- **Update Number:** {update_number}
- **Previous Updates:** {previous_updates}

## Original Scope (Inherited)
[Scope inherited from original review - see original scope.md for details]

## Validation Configuration
**Validation Scope:** All findings
**Original Finding Count:** {original_finding_count}

### Agents
| Agent | Role | Status |
|-------|------|--------|
| Finding Validator | Validate status of each original finding | Pending |
| Progress Analyst | Calculate fix rates and progress metrics | Pending |
| Regression Hunter | Check for regressions in fixed areas | Pending |
| New Issue Scout | Find new issues within original scope | Pending |

## Notes
[Any additional context or notes]
'''

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


def update_index(review_name: str, review_type: str, description: str, original_review: str = None):
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

    # For update reviews, add to Update Reviews section
    if review_type == "update" and original_review:
        # Extract original date from folder name
        original_date = original_review.split('_')[0] if '_' in original_review else "Unknown"
        new_row = f"| {date} | [{original_review}](results/{original_review}/) | {original_date} | In Progress | [{review_name}](results/{review_name}/) |"

        # Check if Update Reviews section exists
        if '## Update Reviews' not in content:
            # Add Update Reviews section before Completed Reviews
            update_section = '''
## Update Reviews
| Update Date | Original Review | Original Date | Progress | Link |
|-------------|-----------------|---------------|----------|------|

'''
            content = content.replace('## Completed Reviews', update_section + '## Completed Reviews')

        # Insert into Update Reviews section
        lines = content.split('\n')
        new_lines = []
        found_update = False
        inserted = False

        for line in lines:
            new_lines.append(line)
            if '## Update Reviews' in line and not inserted:
                found_update = True
            elif found_update and line.startswith('|---') and not inserted:
                new_lines.append(new_row)
                inserted = True

        if not inserted:
            new_lines.append(new_row)

        INDEX_FILE.write_text('\n'.join(new_lines), encoding='utf-8')
        return

    # Regular reviews go to Active Reviews
    new_row = f"| {date} | {type_display} | {description} | In Progress | [{review_name}](results/{review_name}/) |"

    # Insert after the Active Reviews header row
    lines = content.split('\n')
    new_lines = []
    found_active = False
    inserted = False

    for line in lines:
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


def count_findings_in_review(review_folder: Path) -> int:
    """Count findings in a review folder."""
    findings_dir = review_folder / "findings"
    if not findings_dir.exists():
        return 0

    count = 0
    import re
    finding_pattern = re.compile(r'####\s+(CRITICAL|MAJOR|MINOR|INFO):', re.IGNORECASE)

    for report_file in findings_dir.glob("*.md"):
        content = report_file.read_text(encoding='utf-8')
        count += len(finding_pattern.findall(content))

    return count


def count_previous_updates(original_review: str) -> tuple:
    """Count previous updates to an original review.

    Returns (update_number, list of previous update folder names).
    """
    if not RESULTS_DIR.exists():
        return 1, "None"

    # Look for existing updates to this original
    previous_updates = []
    for folder in RESULTS_DIR.iterdir():
        if folder.is_dir() and folder.name.startswith("20") and "_update_" in folder.name:
            # Check if this update references the same original
            scope_file = folder / "scope.md"
            if scope_file.exists():
                content = scope_file.read_text(encoding='utf-8')
                if original_review in content:
                    previous_updates.append(folder.name)

    if not previous_updates:
        return 1, "None"

    return len(previous_updates) + 1, ", ".join(sorted(previous_updates))


def create_review(review_type: str, description: str, original: str = None) -> Path:
    """Create a new review with directory structure.

    Args:
        review_type: Type of review (general, update, etc.)
        description: Brief description of the review
        original: For update reviews, the original review folder name

    Returns the review folder path.
    """
    # Validate review type
    if review_type not in VALID_REVIEW_TYPES:
        print(f"ERROR: Invalid review type '{review_type}'")
        print(f"Valid types: {', '.join(VALID_REVIEW_TYPES)}")
        sys.exit(1)

    # For update reviews, require original
    if review_type == "update" and not original:
        print("ERROR: Update reviews require --original <review_folder>")
        sys.exit(1)

    # Validate original review exists for update reviews
    original_folder = None
    if review_type == "update" and original:
        original_folder = RESULTS_DIR / original
        if not original_folder.exists():
            print(f"ERROR: Original review not found: {original}")
            print(f"       Expected at: {original_folder}")
            sys.exit(1)

    # Create folder name (include time to prevent same-day collisions)
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    date_time = now.strftime("%Y-%m-%d %H:%M")
    time_suffix = now.strftime("%H%M%S")
    slug = slugify(description)
    review_name = f"{date}_{time_suffix}_{review_type}_{slug}"

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

    if review_type == "update" and original_folder:
        # Use update-specific scope template
        original_date = original.split('_')[0] if '_' in original else "Unknown"
        try:
            original_dt = datetime.strptime(original_date, "%Y-%m-%d")
            days_since = (datetime.now() - original_dt).days
        except ValueError:
            days_since = "Unknown"

        finding_count = count_findings_in_review(original_folder)
        update_number, previous_updates = count_previous_updates(original)

        scope_content = UPDATE_SCOPE_TEMPLATE.format(
            review_name=review_name,
            date=date_time,
            description=description,
            original_review=original,
            original_date=original_date,
            days_since=days_since,
            update_number=update_number,
            previous_updates=previous_updates,
            original_finding_count=finding_count,
        )
    else:
        # Use standard scope template
        scope_content = SCOPE_TEMPLATE.format(
            review_name=review_name,
            date=date_time,
            review_type=type_display,
            description=description,
        )

    (review_dir / "scope.md").write_text(scope_content, encoding='utf-8')
    print(f"  Created: scope.md")

    # Create empty report.md placeholder
    if review_type == "update":
        report_placeholder = f'''# Update Review Report: {review_name}

> **THIS REPORT WILL BE GENERATED**
> Run `python Reviews/scripts/compile_update_findings.py {review_name}` after agents complete.

## Status
Awaiting agent findings...

## Original Review
[{original}](../{original}/)
'''
    else:
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
        update_index(review_name, review_type, description, original)
        print(f"  Added {review_name} to index")
    except Exception as e:
        print(f"  [WARN] Could not update index: {e}")
        print(f"         Please add manually to reviews_index.md")

    print(f"\n{'=' * 50}")
    print(f"REVIEW CREATED")
    print(f"  Name: {review_name}")
    print(f"  Directory: {review_dir}")
    if review_type == "update":
        print(f"  Original: {original}")
    print(f"\nNext steps:")
    if review_type == "update":
        print(f"  1. Launch update review agents")
        print(f"  2. Agents write to findings/")
        print(f"  3. Run compile_update_findings.py to generate report")
    else:
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
  update        - Validate progress on previous review (requires --original)

Examples:
  python create_review.py general "game logic health check"
  python create_review.py test-coverage "fleet module tests"
  python create_review.py focused "why does combat freeze"
  python create_review.py migration "callback to async"
  python create_review.py update "maintainability-update" --original 2026-01-24_general_full-codebase
        """
    )
    parser.add_argument('type', choices=VALID_REVIEW_TYPES,
                        help='Type of review')
    parser.add_argument('description',
                        help='Brief description of the review')
    parser.add_argument('--original', '-o',
                        help='For update reviews: the original review folder to update')

    args = parser.parse_args()

    create_review(args.type, args.description, args.original)
    sys.exit(0)


if __name__ == '__main__':
    main()
