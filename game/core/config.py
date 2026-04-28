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

    # Navigation thresholds (degrees)
    NAVIGATION_ROTATION_DEADBAND: float = 5.0   # Don't rotate if within this angle
    NAVIGATION_THRUST_ANGLE_MAX: float = 30.0   # Only thrust if facing target within this angle


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


class BattleTuning:
    """Battle simulation tuning constants.

    Renamed from BattleConfig (PROJ-224 DUP-SYS-003) to avoid ambiguity
    with game.simulation.battle_config.BattleConfig (per-battle instance config).
    """

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


class LLMConfig:
    """Tunable defaults for the LLM service (PROJ-296).

    Plain class with class-level attributes (NOT @dataclass) per
    docs/02_PATTERNS.md Pattern 12.

    All fields can be overridden per-call via `LLMProvider.complete()`'s
    explicit kwargs. Override these at the class level for application-wide
    tuning; do not mutate per-instance.
    """

    # Timeouts (seconds)
    DEFAULT_TIMEOUT_SECONDS: float = 60.0
    CONNECT_TIMEOUT_SECONDS: float = 5.0

    # Completion knobs (defaults; consumer can override per call)
    DEFAULT_MAX_TOKENS: int = 4096
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MODEL: str = "deepseek-v4-flash"

    # Retry policy
    # Exponential backoff on 5xx only; never auto-retry on 429 (rate-limit
    # is a clear back-off signal, not a transient failure).
    MAX_RETRIES_5XX: int = 2
    RETRY_BACKOFF_BASE_SECONDS: float = 1.0

    # Concurrency safeguard. Enforced by LLMBackgroundCall.start().
    MAX_CONCURRENT_CALLS: int = 3

    # API citizenship
    USER_AGENT: str = "starship-battles-llm/1.0"


class ImageConfig:
    """Tunable defaults for the image-generation service (PROJ-314).

    Plain class with class-level attributes (NOT @dataclass) per
    docs/02_PATTERNS.md Pattern 12. Mirrors `LLMConfig`.

    All fields can be overridden per-call via
    `ImageProvider.generate_image()`. Override these at the class level
    for application-wide tuning; do not mutate per-instance.
    """

    # Timeouts (seconds). Image generation is slower than chat, so the
    # default read timeout is generous.
    DEFAULT_TIMEOUT_SECONDS: float = 120.0
    CONNECT_TIMEOUT_SECONDS: float = 10.0

    # Defaults
    DEFAULT_MODEL: str = "gpt-image-2"
    DEFAULT_SIZE: str = "2048x2048"

    # Retry policy. Exponential backoff on 5xx only; never retry 429.
    MAX_RETRIES_5XX: int = 2
    RETRY_BACKOFF_BASE_SECONDS: float = 1.0

    # Concurrency safeguard. Enforced by ImageBackgroundCall.start().
    MAX_CONCURRENT_CALLS: int = 2

    # API citizenship
    USER_AGENT: str = "starship-battles-image/1.0"


# UIConfig has been moved to game.ui.config (PROJ-113)
# Import from game.ui.config directly


