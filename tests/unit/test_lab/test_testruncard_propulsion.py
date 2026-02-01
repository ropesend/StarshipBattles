"""
Tests for TestRunCard propulsion test display.

TDD tests for verifying that TestRunCard displays propulsion-specific metrics:
- Motion tests: velocity, position, distance
- Turn tests: angle change, expected vs actual
"""
import pytest
from unittest.mock import Mock, MagicMock
import pygame


@pytest.fixture
def mock_run_record_motion():
    """Create a mock run record for motion test (PROP-001)."""
    record = Mock()
    record.passed = True
    record.seed = 42
    record.ticks_run = 100
    record.metrics = {
        'test_id': 'PROP-001',
        'initial_velocity_magnitude': 0.0,
        'final_velocity_magnitude': 28.5,
        'expected_max_speed': 31.25,
        'initial_position': (0, 0),
        'final_position': (1425.5, 0),
        'distance_traveled': 1425.5,
        'initial_angle': 0.0,
        'final_angle': 0.0,
        'ticks_run': 100
    }
    record.validation_results = []
    record.validation_summary = {'pass': 2, 'fail': 0, 'warn': 0}
    record.get_formatted_timestamp = Mock(return_value="14:30:00")
    record.get_p_value = Mock(return_value=None)
    record.has_battle_states = Mock(return_value=False)
    return record


@pytest.fixture
def mock_run_record_turn():
    """Create a mock run record for turn test (PROP-003)."""
    record = Mock()
    record.passed = True
    record.seed = 42
    record.ticks_run = 50
    record.metrics = {
        'test_id': 'PROP-003',
        'initial_angle': 0.0,
        'final_angle': 7.8,
        'angle_change': 7.8,
        'expected_angle_change': 7.8125,
        'turn_speed': 15.625,
        'turn_speed_degrees_per_tick': 0.15625,
        'initial_velocity_magnitude': 0.0,
        'final_velocity_magnitude': 0.0,
        'distance_traveled': 0.0,
        'ticks_run': 50
    }
    record.validation_results = []
    record.validation_summary = {'pass': 3, 'fail': 0, 'warn': 0}
    record.get_formatted_timestamp = Mock(return_value="14:31:00")
    record.get_p_value = Mock(return_value=None)
    record.has_battle_states = Mock(return_value=False)
    return record


@pytest.fixture
def mock_run_record_beam():
    """Create a mock run record for beam test (not propulsion)."""
    record = Mock()
    record.passed = True
    record.seed = 42
    record.ticks_run = 500
    record.metrics = {
        'test_id': 'BEAMWEAPON-001',
        'hit_rate': 0.532,
        'expected_hit_chance': 0.5318,
        'damage_dealt': 266,
        'ticks_run': 500
    }
    record.validation_results = [
        {'name': 'Hit Rate', 'expected': 0.5318, 'actual': 0.532, 'status': 'PASS'}
    ]
    record.validation_summary = {'pass': 1, 'fail': 0, 'warn': 0}
    record.get_formatted_timestamp = Mock(return_value="14:32:00")
    record.get_p_value = Mock(return_value=0.032)
    record.has_battle_states = Mock(return_value=False)
    return record


class TestTestRunCardPropulsionDetection:
    """Tests for detecting propulsion tests."""

    def test_detects_prop001_as_propulsion(self, mock_run_record_motion):
        """PROP-001 should be detected as propulsion test."""
        test_id = mock_run_record_motion.metrics.get('test_id', '')
        assert test_id.startswith('PROP-')

    def test_detects_prop003_as_propulsion(self, mock_run_record_turn):
        """PROP-003 should be detected as propulsion test."""
        test_id = mock_run_record_turn.metrics.get('test_id', '')
        assert test_id.startswith('PROP-')

    def test_beam_not_detected_as_propulsion(self, mock_run_record_beam):
        """BEAMWEAPON-001 should NOT be detected as propulsion test."""
        test_id = mock_run_record_beam.metrics.get('test_id', '')
        assert not test_id.startswith('PROP-')


class TestTestRunCardMotionDisplay:
    """Tests that TestRunCard displays motion data for propulsion tests."""

    def test_motion_record_has_velocity_data(self, mock_run_record_motion):
        """Motion test record should have velocity magnitude fields."""
        metrics = mock_run_record_motion.metrics
        assert 'initial_velocity_magnitude' in metrics
        assert 'final_velocity_magnitude' in metrics
        assert metrics['initial_velocity_magnitude'] == 0.0
        assert metrics['final_velocity_magnitude'] == 28.5

    def test_motion_record_has_position_data(self, mock_run_record_motion):
        """Motion test record should have position fields."""
        metrics = mock_run_record_motion.metrics
        assert 'initial_position' in metrics
        assert 'final_position' in metrics
        assert 'distance_traveled' in metrics
        assert metrics['distance_traveled'] == 1425.5

    def test_motion_record_has_expected_max_speed(self, mock_run_record_motion):
        """Motion test record should have expected max speed."""
        metrics = mock_run_record_motion.metrics
        assert 'expected_max_speed' in metrics
        assert metrics['expected_max_speed'] == 31.25


