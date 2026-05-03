"""Shared range-slider row builder for filter sidebars.

Extracted in PROJ-319 (DUP-X-07) to remove the duplicated `add_range` nested
function that previously lived in `planet_list_sidebar.py` and
`star_list_sidebar.py`. Both sidebars build identical Min/Max rows with
slider + text-entry pairs for range filters.
"""
from typing import Any, Dict, Tuple

import pygame
from pygame_gui.elements import UILabel, UIHorizontalSlider, UITextEntryLine


def build_range_slider_row(
    label: str,
    key: str,
    min_limit: float,
    max_limit: float,
    y_off: int,
    width: int,
    manager: Any,
    container: Any,
) -> Tuple[int, Dict[str, Any]]:
    """Build a labelled Min/Max slider+text-entry filter row.

    Args:
        label: Section label (e.g. "Gravity (g)").
        key: Filter dict key (used by the caller for `ui_filters[key]`).
        min_limit, max_limit: Slider value range; also seeded as initial slider/text values.
        y_off: Starting y position inside the sidebar.
        width: Sidebar content width.
        manager: pygame_gui UIManager.
        container: Parent UIPanel/container.

    Returns:
        (new_y_off, filter_entry) where filter_entry is the dict the caller
        should assign to `ui_filters[key]`. Shape:
            {"min": s_min, "max": s_max, "min_txt": t_min, "max_txt": t_max,
             "limits": (min_limit, max_limit)}
    """
    UILabel(pygame.Rect(10, y_off, width, 20), label, manager, container=container)
    y_off += 20

    UILabel(pygame.Rect(10, y_off, 30, 24), "Min", manager, container=container)
    s_min = UIHorizontalSlider(
        relative_rect=pygame.Rect(45, y_off, width - 105, 24),
        start_value=min_limit,
        value_range=(min_limit, max_limit),
        manager=manager,
        container=container,
    )
    t_min = UITextEntryLine(
        relative_rect=pygame.Rect(width - 55, y_off, 55, 24),
        manager=manager,
        container=container,
    )
    t_min.set_text(f"{min_limit:.1f}")
    y_off += 29

    UILabel(pygame.Rect(10, y_off, 30, 24), "Max", manager, container=container)
    s_max = UIHorizontalSlider(
        relative_rect=pygame.Rect(45, y_off, width - 105, 24),
        start_value=max_limit,
        value_range=(min_limit, max_limit),
        manager=manager,
        container=container,
    )
    t_max = UITextEntryLine(
        relative_rect=pygame.Rect(width - 55, y_off, 55, 24),
        manager=manager,
        container=container,
    )
    t_max.set_text(f"{max_limit:.1f}")
    y_off += 35

    filter_entry = {
        "min": s_min,
        "max": s_max,
        "min_txt": t_min,
        "max_txt": t_max,
        "limits": (min_limit, max_limit),
    }
    return y_off, filter_entry
