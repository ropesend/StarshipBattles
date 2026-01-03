from enum import Enum, auto

class AttackType(Enum):
    PROJECTILE = "projectile"
    MISSILE = "missile"
    BEAM = "beam"
    LAUNCH = "launch"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Screen Dimensions
WIDTH = 1920
HEIGHT = 1080

# Fonts
FONT_MAIN = "Arial"


# Directory Paths
import os
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.dirname(CORE_DIR)
ROOT_DIR = os.path.dirname(GAME_DIR)

ASSET_DIR = os.path.join(ROOT_DIR, "assets")
DATA_DIR = os.path.join(ROOT_DIR, "data")
SCREENSHOT_DIR = os.path.join(ROOT_DIR, "screenshots")

# Debug Flags
DEBUG_SCREENSHOTS = True

