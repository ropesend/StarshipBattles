"""PROJ-282 Phase 5: `BattleSetupInputHandler` tests.

The handler dispatches pygame_gui events (`UI_BUTTON_PRESSED`,
`UI_DROP_DOWN_MENU_CHANGED`) to screen mutation methods and view_model
selection setters. Covers:
  - Tag-based button dispatch (fleet / ship / design / TF / SQ / complex)
  - Named-button dispatch (start / save / load / return / add-fleet / end-condition toggles)
  - Dropdown dispatch (side / fleet-role / targeting / movement / per-ship)
  - Unknown events return False without crashing
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pygame_gui


def _button_event(ui_element) -> SimpleNamespace:
    return SimpleNamespace(type=pygame_gui.UI_BUTTON_PRESSED, ui_element=ui_element)


def _dropdown_event(ui_element, text: str) -> SimpleNamespace:
    return SimpleNamespace(
        type=pygame_gui.UI_DROP_DOWN_MENU_CHANGED,
        ui_element=ui_element,
        text=text,
    )


def _make_handler_with_mock_screen():
    """Construct an InputHandler with a MagicMock screen + real ViewModel.

    Screen's `controller` attribute is a MagicMock — PROJ-282 Phase 6
    retargeted mutation dispatch from `screen._*` to `screen.controller.*`.
    """
    from game.ui.screens.battle_setup.input_handler import BattleSetupInputHandler
    from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

    screen = MagicMock()
    screen.view_model = BattleSetupViewModel()
    screen.controller = MagicMock()
    # Named-button identity markers — each one a distinct sentinel so the
    # handler's `event.ui_element == screen._start_btn` identity checks
    # route correctly.
    screen._start_btn = object()
    screen._headless_btn = object()
    screen._save_btn = object()
    screen._load_btn = object()
    screen._return_btn = object()
    screen._add_fleet_btn = object()
    screen._remove_fleet_btn = object()
    screen._add_tf_btn = object()
    screen._add_sq_btn = object()
    screen._end_destroyed_btn = object()
    screen._end_derelict_btn = object()
    screen._end_mass_btn = object()
    screen._add_side_btn = object()
    screen._remove_side_btn = object()
    screen._side_dropdown = object()
    screen._fleet_role_dropdown = object()
    screen._targeting_dropdown = object()
    screen._movement_dropdown = object()
    screen._ship_targeting_dropdown = object()
    screen._ship_movement_dropdown = object()
    # Tick-limit entry isn't built by the renderer in these tests; the
    # start-battle branches guard on `hasattr/get_text`, so leave absent.
    screen._tick_limit_entry = None

    handler = BattleSetupInputHandler(screen)
    return handler, screen


class TestTagBasedButtonDispatch:
    def test_fleet_button_updates_view_model_selection(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(_fleet_index=3)

        handler.handle_event(_button_event(btn))

        assert screen.view_model.active_fleet_index == 3
        assert screen.view_model.selected_tf_index is None
        assert screen.view_model.selected_sq_index is None
        screen._rebuild_ui.assert_called_once()

    def test_ship_button_updates_view_model_selection(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(_ship_index=2)

        handler.handle_event(_button_event(btn))

        assert screen.view_model.selected_ship_index == 2
        screen._rebuild_ui.assert_called_once()

    def test_design_button_calls_add_ship_from_design(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(_design_index=7)

        handler.handle_event(_button_event(btn))

        screen.controller.add_ship_from_design.assert_called_once_with(7)

    def test_remove_ship_button_calls_remove_ship(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(_ship_index=4, _remove_ship_index=4)

        handler.handle_event(_button_event(btn))

        screen.controller.remove_ship.assert_called_once_with(4)

    def test_complex_toggle_button_calls_controller_toggle_complex(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(
            _complex_key=(1, "system", "qs_system_shield_booster_complex"),
            _complex_design_id="qs_system_shield_booster_complex",
        )

        handler.handle_event(_button_event(btn))

        screen.controller.toggle_complex.assert_called_once_with(
            1, "system", "qs_system_shield_booster_complex"
        )

    def test_tf_button_updates_selection(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(_tf_index=2)

        handler.handle_event(_button_event(btn))

        assert screen.view_model.selected_tf_index == 2
        assert screen.view_model.selected_sq_index is None
        screen._rebuild_ui.assert_called_once()

    def test_sq_button_updates_selection(self):
        handler, screen = _make_handler_with_mock_screen()
        # Squadron button has _sq_tf_index + _sq_index, NO _dup_* / _del_* markers.
        btn = SimpleNamespace(_sq_tf_index=1, _sq_index=0)

        handler.handle_event(_button_event(btn))

        assert screen.view_model.selected_tf_index == 1
        assert screen.view_model.selected_sq_index == 0
        screen._rebuild_ui.assert_called_once()

    def test_tf_dup_button_calls_duplicate_task_force(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(_dup_tf_index=0)

        handler.handle_event(_button_event(btn))

        screen.controller.duplicate_task_force.assert_called_once_with(0)

    def test_tf_del_button_calls_delete_task_force(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(_del_tf_index=1)

        handler.handle_event(_button_event(btn))

        screen.controller.delete_task_force.assert_called_once_with(1)

    def test_sq_dup_button_calls_duplicate_squadron(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(_dup_sq_tf_index=1, _dup_sq_index=2)

        handler.handle_event(_button_event(btn))

        screen.controller.duplicate_squadron.assert_called_once_with(1, 2)

    def test_sq_del_button_calls_delete_squadron(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(_del_sq_tf_index=0, _del_sq_index=1)

        handler.handle_event(_button_event(btn))

        screen.controller.delete_squadron.assert_called_once_with(0, 1)


class TestNamedButtonDispatch:
    def test_start_button_launches_visual_battle(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._start_btn))
        screen.controller.start_battle.assert_called_once_with(headless=False)

    def test_headless_button_launches_headless_battle(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._headless_btn))
        screen.controller.start_battle.assert_called_once_with(headless=True)

    def test_save_button_triggers_controller_save(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._save_btn))
        screen.controller.save_setup.assert_called_once()

    def test_load_button_triggers_controller_load(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._load_btn))
        screen.controller.load_setup.assert_called_once()

    def test_return_button_calls_controller_return_to_menu(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._return_btn))
        screen.controller.return_to_menu.assert_called_once_with()

    def test_add_fleet_button_calls_controller_add_fleet(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._add_fleet_btn))
        screen.controller.add_fleet.assert_called_once_with()

    def test_remove_fleet_button_calls_controller_remove_fleet(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._remove_fleet_btn))
        screen.controller.remove_fleet.assert_called_once_with()

    def test_add_tf_button_calls_controller_add_task_force(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._add_tf_btn))
        screen.controller.add_task_force.assert_called_once_with()

    def test_add_sq_button_calls_controller_add_squadron(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._add_sq_btn))
        screen.controller.add_squadron.assert_called_once_with()

    def test_end_destroyed_button_calls_controller_toggle(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._end_destroyed_btn))
        screen.controller.toggle_end_destroyed.assert_called_once_with()

    def test_end_derelict_button_calls_controller_toggle(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._end_derelict_btn))
        screen.controller.toggle_end_derelict.assert_called_once_with()

    def test_end_mass_button_calls_controller_toggle(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._end_mass_btn))
        screen.controller.toggle_end_mass_ratio.assert_called_once_with()

    def test_add_side_button_calls_controller_add_side(self):
        """PROJ-282 Phase 11."""
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._add_side_btn))
        screen.controller.add_side.assert_called_once_with()

    def test_remove_side_button_calls_controller_remove_active(self):
        """PROJ-282 Phase 11: remove-side removes the currently-active side."""
        handler, screen = _make_handler_with_mock_screen()
        screen.view_model.active_side = 2

        handler.handle_event(_button_event(screen._remove_side_btn))

        screen.controller.remove_side.assert_called_once_with(2)


class TestDropdownDispatch:
    def test_side_dropdown_calls_controller_set_active_side_to_1(self):
        handler, screen = _make_handler_with_mock_screen()
        # PROJ-282 Phase 11: dropdown text is "Side N" (dropped Left/Right suffix).
        handler.handle_event(_dropdown_event(screen._side_dropdown, "Side 1"))
        screen.controller.set_active_side.assert_called_once_with(1)

    def test_side_dropdown_back_to_0(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_dropdown_event(screen._side_dropdown, "Side 0"))
        screen.controller.set_active_side.assert_called_once_with(0)

    def test_side_dropdown_handles_n_gt_2(self):
        """PROJ-282 Phase 11: parse side indices beyond 1 (N-team support)."""
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_dropdown_event(screen._side_dropdown, "Side 5"))
        screen.controller.set_active_side.assert_called_once_with(5)

    def test_side_dropdown_fallback_on_malformed_text(self):
        """Parser falls back to 0 rather than raising on unexpected format."""
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_dropdown_event(screen._side_dropdown, "garbage"))
        screen.controller.set_active_side.assert_called_once_with(0)

    def test_fleet_role_dropdown_calls_controller(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_dropdown_event(screen._fleet_role_dropdown, "Vanguard"))
        screen.controller.set_fleet_battle_role.assert_called_once_with("Vanguard")

    def test_targeting_dropdown_calls_controller(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_dropdown_event(screen._targeting_dropdown, "Focus Nearest"))
        screen.controller.set_selected_policy.assert_called_once_with("targeting", "Focus Nearest")

    def test_movement_dropdown_calls_controller(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_dropdown_event(screen._movement_dropdown, "Pursue"))
        screen.controller.set_selected_policy.assert_called_once_with("movement", "Pursue")


class TestUnknownEvents:
    def test_unknown_button_type_does_not_crash(self):
        handler, screen = _make_handler_with_mock_screen()
        # Some random event type the handler doesn't care about.
        other = SimpleNamespace(type=999, ui_element=object())
        # Should be a no-op.
        handler.handle_event(other)

    def test_button_with_no_recognized_tags_is_noop(self):
        handler, screen = _make_handler_with_mock_screen()
        # Unknown button — no tags, not a named button.
        btn = SimpleNamespace()
        handler.handle_event(_button_event(btn))
        # None of the controller mutations should have been called.
        screen.controller.add_ship_from_design.assert_not_called()
        screen.controller.duplicate_task_force.assert_not_called()
        screen.controller.start_battle.assert_not_called()
