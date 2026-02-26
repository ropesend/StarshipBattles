"""
Design Image Helper - Utility functions for loading design thumbnail images.

This module provides pure functions for loading portrait and top-down (skin)
thumbnails for ship designs. These functions have no dependency on UI state
and can be used by any component that needs to display design images.

Functions:
    load_portrait_thumbnail: Load a portrait image for a design.
    load_topdown_thumbnail: Load a top-down skin image for a design.
    clear_thumbnail_cache: Clear the in-memory thumbnail cache.
"""
from __future__ import annotations

import os
import pygame
from typing import Dict, Optional, Tuple, TYPE_CHECKING

import logging

from game.ui.fonts import get_font
from game.ui.colors import (
    THUMB_SHIP, THUMB_FIGHTER, THUMB_SATELLITE, THUMB_COMPLEX,
    THUMB_TEXT, PLACEHOLDER_DEFAULT, SWATCH_BORDER
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.design_metadata import DesignMetadata

# Module-level thumbnail cache: (design_id, size) -> Surface
_portrait_cache: Dict[Tuple[str, int], pygame.Surface] = {}
_topdown_cache: Dict[Tuple[str, int], Optional[pygame.Surface]] = {}


def load_portrait_thumbnail(design: DesignMetadata, size: int = 50) -> pygame.Surface:
    """
    Load a portrait thumbnail for the design.

    Results are cached in memory so repeated calls (e.g. on filter refresh)
    return instantly.

    Args:
        design: Design metadata
        size: Thumbnail size (square)

    Returns:
        pygame.Surface with the portrait or a placeholder
    """
    cache_key = (design.design_id, size)
    if cache_key in _portrait_cache:
        return _portrait_cache[cache_key]

    result = _load_portrait_thumbnail_uncached(design, size)
    _portrait_cache[cache_key] = result
    return result


def _load_portrait_thumbnail_uncached(design: DesignMetadata, size: int) -> pygame.Surface:
    """Load portrait thumbnail without cache lookup."""
    theme = design.theme_id or "Federation"
    ship_class = design.ship_class or "Unknown"

    # Normalize class name for filename
    class_clean = ship_class.replace(" ", "_").replace("-", "_")
    filename = f"{class_clean}_Portrait.jpg"

    # Try multiple portrait paths
    portrait_paths = [
        os.path.join("assets", "ShipThemes", theme, "Portraits", filename),
        os.path.join("assets", "ShipThemes", theme, "Portraits", f"{ship_class}_Portrait.jpg"),
        os.path.join("assets", "Images", "Default_Ship_Portrait.png")
    ]

    for path in portrait_paths:
        if os.path.exists(path):
            try:
                loaded_img = pygame.image.load(path)
                return pygame.transform.smoothscale(loaded_img, (size, size))
            except (FileNotFoundError, OSError, pygame.error) as e:
                logger.warning(f"Failed to load portrait '{path}' for design '{design.design_id}': {e}")
                continue

    # Fallback: Create placeholder with gradient
    surface = pygame.Surface((size, size))

    # Color based on vehicle type
    type_colors = {
        "Ship": THUMB_SHIP,
        "Fighter": THUMB_FIGHTER,
        "Satellite": THUMB_SATELLITE,
        "Planetary Complex": THUMB_COMPLEX
    }
    base_color = type_colors.get(design.vehicle_type, PLACEHOLDER_DEFAULT)

    # Gradient fill
    for y in range(size):
        fade = 1.0 - (y / size) * 0.5
        color = tuple(int(c * fade) for c in base_color)
        pygame.draw.line(surface, color, (0, y), (size, y))

    # Add class initial
    font = get_font(int(size * 0.5), bold=True)
    initial = ship_class[0] if ship_class else "?"
    text = font.render(initial, True, THUMB_TEXT)
    text_rect = text.get_rect(center=(size // 2, size // 2))
    surface.blit(text, text_rect)

    # Border
    pygame.draw.rect(surface, SWATCH_BORDER, (0, 0, size, size), 1)

    return surface


def load_topdown_thumbnail(design: DesignMetadata, target_height: int = 50) -> Optional[pygame.Surface]:
    """
    Load a top-down (skin) thumbnail for the design.

    The image is sized based on its visible (non-transparent) portion,
    scaled so the visible height matches target_height. Results are cached.

    Args:
        design: Design metadata
        target_height: Target height for the visible portion

    Returns:
        pygame.Surface with the top-down view, or None if not found
    """
    cache_key = (design.design_id, target_height)
    if cache_key in _topdown_cache:
        return _topdown_cache[cache_key]

    result = _load_topdown_thumbnail_uncached(design, target_height)
    _topdown_cache[cache_key] = result
    return result


def _load_topdown_thumbnail_uncached(design: DesignMetadata, target_height: int) -> Optional[pygame.Surface]:
    """Load top-down thumbnail without cache lookup."""
    theme = design.theme_id or "Federation"
    ship_class = design.ship_class or "Unknown"

    # Normalize class name for filename - try multiple variations
    class_variations = [
        ship_class,
        ship_class.lower(),
        ship_class.replace(" ", "_"),
        ship_class.replace(" ", ""),
        ship_class.lower().replace(" ", "_"),
        ship_class.lower().replace(" ", " "),
    ]

    # Try to find the skin file
    skin_paths = []
    for class_name in class_variations:
        skin_paths.append(os.path.join("assets", "ShipThemes", theme, "Skins", f"{class_name}.png"))

    loaded_img = None
    for path in skin_paths:
        if os.path.exists(path):
            try:
                loaded_img = pygame.image.load(path).convert_alpha()
                break
            except (FileNotFoundError, OSError, pygame.error):
                logger.warning(f"Failed to load skin image: {path}")
                continue

    if loaded_img is None:
        return None

    # Use pygame's native C-level bounding rect (replaces slow pixel-by-pixel scan)
    bbox = loaded_img.get_bounding_rect(min_alpha=10)
    if bbox.width <= 0 or bbox.height <= 0:
        return None

    visible_width = bbox.width
    visible_height = bbox.height

    # Calculate scale to make visible height match target_height
    scale = target_height / visible_height
    new_width = int(loaded_img.get_width() * scale)
    new_height = int(loaded_img.get_height() * scale)

    # Scale the full image
    scaled_img = pygame.transform.smoothscale(loaded_img, (new_width, new_height))

    # Crop to the visible area (scaled)
    scaled_min_x = int(bbox.x * scale)
    scaled_min_y = int(bbox.y * scale)
    scaled_visible_w = int(visible_width * scale)
    scaled_visible_h = int(visible_height * scale)

    # Create final surface with just the visible portion
    final_surface = pygame.Surface((scaled_visible_w, scaled_visible_h), pygame.SRCALPHA)
    final_surface.blit(scaled_img, (0, 0), (scaled_min_x, scaled_min_y, scaled_visible_w, scaled_visible_h))

    return final_surface


def clear_thumbnail_cache():
    """Clear the in-memory thumbnail caches.

    Call this when designs are modified or when starting a new game
    to free memory.
    """
    _portrait_cache.clear()
    _topdown_cache.clear()
