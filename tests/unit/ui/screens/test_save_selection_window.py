"""Characterization tests for ``SaveSelectionWindow`` Pattern §33
widget-ref placeholders (PROJ-347 T4.3a).

``SaveSelectionWindow.process_event`` accesses ``self.btn_load``,
``self.btn_expand``, ``self.btn_delete``, ``self.btn_cancel``, and
``self.saves_listbox``. Stage 1 must set these to ``None`` before the
bypass guard so a Null-builder test does not AttributeError on those
slots.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pygame
import pygame_gui

from game.ui.screens.save_selection_window import SaveSelectionWindow
from tests.fixtures.save_selection_window_ui_builder import (
    MockSaveSelectionWindowUiBuilder,
    NullSaveSelectionWindowUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init


def _make_window(*, ui_builder):
    rect = pygame.Rect(0, 0, 600, 400)
    with bypass_init(SaveSelectionWindow):
        return SaveSelectionWindow(
            rect,
            MagicMock(name="ui_manager"),
            MagicMock(name="on_load_callback"),
            MagicMock(name="on_cancel_callback"),
            ui_builder=ui_builder,
        )


def _make_mock_window():
    return _make_window(ui_builder=MockSaveSelectionWindowUiBuilder())


def _make_real_mock_window():
    with patch(
        "game.strategy.systems.save_game_service.SaveGameService.list_saves",
        return_value=[],
    ):
        return SaveSelectionWindow(
            pygame.Rect(0, 0, 600, 400),
            pygame_gui.UIManager((800, 600)),
            MagicMock(name="on_load_callback"),
            MagicMock(name="on_cancel_callback"),
            ui_builder=MockSaveSelectionWindowUiBuilder(),
        )


class TestSaveSelectionWindowWidgetPlaceholders:
    """PROJ-347 T4.3a — Pattern §33 widget-ref placeholders.

    The 6 widget refs ``process_event`` reads (saves_listbox,
    info_label, btn_load, btn_expand, btn_delete, btn_cancel) must be
    ``None`` after a Null-builder bypass-init construction.
    """

    def test_null_builder_leaves_widget_placeholders_as_none(self):
        window = _make_window(ui_builder=NullSaveSelectionWindowUiBuilder())
        for slot in (
            "saves_listbox", "info_label",
            "btn_load", "btn_expand", "btn_delete", "btn_cancel",
        ):
            assert getattr(window, slot) is None, (
                f"Pattern §33 placeholder {slot!r} should be None under "
                f"Null builder; got {getattr(window, slot)!r}"
            )

    def test_stage_1_state_survives_bypass(self):
        """Stage 1 cheap state survives the bypass guard."""
        window = _make_window(ui_builder=NullSaveSelectionWindowUiBuilder())
        assert window.saves_list == []
        assert window.selected_save is None
        assert window.selected_turn is None
        assert window.expanded_save_idx is None
        assert window.list_item_mapping == []


class TestSaveSelectionWindowLoadPaths:
    def test_load_saves_empty_list_updates_listbox(self):
        window = _make_mock_window()

        with patch(
            "game.strategy.systems.save_game_service.SaveGameService.list_saves",
            return_value=[],
        ):
            window._load_saves()

        window.saves_listbox.set_item_list.assert_called_once_with(
            ["No save games found"]
        )
        assert window.list_item_mapping == []

    def test_load_saves_stores_results_and_refreshes_display(self, tmp_path):
        window = _make_mock_window()
        save_path = tmp_path / "alpha"
        saves = [{
            "save_name": "Alpha",
            "player_name": "Player",
            "save_path": str(save_path),
            "latest_turn_number": 4,
            "timestamp": "2026-05-05T12:30:00",
        }]

        with patch(
            "game.strategy.systems.save_game_service.SaveGameService.list_saves",
            return_value=saves,
        ), patch.object(window, "_refresh_list_display") as refresh:
            window._load_saves()

        assert window.saves_list == saves
        refresh.assert_called_once()

    def test_refresh_display_expanded_save_lists_turns(self, tmp_path):
        window = _make_mock_window()
        save_path = tmp_path / "alpha"
        window.saves_list = [{
            "save_name": "Alpha",
            "player_name": "Player",
            "save_path": str(save_path),
            "latest_turn_number": 4,
            "timestamp": "2026-05-05T12:30:00",
        }]
        window.expanded_save_idx = 0

        with patch(
            "game.strategy.systems.save_game_service.SaveGameService.list_turns",
            return_value=[{
                "turn_number": 3,
                "timestamp": "2026-05-05T12:00:00",
            }],
        ) as list_turns:
            window._refresh_list_display()

        list_turns.assert_called_once_with(str(save_path))
        items = window.saves_listbox.set_item_list.call_args.args[0]
        assert items == [
            "Alpha - Turn 4 (2026-05-05 12:30)",
            "    Turn 3 (05-05 12:00)",
        ]
        assert window.list_item_mapping == [
            ("save", 0),
            ("turn", 0, 3),
        ]

    def test_on_load_clicked_loads_latest_turn_and_kills_window(self, tmp_path):
        window = _make_mock_window()
        window.kill = MagicMock()
        save_path = tmp_path / "alpha"
        window.selected_save = {"save_path": str(save_path)}
        window.selected_turn = None

        window._on_load_clicked()

        window.on_load_callback.assert_called_once_with(str(save_path), None)
        window.kill.assert_called_once()

    def test_on_load_clicked_loads_specific_turn(self, tmp_path):
        window = _make_mock_window()
        window.kill = MagicMock()
        save_path = tmp_path / "alpha"
        window.selected_save = {"save_path": str(save_path)}
        window.selected_turn = 7

        window._on_load_clicked()

        window.on_load_callback.assert_called_once_with(str(save_path), 7)


class TestSaveSelectionWindowDeletePaths:
    def test_delete_confirmation_success_deletes_save_and_resets_selection(
        self,
        tmp_path,
    ):
        window = _make_mock_window()
        save_path = tmp_path / "alpha"
        window.selected_save = {
            "save_name": "Alpha",
            "save_path": str(save_path),
        }
        window.selected_turn = 5
        window.expanded_save_idx = 0
        window._load_saves = MagicMock()

        with patch(
            "game.strategy.systems.save_game_service.SaveGameService.delete_save",
            return_value=(True, "deleted"),
        ) as delete_save:
            window._handle_delete_confirmation()

        delete_save.assert_called_once_with(str(save_path))
        window._load_saves.assert_called_once()
        assert window.selected_save is None
        assert window.selected_turn is None
        assert window.expanded_save_idx is None
        assert window.btn_load.is_enabled is False
        assert window.btn_expand.is_enabled is False
        assert window.btn_delete.is_enabled is False
        window.info_label.set_text.assert_called_once_with("Select a save to load")

    def test_delete_confirmation_without_selection_is_noop(self):
        window = _make_mock_window()

        with patch(
            "game.strategy.systems.save_game_service.SaveGameService.delete_save"
        ) as delete_save:
            window._handle_delete_confirmation()

        delete_save.assert_not_called()

    def test_delete_confirmation_failure_preserves_selection_and_shows_error(
        self,
        tmp_path,
    ):
        window = _make_real_mock_window()
        save_path = tmp_path / "alpha"
        window.selected_save = {
            "save_name": "Alpha",
            "save_path": str(save_path),
        }

        try:
            with patch(
                "game.strategy.systems.save_game_service.SaveGameService.delete_save",
                return_value=(False, "locked"),
            ), patch(
                "pygame_gui.windows.UIMessageWindow"
            ) as message_window:
                window._handle_delete_confirmation()

            assert window.selected_save["save_path"] == str(save_path)
            message_window.assert_called_once()
            assert "locked" in message_window.call_args.kwargs["html_message"]
        finally:
            window.kill()

    def test_update_consumes_delete_confirmation_event(self):
        window = _make_mock_window()
        window._handle_delete_confirmation = MagicMock()
        event = SimpleNamespace(
            ui_element=SimpleNamespace(action_short_name="delete_save")
        )

        with patch(
            "pygame_gui.elements.UIWindow.update",
            return_value=None,
        ), patch(
            "pygame.event.get",
            return_value=[event],
        ) as event_get:
            window.update(0.016)

        event_get.assert_called_once_with(
            pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED
        )
        window._handle_delete_confirmation.assert_called_once()
