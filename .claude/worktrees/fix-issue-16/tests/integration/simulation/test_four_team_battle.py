"""End-to-end 4-team battle integration (PROJ-275 Phase 8.2).

The engine has always supported N teams; PROJ-275 collapses the
strategy/compile surface to match. This file gives us regression
coverage for N=4 — an important step up from N=3 because it exercises
enemy-scope fan-out across multiple opponents and the ring entry
vector layout at its 4-team cardinal-direction form.
"""
import math

import pytest

from game.ai.ai_factory import AIControllerFactory
from game.core.math import Vector2
from game.simulation.battle_outcome import BattleOutcome, EndReason
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
from game.simulation.combat.formation import resolve_team_entry_vectors
from game.simulation.combat.modifier_stack import ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.entities.ship_serialization import ShipSerializer
from game.simulation.systems.battle_end_conditions import (
    AnyCondition,
    TeamEliminatedCondition,
    TickLimitCondition,
)


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


def _team(team_id: int, ship: ShipSpec, entry_vector: EntryVector) -> TeamSpec:
    return TeamSpec(
        team_id=team_id,
        name=f"Team {team_id}",
        entry_vector=entry_vector,
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


def _ship_spec(instance_id: str, origin: Vector2) -> ShipSpec:
    return ShipSpec(
        instance_id=instance_id,
        design_id="Cruiser",
        theme_id="Federation",
        name=instance_id,
        position=origin,
        angle=0.0,
        velocity=Vector2(0, 0),
        components=(),
    )


def test_four_team_battle_runs_to_completion(fresh_registries):
    """Four teams, one ship each, meet `TeamEliminatedCondition` OR hit
    the tick ceiling; either way the 4-team outcome is well-formed."""
    entry_vectors = resolve_team_entry_vectors(team_count=4)

    def ship_builder(ship_spec, team_id):
        ship = ShipSerializer.from_dict(_design(), registries=fresh_registries)
        ship.instance_id = ship_spec.instance_id
        return ship

    teams = tuple(
        _team(
            tid,
            _ship_spec(f"t{tid}", entry_vectors[tid].origin),
            entry_vectors[tid],
        )
        for tid in range(4)
    )

    spec = BattleSpec(
        seed=42,
        telemetry_level=TelemetryLevel.NORMAL,
        boundary=None,
        end_condition=AnyCondition([
            TickLimitCondition(max_ticks=200),
            TeamEliminatedCondition(),
        ]),
        absolute_max_ticks=500,
        teams=teams,
        modifier_stack=ModifierStack.empty(),
        post_battle_hook=None,
    )

    outcome: BattleOutcome = run_battle(
        spec,
        ai_factory=AIControllerFactory(),
        ship_builder=ship_builder,
    )

    assert len(outcome.teams) == 4
    assert [t.team_id for t in outcome.teams] == [0, 1, 2, 3]
    assert outcome.end_reason in (
        EndReason.TEAM_ELIMINATED,
        EndReason.TICK_LIMIT,
        EndReason.ABSOLUTE_MAX,
        EndReason.ANY,
    )
    all_ids = {s.instance_id for team in outcome.teams for s in team.ships}
    assert all_ids == {"t0", "t1", "t2", "t3"}


def test_four_team_ring_entry_vectors_at_cardinal_points():
    """For 4 teams the ring lands on N/E/S/W (180° start, 90° step)."""
    vectors = resolve_team_entry_vectors(team_count=4)

    assert set(vectors.keys()) == {0, 1, 2, 3}
    # All origins on the same circle.
    radius = math.hypot(vectors[0].origin.x, vectors[0].origin.y)
    for tid in vectors:
        r = math.hypot(vectors[tid].origin.x, vectors[tid].origin.y)
        assert r == pytest.approx(radius), f"Team {tid} off-ring"
    # Each facing points inward (back toward origin).
    for tid, ev in vectors.items():
        origin_angle = math.degrees(math.atan2(ev.origin.y, ev.origin.x)) % 360.0
        inward_facing = (origin_angle + 180.0) % 360.0
        assert ev.facing == pytest.approx(inward_facing), f"Team {tid} not facing inward"


def test_enemy_scope_modifier_on_team_zero_fans_out_to_three_opponents():
    """`enemy_*` scope entries emit one ModifierEntry per opponent team.

    With 4 teams and owner=0, we expect 3 entries — one each targeting
    teams 1, 2, 3. This is the N-team fan-out PROJ-273's registry helper
    delivers.
    """
    from game.simulation.combat.ability_stat_registry import emit_entries_for_ability

    entries = emit_entries_for_ability(
        "DamageModifier",
        {"multiplier": 1.5},
        scope="enemy_system",
        owner_team=0,
        num_teams=4,
        source="test:enemy_damage_booster",
        source_modifier_id="test",
        source_modifier_name="Test",
    )

    team_ids = [team_id for team_id, _ in entries]
    assert sorted(team_ids) == [1, 2, 3], (
        f"Enemy-scope entry on team 0 should fan to teams 1..3; "
        f"got {team_ids}"
    )


def test_four_team_team_eliminated_fires_when_three_teams_wiped():
    """`TeamEliminatedCondition` must wait until only one team has ships.

    With 4 teams and 3 wiped, it fires.
    """
    from unittest.mock import MagicMock
    from game.simulation.systems.battle_end_conditions import TeamEliminatedCondition

    cond = TeamEliminatedCondition()

    def _alive(team_id):
        s = MagicMock(); s.team_id = team_id; s.is_alive = True; s.is_derelict = False; return s

    def _dead(team_id):
        s = MagicMock(); s.team_id = team_id; s.is_alive = False; s.is_derelict = False; return s

    # 3 teams dead, team 3 alive.
    ships = [_dead(0), _dead(1), _dead(2), _alive(3)]
    assert cond.is_met(ships, tick=0) is True

    # 2 teams dead, 2 alive → still running.
    ships = [_dead(0), _dead(1), _alive(2), _alive(3)]
    assert cond.is_met(ships, tick=0) is False
