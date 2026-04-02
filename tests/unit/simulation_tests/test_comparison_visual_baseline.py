"""
Regression test for ComparisonScenario visual baseline crash.

When Combat Lab renders the baseline battle (_visual_baseline=True),
collect_results() only populates baseline attributes. If validate()
accesses variant attributes, it crashes with AttributeError.

The fix: ComparisonScenario._run_validation() should skip validate()
in visual baseline mode and return a baseline-only report.
"""
import pytest
from unittest.mock import MagicMock, patch

from simulation_tests.scenarios.templates import ComparisonScenario
from simulation_tests.scenarios.base import TestMetadata
from simulation_tests.scenarios.validation import check_true


class _DummyComparisonScenario(ComparisonScenario):
    """Minimal ComparisonScenario that accesses variant_damage_dealt."""

    metadata = TestMetadata(
        test_id="TEST-VISUAL-BASELINE",
        category="Test",
        subcategory="Visual",
        name="Visual Baseline Crash Regression",
        summary="Regression test",
        conditions=[],
        edge_cases=[],
        expected_outcome="No crash in visual baseline mode",
        pass_criteria="No AttributeError",
        max_ticks=10,
        seed=42,
        battle_end_mode="time_based",
        tags=["test"],
    )

    baseline_attacker_ship = "Test_Attacker_Beam360_Low.json"
    baseline_target_ship = "Test_Target_Stationary.json"
    variant_attacker_ship = "Test_Attacker_Beam360_Low.json"
    variant_target_ship = "Test_Target_Stationary.json"
    distance = 100

    def validate(self, engine) -> list:
        # This accesses variant_damage_dealt — crashes in visual baseline mode
        return [check_true(
            "Variant Did Damage",
            self.variant_damage_dealt > 0,
            detail=f"damage={self.variant_damage_dealt}",
            phase="outcome",
        )]


class TestComparisonVisualBaselineCrash:
    """Regression test: visual baseline mode must not crash on validate()."""

    def test_visual_baseline_does_not_crash(self):
        """_run_validation should not call validate() in visual baseline mode."""
        scenario = _DummyComparisonScenario()
        scenario._visual_baseline = True

        # Simulate what collect_results does in visual baseline mode:
        # only baseline attributes are set, no variant attributes
        scenario.baseline_damage_dealt = 50.0
        scenario.baseline_initial_hp = 1000.0
        scenario.baseline_final_hp = 950.0
        scenario.baseline_ticks = 10
        scenario.results = {'ticks_run': 10}

        engine = MagicMock()
        engine.tick_counter = 10

        # Patch collect_results to avoid needing real ships
        with patch.object(scenario, 'collect_results'):
            # This should NOT raise AttributeError
            report = scenario._run_validation(engine)

        # Should get a report (baseline-only, no variant checks)
        assert report is not None
        assert report.passed  # baseline-only report should pass

    def test_normal_mode_still_calls_validate(self):
        """In normal mode, validate() should still be called."""
        scenario = _DummyComparisonScenario()
        scenario._visual_baseline = False

        # Set both baseline and variant attributes
        scenario.baseline_damage_dealt = 50.0
        scenario.baseline_initial_hp = 1000.0
        scenario.baseline_final_hp = 950.0
        scenario.baseline_ticks = 10
        scenario.variant_damage_dealt = 75.0
        scenario.variant_initial_hp = 1000.0
        scenario.variant_final_hp = 925.0
        scenario.variant_ticks = 10
        scenario.results = {'ticks_run': 10}

        engine = MagicMock()
        engine.tick_counter = 10

        with patch.object(scenario, 'collect_results'):
            report = scenario._run_validation(engine)

        assert report is not None
        # validate() accessed variant_damage_dealt=75 > 0, so check passes
        assert report.passed
