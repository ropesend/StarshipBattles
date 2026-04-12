"""Tests for BattleOutcome DTOs (PROJ-269 Phase 1 Task 1.1).

Covers:
- Frozen dataclass shape per design.md §2.4
- ShipStatus / EndReason enums with required members
- ModifierApplication, HitRecord, WeaponSummary, ShipStats shapes
- Invariant: every ShipSpec.instance_id should map to exactly one
  ShipOutcome.instance_id (tested structurally by building matching shapes)
"""
import dataclasses
from enum import Enum

import pytest

from game.core.math import Vector2
from game.simulation.battle_outcome import (
    BattleOutcome,
    EndReason,
    HitRecord,
    ModifierApplication,
    ShipOutcome,
    ShipStats,
    ShipStatus,
    TaskForceOutcome,
    TeamOutcome,
    WeaponSummary,
)
from game.simulation.battle_spec import ComponentStateSpec


# ---------------------------------------------------------------------------
# Frozen-shape tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cls",
    [
        ModifierApplication,
        HitRecord,
        WeaponSummary,
        ShipStats,
        ShipOutcome,
        TaskForceOutcome,
        TeamOutcome,
        BattleOutcome,
    ],
)
def test_outcome_dto_is_frozen_dataclass(cls):
    assert dataclasses.is_dataclass(cls), f"{cls.__name__} must be a dataclass"
    params = getattr(cls, "__dataclass_params__", None)
    assert params is not None and params.frozen, (
        f"{cls.__name__} must be frozen (frozen=True)"
    )


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


def test_ship_status_enum_members():
    assert issubclass(ShipStatus, Enum)
    names = {m.name for m in ShipStatus}
    assert {"SURVIVED", "DESTROYED", "DERELICT", "RETREATED"}.issubset(names)


def test_end_reason_enum_members():
    assert issubclass(EndReason, Enum)
    names = {m.name for m in EndReason}
    # Matches the existing battle_end_conditions._CONDITION_TYPES discriminators
    # plus ABSOLUTE_MAX for the engine safety ceiling.
    required = {
        "TICK_LIMIT",
        "TEAM_ELIMINATED",
        "TEAM_INCAPACITATED",
        "ESCAPE",
        "SHIP_DESTROYED",
        "NEVER",
        "MASS_RATIO",
        "ANY",
        "ALL",
        "ABSOLUTE_MAX",
    }
    missing = required - names
    assert not missing, f"EndReason missing members: {missing}"


# ---------------------------------------------------------------------------
# Field-shape tests for each DTO
# ---------------------------------------------------------------------------


def test_modifier_application_fields():
    ma = ModifierApplication(
        source="species:Terran",
        effect_name="ToHitAttackModifier",
        value=1.5,
    )
    assert ma.source == "species:Terran"
    assert ma.effect_name == "ToHitAttackModifier"
    assert ma.value == pytest.approx(1.5)
    with pytest.raises(dataclasses.FrozenInstanceError):
        ma.value = 0.0  # type: ignore[misc]


def test_hit_record_fields():
    hr = HitRecord(
        tick=10,
        attacker_ship_id="ship-a",
        weapon_component_id="beam_small",
        weapon_ability_class="BeamWeaponAbility",
        damage=42.0,
        modifiers_applied=(
            ModifierApplication(source="system:nebula", effect_name="accuracy", value=0.9),
        ),
    )
    assert hr.tick == 10
    assert hr.weapon_ability_class == "BeamWeaponAbility"
    assert isinstance(hr.modifiers_applied, tuple)
    assert len(hr.modifiers_applied) == 1


def test_weapon_summary_fields():
    ws = WeaponSummary(
        component_id="laser_1",
        component_name="Laser Battery",
        shots_fired=12,
        shots_hit=8,
    )
    assert ws.shots_fired == 12
    assert ws.shots_hit == 8


