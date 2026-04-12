"""Tests for the Combat Lab spec compiler (PROJ-269 Phase 1 Task 1.7).

Covers:
- `build_test_battle_spec(scenario, registries)` returns a `BattleSpec`
- For a `StaticTargetScenario` subclass: 2 teams, expected ship counts
- Seed from `scenario.metadata.seed` placed in `BattleSpec.seed`
- `telemetry_level` defaults to DETAILED for Combat Lab
- `end_condition` comes from `scenario._create_end_condition()`
- Boundary is `UnboundedRegion`
- Empty `ModifierStack`
- `TestScenario.to_spec(registries)` base method delegates
"""
import pytest

from combat_lab.scenarios.base import TestMetadata, TestScenario
from combat_lab.scenarios.templates import StaticTargetScenario
from combat_lab.spec_compiler import build_test_battle_spec
from game.simulation.battle_spec import BattleSpec
from game.simulation.combat.boundary import UnboundedRegion
from game.simulation.combat.modifier_stack import ModifierStack
from game.simulation.combat.telemetry import TelemetryLevel
from game.simulation.systems.battle_end_conditions import TickLimitCondition


# ---------------------------------------------------------------------------
# Fixtures — a minimal static-target scenario that does not require loading
# real ship JSON. Uses Task 1.7's documented pattern of ship refs as
# filenames. Phase 1's compiler does NOT actually load the ship files
# (that happens at run_battle time via the injected ship_builder).
# ---------------------------------------------------------------------------


class _MinimalStaticScenario(StaticTargetScenario):
    metadata = TestMetadata(
        test_id="SPEC-TEST-001",
        category="SpecCompiler",
        subcategory="Basic",
        name="Minimal static scenario for spec compiler",
        summary="Asserts the compiler can translate a StaticTargetScenario.",
        conditions=["Distance: 500"],
        edge_cases=[],
        expected_outcome="Spec built",
        pass_criteria="Teams = 2, ship counts correct",
        max_ticks=100,
        seed=314,
    )
    attacker_ship = "Test_Attacker_Beam360_High.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 500
    attacker_angle = 0.0
    target_angle = 0.0

    def validate(self, engine):
        return []


# ---------------------------------------------------------------------------
# Compiler output
# ---------------------------------------------------------------------------


def test_compiler_returns_battle_spec():
    scenario = _MinimalStaticScenario()
    spec = build_test_battle_spec(scenario, registries=None)
    assert isinstance(spec, BattleSpec)


def test_compiler_produces_two_teams_with_one_ship_each():
    scenario = _MinimalStaticScenario()
    spec = build_test_battle_spec(scenario, registries=None)
    assert len(spec.teams) == 2

    def ship_count(team) -> int:
        total = 0
        for tf in team.fleet_hierarchy:
            for sq in tf.squadrons:
                total += len(sq.ships)
        return total

    assert ship_count(spec.teams[0]) == 1  # attacker on team 0
    assert ship_count(spec.teams[1]) == 1  # target on team 1


def test_compiler_places_seed_from_metadata():
    scenario = _MinimalStaticScenario()
    spec = build_test_battle_spec(scenario, registries=None)
    assert spec.seed == 314


def test_compiler_defaults_to_detailed_telemetry():
    scenario = _MinimalStaticScenario()
    spec = build_test_battle_spec(scenario, registries=None)
    assert spec.telemetry_level == TelemetryLevel.DETAILED


def test_compiler_builds_tick_limit_end_condition_from_metadata():
    scenario = _MinimalStaticScenario()
    spec = build_test_battle_spec(scenario, registries=None)
    # Default for scenarios without explicit metadata.end_condition is
    # TickLimitCondition(max_ticks=metadata.max_ticks).
    assert isinstance(spec.end_condition, TickLimitCondition)
    assert spec.end_condition.max_ticks == 100


def test_compiler_uses_unbounded_region():
    scenario = _MinimalStaticScenario()
    spec = build_test_battle_spec(scenario, registries=None)
    assert isinstance(spec.boundary, UnboundedRegion)


def test_compiler_builds_empty_modifier_stack():
    scenario = _MinimalStaticScenario()
    spec = build_test_battle_spec(scenario, registries=None)
    assert isinstance(spec.modifier_stack, ModifierStack)
    assert spec.modifier_stack.global_ == ()
    assert len(spec.modifier_stack.per_team) == 0


def test_compiler_ships_carry_spec_filename_and_pose():
    scenario = _MinimalStaticScenario()
    spec = build_test_battle_spec(scenario, registries=None)
    attacker = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    target = spec.teams[1].fleet_hierarchy[0].squadrons[0].ships[0]
    # design_id carries the JSON filename so the runner's ship_builder
    # can call _load_ship(design_id) to materialize each Ship.
    assert attacker.design_id == "Test_Attacker_Beam360_High.json"
    assert target.design_id == "Test_Target_Stationary.json"
    # Positions per StaticTargetScenario template logic.
    assert attacker.position.x == 0.0
    assert attacker.position.y == 0.0
    assert target.position.x == 500.0
    assert target.position.y == 0.0


def test_compiler_assigns_unique_instance_ids():
    scenario = _MinimalStaticScenario()
    spec = build_test_battle_spec(scenario, registries=None)
    ids = []
    for team in spec.teams:
        for tf in team.fleet_hierarchy:
            for sq in tf.squadrons:
                for ship in sq.ships:
                    ids.append(ship.instance_id)
    # At least 2 ships, each with a unique id.
    assert len(ids) == len(set(ids))
    assert len(ids) == 2


# ---------------------------------------------------------------------------
# TestScenario.to_spec base method
# ---------------------------------------------------------------------------


def test_test_scenario_to_spec_delegates_to_compiler():
    scenario = _MinimalStaticScenario()
    spec_via_method = scenario.to_spec(registries=None)
    spec_direct = build_test_battle_spec(scenario, registries=None)
    # Both paths should produce equivalent specs (same seed, same ship
    # counts, same end condition).
    assert spec_via_method.seed == spec_direct.seed
    assert len(spec_via_method.teams) == len(spec_direct.teams)
    assert isinstance(spec_via_method.end_condition, TickLimitCondition)


# ---------------------------------------------------------------------------
# Unsupported scenario types raise a clear error
# ---------------------------------------------------------------------------


class _RawScenario(TestScenario):
    metadata = TestMetadata(
        test_id="RAW-001",
        category="Raw",
        subcategory="Raw",
        name="Raw",
        summary="",
        conditions=[],
        edge_cases=[],
        expected_outcome="",
        pass_criteria="",
    )

    def setup(self, battle_engine):
        pass

    def validate(self, engine):
        return []


def test_compiler_raises_on_unsupported_scenario_type():
    scenario = _RawScenario()
    with pytest.raises(NotImplementedError):
        build_test_battle_spec(scenario, registries=None)
