"""Unit tests for the per-fleet combat-trigger predicate (PROJ-320).

PROJ-320 reframes strategy combat scheduling: combat fires for a fleet at a
contested hex only on that fleet's movement-opportunity tick
(`tick % get_tick_interval(fleet.speed) == 0`), and only if the fleet did
NOT successfully leave the hex on that tick. These tests target the new
predicate `ConflictResolutionEngine._should_trigger_combat_for_fleet(...)`
that lands in Phase 4.

Until Phase 4, the predicate does not exist — every test in this file is
expected to fail at import time / AttributeError. That is the documented
red baseline (Phase 1 Task 1.5).

The five cases mirror the user-confirmed combat-trigger rules:

| # | Tick | Order | Moved this tick? | Combat fires? |
|---|------|-------|------------------|---------------|
| 1 | opportunity tick | none (idle) | no | YES |
| 2 | opportunity tick | COLONIZE (action) | no | YES |
| 3 | opportunity tick | MOVE (left hex) | YES | NO |
| 4 | non-opportunity | (any) | no | NO |
| 5 | opportunity tick | MOVE (path blocked) | no | YES |
"""
from __future__ import annotations

from unittest.mock import MagicMock

from game.core.hex_math import HexCoord
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.conflict_resolution_engine import (
    ConflictResolutionEngine,
)


# PROJ-479 Task 5.1 (DUP-001): _make_fleet moved to tests/conftest.py.
# Local wrapper preserves the `orders=None` kwarg semantic.
from tests.conftest import _make_mock_fleet as _make_mock_fleet_canonical  # noqa: E402


def _make_fleet(fleet_id: int, owner_id: int, location, speed: float, orders=None):
    """Local thin wrapper delegating to canonical conftest helper.
    Preserves the `orders=None → []` semantic this file used."""
    return _make_mock_fleet_canonical(
        fleet_id=fleet_id,
        owner_id=owner_id,
        location=location,
        speed=speed,
        orders=list(orders) if orders else [],
    )


def _make_engine() -> ConflictResolutionEngine:
    """Build a `ConflictResolutionEngine` with a MagicMock resolver."""
    resolver = MagicMock()
    return ConflictResolutionEngine(battle_resolver=resolver)


# Speed 5 → tick interval = 100 // 5 = 20.
# Opportunity ticks: 20, 40, 60, 80, 100.
SPEED_5_INTERVAL = 20


def test_opportunity_tick_with_no_orders_triggers_combat():
    """Idle fleet (no orders) at a contested hex on its opportunity tick:
    combat must fire. The fleet is "staying put" by inaction.
    """
    engine = _make_engine()
    fleet = _make_fleet(
        fleet_id=1, owner_id=0, location=HexCoord(0, 0), speed=5, orders=[]
    )

    # Empty `moved_fleet_ids` set: nobody moved this tick.
    assert engine._should_trigger_combat_for_fleet(
        fleet, tick=SPEED_5_INTERVAL, moved_fleet_ids=set()
    ) is True


def test_opportunity_tick_with_action_order_triggers_combat():
    """Fleet on an action order (e.g. COLONIZE) is staying put — combat fires.

    Per the PROJ-320 decision: action orders DO NOT shield from combat.
    A colonising fleet under enemy fire is still under fire.
    """
    engine = _make_engine()
    colonize = Order(order_type=OrderType.COLONIZE, target=HexCoord(0, 0))
    fleet = _make_fleet(
        fleet_id=1, owner_id=0, location=HexCoord(0, 0), speed=5,
        orders=[colonize],
    )

    assert engine._should_trigger_combat_for_fleet(
        fleet, tick=SPEED_5_INTERVAL, moved_fleet_ids=set()
    ) is True


def test_opportunity_tick_when_fleet_leaves_skips_combat():
    """Fleet that successfully moved out of the contested hex this tick:
    combat does NOT fire. The fleet exercised its movement option.
    """
    engine = _make_engine()
    fleet = _make_fleet(
        fleet_id=1, owner_id=0, location=HexCoord(1, 0), speed=5,
    )

    # Fleet 1 moved this tick — its id is in the moved set.
    assert engine._should_trigger_combat_for_fleet(
        fleet, tick=SPEED_5_INTERVAL, moved_fleet_ids={1}
    ) is False


def test_non_opportunity_tick_skips_combat():
    """Fleet on a tick that is NOT a multiple of its movement interval:
    combat does NOT fire. The fleet has no movement opportunity this tick.
    """
    engine = _make_engine()
    fleet = _make_fleet(
        fleet_id=1, owner_id=0, location=HexCoord(0, 0), speed=5,
    )

    # Tick 19 is not divisible by 20 (speed 5's interval).
    assert engine._should_trigger_combat_for_fleet(
        fleet, tick=SPEED_5_INTERVAL - 1, moved_fleet_ids=set()
    ) is False


def test_blocked_pathfind_still_triggers_combat():
    """Fleet had a MOVE order but pathfinding failed (or destination
    unreachable) — the fleet did not leave the hex. Same effect as 'idle':
    combat fires. The unifying rule is "did the fleet leave?", not
    "did the fleet have orders?".
    """
    engine = _make_engine()
    blocked_move = Order(order_type=OrderType.MOVE, target=HexCoord(99, 99))
    fleet = _make_fleet(
        fleet_id=1, owner_id=0, location=HexCoord(0, 0), speed=5,
        orders=[blocked_move],
    )

    # `moved_fleet_ids` does not contain fleet 1 because pathfinding
    # failed and Phase 3 didn't apply a movement.
    assert engine._should_trigger_combat_for_fleet(
        fleet, tick=SPEED_5_INTERVAL, moved_fleet_ids=set()
    ) is True
