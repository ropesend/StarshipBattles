"""Focused unit tests for Test Lab dialog state transitions."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pygame
import pygame_gui

from game.ui.screens.test_lab import dialogs


class FakeButton:
    """Small UIButton replacement that records close/kill lifecycle."""

    instances: list["FakeButton"] = []

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.killed = False
        FakeButton.instances.append(self)

    def kill(self) -> None:
        self.killed = True


def _patch_dialog_buttons(monkeypatch) -> None:
    FakeButton.instances = []
    monkeypatch.setattr(dialogs, "UIButton", FakeButton)
    monkeypatch.setattr(dialogs, "get_font", lambda *args, **kwargs: Mock())


def test_json_popup_close_marks_closed_and_kills_button(monkeypatch) -> None:
    _patch_dialog_buttons(monkeypatch)
    popup = dialogs.JSONPopup("Data", {"id": "alpha"}, 1000, 800, Mock())

    popup.close()

    assert popup.is_open is False
    assert popup.close_button.killed is True


def test_json_popup_close_button_event_closes_dialog(monkeypatch) -> None:
    _patch_dialog_buttons(monkeypatch)
    popup = dialogs.JSONPopup("Data", {"id": "alpha"}, 1000, 800, Mock())
    event = SimpleNamespace(type=pygame_gui.UI_BUTTON_PRESSED, ui_element=popup.close_button)

    handled = popup.handle_event(event)

    assert handled is True
    assert popup.is_open is False
    assert popup.close_button.killed is True


def test_confirmation_dialog_confirm_event_closes_and_invokes_callback(monkeypatch) -> None:
    _patch_dialog_buttons(monkeypatch)
    on_confirm = Mock()
    on_cancel = Mock()
    dialog = dialogs.ConfirmationDialog(
        "Confirm",
        [{"field": "name", "old_value": "A", "new_value": "B"}],
        1000,
        800,
        on_confirm,
        on_cancel,
        Mock(),
    )
    event = SimpleNamespace(type=pygame_gui.UI_BUTTON_PRESSED, ui_element=dialog.confirm_button)

    handled = dialog.handle_event(event)

    assert handled is True
    assert dialog.result == "confirm"
    assert dialog.is_open is False
    assert dialog.confirm_button.killed is True
    assert dialog.cancel_button.killed is True
    on_confirm.assert_called_once_with()
    on_cancel.assert_not_called()


def test_confirmation_dialog_cancel_event_closes_and_invokes_callback(monkeypatch) -> None:
    _patch_dialog_buttons(monkeypatch)
    on_confirm = Mock()
    on_cancel = Mock()
    dialog = dialogs.ConfirmationDialog("Confirm", [], 1000, 800, on_confirm, on_cancel, Mock())
    event = SimpleNamespace(type=pygame_gui.UI_BUTTON_PRESSED, ui_element=dialog.cancel_button)

    handled = dialog.handle_event(event)

    assert handled is True
    assert dialog.result == "cancel"
    assert dialog.is_open is False
    assert dialog.confirm_button.killed is True
    assert dialog.cancel_button.killed is True
    on_confirm.assert_not_called()
    on_cancel.assert_called_once_with()


def test_confirmation_dialog_escape_uses_cancel_path(monkeypatch) -> None:
    _patch_dialog_buttons(monkeypatch)
    on_cancel = Mock()
    dialog = dialogs.ConfirmationDialog("Confirm", [], 1000, 800, None, on_cancel, Mock())
    event = SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)

    dialog.handle_event(event)

    assert dialog.result == "cancel"
    assert dialog.is_open is False
    assert dialog.confirm_button.killed is True
    assert dialog.cancel_button.killed is True
    on_cancel.assert_called_once_with()
