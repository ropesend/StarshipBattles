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


def get_visible_bounding_box(surface: pygame.Surface, alpha_threshold: int = 10) -> Optional[Tuple[int, int, int, int]]:
    """
    Find the bounding box of the visible (non-transparent) area of a surface.

    Args:
        surface: pygame.Surface with alpha channel
        alpha_threshold: Minimum alpha value to consider visible (default 10)

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
            if pixel[3] > alpha_threshold:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if max_x <= min_x or max_y <= min_y:
        return None

    return (min_x, min_y, max_x + 1, max_y + 1)


def scale_image_by_visible_portion(
    surface: pygame.Surface,
    target_height: int,
    placeholder_width: int = 40,
    placeholder_color: Tuple[int, int, int] = (50, 50, 50)
) -> pygame.Surface:
    """
    Scale an image based on its visible (non-transparent) portion.

    The visible height will match target_height, and the entire image scales
    proportionally to maintain the original aspect ratio.

    Args:
        surface: Source surface with alpha channel
        target_height: Target height for the visible portion
        placeholder_width: Width of placeholder if surface is empty (default 40)
        placeholder_color: Color of placeholder (default dark gray)

    Returns:
        Scaled surface maintaining original aspect ratio
    """
    # Find visible bounding box
    bbox = get_visible_bounding_box(surface)
    if bbox is None:
        # Fully transparent - return placeholder
        placeholder = pygame.Surface((placeholder_width, target_height), pygame.SRCALPHA)
        placeholder.fill(placeholder_color)
        return placeholder

    min_x, min_y, max_x, max_y = bbox
    visible_width = max_x - min_x
    visible_height = max_y - min_y

    if visible_height <= 0 or visible_width <= 0:
        placeholder = pygame.Surface((placeholder_width, target_height), pygame.SRCALPHA)
        placeholder.fill(placeholder_color)
        return placeholder

    # Calculate scale to make visible height match target_height
    scale = target_height / visible_height
    new_width = int(surface.get_width() * scale)
    new_height = int(surface.get_height() * scale)

    if new_width <= 0 or new_height <= 0:
        placeholder = pygame.Surface((placeholder_width, target_height), pygame.SRCALPHA)
        placeholder.fill(placeholder_color)
        return placeholder

    # Scale the full image (maintains original aspect ratio)
    return pygame.transform.smoothscale(surface, (new_width, new_height))


def scale_image_to_fit(
    surface: pygame.Surface,
    target_size: Tuple[int, int],
    background_color: Tuple[int, int, int] = (30, 30, 30)
) -> pygame.Surface:
    """
    Scale an image to fit within target size, centered on background.

    Args:
        surface: Source pygame.Surface
        target_size: (width, height) to fit within
        background_color: Background color (default dark gray)

    Returns:
        New surface with image centered at target_size
    """
    target_w, target_h = target_size
    img_w, img_h = surface.get_size()

    # Calculate scale to fit
    scale = min(target_w / img_w, target_h / img_h)
    new_w, new_h = int(img_w * scale), int(img_h * scale)

    if new_w <= 0 or new_h <= 0:
        result = pygame.Surface(target_size, pygame.SRCALPHA)
        result.fill(background_color)
        return result

    scaled = pygame.transform.smoothscale(surface, (new_w, new_h))

    # Center on target surface
    result = pygame.Surface(target_size, pygame.SRCALPHA)
    result.fill(background_color)
    x_off = (target_w - new_w) // 2
    y_off = (target_h - new_h) // 2
    result.blit(scaled, (x_off, y_off))

    return result
