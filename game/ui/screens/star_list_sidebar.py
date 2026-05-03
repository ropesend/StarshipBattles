"""Sidebar builder for Star List Window.

Builds filter controls, column toggles, and preset management UI.
Mirrors planet_list_sidebar.py for stars.

PROJ-231: Star List Panel.
"""
from __future__ import annotations

from typing import Any

import pygame
from pygame_gui.elements import (
    UIScrollingContainer, UILabel, UIButton, UITextEntryLine,
    UIDropDownMenu
)

from game.ui.screens.star_list_filter_manager import STAR_TYPES
from game.ui.widgets.range_slider_builder import build_range_slider_row


def build_sidebar(manager, sidebar_panel, sidebar_width, rect_height,
                  star_ranges, columns, preset_manager) -> dict[str, Any]:
    """Build sidebar UI controls for star list filtering.

    Args:
        manager: pygame_gui UIManager
        sidebar_panel: Parent UIPanel for sidebar
        sidebar_width: Width of sidebar in pixels
        rect_height: Height of parent window
        star_ranges: Dict with 'mass', 'temperature', etc. min/max tuples
        columns: List of column definition dicts
        preset_manager: PresetManager instance for presets

    Returns:
        Dict containing all widget references needed by main window.
    """
    sidebar_scroller = UIScrollingContainer(
        relative_rect=pygame.Rect(0, 0, sidebar_width, rect_height - 50),
        manager=manager,
        container=sidebar_panel,
        anchors={'left': 'left', 'right': 'right', 'top': 'top', 'bottom': 'bottom'}
    )
    content_container = sidebar_scroller.get_container()

    y_off = 10
    width = sidebar_width - 30  # Account for scrollbar

    ui_filters = {}

    # Title
    UILabel(pygame.Rect(10, y_off, width, 25), "FILTERS", manager, container=content_container)
    y_off += 30

    # Name Filter
    txt_name_filter = UITextEntryLine(
        relative_rect=pygame.Rect(10, y_off, width, 30),
        manager=manager,
        container=content_container
    )
    txt_name_filter.set_text("Search Name...")
    y_off += 40

    # --- Star Type ---
    UILabel(pygame.Rect(10, y_off, width, 20), "Star Type:", manager, container=content_container)
    y_off += 25

    btn_all_types = UIButton(pygame.Rect(10, y_off, 60, 25), "All", manager, container=content_container)
    btn_none_types = UIButton(pygame.Rect(80, y_off, 60, 25), "None", manager, container=content_container)
    y_off += 30

    ui_filters['types'] = {}

    x_start = 10
    x = x_start
    for t in STAR_TYPES:
        btn = UIButton(
            relative_rect=pygame.Rect(x, y_off, 105, 30),
            text=t,
            manager=manager,
            container=content_container,
            object_id='@filter_toggle_on'
        )
        ui_filters['types'][t] = btn

        x += 115
        if x > width - 105:
            x = x_start
            y_off += 35
    if x != x_start:
        y_off += 35

    # --- Range Sliders ---
    def add_range(label, key, min_limit, max_limit) -> None:
        nonlocal y_off
        y_off, ui_filters[key] = build_range_slider_row(
            label, key, min_limit, max_limit, y_off, width, manager, content_container,
        )

    mass_range = star_ranges['mass']
    temp_range = star_ranges['temperature']
    lum_range = star_ranges['luminosity']
    age_range = star_ranges['age']
    radius_range = star_ranges['radius_hexes']

    add_range("Mass (Solar)", 'mass', mass_range[0], mass_range[1])
    add_range("Temp (K)", 'temperature', temp_range[0], temp_range[1])
    add_range("Luminosity (Solar)", 'luminosity', lum_range[0], lum_range[1])
    add_range("Age (Years)", 'age', age_range[0], age_range[1])
    add_range("Radius (Hexes)", 'radius_hexes', radius_range[0], radius_range[1])

    # Button: Apply Filters
    btn_apply = UIButton(
        relative_rect=pygame.Rect(10, y_off, width, 30),
        text="Apply Filters",
        manager=manager,
        container=content_container
    )
    y_off += 40

    # --- Column Configuration ---
    UILabel(pygame.Rect(10, y_off, width, 25), "COLUMNS", manager, container=content_container)
    y_off += 30

    ui_filters['columns'] = {}
    for col in columns:
        t = f"[x] {col['title'] or col['id']}" if col['visible'] else f"[ ] {col['title'] or col['id']}"
        btn = UIButton(
            relative_rect=pygame.Rect(10, y_off, width, 30),
            text=t,
            manager=manager,
            container=content_container
        )
        btn.col_ref = col
        ui_filters['columns'][col['id']] = btn
        y_off += 35

    y_off += 20
    UILabel(pygame.Rect(10, y_off, width, 25), "PRESETS", manager, container=content_container)
    y_off += 30

    dd_presets = UIDropDownMenu(
        options_list=preset_manager.get_preset_names(),
        starting_option="Default",
        relative_rect=pygame.Rect(10, y_off, width, 30),
        manager=manager,
        container=content_container
    )
    y_off += 40

    # Save New
    txt_preset_name = UITextEntryLine(
        relative_rect=pygame.Rect(10, y_off, width - 60, 30),
        manager=manager,
        container=content_container
    )
    txt_preset_name.set_text("New Preset Name")

    btn_save_preset = UIButton(
        relative_rect=pygame.Rect(width - 50, y_off, 50, 30),
        text="Save",
        manager=manager,
        container=content_container
    )
    y_off += 40

    # Update scrolling area
    sidebar_scroller.set_scrollable_area_dimensions((width, y_off))

    return {
        'sidebar_scroller': sidebar_scroller,
        'txt_name_filter': txt_name_filter,
        'btn_all_types': btn_all_types,
        'btn_none_types': btn_none_types,
        'btn_apply': btn_apply,
        'btn_save_preset': btn_save_preset,
        'txt_preset_name': txt_preset_name,
        'dd_presets': dd_presets,
        'ui_filters': ui_filters,
    }
