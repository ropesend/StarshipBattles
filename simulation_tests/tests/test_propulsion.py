"""
Propulsion Test Suite (PROP-001 to PROP-004)

Pytest wrappers for propulsion test scenarios. These tests validate the core
physics of engines and thrusters using the TestScenario framework.

Test Coverage:
- PROP-001: Engine provides thrust - ship accelerates
- PROP-002: Thrust/mass ratio affects max speed
- PROP-003: Thruster provides turn rate
- PROP-004: Turn rate allows rotation
"""

import pytest
from game.simulation.physics_constants import K_SPEED, K_THRUST, K_TURN
from test_framework.runner import TestRunner
from simulation_tests.logging_config import get_logger
from simulation_tests.scenarios.propulsion_scenarios import (
    PropEngineAccelerationScenario,
    PropThrustMassRatioScenario,
    PropThrusterTurnRateScenario,
    PropThrusterRotationScenario
)

logger = get_logger(__name__)


def print_propulsion_test_header(test_id, description, scenario):
    """Print detailed ship configuration for propulsion tests."""
    logger.info(f"\n{'='*70}")
    logger.info(f"{test_id}: {description}")
    logger.info(f"{'='*70}")
    logger.info(f"\nShip Configuration:")
    logger.info(f"  Name: {scenario.ship.name}")
    logger.info(f"  Mass: {scenario.ship.mass} tons")
    logger.info(f"  Total Thrust: {scenario.ship.total_thrust}")
    logger.info(f"  Max Speed: {scenario.ship.max_speed:.2f} px/s")
    logger.info(f"  Acceleration: {scenario.ship.acceleration_rate:.2f} px/s²")
    logger.info(f"  Turn Speed: {scenario.ship.turn_speed:.2f}°/s")

    logger.info(f"\nComponents:")
    # Iterate through ship layers to find components
    for layer_name, layer_data in scenario.ship.layers.items():
        for component in layer_data.get('components', []):
            if hasattr(component, 'thrust_power') and component.thrust_power > 0:
                logger.info(f"  - {component.name}: {component.thrust_power} thrust")
            elif hasattr(component, 'turn_speed') and component.turn_speed > 0:
                logger.info(f"  - {component.name}: {component.turn_speed} turn rate")

    logger.info(f"\nPhysics Constants:")
    logger.info(f"  K_SPEED = {K_SPEED}")
    logger.info(f"  K_THRUST = {K_THRUST}")
    logger.info(f"  K_TURN = {K_TURN}")

    logger.info(f"\nExpected Physics:")
    logger.info(f"  max_speed = (thrust × K_SPEED) / mass")
    logger.info(f"            = ({scenario.ship.total_thrust} × {K_SPEED}) / {scenario.ship.mass}")
    logger.info(f"            = {scenario.ship.max_speed:.2f}")

    if scenario.ship.total_thrust > 0:
        logger.info(f"\n  acceleration = (thrust × K_THRUST) / mass²")
        logger.info(f"               = ({scenario.ship.total_thrust} × {K_THRUST}) / {scenario.ship.mass}²")
        logger.info(f"               = {scenario.ship.acceleration_rate:.2f}")

    logger.info(f"{'='*70}\n")


