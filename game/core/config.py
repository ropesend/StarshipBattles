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

    # Primary (4K) resolution - used for game window
    DEFAULT_WIDTH: int = 3840
    DEFAULT_HEIGHT: int = 2160

    # Secondary (windowed) resolution
    WINDOWED_WIDTH: int = 2560
    WINDOWED_HEIGHT: int = 1600

    # Test/headless resolution
    TEST_WIDTH: int = 1440
    TEST_HEIGHT: int = 900

    @classmethod
    def default_resolution(cls) -> Tuple[int, int]:
        """Return default resolution as tuple."""
        return (cls.DEFAULT_WIDTH, cls.DEFAULT_HEIGHT)

    @classmethod
    def windowed_resolution(cls) -> Tuple[int, int]:
        """Return windowed resolution as tuple."""
        return (cls.WINDOWED_WIDTH, cls.WINDOWED_HEIGHT)

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
    FLEE_DISTANCE: int = 1000

    # Formation settings
    FORMATION_ENGINE_THROTTLE: float = 0.9
    FORMATION_SLOWDOWN_THROTTLE: float = 0.75

    # Formation behavior (fine-tuning)
    FORMATION_DRIFT_THRESHOLD_FACTOR: float = 1.2
    FORMATION_DRIFT_DIAMETER_MULT: float = 2.0
    FORMATION_TURN_SPEED_FACTOR: float = 100.0
    FORMATION_TURN_PREDICT_FACTOR: float = 1.5
    FORMATION_DEADBAND_ERROR: float = 2.0
    FORMATION_CORRECTION_FACTOR: float = 0.2
    FORMATION_PREDICTION_TICKS: int = 10
    FORMATION_NAVIGATE_STOP_DIST: int = 10

    # Attack run behavior
    ATTACK_RUN_APPROACH_DIST_FACTOR: float = 0.3
    ATTACK_RUN_RETREAT_DIST_FACTOR: float = 0.8
    ATTACK_RUN_RETREAT_DURATION: float = 2.0
    ATTACK_RUN_APPROACH_HYSTERESIS: float = 1.5

    # Erratic behavior
    ERRATIC_TURN_INTERVAL_MIN: float = 0.5
    ERRATIC_TURN_INTERVAL_MAX: float = 2.0

    # Orbit behavior
    ORBIT_DISTANCE_CLOSE_THRESHOLD: float = 0.9
    ORBIT_DISTANCE_FAR_THRESHOLD: float = 1.1
    ORBIT_RADIAL_COMPONENT: float = 0.5
    ORBIT_TARGET_OFFSET: int = 200


class PhysicsConfig:
    """Physics simulation configuration."""

    # Tick rate (seconds per tick)
    TICK_RATE: float = 0.01

    # Drag coefficients (applied per tick to prevent infinite drift)
    DEFAULT_LINEAR_DRAG: float = 0.5
    DEFAULT_ANGULAR_DRAG: float = 0.5

    # Spatial grid configuration
    SPATIAL_GRID_CELL_SIZE: int = 2000

    # Ship physics defaults
    DEFAULT_BASE_RADIUS: int = 40
    REFERENCE_MASS: int = 1000


class BattleConfig:
    """Battle simulation configuration."""

    # Query radius for finding targets
    TARGET_QUERY_RADIUS: int = 200000
    MISSILE_QUERY_RADIUS: int = 1500

    # Collision detection
    COLLISION_BUFFER: int = 100
    AVOIDANCE_RADIUS: int = 1000
    AVOIDANCE_TARGET_DISTANCE: int = 500

    # Damage constants
    GUARANTEED_KILL_DAMAGE: int = 9999
    RAMMING_DAMAGE_FACTOR: float = 0.5

    # Projectile collision
    PROJECTILE_QUERY_BUFFER: int = 100
    PROJECTILE_HIT_TOLERANCE: int = 5

    # Missile and fighter constants
    MISSILE_INTERCEPT_BUFFER: int = 10
    FIGHTER_LAUNCH_SPEED: int = 100


class UIConfig:
    """UI layout and sizing configuration.

    This class consolidates UI magic numbers that were scattered across screens.
    When adding new UI code, check here for existing constants before creating
    hardcoded values. When migrating existing code, replace magic numbers with
    these constants.

    Migration pattern:
        # Before:
        toast_rect = pygame.Rect(0, 0, 300, 60)

        # After:
        from game.core.config import UIConfig
        toast_rect = pygame.Rect(0, 0, UIConfig.TOAST_WIDTH, UIConfig.TOAST_HEIGHT)

    See also:
        - game.ui.screens.builder_utils: Builder-specific layout constants
    """

    # Default panel margins
    PANEL_PADDING: int = 5

    # Panel gaps and spacing
    PANEL_GAP: int = 5
    ELEMENT_SPACING: int = 16
    INDENT: int = 20

    # Toast notification dimensions
    TOAST_WIDTH: int = 300
    TOAST_HEIGHT: int = 60

    # Confirmation dialog dimensions
    CONFIRM_DIALOG_WIDTH: int = 400
    CONFIRM_DIALOG_HEIGHT: int = 200

    # Font sizes (pygame.font.Font None-font sizes)
    FONT_TITLE: int = 28
    FONT_NAME: int = 22
    FONT_STAT: int = 18
    # Battle screen panel dimensions
    STATS_PANEL_WIDTH: int = 450
    SEEKER_PANEL_WIDTH: int = 300

    # Strategy screen dimensions
    STRATEGY_SIDEBAR_WIDTH: int = 600

    # Progress/stat bar dimensions
    BAR_WIDTH: int = 120
    BAR_HEIGHT: int = 10
    BANNER_HEIGHT: int = 22

    # Ship entry dimensions in panels
    SHIP_ENTRY_HEIGHT: int = 25

    # Panel transparency (alpha values 0-255)
    PANEL_ALPHA: int = 230

    # Battle screen
    GRID_SPACING: int = 5000
    TRAIL_LENGTH: int = 100

    # Common dimensions
    ROW_HEIGHT_STANDARD: int = 40
    ROW_HEIGHT_LARGE: int = 50
    SIDEBAR_WIDTH: int = 300
    HEADER_HEIGHT: int = 40


