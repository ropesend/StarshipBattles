from enum import Enum, auto

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

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Screen Dimensions
# NOTE: These are re-exported from DisplayConfig for backward compatibility.
# New code should use DisplayConfig.DEFAULT_WIDTH/DEFAULT_HEIGHT directly.
from game.core.config import DisplayConfig
WIDTH = DisplayConfig.DEFAULT_WIDTH
HEIGHT = DisplayConfig.DEFAULT_HEIGHT

# Fonts
FONT_MAIN = "Arial"


# Directory Paths
import os
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.dirname(CORE_DIR)
ROOT_DIR = os.path.dirname(GAME_DIR)

ASSET_DIR = os.path.join(ROOT_DIR, "assets")
DATA_DIR = os.path.join(ROOT_DIR, "data")
SHIPS_DIR = os.path.join(ROOT_DIR, "ships")
SCREENSHOT_DIR = os.path.join(ROOT_DIR, "screenshots")

# Standard data file paths
COMPONENTS_FILE = os.path.join(DATA_DIR, "components.json")
MODIFIERS_FILE = os.path.join(DATA_DIR, "modifiers.json")
VEHICLE_CLASSES_FILE = os.path.join(DATA_DIR, "vehicleclasses.json")

# Debug Flags
DEBUG_SCREENSHOTS = True

