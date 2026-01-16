"""
Centralized configuration constants for the Starship Battles game.

This module consolidates magic numbers and configuration values that were
previously scattered across multiple files. Using these classes makes the
codebase more maintainable and self-documenting.

Usage:
    from game.core.config import DisplayConfig, AIConfig, PhysicsConfig

    width, height = DisplayConfig.default_resolution()
    spacing = AIConfig.MIN_SPACING
    tick = PhysicsConfig.TICK_RATE
"""
from typing import Tuple


class DisplayConfig:
    """Display and resolution configuration."""

    # Default game resolution
    DEFAULT_WIDTH: int = 2560
    DEFAULT_HEIGHT: int = 1600

    # Test/headless resolution
    TEST_WIDTH: int = 1440
    TEST_HEIGHT: int = 900

    @classmethod
    def default_resolution(cls) -> Tuple[int, int]:
        """Return default resolution as tuple."""
        return (cls.DEFAULT_WIDTH, cls.DEFAULT_HEIGHT)

    @classmethod
    def test_resolution(cls) -> Tuple[int, int]:
        """Return test resolution as tuple."""
        return (cls.TEST_WIDTH, cls.TEST_HEIGHT)


class AIConfig:
    """AI behavior configuration."""

    # Spacing and distance constants
    MIN_SPACING: int = 150
    DEFAULT_ORBIT_DISTANCE: int = 500
    MAX_CORRECTION_FORCE: int = 500

    # Formation settings
    FORMATION_SLOWDOWN_THRESHOLD: float = 0.5
    FORMATION_ENGINE_THROTTLE: float = 0.9
    FORMATION_SLOWDOWN_THROTTLE: float = 0.75


class PhysicsConfig:
    """Physics simulation configuration."""

    # Tick rate (seconds per tick)
    TICK_RATE: float = 0.01

    # Speed limits
    DEFAULT_MAX_SPEED: float = 1000.0

    # Angle thresholds for movement decisions
    THRUST_ANGLE_THRESHOLD: float = 30.0
    ROTATION_ANGLE_THRESHOLD: float = 5.0


class BattleConfig:
    """Battle simulation configuration."""

    # Query radius for finding targets
    TARGET_QUERY_RADIUS: int = 200000
    MISSILE_QUERY_RADIUS: int = 1500

    # Collision detection
    COLLISION_BUFFER: int = 100
    AVOIDANCE_RADIUS: int = 1000
    AVOIDANCE_TARGET_DISTANCE: int = 500


class UIConfig:
    """UI layout and sizing configuration."""

    # Builder panel dimensions
    BUILDER_PANEL_WIDTH: int = 300
    BUILDER_PANEL_HEIGHT: int = 600

    # Default panel margins
    PANEL_MARGIN: int = 10
    PANEL_PADDING: int = 5

    # Font sizes
    HEADER_FONT_SIZE: int = 16
    BODY_FONT_SIZE: int = 12


class TestConfig:
    """Configuration specific to testing."""

    # Random seed for deterministic tests
    DEFAULT_RANDOM_SEED: int = 42

    # Timeout values (milliseconds)
    DEFAULT_TIMEOUT_MS: int = 5000
    LONG_TIMEOUT_MS: int = 30000
