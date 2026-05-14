"""Layer 2 tests for issue #20: right-click 3-way branch in SELECT mode.

Decisions Q1 (per team-lead):

  1. Right-click hex with currently-selected friendly fleet -> open menu.
  2. Right-click hex with a *different* friendly fleet -> select that
     fleet, then open menu.
  3. Right-click hex with no friendly fleet -> preserve existing
     Quick-Move-to-hex for the already-selected fleet.

These tests drive the change in ``ClickModeDispatcher._handle_select_mode_click``.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pygame  # noqa: F401 — Pygame init implicitly needed by underlying types

from game.core.hex_math import HexCoord
from game.ui.screens.strategy_click_dispatcher import ClickModeDispatcher


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _IdentityCamera:
    def __init__(self, *, hex_at: HexCoord = HexCoord(0, 0)) -> None:
        self.zoom = 1.0
        self._hex_at = hex_at

    def hex_at_screen(self, _x: int, _y: int, _hex_size: float) -> HexCoord:
        return self._hex_at

    def world_to_screen(self, world_pos):
        return world_pos


def _fleet(*, fleet_id: int, owner_id: int, location: HexCoord) -> SimpleNamespace:
    return SimpleNamespace(id=fleet_id, owner_id=owner_id, location=location)


def _empire(owner_id: int, fleets: list[SimpleNamespace]) -> SimpleNamespace:
    return SimpleNamespace(owner_id=owner_id, fleets=fleets)


def _scene(
    *,
    selected_fleet: SimpleNamespace | None,
    empires: list[SimpleNamespace],
    current_player_id: int = 1,
    hex_at: HexCoord = HexCoord(0, 0),
) -> SimpleNamespace:
    ui = MagicMock()
    fleet_ops = MagicMock()
    # Default move-designation returns no result (no Quick-Move side-effect).
    fleet_ops.handle_move_designation.return_value = None
    return SimpleNamespace(
        camera=_IdentityCamera(hex_at=hex_at),
        hex_size=10,
        empires=empires,
        galaxy=None,
        ui=ui,
        on_ui_selection=MagicMock(),
        selected_object=None,
        selected_fleet=selected_fleet,
        last_selected_system=None,
        _fleet_ops=fleet_ops,
        human_player_ids=[current_player_id],
        current_player_index=0,
        _get_system_at_hex=lambda _h: None,
    )


def _dispatcher(scene: SimpleNamespace) -> tuple[ClickModeDispatcher, SimpleNamespace]:
    handler = SimpleNamespace(scene=scene, input_mode="SELECT", _fleet_router=MagicMock())
    return ClickModeDispatcher(handler), handler


# ---------------------------------------------------------------------------
# T14 — Right-click on currently-selected fleet's hex opens the menu
# ---------------------------------------------------------------------------


def test_T14_rmb_on_selected_fleet_hex_opens_menu():
    f1 = _fleet(fleet_id=1, owner_id=1, location=HexCoord(0, 0))
    scene = _scene(
        selected_fleet=f1,
        empires=[_empire(1, [f1])],
        hex_at=HexCoord(0, 0),
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.ui.open_fleet_context_menu.assert_called_once()
    args = scene.ui.open_fleet_context_menu.call_args
    assert args.args[0] is f1
    scene._fleet_ops.handle_move_designation.assert_not_called()


# ---------------------------------------------------------------------------
# T15 — Right-click on a different friendly fleet selects then opens menu
# ---------------------------------------------------------------------------


def test_T15_rmb_on_different_friendly_fleet_selects_then_opens_menu():
    f1 = _fleet(fleet_id=1, owner_id=1, location=HexCoord(5, 5))
    f2 = _fleet(fleet_id=2, owner_id=1, location=HexCoord(0, 0))
    scene = _scene(
        selected_fleet=f1,
        empires=[_empire(1, [f1, f2])],
        hex_at=HexCoord(0, 0),
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.on_ui_selection.assert_called_once_with(f2)
    scene.ui.open_fleet_context_menu.assert_called_once()
    assert scene.ui.open_fleet_context_menu.call_args.args[0] is f2
    scene._fleet_ops.handle_move_designation.assert_not_called()


# ---------------------------------------------------------------------------
# T16 — Right-click on enemy fleet (with fleet selected): silent no-op (#29).
# ---------------------------------------------------------------------------


def test_T16_rmb_on_enemy_fleet_is_silent_no_op():
    """Issue #29: empty/enemy-only hex with a fleet selected does NOT issue
    a Quick-Move. The legacy arm was removed in favour of the M-key path."""
    f1 = _fleet(fleet_id=1, owner_id=1, location=HexCoord(5, 5))
    enemy = _fleet(fleet_id=99, owner_id=2, location=HexCoord(0, 0))
    scene = _scene(
        selected_fleet=f1,
        empires=[_empire(1, [f1]), _empire(2, [enemy])],
        hex_at=HexCoord(0, 0),
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.ui.open_fleet_context_menu.assert_not_called()
    scene._fleet_ops.handle_move_designation.assert_not_called()


# ---------------------------------------------------------------------------
# T17 — Right-click on empty hex with fleet selected: silent no-op (#29).
# ---------------------------------------------------------------------------


def test_T17_rmb_on_empty_hex_is_silent_no_op():
    """Issue #29: empty hex with a fleet selected does NOT issue a Quick-Move
    and does NOT open a menu. Move orders go through M -> LMB or the fleet
    context menu's Move row."""
    f1 = _fleet(fleet_id=1, owner_id=1, location=HexCoord(5, 5))
    scene = _scene(
        selected_fleet=f1,
        empires=[_empire(1, [f1])],
        hex_at=HexCoord(0, 0),
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.ui.open_fleet_context_menu.assert_not_called()
    scene._fleet_ops.handle_move_designation.assert_not_called()


# ---------------------------------------------------------------------------
# T18 — No selection; right-click on friendly fleet selects + opens menu
# ---------------------------------------------------------------------------


def test_T18_rmb_no_selection_on_friendly_fleet_selects_and_opens_menu():
    f2 = _fleet(fleet_id=2, owner_id=1, location=HexCoord(0, 0))
    scene = _scene(
        selected_fleet=None,
        empires=[_empire(1, [f2])],
        hex_at=HexCoord(0, 0),
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.on_ui_selection.assert_called_once_with(f2)
    scene.ui.open_fleet_context_menu.assert_called_once()


# ---------------------------------------------------------------------------
# T19 — No selection; right-click on empty hex does nothing
# ---------------------------------------------------------------------------


def test_T19_rmb_no_selection_on_empty_hex_does_nothing():
    scene = _scene(
        selected_fleet=None,
        empires=[],
        hex_at=HexCoord(0, 0),
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.ui.open_fleet_context_menu.assert_not_called()
    scene._fleet_ops.handle_move_designation.assert_not_called()
