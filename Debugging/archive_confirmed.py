#!/usr/bin/env python3
"""
Auto-archive confirmed bugs.

Reads confirmed_bugs.txt and for each bug:
1. Appends entry to solved_bugs.md
2. Moves ticket from active_bugs/ to archived_tickets/
3. Removes row from debug_plan.md
"""

import re
import shutil
from datetime import datetime
from pathlib import Path


DEBUGGING_DIR = Path(__file__).parent
CONFIRMED_FILE = DEBUGGING_DIR / "confirmed_bugs.txt"
DEBUG_PLAN_PATH = DEBUGGING_DIR / "debug_plan.md"
SOLVED_BUGS_PATH = DEBUGGING_DIR / "solved_bugs.md"
ACTIVE_BUGS_DIR = DEBUGGING_DIR / "active_bugs"
ARCHIVED_DIR = DEBUGGING_DIR / "archived_tickets"


def read_confirmed_bugs():
    """Read list of bug IDs from confirmed_bugs.txt."""
    if not CONFIRMED_FILE.exists():
        return []

    content = CONFIRMED_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return []

    return [line.strip() for line in content.split("\n") if line.strip()]


def parse_bug_ticket(bug_id):
    """
    Parse a bug ticket and extract title, description, and work log.

    Returns dict: {"title": "...", "description": "...", "work_log": "..."}
    or None if file not found.
    """
    ticket_path = ACTIVE_BUGS_DIR / f"{bug_id}.md"
    if not ticket_path.exists():
        return None

    content = ticket_path.read_text(encoding="utf-8")

    # Extract title from H1
    title_match = re.search(r"^#\s*BUG-\d+:\s*(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else bug_id

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


def append_to_solved_bugs(bug_id, bug_data):
    """Append a solved bug entry to solved_bugs.md."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    entry = f"""
## [{bug_id}] - {bug_data['title']}
* **Date Solved:** {timestamp}
* **Original Issue:** {bug_data['description']}
* **Solution Implemented:**
{bug_data['work_log']}

---
"""

    with open(SOLVED_BUGS_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


def move_ticket_to_archive(bug_id):
    """Move bug ticket from active_bugs/ to archived_tickets/."""
    source = ACTIVE_BUGS_DIR / f"{bug_id}.md"
    dest = ARCHIVED_DIR / f"{bug_id}.md"

    if source.exists():
        # Ensure archive directory exists
        ARCHIVED_DIR.mkdir(exist_ok=True)
        shutil.move(str(source), str(dest))
        return True
    return False


def remove_from_debug_plan(bug_ids):
    """Remove rows for archived bugs from debug_plan.md table."""
    if not DEBUG_PLAN_PATH.exists():
        return

    content = DEBUG_PLAN_PATH.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Filter out lines containing the bug IDs
    bug_id_set = set(bug_ids)
    new_lines = []

    for line in lines:
        # Check if this is a table row with a bug ID
        match = re.match(r"^\|\s*(BUG-\d+)\s*\|", line)
        if match and match.group(1) in bug_id_set:
            # Skip this line (remove from table)
            continue
        new_lines.append(line)

    DEBUG_PLAN_PATH.write_text("\n".join(new_lines), encoding="utf-8")


def main():
    bug_ids = read_confirmed_bugs()

    if not bug_ids:
        print("No confirmed bugs to archive.")
        print(f"(Looking for: {CONFIRMED_FILE})")
        return

    print(f"Archiving {len(bug_ids)} bug(s)...")
    print()

    archived = []
    skipped = []

    for bug_id in bug_ids:
        bug_data = parse_bug_ticket(bug_id)

        if bug_data is None:
            print(f"  [SKIP] {bug_id} - ticket file not found")
            skipped.append(bug_id)
            continue

        # Append to solved_bugs.md
        append_to_solved_bugs(bug_id, bug_data)

        # Move to archive
        move_ticket_to_archive(bug_id)

        print(f"  [OK] {bug_id}: {bug_data['title']}")
        archived.append(bug_id)

    # Remove from debug_plan.md
    if archived:
        remove_from_debug_plan(archived)

    # Delete confirmed_bugs.txt
    if CONFIRMED_FILE.exists():
        CONFIRMED_FILE.unlink()

    print()
    print("=" * 50)
    print(f"Archived: {len(archived)} bug(s)")
    if archived:
        print(f"  {', '.join(archived)}")
    if skipped:
        print(f"Skipped:  {len(skipped)} bug(s)")
        print(f"  {', '.join(skipped)}")
    print()
    print("Done. Changes made:")
    print(f"  - Entries appended to: {SOLVED_BUGS_PATH.name}")
    print(f"  - Tickets moved to: {ARCHIVED_DIR.name}/")
    print(f"  - Rows removed from: {DEBUG_PLAN_PATH.name}")


if __name__ == "__main__":
    main()