@pytest.mark.simulation
class TestPropulsionPhysics:
    """Test suite for propulsion physics (engines and thrusters)."""

    @pytest.fixture(autouse=True)
    def setup(self, isolated_registry):
        """Use isolated registry for each test."""
        self.runner = TestRunner()

    def test_PROP_001_engine_acceleration(self):
        """
        PROP-001: Engine Provides Thrust - Ship Accelerates

        Validates that an engine component provides thrust and the ship
        accelerates from rest over time.
        """
        scenario = self.runner.run_scenario(
            PropEngineAccelerationScenario,
            headless=True
        )

        # Print detailed configuration
        print_propulsion_test_header(
            "PROP-001",
            "Engine Provides Thrust - Ship Accelerates",
            scenario
        )

        # Check test passed
        assert scenario.passed, \
            f"PROP-001 failed: {scenario.results}"

        # Verify specific metrics
        assert scenario.results['final_velocity'] > scenario.results['initial_velocity'], \
            "Ship should have accelerated"

        assert scenario.results['final_velocity'] > 0, \
            "Final velocity should be positive"

        assert scenario.results['distance_traveled'] > 0, \
            "Ship should have moved"

        # Print results
        logger.info(f"Test Results:")
        logger.info(f"  Initial velocity: {scenario.results['initial_velocity']:.2f} px/s")
        logger.info(f"  Final velocity: {scenario.results['final_velocity']:.2f} px/s")
        logger.info(f"  Distance traveled: {scenario.results['distance_traveled']:.2f} px")
        logger.info(f"  Expected max speed: {scenario.results['expected_max_speed']:.2f} px/s")
        logger.info(f"  Ticks: {scenario.results['ticks_run']}")
        logger.info(f"\n{'='*70}\n")

    def test_PROP_002_thrust_mass_ratio(self):
        """
        PROP-002: Thrust/Mass Ratio Affects Max Speed

        Validates that max_speed scales inversely with mass according to
        the formula: max_speed = (thrust * K_SPEED) / mass
        """
        scenario = self.runner.run_scenario(
            PropThrustMassRatioScenario,
            headless=True
        )

        # Check test passed
        assert scenario.passed, \
            f"PROP-002 failed: {scenario.results}"

        # Verify speed ordering (low mass = high speed)
        assert scenario.results['speed_ordering_correct'], \
            "Speed should decrease with increasing mass"

        # Verify ratio accuracy
        assert scenario.results['ratio_matches'], \
            f"Speed ratio should match inverse mass ratio (error: {scenario.results['ratio_error_percent']:.2f}%)"

        # Print results for debugging
        logger.info(f"\nPROP-002 Results:")
        logger.info(f"  Low Mass Ship:")
        logger.info(f"    Mass: {scenario.results['low_mass']['mass']:.1f}")
        logger.info(f"    Max Speed: {scenario.results['low_mass']['max_speed']:.2f}")
        logger.info(f"    Final Velocity: {scenario.results['low_mass']['final_velocity']:.2f}")
        logger.info(f"  Med Mass Ship:")
        logger.info(f"    Mass: {scenario.results['med_mass']['mass']:.1f}")
        logger.info(f"    Max Speed: {scenario.results['med_mass']['max_speed']:.2f}")
        logger.info(f"    Final Velocity: {scenario.results['med_mass']['final_velocity']:.2f}")
        logger.info(f"  High Mass Ship:")
        logger.info(f"    Mass: {scenario.results['high_mass']['mass']:.1f}")
        logger.info(f"    Max Speed: {scenario.results['high_mass']['max_speed']:.2f}")
        logger.info(f"    Final Velocity: {scenario.results['high_mass']['final_velocity']:.2f}")
        logger.info(f"  Speed Ratio Error: {scenario.results['ratio_error_percent']:.2f}%")

    def test_PROP_003_thruster_turn_rate(self):
        """
        PROP-003: Thruster Provides Turn Rate

        Validates that ManeuveringThruster component provides turn rate
        and turn_speed is calculated correctly.
        """
        scenario = self.runner.run_scenario(
            PropThrusterTurnRateScenario,
            headless=True
        )

        # Check test passed
        assert scenario.passed, \
            f"PROP-003 failed: {scenario.results}"

        # Verify positive turn speed
        assert scenario.results['has_positive_turn_speed'], \
            "Ship should have positive turn_speed"

        # Verify formula accuracy
        assert scenario.results['matches_formula'], \
            f"Turn speed should match formula (error: {scenario.results.get('error_percent', 100):.2f}%)"

        # Print results for debugging
        logger.info(f"\nPROP-003 Results:")
        logger.info(f"  Mass: {scenario.results['mass']:.1f}")
        logger.info(f"  Raw Turn Rate: {scenario.results['raw_turn_rate']:.2f}")
        logger.info(f"  Expected Turn Speed: {scenario.results['expected_turn_speed']:.2f}")
        logger.info(f"  Actual Turn Speed: {scenario.results['actual_turn_speed']:.2f}")
        if 'error_percent' in scenario.results:
            logger.info(f"  Error: {scenario.results['error_percent']:.2f}%")

    def test_PROP_004_thruster_rotation(self):
        """
        PROP-004: Turn Rate Allows Rotation

        Validates that a ship with a thruster can rotate over time
        at the expected rate.
        """
        scenario = self.runner.run_scenario(
            PropThrusterRotationScenario,
            headless=True
        )

        # Check test passed
        assert scenario.passed, \
            f"PROP-004 failed: {scenario.results}"

        # Verify rotation detected
        assert scenario.results['rotation_detected'], \
            "Ship should have rotated"

        # Verify rotation direction
        assert scenario.results['expected_direction_correct'], \
            "Ship should rotate in commanded direction"

        # Print results for debugging
        logger.info(f"\nPROP-004 Results:")
        logger.info(f"  Initial Angle: {scenario.results['initial_angle']:.2f}°")
        logger.info(f"  Final Angle: {scenario.results['final_angle']:.2f}°")
        logger.info(f"  Angle Change: {scenario.results['angle_change']:.2f}°")
        logger.info(f"  Turn Speed: {scenario.results['turn_speed']:.2f}°/s")
        logger.info(f"  Ticks: {scenario.results['ticks_run']}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
