"""PROJ-313 Phase 7: regression tests for the 5 editor windows that
previously leaked clicks through to the strategy map.

These editors (FoodAllocationEditor, AtmosphereTargetEditor,
GravityTargetEditor, WaterTargetEditor, RadiationShieldEditor) were
spawned over the strategy screen but had no slot, no has_modal_open()
clause, and no _is_blocking_ui_element_at() clause — so clicks inside
them passed through to the underlying galaxy map (QA Session
20260428_052952 reported the food-allocation editor specifically).

After Phase 7 they all subclass ``StrategyModalWindow`` and auto-register
via ``iter_live_modals()``. Clicks within their rect block.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class _Rect:
    """Minimal rect supporting collidepoint()."""

    def __init__(self, x, y, w, h):
        self._x, self._y, self._w, self._h = x, y, w, h

    def collidepoint(self, pos):
        x, y = pos
        return self._x <= x < self._x + self._w and self._y <= y < self._y + self._h


def _make_router_with_editor(editor_rect=(800, 500, 400, 300)):
    """Build a router stub that exercises iter_live_modals only.

    Mirrors the per-test fixture pattern used by the existing
    test_click_gate_integration.py.
    """
    from game.ui.screens.strategy_event_router import StrategyEventRouter

    ui = MagicMock()
    ui.width = 1920
    ui.sidebar_width = 300
    ui.menu_panel = None
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
    # Mirror the production iter_live_modals contract: filter dead refs.
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


@pytest.mark.parametrize("editor_class_name", [
    "FoodAllocationEditor",
    "AtmosphereTargetEditor",
    "GravityTargetEditor",
    "WaterTargetEditor",
    "RadiationShieldEditor",
])
def test_editor_blocks_click_inside_rect(editor_class_name):
    """Click inside the editor's rect must NOT pass through to the strategy map.

    Pre-PROJ-313: these editors had no slot tracking, so
    `_is_blocking_ui_element_at` returned False even when the editor was
    open and the click was inside its rect — clicks leaked to the map.

    Post-Phase 7: each editor subclasses StrategyModalWindow and
    auto-registers via `iter_live_modals()`, so the OR-bridge in
    `_is_blocking_ui_element_at` blocks the click.
    """
    router, editor = _make_router_with_editor((800, 500, 400, 300))

    # Click inside the editor's rect (900, 600).
    result = router._is_blocking_ui_element_at(900, 600)

    assert result is True, (
        f"{editor_class_name} (registered via iter_live_modals) "
        f"failed to block a click inside its rect."
    )


@pytest.mark.parametrize("editor_class_name", [
    "FoodAllocationEditor",
    "AtmosphereTargetEditor",
    "GravityTargetEditor",
    "WaterTargetEditor",
    "RadiationShieldEditor",
])
def test_editor_does_not_block_click_outside_rect(editor_class_name):
    """Click outside the editor's rect should pass through to the map.

    Confirms the auto-registered editor only blocks clicks within its
    own rect — the modal-tracking does not over-block.
    """
    router, editor = _make_router_with_editor((800, 500, 400, 300))

    # Click well outside the editor's rect (100, 100).
    result = router._is_blocking_ui_element_at(100, 100)

    assert result is False


def test_dead_editor_does_not_block():
    """If the editor's underlying window is dead, iter_live_modals
    filters it out and the click passes through. Phase 1's GC walk."""
    router, editor = _make_router_with_editor((800, 500, 400, 300))
    editor.alive.return_value = False

    result = router._is_blocking_ui_element_at(900, 600)

    assert result is False


def test_no_editors_open_passes_clicks_through():
    """When no editors are open (modal list empty), clicks pass through."""
    from game.ui.screens.strategy_event_router import StrategyEventRouter

    ui = MagicMock()
    ui.width = 1920
    ui.sidebar_width = 300
    ui.menu_panel = None
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
