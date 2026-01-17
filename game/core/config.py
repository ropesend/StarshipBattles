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

    # Explicit 4K resolution constants
    RESOLUTION_4K_WIDTH: int = 3840
    RESOLUTION_4K_HEIGHT: int = 2160

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
    FORMATION_SLOWDOWN_THRESHOLD: float = 0.5
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

    # Speed limits
    DEFAULT_MAX_SPEED: float = 1000.0

    # Angle thresholds for movement decisions
    THRUST_ANGLE_THRESHOLD: float = 30.0
    ROTATION_ANGLE_THRESHOLD: float = 5.0

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
    """UI layout and sizing configuration."""

    # Builder panel dimensions
    BUILDER_PANEL_WIDTH: int = 300
    BUILDER_PANEL_HEIGHT: int = 600

    # Default panel margins
    PANEL_MARGIN: int = 10
    PANEL_PADDING: int = 5

    # Panel gaps and spacing
    PANEL_GAP: int = 5
    ELEMENT_SPACING: int = 16
    INDENT: int = 20

    # Font sizes (pygame.font.Font None-font sizes)
    FONT_TITLE: int = 28
    FONT_NAME: int = 22
    FONT_STAT: int = 18
    FONT_BODY: int = 12
    FONT_HEADER: int = 16
    FONT_LARGE: int = 36
    FONT_XLARGE: int = 48
    FONT_XXLARGE: int = 64

    # Battle screen panel dimensions
    STATS_PANEL_WIDTH: int = 450
    SEEKER_PANEL_WIDTH: int = 300

    # Strategy screen dimensions
    STRATEGY_SIDEBAR_WIDTH: int = 600
    STRATEGY_BUTTON_WIDTH: int = 150
    STRATEGY_BUTTON_HEIGHT: int = 35

    # Common button dimensions
    BUTTON_WIDTH_SMALL: int = 150
    BUTTON_WIDTH_MEDIUM: int = 250
    BUTTON_WIDTH_LARGE: int = 300
    BUTTON_HEIGHT_SMALL: int = 35
    BUTTON_HEIGHT_MEDIUM: int = 50
    BUTTON_HEIGHT_LARGE: int = 60

    # Progress/stat bar dimensions
    BAR_WIDTH: int = 120
    BAR_HEIGHT: int = 10
    BANNER_HEIGHT: int = 22

    # Ship entry dimensions in panels
    SHIP_ENTRY_HEIGHT: int = 25

    # Window dimensions (dialogs/popups)
    DIALOG_WIDTH_SMALL: int = 300
    DIALOG_WIDTH_MEDIUM: int = 500
    DIALOG_WIDTH_LARGE: int = 800
    DIALOG_HEIGHT_SMALL: int = 150
    DIALOG_HEIGHT_MEDIUM: int = 300
    DIALOG_HEIGHT_LARGE: int = 500

    # Scroll settings
    SCROLL_SPEED: int = 30

    # Panel transparency (alpha values 0-255)
    PANEL_ALPHA: int = 230
    OVERLAY_ALPHA: int = 180

    # Battle screen
    GRID_SPACING: int = 5000
    TRAIL_LENGTH: int = 100

    # Common dimensions
    ROW_HEIGHT_STANDARD: int = 40
    ROW_HEIGHT_LARGE: int = 50
    SIDEBAR_WIDTH: int = 300
    HEADER_HEIGHT: int = 40


class TestConfig:
    """Configuration specific to testing."""

    # Random seed for deterministic tests
    DEFAULT_RANDOM_SEED: int = 42

    # Timeout values (milliseconds)
    DEFAULT_TIMEOUT_MS: int = 5000
    LONG_TIMEOUT_MS: int = 30000
