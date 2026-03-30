from enum import Enum, IntEnum

from game.core.config import PhysicsConfig

__all__ = [
    'AttackType',
    'GameState',
    'LayerType',
    'LayerDefaults',
    'CombatConstants',
    'SimulationConstants',
    'PLANET_RESOURCES',
    'ResourceType',
    'EARTH_MASS',
    # Feature flags
    'ENABLE_SCREENSHOTS',
    # PROJ-113: Colors and FONT_MAIN moved to game.ui.colors
]


class AttackType(Enum):
    PROJECTILE = "projectile"
    MISSILE = "missile"
    BEAM = "beam"
    LAUNCH = "launch"


class GameState(IntEnum):
    MENU = 0
    BUILDER = 1
    BATTLE = 2
    BATTLE_SETUP = 3
    FORMATION = 4
    TEST_LAB = 5
    STRATEGY = 6
    RACE_SETUP = 7
    RESEARCH_TREE = 8
    GALAXY_TEST = 9
    KEYBINDINGS = 10

# PROJ-113: Colors (WHITE, BLACK, BLUE, RED, GREEN) and FONT_MAIN moved to game.ui.colors

# Feature Flags
# PROJ-121: Renamed from DEBUG_SCREENSHOTS - this is a feature toggle, not debug
ENABLE_SCREENSHOTS = True


# Layer Defaults - radius percentages for ship layer zones
class LayerDefaults:
    """Default radius percentages for ship layer zones (core, inner, outer)."""
    CORE_RADIUS_PCT = 0.2    # Core layer at 20% of ship radius
    INNER_RADIUS_PCT = 0.5   # Inner layer at 50% of ship radius
    OUTER_RADIUS_PCT = 0.8   # Outer layer at 80% of ship radius


# Combat Constants
class CombatConstants:
    """Constants for combat simulation."""
    DEFAULT_MAX_TARGETS = 1           # Default maximum targets for multi-target weapons
    DEFAULT_DAMAGE_THRESHOLD = 0.5    # Components fail at 50% HP by default
    # Note: FIGHTER_LAUNCH_SPEED is in BattleTuning (game/core/config.py)


# Simulation Constants
class SimulationConstants:
    """Constants for battle simulation timing and bounds."""
    # Timing
    TICKS_PER_SECOND = int(1.0 / PhysicsConfig.TICK_RATE)  # Derived from PhysicsConfig

    # Warp retreat charging
    WARP_CHARGE_TICKS = 500           # Ticks needed for warp retreat (5 seconds at 100 TPS)

    # Map bounds
    DEFAULT_MAP_EDGE_THRESHOLD = 500  # Units from edge to trigger edge escape
    DEFAULT_MAP_SIZE = 100000         # Default map dimension

    # Battle limits
    DEFAULT_MAX_TICKS = 100000        # Maximum ticks before battle timeout
    ABSOLUTE_MAX_TICKS = 1_000_000    # Hard ceiling to prevent infinite loops (safety net)

    # Projectile/Combat constants
    PROJECTILE_SPEED_SCALE = 100.0    # Divisor to convert projectile_speed stat to world units/tick
    SEEKER_MAX_RANGE_MULTIPLIER = 2.0  # Seekers can track targets up to 2x their theoretical range


# Resource Types
# PROJ-11: Moved from game.strategy.data.planet to eliminate simulation->strategy dependency
PLANET_RESOURCES = ["metals", "organics", "vapors", "radioactives", "exotics"]


class ResourceType:
    """Ship resource type constants for fuel, energy, and ammo."""
    FUEL = 'fuel'
    ENERGY = 'energy'
    AMMO = 'ammo'

    @classmethod
    def all(cls) -> list:
        """Return all resource types in display order."""
        return [cls.FUEL, cls.ENERGY, cls.AMMO]


# Layer Types - Ship layer zones for component placement and damage distribution
# PROJ-17: Moved from game/simulation/components/component_constants.py for proper layer architecture
class LayerType(Enum):
    """Ship layer zones for component placement and damage distribution."""
    HULL = 0    # Innermost Chassis Layer
    CORE = 1
    INNER = 2
    OUTER = 3
    ARMOR = 4


# Physics Constants
EARTH_MASS = 5.97e24  # Earth mass in kg — canonical value, import from here

