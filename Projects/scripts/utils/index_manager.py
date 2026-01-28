"""Utilities for managing projects_index.md."""
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from .config import INDEX_FILE, VALID_STATUSES, ACTIVE_DIR, ARCHIVED_DIR


@dataclass
class ProjectEntry:
    """Represents a project entry in the index."""
    project_id: str
    title: str
    status: str
    started: str
    last_updated: str


def read_projects_index() -> str:
    """Read the projects index file."""
    return INDEX_FILE.read_text(encoding='utf-8')


def write_projects_index(content: str) -> None:
    """Write the projects index file."""
    INDEX_FILE.write_text(content, encoding='utf-8')


def get_next_project_id() -> str:
    """Get the next available project ID, checking for existing directories.

    This function ensures we never return an ID that already has a directory
    on disk, preventing accidental overwrites even if the index is out of sync.
    """
    content = read_projects_index()

    # Start with ID from index
    match = re.search(r'Next Project ID:\s*PROJ-(\d+)', content)
    if match:
        next_num = int(match.group(1))
    else:
        # Fall back to finding highest existing ID and adding 1
        ids = re.findall(r'PROJ-(\d+)', content)
        next_num = max(int(id_num) for id_num in ids) + 1 if ids else 1

    # Keep incrementing until we find an unused ID (no directory exists)
    while True:
        project_id = f"PROJ-{next_num:02d}"
        active_path = ACTIVE_DIR / project_id
        archived_path = ARCHIVED_DIR / project_id

        if not active_path.exists() and not archived_path.exists():
            return project_id

        # Directory exists, try next number
        next_num += 1


def parse_project_entries(content: str) -> List[ProjectEntry]:
    """Parse project entries from the index table."""
    entries = []

    # Find the table rows (skip header)
    # Pattern: | PROJ-XX | Title | Status | Date | Date |
    row_pattern = r'\|\s*(PROJ-\d+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'

    for match in re.finditer(row_pattern, content):
        entries.append(ProjectEntry(
            project_id=match.group(1).strip(),
            title=match.group(2).strip(),
            status=match.group(3).strip(),
            started=match.group(4).strip(),
            last_updated=match.group(5).strip(),
        ))

    return entries


def update_project_status_in_index(project_id: str, new_status: str) -> None:
    """Update a project's status in the index."""
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {new_status}. Must be one of: {VALID_STATUSES}")

    content = read_projects_index()
    today = datetime.now().strftime("%Y-%m-%d")

    # Pattern to match the project row
    pattern = rf'(\|\s*{re.escape(project_id)}\s*\|[^|]+\|)\s*[^|]+\s*(\|[^|]+\|)\s*[^|]+\s*\|'
    replacement = rf'\1 {new_status} \2 {today} |'

    updated, count = re.subn(pattern, replacement, content)

    if count == 0:
        raise ValueError(f"Project not found in index: {project_id}")

    write_projects_index(updated)


def add_project_to_index(project_id: str, title: str, status: str = "Planning") -> None:
    """Add a new project to the index."""
    content = read_projects_index()
    today = datetime.now().strftime("%Y-%m-%d")

    # Create new row
    new_row = f"| {project_id} | {title} | {status} | {today} | {today} |"

    # Find the Active Projects table and add the row
    # Look for the last row before "## Archived" or end of active table
    # Insert after the header separator line

    # Find the Active Projects section
    active_match = re.search(r'(## Active Projects.*?\n\|[^\n]+\|\n\|[-| ]+\|\n)', content, re.DOTALL)
    if active_match:
        insert_pos = active_match.end()
        content = content[:insert_pos] + new_row + "\n" + content[insert_pos:]
    else:
        raise ValueError("Could not find Active Projects table in index")

    # Update Next Project ID
    next_num = int(project_id.replace("PROJ-", "")) + 1
    content = re.sub(
        r'Next Project ID:\s*PROJ-\d+',
        f'Next Project ID: PROJ-{next_num:02d}',
        content
    )

    write_projects_index(content)


def archive_project_in_index(project_id: str) -> None:
    """Move a project from Active to Archived in the index."""
    content = read_projects_index()
    today = datetime.now().strftime("%Y-%m-%d")

    # Find the project row in Active section
    row_pattern = rf'(\|\s*{re.escape(project_id)}\s*\|[^|]+\|)\s*[^|]+\s*(\|[^|]+\|)\s*[^|]+\s*\|'
    row_match = re.search(row_pattern, content)

    if not row_match:
        raise ValueError(f"Project not found in index: {project_id}")

    # Get the full row
    full_row_pattern = rf'\|\s*{re.escape(project_id)}\s*\|[^\n]+\|'
    full_match = re.search(full_row_pattern, content)
    original_row = full_match.group(0)

    # Remove from Active section
    content = content.replace(original_row + "\n", "")

    # Create archived row with updated status and date
    # Parse the original row to get title and started date
    parts = [p.strip() for p in original_row.split("|") if p.strip()]
    if len(parts) >= 4:
        title = parts[1]
        started = parts[3]
        archived_row = f"| {project_id} | {title} | Archived | {started} | {today} |"
    else:
        archived_row = original_row.replace("| Awaiting Verification |", "| Archived |")

    # Find Archived Projects section and add row
    archived_match = re.search(r'(## Archived Projects.*?\n\|[^\n]+\|\n\|[-| ]+\|\n)', content, re.DOTALL)
    if archived_match:
        insert_pos = archived_match.end()
        content = content[:insert_pos] + archived_row + "\n" + content[insert_pos:]
    else:
        # Create Archived Projects section if it doesn't exist
        content += f"\n\n## Archived Projects\n| ID | Title | Status | Started | Completed |\n|-----|-------|--------|---------|----------|\n{archived_row}\n"

    write_projects_index(content)


def get_project_entry(project_id: str) -> Optional[ProjectEntry]:
    """Get a specific project entry from the index."""
    content = read_projects_index()
    entries = parse_project_entries(content)

    for entry in entries:
        if entry.project_id == project_id:
            return entry

    return None
