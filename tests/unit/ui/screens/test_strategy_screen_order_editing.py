"""Tests for ``strategy_screen_order_editing`` (PROJ-330)."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.order_types import OrderType
from game.ui.screens import strategy_screen_order_editing as order_edit


def _make_screen():
    screen = MagicMock()
    screen.session = MagicMock()
    screen.session.active_empire = MagicMock(id=0)
    # PROJ-475: BUG-125 gate reads screen.active_empire_id (off the
    # direct .session read).
    screen.active_empire_id = 0
    screen._edit_move_ghost_hex = None
    screen._edit_move_order_index = None
    screen._edit_move_fleet = None
    screen.selected_fleet = None
    screen.input_mode = "SELECT"
    screen._camera_nav = MagicMock()
    screen.ui = MagicMock()
    screen.ui.window_manager = MagicMock()
    screen.ui.window_manager.fleet_orders_window = MagicMock()

    # PROJ-370 Phase 5: order edit routes through session.fleet_mutator;
    # configure pop_order / set_path to actually mutate the mock fleet.
    def _pop_order(fleet, index=0):
        return fleet.orders.pop(index)

    def _set_path(fleet, new_path):
        fleet.path = new_path

    screen.session.fleet_mutator.pop_order.side_effect = _pop_order
    screen.session.fleet_mutator.set_path.side_effect = _set_path
    return screen


def _fleet(owner_id=0, location=None, orders=None):
    fleet = MagicMock()
    fleet.owner_id = owner_id
    fleet.location = location or HexCoord(0, 0)
    fleet.orders = orders if orders is not None else []
    fleet.path = [1, 2, 3]
    return fleet


def _order(otype, target):
    o = MagicMock()
    o.type = otype
    o.target = target
    return o


class TestOnEditOrder:
    def test_move_dispatches_to_start_edit_move(self):
        screen = _make_screen()
        fleet = _fleet()
        order = _order(OrderType.MOVE, HexCoord(5, 5))
        order_edit.on_edit_order(screen, fleet, 0, order)
        # input_mode set to EDIT_MOVE => start_edit_move ran
        assert screen.input_mode == "EDIT_MOVE"

    @pytest.mark.parametrize("otype", [
        OrderType.TRANSFER,
        OrderType.LOAD_POPULATION,
        OrderType.UNLOAD_POPULATION,
    ])
    def test_transfer_variants_dispatch_to_start_edit_transfer(self, otype):
        screen = _make_screen()
        fleet = _fleet(orders=[_order(otype, HexCoord(1, 1))])
        order = fleet.orders[0]
        order_edit.on_edit_order(screen, fleet, 0, order)
        screen.ui.open_transfer_dialog.assert_called_once()

    def test_unhandled_order_type_is_noop(self):
        screen = _make_screen()
        fleet = _fleet()
        order = _order(OrderType.COLONIZE, None)
        # Must not raise; nothing changes
        order_edit.on_edit_order(screen, fleet, 0, order)
        assert screen.input_mode == "SELECT"


class TestStartEditMove:
    def test_non_hexcoord_target_short_circuits(self):
        screen = _make_screen()
        fleet = _fleet()
        order = _order(OrderType.MOVE, "not-a-hex")
        order_edit.start_edit_move(screen, fleet, 0, order)
        assert screen.input_mode == "SELECT"
        assert screen._edit_move_fleet is None

    def test_opponent_fleet_blocked(self):
        screen = _make_screen()
        screen.active_empire_id = 0
        fleet = _fleet(owner_id=1)  # different owner
        order = _order(OrderType.MOVE, HexCoord(2, 2))
        order_edit.start_edit_move(screen, fleet, 0, order)
        assert screen._edit_move_fleet is None
        assert screen.input_mode == "SELECT"

    def test_records_state_and_pans_camera(self):
        screen = _make_screen()
        fleet = _fleet(owner_id=0)
        target = HexCoord(3, 4)
        order = _order(OrderType.MOVE, target)
        order_edit.start_edit_move(screen, fleet, 2, order)
        assert screen._edit_move_ghost_hex == target
        assert screen._edit_move_order_index == 2
        assert screen._edit_move_fleet is fleet
        assert screen.selected_fleet is fleet
        screen._camera_nav.center_on_hex.assert_called_once_with(target)
        assert screen.input_mode == "EDIT_MOVE"

    def test_active_empire_none_allows_edit(self):
        screen = _make_screen()
        screen.active_empire_id = None
        fleet = _fleet(owner_id=42)
        order = _order(OrderType.MOVE, HexCoord(0, 0))
        order_edit.start_edit_move(screen, fleet, 0, order)
        assert screen._edit_move_fleet is fleet


class TestCompleteEditMove:
    def test_updates_target_and_clears_state(self):
        screen = _make_screen()
        old_order = _order(OrderType.MOVE, HexCoord(0, 0))
        fleet = _fleet(orders=[old_order])
        screen._edit_move_fleet = fleet
        screen._edit_move_order_index = 0
        new_hex = HexCoord(7, 8)
        order_edit.complete_edit_move(screen, new_hex)
        assert old_order.target == new_hex
        assert fleet.path == []  # idx==0 invalidates path
        assert screen._edit_move_fleet is None
        assert screen._edit_move_order_index is None
        assert screen._edit_move_ghost_hex is None
        assert screen.input_mode == "SELECT"
        screen.ui.window_manager.fleet_orders_window.rebuild_list.assert_called_once()
        screen.on_ui_selection.assert_called_once_with(fleet)

    def test_non_first_order_does_not_invalidate_path(self):
        screen = _make_screen()
        orders = [
            _order(OrderType.MOVE, HexCoord(0, 0)),
            _order(OrderType.MOVE, HexCoord(1, 1)),
        ]
        fleet = _fleet(orders=orders)
        screen._edit_move_fleet = fleet
        screen._edit_move_order_index = 1
        order_edit.complete_edit_move(screen, HexCoord(9, 9))
        assert fleet.path == [1, 2, 3]
        assert orders[1].target == HexCoord(9, 9)

    def test_out_of_range_index_skips_target_update(self):
        screen = _make_screen()
        fleet = _fleet(orders=[])
        screen._edit_move_fleet = fleet
        screen._edit_move_order_index = 5
        order_edit.complete_edit_move(screen, HexCoord(1, 1))
        assert screen._edit_move_fleet is None  # state still cleared


class TestStartEditTransfer:
    def test_uses_fleet_location_when_no_prior_moves(self):
        screen = _make_screen()
        loc = HexCoord(0, 0)
        orders = [_order(OrderType.TRANSFER, None)]
        fleet = _fleet(location=loc, orders=orders)
        order_edit.start_edit_transfer(screen, fleet, 0, orders[0])
        # Order popped, dialog opened at fleet location
        assert len(fleet.orders) == 0
        screen.ui.open_transfer_dialog.assert_called_once_with(fleet, loc)

    def test_walks_prior_move_destinations(self):
        screen = _make_screen()
        m1 = _order(OrderType.MOVE, HexCoord(1, 1))
        m2 = _order(OrderType.MOVE, HexCoord(2, 2))
        t = _order(OrderType.TRANSFER, None)
        fleet = _fleet(location=HexCoord(0, 0), orders=[m1, m2, t])
        order_edit.start_edit_transfer(screen, fleet, 2, t)
        screen.ui.open_transfer_dialog.assert_called_once_with(fleet, HexCoord(2, 2))
        # Transfer order was popped
        assert len(fleet.orders) == 2

    def test_walks_warp_destinations(self):
        screen = _make_screen()
        warp = _order(OrderType.WARP, HexCoord(5, 5))
        t = _order(OrderType.TRANSFER, None)
        fleet = _fleet(orders=[warp, t])
        order_edit.start_edit_transfer(screen, fleet, 1, t)
        screen.ui.open_transfer_dialog.assert_called_once_with(fleet, HexCoord(5, 5))
