"""Tests for the Combat Lab spec compiler (PROJ-269 Phase 1 Task 1.7 + Phase 6 Task 6.7a).

Covers:
- `build_test_battle_spec(scenario, registries)` returns a `BattleSpec`
- For a `StaticTargetScenario` subclass: 2 teams, expected ship counts
- Seed from `scenario.metadata.seed` placed in `BattleSpec.seed`
- `telemetry_level` defaults to DETAILED for Combat Lab
- `end_condition` comes from `scenario._create_end_condition()`
- Boundary is `UnboundedRegion`
- Empty `ModifierStack`
- `TestScenario.to_spec(registries)` base method delegates

Task 6.7a extensions (all 5 templates):
- `DuelScenario` → 2 teams, 1 ship each, ship1/ship2 roles, ±distance/2 positions
- `PropulsionScenario` → 1 team, single ship, initial_position/velocity/angle
- `ResourceScenario` → 1 team single ship, or 2 teams w/ optional target
- `ComparisonScenario` → variant spec in normal mode, baseline spec in visual-baseline mode
"""
import pygame
import pytest

from combat_lab.scenarios.base import TestMetadata, TestScenario
from combat_lab.scenarios.templates import (
    ComparisonScenario,
    DuelScenario,
    PropulsionScenario,
    ResourceScenario,
    StaticTargetScenario,
)
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


# ---------------------------------------------------------------------------
# Phase 5 Task 5.6: metadata.telemetry_level override
# ---------------------------------------------------------------------------


def test_compiler_respects_metadata_telemetry_level_override():
    class _MinimalLevelScenario(_MinimalStaticScenario):
        metadata = TestMetadata(
            test_id="SPEC-MINIMAL-TELEM",
            category="SpecCompiler",
            subcategory="Telemetry",
            name="Minimal-telemetry scenario",
            summary="",
            conditions=[],
            edge_cases=[],
            expected_outcome="",
            pass_criteria="",
            max_ticks=100,
            seed=1,
            telemetry_level="MINIMAL",
        )

    scenario = _MinimalLevelScenario()
    spec = build_test_battle_spec(scenario, registries=None)
    assert spec.telemetry_level == TelemetryLevel.MINIMAL


def test_compiler_metadata_default_telemetry_is_detailed():
    # _MinimalStaticScenario has no telemetry_level set — it's DETAILED by default.
    scenario = _MinimalStaticScenario()
    spec = build_test_battle_spec(scenario, registries=None)
    assert spec.telemetry_level == TelemetryLevel.DETAILED


def test_compiler_unrecognized_telemetry_level_string_falls_back_to_detailed():
    class _GarbledScenario(_MinimalStaticScenario):
        metadata = TestMetadata(
            test_id="SPEC-GARBLED",
            category="SpecCompiler",
            subcategory="Telemetry",
            name="Garbled telemetry string",
            summary="",
            conditions=[],
            edge_cases=[],
            expected_outcome="",
            pass_criteria="",
            max_ticks=100,
            seed=1,
            telemetry_level="HIGHER_THAN_DETAILED",  # unknown
        )

    scenario = _GarbledScenario()
    spec = build_test_battle_spec(scenario, registries=None)
    assert spec.telemetry_level == TelemetryLevel.DETAILED


# ===========================================================================
# Phase 6 Task 6.7a — DuelScenario compiler support
# ===========================================================================


class _MinimalDuelScenario(DuelScenario):
    metadata = TestMetadata(
        test_id="SPEC-DUEL-001",
        category="SpecCompiler",
        subcategory="Duel",
        name="Minimal duel scenario",
        summary="",
        conditions=[],
        edge_cases=[],
        expected_outcome="",
        pass_criteria="",
        max_ticks=200,
        seed=7,
    )
    ship1_file = "Test_Attacker_Beam360_High.json"
    ship2_file = "Test_Target_Stationary.json"
    distance = 400

    def validate(self, engine):
        return []


def test_compiler_supports_duel_scenario_two_teams():
    spec = build_test_battle_spec(_MinimalDuelScenario(), registries=None)
    assert isinstance(spec, BattleSpec)
    assert len(spec.teams) == 2
    # One ship per team.
    assert len(spec.teams[0].fleet_hierarchy[0].squadrons[0].ships) == 1
    assert len(spec.teams[1].fleet_hierarchy[0].squadrons[0].ships) == 1


