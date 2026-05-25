"""Regression guard: post-merge speed recalculation (PROJ-320).

The PROJ-320 round-budget model depends on each fleet having an accurate
speed at all times — the trigger predicate uses
`get_tick_interval(fleet.speed)` to decide when a fleet's
movement-opportunity ticks fall. If a merged fleet's speed is stale,
the cadence of its rounds is wrong.

The PROJ-320 risk-assessor agent flagged a SUSPECTED pre-existing bug:
that `OrderProcessor._execute_fleet_merge` did not recalculate the
target fleet's speed after merging in the source fleet's ships.

**This bug does not exist.** Verified by reading
`game/strategy/data/fleet.py::Fleet.merge_with` — line 522 calls
`other_fleet.trigger_speed_recalculation()` after transferring ships,
which dispatches to
`FleetSpeedCalculator.update_fleet_speed(self)`.

PROJ-491 Task 1.8: switched from patching ``trigger_speed_recalculation``
to verify the **observable** outcome — after merging, the target fleet's
``speed`` attribute equals ``min(participating ship speeds)``. The recalc
is therefore exercised end-to-end rather than asserted via mock call count.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from game.strategy.data.order_types import OrderType
from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
from tests.fixtures.strategy_entities import create_test_empire, create_test_fleet


def _make_ship_with_calculated_speed(speed: int):
    """Build a ship-like MagicMock that ``FleetSpeedCalculator`` will read
    a deterministic speed off of via ``calculate_ship_speed``.

    The calculator routes through ``calculate_ship_speed`` for each ship
    in ``calculate_fleet_speed``; patching that single method at the class
    level lets us drive per-ship speeds without setting up
    ``get_calculated_stats`` mass / strategic_movement combos.
    """
    ship = MagicMock()
    ship.is_combat_capable.return_value = True
    ship._test_speed = speed
    return ship


def test_fleet_merge_recalculates_target_speed_to_slowest_ship():
    """``Fleet.merge_with(other)`` produces a target fleet whose ``speed``
    equals the slowest combat-capable ship across the merged composition.

    Set up two fleets each carrying one ship with a known per-ship speed,
    merge them, and assert ``target.speed == min(speeds)``. This is the
    observable invariant the recalc protects.
    """
    target = create_test_fleet(fleet_id=1, num_ships=0, owner_id=0, speed=5.0)
    source = create_test_fleet(fleet_id=2, num_ships=0, owner_id=0, speed=3.0)

    fast_ship = _make_ship_with_calculated_speed(7)
    slow_ship = _make_ship_with_calculated_speed(2)
    target.ships.append(fast_ship)
    source.ships.append(slow_ship)

    def _per_ship_speed(ship):
        return ship._test_speed

    with patch.object(
        FleetSpeedCalculator, "calculate_ship_speed", side_effect=_per_ship_speed
    ):
        source.merge_with(target)

    assert target.speed == 2.0, (
        f"After merging a speed-2 ship into a fleet with a speed-7 ship, "
        f"target.speed must equal min(2, 7) == 2.0; got {target.speed}."
    )


def test_order_processor_merge_path_recalculates_target_speed():
    """End-to-end check via ``OrderProcessor._execute_fleet_merge``.

    Same min-speed invariant as the direct ``Fleet.merge_with`` test, but
    driven through the OrderProcessor wrapper to confirm no future
    refactor can short-circuit the recalc by inlining the ship transfer.
    """
    from game.strategy.engine.order_processor import OrderProcessor

    target = create_test_fleet(fleet_id=10, num_ships=0, owner_id=0, speed=5.0)
    source = create_test_fleet(fleet_id=11, num_ships=0, owner_id=0, speed=3.0)

    fast_ship = _make_ship_with_calculated_speed(8)
    slow_ship = _make_ship_with_calculated_speed(4)
    target.ships.append(fast_ship)
    source.ships.append(slow_ship)

    empire = MagicMock()
    empire.id = 0
    empire.fleets = [target, source]

    processor = OrderProcessor()
    handler = processor._handler_registry.get(OrderType.JOIN_FLEET)

    def _per_ship_speed(ship):
        return ship._test_speed

    with patch.object(
        FleetSpeedCalculator, "calculate_ship_speed", side_effect=_per_ship_speed
    ):
        handler._execute_fleet_merge(source, target, empire)

    assert target.speed == 4.0, (
        f"After OrderProcessor merge of a speed-4 ship into a speed-8 fleet, "
        f"target.speed must equal min(4, 8) == 4.0; got {target.speed}."
    )
