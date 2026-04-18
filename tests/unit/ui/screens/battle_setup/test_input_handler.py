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
    """Construct an InputHandler with a MagicMock screen + real ViewModel."""
    from game.ui.screens.battle_setup.input_handler import BattleSetupInputHandler
    from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

    screen = MagicMock()
    screen.view_model = BattleSetupViewModel()
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
    screen._side_dropdown = object()
    screen._fleet_role_dropdown = object()
    screen._targeting_dropdown = object()
    screen._movement_dropdown = object()
    screen._ship_targeting_dropdown = object()
    screen._ship_movement_dropdown = object()

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

        screen._add_ship_from_design.assert_called_once_with(7)

    def test_remove_ship_button_calls_remove_ship(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(_ship_index=4, _remove_ship_index=4)

        handler.handle_event(_button_event(btn))

        screen._remove_ship.assert_called_once_with(4)

    def test_complex_toggle_button_toggles_via_set_toggle(self):
        handler, screen = _make_handler_with_mock_screen()
        screen._get_toggle = MagicMock(return_value=False)
        btn = SimpleNamespace(
            _complex_key=(1, "system", "qs_system_shield_booster_complex"),
            _complex_design_id="qs_system_shield_booster_complex",
        )

        handler.handle_event(_button_event(btn))

        screen._get_toggle.assert_called_once_with(1, "system", "qs_system_shield_booster_complex")
        screen._set_toggle.assert_called_once_with(
            1, "system", "qs_system_shield_booster_complex", True
        )
        screen._rebuild_ui.assert_called_once()

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

        screen._duplicate_task_force.assert_called_once_with(0)

    def test_tf_del_button_calls_delete_task_force(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(_del_tf_index=1)

        handler.handle_event(_button_event(btn))

        screen._delete_task_force.assert_called_once_with(1)

    def test_sq_dup_button_calls_duplicate_squadron(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(_dup_sq_tf_index=1, _dup_sq_index=2)

        handler.handle_event(_button_event(btn))

        screen._duplicate_squadron.assert_called_once_with(1, 2)

    def test_sq_del_button_calls_delete_squadron(self):
        handler, screen = _make_handler_with_mock_screen()
        btn = SimpleNamespace(_del_sq_tf_index=0, _del_sq_index=1)

        handler.handle_event(_button_event(btn))

        screen._delete_squadron.assert_called_once_with(0, 1)


class TestNamedButtonDispatch:
    def test_start_button_launches_visual_battle(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._start_btn))
        screen._start_battle.assert_called_once_with(headless=False)

    def test_headless_button_launches_headless_battle(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._headless_btn))
        screen._start_battle.assert_called_once_with(headless=True)

    def test_save_button_triggers_save(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._save_btn))
        screen._save_setup.assert_called_once()

    def test_load_button_triggers_load(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_button_event(screen._load_btn))
        screen._load_setup.assert_called_once()

    def test_return_button_fires_scene_callback(self):
        handler, screen = _make_handler_with_mock_screen()
        screen.scene_callback = MagicMock()
        handler.handle_event(_button_event(screen._return_btn))
        screen.scene_callback.assert_called_once_with("return_to_menu")

    def test_return_button_without_callback_does_not_crash(self):
        handler, screen = _make_handler_with_mock_screen()
        screen.scene_callback = None
        # Should not raise.
        handler.handle_event(_button_event(screen._return_btn))

    def test_add_fleet_button_creates_fleet_and_rebuilds(self):
        handler, screen = _make_handler_with_mock_screen()
        fake_side = MagicMock()
        fake_side.fleets = [MagicMock(), MagicMock()]  # len=2
        screen.state.get_side.return_value = fake_side

        handler.handle_event(_button_event(screen._add_fleet_btn))

        fake_side.create_fleet.assert_called_once_with("Fleet 3")
        screen._rebuild_ui.assert_called_once()

    def test_end_destroyed_button_toggles_flag(self):
        handler, screen = _make_handler_with_mock_screen()
        screen.end_all_destroyed = True
        handler.handle_event(_button_event(screen._end_destroyed_btn))
        assert screen.end_all_destroyed is False
        screen._rebuild_ui.assert_called_once()


class TestDropdownDispatch:
    def test_side_dropdown_switches_active_side(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_dropdown_event(screen._side_dropdown, "Side 1 (Right)"))
        assert screen.view_model.active_side == 1
        assert screen.view_model.active_fleet_index == 0
        screen._rebuild_ui.assert_called_once()

    def test_side_dropdown_back_to_0(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_dropdown_event(screen._side_dropdown, "Side 0 (Left)"))
        assert screen.view_model.active_side == 0

    def test_fleet_role_dropdown_calls_set_fleet_battle_role(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_dropdown_event(screen._fleet_role_dropdown, "Vanguard"))
        screen._set_fleet_battle_role.assert_called_once_with("Vanguard")

    def test_targeting_dropdown_calls_set_selected_policy(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_dropdown_event(screen._targeting_dropdown, "Focus Nearest"))
        screen._set_selected_policy.assert_called_once_with("targeting", "Focus Nearest")

    def test_movement_dropdown_calls_set_selected_policy(self):
        handler, screen = _make_handler_with_mock_screen()
        handler.handle_event(_dropdown_event(screen._movement_dropdown, "Pursue"))
        screen._set_selected_policy.assert_called_once_with("movement", "Pursue")


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
        # None of the mutation methods should have been called.
        screen._add_ship_from_design.assert_not_called()
        screen._duplicate_task_force.assert_not_called()
        screen._start_battle.assert_not_called()