def test_compiler_duel_positions_ships_at_plus_minus_half_distance():
    spec = build_test_battle_spec(_MinimalDuelScenario(), registries=None)
    ship1 = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    ship2 = spec.teams[1].fleet_hierarchy[0].squadrons[0].ships[0]
    assert ship1.position.x == -200.0
    assert ship1.position.y == 0.0
    assert ship2.position.x == 200.0
    assert ship2.position.y == 0.0
    assert ship1.angle == 0.0
    assert ship2.angle == 180.0


def test_compiler_duel_ships_carry_scenario_role():
    """PROJ-278 Phase 4: scenario_role field is the typed role tag.
    `instance_id` retains the `:role` suffix as identity disambiguator
    but readers consume the field, never parse the string."""
    spec = build_test_battle_spec(_MinimalDuelScenario(), registries=None)
    ship1 = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    ship2 = spec.teams[1].fleet_hierarchy[0].squadrons[0].ships[0]
    assert ship1.scenario_role == "ship1"
    assert ship2.scenario_role == "ship2"


def test_compiler_duel_design_ids_from_ship_files():
    spec = build_test_battle_spec(_MinimalDuelScenario(), registries=None)
    ship1 = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    ship2 = spec.teams[1].fleet_hierarchy[0].squadrons[0].ships[0]
    assert ship1.design_id == "Test_Attacker_Beam360_High.json"
    assert ship2.design_id == "Test_Target_Stationary.json"


# ===========================================================================
# Phase 6 Task 6.7a — PropulsionScenario compiler support
# ===========================================================================


class _MinimalPropulsionScenario(PropulsionScenario):
    metadata = TestMetadata(
        test_id="SPEC-PROP-001",
        category="SpecCompiler",
        subcategory="Propulsion",
        name="Minimal propulsion scenario",
        summary="",
        conditions=[],
        edge_cases=[],
        expected_outcome="",
        pass_criteria="",
        max_ticks=150,
        seed=9,
    )
    ship_file = "Test_Engine_1x_LowMass.json"
    initial_position = pygame.math.Vector2(10, 20)
    initial_velocity = pygame.math.Vector2(1, 2)
    initial_angle = 45.0
    thrust_forward = True

    def validate(self, engine):
        return []


def test_compiler_supports_propulsion_scenario_single_team():
    spec = build_test_battle_spec(_MinimalPropulsionScenario(), registries=None)
    assert isinstance(spec, BattleSpec)
    # Single-ship scenario: exactly one team with one ship.
    assert len(spec.teams) == 1
    assert len(spec.teams[0].fleet_hierarchy[0].squadrons[0].ships) == 1


def test_compiler_propulsion_applies_initial_pose():
    spec = build_test_battle_spec(_MinimalPropulsionScenario(), registries=None)
    ship = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    assert ship.position.x == 10.0
    assert ship.position.y == 20.0
    assert ship.angle == 45.0
    assert ship.velocity.x == 1.0
    assert ship.velocity.y == 2.0


def test_compiler_propulsion_ship_carries_scenario_role():
    spec = build_test_battle_spec(_MinimalPropulsionScenario(), registries=None)
    ship = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    assert ship.scenario_role == "ship"


# ===========================================================================
# Phase 6 Task 6.7a — ResourceScenario compiler support
# ===========================================================================


class _MinimalResourceScenarioNoTarget(ResourceScenario):
    metadata = TestMetadata(
        test_id="SPEC-RES-001",
        category="SpecCompiler",
        subcategory="Resource",
        name="Minimal resource scenario without target",
        summary="",
        conditions=[],
        edge_cases=[],
        expected_outcome="",
        pass_criteria="",
        max_ticks=100,
        seed=11,
    )
    ship_file = "Test_Engine_1x_LowMass.json"
    resource_type = "fuel"
    thrust_forward = True

    def validate(self, engine):
        return []


