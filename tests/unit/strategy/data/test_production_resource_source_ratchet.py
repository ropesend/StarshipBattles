"""PROJ-451 Phase 4 ratchet: ``IProductionResourceSource`` implementers
must satisfy the affordability/consumption symmetry contract.

For each concrete implementer (Planet, Fleet, ...) and a range of
realistic cost shapes, the test asserts::

    if implementer.production_has_resources(costs):
        for resource_type, amount in costs.items():
            if amount > 0:
                assert implementer.production_consume_resource(
                    resource_type, amount,
                ) is True

This defends against future implementers introducing contract
breaches that the engine assertion (PROJ-451 Phase 3, option B)
would catch only at runtime.

The Protocol contract docstring at
``game/strategy/engine/production_engine.py:65-99`` is the source of
truth; this ratchet enforces it at the implementer layer.
"""
from __future__ import annotations

import pytest

from tests.fixtures.strategy_entities import (
    create_test_fleet,
    create_test_planet,
)


@pytest.fixture
def stocked_planet():
    """Planet with a generously-stocked private stockpile."""
    return create_test_planet(
        has_facilities=False,
        has_population=False,
        _stockpile={"metals": 100.0, "organics": 50.0, "fuel": 10.0},
    )


@pytest.fixture
def stocked_fleet():
    """Fleet with one ship carrying 100 metals + 50 organics."""
    fleet = create_test_fleet(num_ships=1)
    fleet.ships[0]._cargo_mgr.set_cargo("metals", 100)
    fleet.ships[0]._cargo_mgr.set_cargo("organics", 50)
    return fleet


PLANET_COSTS = [
    {"metals": 1.0},                      # integer-shaped float
    {"metals": 1.5},                      # fractional
    {"metals": 0.1},                      # tiny fractional
    {"metals": 50.0, "organics": 25.0},   # multi-resource
    {"metals": 0.0},                      # zero requested
    {"metals": 100.0},                    # exactly the available amount
]


FLEET_COSTS = [
    {"metals": 1.0},
    {"metals": 1.5},                      # int(round(1.5))=2 against cargo=100
    {"metals": 0.1},                      # int(round(0.1))=0 (rounds-to-zero)
    {"metals": 0.4},                      # int(round(0.4))=0
    {"metals": 0.6},                      # int(round(0.6))=1
    {"metals": 50.0, "organics": 25.0},
    {"metals": 0.0},
    {"metals": 100.0},
]


@pytest.mark.parametrize("costs", PLANET_COSTS)
def test_planet_consume_succeeds_when_affordability_passes(stocked_planet, costs):
    """Planet (float stockpile) — symmetric on float comparisons.

    ``Planet.consume_from_stockpile`` consumes the exact float
    ``amount``; the diff equals the requested amount. The ratchet
    holds trivially because no rounding step decouples the gate from
    the unload.
    """
    if not stocked_planet.production_has_resources(costs):
        return
    for resource_type, amount in costs.items():
        if amount > 0:
            assert stocked_planet.production_consume_resource(
                resource_type, amount,
            ) is True, (
                f"Planet contract breach: has_resources({costs!r}) returned "
                f"True but consume({resource_type!r}, {amount}) returned False"
            )


@pytest.mark.parametrize("costs", FLEET_COSTS)
def test_fleet_consume_succeeds_when_affordability_passes(stocked_fleet, costs):
    """Fleet (integer cargo store) — symmetric on int(round(...)) values.

    PROJ-451 Phase 2 Task 2.0 closed the data-layer half: both
    ``Fleet.has_cargo_resources`` and ``Fleet.consume_cargo_resource``
    round the requested ``amount`` to ``int(round(amount))`` before
    comparing against the integer cargo store. The ratchet holds for
    every cost shape including rounds-to-zero.
    """
    if not stocked_fleet.production_has_resources(costs):
        return
    for resource_type, amount in costs.items():
        if amount > 0:
            assert stocked_fleet.production_consume_resource(
                resource_type, amount,
            ) is True, (
                f"Fleet contract breach: has_resources({costs!r}) returned "
                f"True but consume({resource_type!r}, {amount}) returned False"
            )


class TestFleetFractionalCostRoundsToZeroSymmetry:
    """Pin the exact DI-2026-05-18-006 invariant after Phase 2 Task 2.0.

    Walks through rounds-to-zero, rounds-to-one, and exhausted-cargo
    cases. If a future change accidentally re-introduces the
    asymmetry, these assertions fire immediately.
    """

    def test_zero_one_and_below_round_to_zero(self):
        """cargo=1, fractional cost <=0.5 → has=True, consume=True, cargo unchanged."""
        fleet = create_test_fleet(num_ships=1)
        fleet.ships[0]._cargo_mgr.set_cargo("metals", 1)

        for fractional_amount in (0.1, 0.4, 0.5):
            assert fleet.has_cargo_resources({"metals": fractional_amount}) is True
            assert fleet.consume_cargo_resource("metals", fractional_amount) is True
            assert fleet.get_cargo_resource("metals") == 1.0

    def test_zero_point_six_rounds_to_one_and_actually_deducts(self):
        """cargo=1, amount=0.6 → has=True, consume=True, cargo drops to 0."""
        fleet = create_test_fleet(num_ships=1)
        fleet.ships[0]._cargo_mgr.set_cargo("metals", 1)

        assert fleet.has_cargo_resources({"metals": 0.6}) is True
        assert fleet.consume_cargo_resource("metals", 0.6) is True
        assert fleet.get_cargo_resource("metals") == 0.0

    def test_exhausted_cargo_still_accepts_rounds_to_zero_amounts(self):
        """cargo=0, amount<=0.5 → both methods agree both return True
        (rounded amount is 0; consuming 0 from 0 trivially succeeds).

        The engine-side ``_apply_resource_consumption`` (PROJ-451
        Phase 2 Task 2.1) detects ``actually_consumed == 0`` and emits
        ``RESOURCE_SHORTAGE`` so the queue stall is visible.
        """
        fleet = create_test_fleet(num_ships=1)
        fleet.ships[0]._cargo_mgr.set_cargo("metals", 0)

        assert fleet.has_cargo_resources({"metals": 0.1}) is True
        assert fleet.consume_cargo_resource("metals", 0.1) is True
        assert fleet.get_cargo_resource("metals") == 0.0
