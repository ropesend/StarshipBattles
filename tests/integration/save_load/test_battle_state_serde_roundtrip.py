"""Characterization tests for the simulation BattleState serde extraction.

PROJ-460 Phase 1 (F-D-028): these tests lock the byte-for-byte shape of
``to_dict`` and the round-trip identity through ``from_dict`` for the five
``battle_state`` dataclasses (ComponentState, ShipState, ProjectileState,
BattleState, BattleResults) so the extraction into
``game/simulation/battle_state_serde.py`` cannot drift.

The contract is byte-identity of the serialized dict: build a representative
instance, serialize, deserialize, and assert the re-serialized dict equals the
original dict. This is a characterization-first refactor (the tests pass
against current behavior) and serves as the regression gate post-extraction.
"""
from __future__ import annotations

from game.simulation.battle_state import (
    BattleResults,
    BattleState,
    ComponentState,
    ProjectileState,
    ShipState,
)


def _build_component_state() -> ComponentState:
    """Component with a non-empty modifier list and non-default flags."""
    return ComponentState(
        component_id="laser_cannon_mk2",
        current_hp=37,
        max_hp=50,
        is_active=False,
        layer="WEAPONS",
        modifiers=[{"id": "overcharge", "value": 1.25}],
    )


def _build_ship_state() -> ShipState:
    """Ship with components, resources, and non-default status flags."""
    return ShipState(
        ship_id="ship-abc-123",
        name="ISS Resolute",
        ship_class="cruiser",
        theme_id="federation",
        team_id=1,
        color=(12, 200, 255),
        movement_policy="aggressive",
        position=(123.5, -42.0),
        velocity=(1.5, -3.25),
        angle=0.785,
        current_hp=420,
        max_hp=500,
        current_shields=88.5,
        max_shields=120.0,
        components={
            "WEAPONS": [_build_component_state()],
            "ENGINES": [
                ComponentState(
                    component_id="ion_drive",
                    current_hp=20,
                    max_hp=20,
                    is_active=True,
                    layer="ENGINES",
                    modifiers=[],
                )
            ],
        },
        resource_levels={"power": 75.0, "fuel": 30.0},
        resource_max={"power": 100.0, "fuel": 50.0},
        targeting_policy="focus_fire",
        is_alive=True,
        is_derelict=False,
        retreat_status="retreating",
        current_target_id="ship-def-456",
    )


def _build_projectile_state() -> ProjectileState:
    """Missile-shaped projectile exercising all optional fields."""
    return ProjectileState(
        projectile_id="proj-777",
        owner_ship_id="ship-abc-123",
        team_id=1,
        position=(50.0, 60.0),
        velocity=(10.0, 0.0),
        damage=45.5,
        max_range=800.0,
        endurance=12.0,
        max_endurance=20.0,
        projectile_type="missile",
        turn_rate=3.5,
        max_speed=15.0,
        target_ship_id="ship-def-456",
        hp=2,
        max_hp=3,
        distance_traveled=125.0,
        is_alive=True,
    )


def _build_battle_state() -> BattleState:
    """Battle with ships, projectiles, and non-default end-condition data."""
    ship = _build_ship_state()
    return BattleState(
        version="1.0",
        battle_id="battle-xyz-001",
        seed=424242,
        tick_count=137,
        ships={ship.ship_id: ship},
        projectiles=[_build_projectile_state()],
        end_condition_data={"type": "ticks_elapsed", "max_ticks": 5000},
        allow_retreat=True,
        allow_reinforcements=False,
        created_at="2026-05-19T12:00:00",
    )


def _build_battle_results() -> BattleResults:
    """Results with nested initial/final states and categorized ships."""
    initial = _build_battle_state()
    final = _build_battle_state()
    survivor = _build_ship_state()
    destroyed = _build_ship_state()
    destroyed.is_alive = False
    return BattleResults(
        winner=1,
        tick_count=137,
        seed=424242,
        initial_state=initial,
        final_state=final,
        surviving_ships=[survivor],
        destroyed_ships=[destroyed],
        escaped_ships=[],
        captured_ships=[],
    )


def test_component_state_round_trip() -> None:
    original = _build_component_state()
    original_dict = original.to_dict()
    restored = ComponentState.from_dict(original_dict)
    assert restored.to_dict() == original_dict


def test_ship_state_round_trip() -> None:
    original = _build_ship_state()
    original_dict = original.to_dict()
    restored = ShipState.from_dict(original_dict)
    assert restored.to_dict() == original_dict


def test_projectile_state_round_trip() -> None:
    original = _build_projectile_state()
    original_dict = original.to_dict()
    restored = ProjectileState.from_dict(original_dict)
    assert restored.to_dict() == original_dict


def test_battle_state_round_trip() -> None:
    original = _build_battle_state()
    original_dict = original.to_dict()
    restored = BattleState.from_dict(original_dict)
    assert restored.to_dict() == original_dict


def test_battle_results_round_trip() -> None:
    original = _build_battle_results()
    original_dict = original.to_dict()
    restored = BattleResults.from_dict(original_dict)
    assert restored.to_dict() == original_dict
