"""Configuration for project management scripts."""
from pathlib import Path

# Base paths
SCRIPTS_DIR = Path(__file__).parent.parent
PROJECTS_DIR = SCRIPTS_DIR.parent
ACTIVE_DIR = PROJECTS_DIR / "active_projects"
ARCHIVED_DIR = PROJECTS_DIR / "archived_projects"
PROTOCOLS_DIR = PROJECTS_DIR / "protocols"
INDEX_FILE = PROJECTS_DIR / "projects_index.md"

# Valid project statuses (from projects_index.md Status Legend)
VALID_STATUSES = [
    "Planning",
    "In Progress",
    "Auditing",
    "Awaiting Verification",
    "Revision",
    "Archived",
]

# Freshness threshold for Current State (hours)
FRESHNESS_THRESHOLD_HOURS = 48
