"""Per-handler tests for `JoinFleetHandler` (PROJ-368 Phase 1).

Drives the handler directly (no `OrderProcessor` indirection). Covers:
- `execute_action_order` happy + unhappy paths (lifted from
  `test_order_processor_fleet_merge.py` semantics)
- `process_instant_orders` BUG-122 three-phase pipeline
  (lifted from `test_order_processor_instant.py` semantics)
- Event-bus payload exact-match for `FLEET_JOINED` and
  `FLEET_JOIN_CANCELLED`.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.core.exceptions import ValidationException
from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.order_handlers.join_fleet import JoinFleetHandler
from game.strategy.events.event_types import EventType


# Shared test helpers (mirroring conftest patterns).
def _real_fleet(fleet_id: int, ship_count: int = 1, location=HexCoord(0, 0)) -> Fleet:
    f = Fleet(fleet_id=fleet_id, owner_id=0, location=location)
    f.ships = [MagicMock() for _ in range(ship_count)]
    return f


def _empire_with(fleets):
    e = MagicMock()
    e.id = 0
    e.fleets = list(fleets)
    e.remove_fleet = MagicMock(side_effect=lambda fl, **kw: e.fleets.remove(fl))
    return e


def _captured():
    captured: list = []

    class _Bus:
        def log_event(self, event_type, **kwargs):
            captured.append((event_type, kwargs))

    return _Bus(), captured


# ---------------------------------------------------------------------------
# execute_action_order — single-fleet path
# ---------------------------------------------------------------------------


def test_execute_action_order_no_order_returns_unmerged():
    handler = JoinFleetHandler()
    fleet = MagicMock(spec=Fleet)
    fleet.get_current_order.return_value = None
    result = handler.execute_action_order(fleet, MagicMock(), MagicMock())
    assert result.merged is False
    assert result.success is False


def test_execute_action_order_target_destroyed_pops_and_cancels():
    handler = JoinFleetHandler()
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.location = HexCoord(0, 0)
    fleet.get_current_order.return_value = Order(OrderType.JOIN_FLEET, None)
    fleet.pop_order = MagicMock()
    result = handler.execute_action_order(fleet, MagicMock(), MagicMock())
    assert result.merged is False
    assert result.cancelled is True
    fleet.pop_order.assert_called_once()


def test_execute_action_order_co_located_merges():
    bus, captured = _captured()
    handler = JoinFleetHandler(event_bus=bus)
    src = _real_fleet(fleet_id=1, ship_count=2)
    tgt = _real_fleet(fleet_id=2, ship_count=3)
    empire = _empire_with([src, tgt])
    src.orders = [Order(OrderType.JOIN_FLEET, tgt)]
    with patch.object(type(tgt), "trigger_speed_recalculation"):
        result = handler.execute_action_order(src, empire, MagicMock())
    assert result.merged is True
    assert result.success is True
    joined = [e for e in captured if e[0] == EventType.FLEET_JOINED]
    assert len(joined) == 1


def test_execute_action_order_not_co_located_pops_without_merge():
    handler = JoinFleetHandler()
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.location = HexCoord(0, 0)
    fleet.pop_order = MagicMock()
    target = MagicMock(spec=Fleet)
    target.id = 2
    target.location = HexCoord(5, 5)
    fleet.get_current_order.return_value = Order(OrderType.JOIN_FLEET, target)
    result = handler.execute_action_order(fleet, MagicMock(), MagicMock())
    assert result.merged is False
    fleet.pop_order.assert_called_once()


# ---------------------------------------------------------------------------
# process_instant_orders — BUG-122 pipeline
# ---------------------------------------------------------------------------


def test_process_instant_orders_validates_orders_not_none():
    handler = JoinFleetHandler()
    bad = MagicMock(spec=Fleet)
    bad.id = 1
    bad.orders = None
    empire = MagicMock()
    empire.id = 0
    empire.fleets = [bad]
    with pytest.raises(ValidationException):
        handler.process_instant_orders([empire])


def test_process_instant_orders_collects_co_located_candidates_only():
    handler = JoinFleetHandler()
    src = _real_fleet(fleet_id=1, location=HexCoord(0, 0))
    tgt = _real_fleet(fleet_id=2, location=HexCoord(5, 5))  # not co-located
    empire = _empire_with([src, tgt])
    src.orders = [Order(OrderType.JOIN_FLEET, tgt)]
    tgt.orders = []
    # No candidates — no merge, empty result.
    result = handler.process_instant_orders([empire])
    assert result == []


def test_process_instant_orders_mutual_pair_canonicalization_most_ships_wins():
    """BUG-122: when both fleets target each other, the larger one wins."""
    handler = JoinFleetHandler()
    big = _real_fleet(fleet_id=1, ship_count=5)
    small = _real_fleet(fleet_id=2, ship_count=2)
    empire = _empire_with([big, small])
    big.orders = [Order(OrderType.JOIN_FLEET, small)]
    small.orders = [Order(OrderType.JOIN_FLEET, big)]
    with patch.object(type(big), "trigger_speed_recalculation"), \
         patch.object(type(small), "trigger_speed_recalculation"):
        result = handler.process_instant_orders([empire])
    # Loser (small=2 ships) merges into winner (big=5 ships).
    assert len(result) == 1
    _, removed = result[0]
    assert removed is small
    assert big in empire.fleets
    assert small not in empire.fleets


def test_process_instant_orders_mutual_pair_tie_smaller_id_wins():
    """BUG-122: equal ship counts → smaller fleet id wins."""
    handler = JoinFleetHandler()
    a = _real_fleet(fleet_id=1, ship_count=2)
    b = _real_fleet(fleet_id=2, ship_count=2)
    empire = _empire_with([a, b])
    a.orders = [Order(OrderType.JOIN_FLEET, b)]
    b.orders = [Order(OrderType.JOIN_FLEET, a)]
    with patch.object(type(a), "trigger_speed_recalculation"), \
         patch.object(type(b), "trigger_speed_recalculation"):
        result = handler.process_instant_orders([empire])
    # Smaller id (a=1) wins; b is removed.
    assert len(result) == 1
    _, removed = result[0]
    assert removed is b


def test_process_instant_orders_phase_c_aliveness_skip_absorbed_source():
    """Source absorbed earlier this tick → emits `absorbed_by_other_merge`."""
    bus, captured = _captured()
    handler = JoinFleetHandler(event_bus=bus)
    src = _real_fleet(fleet_id=1)
    tgt = _real_fleet(fleet_id=2)
    empire = _empire_with([tgt])  # src not in empire
    src.orders = [Order(OrderType.JOIN_FLEET, tgt)]
    tgt.orders = []
    src.location = tgt.location

    # Inject a candidate that bypasses Phase A by patching the canonical step.
    with patch.object(
        handler, "_elect_canonical_merges",
        return_value=[(empire, src, tgt)],
    ):
        result = handler.process_instant_orders([empire])

    cancelled = [e for e in captured if e[0] == EventType.FLEET_JOIN_CANCELLED]
    assert any(e[1]["reason"] == "absorbed_by_other_merge" for e in cancelled)
    assert result == []


def test_process_instant_orders_phase_c_aliveness_skip_absorbed_target():
    """Target gone mid-iteration → emits `target_absorbed_mid_iteration` + pops stale order."""
    bus, captured = _captured()
    handler = JoinFleetHandler(event_bus=bus)
    src = _real_fleet(fleet_id=1)
    tgt = _real_fleet(fleet_id=2)
    empire = _empire_with([src])  # tgt is NOT in empire (already absorbed)
    src.orders = [Order(OrderType.JOIN_FLEET, tgt)]
    tgt.orders = []

    with patch.object(
        handler, "_elect_canonical_merges",
        return_value=[(empire, src, tgt)],
    ):
        result = handler.process_instant_orders([empire])

    cancelled = [e for e in captured if e[0] == EventType.FLEET_JOIN_CANCELLED]
    assert any(e[1]["reason"] == "target_absorbed_mid_iteration" for e in cancelled)
    assert src.orders == []
    assert result == []


def test_process_instant_orders_emits_fleet_joined_event_payload_exact_match():
    """FLEET_JOINED event payload — exact dict equality."""
    from game.strategy.events.event_types import EventCategory
    bus, captured = _captured()
    handler = JoinFleetHandler(event_bus=bus)
    src = _real_fleet(fleet_id=1, ship_count=2)
    tgt = _real_fleet(fleet_id=2, ship_count=3)
    empire = _empire_with([src, tgt])
    src.orders = [Order(OrderType.JOIN_FLEET, tgt)]
    tgt.orders = []

    with patch.object(type(tgt), "trigger_speed_recalculation"):
        handler.process_instant_orders([empire])

    joined = [e for e in captured if e[0] == EventType.FLEET_JOINED]
    assert len(joined) == 1
    payload = joined[0][1]
    # Exact-dict-equality on the structured fields.
    assert payload == {
        "category": EventCategory.FLEET_OPERATIONS,
        "empire_id": 0,
        "message": "Fleet 1 joined Fleet 2",
        "fleet_id": 1,
        "target_fleet_id": 2,
        "ship_count": 5,  # post-merge target size
    }


def test_process_instant_orders_emits_fleet_join_cancelled_with_reason_field():
    """FLEET_JOIN_CANCELLED carries a structured `reason` field (BUG-122)."""
    from game.strategy.events.event_types import EventCategory
    bus, captured = _captured()
    handler = JoinFleetHandler(event_bus=bus)
    src = _real_fleet(fleet_id=1)
    tgt = _real_fleet(fleet_id=2)
    empire = _empire_with([src])  # tgt not present
    src.orders = [Order(OrderType.JOIN_FLEET, tgt)]
    tgt.orders = []

    with patch.object(
        handler, "_elect_canonical_merges",
        return_value=[(empire, src, tgt)],
    ):
        handler.process_instant_orders([empire])

    cancelled = [e for e in captured if e[0] == EventType.FLEET_JOIN_CANCELLED]
    assert len(cancelled) == 1
    payload = cancelled[0][1]
    assert payload["reason"] == "target_absorbed_mid_iteration"
    assert payload["category"] == EventCategory.FLEET_OPERATIONS
    assert payload["fleet_id"] == 1
    assert payload["target_fleet_id"] == 2
    assert payload["empire_id"] == 0
