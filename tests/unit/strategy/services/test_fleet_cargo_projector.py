"""Characterization tests for FleetCargoProjector (PROJ-336).

Pin current behavior of `FleetCargoProjector.get_projected_cargo`. No bug
fixes; observation entries are tracked in PROJ-336 decisions.md.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from game.strategy.data.order_types import Order, OrderType
from game.strategy.services.fleet_cargo_projector import FleetCargoProjector


def _make_cargo_projector_fleet(current: int, capacity: int, orders=None):
    """Build a minimal fleet stub that exposes only what the projector reads."""
    fleet = MagicMock()
    fleet.resources = MagicMock()
    fleet.resources.get_fleet_cargo_current = MagicMock(return_value=current)
    fleet.resources.get_fleet_cargo_capacity = MagicMock(return_value=capacity)
    fleet.orders = list(orders or [])
    return fleet


def _transfer(direction: str, amount: int, cargo_type: str = "passengers",
              order_type: OrderType = OrderType.TRANSFER) -> Order:
    return Order(
        order_type,
        target={"direction": direction, "amount": amount, "cargo_type": cargo_type},
    )


class TestEmptyAndPassthrough:
    def test_returns_current_when_order_queue_empty(self):
        fleet = _make_cargo_projector_fleet(current=42, capacity=100, orders=[])
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 42


class TestLoadDirection:
    def test_load_with_explicit_amount_adds_to_projected(self):
        fleet = _make_cargo_projector_fleet(current=10, capacity=100,
                            orders=[_transfer("load", 30)])
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 40

    def test_load_with_zero_amount_fills_to_capacity(self):
        fleet = _make_cargo_projector_fleet(current=20, capacity=100,
                            orders=[_transfer("load", 0)])
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 100

    def test_load_clamps_to_capacity_when_amount_exceeds_remaining(self):
        fleet = _make_cargo_projector_fleet(current=80, capacity=100,
                            orders=[_transfer("load", 9999)])
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 100


class TestUnloadDirection:
    def test_unload_with_explicit_amount_subtracts_from_projected(self):
        fleet = _make_cargo_projector_fleet(current=80, capacity=100,
                            orders=[_transfer("unload", 30)])
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 50

    def test_unload_with_zero_amount_drains_to_zero(self):
        fleet = _make_cargo_projector_fleet(current=80, capacity=100,
                            orders=[_transfer("unload", 0)])
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 0

    def test_unload_clamps_to_zero_when_amount_exceeds_projected(self):
        fleet = _make_cargo_projector_fleet(current=20, capacity=100,
                            orders=[_transfer("unload", 9999)])
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 0


class TestOrderFiltering:
    def test_skips_orders_whose_target_is_not_a_dict(self):
        # Fleet-target order (e.g. MOVE_TO_FLEET) — target isn't a dict.
        # Must NOT raise; must NOT alter projection.
        bad_order = Order(OrderType.TRANSFER, target=MagicMock())
        fleet = _make_cargo_projector_fleet(current=15, capacity=100, orders=[bad_order])
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 15

    def test_skips_orders_with_mismatching_cargo_type(self):
        fleet = _make_cargo_projector_fleet(current=10, capacity=100,
                            orders=[_transfer("load", 50, cargo_type="fuel")])
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 10

    def test_skips_orders_with_unrecognized_direction(self):
        fleet = _make_cargo_projector_fleet(current=10, capacity=100,
                            orders=[_transfer("sideways", 50)])
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 10

    def test_only_transfer_load_unload_population_order_types_are_processed(self):
        # MOVE order is ignored even if its target happens to look right.
        # Use MOVE with a dict target so dict-type isn't the filter reason.
        move_with_dict = Order(
            OrderType.MOVE,
            target={"direction": "load", "amount": 50, "cargo_type": "passengers"},
        )
        fleet = _make_cargo_projector_fleet(current=10, capacity=100, orders=[move_with_dict])
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 10


class TestComposition:
    def test_multiple_orders_for_same_cargo_type_compose_cumulatively(self):
        fleet = _make_cargo_projector_fleet(
            current=0, capacity=2000,
            orders=[_transfer("load", 1000), _transfer("unload", 400)],
        )
        # 0 + 1000 = 1000; 1000 - 400 = 600.
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 600

    def test_load_population_and_unload_population_order_types_processed(self):
        fleet = _make_cargo_projector_fleet(
            current=0, capacity=500,
            orders=[
                _transfer("load", 200, order_type=OrderType.LOAD_POPULATION),
                _transfer("unload", 50, order_type=OrderType.UNLOAD_POPULATION),
            ],
        )
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 150


class TestNegativeAmountIsolation:
    """MIN-001 fix from PROJ-336 review (req_20260504_213624_1361ce):
    pin actual production behavior on negative `amount` for transfer
    orders. Production at `fleet_cargo_projector.py:56,60` treats any
    non-positive amount as the auto-fill/auto-drain sentinel:
        load:   delta = amount if amount > 0 else (capacity - projected)
        unload: delta = amount if amount > 0 else projected
    So negative load FILLS to capacity (not reduces); negative unload
    DRAINS to zero (not adds). D-008 in the project's decisions.md
    documented this as 'negative load reduces projected', which was
    INCORRECT — these tests pin the actual behavior. (D-008 should be
    revised in a follow-up; the production behavior is what production
    does.)
    """

    def test_load_with_negative_amount_fills_to_capacity_like_zero(self):
        # Negative `amount` on load is treated as auto-fill (same as
        # amount=0). Production ignores the sign and the magnitude.
        fleet = _make_cargo_projector_fleet(
            current=100, capacity=2000,
            orders=[_transfer("load", -50)],
        )
        # delta = capacity - projected = 1900; projected = min(100+1900, 2000) = 2000.
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 2000

    def test_unload_with_negative_amount_drains_to_zero_like_zero(self):
        # Negative `amount` on unload is treated as auto-drain (same as
        # amount=0).
        fleet = _make_cargo_projector_fleet(
            current=100, capacity=2000,
            orders=[_transfer("unload", -500)],
        )
        # delta = projected = 100; projected = max(100-100, 0) = 0.
        assert FleetCargoProjector.get_projected_cargo(fleet, "passengers") == 0
