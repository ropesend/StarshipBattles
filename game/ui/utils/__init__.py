"""
UI utility modules.

This package provides reusable helpers for common UI operations:
- pygame_utils: Pygame-specific utilities (scaling, rectangles, etc.)
- json_diff: JSON structure comparison algorithm
"""
# Public API - re-export pygame utilities from submodule
from game.ui.utils.pygame_utils import (
    create_centered_rect,
    calculate_ship_image_scale,
    scale_and_rotate_image,
    get_visible_bounding_box,
    scale_image_by_visible_portion,
    create_section_header,
    scale_image_to_fit,
)

# JSON diff utilities
from game.ui.utils.json_diff import (
    compute_json_diff,
    DiffResult,
    DIFF_IGNORE_KEYS,
)

__all__ = [
    # Pygame utilities
    'create_centered_rect',
    'calculate_ship_image_scale',
    'scale_and_rotate_image',
    'get_visible_bounding_box',
    'scale_image_by_visible_portion',
    'create_section_header',
    'scale_image_to_fit',
    # JSON diff
    'compute_json_diff',
    'DiffResult',
    'DIFF_IGNORE_KEYS',
]
