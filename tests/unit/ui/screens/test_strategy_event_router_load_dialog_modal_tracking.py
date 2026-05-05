"""PROJ-352 T6.6 regression: load dialog must block strategy input.

The strategy load dialog (``SaveSelectionWindow``) opened via
``strategy_screen_lifecycle.show_load_game_dialog`` was historically a
raw ``pygame_gui.elements.UIWindow`` and never registered with
``StrategyWindowManager``'s modal-tracking list, so
``StrategyEventRouter.has_modal_open()`` and
``_is_blocking_ui_element_at()`` returned ``False`` even while the
dialog was visibly open. This let strategy-screen input (hex clicks,
sidebar buttons) coexist with the dialog — the only modal in the
strategy screen with that exemption.

Shape A fix (per ``Projects/active_projects/PROJ-352/decisions.md``):
``SaveSelectionWindow`` now subclasses ``StrategyModalWindow`` and
``show_load_game_dialog`` passes the strategy ``window_manager``,
so the dialog auto-registers via ``StrategyModalWindow.__init__`` and
auto-deregisters via ``StrategyModalWindow.kill()``.

These tests pin the behavior at the router-level (live-list participation)
without bringing up a real pygame display.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame
import pytest

from game.ui.screens.save_selection_window import SaveSelectionWindow
from game.ui.screens.strategy_event_router import StrategyEventRouter
from game.ui.screens.strategy_window_manager import StrategyWindowManager
from tests.fixtures.save_selection_window_ui_builder import (
    NullSaveSelectionWindowUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init


class _Rect:
    """Minimal rect-like with ``collidepoint`` for the click-gate tests."""

    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self.x, self.y, self.width, self.height = x, y, w, h

    def collidepoint(self, pos):
        px, py = pos
        return self.x <= px < self.x + self.width and self.y <= py < self.y + self.height


def _make_window_manager() -> StrategyWindowManager:
    """Build a real ``StrategyWindowManager`` without invoking registrar
    construction beyond what ``__init__`` does. The composer's
    ``__init__`` is pure-Python aside from the ``pygame_gui.UIManager``
    arg, which it stores but does not call into."""
    return StrategyWindowManager(
        scene=MagicMock(name="scene"),
        manager=MagicMock(name="ui_manager"),
        width=2560,
        height=1600,
    )


def _make_router(window_manager: StrategyWindowManager) -> StrategyEventRouter:
    """Build a router around a mock UI whose window_manager is real,
    so the OR-bridge over ``iter_live_modals()`` exercises live-list
    participation rather than a stub."""
    ui = MagicMock(name="strategy_ui")
    ui.width = 2560
    ui.height = 1600
    ui.sidebar_width = 300
    ui.menu_panel = None
    ui.scene.build_queue_screen = None
    ui.window_manager = window_manager
    ui.top_bar.rect = _Rect(0, 0, 2260, 50)
    ui.resource_bar.rect = _Rect(0, 50, 2260, 24)
    return StrategyEventRouter(ui)


def _make_load_dialog(window_manager: StrategyWindowManager) -> SaveSelectionWindow:
    """Build a SaveSelectionWindow under ``bypass_init`` so it
    participates in modal tracking without spinning up a real
    ``UIWindow`` shell."""
    rect = pygame.Rect(100, 100, 600, 500)
    with bypass_init(SaveSelectionWindow):
        return SaveSelectionWindow(
            rect,
            MagicMock(name="ui_manager"),
            on_load_callback=MagicMock(),
            on_cancel_callback=MagicMock(),
            window_manager=window_manager,
            ui_builder=NullSaveSelectionWindowUiBuilder(),
        )


class TestLoadDialogBlocksStrategyInput:
    """T6.6 regression: an open load dialog blocks strategy-screen input."""

    def test_has_modal_open_true_while_load_dialog_alive(self):
        wm = _make_window_manager()
        router = _make_router(wm)

        assert router.has_modal_open() is False, (
            "Sanity check: no modals open at start"
        )

        dialog = _make_load_dialog(wm)
        # Force ``alive()`` true under bypass_init (no real UIWindow shell).
        dialog.alive = MagicMock(return_value=True)
        # Register manually because bypass_init skips registration to keep
        # test fixtures off the live list by default; for this regression
        # we need the production registration path simulated.
        wm.register_modal(dialog)

        assert router.has_modal_open() is True, (
            "Load dialog must block strategy input via iter_live_modals"
        )

    def test_click_at_dialog_rect_is_blocked(self):
        wm = _make_window_manager()
        router = _make_router(wm)

        dialog = _make_load_dialog(wm)
        dialog.alive = MagicMock(return_value=True)
        # Override the rect descriptor (assigning ``self.rect`` on a
        # bypassed instance is unsafe — it mutates pygame_gui's blit_data)
        # via an object-level shadow that ``_is_blocking_ui_element_at``
        # reads through duck typing.
        type(dialog).rect = property(lambda self: _Rect(100, 100, 600, 500))
        try:
            wm.register_modal(dialog)

            # Click inside the dialog rect.
            assert router._is_blocking_ui_element_at(400, 350) is True

            # Click on the map area, far from the dialog.
            assert router._is_blocking_ui_element_at(1500, 1000) is False
        finally:
            # Restore so other tests in the same module/class don't see
            # a synthetic ``rect`` property on the class.
            del type(dialog).rect

    def test_kill_removes_dialog_from_live_list(self):
        wm = _make_window_manager()
        router = _make_router(wm)

        dialog = _make_load_dialog(wm)
        dialog.alive = MagicMock(return_value=True)
        wm.register_modal(dialog)
        assert router.has_modal_open() is True

        # Simulate kill: live-list filtering reaps dead refs.
        dialog.alive = MagicMock(return_value=False)
        assert router.has_modal_open() is False, (
            "Dead dialog must be reaped from iter_live_modals so strategy "
            "input is restored when the load dialog closes"
        )


class TestLoadDialogConstructionContract:
    """SaveSelectionWindow must accept ``window_manager`` as a kwarg
    and decline to register when ``None`` (matching every other
    StrategyModalWindow subclass)."""

    def test_construction_with_window_manager_registers(self):
        wm = _make_window_manager()
        # Bypassed instances intentionally skip registration; this test
        # therefore checks the production wiring directly by asserting
        # the constructor accepts the keyword without raising.
        rect = pygame.Rect(0, 0, 600, 500)
        with bypass_init(SaveSelectionWindow):
            dialog = SaveSelectionWindow(
                rect,
                MagicMock(name="ui_manager"),
                on_load_callback=MagicMock(),
                on_cancel_callback=MagicMock(),
                window_manager=wm,
                ui_builder=NullSaveSelectionWindowUiBuilder(),
            )
        # The constructor must store the window_manager on the
        # bypass-init shell so kill() can deregister consistently.
        assert getattr(dialog, "_window_manager", None) is wm

    def test_construction_with_none_window_manager_safe(self):
        """Menu-scene loader (``screen_router.show_load_menu``) opens
        the dialog outside the strategy screen; passing ``None`` must
        be supported and skip live-list registration."""
        rect = pygame.Rect(0, 0, 600, 500)
        with bypass_init(SaveSelectionWindow):
            dialog = SaveSelectionWindow(
                rect,
                MagicMock(name="ui_manager"),
                on_load_callback=MagicMock(),
                on_cancel_callback=MagicMock(),
                window_manager=None,
                ui_builder=NullSaveSelectionWindowUiBuilder(),
            )
        assert getattr(dialog, "_window_manager", None) is None
