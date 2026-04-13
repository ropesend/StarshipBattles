"""Tests for `BattleEngine.modifier_stack` field (PROJ-269 Phase 5.5 Task 5.5.1).

Covers:
- `BattleEngine(modifier_stack=stack)` stores the stack on `self.modifier_stack`
- Default is None when not passed
- `run_battle(spec)` threads `spec.modifier_stack` onto the engine
"""
from typing import Callable

import pytest

from game.ai.ai_factory import AIControllerFactory
from game.core.math import Vector2
from game.simulation.battle_runner import run_battle
from game.simulation.battle_spec import (
    BattleSpec,
    CombatPolicies,
    EntryVector,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.components.modifier_effects import ModifierEffect
from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_serialization import ShipSerializer
from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import TickLimitCondition


def _design() -> dict:
    return {
        "name": "MSCruiser",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {"CORE": [{"id": "bridge"}], "ARMOR": []},
        "_metadata": {},
    }


@pytest.fixture
def ship_builder(fresh_registries) -> Callable[[ShipSpec], Ship]:
    def _build(ship_spec):
        ship = ShipSerializer.from_dict(_design(), registries=fresh_registries)
        ship.instance_id = ship_spec.instance_id
        return ship
    return _build


def _team(team_id: int, ship: ShipSpec) -> TeamSpec:
    return TeamSpec(
        team_id=team_id,
        name=f"T{team_id}",
        entry_vector=EntryVector(origin=Vector2(0, 0), facing=0.0),
        fleet_hierarchy=(
            TaskForceSpec(
                task_force_id=f"tf-{team_id}",
                formation=None,
                policies=CombatPolicies(),
                squadrons=(
                    SquadronSpec(
                        squadron_id=f"sq-{team_id}",
                        policies=CombatPolicies(),
                        ships=(ship,),
                    ),
                ),
            ),
        ),
    )


def _real_effect(stat_key: str, value: float) -> ModifierEffect:
    return ModifierEffect(
        stat_key=stat_key,
        value=value,
        operation="multiply",
        target_ability=None,
        source_modifier_id="test_mod",
        source_modifier_name="Test Mod",
        formula_str="param",
        param_value=value,
    )


# ---------------------------------------------------------------------------
# BattleEngine.modifier_stack field
# ---------------------------------------------------------------------------


def test_battle_engine_default_modifier_stack_is_none():
    engine = BattleEngine(ai_factory=AIControllerFactory())
    assert engine.modifier_stack is None


def test_battle_engine_accepts_modifier_stack_kwarg():
    stack = ModifierStack.empty()
    engine = BattleEngine(
        ai_factory=AIControllerFactory(),
        modifier_stack=stack,
    )
    assert engine.modifier_stack is stack


# ---------------------------------------------------------------------------
# run_battle threads modifier_stack onto engine
# ---------------------------------------------------------------------------


def test_run_battle_threads_modifier_stack_onto_engine(ship_builder):
    entry = ModifierEntry(
        source="empire:test",
        stack_group=None,
        effect=_real_effect("ToHitAttackModifier", 0.5),
    )
    stack = ModifierStack(per_team={0: (entry,)}, global_=())

    # Capture engine reference via per_tick_callback.
    captured = {"engine": None}

    def capture(engine):
        captured["engine"] = engine

    ship_a = ShipSpec(
        instance_id="a",
        design_id="Cruiser",
        theme_id="Federation",
        name="A",
        position=Vector2(-500, 0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )
    ship_b = ShipSpec(
        instance_id="b",
        design_id="Cruiser",
        theme_id="Federation",
        name="B",
        position=Vector2(500, 0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )
    spec = BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=1),
        absolute_max_ticks=10,
        teams=(_team(0, ship_a), _team(1, ship_b)),
        modifier_stack=stack,
        post_battle_hook=None,
    )
    run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
        per_tick_callback=capture,
    )
    engine = captured["engine"]
    assert engine is not None
    assert engine.modifier_stack is stack
