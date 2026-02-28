"""Configuration for project management scripts."""
from pathlib import Path

# Base paths
SCRIPTS_DIR = Path(__file__).parent.parent
PROJECTS_DIR = SCRIPTS_DIR.parent
ACTIVE_DIR = PROJECTS_DIR / "active_projects"
ARCHIVED_DIR = PROJECTS_DIR / "archived_projects"
DEEP_ARCHIVE_DIR = PROJECTS_DIR / "deep_archive"
DEEP_ARCHIVE_INDEX = PROJECTS_DIR / "deep_archive_index.md"
PROTOCOLS_DIR = PROJECTS_DIR / "protocols"
INDEX_FILE = PROJECTS_DIR / "projects_index.md"

# How many projects to keep in archived_projects before sweeping to deep archive
MAX_ARCHIVED_PROJECTS = 20

# Valid project statuses (from projects_index.md Status Legend)
VALID_STATUSES = [
    "Planning",
    "In Progress",
    "Auditing",
    "Awaiting Verification",
    "Revision",
    "Archived",
]

# Valid phase statuses (for individual phase checklists)
VALID_PHASE_STATUSES = [
    "Not Started",
    "In Progress",
    "Complete",
    "Deferred",
    "Skipped",
    "Extracted",           # Phase extracted to sub-project
    "Extracted (Complete)", # Sub-project archived, phase auto-completed
]

# Freshness threshold for Current State (hours)
FRESHNESS_THRESHOLD_HOURS = 48
