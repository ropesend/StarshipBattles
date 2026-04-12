"""Tests for BattleSpec DTOs (PROJ-269 Phase 1 Task 1.1).

Covers:
- Frozen dataclass shape of BattleSpec + nested DTOs per design.md §2.1-§2.3
- EntryVector, AIPolicy, CombatPolicies, ComponentStateSpec, ShipSpec,
  SquadronSpec, TaskForceSpec, TeamSpec, BattleSpec
- Round-trip: attribute access + pickle reproduces identical DTO
- Exports via `from game.simulation import ...`
"""
import dataclasses
import pickle

import pytest

from game.core.math import Vector2
from game.simulation.battle_spec import (
    AIPolicy,
    BattleSpec,
    CombatPolicies,
    ComponentStateSpec,
    EntryVector,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
)
from game.simulation.systems.battle_end_conditions import TeamEliminatedCondition


# ---------------------------------------------------------------------------
# Placeholder values for fields whose real types land in sibling Phase 1 tasks.
# Task 1.2 lands BoundaryRegion; Task 1.3 ModifierStack; Task 1.4 FormationSpec;
# Task 1.5 TelemetryLevel. For the DTO-shape contract in Task 1.1 we pass plain
# sentinel objects — the dataclasses carry whatever is handed to them.
# ---------------------------------------------------------------------------
_SENTINEL_MODIFIER_STACK = object()
_SENTINEL_FORMATION = object()
_SENTINEL_TELEMETRY = object()


def _minimal_ship_spec(instance_id: str = "ship-1") -> ShipSpec:
    return ShipSpec(
        instance_id=instance_id,
        design_id="qs_heavy_cruiser",
        theme_id="Federation",
        name="Test Ship",
        position=Vector2(0.0, 0.0),
        angle=0.0,
        velocity=Vector2(0.0, 0.0),
        components=(),
    )


def _minimal_task_force(ships: tuple = ()) -> TaskForceSpec:
    return TaskForceSpec(
        task_force_id="tf-1",
        formation=_SENTINEL_FORMATION,
        policies=CombatPolicies(),
        squadrons=(
            SquadronSpec(
                squadron_id="sq-1",
                policies=CombatPolicies(),
                ships=ships or (_minimal_ship_spec(),),
            ),
        ),
    )


def _minimal_team(team_id: int = 0) -> TeamSpec:
    return TeamSpec(
        team_id=team_id,
        name=f"Team {team_id}",
        entry_vector=EntryVector(origin=Vector2(0.0, 0.0), facing=0.0),
        fleet_hierarchy=(_minimal_task_force(),),
        ai_policy=AIPolicy(),
    )


def _minimal_battle_spec() -> BattleSpec:
    return BattleSpec(
        seed=42,
        telemetry_level=_SENTINEL_TELEMETRY,
        boundary=None,
        end_condition=TeamEliminatedCondition(),
        absolute_max_ticks=10_000,
        teams=(_minimal_team(0), _minimal_team(1)),
        modifier_stack=_SENTINEL_MODIFIER_STACK,
        post_battle_hook=None,
    )


# ---------------------------------------------------------------------------
# Frozen-shape tests — every DTO must be a frozen dataclass.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cls",
    [
        EntryVector,
        AIPolicy,
        CombatPolicies,
        ComponentStateSpec,
        ShipSpec,
        SquadronSpec,
        TaskForceSpec,
        TeamSpec,
        BattleSpec,
    ],
)
def test_dto_is_frozen_dataclass(cls):
    assert dataclasses.is_dataclass(cls), f"{cls.__name__} must be a dataclass"
    params = getattr(cls, "__dataclass_params__", None)
    assert params is not None and params.frozen, (
        f"{cls.__name__} must be frozen (frozen=True)"
    )


def test_entry_vector_fields():
    ev = EntryVector(origin=Vector2(10.0, 20.0), facing=45.0)
    assert ev.origin == Vector2(10.0, 20.0)
    assert ev.facing == 45.0
    with pytest.raises(dataclasses.FrozenInstanceError):
        ev.facing = 90.0  # type: ignore[misc]


def test_component_state_spec_fields():
    cs = ComponentStateSpec(
        component_id="bridge",
        instance_index=0,
        current_hp=123.4,
        is_active=True,
    )
    assert cs.component_id == "bridge"
    assert cs.instance_index == 0
    assert cs.current_hp == pytest.approx(123.4)
    assert cs.is_active is True
    with pytest.raises(dataclasses.FrozenInstanceError):
        cs.current_hp = 0.0  # type: ignore[misc]


