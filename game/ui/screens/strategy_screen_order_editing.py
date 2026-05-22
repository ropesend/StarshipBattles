"""Strategy screen order-editing helper (PROJ-330).

Extracted from ``strategy_screen.py`` as part of the LOC decomposition.
This module owns EDIT_MOVE / EDIT_TRANSFER state transitions for fleet
orders. The screen retains the three private attributes
(``_edit_move_ghost_hex``, ``_edit_move_order_index``, ``_edit_move_fleet``)
which the helper reads/writes directly.

The extraction is mechanical — there is no new MVVM seam.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from game.core.hex_math import HexCoord
from game.strategy.data.order_types import OrderType

if TYPE_CHECKING:
    from game.ui.screens.strategy_screen import StrategyScreen


def on_edit_order(screen: "StrategyScreen", entity, order_index, order) -> None:
    """Handle edit request for an order in the queue."""
    if order.type == OrderType.MOVE:
        start_edit_move(screen, entity, order_index, order)
    elif order.type in (
        OrderType.TRANSFER,
        OrderType.LOAD_POPULATION,
        OrderType.UNLOAD_POPULATION,
    ):
        start_edit_transfer(screen, entity, order_index, order)


def start_edit_move(screen: "StrategyScreen", fleet, order_index, order) -> None:
    """Enter EDIT_MOVE mode: pan to old destination, show ghost, wait for new click."""
    old_hex = order.target
    if not isinstance(old_hex, HexCoord):
        return

    # BUG-125: gate against active empire — opponent fleets are
    # informational only (read-only via on_ui_selection's gate).
    # PROJ-475: id-compare via the scene's active_empire_id accessor.
    active_id = screen.active_empire_id
    if active_id is not None and fleet.owner_id != active_id:
        return

    screen._edit_move_ghost_hex = old_hex
    screen._edit_move_order_index = order_index
    screen._edit_move_fleet = fleet
    screen.selected_fleet = fleet

    # Pan camera to the old destination so the user can see the ghost
    screen._camera_nav.center_on_hex(old_hex)
    screen.input_mode = "EDIT_MOVE"


def complete_edit_move(screen: "StrategyScreen", new_hex) -> None:
    """Finalize MOVE order edit: update the order target in-place."""
    fleet = screen._edit_move_fleet
    idx = screen._edit_move_order_index
    if fleet and idx is not None and 0 <= idx < len(fleet.orders):
        order = fleet.orders[idx]
        order.target = new_hex
        # Invalidate path if editing the active (first) order.
        # PROJ-370 Phase 2: route through IFleetMutator.
        if idx == 0:
            screen.session.fleet_mutator.set_path(fleet, [])
    # Clear edit state
    screen._edit_move_ghost_hex = None
    screen._edit_move_order_index = None
    screen._edit_move_fleet = None
    screen.input_mode = "SELECT"
    # Refresh the orders window
    if hasattr(screen.ui, "window_manager") and screen.ui.window_manager.fleet_orders_window:
        screen.ui.window_manager.fleet_orders_window.rebuild_list()
    screen.on_ui_selection(fleet)


def start_edit_transfer(screen: "StrategyScreen", fleet, order_index, order) -> None:
    """Re-open transfer dialog pre-populated with current order amounts."""
    # Walk orders up to this index to find the last MOVE/WARP destination
    transfer_hex = fleet.location
    for i in range(order_index):
        prev = fleet.orders[i]
        if prev.type == OrderType.MOVE and isinstance(prev.target, HexCoord):
            transfer_hex = prev.target
        elif prev.type == OrderType.WARP and isinstance(prev.target, HexCoord):
            transfer_hex = prev.target

    # Delete the old order, then open transfer dialog at the resolved hex.
    # PROJ-370 Phase 2: route through IFleetMutator.
    if 0 <= order_index < len(fleet.orders):
        screen.session.fleet_mutator.pop_order(fleet, index=order_index)
    screen.ui.open_transfer_dialog(fleet, transfer_hex)
