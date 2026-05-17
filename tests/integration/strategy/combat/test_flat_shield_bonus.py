"""PROJ-271 Phase 4.2: Dedicated integration tests for `flat_shield_bonus`.

Parallel file to `test_storm_shield_interference.py` (Track A) —
locks Track B end-to-end mechanics.

Covers:
- Direct ModifierStack `shield_bonus_add` entry → ship.max_shields raised
- Strategy compiler `FleetCombatModifiers.flat_shield_bonus` → ship buff
- Pipeline ordering `(base + flat) × mult` proven via battle outcomes
"""
from game.ai.ai_factory import AIControllerFactory
from game.core.math import Vector2
from game.simulation.battle_outcome import BattleOutcome
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
from game.simulation.combat.boundary import UnboundedRegion, ExitPolicy
from game.simulation.combat.modifier_stack import ModifierEntry, ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.components.modifier_effects import ModifierEffect
from game.simulation.entities.ship_serialization import ShipSerializer
from game.simulation.systems.battle_end_conditions import TickLimitCondition


def _design_with_shields() -> dict:
    return {
        "name": "Cruiser",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            # crew_quarters + life_support are required so the bridge (CrewRequired)
            # has crew to operate; without them all weapons/shields go inactive.
            "CORE": [
                {"id": "bridge"},
                {"id": "crew_quarters"},
                {"id": "life_support"},
                {"id": "shield_generator"},
            ],
            "OUTER": [{"id": "laser_cannon"}],
            "ARMOR": [],
        },
        "_metadata": {},
    }


def _team(team_id: int, ship: ShipSpec) -> TeamSpec:
    return TeamSpec(
        team_id=team_id,
        name=f"Team {team_id}",
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


def _ship_spec(instance_id: str) -> ShipSpec:
    return ShipSpec(
        instance_id=instance_id,
        design_id="Cruiser",
        theme_id="Federation",
        name=instance_id,
        position=Vector2(0.0, 0.0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )


def _run(spec: BattleSpec, registries) -> BattleOutcome:
    def ship_builder(ship_spec, team_id):
        ship = ShipSerializer.from_dict(_design_with_shields(), registries=registries)
        ship.instance_id = ship_spec.instance_id
        return ship
    return run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )


def _ship_outcome(outcome: BattleOutcome, instance_id: str):
    for team in outcome.teams:
        for s in team.ships:
            if s.instance_id == instance_id:
                return s
    raise AssertionError(f"Ship {instance_id!r} missing from outcome")


def _bonus_entry(value: float) -> ModifierEntry:
    return ModifierEntry(
        source="test_flat_shield",
        stack_group=None,
        effect=ModifierEffect(
            stat_key="shield_bonus_add",
            value=value,
            operation="add",
            target_ability=None,
            source_modifier_id="test_flat_shield",
            source_modifier_name="Flat Shield Bonus",
            formula_str="",
            param_value=value,
        ),
    )


def _mult_entry(value: float) -> ModifierEntry:
    return ModifierEntry(
        source="test_shield_mult",
        stack_group=None,
        effect=ModifierEffect(
            stat_key="shield_capacity_mult",
            value=value,
            operation="multiply",
            target_ability=None,
            source_modifier_id="test_shield_mult",
            source_modifier_name="Shield Mult",
            formula_str="",
            param_value=value,
        ),
    )


def test_flat_shield_bonus_appears_in_outcome(fresh_registries):
    """`shield_bonus_add=75` on team 0 → ShipOutcome.max_shields == 575."""
    stack = ModifierStack(per_team={0: (_bonus_entry(75.0),)}, global_=())
    spec = BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=UnboundedRegion(exit_policy=ExitPolicy.NONE),
        end_condition=TickLimitCondition(max_ticks=2),
        absolute_max_ticks=100,
        teams=(_team(0, _ship_spec("buffed")), _team(1, _ship_spec("baseline"))),
        modifier_stack=stack,
        post_battle_hook=None,
    )
    outcome = _run(spec, fresh_registries)
    buffed = _ship_outcome(outcome, "buffed")
    baseline = _ship_outcome(outcome, "baseline")
    assert buffed.max_shields == 575.0
    assert baseline.max_shields == 500.0


def test_flat_bonus_and_storm_mult_compose(fresh_registries):
    """Pipeline: (500 base + 50 flat) × 0.5 storm = 275."""
    stack = ModifierStack(
        per_team={0: (_bonus_entry(50.0), _mult_entry(0.5))},
        global_=(),
    )
    spec = BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=UnboundedRegion(exit_policy=ExitPolicy.NONE),
        end_condition=TickLimitCondition(max_ticks=2),
        absolute_max_ticks=100,
        teams=(_team(0, _ship_spec("stormed_buffed")), _team(1, _ship_spec("baseline"))),
        modifier_stack=stack,
        post_battle_hook=None,
    )
    outcome = _run(spec, fresh_registries)
    ship = _ship_outcome(outcome, "stormed_buffed")
    assert ship.max_shields == 275.0


def test_flat_shield_bonus_from_strategy_compiler_helper(fresh_registries):
    """End-to-end: FleetCombatModifiers → compiler → ModifierStack → run_battle."""
    from game.strategy.combat.strategy_modifier_stack_builder import StrategyModifierStackBuilder
    from game.strategy.services.combat_modifier_collector import FleetCombatModifiers

    mods = FleetCombatModifiers(shield_mult=1.0, damage_mult=1.0, flat_shield_bonus=100.0)
    entries = tuple(StrategyModifierStackBuilder().entries_from_fleet_combat_modifiers(mods, team_id=0))
    stack = ModifierStack(per_team={0: entries}, global_=())
    spec = BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=UnboundedRegion(exit_policy=ExitPolicy.NONE),
        end_condition=TickLimitCondition(max_ticks=2),
        absolute_max_ticks=100,
        teams=(_team(0, _ship_spec("planet_buffed")), _team(1, _ship_spec("baseline"))),
        modifier_stack=stack,
        post_battle_hook=None,
    )
    outcome = _run(spec, fresh_registries)
    buffed = _ship_outcome(outcome, "planet_buffed")
    assert buffed.max_shields == 600.0
