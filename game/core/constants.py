from enum import Enum, auto

__all__ = [
    'AttackType',
    'GameState',
    'LayerType',
    'LayerDefaults',
    'CombatConstants',
    'SimulationConstants',
    'PLANET_RESOURCES',
    # Colors
    'WHITE', 'BLACK', 'BLUE', 'RED', 'GREEN',
    # Font
    'FONT_MAIN',
    # Debug flags
    'DEBUG_SCREENSHOTS',
]


class AttackType(Enum):
    PROJECTILE = "projectile"
    MISSILE = "missile"
    BEAM = "beam"
    LAUNCH = "launch"

from enum import IntEnum
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

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Fonts
FONT_MAIN = "Arial"


# Debug Flags
DEBUG_SCREENSHOTS = True


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
    # Note: FIGHTER_LAUNCH_SPEED is in BattleConfig (game/core/config.py)


# Simulation Constants
class SimulationConstants:
    """Constants for battle simulation timing and bounds."""
    # Timing
    TICKS_PER_SECOND = 100            # Simulation tick rate

    # Warp retreat charging
    WARP_CHARGE_TICKS = 500           # Ticks needed for warp retreat (5 seconds at 100 TPS)

    # Map bounds
    DEFAULT_MAP_EDGE_THRESHOLD = 500  # Units from edge to trigger edge escape
    DEFAULT_MAP_SIZE = 100000         # Default map dimension

    # Battle limits
    DEFAULT_MAX_TICKS = 100000        # Maximum ticks before battle timeout
    ABSOLUTE_MAX_TICKS = 1_000_000    # Hard ceiling to prevent infinite loops (safety net)


# Resource Types
# PROJ-11: Moved from game.strategy.data.planet to eliminate simulation->strategy dependency
PLANET_RESOURCES = ["Metals", "Organics", "Vapors", "Radioactives", "Exotics"]


# Layer Types - Ship layer zones for component placement and damage distribution
# PROJ-17: Moved from game/simulation/components/component_constants.py for proper layer architecture
class LayerType(Enum):
    """Ship layer zones for component placement and damage distribution."""
    HULL = 0    # Innermost Chassis Layer
    CORE = 1
    INNER = 2
    OUTER = 3
    ARMOR = 4

    @staticmethod
    def from_string(s):
        return getattr(LayerType, s.upper())

