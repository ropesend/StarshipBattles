"""Tests for Combat Lab compiler ↔ FormationResolver integration (PROJ-269 Phase 4 Task 4.6).

Confirms `build_test_battle_spec` routes `StaticTargetScenario`'s
explicit positions through `FormationSpec(shape=CUSTOM)` so the final
ShipSpec positions are identical to the existing test scenarios
(no regression) but the pipeline is consistent with the other compilers.
"""
import pytest

from combat_lab.scenarios.base import TestMetadata
from combat_lab.scenarios.templates import StaticTargetScenario
from combat_lab.spec_compiler import build_test_battle_spec
from game.simulation.combat.formation import FormationShape


class _MinimalStaticScenario(StaticTargetScenario):
    metadata = TestMetadata(
        test_id="SPEC-FORM-001",
        category="SpecCompiler",
        subcategory="Formation",
        name="Attacker+Target static",
        summary="",
        conditions=["Distance: 500"],
        edge_cases=[],
        expected_outcome="",
        pass_criteria="",
        max_ticks=100,
        seed=1,
    )
    attacker_ship = "Test_Attacker_Beam360_High.json"
    target_ship = "Test_Target_Stationary.json"
    distance = 500

    def validate(self, engine):
        return []


def _ships_on_team(spec, team_id: int):
    return [
        s
        for tf in spec.teams[team_id].fleet_hierarchy
        for sq in tf.squadrons
        for s in sq.ships
    ]


def test_compiler_attacker_at_origin(session_registries):
    scenario = _MinimalStaticScenario()
    spec = build_test_battle_spec(scenario, session_registries)
    attacker = _ships_on_team(spec, team_id=0)[0]
    assert attacker.position.x == pytest.approx(0.0)
    assert attacker.position.y == pytest.approx(0.0)


def test_compiler_target_at_distance(session_registries):
    scenario = _MinimalStaticScenario()
    spec = build_test_battle_spec(scenario, session_registries)
    target = _ships_on_team(spec, team_id=1)[0]
    assert target.position.x == pytest.approx(500.0)
    assert target.position.y == pytest.approx(0.0)


def test_compiler_uses_custom_formation_spec(session_registries):
    """TaskForce.formation is populated with a CUSTOM FormationSpec
    so the resolver can reproduce the positions deterministically."""
    scenario = _MinimalStaticScenario()
    spec = build_test_battle_spec(scenario, session_registries)

    attacker_tf = spec.teams[0].fleet_hierarchy[0]
    target_tf = spec.teams[1].fleet_hierarchy[0]

    # Phase 4 requirement: formations are now explicit (not None) on each TF.
    assert attacker_tf.formation is not None
    assert target_tf.formation is not None
    assert attacker_tf.formation.shape == FormationShape.CUSTOM
    assert target_tf.formation.shape == FormationShape.CUSTOM
