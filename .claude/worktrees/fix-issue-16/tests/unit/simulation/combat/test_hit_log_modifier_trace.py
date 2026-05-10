"""Tests for `HitLogRecorder.modifiers_applied` population (PROJ-269 Phase 5.5 Task 5.5.3).

Covers:
- `HitLogRecorder(event_bus, modifier_stack=stack)` stores the stack
- Each recorded `HitRecord.modifiers_applied` contains `ModifierApplication`
  entries for global + per_team[attacker.team_id] entries in the stack
- Placeholder effects (stat_key="placeholder") are filtered out
- Per-team entries for OTHER teams do not appear
"""
from types import SimpleNamespace

import pytest

from game.core.combat_types import DamageContext
from game.simulation.battle_outcome import HitRecord, ModifierApplication
from game.simulation.combat.combat_events import (
    CombatEvent,
    CombatEventBus,
    CombatEventType,
    EventDetailLevel,
)
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack
from game.simulation.combat.telemetry import HitLogRecorder
from game.simulation.components.modifier_effects import ModifierEffect


def _mk_ship(instance_id: str, team_id: int = 0):
    return SimpleNamespace(instance_id=instance_id, team_id=team_id)


def _effect(stat_key: str, value: float, source_name: str = "Mod") -> ModifierEffect:
    return ModifierEffect(
        stat_key=stat_key,
        value=value,
        operation="multiply",
        target_ability=None,
        source_modifier_id="mod",
        source_modifier_name=source_name,
        formula_str="param",
        param_value=value,
    )


def _entry(source: str, stat_key: str, value: float) -> ModifierEntry:
    return ModifierEntry(
        source=source,
        stack_group=None,
        effect=_effect(stat_key, value),
    )


def _ctx(attacker_team_id: int, attacker_ship_id: str = "attacker"):
    return DamageContext(
        attacker=SimpleNamespace(
            instance_id=attacker_ship_id,
            team_id=attacker_team_id,
        ),
        source_weapon=SimpleNamespace(id="laser_cannon"),
        damage_type="beam",
    )


# ---------------------------------------------------------------------------
# Global entries appear on every hit
# ---------------------------------------------------------------------------


def test_global_modifier_appears_on_hit_record():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    stack = ModifierStack(
        per_team={},
        global_=(_entry("system:nebula", "ToHitAttackModifier", 0.3),),
    )
    rec = HitLogRecorder(bus, modifier_stack=stack)

    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("target", team_id=1),
        damage_amount=10.0,
        context=_ctx(attacker_team_id=0),
    ))
    hits = rec.get_hits("target")
    assert len(hits) == 1
    sources = [m.source for m in hits[0].modifiers_applied]
    assert "system:nebula" in sources


# ---------------------------------------------------------------------------
# Per-team modifiers appear only for matching attacker team
# ---------------------------------------------------------------------------


def test_per_team_modifier_appears_only_for_matching_attacker():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    stack = ModifierStack(
        per_team={
            0: (_entry("empire:team0_buff", "ToHitAttackModifier", 0.2),),
            1: (_entry("empire:team1_buff", "ToHitAttackModifier", 0.1),),
        },
        global_=(),
    )
    rec = HitLogRecorder(bus, modifier_stack=stack)

    # Attacker on team 0 hits target on team 1 → team0 entries only.
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("t1", team_id=1),
        damage_amount=5.0,
        context=_ctx(attacker_team_id=0),
    ))
    # Attacker on team 1 hits target on team 0 → team1 entries only.
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("t0", team_id=0),
        damage_amount=5.0,
        context=_ctx(attacker_team_id=1),
    ))

    t1_hit = rec.get_hits("t1")[0]
    t0_hit = rec.get_hits("t0")[0]
    t1_sources = {m.source for m in t1_hit.modifiers_applied}
    t0_sources = {m.source for m in t0_hit.modifiers_applied}

    assert "empire:team0_buff" in t1_sources
    assert "empire:team1_buff" not in t1_sources
    assert "empire:team1_buff" in t0_sources
    assert "empire:team0_buff" not in t0_sources


# ---------------------------------------------------------------------------
# Placeholder effects are filtered out
# ---------------------------------------------------------------------------


def test_placeholder_effects_excluded_from_trace():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    stack = ModifierStack(
        per_team={0: (_entry("complex:stub", "placeholder", 0.0),)},
        global_=(_entry("sector:stub", "placeholder", 0.0),),
    )
    rec = HitLogRecorder(bus, modifier_stack=stack)
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("target"),
        damage_amount=10.0,
        context=_ctx(attacker_team_id=0),
    ))
    hits = rec.get_hits("target")
    assert hits[0].modifiers_applied == ()


# ---------------------------------------------------------------------------
# ModifierApplication carries the right fields
# ---------------------------------------------------------------------------


def test_modifier_application_fields_populated():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    stack = ModifierStack(
        per_team={},
        global_=(_entry("system:research", "ToHitDefenseModifier", 0.75),),
    )
    rec = HitLogRecorder(bus, modifier_stack=stack)
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("target"),
        damage_amount=10.0,
        context=_ctx(attacker_team_id=0),
    ))
    hits = rec.get_hits("target")
    apps = hits[0].modifiers_applied
    assert len(apps) == 1
    app = apps[0]
    assert isinstance(app, ModifierApplication)
    assert app.source == "system:research"
    assert app.effect_name == "ToHitDefenseModifier"
    assert app.value == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# No modifier_stack → empty modifiers_applied (backward compat)
# ---------------------------------------------------------------------------


def test_no_modifier_stack_produces_empty_trace():
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    rec = HitLogRecorder(bus)
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("target"),
        damage_amount=10.0,
        context=_ctx(attacker_team_id=0),
    ))
    hits = rec.get_hits("target")
    assert hits[0].modifiers_applied == ()


def test_missing_attacker_context_produces_only_global_trace():
    """Without attacker context, per-team entries can't be resolved —
    only globals show up in the trace."""
    bus = CombatEventBus(detail_level=EventDetailLevel.DETAILED)
    stack = ModifierStack(
        per_team={0: (_entry("empire:team0_buff", "ToHitAttackModifier", 0.2),)},
        global_=(_entry("system:nebula", "ToHitAttackModifier", 0.3),),
    )
    rec = HitLogRecorder(bus, modifier_stack=stack)
    bus.emit(CombatEvent(
        event_type=CombatEventType.COMPONENT_HIT,
        target_ship=_mk_ship("target"),
        damage_amount=10.0,
        context=None,
    ))
    hits = rec.get_hits("target")
    sources = {m.source for m in hits[0].modifiers_applied}
    assert "system:nebula" in sources
    # No per-team entries without attacker context.
    assert "empire:team0_buff" not in sources
