"""MOD-001 (PROJ-470): SettingsWindow conforms to Pattern #31 (StrategyModalWindow).

Previously ``SettingsWindow(UIWindow)`` was a manual-close-callback window that
was NOT counted by ``has_modal_open()`` and did not set ``is_blocking`` — so
background hover/click leaked through while Settings was open. These tests pin
the conformance to the StrategyModalWindow base class.
"""
from __future__ import annotations

import inspect
from unittest.mock import MagicMock

import pygame

from game.ui.screens.settings_window import SettingsWindow
from game.ui.screens.strategy_modal_window import StrategyModalWindow
from tests.fixtures.ui_widget_factory import bypass_init


def test_settings_window_subclasses_strategy_modal_window() -> None:
    assert issubclass(SettingsWindow, StrategyModalWindow)


def test_settings_window_requires_window_manager_kwarg() -> None:
    """Strategy-screen modals must require explicit ``window_manager`` wiring
    (mirrors test_strategy_modal_window.TestWindowManagerSignature)."""
    param = inspect.signature(SettingsWindow.__init__).parameters["window_manager"]
    assert param.default is inspect.Parameter.empty
    assert param.kind is inspect.Parameter.KEYWORD_ONLY


def _build_settings_through_production_path(mgr, on_close=None) -> SettingsWindow:
    """Construct a real SettingsWindow via the NON-bypass code path with
    pygame_gui's heavy ``UIWindow.__init__`` stubbed to a no-op.

    This exercises ``StrategyModalWindow.__init__``'s production side-effects
    (``register_modal(self)`` + ``is_blocking = True``) for the SettingsWindow
    subclass specifically — bypass_init would skip exactly those. Stage-3
    widget construction is short-circuited by injecting a no-op ``ui_builder``
    (PROJ-458 retrofit seam): the production path runs register_modal +
    is_blocking via ``StrategyModalWindow.__init__`` without needing a real
    pygame display or attempting to read ``window.rect`` from a half-initialised
    sprite.
    """
    from unittest.mock import patch

    def _stub_init(self, *args, **kwargs):  # noqa: ANN001 — pygame_gui shim
        return None

    with patch("pygame_gui.elements.UIWindow.__init__", _stub_init):
        win = SettingsWindow(
            pygame.Rect(0, 0, 500, 200),
            MagicMock(name="ui_manager"),
            window_manager=mgr,
            on_close_callback=on_close,
            ui_builder=MagicMock(spec=["build"]),
        )
    return win


def test_settings_window_registers_as_live_modal_on_construction() -> None:
    """Constructing SettingsWindow with a manager registers it as a live modal
    so ``iter_live_modals()`` / ``has_modal_open()`` count it — exercised through
    the PRODUCTION code path (not bypass_init, which skips registration)."""
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

    mgr = StrategyWindowManager.__new__(StrategyWindowManager)
    mgr._modals = []

    win = _build_settings_through_production_path(mgr)

    # Construction side-effects from StrategyModalWindow.__init__ via the
    # production path: SettingsWindow registers itself with the manager (so
    # has_modal_open()/iter_live_modals() count it once .alive() is backed by
    # a real sprite group in production). We assert direct membership rather
    # than iter_live_modals() because UIWindow.__init__ is stubbed here, so
    # the sprite-group state .alive() reads is not initialized.
    assert win in mgr._modals
    assert win._window_manager is mgr
    assert getattr(win, "_window_init_bypassed", None) is False


def test_settings_window_is_blocking_on_construction() -> None:
    """Issue #12 hover-block: a constructed SettingsWindow must set
    ``is_blocking = True`` so background hover/click is suppressed while the
    settings modal is open — pinned on the SettingsWindow subclass via the
    production path."""
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

    mgr = StrategyWindowManager.__new__(StrategyWindowManager)
    mgr._modals = []

    win = _build_settings_through_production_path(mgr)

    assert win.is_blocking is True


def test_settings_window_kill_invokes_on_close_callback_and_deregisters() -> None:
    """The registrar slot-cleanup callback must still fire on kill, while
    deregistration is handled by the StrategyModalWindow base."""
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

    mgr = StrategyWindowManager.__new__(StrategyWindowManager)
    mgr._modals = []
    on_close = MagicMock(name="on_close_callback")

    with bypass_init(SettingsWindow):
        win = SettingsWindow(
            pygame.Rect(0, 0, 500, 200),
            MagicMock(name="ui_manager"),
            window_manager=mgr,
            on_close_callback=on_close,
        )
    mgr.register_modal(win)
    win.alive = MagicMock(return_value=True)

    from unittest.mock import patch

    with patch("pygame_gui.elements.UIWindow.kill"):
        win.kill()

    on_close.assert_called_once()
    assert win not in mgr._modals
