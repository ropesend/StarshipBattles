"""Tests for ComparisonScenario's PROJ-277 Phase 3 API additions.

Phase 3 adds `build_baseline_spec()` and `build_variant_spec()` as
additive hooks on `ComparisonScenario`. These tests cover only the
NEW API; the legacy `_run_baseline_battle` + `_run_validation`
override + `_baseline_*` attribute stashing continues to exist
unchanged and is exercised by the existing full-scenario tests.

Phase 5 will migrate the subclasses and delete the legacy path;
Phase 3's tests deliberately do NOT assert the legacy is gone
because that deletion is a later atomic swap.
"""
from __future__ import annotations

from unittest.mock import MagicMock

from combat_lab.scenarios.base import TestMetadata
from combat_lab.scenarios.templates import ComparisonScenario
from game.simulation.battle_spec import BattleSpec


class _MinimalComparisonScenario(ComparisonScenario):
    """Stand-in subclass used only to exercise the new hooks."""
    metadata = TestMetadata(
        test_id="minimal-comparison",
        category="Test",
        subcategory="Comparison",
        name="Minimal Comparison",
        summary="Minimal subclass for exercising A/B spec hooks.",
        conditions=[],
        edge_cases=[],
        expected_outcome="N/A",
        pass_criteria="N/A",
        max_ticks=5,
    )
    baseline_attacker_ship = "Test_Attacker.json"
    baseline_target_ship = "Test_Target.json"
    variant_attacker_ship = "Test_Attacker_Variant.json"
    variant_target_ship = "Test_Target.json"
    distance = 400.0


class TestBuildBaselineSpec:
    def test_returns_battle_spec(self):
        scenario = _MinimalComparisonScenario()
        scenario._effective_seed = 1234  # required by _build_baseline_battle_spec

        spec = scenario.build_baseline_spec()

        assert isinstance(spec, BattleSpec)

    def test_default_uses_baseline_ship_designs(self):
        """Default implementation produces a spec whose ships reference
        the `baseline_*_ship` design ids, not the `variant_*_ship`."""
        scenario = _MinimalComparisonScenario()
        scenario._effective_seed = 1234

        spec = scenario.build_baseline_spec()

        design_ids = [
            ship.design_id
            for team in spec.teams
            for tf in team.fleet_hierarchy
            for sq in tf.squadrons
            for ship in sq.ships
        ]
        assert "Test_Attacker.json" in design_ids
        assert "Test_Target.json" in design_ids
        # Critically, NOT the variant attacker.
        assert "Test_Attacker_Variant.json" not in design_ids

    def test_subclass_can_override(self):
        """Subclasses can replace the default spec entirely."""
        custom_spec = MagicMock(spec=BattleSpec)

        class _OverrideScenario(_MinimalComparisonScenario):
            def build_baseline_spec(self):
                return custom_spec

        scenario = _OverrideScenario()
        assert scenario.build_baseline_spec() is custom_spec


class TestBuildVariantSpec:
    def test_returns_battle_spec(self):
        scenario = _MinimalComparisonScenario()

        spec = scenario.build_variant_spec()

        assert isinstance(spec, BattleSpec)

    def test_default_uses_variant_ship_designs(self):
        """Default implementation produces a spec whose ships reference
        the `variant_*_ship` designs, even if `_visual_baseline=True`."""
        scenario = _MinimalComparisonScenario()
        # Force the scenario to think it's in visual-baseline mode;
        # build_variant_spec must still return a variant-side spec.
        scenario._visual_baseline = True

        spec = scenario.build_variant_spec()

        design_ids = [
            ship.design_id
            for team in spec.teams
            for tf in team.fleet_hierarchy
            for sq in tf.squadrons
            for ship in sq.ships
        ]
        assert "Test_Attacker_Variant.json" in design_ids
        assert "Test_Attacker.json" not in design_ids

    def test_restores_visual_baseline_flag_after_call(self):
        """The hook toggles `_visual_baseline` internally; caller
        state must be preserved."""
        scenario = _MinimalComparisonScenario()
        scenario._visual_baseline = True

        scenario.build_variant_spec()

        assert scenario._visual_baseline is True

    def test_subclass_can_override(self):
        custom_spec = MagicMock(spec=BattleSpec)

        class _OverrideScenario(_MinimalComparisonScenario):
            def build_variant_spec(self):
                return custom_spec

        scenario = _OverrideScenario()
        assert scenario.build_variant_spec() is custom_spec
