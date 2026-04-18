"""PROJ-282 Phase 4: left-panel renderer for `FleetBattleSetupScreen`.

Builds the left-side pygame_gui panel: side dropdown, fleet list, complex
toggle buttons, end-condition controls. Mutates the screen's handle
attributes directly (`screen._side_dropdown`, `screen._fleet_buttons`,
etc.) — Phase 8 consolidates handles onto a dedicated dataclass when the
screen is reduced to a thin shell.
"""
from __future__ import annotations

import pygame
from pygame_gui.elements import UIPanel, UIButton, UILabel, UITextEntryLine, UIDropDownMenu


# Complex design tables live on the screen module for now (they're
# imported here). Keeping them screen-module-local preserves Phase 2's
# minimal-change footprint; Phase 4+ could relocate these to a shared
# module if needed.


def build(screen, width: int, height: int) -> None:
    """Build the left panel. Mutates `screen` in-place with pygame_gui handles."""
    from game.ui.screens.battle_setup.constants import (
        _SYSTEM_SCOPE_COMPLEXES,
        _SECTOR_SCOPE_COMPLEXES,
    )
    from game.ui.screens.battle_setup_state import MIN_SIDES, MAX_SIDES

    panel = UIPanel(
        relative_rect=pygame.Rect(0, 0, width, height),
        manager=screen._ui_manager, object_id='#left_panel'
    )
    y = 10

    UILabel(pygame.Rect(10, y, width - 20, 30), "Battle Setup",
            manager=screen._ui_manager, container=panel)
    y += 35

    # Side selector (PROJ-282 Phase 11: dynamically populated from state.sides).
    UILabel(pygame.Rect(10, y, 50, 25), "Side:",
            manager=screen._ui_manager, container=panel)
    num_sides = len(screen.state.sides)
    side_options = [f"Side {i}" for i in range(num_sides)]
    # Clamp active_side into range — defensive against stale view_model state
    # after a remove_side that didn't reconcile.
    active_side_display = max(0, min(screen.active_side, num_sides - 1))
    screen._side_dropdown = UIDropDownMenu(
        side_options,
        f"Side {active_side_display}",
        pygame.Rect(60, y, width - 70, 28),
        manager=screen._ui_manager, container=panel
    )
    y += 35

    # Add-Side / Remove-Side buttons (PROJ-282 Phase 11).
    half_w = (width - 30) // 2
    add_label = "Add Side" if num_sides < MAX_SIDES else f"Add Side (max {MAX_SIDES})"
    screen._add_side_btn = UIButton(
        pygame.Rect(10, y, half_w, 26), add_label,
        manager=screen._ui_manager, container=panel,
    )
    if num_sides >= MAX_SIDES:
        screen._add_side_btn.disable()

    remove_label = "Remove Side" if num_sides > MIN_SIDES else f"Remove (min {MIN_SIDES})"
    screen._remove_side_btn = UIButton(
        pygame.Rect(20 + half_w, y, half_w, 26), remove_label,
        manager=screen._ui_manager, container=panel,
    )
    if num_sides <= MIN_SIDES:
        screen._remove_side_btn.disable()
    y += 32

    # Fleet list
    UILabel(pygame.Rect(10, y, width - 20, 22), "Fleets:",
            manager=screen._ui_manager, container=panel)
    y += 25

    side = screen.state.get_side(screen.active_side)
    screen._fleet_buttons = []
    for i, fleet in enumerate(side.fleets):
        name = getattr(fleet, '_battle_setup_name', f"Fleet {fleet.id}")
        ship_count = len(fleet.ships)
        btn = UIButton(
            pygame.Rect(10, y, width - 20, 28),
            f"{'> ' if i == screen.active_fleet_index else '  '}{name} ({ship_count} ships)",
            manager=screen._ui_manager, container=panel
        )
        btn._fleet_index = i
        screen._fleet_buttons.append(btn)
        y += 30

    # Fleet management buttons
    y += 5
    half_w = (width - 30) // 2
    screen._add_fleet_btn = UIButton(
        pygame.Rect(10, y, half_w, 28), "Add Fleet",
        manager=screen._ui_manager, container=panel
    )
    screen._remove_fleet_btn = UIButton(
        pygame.Rect(20 + half_w, y, half_w, 28), "Remove Fleet",
        manager=screen._ui_manager, container=panel
    )
    y += 35

    # System complexes section
    UILabel(pygame.Rect(10, y, width - 20, 22), "System Complexes:",
            manager=screen._ui_manager, container=panel)
    y += 25

    screen._system_complex_btns = []
    for design_id, display_name in _SYSTEM_SCOPE_COMPLEXES:
        is_on = screen._get_toggle(screen.active_side, "system", design_id)
        icon = "[X]" if is_on else "[  ]"
        btn = UIButton(
            pygame.Rect(10, y, width - 20, 24),
            f"{icon} {display_name}",
            manager=screen._ui_manager, container=panel
        )
        btn._complex_key = (screen.active_side, "system", design_id)
        btn._complex_design_id = design_id
        screen._system_complex_btns.append(btn)
        y += 26

    y += 5
    # Sector complexes section
    UILabel(pygame.Rect(10, y, width - 20, 22), "Sector Complexes:",
            manager=screen._ui_manager, container=panel)
    y += 25

    screen._sector_complex_btns = []
    for design_id, display_name in _SECTOR_SCOPE_COMPLEXES:
        is_on = screen._get_toggle(screen.active_side, "sector", design_id)
        icon = "[X]" if is_on else "[  ]"
        btn = UIButton(
            pygame.Rect(10, y, width - 20, 24),
            f"{icon} {display_name}",
            manager=screen._ui_manager, container=panel
        )
        btn._complex_key = (screen.active_side, "sector", design_id)
        btn._complex_design_id = design_id
        screen._sector_complex_btns.append(btn)
        y += 26

    # End conditions section
    y += 5
    UILabel(pygame.Rect(10, y, width - 20, 22), "End Conditions:",
            manager=screen._ui_manager, container=panel)
    y += 25

    # Tick limit
    UILabel(pygame.Rect(10, y, 60, 22), "Ticks:",
            manager=screen._ui_manager, container=panel)
    screen._tick_limit_entry = UITextEntryLine(
        pygame.Rect(70, y, width - 80, 24),
        manager=screen._ui_manager, container=panel
    )
    screen._tick_limit_entry.set_text(str(screen.tick_limit))
    y += 28

    # End mode toggles
    screen._end_destroyed_btn = UIButton(
        pygame.Rect(10, y, width - 20, 24),
        f"{'[X]' if screen.end_all_destroyed else '[  ]'} All Destroyed",
        manager=screen._ui_manager, container=panel
    )
    y += 26

    screen._end_derelict_btn = UIButton(
        pygame.Rect(10, y, width - 20, 24),
        f"{'[X]' if screen.end_all_derelict else '[  ]'} All Derelict/Destroyed",
        manager=screen._ui_manager, container=panel
    )
    y += 26

    screen._end_mass_btn = UIButton(
        pygame.Rect(10, y, width - 20, 24),
        f"{'[X]' if screen.end_mass_ratio else '[  ]'} Mass Ratio < {screen.mass_ratio_threshold:.0%}",
        manager=screen._ui_manager, container=panel
    )
    y += 26
