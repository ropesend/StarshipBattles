"""PROJ-333 Phase 1: OrderProcessor instant-orders (BUG-122) characterization.

Pins the three-phase JOIN_FLEET tick processor: validation,
co-located candidate collection, mutual-pair canonicalization
(most-ships winner with smaller-id tiebreak), Phase C aliveness
re-validation (`absorbed_by_other_merge` and
`target_absorbed_mid_iteration`), and event payloads. Also pins
single-fleet `process_join_fleet` pop-on-invalid behaviors.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from game.core.exceptions import ValidationException
from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.order_processor import OrderProcessor
from game.strategy.events.event_types import EventType


# ---------------------------------------------------------------------------
# Helpers — real Fleet + Empire substitutes
# ---------------------------------------------------------------------------


def _real_fleet(fleet_id: int, ship_count: int = 1, location=HexCoord(0, 0)) -> Fleet:
    """Real Fleet so isinstance(target, Fleet) and other type checks pass."""
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
# Validation
# ---------------------------------------------------------------------------


def test_process_instant_orders_validates_orders_not_none():
    """fleet.orders is None → ValidationException before any processing."""
    proc = OrderProcessor()
    bad = MagicMock(spec=Fleet)
    bad.id = 1
    bad.orders = None

    empire = MagicMock()
    empire.id = 0
    empire.fleets = [bad]

    with pytest.raises(ValidationException):
        proc.process_instant_orders([empire])


# ---------------------------------------------------------------------------
# Phase A: candidate collection — co-location filter
# ---------------------------------------------------------------------------


def test_process_instant_orders_collects_only_co_located_join_fleet_candidates():
    """Non-co-located JOIN_FLEET candidates are silently skipped (no pop)."""
    proc = OrderProcessor()
    src = _real_fleet(fleet_id=1, location=HexCoord(0, 0))
    target = _real_fleet(fleet_id=2, location=HexCoord(5, 5))  # different hex

    src.orders = [Order(OrderType.JOIN_FLEET, target)]
    target.orders = []

    empire = _empire_with([src, target])

    result = proc.process_instant_orders([empire])

    # No merge occurred, source still in empire, order NOT popped.
    assert result == []
    assert src in empire.fleets
    assert len(src.orders) == 1
    assert src.orders[0].type == OrderType.JOIN_FLEET
    assert src.orders[0].target is target


# ---------------------------------------------------------------------------
# Phase B: canonical merge election
# ---------------------------------------------------------------------------


def test_elect_canonical_merges_picks_more_ships_in_mutual_pair():
    """In a mutual A↔B pair, the larger fleet absorbs the smaller."""
    proc = OrderProcessor()
    big = _real_fleet(fleet_id=1, ship_count=5)
    small = _real_fleet(fleet_id=2, ship_count=1)
    empire = _empire_with([big, small])

    candidates = [(empire, big, small), (empire, small, big)]
    result = proc._elect_canonical_merges(candidates)

    assert len(result) == 1
    _, loser, winner = result[0]
    assert winner is big
    assert loser is small


def test_elect_canonical_merges_uses_smaller_id_tiebreak_on_equal_ships():
    """Tie on ship count: smaller-id fleet wins (deterministic for tests)."""
    proc = OrderProcessor()
    a = _real_fleet(fleet_id=1, ship_count=3)
    b = _real_fleet(fleet_id=2, ship_count=3)
    empire = _empire_with([a, b])

    candidates = [(empire, a, b), (empire, b, a)]
    result = proc._elect_canonical_merges(candidates)

    assert len(result) == 1
    _, loser, winner = result[0]
    assert winner is a  # smaller id wins
    assert loser is b


# ---------------------------------------------------------------------------
# Phase C: aliveness re-validation
# ---------------------------------------------------------------------------


def test_phase_c_skips_when_source_no_longer_in_empire_emits_absorbed_by_other_merge():
    """Source absorbed earlier this tick → emit `absorbed_by_other_merge`, skip."""
    bus, captured = _captured()
    proc = OrderProcessor(event_bus=bus)
    src = _real_fleet(fleet_id=1)
    tgt = _real_fleet(fleet_id=2)
    empire = _empire_with([tgt])  # src not in empire

    src.orders = [Order(OrderType.JOIN_FLEET, tgt)]
    tgt.orders = []
    # Force them co-located so candidate collection includes the entry…
    src.location = tgt.location

    # Inject the candidate manually by patching _elect_canonical_merges:
    with patch.object(
        proc, "_elect_canonical_merges",
        return_value=[(empire, src, tgt)],
    ):
        # Make the validate path see src.orders so we don't trip on None.
        empire.fleets.append(src)  # so Phase A collection works
        # but then remove src to simulate prior absorption…
        # Actually, the simpler approach: set candidates directly via patching.
        empire.fleets.remove(src)
        result = proc.process_instant_orders([empire])

    cancelled = [e for e in captured if e[0] == EventType.FLEET_JOIN_CANCELLED]
    assert any(e[1]["reason"] == "absorbed_by_other_merge" for e in cancelled)
    assert result == []


def test_phase_c_skips_when_target_absorbed_mid_iteration_pops_stale_order():
    """Target gone mid-iteration → emit `target_absorbed_mid_iteration` + pop."""
    bus, captured = _captured()
    proc = OrderProcessor(event_bus=bus)

    src = _real_fleet(fleet_id=1)
    tgt = _real_fleet(fleet_id=2)
    empire = _empire_with([src])  # tgt is NOT in empire (already absorbed)

    src.orders = [Order(OrderType.JOIN_FLEET, tgt)]
    tgt.orders = []

    with patch.object(
        proc, "_elect_canonical_merges",
        return_value=[(empire, src, tgt)],
    ):
        result = proc.process_instant_orders([empire])

    cancelled = [e for e in captured if e[0] == EventType.FLEET_JOIN_CANCELLED]
    assert any(
        e[1]["reason"] == "target_absorbed_mid_iteration" for e in cancelled
    )
    # Stale order popped.
    assert src.orders == []
    assert result == []


# ---------------------------------------------------------------------------
# _execute_fleet_merge: event emission
# ---------------------------------------------------------------------------


def test_execute_fleet_merge_logs_fleet_joined_event_with_ship_count():
    """Successful merge emits FLEET_JOINED with target ship_count after merge."""
    bus, captured = _captured()
    proc = OrderProcessor(event_bus=bus)
    src = _real_fleet(fleet_id=1, ship_count=2)
    tgt = _real_fleet(fleet_id=2, ship_count=3)
    empire = _empire_with([src, tgt])

    # Patch the speed-recalc that fires inside Fleet.merge_with — it
    # reads MagicMock ship stats and would TypeError. The merge
    # behavior under test (ship transfer + event emission) doesn't need
    # an actual speed recompute.
    with patch.object(type(tgt), "trigger_speed_recalculation"):
        proc._execute_fleet_merge(src, tgt, empire)

    joined = [e for e in captured if e[0] == EventType.FLEET_JOINED]
    assert len(joined) == 1
    payload = joined[0][1]
    assert payload["fleet_id"] == 1
    assert payload["target_fleet_id"] == 2
    # ship_count is read post-merge (target now has 5 ships)
    assert payload["ship_count"] == 5


# ---------------------------------------------------------------------------
# Single-fleet process_join_fleet: pop semantics
# ---------------------------------------------------------------------------


def test_process_join_fleet_pops_order_when_target_invalid_destroyed():
    """`order.target is None` (destroyed target) pops the order, cancelled=True."""
    proc = OrderProcessor()
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.location = HexCoord(0, 0)
    fleet.get_current_order.return_value = Order(OrderType.JOIN_FLEET, None)
    fleet.pop_order = MagicMock()

    result = proc.process_join_fleet(fleet, MagicMock(), MagicMock())

    assert result.merged is False
    assert result.cancelled is True
    fleet.pop_order.assert_called_once()


def test_process_join_fleet_pops_order_when_not_at_same_location():
    """Single-fleet path pops the order on 'Not at same location' (per design.md)."""
    proc = OrderProcessor()
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.location = HexCoord(0, 0)
    fleet.pop_order = MagicMock()

    target = MagicMock(spec=Fleet)
    target.id = 2
    target.location = HexCoord(5, 5)  # not co-located

    fleet.get_current_order.return_value = Order(OrderType.JOIN_FLEET, target)

    result = proc.process_join_fleet(fleet, MagicMock(), MagicMock())

    assert result.merged is False
    fleet.pop_order.assert_called_once()


# ---------------------------------------------------------------------------
# _emit_join_cancelled: no-op when no event bus
# ---------------------------------------------------------------------------


def test_emit_join_cancelled_no_op_when_event_bus_none():
    """Without an event bus the helper is a silent no-op (no AttributeError)."""
    proc = OrderProcessor(event_bus=None)
    src = _real_fleet(fleet_id=1)
    tgt = _real_fleet(fleet_id=2)
    empire = _empire_with([src, tgt])

    # Should simply return without raising.
    proc._emit_join_cancelled(src, tgt, empire, reason="anything")
