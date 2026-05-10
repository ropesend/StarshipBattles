"""Tests for `HitLogRecorder` (PROJ-269 Phase 5 Task 5.3).

Subscribes to damage events and records one `HitRecord` per hit
against each ship, exposing `get_hits(instance_id) -> Tuple[HitRecord, ...]`
and `snapshot() -> Dict[instance_id, Tuple[HitRecord, ...]]`.
"""
from types import SimpleNamespace

import pytest

from game.core.combat_types import DamageContext
from game.simulation.battle_outcome import HitRecord
from game.simulation.combat.combat_events import (
    CombatEvent,
    CombatEventBus,
    CombatEventType,
    EventDetailLevel,
)
from game.simulation.combat.telemetry import HitLogRecorder


def _mk_ship(instance_id: str):
    return SimpleNamespace(instance_id=instance_id)


def _mk_attacker(instance_id: str, weapon_component_id: str = "laser_cannon"):
    return DamageContext(
        attacker=SimpleNamespace(instance_id=instance_id),
        source_weapon=SimpleNamespace(id=weapon_component_id),
        damage_type="beam",
    )


# ---------------------------------------------------------------------------
# COMPONENT_HIT events produce HitRecord entries
# ---------------------------------------------------------------------------


def test_recorder_captures_component_hit_events():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    rec = HitLogRecorder(bus)

    target = _mk_ship("target")
    attacker_ctx = _mk_attacker("attacker", "laser_cannon")

    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=target,
        damage_amount=42.0,
        context=attacker_ctx,
    ))

    hits = rec.get_hits("target")
    assert len(hits) == 1
    record = hits[0]
    assert isinstance(record, HitRecord)
    assert record.attacker_ship_id == "attacker"
    assert record.weapon_component_id == "laser_cannon"
    assert record.damage == pytest.approx(42.0)


def test_recorder_captures_multiple_hits():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    rec = HitLogRecorder(bus)

    target = _mk_ship("target")
    for i in range(5):
        bus.emit(CombatEvent(
            event_type=CombatEventType.COMPONENT_HIT,
            target_ship=target,
            damage_amount=float(i + 1),
            context=_mk_attacker("attacker"),
        ))

    hits = rec.get_hits("target")
    assert len(hits) == 5
    assert [h.damage for h in hits] == [1.0, 2.0, 3.0, 4.0, 5.0]


def test_recorder_separates_hits_per_target_ship():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    rec = HitLogRecorder(bus)

    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("a"),
        damage_amount=10.0,
        context=_mk_attacker("x"),
    ))
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("b"),
        damage_amount=20.0,
        context=_mk_attacker("y"),
    ))

    assert len(rec.get_hits("a")) == 1
    assert len(rec.get_hits("b")) == 1


def test_recorder_records_tick_number_from_event_when_available():
    """Engine emits events with a tick_number on the event if available;
    otherwise, defaults to 0."""
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    rec = HitLogRecorder(bus, tick_provider=lambda: 42)

    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("target"),
        damage_amount=10.0,
        context=_mk_attacker("attacker"),
    ))
    hits = rec.get_hits("target")
    assert hits[0].tick == 42


def test_recorder_also_captures_shield_hit():
    """SHIELD_HIT events should also produce HitRecord entries."""
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    rec = HitLogRecorder(bus)

    bus.emit(CombatEvent(
        event_type=CombatEventType.SHIELD_HIT,
        target_ship=_mk_ship("t"),
        damage_amount=15.0,
        context=_mk_attacker("a"),
    ))
    hits = rec.get_hits("t")
    assert len(hits) == 1
    assert hits[0].damage == pytest.approx(15.0)


def test_recorder_snapshot_returns_all_targets():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    rec = HitLogRecorder(bus)

    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("a"),
        damage_amount=1.0,
        context=_mk_attacker("x"),
    ))
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("b"),
        damage_amount=2.0,
        context=_mk_attacker("y"),
    ))

    snap = rec.snapshot()
    assert set(snap.keys()) == {"a", "b"}
    assert len(snap["a"]) == 1
    assert len(snap["b"]) == 1


def test_recorder_handles_missing_attacker_context():
    """Events with no attacker context shouldn't crash; the record
    carries empty-string defaults."""
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    rec = HitLogRecorder(bus)
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("t"),
        damage_amount=5.0,
        context=None,
    ))
    hits = rec.get_hits("t")
    assert len(hits) == 1
    assert hits[0].attacker_ship_id == ""
    assert hits[0].weapon_component_id == ""
