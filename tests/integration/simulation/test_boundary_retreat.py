"""End-to-end integration test for boundary RETREAT policy (PROJ-269 Phase 3 Task 3.7).

Confirms the full `BattleSpec → run_battle → BattleOutcome` pipeline
carries a boundary through, enforces it per-tick, and reports retreated
ships with `ShipStatus.RETREATED`.
"""
from game.ai.ai_factory import AIControllerFactory
from game.core.math import Vector2
from game.simulation.battle_outcome import BattleOutcome, ShipStatus
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
from game.simulation.combat.boundary import RectBoundary, ExitPolicy
from game.simulation.combat.modifier_stack import ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.entities.ship_serialization import ShipSerializer
from game.simulation.systems.battle_end_conditions import TickLimitCondition


def _design() -> dict:
    return {
        "name": "Cruiser",
        "ship_class": "Escort",
        "vehicle_type": "Ship",
        "design_role": "fleet_escort",
        "theme_id": "Federation",
        "layers": {
            "CORE": [{"id": "bridge"}],
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


def test_ship_outside_retreat_boundary_is_marked_retreated(fresh_registries):
    """Ship starts outside the RETREAT boundary → `status=RETREATED`
    in the outcome."""

    def ship_builder(ship_spec):
        ship = ShipSerializer.from_dict(_design(), registries=fresh_registries)
        ship.instance_id = ship_spec.instance_id
        return ship

    # Boundary is a small rect; ship_a starts WAY outside it.
    boundary = RectBoundary(width=500.0, height=500.0, exit_policy=ExitPolicy.RETREAT)
    ship_a_outside = ShipSpec(
        instance_id="outside",
        design_id="Cruiser",
        theme_id="Federation",
        name="Outside",
        position=Vector2(5000.0, 0.0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )
    ship_b_inside = ShipSpec(
        instance_id="inside",
        design_id="Cruiser",
        theme_id="Federation",
        name="Inside",
        position=Vector2(0.0, 0.0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )

    spec = BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=boundary,
        end_condition=TickLimitCondition(max_ticks=5),
        absolute_max_ticks=100,
        teams=(_team(0, ship_a_outside), _team(1, ship_b_inside)),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )

    outcome: BattleOutcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )

    # Ship outside boundary should be marked RETREATED.
    outside_outcome = next(
        s for team in outcome.teams
        for s in team.ships
        if s.instance_id == "outside"
    )
    assert outside_outcome.status == ShipStatus.RETREATED, (
        f"Expected RETREATED, got {outside_outcome.status}"
    )

    # Ship inside boundary should NOT be RETREATED.
    inside_outcome = next(
        s for team in outcome.teams
        for s in team.ships
        if s.instance_id == "inside"
    )
    assert inside_outcome.status != ShipStatus.RETREATED


def test_unbounded_region_never_marks_ships_retreated(fresh_registries):
    """With `boundary=None` (unbounded), nobody should be retreated —
    regression gate for the 2-team common case."""

    def ship_builder(ship_spec):
        ship = ShipSerializer.from_dict(_design(), registries=fresh_registries)
        ship.instance_id = ship_spec.instance_id
        return ship

    far = ShipSpec(
        instance_id="far",
        design_id="Cruiser",
        theme_id="Federation",
        name="Far",
        position=Vector2(1e9, 0.0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )
    near = ShipSpec(
        instance_id="near",
        design_id="Cruiser",
        theme_id="Federation",
        name="Near",
        position=Vector2(0.0, 0.0),
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )

    spec = BattleSpec(
        seed=1,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=3),
        absolute_max_ticks=100,
        teams=(_team(0, far), _team(1, near)),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )

    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )
    for team in outcome.teams:
        for s in team.ships:
            assert s.status != ShipStatus.RETREATED
