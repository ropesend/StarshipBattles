"""
Beam Weapon Tests (BEAM360-001 through BEAM360-011)

Pytest wrappers for beam weapon test scenarios. These tests validate beam weapon
accuracy mechanics using the TestScenario framework.

Accuracy Formula:
- Sigmoid accuracy formula: P = 1 / (1 + e^-x)
- where x = (base_accuracy + attack_bonus) - (range_penalty + defense_penalty)
- Range penalty = accuracy_falloff * distance

Test Coverage:
- BEAM360-001 to BEAM360-003: Low accuracy beam (3 distance variants)
- BEAM360-004 to BEAM360-006: Medium accuracy beam (3 distance variants)
- BEAM360-007 to BEAM360-008: High accuracy beam (2 distance variants)
- BEAM360-009 to BEAM360-010: Moving target tests (erratic targets)
- BEAM360-011: Out of range test
"""
import pytest
from test_framework.runner import TestRunner
from simulation_tests.logging_config import get_logger
from simulation_tests.scenarios.beam_scenarios import (
    BeamLowAccuracyPointBlankScenario,
    BeamLowAccuracyMidRangeScenario,
    BeamLowAccuracyMaxRangeScenario,
    BeamMediumAccuracyPointBlankScenario,
    BeamMediumAccuracyMidRangeScenario,
    BeamMediumAccuracyMaxRangeScenario,
    BeamHighAccuracyPointBlankScenario,
    BeamHighAccuracyMaxRangeScenario,
    BeamMediumAccuracyErraticMidRangeScenario,
    BeamMediumAccuracyErraticMaxRangeScenario,
    BeamOutOfRangeScenario
)

logger = get_logger(__name__)


