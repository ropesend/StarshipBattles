"""Right-click (button 3) tests for SELECT mode in
``ClickModeDispatcher._handle_select_mode_click``.

Contract — strict selection-only (QA 2026-05-16 Obs 4+6):

  * Right-click dispatches based on ``scene.selected_object``, NOT on the
    hex / object under the cursor.
  * Friendly planet selected → ``open_planet_context_menu``.
  * Friendly fleet selected  → ``open_fleet_context_menu``.
  * Nothing useful selected (none / enemy-owned) → silent no-op.
  * Right-click NEVER changes selection — ``on_ui_selection`` is not
    called by this branch.
  * The cursor position ``(mx, my)`` is forwarded to the menu opener for
    positioning only; it does not influence which menu opens.

History: the previous hit-test-driven model (#20 + QA-B-Round 3) had two
bugs in user testing:

  * Obs 4 — selected planet + friendly fleet co-located → fleet menu won
    (hit-test order).
  * Obs 6 — selected planet + no fleet present → no menu at all
    (``_friendly_planet_at_screen`` hit-test failed silently).

Both close under selection-only dispatch.
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
    # Distinguishing attributes for ``is_fleet`` TypeGuard: ``ships`` +
    # ``orders``. ``location`` / ``owner_id`` already present.
    return SimpleNamespace(
        id=fleet_id,
        owner_id=owner_id,
        location=location,
        ships=[],
        orders=[],
    )


def _planet(*, planet_id: int, owner_id: int) -> SimpleNamespace:
    # Distinguishing attributes for ``is_planet`` TypeGuard: ``planet_type``
    # + ``deposits``. Provide minimal stubs.
    return SimpleNamespace(
        id=planet_id,
        owner_id=owner_id,
        planet_type=SimpleNamespace(name="Terran"),
        deposits={},
    )


def _empire(owner_id: int, fleets: list[SimpleNamespace]) -> SimpleNamespace:
    return SimpleNamespace(owner_id=owner_id, fleets=fleets)


def _scene(
    *,
    selected_object: SimpleNamespace | None = None,
    selected_fleet: SimpleNamespace | None = None,
    empires: list[SimpleNamespace] | None = None,
    current_player_id: int = 1,
    hex_at: HexCoord = HexCoord(0, 0),
) -> SimpleNamespace:
    ui = MagicMock()
    fleet_ops = MagicMock()
    fleet_ops.handle_move_designation.return_value = None
    return SimpleNamespace(
        camera=_IdentityCamera(hex_at=hex_at),
        hex_size=10,
        empires=empires or [],
        galaxy=None,
        ui=ui,
        on_ui_selection=MagicMock(),
        selected_object=selected_object,
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
# T14 — Selected friendly fleet → fleet menu opens regardless of cursor hex
# ---------------------------------------------------------------------------


def test_T14_rmb_with_selected_friendly_fleet_opens_fleet_menu() -> None:
    f1 = _fleet(fleet_id=1, owner_id=1, location=HexCoord(0, 0))
    scene = _scene(
        selected_object=f1,
        selected_fleet=f1,
        empires=[_empire(1, [f1])],
        hex_at=HexCoord(99, 99),  # cursor far from f1; should not matter.
    )
    disp, _ = _dispatcher(scene)
    handled = disp.dispatch_click(50, 50, 3)
    assert handled is True
    scene.ui.open_fleet_context_menu.assert_called_once()
    assert scene.ui.open_fleet_context_menu.call_args.args[0] is f1
    scene.ui.open_planet_context_menu.assert_not_called()
    scene.on_ui_selection.assert_not_called()


# ---------------------------------------------------------------------------
# T15 — Selected friendly fleet wins even when cursor is on a DIFFERENT
# friendly fleet's hex. Right-click does NOT change selection.
# ---------------------------------------------------------------------------


def test_T15_rmb_does_not_reselect_to_other_friendly_fleet() -> None:
    f1 = _fleet(fleet_id=1, owner_id=1, location=HexCoord(5, 5))
    f2 = _fleet(fleet_id=2, owner_id=1, location=HexCoord(0, 0))
    scene = _scene(
        selected_object=f1,
        selected_fleet=f1,
        empires=[_empire(1, [f1, f2])],
        hex_at=HexCoord(0, 0),
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.on_ui_selection.assert_not_called()
    scene.ui.open_fleet_context_menu.assert_called_once()
    assert scene.ui.open_fleet_context_menu.call_args.args[0] is f1


# ---------------------------------------------------------------------------
# T16 — Cursor over an enemy fleet's hex with a friendly fleet selected:
# the selected friendly fleet still wins.
# ---------------------------------------------------------------------------


def test_T16_rmb_on_enemy_hex_with_friendly_selected_opens_selected_menu() -> None:
    f1 = _fleet(fleet_id=1, owner_id=1, location=HexCoord(5, 5))
    enemy = _fleet(fleet_id=99, owner_id=2, location=HexCoord(0, 0))
    scene = _scene(
        selected_object=f1,
        selected_fleet=f1,
        empires=[_empire(1, [f1]), _empire(2, [enemy])],
        hex_at=HexCoord(0, 0),
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.ui.open_fleet_context_menu.assert_called_once()
    assert scene.ui.open_fleet_context_menu.call_args.args[0] is f1
    scene._fleet_ops.handle_move_designation.assert_not_called()


# ---------------------------------------------------------------------------
# T17 — Cursor over empty hex with friendly fleet selected: menu opens
# for selected fleet (no quick-move side effect, no menu suppression).
# ---------------------------------------------------------------------------


def test_T17_rmb_on_empty_hex_with_friendly_selected_opens_selected_menu() -> None:
    f1 = _fleet(fleet_id=1, owner_id=1, location=HexCoord(5, 5))
    scene = _scene(
        selected_object=f1,
        selected_fleet=f1,
        empires=[_empire(1, [f1])],
        hex_at=HexCoord(99, 99),
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.ui.open_fleet_context_menu.assert_called_once()
    assert scene.ui.open_fleet_context_menu.call_args.args[0] is f1
    scene._fleet_ops.handle_move_designation.assert_not_called()


# ---------------------------------------------------------------------------
# T18 — No selection: RMB never opens a menu and never changes selection.
# (Was: hit-test-driven auto-select-on-RMB. Removed by Obs 4+6.)
# ---------------------------------------------------------------------------


def test_T18_rmb_with_no_selection_is_silent_no_op() -> None:
    f2 = _fleet(fleet_id=2, owner_id=1, location=HexCoord(0, 0))
    scene = _scene(
        selected_object=None,
        selected_fleet=None,
        empires=[_empire(1, [f2])],
        hex_at=HexCoord(0, 0),
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.on_ui_selection.assert_not_called()
    scene.ui.open_fleet_context_menu.assert_not_called()
    scene.ui.open_planet_context_menu.assert_not_called()


# ---------------------------------------------------------------------------
# T19 — No selection + empty hex: still silent.
# ---------------------------------------------------------------------------


def test_T19_rmb_with_no_selection_on_empty_hex_does_nothing() -> None:
    scene = _scene(
        selected_object=None,
        selected_fleet=None,
        empires=[],
        hex_at=HexCoord(0, 0),
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.ui.open_fleet_context_menu.assert_not_called()
    scene.ui.open_planet_context_menu.assert_not_called()
    scene._fleet_ops.handle_move_designation.assert_not_called()


# ---------------------------------------------------------------------------
# QA Obs 4 — Selected friendly planet wins over co-located friendly fleet
# ---------------------------------------------------------------------------


def test_obs4_rmb_with_planet_selected_opens_planet_menu_over_colocated_fleet() -> None:
    """The scenario the user reported: planet selected, friendly fleet at
    the same hex, right-click should open the *planet* menu, not the fleet
    menu."""
    p = _planet(planet_id=21, owner_id=1)
    fleet = _fleet(fleet_id=2, owner_id=1, location=HexCoord(0, 0))
    scene = _scene(
        selected_object=p,
        selected_fleet=None,
        empires=[_empire(1, [fleet])],
        hex_at=HexCoord(0, 0),
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.ui.open_planet_context_menu.assert_called_once()
    assert scene.ui.open_planet_context_menu.call_args.args[0] is p
    scene.ui.open_fleet_context_menu.assert_not_called()
    scene.on_ui_selection.assert_not_called()


# ---------------------------------------------------------------------------
# QA Obs 6 — Selected friendly planet with no fleet in the sector: menu
# still opens. The old _friendly_planet_at_screen hit-test was failing
# silently here; selection-driven dispatch removes that path entirely.
# ---------------------------------------------------------------------------


def test_obs6_rmb_with_planet_selected_no_fleet_present_opens_planet_menu() -> None:
    p = _planet(planet_id=21, owner_id=1)
    scene = _scene(
        selected_object=p,
        selected_fleet=None,
        empires=[],
        hex_at=HexCoord(99, 99),  # cursor far from any system; should not matter.
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.ui.open_planet_context_menu.assert_called_once()
    assert scene.ui.open_planet_context_menu.call_args.args[0] is p


# ---------------------------------------------------------------------------
# Foreign-owned selection: no menu (planet or fleet owned by another empire).
# ---------------------------------------------------------------------------


def test_rmb_with_enemy_planet_selected_is_silent_no_op() -> None:
    p_enemy = _planet(planet_id=21, owner_id=2)
    scene = _scene(
        selected_object=p_enemy,
        empires=[],
        current_player_id=1,
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.ui.open_planet_context_menu.assert_not_called()
    scene.ui.open_fleet_context_menu.assert_not_called()


def test_rmb_with_enemy_fleet_selected_is_silent_no_op() -> None:
    enemy = _fleet(fleet_id=99, owner_id=2, location=HexCoord(0, 0))
    scene = _scene(
        selected_object=enemy,
        empires=[_empire(2, [enemy])],
        current_player_id=1,
    )
    disp, _ = _dispatcher(scene)
    disp.dispatch_click(50, 50, 3)
    scene.ui.open_fleet_context_menu.assert_not_called()
    scene.ui.open_planet_context_menu.assert_not_called()
