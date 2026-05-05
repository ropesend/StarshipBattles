"""Tests for the PROJ-313 StrategyModalWindow base class.

The base class auto-registers subclasses with a StrategyWindowManager on
construction and auto-deregisters in kill(). These tests pin the
structural invariant that replaces the removed (Phase 8) source-string
matching ``TestModalSlotCleanupContract``.

PROJ-328 Phase A Task A.5 (PROJ-322 Task 3.24): Migrated from the
legacy ``__new__`` + ``patch("pygame_gui.elements.UIWindow.__init__")``
helper to the two-stage bypass_init pattern. After Task A.1, the
StrategyModalWindow bypass branch leaves a usable minimal shell
(_window_manager, ui_manager, _window_init_bypassed all set), so
direct construction under bypass_init is the canonical test path.
"""
from __future__ import annotations

import inspect
from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.screens.strategy_modal_window import StrategyModalWindow
from tests.fixtures.ui_widget_factory import bypass_init


class _ProbeModal(StrategyModalWindow):
    """Concrete StrategyModalWindow subclass for tests that need a
    constructible instance.

    The base class accepts ``window_manager`` as a keyword-only
    argument; this subclass narrows the signature so tests can
    construct it as ``_ProbeModal(rect, manager, window_manager=...)``.
    """

    def __init__(self, rect, manager, *, window_manager):
        super().__init__(
            rect, manager,
            window_manager=window_manager,
            window_display_title="Probe",
            resizable=False,
        )


def _make_modal_window(window_manager):
    """Construct a real ``_ProbeModal`` under ``bypass_init``.

    PROJ-328 Phase A: the base bypass branch now sets
    ``_window_manager``, ``ui_manager``, and ``_window_init_bypassed``
    so the returned instance is usable. Manual registration is needed
    because the base intentionally skips ``register_modal`` under
    bypass (bypassed instances are test fixtures, not live windows).
    """
    with bypass_init(_ProbeModal):
        win = _ProbeModal(
            pygame.Rect(0, 0, 100, 100),
            MagicMock(name="ui_manager"),
            window_manager=window_manager,
        )
    if window_manager is not None:
        window_manager.register_modal(win)
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
    """A subclass instance must appear in iter_live_modals on construction.

    PROJ-353 Tier-7 (T2.12): retrofit. After PROJ-328 A.5 the original
    versions of these tests went through `_make_modal_window`, which
    uses `bypass_init` and then MANUALLY calls
    `window_manager.register_modal(win)`. That meant the assertions were
    actually pinning the factory's manual call, not the production
    "register on construction" side-effect we care about.

    The retrofit goes through the production code path: stub
    `UIWindow.__init__` (the heavy pygame-display dependency that
    `bypass_init` was created to avoid) and assert that
    `register_modal` is invoked as a construction side-effect of
    `StrategyModalWindow.__init__` itself, NOT via a manual fixture call.
    """

    def _build_through_production_path(self, mgr) -> "_ProbeModal":
        """Construct a real `_ProbeModal` via the non-bypass code path
        with `pygame_gui.elements.UIWindow.__init__` stubbed to a no-op.
        Sets the few attributes the un-bypassed branch leaves to the
        UIWindow chain (otherwise `register_modal`'s downstream
        operations have nothing to attach to)."""

        def _stub_init(self, *args, **kwargs):  # noqa: ANN001 — pygame_gui shim
            return None

        with patch(
            "pygame_gui.elements.UIWindow.__init__", _stub_init,
        ):
            win = _ProbeModal(
                pygame.Rect(0, 0, 100, 100),
                MagicMock(name="ui_manager"),
                window_manager=mgr,
            )
        return win

    def test_construction_registers_with_manager(self) -> None:
        mgr = _make_manager()

        # Production path — NO manual `register_modal` call from the
        # test side. Construction itself should register the modal.
        win = self._build_through_production_path(mgr)

        assert win in mgr._modals
        # The bypass flag must NOT be set — we went through real init.
        assert getattr(win, "_window_init_bypassed", None) is False

    def test_two_instances_both_registered(self) -> None:
        mgr = _make_manager()
        a = self._build_through_production_path(mgr)
        b = self._build_through_production_path(mgr)

        # Both must have arrived via the construction side-effect — not
        # via any factory-side manual `register_modal` call.
        assert a in mgr._modals
        assert b in mgr._modals
        assert len(mgr._modals) == 2

    def test_construction_with_none_window_manager_does_not_register(self) -> None:
        """The production guard `if window_manager is not None` skips
        registration when no manager is supplied. Pin that branch too —
        otherwise a future refactor that drops the guard would silently
        crash on `None.register_modal(...)` at construction."""

        def _stub_init(self, *args, **kwargs):  # noqa: ANN001
            return None

        with patch(
            "pygame_gui.elements.UIWindow.__init__", _stub_init,
        ):
            # No manager — construction should NOT crash even though
            # there's nothing to register with.
            win = _ProbeModal(
                pygame.Rect(0, 0, 100, 100),
                MagicMock(name="ui_manager"),
                window_manager=None,
            )

        assert win._window_manager is None


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
        # Define a fresh subclass mid-test
        class _RegistryProbeWindow(StrategyModalWindow):
            pass

        try:
            assert _RegistryProbeWindow in StrategyModalWindow._registered_subclasses
        finally:
            StrategyModalWindow._registered_subclasses.discard(_RegistryProbeWindow)


