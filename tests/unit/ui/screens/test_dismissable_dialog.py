"""Characterization tests for the shared dismiss behaviour of
:class:`DefeatDialog` and :class:`TurnFailedDialog` (Cluster 7, PROJ-465).

Both dialogs previously owned a character-for-character identical
``process_event`` that killed the window on a "Dismiss" button press.
These tests pin that behaviour so the extraction to a shared
``DismissableModalDialog`` mixin is proven behaviour-preserving. The
``process_event`` logic is exercised directly on a bare instance
(``object.__new__``) so no real ``pygame_gui`` UIWindow construction is
required.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame_gui
import pytest

from game.ui.screens.defeat_dialog import DefeatDialog
from game.ui.screens.strategy_modal_window import StrategyModalWindow
from game.ui.screens.turn_failed_dialog import TurnFailedDialog


def _event(*, event_type, ui_element):
    e = MagicMock()
    e.type = event_type
    e.ui_element = ui_element
    return e


def _make(cls, dismiss_button):
    inst = object.__new__(cls)
    inst._dismiss_button = dismiss_button
    inst.killed = False
    inst.kill = lambda: setattr(inst, "killed", True)  # type: ignore[method-assign]
    return inst


@pytest.mark.parametrize("cls", [DefeatDialog, TurnFailedDialog])
def test_dismiss_button_press_kills_and_consumes(cls):
    button = object()
    inst = _make(cls, button)

    evt = _event(event_type=pygame_gui.UI_BUTTON_PRESSED, ui_element=button)
    consumed = inst.process_event(evt)

    assert consumed is True
    assert inst.killed is True


@pytest.mark.parametrize("cls", [DefeatDialog, TurnFailedDialog])
def test_non_dismiss_event_delegates_to_modal_base(cls, monkeypatch):
    button = object()
    inst = _make(cls, button)

    sentinel = object()
    monkeypatch.setattr(
        StrategyModalWindow, "process_event",
        lambda self, e: sentinel, raising=False,
    )

    other_evt = _event(event_type=pygame_gui.UI_BUTTON_PRESSED, ui_element=object())
    result = inst.process_event(other_evt)

    assert inst.killed is False
    assert result is sentinel


@pytest.mark.parametrize("cls", [DefeatDialog, TurnFailedDialog])
def test_no_dismiss_button_delegates(cls, monkeypatch):
    inst = _make(cls, None)
    sentinel = object()
    monkeypatch.setattr(
        StrategyModalWindow, "process_event",
        lambda self, e: sentinel, raising=False,
    )

    evt = _event(event_type=pygame_gui.UI_BUTTON_PRESSED, ui_element=object())
    result = inst.process_event(evt)

    assert inst.killed is False
    assert result is sentinel
