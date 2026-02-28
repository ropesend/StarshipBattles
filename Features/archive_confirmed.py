#!/usr/bin/env python3
"""
Auto-archive confirmed features.

Reads confirmed_features.txt and for each feature:
1. Appends entry to completed_features.md
2. Moves ticket from active_features/ to archived_features/
3. Removes row from feature_plan.md
"""

import re
import shutil
from datetime import datetime
from pathlib import Path


FEATURES_DIR = Path(__file__).parent
CONFIRMED_FILE = FEATURES_DIR / "confirmed_features.txt"
FEATURE_PLAN_PATH = FEATURES_DIR / "feature_plan.md"
COMPLETED_FEATURES_PATH = FEATURES_DIR / "completed_features.md"
ACTIVE_FEATURES_DIR = FEATURES_DIR / "active_features"
ARCHIVED_DIR = FEATURES_DIR / "archived_features"


def read_confirmed_features():
    """Read list of feature IDs from confirmed_features.txt."""
    if not CONFIRMED_FILE.exists():
        return []

    content = CONFIRMED_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return []

    return [line.strip() for line in content.split("\n") if line.strip()]


def parse_feature_ticket(feat_id):
    """
    Parse a feature ticket and extract title, description, and work log.

    Returns dict: {"title": "...", "description": "...", "work_log": "..."}
    or None if file not found.
    """
    ticket_path = ACTIVE_FEATURES_DIR / f"{feat_id}.md"
    if not ticket_path.exists():
        return None

    content = ticket_path.read_text(encoding="utf-8")

    # Extract title from H1
    title_match = re.search(r"^#\s*FEAT-\d+:\s*(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else feat_id

    # Extract description (between ## Description and next ##)
    desc_match = re.search(
        r"## Description\s*\n(.*?)(?=\n##|\Z)",
        content,
        re.DOTALL
    )
    description = desc_match.group(1).strip() if desc_match else ""
    # Get first line of description for summary
    first_line = description.split("\n")[0].strip() if description else "No description"

    # Extract work log (from ## Work Log to next ## or EOF)
    worklog_match = re.search(
        r"## Work Log\s*\n(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL
    )
    work_log = worklog_match.group(1).strip() if worklog_match else ""

    return {
        "title": title,
        "description": first_line,
        "work_log": work_log
    }


def append_to_completed_features(feat_id, feat_data):
    """Append a completed feature entry to completed_features.md."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    entry = f"""
## [{feat_id}] - {feat_data['title']}
* **Date Completed:** {timestamp}
* **Original Request:** {feat_data['description']}
* **Implementation Summary:**
{feat_data['work_log']}
* **Test Case:** See ticket for details
* **Notes:** —

---
"""

    with open(COMPLETED_FEATURES_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


def move_ticket_to_archive(feat_id):
    """Move feature ticket from active_features/ to archived_features/."""
    source = ACTIVE_FEATURES_DIR / f"{feat_id}.md"
    dest = ARCHIVED_DIR / f"{feat_id}.md"

    if source.exists():
        # Ensure archive directory exists
        ARCHIVED_DIR.mkdir(exist_ok=True)
        shutil.move(str(source), str(dest))
        return True
    return False


def remove_from_feature_plan(feat_ids):
    """Remove rows for archived features from feature_plan.md table."""
    if not FEATURE_PLAN_PATH.exists():
        return

    content = FEATURE_PLAN_PATH.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Filter out lines containing the feature IDs
    feat_id_set = set(feat_ids)
    new_lines = []

    for line in lines:
        # Check if this is a table row with a feature ID
        match = re.match(r"^\|\s*(FEAT-\d+)\s*\|", line)
        if match and match.group(1) in feat_id_set:
            # Skip this line (remove from table)
            continue
        new_lines.append(line)

    FEATURE_PLAN_PATH.write_text("\n".join(new_lines), encoding="utf-8")


def main():
    feat_ids = read_confirmed_features()

    if not feat_ids:
        print("No confirmed features to archive.")
        print(f"(Looking for: {CONFIRMED_FILE})")
        return

    print(f"Archiving {len(feat_ids)} feature(s)...")
    print()

    archived = []
    skipped = []

    for feat_id in feat_ids:
        feat_data = parse_feature_ticket(feat_id)

        if feat_data is None:
            print(f"  [SKIP] {feat_id} - ticket file not found")
            skipped.append(feat_id)
            continue

        # Append to completed_features.md
        append_to_completed_features(feat_id, feat_data)

        # Move to archive
        move_ticket_to_archive(feat_id)

        print(f"  [OK] {feat_id}: {feat_data['title']}")
        archived.append(feat_id)

    # Remove from feature_plan.md
    if archived:
        remove_from_feature_plan(archived)

    # Delete confirmed_features.txt
    if CONFIRMED_FILE.exists():
        CONFIRMED_FILE.unlink()

    print()
    print("=" * 50)
    print(f"Archived: {len(archived)} feature(s)")
    if archived:
        print(f"  {', '.join(archived)}")
    if skipped:
        print(f"Skipped:  {len(skipped)} feature(s)")
        print(f"  {', '.join(skipped)}")
    print()
    print("Done. Changes made:")
    print(f"  - Entries appended to: {COMPLETED_FEATURES_PATH.name}")
    print(f"  - Tickets moved to: {ARCHIVED_DIR.name}/")
    print(f"  - Rows removed from: {FEATURE_PLAN_PATH.name}")


if __name__ == "__main__":
    main()