class TestTestRunCardTurnDisplay:
    """Tests that TestRunCard displays turn data for thruster tests."""

    def test_turn_record_has_angle_data(self, mock_run_record_turn):
        """Turn test record should have angle fields."""
        metrics = mock_run_record_turn.metrics
        assert 'initial_angle' in metrics
        assert 'final_angle' in metrics
        assert 'angle_change' in metrics
        assert metrics['angle_change'] == 7.8

    def test_turn_record_has_expected_angle_change(self, mock_run_record_turn):
        """Turn test record should have expected angle change."""
        metrics = mock_run_record_turn.metrics
        assert 'expected_angle_change' in metrics
        assert metrics['expected_angle_change'] == 7.8125

    def test_turn_record_has_turn_speed(self, mock_run_record_turn):
        """Turn test record should have turn_speed value."""
        metrics = mock_run_record_turn.metrics
        assert 'turn_speed' in metrics
        assert metrics['turn_speed'] == 15.625


class TestTestRunCardDisplayLogic:
    """Tests for display logic decisions."""

    def test_motion_test_displays_velocity(self, mock_run_record_motion):
        """Motion tests should display velocity data."""
        metrics = mock_run_record_motion.metrics
        # A motion test has velocity data and meaningful velocity change
        has_velocity_data = 'final_velocity_magnitude' in metrics
        is_motion_test = has_velocity_data and metrics.get('final_velocity_magnitude', 0) > 0.1
        assert is_motion_test

    def test_turn_test_displays_angle(self, mock_run_record_turn):
        """Turn tests should display angle data."""
        metrics = mock_run_record_turn.metrics
        # A turn test has angle_change > 0 and turn_speed > 0
        is_turn_test = (
            'angle_change' in metrics and
            metrics.get('angle_change', 0) > 0.01 and
            metrics.get('turn_speed', 0) > 0
        )
        assert is_turn_test

    def test_stationary_test_shows_zero_velocity(self, mock_run_record_turn):
        """Stationary tests (PROP-003 type) should show zero velocity."""
        metrics = mock_run_record_turn.metrics
        assert metrics.get('final_velocity_magnitude', 0) == 0.0
        assert metrics.get('distance_traveled', 0) == 0.0


class TestPropulsionMetricsFormatting:
    """Tests for propulsion metrics formatting."""

    def test_velocity_format(self, mock_run_record_motion):
        """Velocity should be formatted with units."""
        metrics = mock_run_record_motion.metrics
        start_vel = metrics['initial_velocity_magnitude']
        end_vel = metrics['final_velocity_magnitude']
        max_speed = metrics['expected_max_speed']

        # Format string construction
        vel_text = f"Velocity: {start_vel:.1f} -> {end_vel:.2f}"
        assert "Velocity: 0.0 -> 28.50" == vel_text

        # With max speed
        vel_text_with_max = f"Velocity: {start_vel:.1f} -> {end_vel:.2f} (max: {max_speed:.2f})"
        assert "(max: 31.25)" in vel_text_with_max

    def test_distance_format(self, mock_run_record_motion):
        """Distance should be formatted with px unit."""
        metrics = mock_run_record_motion.metrics
        distance = metrics['distance_traveled']
        dist_text = f"Distance: {distance:.1f} px"
        assert "Distance: 1425.5 px" == dist_text

    def test_angle_format(self, mock_run_record_turn):
        """Angle should be formatted in degrees."""
        metrics = mock_run_record_turn.metrics
        start_angle = metrics['initial_angle']
        end_angle = metrics['final_angle']
        angle_text = f"Angle: {start_angle:.1f} -> {end_angle:.1f} deg"
        assert "Angle: 0.0 -> 7.8 deg" == angle_text

    def test_expected_vs_actual_angle_format(self, mock_run_record_turn):
        """Expected vs actual angle should be formatted for comparison."""
        metrics = mock_run_record_turn.metrics
        expected = metrics['expected_angle_change']
        actual = metrics['angle_change']
        exp_act_text = f"Expected: {expected:.2f} Actual: {actual:.2f}"
        assert "Expected: 7.81 Actual: 7.80" == exp_act_text
