"""
Tests for PropulsionScenario enhanced results storage.

TDD tests for verifying that PropulsionScenario.verify() stores:
- Velocity data (starting, ending, magnitude)
- Position data (starting, ending, distance traveled)
- Angle data (starting, ending, change)
- Expected angle change for turn tests
- Turn speed in degrees per tick
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import pygame

from combat_lab.scenarios.templates import PropulsionScenario
from combat_lab.scenarios.base import TestMetadata


class MockPropulsionScenario(PropulsionScenario):
    """Concrete implementation for testing."""

    metadata = TestMetadata(
        test_id="TEST-PROP",
        category="Test",
        subcategory="Propulsion",
        name="Test propulsion scenario",
        summary="A test scenario for propulsion",
        conditions=[],
        edge_cases=[],
        expected_outcome="Pass",
        pass_criteria="True",
        max_ticks=50,
    )

    ship_file = "Test_Engine_1x_LowMass.json"
    thrust_forward = True


class MockTurnScenario(PropulsionScenario):
    """Concrete implementation for turn testing."""

    metadata = TestMetadata(
        test_id="TEST-TURN",
        category="Test",
        subcategory="Propulsion",
        name="Test turn scenario",
        summary="A test scenario for turning",
        conditions=[],
        edge_cases=[],
        expected_outcome="Pass",
        pass_criteria="True",
        max_ticks=50,
    )

    ship_file = "Test_Thruster_Simple.json"
    turn_right = True


@pytest.fixture
def mock_ship():
    """Create a mock ship with propulsion attributes."""
    ship = Mock()
    ship.position = pygame.math.Vector2(100, 50)
    ship.velocity = pygame.math.Vector2(25, 0)
    ship.angle = 15.0
    ship.mass = 400
    ship.total_thrust = 500
    ship.max_speed = 31.25
    ship.turn_speed = 15.625  # degrees per 100 ticks
    ship.is_alive = True
    return ship


@pytest.fixture
def mock_battle_engine():
    """Create a mock outcome-shaped object.

    PROJ-270 Phase 2.5: `collect_results` now takes a `BattleOutcome`
    instead of a live engine. The fixture name is retained for test
    backwards-compat, but it now returns an outcome-shaped mock with
    `duration_ticks` (replaces `tick_counter`) + a few engine-compat
    attributes for tests that still reference `.tick_counter` directly.
    """
    outcome = Mock()
    outcome.duration_ticks = 50
    outcome.tick_counter = 50  # legacy alias for tests that still check it
    return outcome


class TestPropulsionScenarioVelocityResults:
    """Tests that PropulsionScenario stores velocity data."""

    def test_results_include_initial_velocity_magnitude(self, mock_ship, mock_battle_engine):
        """PropulsionScenario.verify() should store initial velocity magnitude."""
        scenario = MockPropulsionScenario()
        scenario.ship = mock_ship
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.start_velocity = pygame.math.Vector2(0, 0)
        scenario.start_angle = 0.0
        scenario.expected_max_speed = 31.25
        scenario.expected_acceleration_rate = 7.8125
        scenario.results = {}

        scenario.collect_results(mock_battle_engine)

        assert 'initial_velocity_magnitude' in scenario.results
        assert scenario.results['initial_velocity_magnitude'] == 0.0

    def test_results_include_final_velocity_magnitude(self, mock_ship, mock_battle_engine):
        """PropulsionScenario.verify() should store final velocity magnitude."""
        scenario = MockPropulsionScenario()
        scenario.ship = mock_ship
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.start_velocity = pygame.math.Vector2(0, 0)
        scenario.start_angle = 0.0
        scenario.expected_max_speed = 31.25
        scenario.expected_acceleration_rate = 7.8125
        scenario.results = {}

        scenario.collect_results(mock_battle_engine)

        assert 'final_velocity_magnitude' in scenario.results
        assert scenario.results['final_velocity_magnitude'] == 25.0  # mock_ship.velocity.length()


class TestPropulsionScenarioPositionResults:
    """Tests that PropulsionScenario stores position data."""

    def test_results_include_initial_position(self, mock_ship, mock_battle_engine):
        """PropulsionScenario.verify() should store initial position as tuple."""
        scenario = MockPropulsionScenario()
        scenario.ship = mock_ship
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.start_velocity = pygame.math.Vector2(0, 0)
        scenario.start_angle = 0.0
        scenario.expected_max_speed = 31.25
        scenario.expected_acceleration_rate = 7.8125
        scenario.results = {}

        scenario.collect_results(mock_battle_engine)

        assert 'initial_position' in scenario.results
        assert scenario.results['initial_position'] == (0, 0)

    def test_results_include_final_position(self, mock_ship, mock_battle_engine):
        """PropulsionScenario.verify() should store final position as tuple."""
        scenario = MockPropulsionScenario()
        scenario.ship = mock_ship
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.start_velocity = pygame.math.Vector2(0, 0)
        scenario.start_angle = 0.0
        scenario.expected_max_speed = 31.25
        scenario.expected_acceleration_rate = 7.8125
        scenario.results = {}

        scenario.collect_results(mock_battle_engine)

        assert 'final_position' in scenario.results
        assert scenario.results['final_position'] == (100, 50)

    def test_results_include_distance_traveled(self, mock_ship, mock_battle_engine):
        """PropulsionScenario.verify() should calculate and store distance traveled."""
        scenario = MockPropulsionScenario()
        scenario.ship = mock_ship
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.start_velocity = pygame.math.Vector2(0, 0)
        scenario.start_angle = 0.0
        scenario.expected_max_speed = 31.25
        scenario.expected_acceleration_rate = 7.8125
        scenario.results = {}

        scenario.collect_results(mock_battle_engine)

        assert 'distance_traveled' in scenario.results
        # Distance from (0,0) to (100, 50) = sqrt(100^2 + 50^2) = 111.8
        expected_distance = pygame.math.Vector2(100, 50).length()
        assert abs(scenario.results['distance_traveled'] - expected_distance) < 0.01


class TestPropulsionScenarioAngleResults:
    """Tests that PropulsionScenario stores angle data."""

    def test_results_include_initial_angle(self, mock_ship, mock_battle_engine):
        """PropulsionScenario.verify() should store initial angle."""
        scenario = MockTurnScenario()
        scenario.ship = mock_ship
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.start_velocity = pygame.math.Vector2(0, 0)
        scenario.start_angle = 0.0
        scenario.expected_max_speed = 31.25
        scenario.expected_acceleration_rate = 7.8125
        scenario.results = {}

        scenario.collect_results(mock_battle_engine)

        assert 'initial_angle' in scenario.results
        assert scenario.results['initial_angle'] == 0.0

    def test_results_include_final_angle(self, mock_ship, mock_battle_engine):
        """PropulsionScenario.verify() should store final angle."""
        scenario = MockTurnScenario()
        scenario.ship = mock_ship
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.start_velocity = pygame.math.Vector2(0, 0)
        scenario.start_angle = 0.0
        scenario.expected_max_speed = 31.25
        scenario.expected_acceleration_rate = 7.8125
        scenario.results = {}

        scenario.collect_results(mock_battle_engine)

        assert 'final_angle' in scenario.results
        assert scenario.results['final_angle'] == 15.0  # mock_ship.angle

    def test_results_include_angle_change(self, mock_ship, mock_battle_engine):
        """PropulsionScenario.verify() should store angle change."""
        scenario = MockTurnScenario()
        scenario.ship = mock_ship
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.start_velocity = pygame.math.Vector2(0, 0)
        scenario.start_angle = 0.0
        scenario.expected_max_speed = 31.25
        scenario.expected_acceleration_rate = 7.8125
        scenario.results = {}

        scenario.collect_results(mock_battle_engine)

        assert 'angle_change' in scenario.results
        assert scenario.results['angle_change'] == 15.0  # final - initial


class TestPropulsionScenarioExpectedAngle:
    """Tests for expected angle change calculation in turn tests."""

    def test_results_include_expected_angle_change(self, mock_ship, mock_battle_engine):
        """Turn tests should calculate expected_angle_change = turn_speed * ticks / 100."""
        scenario = MockTurnScenario()
        scenario.ship = mock_ship
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.start_velocity = pygame.math.Vector2(0, 0)
        scenario.start_angle = 0.0
        scenario.expected_max_speed = 31.25
        scenario.expected_acceleration_rate = 7.8125
        scenario.results = {}

        scenario.collect_results(mock_battle_engine)

        # turn_speed = 15.625 degrees per 100 ticks
        # ticks = 50
        # expected_angle_change = 15.625 * 50 / 100 = 7.8125 degrees
        assert 'expected_angle_change' in scenario.results
        expected = (mock_ship.turn_speed / 100.0) * mock_battle_engine.tick_counter
        assert abs(scenario.results['expected_angle_change'] - expected) < 0.001

    def test_results_include_turn_speed_degrees_per_tick(self, mock_ship, mock_battle_engine):
        """Turn tests should store turn_speed in degrees per tick."""
        scenario = MockTurnScenario()
        scenario.ship = mock_ship
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.start_velocity = pygame.math.Vector2(0, 0)
        scenario.start_angle = 0.0
        scenario.expected_max_speed = 31.25
        scenario.expected_acceleration_rate = 7.8125
        scenario.results = {}

        scenario.collect_results(mock_battle_engine)

        assert 'turn_speed_degrees_per_tick' in scenario.results
        # turn_speed / 100 = degrees per tick
        assert scenario.results['turn_speed_degrees_per_tick'] == 15.625 / 100.0

    def test_no_expected_angle_for_zero_turn_speed(self, mock_battle_engine):
        """Ships with zero turn_speed should not have expected_angle_change."""
        mock_ship_no_turn = Mock()
        mock_ship_no_turn.position = pygame.math.Vector2(100, 0)
        mock_ship_no_turn.velocity = pygame.math.Vector2(25, 0)
        mock_ship_no_turn.angle = 0.0
        mock_ship_no_turn.mass = 400
        mock_ship_no_turn.total_thrust = 500
        mock_ship_no_turn.max_speed = 31.25
        mock_ship_no_turn.turn_speed = 0.0  # No thruster
        mock_ship_no_turn.is_alive = True

        scenario = MockPropulsionScenario()
        scenario.ship = mock_ship_no_turn
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.start_velocity = pygame.math.Vector2(0, 0)
        scenario.start_angle = 0.0
        scenario.expected_max_speed = 31.25
        scenario.expected_acceleration_rate = 7.8125
        scenario.results = {}

        scenario.collect_results(mock_battle_engine)

        # For ships with turn_speed=0, expected_angle_change should not be calculated
        # or should be 0
        if 'expected_angle_change' in scenario.results:
            assert scenario.results['expected_angle_change'] == 0.0


class TestPropulsionScenarioExpectedVelocity:
    """Tests for expected max speed storage."""

    def test_results_include_expected_max_speed(self, mock_ship, mock_battle_engine):
        """PropulsionScenario.verify() should store expected max_speed."""
        scenario = MockPropulsionScenario()
        scenario.ship = mock_ship
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.start_velocity = pygame.math.Vector2(0, 0)
        scenario.start_angle = 0.0
        scenario.expected_max_speed = 31.25
        scenario.expected_acceleration_rate = 7.8125
        scenario.results = {}

        scenario.collect_results(mock_battle_engine)

        assert 'expected_max_speed' in scenario.results
        assert scenario.results['expected_max_speed'] == 31.25

    def test_results_include_expected_acceleration_rate(self, mock_ship, mock_battle_engine):
        """PropulsionScenario.verify() should store expected acceleration rate."""
        scenario = MockPropulsionScenario()
        scenario.ship = mock_ship
        scenario.start_position = pygame.math.Vector2(0, 0)
        scenario.start_velocity = pygame.math.Vector2(0, 0)
        scenario.start_angle = 0.0
        scenario.expected_max_speed = 31.25
        scenario.expected_acceleration_rate = 7.8125
        scenario.results = {}

        scenario.collect_results(mock_battle_engine)

        assert 'expected_acceleration_rate' in scenario.results
        assert scenario.results['expected_acceleration_rate'] == 7.8125
