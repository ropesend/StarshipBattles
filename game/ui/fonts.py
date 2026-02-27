"""Cached Font Management.

PROJ-196: Centralized font creation with caching to eliminate per-frame
font instantiation performance bugs. All font access should go through
get_font() or get_default_font() to leverage the cache.

Usage:
    from game.ui.fonts import get_font, get_default_font, FONT_MAIN, FONT_MONO

    # System fonts (Arial, Consolas, etc.)
    font = get_font(24)                      # Arial 24pt
    font = get_font(18, bold=True)           # Arial 18pt bold
    font = get_font(14, FONT_MONO)           # Consolas 14pt

    # Pygame default font (Font(None, size))
    font = get_default_font(32)              # Default 32pt
"""

import pygame

# Font family constants
FONT_MAIN = "Arial"
FONT_MONO = "Consolas"

# Module-level cache: (name, size, bold) -> Font for SysFont
#                     (None, size) -> Font for default font
_font_cache: dict = {}

def _ensure_cache_valid() -> None:
    """Ensure cache is valid (font module wasn't quit since fonts were cached).

    If pygame.font was quit and re-initialized, any cached Font objects
    become invalid. We detect this by trying to use a cached font - if it
    raises an error, we clear the cache.
    """
    if not _font_cache:
        return

    # Check if any cached font is still valid by trying to get its metrics
    # This is a lightweight operation that will fail if pygame.font was quit
    try:
        # Get any cached font and test it
        font = next(iter(_font_cache.values()))
        font.get_linesize()  # Will raise if font is invalid
    except (pygame.error, StopIteration):
        # Font is invalid - clear the cache
        _font_cache.clear()


def get_font(size: int, name: str = FONT_MAIN, bold: bool = False) -> pygame.font.Font:
    """Get a cached system font.

    Args:
        size: Font size in points.
        name: Font family name (default: FONT_MAIN = "Arial").
        bold: Whether to use bold variant.

    Returns:
        Cached pygame.font.Font instance.
    """
    _ensure_cache_valid()
    key = (name, size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(name, size, bold=bold)
    return _font_cache[key]


def get_default_font(size: int) -> pygame.font.Font:
    """Get a cached pygame default font.

    This uses pygame.font.Font(None, size) which gives the built-in
    pygame default font rather than a system font.

    Args:
        size: Font size in points.

    Returns:
        Cached pygame.font.Font instance.
    """
    _ensure_cache_valid()
    key = (None, size)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.Font(None, size)
    return _font_cache[key]


def clear_cache() -> None:
    """Clear the font cache.

    Useful for testing or when pygame display mode changes.
    """
    _font_cache.clear()
