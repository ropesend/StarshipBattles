"""Tests for `ShipStatsAggregator` (PROJ-269 Phase 5 Task 5.2).

Tracks per-ship in-battle stats:
- `total_damage_taken`: sum of `CombatEvent.damage_amount` across all
  damage events where `target_ship == ship`
- `peak_speed`: highest speed observed via per-tick sampling
- `ticks_derelict`: count of ticks the ship spent in `is_derelict=True` state
- `ticks_alive`: count of ticks the ship spent alive (pre-destruction)

Wire at NORMAL+ telemetry only. `ShipStatsAggregator` subscribes to
damage events on the CombatEventBus and exposes a `sample_tick(engine)`
method that the runner calls each tick.
"""
from types import SimpleNamespace

import pytest

from game.core.math import Vector2
from game.simulation.battle_outcome import ShipStats
from game.simulation.combat.combat_events import (
    CombatEvent,
    CombatEventBus,
    CombatEventType,
    EventDetailLevel,
)
from game.simulation.combat.telemetry import ShipStatsAggregator


def _mk_ship(instance_id: str, is_alive: bool = True, is_derelict: bool = False,
             velocity: Vector2 = Vector2(0, 0)):
    return SimpleNamespace(
        instance_id=instance_id,
        is_alive=is_alive,
        is_derelict=is_derelict,
        velocity=velocity,
    )


# ---------------------------------------------------------------------------
# total_damage_taken via damage events
# ---------------------------------------------------------------------------


def test_aggregator_tracks_total_damage_taken():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    agg = ShipStatsAggregator(bus)

    ship = _mk_ship("s1")
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=ship,
        damage_amount=25.0,
    ))
    bus.emit(CombatEvent(
        event_type=CombatEventType.SHIELD_HIT,
        target_ship=ship,
        damage_amount=10.0,
    ))

    stats = agg.get_stats("s1")
    assert stats.total_damage_taken == pytest.approx(35.0)


def test_aggregator_tracks_damage_per_ship():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    agg = ShipStatsAggregator(bus)

    ship_a = _mk_ship("a")
    ship_b = _mk_ship("b")
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=ship_a,
        damage_amount=30.0,
    ))
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=ship_b,
        damage_amount=50.0,
    ))

    assert agg.get_stats("a").total_damage_taken == pytest.approx(30.0)
    assert agg.get_stats("b").total_damage_taken == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# peak_speed via sample_tick
# ---------------------------------------------------------------------------


def test_aggregator_tracks_peak_speed_via_sampling():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    agg = ShipStatsAggregator(bus)

    ship = _mk_ship("s1", velocity=Vector2(10.0, 0.0))

    class _FakeEngine:
        def __init__(self, ships):
            self.ships = ships

    engine = _FakeEngine([ship])

    agg.sample_tick(engine)
    ship.velocity = Vector2(50.0, 0.0)
    agg.sample_tick(engine)
    ship.velocity = Vector2(20.0, 0.0)
    agg.sample_tick(engine)

    stats = agg.get_stats("s1")
    assert stats.peak_speed == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# ticks_alive + ticks_derelict via sample_tick
# ---------------------------------------------------------------------------


def test_aggregator_tracks_ticks_alive_and_derelict():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    agg = ShipStatsAggregator(bus)

    ship = _mk_ship("s1", is_alive=True, is_derelict=False)

    class _FakeEngine:
        def __init__(self, ships):
            self.ships = ships

    engine = _FakeEngine([ship])

    # 3 ticks alive + not derelict
    for _ in range(3):
        agg.sample_tick(engine)

    # 2 ticks derelict
    ship.is_derelict = True
    for _ in range(2):
        agg.sample_tick(engine)

    stats = agg.get_stats("s1")
    assert stats.ticks_alive == 5  # total ticks the ship was alive
    assert stats.ticks_derelict == 2


# ---------------------------------------------------------------------------
# Defaults / no-data case
# ---------------------------------------------------------------------------


def test_aggregator_returns_zero_stats_for_unknown_ship():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    agg = ShipStatsAggregator(bus)
    stats = agg.get_stats("never_seen")
    assert isinstance(stats, ShipStats)
    assert stats.total_damage_taken == 0.0
    assert stats.peak_speed == 0.0
    assert stats.ticks_alive == 0
    assert stats.ticks_derelict == 0


# ---------------------------------------------------------------------------
# Snapshot API
# ---------------------------------------------------------------------------


def test_aggregator_snapshot_returns_all_tracked_ships():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    agg = ShipStatsAggregator(bus)
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("a"),
        damage_amount=10.0,
    ))
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("b"),
        damage_amount=20.0,
    ))
    snap = agg.snapshot()
    assert "a" in snap
    assert "b" in snap
    assert snap["a"].total_damage_taken == pytest.approx(10.0)
