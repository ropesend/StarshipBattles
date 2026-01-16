"""
Tests for configuration module.

These configuration classes centralize magic numbers and constants
used throughout the codebase.
"""
import pytest


class TestDisplayConfig:
    """Tests for DisplayConfig."""

    def test_default_resolution_values(self):
        """Default resolution values are correct."""
        from game.core.config import DisplayConfig

        assert DisplayConfig.DEFAULT_WIDTH == 2560
        assert DisplayConfig.DEFAULT_HEIGHT == 1600

    def test_test_resolution_values(self):
        """Test resolution values are correct."""
        from game.core.config import DisplayConfig

        assert DisplayConfig.TEST_WIDTH == 1440
        assert DisplayConfig.TEST_HEIGHT == 900

    def test_default_resolution_tuple(self):
        """default_resolution() returns tuple."""
        from game.core.config import DisplayConfig

        resolution = DisplayConfig.default_resolution()
        assert resolution == (2560, 1600)
        assert isinstance(resolution, tuple)

    def test_test_resolution_tuple(self):
        """test_resolution() returns tuple."""
        from game.core.config import DisplayConfig

        resolution = DisplayConfig.test_resolution()
        assert resolution == (1440, 900)


class TestAIConfig:
    """Tests for AIConfig."""

    def test_spacing_values(self):
        """Spacing values are correct."""
        from game.core.config import AIConfig

        assert AIConfig.MIN_SPACING == 150
        assert AIConfig.DEFAULT_ORBIT_DISTANCE == 500
        assert AIConfig.MAX_CORRECTION_FORCE == 500

    def test_values_are_integers(self):
        """Spacing values are integers."""
        from game.core.config import AIConfig

        assert isinstance(AIConfig.MIN_SPACING, int)
        assert isinstance(AIConfig.DEFAULT_ORBIT_DISTANCE, int)


class TestPhysicsConfig:
    """Tests for PhysicsConfig."""

    def test_tick_rate(self):
        """Tick rate is correct."""
        from game.core.config import PhysicsConfig

        assert PhysicsConfig.TICK_RATE == 0.01

    def test_speed_values(self):
        """Speed values are correct."""
        from game.core.config import PhysicsConfig

        assert PhysicsConfig.DEFAULT_MAX_SPEED == 1000.0
        assert isinstance(PhysicsConfig.DEFAULT_MAX_SPEED, float)


class TestBattleConfig:
    """Tests for BattleConfig."""

    def test_query_radius(self):
        """Query radius values are correct."""
        from game.core.config import BattleConfig

        assert BattleConfig.TARGET_QUERY_RADIUS == 200000
        assert BattleConfig.MISSILE_QUERY_RADIUS == 1500

    def test_collision_values(self):
        """Collision detection values are correct."""
        from game.core.config import BattleConfig

        assert BattleConfig.COLLISION_BUFFER == 100


class TestUIConfig:
    """Tests for UIConfig."""

    def test_panel_dimensions(self):
        """Panel dimension values exist."""
        from game.core.config import UIConfig

        assert hasattr(UIConfig, 'BUILDER_PANEL_WIDTH')
        assert isinstance(UIConfig.BUILDER_PANEL_WIDTH, int)
