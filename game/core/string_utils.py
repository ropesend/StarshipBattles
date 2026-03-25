"""
String utility functions for display formatting and ID generation.

Provides shared helpers for common string transformations used across
the codebase, eliminating duplicated inline patterns.

Usage:
    from game.core.string_utils import display_name, slugify

    display_name("heavy_laser")  # "Heavy Laser"
    slugify("Heavy Laser")       # "heavy_laser"
"""
import re


def display_name(raw: str) -> str:
    """Convert an internal identifier to a human-readable display name.

    Replaces underscores with spaces and title-cases each word.

    Args:
        raw: Internal name with underscores (e.g. "heavy_laser")

    Returns:
        Human-readable display name (e.g. "Heavy Laser")
    """
    return raw.replace('_', ' ').title()


def slugify(text: str) -> str:
    """Convert a display string to a lowercase slug identifier.

    Strips whitespace, lowercases, replaces spaces and hyphens with
    underscores, removes non-alphanumeric characters (except underscores),
    and collapses multiple underscores.

    Args:
        text: Human-readable text (e.g. "Heavy Laser")

    Returns:
        Slug identifier (e.g. "heavy_laser")
    """
    text = text.strip().lower()
    # Convert hyphens to underscores before stripping other chars
    text = text.replace('-', '_')
    text = re.sub(r'[^a-z0-9\s_]', '', text)
    text = re.sub(r'[\s_]+', '_', text)
    return text
