"""
Design Image Helper - Utility functions for loading design thumbnail images.

This module provides pure functions for loading portrait and top-down (skin)
thumbnails for ship designs. These functions have no dependency on UI state
and can be used by any component that needs to display design images.

Functions:
    load_portrait_thumbnail: Load a portrait image for a design.
    load_topdown_thumbnail: Load a top-down skin image for a design.
"""
from __future__ import annotations

import os
import pygame
from typing import Optional, TYPE_CHECKING

from game.core.logger import log_warning

if TYPE_CHECKING:
    from game.strategy.data.design_metadata import DesignMetadata


def load_portrait_thumbnail(design: DesignMetadata, size: int = 50) -> pygame.Surface:
    """
    Load a portrait thumbnail for the design.

    Args:
        design: Design metadata
        size: Thumbnail size (square)

    Returns:
        pygame.Surface with the portrait or a placeholder
    """
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
                log_warning(f"Failed to load portrait '{path}' for design '{design.design_id}': {e}")
                continue

    # Fallback: Create placeholder with gradient
    surface = pygame.Surface((size, size))

    # Color based on vehicle type
    type_colors = {
        "Ship": (60, 80, 120),
        "Fighter": (80, 100, 60),
        "Satellite": (100, 80, 100),
        "Planetary Complex": (90, 70, 50)
    }
    base_color = type_colors.get(design.vehicle_type, (80, 80, 80))

    # Gradient fill
    for y in range(size):
        fade = 1.0 - (y / size) * 0.5
        color = tuple(int(c * fade) for c in base_color)
        pygame.draw.line(surface, color, (0, y), (size, y))

    # Add class initial
    font = pygame.font.SysFont("arial", int(size * 0.5), bold=True)
    initial = ship_class[0] if ship_class else "?"
    text = font.render(initial, True, (200, 200, 200))
    text_rect = text.get_rect(center=(size // 2, size // 2))
    surface.blit(text, text_rect)

    # Border
    pygame.draw.rect(surface, (100, 100, 100), (0, 0, size, size), 1)

    return surface


def load_topdown_thumbnail(design: DesignMetadata, target_height: int = 50) -> Optional[pygame.Surface]:
    """
    Load a top-down (skin) thumbnail for the design.

    The image is sized based on its visible (non-transparent) portion,
    scaled so the visible height matches target_height.

    Args:
        design: Design metadata
        target_height: Target height for the visible portion

    Returns:
        pygame.Surface with the top-down view, or None if not found
    """
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
                log_warning(f"Failed to load skin image: {path}")
                continue

    if loaded_img is None:
        return None

    # Find the visible bounding box (non-transparent area)
    bbox = _get_visible_bounding_box(loaded_img)
    if bbox is None:
        return None

    min_x, min_y, max_x, max_y = bbox
    visible_width = max_x - min_x
    visible_height = max_y - min_y

    if visible_height <= 0 or visible_width <= 0:
        return None

    # Calculate scale to make visible height match target_height
    scale = target_height / visible_height
    new_width = int(loaded_img.get_width() * scale)
    new_height = int(loaded_img.get_height() * scale)

    # Scale the full image
    scaled_img = pygame.transform.smoothscale(loaded_img, (new_width, new_height))

    # Crop to the visible area (scaled)
    scaled_min_x = int(min_x * scale)
    scaled_min_y = int(min_y * scale)
    scaled_visible_w = int(visible_width * scale)
    scaled_visible_h = int(visible_height * scale)

    # Create final surface with just the visible portion
    final_surface = pygame.Surface((scaled_visible_w, scaled_visible_h), pygame.SRCALPHA)
    final_surface.blit(scaled_img, (0, 0), (scaled_min_x, scaled_min_y, scaled_visible_w, scaled_visible_h))

    return final_surface


def _get_visible_bounding_box(surface: pygame.Surface) -> Optional[tuple]:
    """
    Find the bounding box of the visible (non-transparent) area of a surface.

    Args:
        surface: pygame.Surface with alpha channel

    Returns:
        Tuple (min_x, min_y, max_x, max_y) or None if fully transparent
    """
    width = surface.get_width()
    height = surface.get_height()

    min_x, min_y = width, height
    max_x, max_y = 0, 0

    # Check each pixel for non-transparent content
    for y in range(height):
        for x in range(width):
            pixel = surface.get_at((x, y))
            if pixel[3] > 10:  # Alpha > 10 (not fully transparent)
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if max_x < min_x or max_y < min_y:
        return None

    return (min_x, min_y, max_x + 1, max_y + 1)
