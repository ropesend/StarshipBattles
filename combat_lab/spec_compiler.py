"""Combat Lab spec compiler — TestScenario → BattleSpec.

Introduced by PROJ-269 Phase 1 Task 1.7. Translates a Combat Lab
`TestScenario` into a `BattleSpec` that `run_battle(spec)` can execute.

PROJ-269 Phase 6 Task 6.7a extends dispatch to all 5 scenario templates:
`StaticTargetScenario`, `DuelScenario`, `PropulsionScenario`,
`ResourceScenario`, `ComparisonScenario`. Each template emits a spec that
mirrors its `setup()` positions / angles / initial pose.

The compiler records each ship's loader filename as `ShipSpec.design_id`.
Materialization is deferred to a `ship_builder` closure supplied by the
Combat Lab runner (`combat_lab/runner.py`). Every `ShipSpec.instance_id`
carries a role suffix (`:attacker`, `:target`, `:ship1`, `:ship2`,
`:ship`, `:variant_attacker`, `:variant_target`, `:baseline_attacker`,
`:baseline_target`) so the runner can wire Ship references back onto the
scenario's template-level attributes via `scenario.wire_ships({role: ship})`.

`boundary` = `UnboundedRegion()` — Combat Lab tests are unbounded.
`modifier_stack` = `ModifierStack.empty()` — test scenarios don't use
modifiers today.
`telemetry_level` = DETAILED by default (Combat Lab needs the full hit
log); scenarios can override via `TestMetadata.telemetry_level`.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

from combat_lab.scenarios.base import TestScenario
from combat_lab.scenarios.templates import (
    ComparisonScenario,
    DuelScenario,
    PropulsionScenario,
    ResourceScenario,
    StaticTargetScenario,
)
from game.core.math import Vector2
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
from game.simulation.combat.boundary import UnboundedRegion
from game.simulation.combat.formation import FormationShape, FormationSpec
from game.simulation.combat.modifier_stack import ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel

if TYPE_CHECKING:
    from game.core.registry import GameRegistries


# ---------------------------------------------------------------------------
# Public entry
# ---------------------------------------------------------------------------


def build_test_battle_spec(
    scenario: TestScenario,
    registries: Optional["GameRegistries"],
) -> BattleSpec:
    """Compile a `TestScenario` into a `BattleSpec`.

    Dispatches on the scenario's template type. Unsupported subclasses
    (pure `TestScenario` with no template) raise `NotImplementedError` —
    a scenario must inherit from one of the five known templates to be
    compilable into a spec.
    """
    _ = registries  # Unused: materialization happens in the runner.

    if isinstance(scenario, StaticTargetScenario):
        return _compile_static_target(scenario)
    if isinstance(scenario, DuelScenario):
        return _compile_duel(scenario)
    if isinstance(scenario, PropulsionScenario):
        return _compile_propulsion(scenario)
    if isinstance(scenario, ResourceScenario):
        return _compile_resource(scenario)
    if isinstance(scenario, ComparisonScenario):
        return _compile_comparison(scenario)

    raise NotImplementedError(
        f"Combat Lab spec compiler does not support "
        f"{type(scenario).__name__}. Subclass one of "
        "StaticTargetScenario / DuelScenario / PropulsionScenario / "
        "ResourceScenario / ComparisonScenario."
    )


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _single_ship_custom_formation() -> FormationSpec:
    """CUSTOM formation with one local-frame position at origin."""
    return FormationSpec(
        shape=FormationShape.CUSTOM,
        spacing=100.0,
        custom_positions=(Vector2(0.0, 0.0),),
    )


def _one_ship_team(
    *,
    team_id: int,
    team_name: str,
    ship: ShipSpec,
    entry_origin: Vector2,
    entry_facing: float,
    task_force_id: str,
    squadron_id: str,
) -> TeamSpec:
    """Wrap a single ShipSpec in the TF/Squadron/Team scaffolding."""
    return TeamSpec(
        team_id=team_id,
        name=team_name,
        entry_vector=EntryVector(origin=entry_origin, facing=entry_facing),
        fleet_hierarchy=(
            TaskForceSpec(
                task_force_id=task_force_id,
                formation=_single_ship_custom_formation(),
                policies=CombatPolicies(),
                squadrons=(
                    SquadronSpec(
                        squadron_id=squadron_id,
                        policies=CombatPolicies(),
                        ships=(ship,),
                    ),
                ),
            ),
        ),
        ai_policy=AIPolicy(),
    )


def _resolve_telemetry_level(metadata) -> TelemetryLevel:
    """Parse `metadata.telemetry_level` (str) into a `TelemetryLevel`.

    Default when unset or unrecognized: DETAILED (Combat Lab default).
    """
    raw = getattr(metadata, "telemetry_level", None)
    if isinstance(raw, TelemetryLevel):
        return raw
    if isinstance(raw, str):
        name = raw.strip().upper()
        try:
            return TelemetryLevel[name]
        except KeyError:
            pass
    return TelemetryLevel.DETAILED


def _absolute_max(metadata_max_ticks: int) -> int:
    """Safety ceiling: 10× metadata max_ticks, floored at 1000."""
    return max(int(metadata_max_ticks) * 10, 1000)


def _make_spec(
    *,
    scenario: TestScenario,
    teams: Tuple[TeamSpec, ...],
) -> BattleSpec:
    """Assemble the final BattleSpec with Combat Lab defaults."""
    return BattleSpec(
        seed=scenario.metadata.seed,
        telemetry_level=_resolve_telemetry_level(scenario.metadata),
        boundary=UnboundedRegion(),
        end_condition=scenario._create_end_condition(),
        absolute_max_ticks=_absolute_max(scenario.metadata.max_ticks),
        teams=teams,
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )


def _ship_spec(
    *,
    scenario: TestScenario,
    role: str,
    design_id: str,
    position: Vector2,
    angle: float,
    velocity: Vector2 = Vector2(0.0, 0.0),
    name_suffix: Optional[str] = None,
) -> ShipSpec:
    """Build a `ShipSpec` with role-tagged instance_id."""
    test_id = scenario.metadata.test_id
    suffix = name_suffix if name_suffix is not None else role
    return ShipSpec(
        instance_id=f"{test_id}:{role}",
        design_id=design_id,
        theme_id="Federation",
        name=f"{test_id}-{suffix}",
        position=position,
        angle=angle,
        velocity=velocity,
        components=(),
    )


# ---------------------------------------------------------------------------
# StaticTargetScenario compiler
# ---------------------------------------------------------------------------


def _compile_static_target(scenario: StaticTargetScenario) -> BattleSpec:
    if scenario.attacker_ship is None:
        raise ValueError(
            f"{type(scenario).__name__}.attacker_ship must be set"
        )
    if scenario.target_ship is None:
        raise ValueError(
            f"{type(scenario).__name__}.target_ship must be set"
        )
    if scenario.distance is None:
        raise ValueError(
            f"{type(scenario).__name__}.distance must be set"
        )

    attacker = _ship_spec(
        scenario=scenario,
        role="attacker",
        design_id=scenario.attacker_ship,
        position=Vector2(0.0, 0.0),
        angle=float(scenario.attacker_angle),
    )
    target = _ship_spec(
        scenario=scenario,
        role="target",
        design_id=scenario.target_ship,
        position=Vector2(float(scenario.distance), 0.0),
        angle=float(scenario.target_angle),
    )

    team_attacker = _one_ship_team(
        team_id=0, team_name="Attacker", ship=attacker,
        entry_origin=Vector2(0.0, 0.0), entry_facing=0.0,
        task_force_id="tf-attacker", squadron_id="sq-attacker",
    )
    team_target = _one_ship_team(
        team_id=1, team_name="Target", ship=target,
        entry_origin=Vector2(float(scenario.distance), 0.0),
        entry_facing=180.0,
        task_force_id="tf-target", squadron_id="sq-target",
    )
    return _make_spec(scenario=scenario, teams=(team_attacker, team_target))


# ---------------------------------------------------------------------------
# DuelScenario compiler
# ---------------------------------------------------------------------------


def _compile_duel(scenario: DuelScenario) -> BattleSpec:
    if scenario.ship1_file is None:
        raise ValueError(f"{type(scenario).__name__}.ship1_file must be set")
    if scenario.ship2_file is None:
        raise ValueError(f"{type(scenario).__name__}.ship2_file must be set")
    if scenario.distance is None:
        raise ValueError(f"{type(scenario).__name__}.distance must be set")

    # Mirror template setup(): ships placed at ±distance/2 unless
    # explicitly overridden by ship1_position / ship2_position.
    if scenario.ship1_position is not None:
        p1 = Vector2(
            float(scenario.ship1_position.x), float(scenario.ship1_position.y)
        )
    else:
        p1 = Vector2(-float(scenario.distance) / 2.0, 0.0)
    if scenario.ship2_position is not None:
        p2 = Vector2(
            float(scenario.ship2_position.x), float(scenario.ship2_position.y)
        )
    else:
        p2 = Vector2(float(scenario.distance) / 2.0, 0.0)

    ship1 = _ship_spec(
        scenario=scenario,
        role="ship1",
        design_id=scenario.ship1_file,
        position=p1,
        angle=float(scenario.ship1_angle),
    )
    ship2 = _ship_spec(
        scenario=scenario,
        role="ship2",
        design_id=scenario.ship2_file,
        position=p2,
        angle=float(scenario.ship2_angle),
    )

    team1 = _one_ship_team(
        team_id=0, team_name="Ship1", ship=ship1,
        entry_origin=p1, entry_facing=float(scenario.ship1_angle),
        task_force_id="tf-ship1", squadron_id="sq-ship1",
    )
    team2 = _one_ship_team(
        team_id=1, team_name="Ship2", ship=ship2,
        entry_origin=p2, entry_facing=float(scenario.ship2_angle),
        task_force_id="tf-ship2", squadron_id="sq-ship2",
    )
    return _make_spec(scenario=scenario, teams=(team1, team2))


# ---------------------------------------------------------------------------
# PropulsionScenario compiler
# ---------------------------------------------------------------------------


def _compile_propulsion(scenario: PropulsionScenario) -> BattleSpec:
    if scenario.ship_file is None:
        raise ValueError(f"{type(scenario).__name__}.ship_file must be set")

    # pygame.Vector2 → core Vector2. Templates use pygame Vector2 for
    # `initial_position`/`initial_velocity` defaults.
    init_pos = _to_core_vector(scenario.initial_position)
    init_vel = _to_core_vector(scenario.initial_velocity)

    ship = _ship_spec(
        scenario=scenario,
        role="ship",
        design_id=scenario.ship_file,
        position=init_pos,
        angle=float(scenario.initial_angle),
        velocity=init_vel,
    )
    team = _one_ship_team(
        team_id=0, team_name="Ship", ship=ship,
        entry_origin=init_pos, entry_facing=float(scenario.initial_angle),
        task_force_id="tf-ship", squadron_id="sq-ship",
    )
    return _make_spec(scenario=scenario, teams=(team,))


# ---------------------------------------------------------------------------
# ResourceScenario compiler
# ---------------------------------------------------------------------------


def _compile_resource(scenario: ResourceScenario) -> BattleSpec:
    if scenario.ship_file is None:
        raise ValueError(f"{type(scenario).__name__}.ship_file must be set")
    if scenario.resource_type is None:
        raise ValueError(
            f"{type(scenario).__name__}.resource_type must be set"
        )
    if scenario.force_fire and scenario.target_ship_file is None:
        raise ValueError(
            f"{type(scenario).__name__} has force_fire=True but no "
            "'target_ship_file' set"
        )

    ship = _ship_spec(
        scenario=scenario,
        role="ship",
        design_id=scenario.ship_file,
        position=Vector2(0.0, 0.0),
        angle=0.0,
    )
    team_ship = _one_ship_team(
        team_id=0, team_name="Ship", ship=ship,
        entry_origin=Vector2(0.0, 0.0), entry_facing=0.0,
        task_force_id="tf-ship", squadron_id="sq-ship",
    )

    if scenario.target_ship_file is None:
        # Single-team spec: no opponent.
        return _make_spec(scenario=scenario, teams=(team_ship,))

    target = _ship_spec(
        scenario=scenario,
        role="target",
        design_id=scenario.target_ship_file,
        position=Vector2(float(scenario.target_distance), 0.0),
        angle=0.0,
    )
    team_target = _one_ship_team(
        team_id=1, team_name="Target", ship=target,
        entry_origin=Vector2(float(scenario.target_distance), 0.0),
        entry_facing=180.0,
        task_force_id="tf-target", squadron_id="sq-target",
    )
    return _make_spec(scenario=scenario, teams=(team_ship, team_target))


# ---------------------------------------------------------------------------
# ComparisonScenario compiler
# ---------------------------------------------------------------------------


def _compile_comparison(scenario: ComparisonScenario) -> BattleSpec:
    required = (
        scenario.baseline_attacker_ship,
        scenario.baseline_target_ship,
        scenario.variant_attacker_ship,
        scenario.variant_target_ship,
        scenario.distance,
    )
    if any(v is None for v in required):
        raise ValueError(
            f"{type(scenario).__name__} must set baseline_*_ship / "
            "variant_*_ship / distance"
        )

    # Visual-baseline mode runs the baseline on the runner's engine;
    # normal mode runs the variant (baseline runs privately via Task 6.8).
    if getattr(scenario, "_visual_baseline", False):
        attacker_design = scenario.baseline_attacker_ship
        target_design = scenario.baseline_target_ship
        attacker_role = "baseline_attacker"
        target_role = "baseline_target"
    else:
        attacker_design = scenario.variant_attacker_ship
        target_design = scenario.variant_target_ship
        attacker_role = "variant_attacker"
        target_role = "variant_target"

    attacker = _ship_spec(
        scenario=scenario,
        role=attacker_role,
        design_id=attacker_design,
        position=Vector2(0.0, 0.0),
        angle=float(scenario.attacker_angle),
    )
    target = _ship_spec(
        scenario=scenario,
        role=target_role,
        design_id=target_design,
        position=Vector2(float(scenario.distance), 0.0),
        angle=float(scenario.target_angle),
    )
    team_attacker = _one_ship_team(
        team_id=0, team_name="Attacker", ship=attacker,
        entry_origin=Vector2(0.0, 0.0), entry_facing=0.0,
        task_force_id="tf-attacker", squadron_id="sq-attacker",
    )
    team_target = _one_ship_team(
        team_id=1, team_name="Target", ship=target,
        entry_origin=Vector2(float(scenario.distance), 0.0),
        entry_facing=180.0,
        task_force_id="tf-target", squadron_id="sq-target",
    )
    return _make_spec(scenario=scenario, teams=(team_attacker, team_target))


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _to_core_vector(v) -> Vector2:
    """Coerce a pygame.Vector2-ish value to `game.core.math.Vector2`."""
    if isinstance(v, Vector2):
        return v
    # pygame.math.Vector2 exposes .x / .y.
    return Vector2(float(getattr(v, "x", 0.0)), float(getattr(v, "y", 0.0)))


# ---------------------------------------------------------------------------
# Monkey-patch TestScenario.to_spec to delegate to the compiler.
# ---------------------------------------------------------------------------
#
# Keeping the base-class method ergonomic — any scenario can call
# `scenario.to_spec(registries)` without the caller importing
# `build_test_battle_spec`. Subclasses that need a custom translation
# override `to_spec()` directly.
def _to_spec(self: TestScenario, registries=None) -> BattleSpec:
    return build_test_battle_spec(self, registries)


TestScenario.to_spec = _to_spec  # type: ignore[attr-defined]


__all__ = [
    "build_test_battle_spec",
    # Public helpers for custom scenarios that subclass `TestScenario`
    # directly (not one of the five canonical templates) and need to
    # build a `BattleSpec` in their own `to_spec()` override.
    "make_ship_spec",
    "make_one_ship_team",
    "make_battle_spec",
    "make_single_ship_custom_formation",
]


# Public aliases for the private helpers above — callers that need to
# build a custom spec (e.g. `tohit_attack_fleet_scenarios.py`'s
# multi-provider sensor tests) use these without reaching into the
# compiler's internals.
make_ship_spec = _ship_spec
make_one_ship_team = _one_ship_team
make_battle_spec = _make_spec
make_single_ship_custom_formation = _single_ship_custom_formation