class TestBypassShellInvariants:
    """PROJ-328 Phase A Task A.1: the bypass branch leaves a usable
    minimal shell — exercises the new contract directly."""

    def test_bypass_sets_window_init_bypassed_flag(self):
        win = _make_modal_window(_make_manager())
        assert win._window_init_bypassed is True

    def test_bypass_sets_window_manager_attribute(self):
        mgr = _make_manager()
        win = _make_modal_window(mgr)
        assert win._window_manager is mgr

    def test_bypass_sets_ui_manager_attribute(self):
        win = _make_modal_window(_make_manager())
        # ui_manager is the MagicMock we passed as the manager arg.
        assert win.ui_manager is not None

    def test_bypass_skips_window_manager_register_call(self):
        """Per Task A.1 contract: the bypass branch does not call
        register_modal — bypassed instances are test fixtures, not
        live windows. (The _make_modal_window helper does the manual
        register so the legacy registration tests still work.)"""
        mgr = _make_manager()
        with bypass_init(_ProbeModal):
            _ProbeModal(
                pygame.Rect(0, 0, 100, 100),
                MagicMock(name="ui_manager"),
                window_manager=mgr,
            )
        # No automatic registration under bypass.
        assert mgr._modals == []

    def test_production_path_still_registers(self):
        """Without bypass_init, the base goes through super().__init__
        and register_modal — verified at the base-class level by
        leaving bypass_init off and stubbing the heavy UIWindow init."""
        mgr = _make_manager()
        with patch("pygame_gui.elements.UIWindow.__init__",
                   lambda self, *a, **kw: None):
            win = _ProbeModal.__new__(_ProbeModal)
            StrategyModalWindow.__init__(
                win,
                pygame.Rect(0, 0, 100, 100),
                MagicMock(),
                window_manager=mgr,
                window_display_title="Probe",
                resizable=False,
            )

        assert win in mgr._modals
        assert win._window_init_bypassed is False


class TestWindowManagerSignature:
    """Strategy-screen-only modals must require explicit manager wiring."""

    @pytest.mark.parametrize(
        "cls",
        [
            pytest.param(
                __import__(
                    "game.ui.screens.planet_list_window",
                    fromlist=["PlanetListWindow"],
                ).PlanetListWindow,
                id="PlanetListWindow",
            ),
            pytest.param(
                __import__(
                    "game.ui.screens.star_list_window",
                    fromlist=["StarListWindow"],
                ).StarListWindow,
                id="StarListWindow",
            ),
            pytest.param(
                __import__(
                    "game.ui.screens.build_queue_list_window",
                    fromlist=["BuildQueueListWindow"],
                ).BuildQueueListWindow,
                id="BuildQueueListWindow",
            ),
            pytest.param(
                __import__(
                    "game.ui.screens.empire_build_queue_window",
                    fromlist=["EmpireBuildQueueWindow"],
                ).EmpireBuildQueueWindow,
                id="EmpireBuildQueueWindow",
            ),
            pytest.param(
                __import__(
                    "game.ui.screens.event_log_window",
                    fromlist=["EventLogWindow"],
                ).EventLogWindow,
                id="EventLogWindow",
            ),
            pytest.param(
                __import__(
                    "game.ui.screens.empire_panel_window",
                    fromlist=["EmpirePanelWindow"],
                ).EmpirePanelWindow,
                id="EmpirePanelWindow",
            ),
            pytest.param(
                __import__(
                    "game.ui.screens.fleet_report_window",
                    fromlist=["FleetReportWindow"],
                ).FleetReportWindow,
                id="FleetReportWindow",
            ),
            pytest.param(
                __import__(
                    "game.ui.screens.planet_abilities_window",
                    fromlist=["PlanetAbilitiesWindow"],
                ).PlanetAbilitiesWindow,
                id="PlanetAbilitiesWindow",
            ),
            pytest.param(
                __import__(
                    "game.ui.screens.strategy_windows.move_choice_dialog",
                    fromlist=["MoveChoiceWindow"],
                ).MoveChoiceWindow,
                id="MoveChoiceWindow",
            ),
            pytest.param(
                __import__(
                    "game.ui.screens.food_allocation_editor",
                    fromlist=["FoodAllocationEditor"],
                ).FoodAllocationEditor,
                id="FoodAllocationEditor",
            ),
            pytest.param(
                __import__(
                    "game.ui.screens.atmosphere_target_editor",
                    fromlist=["AtmosphereTargetEditor"],
                ).AtmosphereTargetEditor,
                id="AtmosphereTargetEditor",
            ),
            pytest.param(
                __import__(
                    "game.ui.screens.gravity_target_editor",
                    fromlist=["GravityTargetEditor"],
                ).GravityTargetEditor,
                id="GravityTargetEditor",
            ),
            pytest.param(
                __import__(
                    "game.ui.screens.water_target_editor",
                    fromlist=["WaterTargetEditor"],
                ).WaterTargetEditor,
                id="WaterTargetEditor",
            ),
            pytest.param(
                __import__(
                    "game.ui.screens.radiation_shield_editor",
                    fromlist=["RadiationShieldEditor"],
                ).RadiationShieldEditor,
                id="RadiationShieldEditor",
            ),
        ],
    )
    def test_strategy_only_windows_require_explicit_window_manager(self, cls) -> None:
        param = inspect.signature(cls.__init__).parameters["window_manager"]

        assert param.default is inspect.Parameter.empty


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
