"""PROJ-282 Phase 5 + 6: `BattleSetupInputHandler`.

Translates pygame_gui events (`UI_BUTTON_PRESSED`, `UI_DROP_DOWN_MENU_CHANGED`)
into `BattleSetupController` mutation calls and ViewModel selection
updates.

**Scope boundary:** the handler knows nothing about pygame_gui element
construction (that's the Renderer's job). It reads element identity
(`event.ui_element == screen._start_btn`) from the screen's handle
attributes, and custom tags attached by panel builders
(`element._fleet_index`, `element._complex_key`, etc.).

**Phase 6 retarget:** mutation dispatch now routes to
`screen.controller.*` (e.g. `add_ship_from_design`,
`duplicate_task_force`, `start_battle`). Selection-only updates stay on
`screen.view_model.*` directly — selections aren't state mutations. The
screen is still referenced for pygame_gui element-handle identity
comparisons (named buttons and dropdowns owned by the renderer).
"""
from __future__ import annotations

import pygame_gui


class BattleSetupInputHandler:
    """Routes pygame_gui events to screen mutation methods and view_model
    selection updates. Holds a reference to the owning screen — the
    screen's handle attributes + mutation methods are both read here."""

    def __init__(self, screen) -> None:
        self._screen = screen

    # === Public entry point ===

    def handle_event(self, event) -> None:
        """Dispatch `event` to the appropriate handler based on type."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button(event)
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            self._handle_dropdown(event)

    # === Button dispatch ===

    def _handle_button(self, event) -> None:
        screen = self._screen
        view_model = screen.view_model
        controller = screen.controller
        element = event.ui_element

        # Fleet selection — view-state only, no mutation.
        if hasattr(element, '_fleet_index'):
            view_model.active_fleet_index = element._fleet_index
            view_model.selected_tf_index = None
            view_model.selected_sq_index = None
            screen._rebuild_ui()
            return

        # Ship selection (click to show strategy dropdown).
        if hasattr(element, '_ship_index') and not hasattr(element, '_remove_ship_index'):
            view_model.selected_ship_index = element._ship_index
            screen._rebuild_ui()
            return

        # Design buttons — add ship.
        if hasattr(element, '_design_index'):
            controller.add_ship_from_design(element._design_index)
            return

        # Remove ship.
        if hasattr(element, '_remove_ship_index'):
            controller.remove_ship(element._remove_ship_index)
            return

        # Complex toggles.
        if hasattr(element, '_complex_key'):
            side_id, scope, design_id = element._complex_key
            controller.toggle_complex(side_id, scope, design_id)
            return

        # Task force selection.
        if hasattr(element, '_tf_index'):
            view_model.selected_tf_index = element._tf_index
            view_model.selected_sq_index = None
            screen._rebuild_ui()
            return

        # Squadron selection (plain SQ buttons only — dup/del carry their own tags).
        if hasattr(element, '_sq_tf_index') and hasattr(element, '_sq_index'):
            if not hasattr(element, '_dup_sq_tf_index') and not hasattr(element, '_del_sq_tf_index'):
                view_model.selected_tf_index = element._sq_tf_index
                view_model.selected_sq_index = element._sq_index
                screen._rebuild_ui()
                return

        # Task force duplication.
        if hasattr(element, '_dup_tf_index'):
            controller.duplicate_task_force(element._dup_tf_index)
            return

        # Task force deletion.
        if hasattr(element, '_del_tf_index'):
            controller.delete_task_force(element._del_tf_index)
            return

        # Squadron duplication.
        if hasattr(element, '_dup_sq_tf_index'):
            controller.duplicate_squadron(element._dup_sq_tf_index, element._dup_sq_index)
            return

        # Squadron deletion.
        if hasattr(element, '_del_sq_tf_index'):
            controller.delete_squadron(element._del_sq_tf_index, element._del_sq_index)
            return

        # Named action buttons.
        if element == screen._start_btn:
            # Read the tick-limit text entry before launch — the user may
            # have typed a new value without committing it elsewhere.
            self._push_tick_limit_to_controller()
            controller.start_battle(headless=False)
        elif element == screen._headless_btn:
            self._push_tick_limit_to_controller()
            controller.start_battle(headless=True)
        elif element == screen._save_btn:
            controller.save_setup()
        elif element == screen._load_btn:
            controller.load_setup()
        elif element == screen._return_btn:
            controller.return_to_menu()
        elif element == screen._add_fleet_btn:
            controller.add_fleet()
        elif element == screen._remove_fleet_btn:
            controller.remove_fleet()
        elif hasattr(screen, '_add_side_btn') and element == screen._add_side_btn:
            controller.add_side()
        elif hasattr(screen, '_remove_side_btn') and element == screen._remove_side_btn:
            # Remove the currently-active side.
            controller.remove_side(screen.view_model.active_side)
        elif hasattr(screen, '_add_tf_btn') and element == screen._add_tf_btn:
            controller.add_task_force()
        elif hasattr(screen, '_add_sq_btn') and element == screen._add_sq_btn:
            controller.add_squadron()
        elif hasattr(screen, '_end_destroyed_btn') and element == screen._end_destroyed_btn:
            controller.toggle_end_destroyed()
        elif hasattr(screen, '_end_derelict_btn') and element == screen._end_derelict_btn:
            controller.toggle_end_derelict()
        elif hasattr(screen, '_end_mass_btn') and element == screen._end_mass_btn:
            controller.toggle_end_mass_ratio()

    def _push_tick_limit_to_controller(self) -> None:
        """Read the tick-limit text entry (if the renderer built one) and
        push the value to the controller before battle launch."""
        screen = self._screen
        entry = getattr(screen, '_tick_limit_entry', None)
        if entry is not None and hasattr(entry, 'get_text'):
            screen.controller.set_tick_limit_from_text(entry.get_text())

    # === Dropdown dispatch ===

    def _handle_dropdown(self, event) -> None:
        screen = self._screen
        controller = screen.controller

        if event.ui_element == screen._side_dropdown:
            # PROJ-282 Phase 11: parse the "Side N" format (N up to 7).
            # Fallback to 0 on unexpected formats — keeps the UI safe if
            # panels drift from the expected string shape.
            try:
                side_id = int(event.text.split()[-1])
            except (ValueError, IndexError):
                side_id = 0
            controller.set_active_side(side_id)
        elif hasattr(screen, '_fleet_role_dropdown') and event.ui_element == screen._fleet_role_dropdown:
            controller.set_fleet_battle_role(event.text)
        elif screen._targeting_dropdown and event.ui_element == screen._targeting_dropdown:
            controller.set_selected_policy("targeting", event.text)
        elif screen._movement_dropdown and event.ui_element == screen._movement_dropdown:
            controller.set_selected_policy("movement", event.text)
        elif (
            screen._ship_targeting_dropdown
            and event.ui_element == screen._ship_targeting_dropdown
        ):
            from game.ui.screens.battle_setup.constants import _TARGETING_OPTIONS
            controller.set_ship_policy("_targeting_policy", event.text, _TARGETING_OPTIONS)
        elif (
            screen._ship_movement_dropdown
            and event.ui_element == screen._ship_movement_dropdown
        ):
            from game.ui.screens.battle_setup.constants import _MOVEMENT_OPTIONS
            controller.set_ship_policy("_movement_policy", event.text, _MOVEMENT_OPTIONS)
