"""
Modifier Tests (MOD-001 to MOD-006)

Pytest wrappers for modifier test scenarios. These tests validate that the
modifier system correctly modifies component ability attributes and affects
combat/physics behavior accordingly.

Test Coverage:
- MOD-001: Damage multiplier (1.5x) on beam weapon
- MOD-002: Range multiplier (2x) on beam weapon
- MOD-003: Reload reduction on beam weapon (attribute check)
- MOD-004: Thrust multiplier (2x) on engine
- MOD-005: Accuracy boost on beam weapon (measurement)
- MOD-006: Turret arc set (180) on beam weapon
"""
import pytest
from test_framework.runner import TestRunner
from simulation_tests.logging_config import get_logger
from simulation_tests.scenarios.modifier_scenarios import (
    DamageMultiplierScenario,
    RangeMultiplierScenario,
    ReloadReductionScenario,
    ThrustMultiplierScenario,
    AccuracyBoostScenario,
    TurretArcSetScenario,
)

logger = get_logger(__name__)


@pytest.mark.simulation
class TestBeamModifiers:
    """Test modifier effects on beam weapon abilities."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry for each test."""
        self.runner = TestRunner()

    def test_MOD_001_damage_multiplier(self):
        """
        MOD-001: Damage multiplier (1.5x) on beam weapon.

        Expected: beam.damage = 1.5, damage dealt to target.
        """
        scenario = self.runner.run_scenario(
            DamageMultiplierScenario,
            headless=True
        )

        assert scenario.passed, \
            f"MOD-001 failed: {scenario.results.get('failure_reason', scenario.results)}"
        assert scenario.results.get('modifier_applied_correctly'), \
            f"Damage modifier not applied: expected {scenario.results.get('expected_beam_damage')}, " \
            f"got {scenario.results.get('actual_beam_damage')}"
        assert scenario.results['damage_dealt'] > 0, \
            "Modified beam should deal damage"

        logger.info(f"\nMOD-001 Results:")
        logger.info(f"  Base Damage: {scenario.results['base_damage']}")
        logger.info(f"  Expected Beam Damage: {scenario.results['expected_beam_damage']}")
        logger.info(f"  Actual Beam Damage: {scenario.results['actual_beam_damage']}")
        logger.info(f"  Total Damage Dealt: {scenario.results['damage_dealt']}")

    def test_MOD_002_range_multiplier(self):
        """
        MOD-002: Range multiplier (2x) on beam weapon.

        Expected: beam.range = 1600, beam hits at 1200px (beyond base 800 range).
        """
        scenario = self.runner.run_scenario(
            RangeMultiplierScenario,
            headless=True
        )

        assert scenario.passed, \
            f"MOD-002 failed: {scenario.results.get('failure_reason', scenario.results)}"
        assert scenario.results.get('modifier_applied_correctly'), \
            f"Range modifier not applied: expected {scenario.results.get('expected_beam_range')}, " \
            f"got {scenario.results.get('actual_beam_range')}"
        assert scenario.results['damage_dealt'] > 0, \
            "Beam with extended range should hit at 1200px"

        logger.info(f"\nMOD-002 Results:")
        logger.info(f"  Base Range: {scenario.results['base_range']}")
        logger.info(f"  Expected Beam Range: {scenario.results['expected_beam_range']}")
        logger.info(f"  Actual Beam Range: {scenario.results['actual_beam_range']}")
        logger.info(f"  Distance: {scenario.results['distance']}")
        logger.info(f"  Total Damage Dealt: {scenario.results['damage_dealt']}")

    def test_MOD_003_reload_reduction(self):
        """
        MOD-003: Reload reduction on beam weapon.

        Expected: Modifier system loads and simulation completes.
        Note: Base reload is 0.0 so multiplier has no observable effect.
        """
        scenario = self.runner.run_scenario(
            ReloadReductionScenario,
            headless=True
        )

        assert scenario.passed, \
            f"MOD-003 failed: {scenario.results}"
        assert scenario.results['ticks_run'] > 0, \
            "Simulation should complete"

        logger.info(f"\nMOD-003 Results:")
        logger.info(f"  Actual Reload Time: {scenario.results.get('actual_reload_time')}")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")

    def test_MOD_005_accuracy_boost(self):
        """
        MOD-005: Accuracy boost on beam weapon.

        Expected: Modifier system works and simulation completes.
        """
        scenario = self.runner.run_scenario(
            AccuracyBoostScenario,
            headless=True
        )

        assert scenario.passed, \
            f"MOD-005 failed: {scenario.results}"
        assert scenario.results['ticks_run'] > 0, \
            "Simulation should complete"

        logger.info(f"\nMOD-005 Results:")
        logger.info(f"  Actual Base Accuracy: {scenario.results.get('actual_base_accuracy')}")
        logger.info(f"  Damage Dealt: {scenario.results['damage_dealt']}")

    def test_MOD_006_turret_arc_set(self):
        """
        MOD-006: Turret arc set to 180 degrees on beam weapon.

        Expected: beam.firing_arc = 180, beam still hits target within arc.
        """
        scenario = self.runner.run_scenario(
            TurretArcSetScenario,
            headless=True
        )

        assert scenario.passed, \
            f"MOD-006 failed: {scenario.results.get('failure_reason', scenario.results)}"
        assert scenario.results.get('modifier_applied_correctly'), \
            f"Arc modifier not applied: expected {scenario.results.get('expected_arc')}, " \
            f"got {scenario.results.get('actual_firing_arc')}"
        assert scenario.results['damage_dealt'] > 0, \
            "Beam with 180 arc should hit target directly ahead"

        logger.info(f"\nMOD-006 Results:")
        logger.info(f"  Base Arc: {scenario.results['base_arc']}")
        logger.info(f"  Expected Arc: {scenario.results['expected_arc']}")
        logger.info(f"  Actual Firing Arc: {scenario.results['actual_firing_arc']}")
        logger.info(f"  Total Damage Dealt: {scenario.results['damage_dealt']}")


@pytest.mark.simulation
class TestPropulsionModifiers:
    """Test modifier effects on propulsion abilities."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry for each test."""
        self.runner = TestRunner()

    def test_MOD_004_thrust_multiplier(self):
        """
        MOD-004: Thrust multiplier (2x) on engine.

        Expected: ship.total_thrust = 1000, max_speed = 62.5.
        """
        scenario = self.runner.run_scenario(
            ThrustMultiplierScenario,
            headless=True
        )

        assert scenario.passed, \
            f"MOD-004 failed: {scenario.results.get('failure_reason', scenario.results)}"
        assert scenario.results.get('modifier_applied_correctly'), \
            f"Thrust modifier not applied: expected {scenario.results.get('expected_thrust')}, " \
            f"got {scenario.results.get('actual_thrust')}"

        logger.info(f"\nMOD-004 Results:")
        logger.info(f"  Base Thrust: {scenario.results['base_thrust']}")
        logger.info(f"  Expected Thrust: {scenario.results['expected_thrust']}")
        logger.info(f"  Actual Thrust: {scenario.results['actual_thrust']}")
        logger.info(f"  Final Speed: {scenario.results['final_velocity_magnitude']:.2f}")
        logger.info(f"  Expected Max Speed: {scenario.results['expected_max_speed']:.2f}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
