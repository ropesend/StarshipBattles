"""Shared portrait placeholder generation utilities.

Provides common functions for ship class colors and placeholder portrait
creation used across UI panels.

Usage:
    from game.ui.utils.portraits import (
        get_ship_class_color,
        create_placeholder_portrait,
    )
"""
from typing import Optional, Tuple

import pygame

from game.ui.colors import (
    SHIP_CLASS_FIGHTER, SHIP_CLASS_CORVETTE, SHIP_CLASS_ESCORT,
    SHIP_CLASS_DESTROYER, SHIP_CLASS_CRUISER, SHIP_CLASS_BATTLESHIP,
    SHIP_CLASS_CARRIER, SHIP_CLASS_DEFAULT,
    WHITE, BLACK, TEXT_ITEM,
)
from game.ui.fonts import get_font


# Ship class to color mapping for placeholder generation
_SHIP_CLASS_COLORS = {
    'Fighter': SHIP_CLASS_FIGHTER,
    'Corvette': SHIP_CLASS_CORVETTE,
    'Escort': SHIP_CLASS_ESCORT,
    'Frigate': SHIP_CLASS_ESCORT,
    'Destroyer': SHIP_CLASS_DESTROYER,
    'Cruiser': SHIP_CLASS_CRUISER,
    'Battleship': SHIP_CLASS_BATTLESHIP,
    'Carrier': SHIP_CLASS_CARRIER,
}


def get_ship_class_color(ship_class: Optional[str]) -> Tuple[int, int, int]:
    """Get the color associated with a ship class for placeholder portraits.

    Args:
        ship_class: Ship class name (e.g. "Fighter", "Cruiser").

    Returns:
        RGB color tuple. Returns SHIP_CLASS_DEFAULT for unknown classes.
    """
    if ship_class is None:
        return SHIP_CLASS_DEFAULT
    return _SHIP_CLASS_COLORS.get(ship_class, SHIP_CLASS_DEFAULT)


def create_placeholder_portrait(
    width: int,
    height: int,
    base_color: Tuple[int, int, int],
    name_text: str,
    subtitle: Optional[str] = None,
) -> pygame.Surface:
    """Create a placeholder portrait with gradient fill and text.

    Generates a portrait surface with a vertical gradient from the base
    color, centered name text with shadow, optional subtitle, and a border.

    Args:
        width: Portrait width in pixels.
        height: Portrait height in pixels.
        name_text: Primary text (e.g. ship name), truncated to 25 chars.
        subtitle: Optional secondary text (e.g. ship class).
        base_color: Base RGB color for the gradient fill.

    Returns:
        A pygame.Surface with the placeholder portrait.
    """
    surface = pygame.Surface((width, height))

    # Gradient fill - fade downward
    for y in range(height):
        fade = 1.0 - (y / height) * 0.4
        color = tuple(int(c * fade) for c in base_color)
        pygame.draw.line(surface, color, (0, y), (width, y))

    # Scale font sizes based on portrait size
    font_scale = width / 200.0
    font_large = get_font(max(8, int(18 * font_scale)), bold=True)
    font_small = get_font(max(6, int(14 * font_scale)))

    # Name text with shadow
    truncated = name_text[:25]
    name_surf = font_large.render(truncated, True, WHITE)
    name_rect = name_surf.get_rect(center=(width // 2, int(height * 0.45)))
    shadow_surf = font_large.render(truncated, True, BLACK)
    shadow_rect = shadow_surf.get_rect(center=(width // 2 + 1, int(height * 0.45) + 1))
    surface.blit(shadow_surf, shadow_rect)
    surface.blit(name_surf, name_rect)

    # Subtitle
    if subtitle:
        sub_surf = font_small.render(str(subtitle), True, TEXT_ITEM)
        sub_rect = sub_surf.get_rect(center=(width // 2, int(height * 0.55)))
        surface.blit(sub_surf, sub_rect)

    # Border
    pygame.draw.rect(surface, TEXT_ITEM, (0, 0, width, height), 2)

    return surface
