"""Tests for the PROJ-313 StrategyModalWindow base class.

The base class auto-registers subclasses with a StrategyWindowManager on
construction and auto-deregisters in kill(). These tests pin the
structural invariant that replaces the removed (Phase 8) source-string
matching ``TestModalSlotCleanupContract``.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def _make_modal_window(window_manager, cls=None):
    """Construct a StrategyModalWindow instance without booting pygame_gui.

    Uses the ``__new__`` + patched-pygame_gui-init technique so the test
    does not need a live display. The base class's own ``__init__`` is
    invoked manually so registration runs and ``self._window_manager``
    is populated.
    """
    from game.ui.screens.strategy_modal_window import StrategyModalWindow

    if cls is None:
        cls = StrategyModalWindow

    with patch("pygame_gui.elements.UIWindow.__init__",
               lambda self, *a, **kw: None):
        win = cls.__new__(cls)
        # Invoke the base class __init__ explicitly. The first positional
        # arg is empty (UIWindow.__init__ is patched to accept anything).
        StrategyModalWindow.__init__(win, window_manager=window_manager)
    # alive() is exercised in some tests; default to True
    win.alive = MagicMock(return_value=True)
    return win


def _make_manager():
    """Build a minimal StrategyWindowManager-like stub.

    The real class wires registrars in __init__; we only need the modal
    list and the three new methods for these tests.
    """
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

    mgr = StrategyWindowManager.__new__(StrategyWindowManager)
    mgr._modals = []
    return mgr


class TestRegisterOnConstruction:
    """A subclass instance must appear in iter_live_modals on construction."""

    def test_construction_registers_with_manager(self) -> None:
        mgr = _make_manager()
        win = _make_modal_window(mgr)

        assert win in list(mgr.iter_live_modals())

    def test_two_instances_both_registered(self) -> None:
        mgr = _make_manager()
        a = _make_modal_window(mgr)
        b = _make_modal_window(mgr)

        live = list(mgr.iter_live_modals())
        assert a in live
        assert b in live
        assert len(live) == 2


class TestKillDeregisters:
    """kill() must remove the instance from iter_live_modals before super.kill."""

    def test_kill_removes_from_live_list(self) -> None:
        mgr = _make_manager()
        win = _make_modal_window(mgr)
        assert win in list(mgr.iter_live_modals())

        with patch("pygame_gui.elements.UIWindow.kill"):
            win.kill()

        # alive() is still True (we mocked it), but the deregistration in
        # kill() should have removed it from the manager's list directly.
        assert win not in mgr._modals

    def test_kill_is_idempotent(self) -> None:
        mgr = _make_manager()
        win = _make_modal_window(mgr)

        with patch("pygame_gui.elements.UIWindow.kill"):
            win.kill()
            win.kill()  # second call must not raise

        assert win not in mgr._modals

    def test_kill_calls_super_kill(self) -> None:
        mgr = _make_manager()
        win = _make_modal_window(mgr)

        with patch("pygame_gui.elements.UIWindow.kill") as super_kill:
            win.kill()

        super_kill.assert_called_once()


class TestIterLiveModalsReapsDeadRefs:
    """Parent-kill cascades may orphan refs; iter_live_modals reaps them."""

    def test_dead_ref_reaped_within_one_walk(self) -> None:
        mgr = _make_manager()
        win = _make_modal_window(mgr)

        # Simulate parent-kill cascade: window's alive() returns False but
        # kill() override never ran (so deregistration didn't happen).
        win.alive = MagicMock(return_value=False)

        live = list(mgr.iter_live_modals())
        assert win not in live
        # The internal list is also rewritten — dead ref is gone.
        assert win not in mgr._modals

    def test_mixed_alive_and_dead(self) -> None:
        mgr = _make_manager()
        alive_win = _make_modal_window(mgr)
        dead_win = _make_modal_window(mgr)
        dead_win.alive = MagicMock(return_value=False)

        live = list(mgr.iter_live_modals())
        assert alive_win in live
        assert dead_win not in live


class TestSubclassRegistry:
    """__init_subclass__ populates StrategyModalWindow._registered_subclasses."""

    def test_init_subclass_populates_registry(self) -> None:
        from game.ui.screens.strategy_modal_window import StrategyModalWindow

        # Define a fresh subclass mid-test
        class _ProbeWindow(StrategyModalWindow):
            pass

        try:
            assert _ProbeWindow in StrategyModalWindow._registered_subclasses
        finally:
            StrategyModalWindow._registered_subclasses.discard(_ProbeWindow)


class TestMultipleManagersIsolated:
    """Each manager owns its own modal list — no cross-contamination."""

    def test_two_managers_each_see_only_their_own(self) -> None:
        mgr_a = _make_manager()
        mgr_b = _make_manager()

        win_a = _make_modal_window(mgr_a)
        win_b = _make_modal_window(mgr_b)

        live_a = list(mgr_a.iter_live_modals())
        live_b = list(mgr_b.iter_live_modals())

        assert win_a in live_a
        assert win_a not in live_b
        assert win_b in live_b
        assert win_b not in live_a
