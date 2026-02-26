"""
UI utility functions for common patterns.

This module provides reusable helpers for common UI operations to
eliminate duplicate code (DRY principle).
"""
from typing import Optional, Tuple
import pygame
from game.ui.colors import TEXT_DIM, GRID_BG


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

    Uses pygame's native C-level get_bounding_rect() for performance.

    Args:
        surface: pygame.Surface with alpha channel
        alpha_threshold: Minimum alpha value to consider visible (default 10)

    Returns:
        Tuple (min_x, min_y, max_x, max_y) or None if fully transparent
    """
    bbox = surface.get_bounding_rect(min_alpha=alpha_threshold)
    if bbox.width <= 0 or bbox.height <= 0:
        return None
    return (bbox.x, bbox.y, bbox.x + bbox.width, bbox.y + bbox.height)


def scale_image_by_visible_portion(
    surface: pygame.Surface,
    target_height: int,
    placeholder_width: int = 40,
    placeholder_color: Tuple[int, int, int] = TEXT_DIM
) -> pygame.Surface:
    """
    Scale an image based on its visible (non-transparent) portion, then crop
    to the visible area so the result is tightly framed.

    The visible height will match target_height, maintaining the original
    aspect ratio of the visible content.

    Args:
        surface: Source surface with alpha channel
        target_height: Target height for the visible portion
        placeholder_width: Width of placeholder if surface is empty (default 40)
        placeholder_color: Color of placeholder (default dark gray)

    Returns:
        Cropped, scaled surface of the visible portion
    """
    # Find visible bounding box
    bbox = get_visible_bounding_box(surface)
    if bbox is None:
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

    # Crop to visible area first, then scale
    visible_rect = pygame.Rect(min_x, min_y, visible_width, visible_height)
    cropped = surface.subsurface(visible_rect).copy()

    # Scale cropped visible content to target_height, maintaining aspect ratio
    scale = target_height / visible_height
    new_width = max(1, int(visible_width * scale))

    return pygame.transform.smoothscale(cropped, (new_width, target_height))


def create_section_header(
    text: str,
    y: int,
    width: int,
    manager,
    container,
    x: int = 10,
    height: int = 25
) -> 'pygame_gui.elements.UILabel':
    """
    Create a standard section header UILabel.

    Consolidates the repeated pattern of creating section header labels
    with consistent styling across UI panels.

    Args:
        text: Header text to display
        y: Vertical position
        width: Label width
        manager: pygame_gui UIManager instance
        container: Parent UI container
        x: Horizontal position (default: 10)
        height: Label height (default: 25)

    Returns:
        The created UILabel element
    """
    import pygame_gui
    return pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(x, y, width, height),
        text=text,
        manager=manager,
        container=container,
        object_id="#section_header"
    )


def scale_image_to_fit(
    surface: pygame.Surface,
    target_size: Tuple[int, int],
    background_color: Tuple[int, int, int] = GRID_BG
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
