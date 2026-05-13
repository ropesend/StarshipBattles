"""Regression tests for strategy editor modal tracking.

PROJ-313 Phase 7 migrated the five environment/food editor windows to
``StrategyModalWindow`` so clicks inside those editors no longer leak
through to the strategy map. These tests pin the actual structural
contract: the real editor classes subclass the base class, the base class
registers/deregisters them, and the spawn sites pass the live strategy
window manager.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.ui.screens.atmosphere_target_editor import AtmosphereTargetEditor
from game.ui.screens.food_allocation_editor import FoodAllocationEditor
from game.ui.screens.gravity_target_editor import GravityTargetEditor
from game.ui.screens.radiation_shield_editor import RadiationShieldEditor
from game.ui.screens.strategy_modal_window import StrategyModalWindow
from game.ui.screens.water_target_editor import WaterTargetEditor


EDITOR_CLASSES = [
    FoodAllocationEditor,
    AtmosphereTargetEditor,
    GravityTargetEditor,
    WaterTargetEditor,
    RadiationShieldEditor,
]


class _Rect:
    """Minimal rect supporting collidepoint()."""

    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self._x, self._y, self._w, self._h = x, y, w, h

    def collidepoint(self, pos: tuple[int, int]) -> bool:
        x, y = pos
        return self._x <= x < self._x + self._w and self._y <= y < self._y + self._h


def _make_manager():
    """Build a minimal StrategyWindowManager-like stub."""
    from game.ui.screens.strategy_window_manager import StrategyWindowManager

    mgr = StrategyWindowManager.__new__(StrategyWindowManager)
    mgr._modals = []
    return mgr


def _make_editor_via_base_init(cls, window_manager):
    """Construct an editor while exercising only StrategyModalWindow.__init__."""
    with patch("pygame_gui.elements.UIWindow.__init__", lambda self, *a, **kw: None):
        win = cls.__new__(cls)
        StrategyModalWindow.__init__(win, window_manager=window_manager)
    win.alive = MagicMock(return_value=True)
    return win


def _make_router_with_editor(editor_rect: tuple[int, int, int, int] = (800, 500, 400, 300)):
    """Build a router stub that exercises iter_live_modals only."""
    from game.ui.screens.strategy_event_router import StrategyEventRouter

    ui = MagicMock()
    ui.width = 1920
    ui.sidebar_width = 300
    ui.menu_panel = None
    ui.fleet_context_menu = None  # issue #20: fleet right-click menu slot
    ui.top_bar = MagicMock()
    ui.top_bar.rect.collidepoint.return_value = False
    ui.resource_bar = MagicMock()
    ui.resource_bar.rect.collidepoint.return_value = False

    wm = MagicMock()
    # Slot scans: every modal slot None.
    for slot in (
        "fleet_orders_window", "planet_list_window", "star_list_window",
        "fleet_report_window", "transfer_dialog", "build_queue_list_window",
        "empire_build_queue_window", "event_log_window", "empire_panel_window",
        "_pending_confirmation_dialog", "move_choice_window",
        "cargo_quick_dialog", "planet_selection_window",
        "system_selection_window", "fleet_selection_window",
        "planet_abilities_window",
    ):
        setattr(wm, slot, None)

    # Modal-list path: simulate the editor having auto-registered.
    editor = MagicMock()
    editor.alive.return_value = True
    editor.rect = _Rect(*editor_rect)
    wm._modals = [editor]
    wm.iter_live_modals = lambda: iter([w for w in wm._modals if w.alive()])

    ui.window_manager = wm
    ui.scene = MagicMock()
    ui.scene.build_queue_screen = None

    router = StrategyEventRouter(ui)
    return router, editor


def _make_router_for_spawn_site():
    """Create a StrategyEventRouter with the fields editor spawns use."""
    from game.ui.screens.strategy_event_router import StrategyEventRouter

    ui = MagicMock()
    ui.width = 1920
    ui.height = 1080
    ui.manager = MagicMock()
    ui.window_manager = MagicMock(name="strategy_window_manager")

    scene = MagicMock()
    scene.session.get_empire.return_value = None
    scene.facade = MagicMock()
    ui.scene = scene

    return StrategyEventRouter(ui), ui


@pytest.mark.parametrize("cls", EDITOR_CLASSES)
def test_editor_subclasses_strategy_modal_window(cls) -> None:
    assert issubclass(cls, StrategyModalWindow)


@pytest.mark.parametrize("cls", EDITOR_CLASSES)
def test_editor_registers_and_deregisters_via_strategy_modal_window(cls) -> None:
    manager = _make_manager()
    win = _make_editor_via_base_init(cls, manager)

    assert win in list(manager.iter_live_modals())

    with patch("pygame_gui.elements.UIWindow.kill"):
        win.kill()

    assert win not in list(manager.iter_live_modals())


@pytest.mark.parametrize(
    ("method_name", "patch_target"),
    [
        (
            "_open_food_allocation_editor",
            "game.ui.screens.food_allocation_editor.FoodAllocationEditor",
        ),
        (
            "_open_atmosphere_editor",
            "game.ui.screens.atmosphere_target_editor.AtmosphereTargetEditor",
        ),
        (
            "_open_gravity_editor",
            "game.ui.screens.gravity_target_editor.GravityTargetEditor",
        ),
        (
            "_open_water_editor",
            "game.ui.screens.water_target_editor.WaterTargetEditor",
        ),
        (
            "_open_radiation_shield_editor",
            "game.ui.screens.radiation_shield_editor.RadiationShieldEditor",
        ),
    ],
)
def test_editor_spawn_site_passes_strategy_window_manager(method_name, patch_target) -> None:
    router, ui = _make_router_for_spawn_site()
    planet = MagicMock(owner_id=123)

    with patch(patch_target) as editor_cls:
        getattr(router, method_name)(planet)

    assert editor_cls.call_count == 1
    assert editor_cls.call_args.args == ()
    assert editor_cls.call_args.kwargs["window_manager"] is ui.window_manager
    assert editor_cls.call_args.kwargs["window_manager"] is not None


def test_router_blocks_clicks_inside_any_modal_in_iter_live_modals() -> None:
    """Click inside any live modal rect must not pass through to the map."""
    router, _editor = _make_router_with_editor((800, 500, 400, 300))

    assert router._is_blocking_ui_element_at(900, 600) is True


def test_editor_blocks_click_outside_rect_under_full_modality() -> None:
    """Click outside the editor's rect must be blocked (issue #12).

    Renamed/inverted from the prior ``test_editor_does_not_block_click_outside_rect``
    as part of issue #12. The previous contract (rect-coincident block,
    gutter pass-through) is intentionally replaced with full modality:
    any live ``StrategyModalWindow`` blocks ALL background clicks
    regardless of click position relative to the window's rect.

    The rename leaves a discoverable archaeology trail for future agents
    grepping for the old name — see Anti-Reversion Notes in the issue #12
    investigation.
    """
    router, _editor = _make_router_with_editor((800, 500, 400, 300))

    assert router._is_blocking_ui_element_at(100, 100) is True


def test_dead_editor_does_not_block() -> None:
    """Dead windows are filtered out by iter_live_modals."""
    router, editor = _make_router_with_editor((800, 500, 400, 300))
    editor.alive.return_value = False

    assert router._is_blocking_ui_element_at(900, 600) is False


def test_no_editors_open_passes_clicks_through() -> None:
    """When no editors are open, clicks pass through."""
    from game.ui.screens.strategy_event_router import StrategyEventRouter

    ui = MagicMock()
    ui.width = 1920
    ui.sidebar_width = 300
    ui.menu_panel = None
    ui.fleet_context_menu = None  # issue #20: fleet right-click menu slot
    ui.top_bar = MagicMock()
    ui.top_bar.rect.collidepoint.return_value = False
    ui.resource_bar = MagicMock()
    ui.resource_bar.rect.collidepoint.return_value = False

    wm = MagicMock()
    for slot in (
        "fleet_orders_window", "planet_list_window", "star_list_window",
        "fleet_report_window", "transfer_dialog", "build_queue_list_window",
        "empire_build_queue_window", "event_log_window", "empire_panel_window",
        "_pending_confirmation_dialog", "move_choice_window",
        "cargo_quick_dialog", "planet_selection_window",
        "system_selection_window", "fleet_selection_window",
        "planet_abilities_window",
    ):
        setattr(wm, slot, None)
    wm._modals = []
    wm.iter_live_modals = lambda: iter([])
    ui.window_manager = wm
    ui.scene = MagicMock()
    ui.scene.build_queue_screen = None

    router = StrategyEventRouter(ui)

    assert router._is_blocking_ui_element_at(900, 600) is False