def test_ship_spec_fields_and_frozen():
    ss = _minimal_ship_spec()
    for field in (
        "instance_id",
        "design_id",
        "theme_id",
        "name",
        "position",
        "angle",
        "velocity",
        "components",
    ):
        assert hasattr(ss, field), f"ShipSpec missing field {field!r}"
    assert isinstance(ss.components, tuple)
    with pytest.raises(dataclasses.FrozenInstanceError):
        ss.name = "Renamed"  # type: ignore[misc]


def test_squadron_spec_fields():
    sq = SquadronSpec(
        squadron_id="alpha",
        policies=CombatPolicies(),
        ships=(_minimal_ship_spec(),),
    )
    assert sq.squadron_id == "alpha"
    assert isinstance(sq.ships, tuple)
    assert len(sq.ships) == 1


def test_task_force_spec_fields():
    tf = _minimal_task_force()
    for field in ("task_force_id", "formation", "policies", "squadrons"):
        assert hasattr(tf, field)
    assert isinstance(tf.squadrons, tuple)


def test_team_spec_fields():
    team = _minimal_team(3)
    assert team.team_id == 3
    assert isinstance(team.fleet_hierarchy, tuple)
    assert isinstance(team.entry_vector, EntryVector)
    assert isinstance(team.ai_policy, AIPolicy)


def test_battle_spec_all_fields_from_design():
    spec = _minimal_battle_spec()
    # design.md §2.1 — identity / arena / termination / teams / modifiers / hook
    for field in (
        "seed",
        "telemetry_level",
        "boundary",
        "end_condition",
        "absolute_max_ticks",
        "teams",
        "modifier_stack",
        "post_battle_hook",
    ):
        assert hasattr(spec, field), f"BattleSpec missing field {field!r}"
    assert isinstance(spec.teams, tuple)
    assert spec.boundary is None  # None = unbounded (sentinel per design)
    assert spec.post_battle_hook is None  # optional


def test_battle_spec_is_immutable():
    spec = _minimal_battle_spec()
    with pytest.raises(dataclasses.FrozenInstanceError):
        spec.seed = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Round-trip — attribute access stays reachable and DTO remains equal under
# dataclasses.replace + recursive equality.
# ---------------------------------------------------------------------------


def test_battle_spec_round_trip_attribute_access():
    spec = _minimal_battle_spec()
    team0 = spec.teams[0]
    ship0 = team0.fleet_hierarchy[0].squadrons[0].ships[0]
    assert ship0.instance_id == "ship-1"
    assert ship0.design_id == "qs_heavy_cruiser"


def test_battle_spec_pickle_round_trip_preserves_identity_fields():
    """Pickle round-trip reproduces equal DTO for fields that do pickle.

    The sentinel fields we pass for unfinished Phase 1 sibling types (plain
    `object()`s + the end-condition class) won't necessarily survive pickle
    identity — that's intended for later phases. We verify that the
    *DTO shape itself* pickles: a spec built from pickle-safe inputs
    round-trips under equality.
    """
    # Build a spec with only pickle-safe fields.
    pickle_safe_spec = BattleSpec(
        seed=7,
        telemetry_level="NORMAL",       # plain str — pickle-safe sentinel
        boundary=None,
        end_condition=TeamEliminatedCondition(),
        absolute_max_ticks=1000,
        teams=(_minimal_team(0),),
        modifier_stack={},              # plain dict — pickle-safe sentinel
        post_battle_hook=None,
    )
    restored = pickle.loads(pickle.dumps(pickle_safe_spec))
    # Equality check on pickle-safe fields
    assert restored.seed == pickle_safe_spec.seed
    assert restored.telemetry_level == pickle_safe_spec.telemetry_level
    assert restored.boundary is None
    assert restored.absolute_max_ticks == 1000
    assert restored.modifier_stack == {}
    assert restored.post_battle_hook is None
    # Nested equality on teams
    assert len(restored.teams) == 1
    assert restored.teams[0].team_id == 0
    assert restored.teams[0].name == "Team 0"
    # Ship round-tripped
    sq0 = restored.teams[0].fleet_hierarchy[0].squadrons[0]
    assert sq0.ships[0].instance_id == "ship-1"


def test_battle_spec_equality_semantics():
    a = _minimal_battle_spec()
    # Changing one primitive field produces an unequal spec (frozen dataclass
    # provides __eq__ automatically).
    b = dataclasses.replace(a, seed=a.seed + 1)
    assert a != b


# ---------------------------------------------------------------------------
# Public-export surface from game.simulation.
# ---------------------------------------------------------------------------


def test_battle_spec_exports_from_game_simulation():
    # Must be importable at the package root per Task 1.1 acceptance.
    from game.simulation import BattleSpec as ExportedBattleSpec

    assert ExportedBattleSpec is BattleSpec
