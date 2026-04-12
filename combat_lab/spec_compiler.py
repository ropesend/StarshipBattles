"""Combat Lab spec compiler — TestScenario → BattleSpec.

Introduced by PROJ-269 Phase 1 Task 1.7. Translates a Combat Lab
`TestScenario` into a `BattleSpec` that `run_battle(spec)` can execute.

Phase 1 scope:
  - Supports `StaticTargetScenario` subclasses only. Other templates
    (DuelScenario, PropulsionScenario, ResourceScenario, ComparisonScenario)
    need their own `to_spec()` overrides when they migrate — the base
    compiler raises `NotImplementedError` until those overrides land.
  - The compiler records each ship's loader filename as `ShipSpec.design_id`.
    Materialization is deferred to a `ship_builder` closure supplied by
    Task 1.10's Combat Lab runner integration (the runner knows how to
    call `scenario._load_ship(design_id)`).
  - Formation resolver is NOT used yet — positions come straight from the
    template's configured pose (`StaticTargetScenario` places attacker at
    origin, target at `(distance, 0)`). Phase 4 switches to
    FormationResolver.
  - `boundary` = `UnboundedRegion()` — Combat Lab tests are unbounded today.
  - `modifier_stack` = `ModifierStack.empty()` — test scenarios don't use
    modifiers today.
  - `telemetry_level` = `DETAILED` — Combat Lab needs the full hit log.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from combat_lab.scenarios.base import TestScenario
from combat_lab.scenarios.templates import StaticTargetScenario
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


def build_test_battle_spec(
    scenario: TestScenario,
    registries: Optional["GameRegistries"],
) -> BattleSpec:
    """Compile a `TestScenario` into a `BattleSpec`.

    Args:
        scenario: The TestScenario subclass instance. Phase 1 supports
            `StaticTargetScenario` subclasses only.
        registries: Loaded registries for the scenario's test data.
            Unused in Phase 1 (ship materialization happens later in
            Task 1.10's runner), but the signature matches Tasks 1.8/1.9
            for parallel conceptual shape.

    Returns:
        A fully-populated `BattleSpec`. The caller (typically
        `combat_lab/runner.py` via Task 1.10's flag path) supplies the
        `ship_builder` closure when calling `run_battle`.

    Raises:
        NotImplementedError: if the scenario's template is not supported
            in Phase 1. The migration of DuelScenario / PropulsionScenario /
            ResourceScenario / ComparisonScenario happens in later phases.
    """
    # Touch registries to mark it intentionally unused in Phase 1.
    _ = registries

    if not isinstance(scenario, StaticTargetScenario):
        raise NotImplementedError(
            f"Combat Lab spec compiler does not yet support "
            f"{type(scenario).__name__}. Phase 1 supports "
            f"StaticTargetScenario subclasses only; other template "
            f"migrations land in later phases."
        )

    # Validate required attrs — mirrors the checks StaticTargetScenario.setup
    # performs, raised here so the compiler fails loudly if a subclass forgot
    # to configure them.
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

    attacker_ship_spec = ShipSpec(
        instance_id=f"{scenario.metadata.test_id}:attacker",
        design_id=scenario.attacker_ship,
        theme_id="Federation",
        name=f"{scenario.metadata.test_id}-attacker",
        position=Vector2(0.0, 0.0),
        angle=float(scenario.attacker_angle),
        velocity=Vector2(0.0, 0.0),
        components=(),
    )
    target_ship_spec = ShipSpec(
        instance_id=f"{scenario.metadata.test_id}:target",
        design_id=scenario.target_ship,
        theme_id="Federation",
        name=f"{scenario.metadata.test_id}-target",
        position=Vector2(float(scenario.distance), 0.0),
        angle=float(scenario.target_angle),
        velocity=Vector2(0.0, 0.0),
        components=(),
    )

    # PROJ-269 Phase 4: explicit CUSTOM formations so the resolver can
    # reproduce the scenario's positions from the spec alone. Each
    # single-ship TaskForce gets a single custom position in its own
    # local frame (origin), since the team's entry_vector already
    # places the formation in world space.
    attacker_formation = FormationSpec(
        shape=FormationShape.CUSTOM,
        spacing=100.0,
        custom_positions=(Vector2(0.0, 0.0),),
    )
    target_formation = FormationSpec(
        shape=FormationShape.CUSTOM,
        spacing=100.0,
        custom_positions=(Vector2(0.0, 0.0),),
    )

    team_attacker = TeamSpec(
        team_id=0,
        name="Attacker",
        entry_vector=EntryVector(origin=Vector2(0.0, 0.0), facing=0.0),
        fleet_hierarchy=(
            TaskForceSpec(
                task_force_id="tf-attacker",
                formation=attacker_formation,
                policies=CombatPolicies(),
                squadrons=(
                    SquadronSpec(
                        squadron_id="sq-attacker",
                        policies=CombatPolicies(),
                        ships=(attacker_ship_spec,),
                    ),
                ),
            ),
        ),
        ai_policy=AIPolicy(),
    )
    team_target = TeamSpec(
        team_id=1,
        name="Target",
        entry_vector=EntryVector(
            origin=Vector2(float(scenario.distance), 0.0),
            facing=180.0,
        ),
        fleet_hierarchy=(
            TaskForceSpec(
                task_force_id="tf-target",
                formation=target_formation,
                policies=CombatPolicies(),
                squadrons=(
                    SquadronSpec(
                        squadron_id="sq-target",
                        policies=CombatPolicies(),
                        ships=(target_ship_spec,),
                    ),
                ),
            ),
        ),
        ai_policy=AIPolicy(),
    )

    # Safety ceiling — 10x the scenario's max_ticks. The scenario's
    # end_condition fires at metadata.max_ticks in the common case; the
    # ceiling is only relevant when callers wire composite conditions.
    absolute_max = max(scenario.metadata.max_ticks * 10, 1000)

    return BattleSpec(
        seed=scenario.metadata.seed,
        telemetry_level=TelemetryLevel.DETAILED,
        boundary=UnboundedRegion(),
        end_condition=scenario._create_end_condition(),
        absolute_max_ticks=absolute_max,
        teams=(team_attacker, team_target),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )


# ---------------------------------------------------------------------------
# Monkey-patch TestScenario.to_spec to delegate to the compiler.
# ---------------------------------------------------------------------------
#
# Keeping the base-class method ergonomic — any scenario can call
# `scenario.to_spec(registries)` without the caller importing
# `build_test_battle_spec`. Subclasses that need a custom translation
# (DuelScenario in Phase 4, etc.) override `to_spec()` directly.
def _to_spec(self: TestScenario, registries=None) -> BattleSpec:
    return build_test_battle_spec(self, registries)


TestScenario.to_spec = _to_spec  # type: ignore[attr-defined]


__all__ = ["build_test_battle_spec"]
