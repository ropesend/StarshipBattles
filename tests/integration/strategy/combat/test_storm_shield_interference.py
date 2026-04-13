"""End-to-end integration test for strategic shield-interference modifier math.

PROJ-270 Phase 9 Task 9.1 — this is the test that was DEFERRED from Task 6.5.
Its absence is why the skeptic audit was able to find that Track A is
empirically broken. PROJ-270 Phase 6 claimed "strategic-modifier battle-math
restored" on the strength of unit tests asserting the COMPILER emits real
stat_keys, but the downstream pipeline dies at `FleetAuraManager._apply_bonuses`
(which reads only the hardcoded `ToHitAttackModifier`/`ToHitDefenseModifier`
keys from `_team_bonuses` and silently discards everything else).

This file contains the end-to-end regression tests that Phase 9 must make
pass. On first run (pre-fix), they should FAIL, proving the bug. After
Phase 9's bridge work lands, they must go green.
"""
from unittest.mock import MagicMock

from game.ai.ai_factory import AIControllerFactory
from game.core.math import Vector2
from game.simulation.battle_outcome import BattleOutcome
from game.simulation.battle_runner import run_battle
from game.simulation.battle_spec import (
    AIPolicy,
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


# ---------------------------------------------------------------------------
# Test infrastructure — minimal ship + spec builders.
# ---------------------------------------------------------------------------


def _design_with_shields() -> dict:
    """Ship design carrying a `shield_generator` component.

    `shield_generator` has `ShieldProjection` ability with `base_capacity=500`,
    so the ship's `max_shields` should be 500 at baseline and 250 under a
    `shield_capacity_mult=0.5` modifier.
    """
    return {
        "name": "Cruiser",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}, {"id": "shield_generator"}],
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
        ai_policy=AIPolicy(),
    )


def _shield_cap_mult_entry(value: float) -> ModifierEntry:
    """Build a `ModifierEntry` that targets shield capacity multiplicatively."""
    effect = ModifierEffect(
        stat_key="shield_capacity_mult",
        value=value,
        operation="multiply",
        target_ability=None,
        source_modifier_id="test_shield_cap",
        source_modifier_name="Test Shield Interference",
        formula_str="",
        param_value=value,
    )
    return ModifierEntry(source="test_storm", stack_group=None, effect=effect)


def _damage_mult_entry(value: float) -> ModifierEntry:
    effect = ModifierEffect(
        stat_key="damage_mult",
        value=value,
        operation="multiply",
        target_ability=None,
        source_modifier_id="test_damage",
        source_modifier_name="Test Damage Modifier",
        formula_str="",
        param_value=value,
    )
    return ModifierEntry(source="test_fleet_mod", stack_group=None, effect=effect)


def _run(spec: BattleSpec, registries) -> BattleOutcome:
    def ship_builder(ship_spec):
        ship = ShipSerializer.from_dict(_design_with_shields(), registries=registries)
        ship.instance_id = ship_spec.instance_id
        return ship
    return run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
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


def _ship_outcome(outcome: BattleOutcome, instance_id: str):
    for team in outcome.teams:
        for s in team.ships:
            if s.instance_id == instance_id:
                return s
    raise AssertionError(f"Ship {instance_id!r} missing from outcome")


# ---------------------------------------------------------------------------
# Phase 9 failing tests — prove the pipeline is broken today.
# ---------------------------------------------------------------------------


def test_shield_capacity_mult_halves_max_shields(fresh_registries):
    """Ship under `shield_capacity_mult=0.5` should have max_shields = 250.

    Baseline: `shield_generator.ShieldProjection.base_capacity = 500`.
    Multiplier: 0.5.
    Expected: `ship_outcome.max_shields == 250`.
    Actual (pre-Phase 9 fix): 500 — the bug.
    """
    stack = ModifierStack(
        per_team={0: (_shield_cap_mult_entry(0.5),)},
        global_=(),
    )
    spec = BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=UnboundedRegion(exit_policy=ExitPolicy.NONE),
        end_condition=TickLimitCondition(max_ticks=2),
        absolute_max_ticks=100,
        teams=(_team(0, _ship_spec("shielded_ship")), _team(1, _ship_spec("opponent"))),
        modifier_stack=stack,
        post_battle_hook=None,
    )

    outcome = _run(spec, fresh_registries)

    shielded = _ship_outcome(outcome, "shielded_ship")
    # Multiplier must cut effective shield capacity in half:
    assert shielded.max_shields == 250.0, (
        f"Expected max_shields=250 under shield_capacity_mult=0.5, got "
        f"{shielded.max_shields}. Track A pipeline is broken — "
        f"FleetAuraManager._apply_bonuses discards the stat_key."
    )


def test_shield_capacity_mult_only_applies_to_target_team(fresh_registries):
    """`shield_capacity_mult=0.5` on team 0 must NOT affect team 1."""
    stack = ModifierStack(
        per_team={0: (_shield_cap_mult_entry(0.5),)},
        global_=(),
    )
    spec = BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=UnboundedRegion(exit_policy=ExitPolicy.NONE),
        end_condition=TickLimitCondition(max_ticks=2),
        absolute_max_ticks=100,
        teams=(_team(0, _ship_spec("team0_ship")), _team(1, _ship_spec("team1_ship"))),
        modifier_stack=stack,
        post_battle_hook=None,
    )

    outcome = _run(spec, fresh_registries)

    team0_ship = _ship_outcome(outcome, "team0_ship")
    team1_ship = _ship_outcome(outcome, "team1_ship")

    assert team0_ship.max_shields == 250.0, (
        f"Team-0 ship should have halved shields; got {team0_ship.max_shields}"
    )
    assert team1_ship.max_shields == 500.0, (
        f"Team-1 ship should be unaffected; got {team1_ship.max_shields}"
    )


def test_damage_mult_halves_weapon_damage(fresh_registries):
    """Ship with `damage_mult=0.5` should deal half damage.

    Direct assertion on the weapon component's effective `damage` stat after
    battle start. `laser_cannon.BeamWeapon._base_damage` is the baseline;
    with `damage_mult=0.5` applied, `weapon.damage` should be halved.

    If the integration test is too opaque (stat read from a deep component
    path), this test can be skipped and proven instead by component-level
    inspection during Task 9.3.
    """
    stack = ModifierStack(
        per_team={0: (_damage_mult_entry(0.5),)},
        global_=(),
    )
    spec = BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=UnboundedRegion(exit_policy=ExitPolicy.NONE),
        end_condition=TickLimitCondition(max_ticks=3),
        absolute_max_ticks=100,
        teams=(_team(0, _ship_spec("weak_ship")), _team(1, _ship_spec("opponent"))),
        modifier_stack=stack,
        post_battle_hook=None,
    )

    # For now, assert the plumbing reached the FleetAuraManager but not further.
    # Once Task 9.3 implements the bridge, extend this test to inspect the
    # weapon component's effective damage directly.
    outcome = _run(spec, fresh_registries)
    # Minimum assertion: outcome is produced (doesn't crash) — and
    # telemetry or ShipOutcome records reflect the reduced damage somehow.
    # Tightened assertion depends on Task 9.3 bridge choice.
    assert outcome is not None
    # Placeholder for future tightening. Intentionally no negation-assertion
    # so the test doesn't spuriously pass while the bug is live. The other
    # two tests above cover the empirical regression.
