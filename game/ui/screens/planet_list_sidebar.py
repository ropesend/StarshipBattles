"""Sidebar builder for Planet List Window.

Extracted from planet_list_window.py (Phase 1) for better modularity.
Builds filter controls, column toggles, and preset management UI.
"""
import pygame
from pygame_gui.elements import (
    UIScrollingContainer, UILabel, UIButton, UITextEntryLine,
    UIHorizontalSlider, UIDropDownMenu
)


def build_sidebar(manager, sidebar_panel, sidebar_width, rect_height,
                  planet_ranges, columns, preset_manager):
    """Build sidebar UI controls for planet list filtering.

    Args:
        manager: pygame_gui UIManager
        sidebar_panel: Parent UIPanel for sidebar
        sidebar_width: Width of sidebar in pixels
        rect_height: Height of parent window
        planet_ranges: Dict with 'gravity', 'temp', 'mass' min/max tuples
        columns: List of column definition dicts
        preset_manager: PresetManager instance for presets

    Returns:
        Dict containing all widget references needed by main window:
        - sidebar_scroller: UIScrollingContainer
        - txt_name_filter: UITextEntryLine for name search
        - btn_all_types, btn_none_types: Type filter buttons
        - btn_all_owners, btn_none_owners: Owner filter buttons
        - btn_apply: Apply filters button
        - btn_save_preset: Save preset button
        - txt_preset_name: UITextEntryLine for preset name
        - dd_presets: UIDropDownMenu for preset selection
        - ui_filters: Dict containing filter widget references
    """
    # Use a scrolling container for the sidebar because filters are tall
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

    # --- Planet Type ---
    UILabel(pygame.Rect(10, y_off, width, 20), "Planet Type:", manager, container=content_container)
    y_off += 25

    # All / None Buttons
    btn_all_types = UIButton(pygame.Rect(10, y_off, 60, 25), "All", manager, container=content_container)
    btn_none_types = UIButton(pygame.Rect(80, y_off, 60, 25), "None", manager, container=content_container)
    y_off += 30

    # Grid of checkboxes
    types = [
        'Continental', 'Arid', 'Pelagic', 'Magma', 'Cryoplanet',
        'Barren', 'Jovian', 'Ice Giant', 'Chthonian', 'Ice Dwarf', 'Planetoid'
    ]
    ui_filters['types'] = {}

    x_start = 10
    x = x_start
    for t in types:
        btn = UIButton(
            relative_rect=pygame.Rect(x, y_off, 80, 30),
            text=t,
            manager=manager,
            container=content_container,
            object_id='@filter_toggle_on'
        )
        ui_filters['types'][t] = btn

        x += 90
        if x > width - 80:
            x = x_start
            y_off += 35
    if x != x_start:
        y_off += 35

    # --- Owner Filter --- (BUG-27)
    UILabel(pygame.Rect(10, y_off, width, 20), "Owner:", manager, container=content_container)
    y_off += 25

    # All / None Buttons for owner
    btn_all_owners = UIButton(pygame.Rect(10, y_off, 60, 25), "All", manager, container=content_container)
    btn_none_owners = UIButton(pygame.Rect(80, y_off, 60, 25), "None", manager, container=content_container)
    y_off += 30

    # Owner toggle buttons
    owners = ['Player', 'Enemy', 'Unowned']
    ui_filters['owners'] = {}

    x = x_start
    for o in owners:
        btn = UIButton(
            relative_rect=pygame.Rect(x, y_off, 80, 30),
            text=o,
            manager=manager,
            container=content_container,
            object_id='@filter_toggle_on'
        )
        ui_filters['owners'][o] = btn
        x += 90
        if x > width - 80:
            x = x_start
            y_off += 35
    if x != x_start:
        y_off += 35

    # --- Range Sliders ---
    def add_range(label, key, min_limit, max_limit):
        nonlocal y_off
        UILabel(pygame.Rect(10, y_off, width, 20), label, manager, container=content_container)
        y_off += 20

        # Min Row
        UILabel(pygame.Rect(10, y_off, 30, 24), "Min", manager, container=content_container)
        s_min = UIHorizontalSlider(
            relative_rect=pygame.Rect(45, y_off, width - 105, 24),
            start_value=min_limit,
            value_range=(min_limit, max_limit),
            manager=manager,
            container=content_container
        )
        t_min = UITextEntryLine(
            relative_rect=pygame.Rect(width - 55, y_off, 55, 24),
            manager=manager,
            container=content_container
        )
        t_min.set_text(f"{min_limit:.1f}")
        y_off += 29

        # Max Row
        UILabel(pygame.Rect(10, y_off, 30, 24), "Max", manager, container=content_container)
        s_max = UIHorizontalSlider(
            relative_rect=pygame.Rect(45, y_off, width - 105, 24),
            start_value=max_limit,
            value_range=(min_limit, max_limit),
            manager=manager,
            container=content_container
        )
        t_max = UITextEntryLine(
            relative_rect=pygame.Rect(width - 55, y_off, 55, 24),
            manager=manager,
            container=content_container
        )
        t_max.set_text(f"{max_limit:.1f}")
        y_off += 35

        ui_filters[key] = {
            'min': s_min, 'max': s_max,
            'min_txt': t_min, 'max_txt': t_max,
            'limits': (min_limit, max_limit)
        }

    # Use dynamic ranges computed from actual planet data
    grav_range = planet_ranges['gravity']
    temp_range = planet_ranges['temp']
    mass_range = planet_ranges['mass']

    add_range("Gravity (g)", 'gravity', grav_range[0], grav_range[1])
    add_range("Temp (K)", 'temp', temp_range[0], temp_range[1])
    add_range("Mass (Earths)", 'mass', mass_range[0], mass_range[1])

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
        'btn_all_owners': btn_all_owners,
        'btn_none_owners': btn_none_owners,
        'btn_apply': btn_apply,
        'btn_save_preset': btn_save_preset,
        'txt_preset_name': txt_preset_name,
        'dd_presets': dd_presets,
        'ui_filters': ui_filters
    }
