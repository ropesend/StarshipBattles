"""Direct tests for Fleet order-removal helpers."""

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.fleet_pursuer_tracker import PURSUIT_ORDER_TYPES
from game.strategy.data.order_types import Order, OrderType


def test_remove_orders_by_type_and_target_removes_only_matching_orders() -> None:
    pursuer = Fleet(1, 0, HexCoord(0, 0))
    target = Fleet(2, 0, HexCoord(5, 0))
    other_target = Fleet(3, 0, HexCoord(10, 0))
    move = Order(OrderType.MOVE, HexCoord(1, 0))
    matching_move = Order(OrderType.MOVE_TO_FLEET, target)
    matching_join = Order(OrderType.JOIN_FLEET, target)
    other_join = Order(OrderType.JOIN_FLEET, other_target)
    pursuer.orders = [move, matching_move, matching_join, other_join]

    removed = pursuer.remove_orders_by_type_and_target(PURSUIT_ORDER_TYPES, target)

    assert removed == [matching_move, matching_join]
    assert pursuer.orders == [move, other_join]


def test_remove_orders_by_type_and_target_unregisters_when_no_targeting_orders_remain() -> None:
    pursuer = Fleet(1, 0, HexCoord(0, 0))
    target = Fleet(2, 0, HexCoord(5, 0))
    pursuer.orders = [
        Order(OrderType.MOVE_TO_FLEET, target),
        Order(OrderType.JOIN_FLEET, target),
    ]
    target.pursuer_tracker.add_pursuer(pursuer)

    pursuer.remove_orders_by_type_and_target(PURSUIT_ORDER_TYPES, target)

    assert target.pursuer_tracker.pursuer_count == 0


def test_remove_orders_by_type_and_target_keeps_registration_for_remaining_target_order() -> None:
    pursuer = Fleet(1, 0, HexCoord(0, 0))
    target = Fleet(2, 0, HexCoord(5, 0))
    pursuer.orders = [
        Order(OrderType.MOVE_TO_FLEET, target),
        Order(OrderType.JOIN_FLEET, target),
    ]
    target.pursuer_tracker.add_pursuer(pursuer)

    pursuer.remove_orders_by_type_and_target(
        frozenset({OrderType.MOVE_TO_FLEET}),
        target,
    )

    assert [order.type for order in pursuer.orders] == [OrderType.JOIN_FLEET]
    assert target.pursuer_tracker.pursuer_count == 1


def test_remove_orders_by_type_and_target_clears_path_when_active_order_removed() -> None:
    pursuer = Fleet(1, 0, HexCoord(0, 0))
    target = Fleet(2, 0, HexCoord(5, 0))
    pursuer.orders = [
        Order(OrderType.MOVE_TO_FLEET, target),
        Order(OrderType.MOVE, HexCoord(1, 0)),
    ]
    pursuer.path = [HexCoord(0, 0), HexCoord(5, 0)]

    pursuer.remove_orders_by_type_and_target(PURSUIT_ORDER_TYPES, target)

    assert pursuer.path == []
