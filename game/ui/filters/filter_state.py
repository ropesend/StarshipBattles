"""Tri-state filter enum for unified filter infrastructure."""
from enum import Enum


class FilterState(Enum):
    """Tri-state filter value: YES (include matching), NO (exclude matching), IGNORE (no filter)."""

    YES = "yes"
    NO = "no"
    IGNORE = "ignore"
