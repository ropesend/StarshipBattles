"""
UI utility functions for common patterns.

This module provides reusable helpers for common UI operations to
eliminate duplicate code (DRY principle).
"""
from typing import Optional, Tuple
import pygame


def create_centered_rect(width: int, height: int, screen_width: int, screen_height: int) -> pygame.Rect:
    """
    Create a pygame.Rect centered on the screen.

    Args:
        width: Width of the rectangle
        height: Height of the rectangle
        screen_width: Width of the screen/container
        screen_height: Height of the screen/container

    Returns:
        A pygame.Rect centered on the screen
    """
    return pygame.Rect(
        (screen_width - width) // 2,
        (screen_height - height) // 2,
        width,
        height
    )


def calculate_ship_image_scale(
    image_size: Tuple[int, int],
    target_size: float,
    visible_size: Optional[float] = None,
    manual_scale: float = 1.0
) -> float:
    """
    Calculate the scale factor for a ship image to fit a target size.

    This centralizes the ship image scaling logic used throughout the UI
    for consistent ship rendering.

    Args:
        image_size: Original image dimensions (width, height)
        target_size: Target diameter/size in pixels
        visible_size: Actual visible content size (from metrics), defaults to max(image_size)
        manual_scale: Manual scale multiplier from theme config (default 1.0)

    Returns:
        Scale factor to apply to the image
    """
    img_w, img_h = image_size

    # Use visible size from metrics, or fall back to image dimensions
    if visible_size is None or visible_size < 1:
        visible_size = max(img_w, img_h)

    # Avoid division by zero
    if visible_size < 1:
        visible_size = 1

    return (target_size / visible_size) * manual_scale


def scale_and_rotate_image(
    image: pygame.Surface,
    scale_factor: float,
    rotation: float = 0.0
) -> pygame.Surface:
    """
    Scale and optionally rotate a pygame surface.

    Args:
        image: Source pygame.Surface
        scale_factor: Scale multiplier
        rotation: Rotation angle in degrees (default 0)

    Returns:
        Scaled and rotated pygame.Surface, or original if scale would be invalid
    """
    img_w, img_h = image.get_size()
    new_w = int(img_w * scale_factor)
    new_h = int(img_h * scale_factor)

    if new_w <= 0 or new_h <= 0:
        return image

    scaled = pygame.transform.scale(image, (new_w, new_h))

    if rotation != 0.0:
        return pygame.transform.rotate(scaled, rotation)

    return scaled
