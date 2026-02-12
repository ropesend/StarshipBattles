"""
Unit tests for configuration classes edge cases.

Tests resolution tuples, AIConfig boundary values,
and PhysicsConfig constraints.
"""
import pytest

from game.core.config import DisplayConfig, AIConfig, PhysicsConfig


class TestDisplayConfigResolutions:
    """Tests for DisplayConfig resolution methods."""

    def test_default_resolution_tuple(self):
        """Returns (3840, 2160) 4K resolution."""
        result = DisplayConfig.default_resolution()
        assert result == (3840, 2160)
        assert isinstance(result, tuple)

    def test_windowed_resolution_tuple(self):
        """Returns (2560, 1600) windowed resolution."""
        result = DisplayConfig.windowed_resolution()
        assert result == (2560, 1600)
        assert isinstance(result, tuple)

    def test_test_resolution_tuple(self):
        """Returns (1440, 900) test resolution."""
        result = DisplayConfig.test_resolution()
        assert result == (1440, 900)
        assert isinstance(result, tuple)

    def test_resolution_values_positive(self):
        """All resolution values are positive integers."""
        assert DisplayConfig.DEFAULT_WIDTH > 0
        assert DisplayConfig.DEFAULT_HEIGHT > 0
        assert DisplayConfig.WINDOWED_WIDTH > 0
        assert DisplayConfig.WINDOWED_HEIGHT > 0
        assert DisplayConfig.TEST_WIDTH > 0
        assert DisplayConfig.TEST_HEIGHT > 0


class TestAIConfigBoundaryValues:
    """Tests for AIConfig boundary values."""

    def test_min_spacing_positive(self):
        """MIN_SPACING is positive."""
        assert AIConfig.MIN_SPACING > 0

    def test_flee_distance_greater_than_orbit(self):
        """FLEE_DISTANCE is greater than DEFAULT_ORBIT_DISTANCE."""
        assert AIConfig.FLEE_DISTANCE > AIConfig.DEFAULT_ORBIT_DISTANCE

    def test_formation_throttle_0_to_1(self):
        """FORMATION_ENGINE_THROTTLE is in (0, 1] range."""
        assert 0 < AIConfig.FORMATION_ENGINE_THROTTLE <= 1

    def test_formation_slowdown_throttle_valid(self):
        """FORMATION_SLOWDOWN_THROTTLE is in valid range."""
        assert 0 < AIConfig.FORMATION_SLOWDOWN_THROTTLE <= 1

    def test_default_orbit_distance_positive(self):
        """DEFAULT_ORBIT_DISTANCE is positive."""
        assert AIConfig.DEFAULT_ORBIT_DISTANCE > 0

    def test_max_correction_force_positive(self):
        """MAX_CORRECTION_FORCE is positive."""
        assert AIConfig.MAX_CORRECTION_FORCE > 0

    def test_erratic_turn_interval_range(self):
        """ERRATIC_TURN_INTERVAL_MIN < MAX."""
        assert AIConfig.ERRATIC_TURN_INTERVAL_MIN < AIConfig.ERRATIC_TURN_INTERVAL_MAX
        assert AIConfig.ERRATIC_TURN_INTERVAL_MIN > 0


class TestPhysicsConfigConstraints:
    """Tests for PhysicsConfig constraints."""

    def test_tick_rate_positive(self):
        """TICK_RATE is positive."""
        assert PhysicsConfig.TICK_RATE > 0

    def test_tick_rate_reasonable(self):
        """TICK_RATE is a reasonable small value (not too large)."""
        # Should be less than 1 second per tick for real-time simulation
        assert PhysicsConfig.TICK_RATE < 1.0

    def test_spatial_grid_cell_size_positive(self):
        """SPATIAL_GRID_CELL_SIZE is positive."""
        assert PhysicsConfig.SPATIAL_GRID_CELL_SIZE > 0

    def test_default_drag_values_positive(self):
        """Drag values are positive."""
        assert PhysicsConfig.DEFAULT_LINEAR_DRAG > 0
        assert PhysicsConfig.DEFAULT_ANGULAR_DRAG > 0

    def test_default_base_radius_positive(self):
        """DEFAULT_BASE_RADIUS is positive."""
        assert PhysicsConfig.DEFAULT_BASE_RADIUS > 0

    def test_reference_mass_positive(self):
        """REFERENCE_MASS is positive."""
        assert PhysicsConfig.REFERENCE_MASS > 0
