"""PROJ-282 Phase 5: `BattleSetupInputHandler`.

Translates pygame_gui events (`UI_BUTTON_PRESSED`, `UI_DROP_DOWN_MENU_CHANGED`)
into screen mutation calls and ViewModel selection updates. Lifts
`FleetBattleSetupScreen._handle_button` + `_handle_dropdown` out of the
screen.

**Scope boundary:** the handler knows nothing about pygame_gui element
construction (that's the Renderer's job). It reads element identity
(`event.ui_element == screen._start_btn`) and custom tags attached by
panel builders (`element._fleet_index`, `element._complex_key`, etc.).

**Why the handler talks to `screen` directly:** the mutation methods
(`_add_ship_from_design`, `_duplicate_task_force`, `_start_battle`, ...)
still live on the screen at this phase. Phase 6's `BattleSetupController`
will pull them off — at which point these `screen.*` calls become
`controller.*` calls. Until then, the screen is the Controller's stand-in.
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
        element = event.ui_element

        # Fleet selection
        if hasattr(element, '_fleet_index'):
            view_model.active_fleet_index = element._fleet_index
            view_model.selected_tf_index = None
            view_model.selected_sq_index = None
            screen._rebuild_ui()
            return

        # Ship selection (click to show strategy dropdown)
        if hasattr(element, '_ship_index') and not hasattr(element, '_remove_ship_index'):
            view_model.selected_ship_index = element._ship_index
            screen._rebuild_ui()
            return

        # Design buttons — add ship
        if hasattr(element, '_design_index'):
            screen._add_ship_from_design(element._design_index)
            return

        # Remove ship
        if hasattr(element, '_remove_ship_index'):
            screen._remove_ship(element._remove_ship_index)
            return

        # Complex toggles
        if hasattr(element, '_complex_key'):
            side_id, scope, design_id = element._complex_key
            screen._set_toggle(
                side_id, scope, design_id,
                not screen._get_toggle(side_id, scope, design_id),
            )
            screen._rebuild_ui()
            return

        # Task force selection (click TF to set as target for new ships)
        if hasattr(element, '_tf_index'):
            view_model.selected_tf_index = element._tf_index
            view_model.selected_sq_index = None
            screen._rebuild_ui()
            return

        # Squadron selection (click SQ to set as target for new ships).
        # Only fire for plain SQ buttons — dup/del buttons carry their own
        # tags and are handled below.
        if hasattr(element, '_sq_tf_index') and hasattr(element, '_sq_index'):
            if not hasattr(element, '_dup_sq_tf_index') and not hasattr(element, '_del_sq_tf_index'):
                view_model.selected_tf_index = element._sq_tf_index
                view_model.selected_sq_index = element._sq_index
                screen._rebuild_ui()
                return

        # Task force duplication
        if hasattr(element, '_dup_tf_index'):
            screen._duplicate_task_force(element._dup_tf_index)
            return

        # Task force deletion
        if hasattr(element, '_del_tf_index'):
            screen._delete_task_force(element._del_tf_index)
            return

        # Squadron duplication
        if hasattr(element, '_dup_sq_tf_index'):
            screen._duplicate_squadron(element._dup_sq_tf_index, element._dup_sq_index)
            return

        # Squadron deletion
        if hasattr(element, '_del_sq_tf_index'):
            screen._delete_squadron(element._del_sq_tf_index, element._del_sq_index)
            return

        # Named action buttons
        if element == screen._start_btn:
            screen._start_battle(headless=False)
        elif element == screen._headless_btn:
            screen._start_battle(headless=True)
        elif element == screen._save_btn:
            screen._save_setup()
        elif element == screen._load_btn:
            screen._load_setup()
        elif element == screen._return_btn:
            if screen.scene_callback:
                screen.scene_callback("return_to_menu")
        elif element == screen._add_fleet_btn:
            side = screen.state.get_side(view_model.active_side)
            side.create_fleet(f"Fleet {len(side.fleets) + 1}")
            screen._rebuild_ui()
        elif element == screen._remove_fleet_btn:
            side = screen.state.get_side(view_model.active_side)
            if len(side.fleets) > 1 and view_model.active_fleet_index < len(side.fleets):
                side.fleets.pop(view_model.active_fleet_index)
                view_model.active_fleet_index = min(
                    view_model.active_fleet_index, len(side.fleets) - 1
                )
                screen._rebuild_ui()
        elif hasattr(screen, '_add_tf_btn') and element == screen._add_tf_btn:
            screen._add_task_force()
        elif hasattr(screen, '_add_sq_btn') and element == screen._add_sq_btn:
            screen._add_squadron()
        elif hasattr(screen, '_end_destroyed_btn') and element == screen._end_destroyed_btn:
            screen.end_all_destroyed = not screen.end_all_destroyed
            screen._rebuild_ui()
        elif hasattr(screen, '_end_derelict_btn') and element == screen._end_derelict_btn:
            screen.end_all_derelict = not screen.end_all_derelict
            screen._rebuild_ui()
        elif hasattr(screen, '_end_mass_btn') and element == screen._end_mass_btn:
            screen.end_mass_ratio = not screen.end_mass_ratio
            screen._rebuild_ui()

    # === Dropdown dispatch ===

    def _handle_dropdown(self, event) -> None:
        screen = self._screen
        view_model = screen.view_model

        if event.ui_element == screen._side_dropdown:
            view_model.active_side = 1 if "1" in event.text else 0
            view_model.active_fleet_index = 0
            screen._rebuild_ui()
        elif hasattr(screen, '_fleet_role_dropdown') and event.ui_element == screen._fleet_role_dropdown:
            screen._set_fleet_battle_role(event.text)
        elif screen._targeting_dropdown and event.ui_element == screen._targeting_dropdown:
            screen._set_selected_policy("targeting", event.text)
        elif screen._movement_dropdown and event.ui_element == screen._movement_dropdown:
            screen._set_selected_policy("movement", event.text)
        elif (
            screen._ship_targeting_dropdown
            and event.ui_element == screen._ship_targeting_dropdown
        ):
            from game.ui.screens.battle_setup_screen import _TARGETING_OPTIONS
            screen._set_ship_policy("_targeting_policy", event.text, _TARGETING_OPTIONS)
        elif (
            screen._ship_movement_dropdown
            and event.ui_element == screen._ship_movement_dropdown
        ):
            from game.ui.screens.battle_setup_screen import _MOVEMENT_OPTIONS
            screen._set_ship_policy("_movement_policy", event.text, _MOVEMENT_OPTIONS)
