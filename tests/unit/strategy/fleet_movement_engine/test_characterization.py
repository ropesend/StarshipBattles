"""PROJ-333 Phase 1: FleetMovementEngine surface-gap characterization.

Pins design.md observations: speed-modifier `int(...)` truncation,
ACTION/BUILD-order skip in `collect_movements`, tick % interval
gating, warp blocked-no-capability vs blocked-no-resources,
warp-distance > 1 resource consumption, and the FEAT-28 swap-parity
filter (larger fleet drops, id tiebreak).
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.core.exceptions import ValidationException
from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import ACTION_ORDER_TYPES, Order, OrderType
from game.strategy.engine.fleet_movement_engine import FleetMovementEngine


# ---------------------------------------------------------------------------
# _validate_tick_inputs
# ---------------------------------------------------------------------------


def test_validate_tick_inputs_raises_when_fleet_location_is_none(mock_galaxy):
    """`fleet.location is None` raises ValidationException before movement."""
    bad_fleet = MagicMock(spec=Fleet)
    bad_fleet.id = 1
    bad_fleet.location = None
    empire = MagicMock()
    empire.id = 0
    empire.fleets = [bad_fleet]

    engine = FleetMovementEngine()
    with pytest.raises(ValidationException):
        engine.collect_movements([empire], mock_galaxy, tick=1)


# ---------------------------------------------------------------------------
# _get_effective_fleet_speed: galaxy + system fallbacks
# ---------------------------------------------------------------------------


def test_get_effective_speed_returns_base_when_no_get_system_at_location(mock_fleet):
    """Galaxy without `get_system_at_location` → base speed (no modifier)."""
    engine = FleetMovementEngine()
    mock_fleet.speed = 5
    galaxy_no_attr = object()  # no get_system_at_location
    assert engine._get_effective_fleet_speed(mock_fleet, galaxy_no_attr) == 5


def test_get_effective_speed_returns_base_when_no_system_at_hex(mock_fleet):
    """`get_system_at_location() → None` short-circuits to base speed."""
    engine = FleetMovementEngine()
    mock_fleet.speed = 5
    galaxy = MagicMock()
    galaxy.get_system_at_location.return_value = None
    assert engine._get_effective_fleet_speed(mock_fleet, galaxy) == 5


def test_get_effective_speed_returns_base_when_modifier_is_one(mock_fleet):
    """Aggregated multiplier == 1.0 short-circuits without int() truncation."""
    engine = FleetMovementEngine()
    mock_fleet.speed = 5
    galaxy = MagicMock()
    galaxy.get_system_at_location.return_value = MagicMock()

    with patch(
        "game.strategy.services.system_effects_collector.collect_sector_effects",
        return_value=[],
    ), patch(
        "game.strategy.services.system_effects_collector.aggregate_value_or",
        return_value=1.0,
    ):
        assert engine._get_effective_fleet_speed(mock_fleet, galaxy) == 5


def test_get_effective_speed_floors_via_int_truncation_after_multiplier(mock_fleet):
    """Speed 1 × 0.6 = 0.6 → int() → 0 (immobile). Pinned per design.md."""
    engine = FleetMovementEngine()
    mock_fleet.speed = 1
    galaxy = MagicMock()
    galaxy.get_system_at_location.return_value = MagicMock()

    with patch(
        "game.strategy.services.system_effects_collector.collect_sector_effects",
        return_value=[],
    ), patch(
        "game.strategy.services.system_effects_collector.aggregate_value_or",
        return_value=0.6,
    ):
        result = engine._get_effective_fleet_speed(mock_fleet, galaxy)
    assert result == 0.0


# ---------------------------------------------------------------------------
# collect_movements skip rules
# ---------------------------------------------------------------------------


def test_collect_movements_skips_action_order_fleets(mock_fleet, mock_galaxy):
    """Fleets with an ACTION order (e.g. COLONIZE) are skipped during movement."""
    engine = FleetMovementEngine()
    mock_fleet.speed = 10.0
    # Pick any ACTION order type.
    action_type = next(iter(ACTION_ORDER_TYPES))
    order = Order(action_type, MagicMock())
    mock_fleet.get_current_order.return_value = order
    mock_fleet.orders = [order]
    mock_galaxy.get_system_at_location = lambda _loc: None

    empire = MagicMock()
    empire.id = 0
    empire.fleets = [mock_fleet]

    result = engine.collect_movements([empire], mock_galaxy, tick=1)
    assert result == []


def test_collect_movements_skips_build_order_fleets(mock_fleet, mock_galaxy):
    """Fleets with a BUILD order are stationary."""
    engine = FleetMovementEngine()
    mock_fleet.speed = 10.0
    order = Order(OrderType.BUILD, None)
    mock_fleet.get_current_order.return_value = order
    mock_fleet.orders = [order]
    mock_galaxy.get_system_at_location = lambda _loc: None

    empire = MagicMock()
    empire.id = 0
    empire.fleets = [mock_fleet]

    assert engine.collect_movements([empire], mock_galaxy, tick=1) == []


def test_collect_movements_uses_tick_modulo_interval(mock_fleet, mock_galaxy):
    """`tick % interval != 0` skips movement; interval comes from speed."""
    engine = FleetMovementEngine()
    # Speed 1 → interval 10 (per get_tick_interval). Tick 5 should be skipped.
    mock_fleet.speed = 1
    mock_fleet.get_current_order.return_value = None
    mock_fleet.orders = []
    mock_galaxy.get_system_at_location = lambda _loc: None

    empire = MagicMock()
    empire.id = 0
    empire.fleets = [mock_fleet]

    # Ticks where speed-1 interval=10 doesn't divide should yield no moves.
    assert engine.collect_movements([empire], mock_galaxy, tick=5) == []


# ---------------------------------------------------------------------------
# apply_movement: stranded / warp-blocked branches
# ---------------------------------------------------------------------------


def test_apply_movement_returns_stranded_when_no_movement_resources(mock_fleet, mock_galaxy):
    """No movement resources → stranded=True, clear_orders called."""
    engine = FleetMovementEngine()
    mock_fleet.resources.has_resources_for_movement.return_value = False
    result = engine.apply_movement(mock_fleet, HexCoord(5, 0), mock_galaxy)
    assert result.moved is False
    assert result.stranded is True
    mock_fleet.clear_orders.assert_called_once()


def test_apply_movement_warp_blocked_when_no_capability_pops_one_order(mock_fleet, mock_galaxy):
    """Warp distance > 1 with no warp capability → pop_order, warp_blocked=True."""
    engine = FleetMovementEngine()
    mock_fleet.location = HexCoord(0, 0)
    mock_fleet.capabilities.can_use_warp.return_value = False

    result = engine.apply_movement(mock_fleet, HexCoord(10, 0), mock_galaxy)

    assert result.moved is False
    assert result.warp_blocked is True
    mock_fleet.pop_order.assert_called_once()
    mock_fleet.clear_orders.assert_not_called()  # PROJ-207: pop, not clear


def test_warp_no_resources_returns_warp_blocked_false(mock_fleet, mock_galaxy):
    """design.md surprise #3: warp distance > 1 with the warp CAPABILITY
    present but insufficient WARP RESOURCES returns
    `MovementResult(moved=False, warp_blocked=False)` — i.e. the
    `warp_blocked` flag is identical to the successful non-warp move
    case at the result level, even though one is a failure and the
    other is success. The only observable difference is that
    `pop_order` is called and `consume_warp_resources` is NOT.

    Pin the surprise so a future refactor that flips this flag (to
    distinguish the two cases at the result type) fails this test
    rather than silently changing call-site behavior.

    Pinned production at fleet_movement_engine.py:169-172.
    """
    engine = FleetMovementEngine()
    mock_fleet.location = HexCoord(0, 0)
    mock_fleet.capabilities.can_use_warp.return_value = True
    # Resources for general movement OK, but no warp resources.
    mock_fleet.resources.has_resources_for_movement.return_value = True
    mock_fleet.resources.has_resources_for_warp.return_value = False

    result = engine.apply_movement(mock_fleet, HexCoord(10, 0), mock_galaxy)

    # No move happened but warp_blocked is False (the surprising bit).
    assert result.moved is False
    assert result.warp_blocked is False
    # The fleet did pop its order (failure path side-effect).
    mock_fleet.pop_order.assert_called_once()
    # And critically did NOT consume warp resources.
    mock_fleet.resources.consume_warp_resources.assert_not_called()
    # And did NOT clear all orders (PROJ-207: pop, not clear).
    mock_fleet.clear_orders.assert_not_called()


def test_apply_movement_consumes_warp_resources_when_distance_gt_1(mock_fleet, mock_galaxy):
    """Successful warp jump (distance > 1) calls `consume_warp_resources`."""
    engine = FleetMovementEngine()
    mock_fleet.location = HexCoord(0, 0)
    mock_fleet.capabilities.can_use_warp.return_value = True
    mock_fleet.resources.has_resources_for_warp.return_value = True

    result = engine.apply_movement(mock_fleet, HexCoord(10, 0), mock_galaxy)

    assert result.moved is True
    mock_fleet.resources.consume_warp_resources.assert_called_once()
    mock_fleet.resources.consume_movement_resources.assert_called_once_with(1)


# ---------------------------------------------------------------------------
# _filter_jump_past_collisions: FEAT-28 swap parity
# ---------------------------------------------------------------------------


def test_filter_jump_past_drops_larger_fleet_on_swap_parity_with_id_tiebreak():
    """When fleets would swap hexes, larger fleet (or smaller id on tie) drops."""
    engine = FleetMovementEngine()

    # Use real Fleet objects so isinstance check inside the filter is satisfied.
    fleet_a = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    fleet_b = Fleet(fleet_id=2, owner_id=0, location=HexCoord(1, 0))

    # Both pursue each other.
    fleet_a.orders = [Order(OrderType.MOVE_TO_FLEET, fleet_b)]
    fleet_b.orders = [Order(OrderType.MOVE_TO_FLEET, fleet_a)]

    # Both have one ship each (tie on ship count) → smaller id (fleet_a) drops.
    fleet_a.ships = [MagicMock()]
    fleet_b.ships = [MagicMock()]

    move_queue = [(fleet_a, fleet_b.location), (fleet_b, fleet_a.location)]
    filtered = engine._filter_jump_past_collisions(move_queue)

    surviving_ids = {f.id for f, _ in filtered}
    assert surviving_ids == {2}  # fleet_a (id=1) was dropped on tiebreak


def test_filter_jump_past_drops_fleet_with_more_ships_on_swap_parity():
    """The larger fleet by ship count waits when mutual pursuit would swap hexes."""
    engine = FleetMovementEngine()
    fleet_a = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    fleet_b = Fleet(fleet_id=2, owner_id=0, location=HexCoord(1, 0))
    fleet_a.orders = [Order(OrderType.MOVE_TO_FLEET, fleet_b)]
    fleet_b.orders = [Order(OrderType.MOVE_TO_FLEET, fleet_a)]
    fleet_a.ships = [MagicMock(), MagicMock()]
    fleet_b.ships = [MagicMock()]

    filtered = engine._filter_jump_past_collisions([
        (fleet_a, fleet_b.location),
        (fleet_b, fleet_a.location),
    ])

    assert [(fleet.id, next_hex) for fleet, next_hex in filtered] == [
        (2, fleet_a.location)
    ]


def test_filter_jump_past_accepts_join_fleet_as_mutual_pursuit_trigger():
    """JOIN_FLEET remains eligible after navigation pops MOVE_TO_FLEET."""
    engine = FleetMovementEngine()
    fleet_a = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    fleet_b = Fleet(fleet_id=2, owner_id=0, location=HexCoord(1, 0))
    fleet_a.orders = [Order(OrderType.JOIN_FLEET, fleet_b)]
    fleet_b.orders = [Order(OrderType.JOIN_FLEET, fleet_a)]
    fleet_a.ships = [MagicMock()]
    fleet_b.ships = [MagicMock(), MagicMock()]

    filtered = engine._filter_jump_past_collisions([
        (fleet_a, fleet_b.location),
        (fleet_b, fleet_a.location),
    ])

    assert {fleet.id for fleet, _ in filtered} == {1}


def test_filter_jump_past_keeps_non_pursuit_swap_moves():
    """Swap-shaped movement is ignored when current orders are normal MOVE orders."""
    engine = FleetMovementEngine()
    fleet_a = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    fleet_b = Fleet(fleet_id=2, owner_id=0, location=HexCoord(1, 0))
    fleet_a.orders = [Order(OrderType.MOVE, fleet_b.location)]
    fleet_b.orders = [Order(OrderType.MOVE, fleet_a.location)]
    fleet_a.ships = [MagicMock(), MagicMock()]
    fleet_b.ships = [MagicMock()]
    move_queue = [(fleet_a, fleet_b.location), (fleet_b, fleet_a.location)]

    assert engine._filter_jump_past_collisions(move_queue) == move_queue


def test_filter_jump_past_keeps_pursuit_when_target_is_not_fleet_instance():
    """The Fleet isinstance guard leaves malformed pursuit targets untouched."""
    engine = FleetMovementEngine()
    fleet_a = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    fleet_b = Fleet(fleet_id=2, owner_id=0, location=HexCoord(1, 0))
    fleet_a.orders = [Order(OrderType.MOVE_TO_FLEET, MagicMock())]
    fleet_b.orders = [Order(OrderType.MOVE_TO_FLEET, fleet_a)]
    fleet_a.ships = [MagicMock(), MagicMock()]
    fleet_b.ships = [MagicMock()]
    move_queue = [(fleet_a, fleet_b.location), (fleet_b, fleet_a.location)]

    assert engine._filter_jump_past_collisions(move_queue) == move_queue
