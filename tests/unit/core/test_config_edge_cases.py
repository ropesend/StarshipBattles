"""
Unit tests for configuration classes edge cases.

Tests resolution tuples, AIConfig boundary values,
and PhysicsConfig constraints.
"""
import pytest

from game.core.config import DisplayConfig, AIConfig, PhysicsConfig


class TestDisplayConfigResolutions:
    """Tests for DisplayConfig resolution methods."""

    def test_windowed_resolution_tuple(self):
        """Returns (2560, 1600) windowed resolution."""
        result = DisplayConfig.windowed_resolution()
        assert result == (2560, 1600)
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
    """Tests for AIConfig boundary values.

    PROJ-323 Task 3.8: positive-attr tests parametrized.
    """

    @pytest.mark.parametrize("attr_name", [
        "MIN_SPACING",
        "DEFAULT_ORBIT_DISTANCE",
        "MAX_CORRECTION_FORCE",
    ])
    def test_attr_positive(self, attr_name):
        """AIConfig positive-value attributes are > 0."""
        assert getattr(AIConfig, attr_name) > 0

    def test_flee_distance_greater_than_orbit(self):
        """FLEE_DISTANCE is greater than DEFAULT_ORBIT_DISTANCE."""
        assert AIConfig.FLEE_DISTANCE > AIConfig.DEFAULT_ORBIT_DISTANCE

    @pytest.mark.parametrize("attr_name", [
        "FORMATION_ENGINE_THROTTLE",
        "FORMATION_SLOWDOWN_THROTTLE",
    ])
    def test_throttle_in_unit_range(self, attr_name):
        """Throttle values are in (0, 1] range."""
        assert 0 < getattr(AIConfig, attr_name) <= 1

    def test_erratic_turn_interval_range(self):
        """ERRATIC_TURN_INTERVAL_MIN < MAX."""
        assert AIConfig.ERRATIC_TURN_INTERVAL_MIN < AIConfig.ERRATIC_TURN_INTERVAL_MAX
        assert AIConfig.ERRATIC_TURN_INTERVAL_MIN > 0


class TestPhysicsConfigConstraints:
    """Tests for PhysicsConfig constraints.

    PROJ-323 Task 3.8: positive-attr tests parametrized.
    """

    @pytest.mark.parametrize("attr_name", [
        "TICK_RATE",
        "SPATIAL_GRID_CELL_SIZE",
        "DEFAULT_LINEAR_DRAG",
        "DEFAULT_ANGULAR_DRAG",
        "DEFAULT_BASE_RADIUS",
        "REFERENCE_MASS",
    ])
    def test_attr_positive(self, attr_name):
        """PhysicsConfig positive-value attributes are > 0."""
        assert getattr(PhysicsConfig, attr_name) > 0

    def test_tick_rate_reasonable(self):
        """TICK_RATE is a reasonable small value (not too large)."""
        # Should be less than 1 second per tick for real-time simulation
        assert PhysicsConfig.TICK_RATE < 1.0
