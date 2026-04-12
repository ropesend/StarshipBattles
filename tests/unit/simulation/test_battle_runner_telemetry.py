"""Tests for `run_battle` telemetry wiring (PROJ-269 Phase 5 Task 5.4).

`run_battle` attaches aggregators based on `BattleSpec.telemetry_level`:
  - MINIMAL: no aggregators; `ShipOutcome.weapons == ()`,
    `hits_taken == ()`, `stats` zeroed.
  - NORMAL: `WeaponSummaryAggregator` + `ShipStatsAggregator` attached;
    `weapons` + `stats` populated in outcome; `hits_taken == ()`.
  - DETAILED: NORMAL + `HitLogRecorder`; `hits_taken` may be populated.
"""
from typing import Callable

import pytest

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
from game.simulation.combat.modifier_stack import ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_serialization import ShipSerializer
from game.simulation.systems.battle_end_conditions import TickLimitCondition


def _design() -> dict:
    return {
        "name": "TelemetryCruiser",
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


def _make_spec(level: TelemetryLevel) -> BattleSpec:
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
    return BattleSpec(
        seed=42,
        telemetry_level=level,
        boundary=None,
        end_condition=TickLimitCondition(max_ticks=3),
        absolute_max_ticks=100,
        teams=(_team(0, ship_a), _team(1, ship_b)),
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )


# ---------------------------------------------------------------------------
# MINIMAL telemetry
# ---------------------------------------------------------------------------


def test_minimal_telemetry_empty_weapons_and_hit_log(ship_builder):
    spec = _make_spec(TelemetryLevel.MINIMAL)
    outcome: BattleOutcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )
    for team in outcome.teams:
        for ship in team.ships:
            assert ship.weapons == (), (
                f"MINIMAL must produce empty weapons, got {ship.weapons}"
            )
            assert ship.hits_taken == ()


def test_minimal_telemetry_ship_stats_zero(ship_builder):
    spec = _make_spec(TelemetryLevel.MINIMAL)
    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )
    for team in outcome.teams:
        for ship in team.ships:
            assert ship.stats.total_damage_taken == 0.0
            assert ship.stats.peak_speed == 0.0
            assert ship.stats.ticks_alive == 0
            assert ship.stats.ticks_derelict == 0


# ---------------------------------------------------------------------------
# NORMAL telemetry
# ---------------------------------------------------------------------------


def test_normal_telemetry_weapon_summaries_populated(ship_builder):
    spec = _make_spec(TelemetryLevel.NORMAL)
    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )
    # Each ship has one laser_cannon so each outcome should have a
    # single WeaponSummary entry.
    for team in outcome.teams:
        for ship in team.ships:
            assert len(ship.weapons) == 1
            assert ship.weapons[0].component_id == "laser_cannon"


def test_normal_telemetry_ship_stats_populated(ship_builder):
    spec = _make_spec(TelemetryLevel.NORMAL)
    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )
    for team in outcome.teams:
        for ship in team.ships:
            # Ran 3 ticks → ticks_alive should be >= 1 for alive ships.
            if ship.status.value in ("survived", "derelict"):
                assert ship.stats.ticks_alive >= 1


def test_normal_telemetry_hits_taken_empty(ship_builder):
    """NORMAL populates weapons + stats but NOT hits_taken."""
    spec = _make_spec(TelemetryLevel.NORMAL)
    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )
    for team in outcome.teams:
        for ship in team.ships:
            assert ship.hits_taken == ()


# ---------------------------------------------------------------------------
# DETAILED telemetry
# ---------------------------------------------------------------------------


def test_detailed_telemetry_all_fields_populated(ship_builder):
    """At DETAILED, weapons + stats populated + hits_taken MAY be non-empty.
    Given ships are far apart and only 3 ticks, hits may or may not
    occur — we just assert the aggregator was active (weapons non-empty,
    stats non-zero ticks_alive) and the hit log type is a tuple."""
    spec = _make_spec(TelemetryLevel.DETAILED)
    outcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )
    for team in outcome.teams:
        for ship in team.ships:
            assert len(ship.weapons) == 1
            assert isinstance(ship.hits_taken, tuple)
            # stats still populated
            if ship.status.value in ("survived", "derelict"):
                assert ship.stats.ticks_alive >= 1