class _MinimalResourceScenarioWithTarget(ResourceScenario):
    metadata = TestMetadata(
        test_id="SPEC-RES-002",
        category="SpecCompiler",
        subcategory="Resource",
        name="Minimal resource scenario with target",
        summary="",
        conditions=[],
        edge_cases=[],
        expected_outcome="",
        pass_criteria="",
        max_ticks=100,
        seed=13,
    )
    ship_file = "Test_Attacker_Beam360_High.json"
    resource_type = "energy"
    force_fire = True
    target_ship_file = "Test_Target_Stationary.json"
    target_distance = 250

    def validate(self, engine):
        return []


def test_compiler_supports_resource_scenario_single_ship():
    spec = build_test_battle_spec(
        _MinimalResourceScenarioNoTarget(), registries=None
    )
    assert isinstance(spec, BattleSpec)
    # No target → single team with single ship.
    assert len(spec.teams) == 1
    assert len(spec.teams[0].fleet_hierarchy[0].squadrons[0].ships) == 1


def test_compiler_supports_resource_scenario_with_target():
    spec = build_test_battle_spec(
        _MinimalResourceScenarioWithTarget(), registries=None
    )
    # With target → two teams, one ship each.
    assert len(spec.teams) == 2
    assert len(spec.teams[0].fleet_hierarchy[0].squadrons[0].ships) == 1
    assert len(spec.teams[1].fleet_hierarchy[0].squadrons[0].ships) == 1


def test_compiler_resource_scenario_target_at_target_distance():
    spec = build_test_battle_spec(
        _MinimalResourceScenarioWithTarget(), registries=None
    )
    ship = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    target = spec.teams[1].fleet_hierarchy[0].squadrons[0].ships[0]
    assert ship.position.x == 0.0
    assert target.position.x == 250.0
    assert ship.scenario_role == "ship"
    assert target.scenario_role == "target"


# ===========================================================================
# Phase 6 Task 6.7a — ComparisonScenario compiler support
# ===========================================================================


class _MinimalComparisonScenario(ComparisonScenario):
    metadata = TestMetadata(
        test_id="SPEC-CMP-001",
        category="SpecCompiler",
        subcategory="Comparison",
        name="Minimal comparison scenario",
        summary="",
        conditions=[],
        edge_cases=[],
        expected_outcome="",
        pass_criteria="",
        max_ticks=120,
        seed=17,
    )
    baseline_attacker_ship = "Test_Attacker_Beam360_High.json"
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = "Test_Attacker_Beam360_High.json"
    variant_target_ship = "Test_Target_ECM.json"
    distance = 300

    def validate(self, engine):
        return []


def test_compiler_comparison_normal_mode_emits_variant_spec():
    scenario = _MinimalComparisonScenario()
    spec = build_test_battle_spec(scenario, registries=None)
    assert isinstance(spec, BattleSpec)
    assert len(spec.teams) == 2
    attacker = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    target = spec.teams[1].fleet_hierarchy[0].squadrons[0].ships[0]
    # Normal mode emits VARIANT ships.
    assert attacker.design_id == "Test_Attacker_Beam360_High.json"
    assert target.design_id == "Test_Target_ECM.json"
    assert attacker.scenario_role == "variant_attacker"
    assert target.scenario_role == "variant_target"


def test_compiler_comparison_visual_baseline_mode_emits_baseline_spec():
    scenario = _MinimalComparisonScenario()
    scenario._visual_baseline = True
    spec = build_test_battle_spec(scenario, registries=None)
    assert len(spec.teams) == 2
    attacker = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    target = spec.teams[1].fleet_hierarchy[0].squadrons[0].ships[0]
    # Visual-baseline mode emits BASELINE ships.
    assert attacker.design_id == "Test_Attacker_Beam360_High.json"
    assert target.design_id == "Test_Target_Stationary.json"
    assert attacker.scenario_role == "baseline_attacker"
    assert target.scenario_role == "baseline_target"


def test_compiler_comparison_positions_target_at_distance():
    spec = build_test_battle_spec(_MinimalComparisonScenario(), registries=None)
    attacker = spec.teams[0].fleet_hierarchy[0].squadrons[0].ships[0]
    target = spec.teams[1].fleet_hierarchy[0].squadrons[0].ships[0]
    assert attacker.position.x == 0.0
    assert target.position.x == 300.0