def test_ship_stats_fields():
    stats = ShipStats(
        total_damage_taken=123.0,
        peak_speed=45.6,
        ticks_derelict=7,
        ticks_alive=500,
    )
    assert stats.total_damage_taken == pytest.approx(123.0)
    assert stats.peak_speed == pytest.approx(45.6)
    assert stats.ticks_derelict == 7
    assert stats.ticks_alive == 500


def _minimal_ship_outcome(instance_id: str = "ship-1") -> ShipOutcome:
    return ShipOutcome(
        instance_id=instance_id,
        status=ShipStatus.SURVIVED,
        final_position=Vector2(100.0, 50.0),
        final_angle=90.0,
        final_velocity=Vector2(0.0, 0.0),
        components=(
            ComponentStateSpec(
                component_id="bridge",
                instance_index=0,
                current_hp=200.0,
                is_active=True,
            ),
        ),
        weapons=(
            WeaponSummary(
                component_id="w1",
                component_name="Weapon",
                shots_fired=0,
                shots_hit=0,
            ),
        ),
        hits_taken=(),
        stats=ShipStats(
            total_damage_taken=0.0,
            peak_speed=0.0,
            ticks_derelict=0,
            ticks_alive=100,
        ),
    )


def test_ship_outcome_fields():
    so = _minimal_ship_outcome()
    for field in (
        "instance_id",
        "status",
        "final_position",
        "final_angle",
        "final_velocity",
        "components",
        "weapons",
        "hits_taken",
        "stats",
    ):
        assert hasattr(so, field), f"ShipOutcome missing field {field!r}"
    assert so.status == ShipStatus.SURVIVED
    assert isinstance(so.components, tuple)
    assert isinstance(so.weapons, tuple)
    assert isinstance(so.hits_taken, tuple)


def test_team_outcome_fields_and_shape():
    team = TeamOutcome(
        team_id=1,
        name="Federation",
        fleet_hierarchy=(TaskForceOutcome(task_force_id="tf-1"),),
        ships=(_minimal_ship_outcome(),),
    )
    assert team.team_id == 1
    assert team.name == "Federation"
    assert isinstance(team.fleet_hierarchy, tuple)
    assert isinstance(team.ships, tuple)


def test_battle_outcome_fields():
    outcome = BattleOutcome(
        end_reason=EndReason.TEAM_ELIMINATED,
        duration_ticks=250,
        seed=42,
        teams=(
            TeamOutcome(
                team_id=0,
                name="Team 0",
                fleet_hierarchy=(),
                ships=(),
            ),
        ),
        telemetry_level="NORMAL",
    )
    assert outcome.end_reason == EndReason.TEAM_ELIMINATED
    assert outcome.duration_ticks == 250
    assert outcome.seed == 42
    assert isinstance(outcome.teams, tuple)


def test_battle_outcome_is_immutable():
    outcome = BattleOutcome(
        end_reason=EndReason.TICK_LIMIT,
        duration_ticks=100,
        seed=1,
        teams=(),
        telemetry_level="NORMAL",
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        outcome.duration_ticks = 0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Invariant: instance_id round-trip shape (§2.4 "Key invariants")
# ---------------------------------------------------------------------------


def test_outcome_ship_ids_match_spec_ship_ids_when_constructed_to_match():
    """Structural check: if constructor code produces matching instance_ids,
    ShipOutcome.instance_id corresponds 1:1 with ShipSpec.instance_id.

    The engine-side enforcement of this invariant lands in Task 1.6; this test
    just pins that the DTOs *can* carry the same identifier.
    """
    from game.simulation.battle_spec import ShipSpec

    spec = ShipSpec(
        instance_id="abc-123",
        design_id="d",
        theme_id="t",
        name="n",
        position=Vector2(0, 0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )
    outcome = _minimal_ship_outcome(instance_id="abc-123")
    assert spec.instance_id == outcome.instance_id


# ---------------------------------------------------------------------------
# Public-export surface
# ---------------------------------------------------------------------------


def test_battle_outcome_exports_from_game_simulation():
    from game.simulation import BattleOutcome as ExportedBattleOutcome

    assert ExportedBattleOutcome is BattleOutcome
