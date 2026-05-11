"""Layer 3 tests for issue #20: menu -> router dispatch + dismissal.

When the user clicks an entry in the fleet context menu, the menu must:

  1. Close itself (one-shot).
  2. Route the carried ``InputAction`` through
     ``FleetCommandRouter.handle_fleet_action`` first, then
     ``handle_superweapon_action`` if the first didn't claim it.

These tests use a fake router with the two methods instrumented; they
verify that the menu's ``on_action_selected`` does the right thing for
each ``InputAction`` value the menu can carry.

Dismissal:

  - Esc closes the menu (via ``strategy_event_router.route_event``).
  - Click outside the menu rect closes it.

The Esc + click-outside tests reuse the StrategyEventRouter test-mock
pattern from ``test_strategy_event_router_esc_modal.py``.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pygame
import pytest

from game.core.input_actions import InputAction
from game.ui.screens.strategy_event_router import StrategyEventRouter
from game.ui.screens.strategy_fleet_context_menu import (
    FleetContextMenu,
    dispatch_action,
)


# ---------------------------------------------------------------------------
# Router dispatch tests (pure: no pygame)
# ---------------------------------------------------------------------------


def _router_with_claim(claim: dict[InputAction, str]) -> SimpleNamespace:
    """Build a fake fleet router.

    ``claim[action]`` is either ``"fleet"`` (handle_fleet_action returns
    True), ``"superweapon"`` (handle_superweapon_action returns True),
    or absent (both return False).
    """

    def handle_fleet_action(action: InputAction) -> bool:
        return claim.get(action) == "fleet"

    def handle_superweapon_action(action: InputAction) -> bool:
        return claim.get(action) == "superweapon"

    return SimpleNamespace(
        handle_fleet_action=MagicMock(side_effect=handle_fleet_action),
        handle_superweapon_action=MagicMock(side_effect=handle_superweapon_action),
    )


@pytest.mark.parametrize(
    "action,expected_router",
    [
        (InputAction.FLEET_MOVE, "fleet"),
        (InputAction.FLEET_JOIN, "fleet"),
        (InputAction.FLEET_COLONIZE, "fleet"),
        (InputAction.FLEET_TRANSFER, "fleet"),
        (InputAction.FLEET_DROP_CARGO, "fleet"),
        (InputAction.FLEET_LOAD_CARGO, "fleet"),
        (InputAction.FLEET_WARP, "fleet"),
        (InputAction.FLEET_OPEN_WARP_POINT, "superweapon"),
        (InputAction.FLEET_CLOSE_WARP_POINT, "superweapon"),
        (InputAction.FLEET_IMPLODE_PLANET, "superweapon"),
        (InputAction.FLEET_STELLERATE_STAR, "superweapon"),
        (InputAction.FLEET_CREATE_DYSON_SPHERE, "superweapon"),
        (InputAction.FLEET_SELF_DESTRUCT, "superweapon"),
    ],
)
def test_dispatch_action_routes_to_correct_handler(action, expected_router):
    """T20-T26: each menu action lands on the correct router method."""
    router = _router_with_claim({action: expected_router})
    dispatch_action(router, action)
    if expected_router == "fleet":
        router.handle_fleet_action.assert_called_once_with(action)
        router.handle_superweapon_action.assert_not_called()
    else:
        # Fleet-action tried first, then falls through to superweapon.
        router.handle_fleet_action.assert_called_once_with(action)
        router.handle_superweapon_action.assert_called_once_with(action)


def test_dispatch_action_no_router_claims_is_a_no_op():
    """If neither router claims the action, the call is a silent no-op."""
    router = _router_with_claim({})
    dispatch_action(router, InputAction.FLEET_MOVE)
    router.handle_fleet_action.assert_called_once()
    router.handle_superweapon_action.assert_called_once()


# ---------------------------------------------------------------------------
# T20-T26 also covered via the parametrize above.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Dismissal (Esc + click-outside) via StrategyEventRouter
# ---------------------------------------------------------------------------


def _keydown(key):
    return pygame.event.Event(pygame.KEYDOWN, {"key": key, "mod": 0})


def _mousedown(pos, button=1):
    return pygame.event.Event(
        pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": button}
    )


def _make_event_router_ui(fleet_context_menu=None):
    """Mock StrategyUI plumbing for event-router tests."""
    ui = MagicMock()
    ui.width = 2560
    ui.height = 1600
    ui.menu_panel = None
    ui.fleet_context_menu = fleet_context_menu

    ui.window_manager = MagicMock()
    ui.window_manager.fleet_orders_window = None
    ui.window_manager._modals_for_test = []
    ui.window_manager.iter_live_modals = lambda: iter(
        list(ui.window_manager._modals_for_test)
    )
    ui.window_manager.process_ui_callbacks.return_value = False

    ui.system_tree = MagicMock()
    ui.system_tree.process_event.return_value = False
    ui.sector_tree = MagicMock()
    ui.sector_tree.process_event.return_value = False
    return ui


def _make_fake_menu(rect=pygame.Rect(100, 100, 200, 300)):
    menu = MagicMock(spec=FleetContextMenu)
    menu.get_abs_rect.return_value = rect
    return menu


def test_T27_esc_closes_open_fleet_context_menu():
    menu = _make_fake_menu()
    ui = _make_event_router_ui(fleet_context_menu=menu)
    router = StrategyEventRouter(ui)
    router.route_event(_keydown(pygame.K_ESCAPE))
    ui.close_fleet_context_menu.assert_called_once()


def test_T28_left_click_outside_menu_closes_it():
    menu = _make_fake_menu(rect=pygame.Rect(100, 100, 200, 300))
    ui = _make_event_router_ui(fleet_context_menu=menu)
    router = StrategyEventRouter(ui)
    # Click at (10, 10) — well outside the menu rect.
    router.route_event(_mousedown((10, 10), button=1))
    ui.close_fleet_context_menu.assert_called_once()


def test_T28b_left_click_inside_menu_does_not_close_it():
    menu = _make_fake_menu(rect=pygame.Rect(100, 100, 200, 300))
    ui = _make_event_router_ui(fleet_context_menu=menu)
    router = StrategyEventRouter(ui)
    # Click at (150, 150) — inside the menu rect.
    router.route_event(_mousedown((150, 150), button=1))
    ui.close_fleet_context_menu.assert_not_called()


def test_T29_right_click_outside_menu_closes_it():
    menu = _make_fake_menu(rect=pygame.Rect(100, 100, 200, 300))
    ui = _make_event_router_ui(fleet_context_menu=menu)
    router = StrategyEventRouter(ui)
    router.route_event(_mousedown((400, 400), button=3))
    ui.close_fleet_context_menu.assert_called_once()


def test_esc_menu_panel_takes_precedence_over_fleet_context_menu():
    """If both panels are open, Esc closes the top-bar menu first.

    Mirrors the documented precedence chain in #18's Esc handler:
    menu_panel -> fleet_context_menu -> topmost modal window.
    """
    menu = _make_fake_menu()
    ui = _make_event_router_ui(fleet_context_menu=menu)
    ui.menu_panel = MagicMock()  # top-bar menu is open too
    router = StrategyEventRouter(ui)
    router.route_event(_keydown(pygame.K_ESCAPE))
    ui.close_menu_panel.assert_called_once()
    ui.close_fleet_context_menu.assert_not_called()


def test_esc_no_menus_open_does_not_call_close():
    ui = _make_event_router_ui(fleet_context_menu=None)
    router = StrategyEventRouter(ui)
    router.route_event(_keydown(pygame.K_ESCAPE))
    ui.close_fleet_context_menu.assert_not_called()
