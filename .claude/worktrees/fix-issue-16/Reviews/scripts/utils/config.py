"""Configuration for review management scripts."""
from pathlib import Path

# Base paths
SCRIPTS_DIR = Path(__file__).parent.parent
REVIEWS_DIR = SCRIPTS_DIR.parent
RESULTS_DIR = REVIEWS_DIR / "results"
PROTOCOLS_DIR = REVIEWS_DIR / "protocols"
INDEX_FILE = REVIEWS_DIR / "reviews_index.md"

# Valid review types
VALID_REVIEW_TYPES = [
    "general",
    "test-coverage",
    "focused",
    "migration",
    "security",
    "performance",
    "tech-debt",
    "consistency",
    "update",
    "sweep",
]

# Review type display names
REVIEW_TYPE_NAMES = {
    "general": "General Review",
    "test-coverage": "Test Coverage Review",
    "focused": "Focused Question Review",
    "migration": "Migration Review",
    "security": "Security Review",
    "performance": "Performance Review",
    "tech-debt": "Technical Debt Review",
    "consistency": "Consistency Review",
    "update": "Update Review",
    "sweep": "Sweep Review",
}

# Valid review statuses
VALID_STATUSES = [
    "In Progress",
    "Completed",
    "Archived",
    "Led to Project",
]

# Severity levels
SEVERITY_LEVELS = ["Critical", "Major", "Minor", "Info"]

# Validation statuses for update reviews
VALIDATION_STATUSES = [
    "FIXED",
    "PARTIALLY_FIXED",
    "STILL_PRESENT",
    "WORSE",
    "OBSOLETE",
    "CANNOT_VERIFY",
]

# Agent count recommendations by scope size
AGENT_SCALING = {
    "small": {"min": 4, "max": 6, "description": "1-20 files"},
    "medium": {"min": 6, "max": 10, "description": "20-100 files"},
    "large": {"min": 10, "max": 15, "description": "100-500 files"},
    "comprehensive": {"min": 15, "max": 25, "description": "500+ files"},
}