@pytest.mark.simulation
class TestBeamWeapons:
    """Test beam weapon accuracy at various ranges and configurations using TestScenario wrappers."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry for each test."""
        self.runner = TestRunner()
    
    # ===== LOW ACCURACY BEAM TESTS (base_accuracy=0.5, falloff=0.002) =====

    def test_BEAM360_001_low_acc_point_blank(self):
        """
        BEAM360-001: Low accuracy beam (0.5) at point-blank.

        Expected: ~60% hit rate at 50px distance.
        """
        scenario = self.runner.run_scenario(
            BeamLowAccuracyPointBlankScenario,
            headless=True
        )

        assert scenario.passed, \
            f"BEAM360-001 failed: {scenario.results.get('failure_reason', 'Unknown')}"
        assert scenario.results['damage_dealt'] > 0, \
            "Low accuracy beam should deal damage at point-blank"

        # Print results for debugging
        logger.info(f"\nBEAM360-001 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Expected Hit Chance: {scenario.results['expected_hit_chance']:.2%}")
        logger.info(f"  Ticks: {scenario.results['ticks_run']}")
    
    def test_BEAM360_002_low_acc_mid_range(self):
        """
        BEAM360-002: Low accuracy beam (0.5) at 400 pixels.

        Expected: ~43% hit rate at mid-range with moderate range penalty.
        """
        scenario = self.runner.run_scenario(
            BeamLowAccuracyMidRangeScenario,
            headless=True
        )

        assert scenario.passed, \
            f"BEAM360-002 failed: {scenario.results.get('failure_reason', 'Unknown')}"
        assert scenario.results['ticks_run'] > 0, "Simulation should run"

        # Print results for debugging
        logger.info(f"\nBEAM360-002 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Expected Hit Chance: {scenario.results['expected_hit_chance']:.2%}")
        logger.info(f"  Ticks: {scenario.results['ticks_run']}")
    
    def test_BEAM360_003_low_acc_max_range(self):
        """
        BEAM360-003: Low accuracy beam (0.5) at max range (750px).

        Expected: ~27% hit rate - accuracy heavily degraded at range.
        """
        scenario = self.runner.run_scenario(
            BeamLowAccuracyMaxRangeScenario,
            headless=True
        )

        assert scenario.passed, \
            f"BEAM360-003 failed: {scenario.results.get('failure_reason', 'Unknown')}"
        assert scenario.results['ticks_run'] > 0, "Simulation should complete"

        # Print results for debugging
        logger.info(f"\nBEAM360-003 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Expected Hit Chance: {scenario.results['expected_hit_chance']:.2%}")
        logger.info(f"  Ticks: {scenario.results['ticks_run']}")
    
    # ===== MEDIUM ACCURACY BEAM TESTS (base_accuracy=2.0, falloff=0.001) =====

    def test_BEAM360_004_med_acc_point_blank(self):
        """
        BEAM360-004: Medium accuracy beam (2.0) at point-blank.

        Expected: ~88% hit rate at 50px distance.
        """
        scenario = self.runner.run_scenario(
            BeamMediumAccuracyPointBlankScenario,
            headless=True
        )

        assert scenario.passed, \
            f"BEAM360-004 failed: {scenario.results.get('failure_reason', 'Unknown')}"
        assert scenario.results['damage_dealt'] > 0, \
            "Medium accuracy beam should deal significant damage at point-blank"

        # Print results for debugging
        logger.info(f"\nBEAM360-004 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Expected Hit Chance: {scenario.results['expected_hit_chance']:.2%}")
        logger.info(f"  Ticks: {scenario.results['ticks_run']}")
    
    def test_BEAM360_005_med_acc_mid_range(self):
        """
        BEAM360-005: Medium accuracy beam (2.0) at 400 pixels.

        Expected: ~83% hit rate at mid-range.
        """
        scenario = self.runner.run_scenario(
            BeamMediumAccuracyMidRangeScenario,
            headless=True
        )

        assert scenario.passed, \
            f"BEAM360-005 failed: {scenario.results.get('failure_reason', 'Unknown')}"
        assert scenario.results['damage_dealt'] > 0, \
            "Medium accuracy beam should deal damage at mid-range"

        # Print results for debugging
        logger.info(f"\nBEAM360-005 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Expected Hit Chance: {scenario.results['expected_hit_chance']:.2%}")
        logger.info(f"  Ticks: {scenario.results['ticks_run']}")
    
    def test_BEAM360_006_med_acc_max_range(self):
        """
        BEAM360-006: Medium accuracy beam (2.0) at max range (750px).

        Expected: ~78% hit rate at max range.
        """
        scenario = self.runner.run_scenario(
            BeamMediumAccuracyMaxRangeScenario,
            headless=True
        )

        assert scenario.passed, \
            f"BEAM360-006 failed: {scenario.results.get('failure_reason', 'Unknown')}"
        assert scenario.results['ticks_run'] > 0, "Simulation should complete"

        # Print results for debugging
        logger.info(f"\nBEAM360-006 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Expected Hit Chance: {scenario.results['expected_hit_chance']:.2%}")
        logger.info(f"  Ticks: {scenario.results['ticks_run']}")
    
    # ===== HIGH ACCURACY BEAM TESTS (base_accuracy=5.0, falloff=0.0005) =====

    def test_BEAM360_007_high_acc_point_blank(self):
        """
        BEAM360-007: High accuracy beam (5.0) at point-blank.

        Expected: ~99.3% hit rate at 50px distance.
        """
        scenario = self.runner.run_scenario(
            BeamHighAccuracyPointBlankScenario,
            headless=True
        )

        assert scenario.passed, \
            f"BEAM360-007 failed: {scenario.results.get('failure_reason', 'Unknown')}"
        assert scenario.results['damage_dealt'] > 0, \
            "High accuracy beam should hit consistently at point-blank"

        # Print results for debugging
        logger.info(f"\nBEAM360-007 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Expected Hit Chance: {scenario.results['expected_hit_chance']:.2%}")
        logger.info(f"  Ticks: {scenario.results['ticks_run']}")
    
    def test_BEAM360_008_high_acc_max_range(self):
        """
        BEAM360-008: High accuracy beam (5.0) at max range (750px).

        Expected: ~99.0% hit rate - barely affected by range.
        """
        scenario = self.runner.run_scenario(
            BeamHighAccuracyMaxRangeScenario,
            headless=True
        )

        assert scenario.passed, \
            f"BEAM360-008 failed: {scenario.results.get('failure_reason', 'Unknown')}"
        assert scenario.results['damage_dealt'] > 0, \
            "High accuracy beam should hit at max range"

        # Print results for debugging
        logger.info(f"\nBEAM360-008 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Expected Hit Chance: {scenario.results['expected_hit_chance']:.2%}")
        logger.info(f"  Ticks: {scenario.results['ticks_run']}")
    
    # ===== MOVING TARGET TESTS =====

    def test_BEAM360_009_med_acc_vs_erratic_small_mid_range(self):
        """
        BEAM360-009: Medium accuracy beam vs small erratic target at 400 pixels.

        Defense score increases for maneuverable targets, reducing hit chance.
        Expected: Reduced hit rate compared to stationary target.
        """
        scenario = self.runner.run_scenario(
            BeamMediumAccuracyErraticMidRangeScenario,
            headless=True
        )

        assert scenario.passed, \
            f"BEAM360-009 failed: {scenario.results.get('failure_reason', 'Unknown')}"
        assert scenario.results['ticks_run'] > 0, "Simulation should complete"

        # Print results for debugging
        logger.info(f"\nBEAM360-009 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Expected Hit Chance (with defense): {scenario.results['expected_hit_chance']:.2%}")
        logger.info(f"  Expected Hit Chance (base only): {scenario.results['expected_hit_chance_base']:.2%}")
        logger.info(f"  Ticks: {scenario.results['ticks_run']}")
    
    def test_BEAM360_010_med_acc_vs_erratic_small_max_range(self):
        """
        BEAM360-010: Medium accuracy beam vs small erratic target at max range.

        Combination of range and maneuverability penalties.
        Expected: Significantly reduced hit rate.
        """
        scenario = self.runner.run_scenario(
            BeamMediumAccuracyErraticMaxRangeScenario,
            headless=True
        )

        assert scenario.passed, \
            f"BEAM360-010 failed: {scenario.results.get('failure_reason', 'Unknown')}"
        assert scenario.results['ticks_run'] > 0, "Simulation should complete"

        # Print results for debugging
        logger.info(f"\nBEAM360-010 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Expected Hit Chance (with defense): {scenario.results['expected_hit_chance']:.2%}")
        logger.info(f"  Expected Hit Chance (base only): {scenario.results['expected_hit_chance_base']:.2%}")
        logger.info(f"  Ticks: {scenario.results['ticks_run']}")
    
    def test_BEAM360_011_out_of_range(self):
        """
        BEAM360-011: Beam weapon fires but no hits beyond max range.

        Target at max_range + 100 (900 pixels for 800 range weapon).
        """
        scenario = self.runner.run_scenario(
            BeamOutOfRangeScenario,
            headless=True
        )

        assert scenario.passed, \
            f"BEAM360-011 failed: {scenario.results.get('failure_reason', 'Unknown')}"
        assert scenario.results['damage_dealt'] == 0, \
            f"Target beyond range should take 0 damage, got {scenario.results['damage_dealt']}"

        # Print results for debugging
        logger.info(f"\nBEAM360-011 Results:")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")
        logger.info(f"  Distance: {scenario.results['distance']}")
        logger.info(f"  Weapon Max Range: {scenario.results['weapon_max_range']}")
        logger.info(f"  Ticks: {scenario.results['ticks_run']}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
