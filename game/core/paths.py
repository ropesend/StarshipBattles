"""
Centralized path configuration for StarshipBattles.

Usage:
    from game.core.paths import Paths

    data_path = Paths.DATA_DIR
    components = Paths.COMPONENTS_FILE
    data_path = Paths.get_data_dir()  # Returns pathlib.Path

Exceptions:
    ResourceException: If project root cannot be found during module load
"""
import os
from pathlib import Path

from game.core.exceptions import ResourceException
from game.core.error_codes import ErrorCode


def _find_project_root() -> Path:
    """Find project root by looking for game/ and data/ directories.

    Raises:
        ResourceException: If project root cannot be found after searching
            up to 10 parent directories.
    """
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    raise ResourceException(
        "Could not find project root (looking for game/ and data/ directories)",
        code=ErrorCode.RESOURCE_NOT_FOUND.value,
        context={"start_path": str(Path(__file__).resolve().parent)}
    )


_PROJECT_ROOT: Path = _find_project_root()


class Paths:
    """Centralized path configuration."""

    # === Project Root ===
    ROOT_DIR: str = str(_PROJECT_ROOT)

    # === Core Directories ===
    GAME_DIR: str = os.path.join(ROOT_DIR, "game")
    CORE_DIR: str = os.path.join(GAME_DIR, "core")
    DATA_DIR: str = os.path.join(ROOT_DIR, "data")
    ASSET_DIR: str = os.path.join(ROOT_DIR, "assets")
    SHIPS_DIR: str = os.path.join(ROOT_DIR, "ships")

    # === Output Directory (user/runtime data) ===
    OUTPUT_DIR: str = os.path.join(ROOT_DIR, "output")
    SAVES_DIR: str = os.path.join(OUTPUT_DIR, "saves")
    RACES_DIR: str = os.path.join(OUTPUT_DIR, "races")
    SCREENSHOTS_DIR: str = os.path.join(OUTPUT_DIR, "screenshots")
    LOGS_DIR: str = os.path.join(OUTPUT_DIR, "logs")

    # === Data Subdirectories ===
    FORMATIONS_DIR: str = os.path.join(DATA_DIR, "formations")
    TECH_PRESETS_DIR: str = os.path.join(DATA_DIR, "tech_presets")

    # === Asset Subdirectories ===
    SHIP_THEMES_DIR: str = os.path.join(ASSET_DIR, "ShipThemes")
    PLANETS_V3_DIR: str = os.path.join(ASSET_DIR, "Images", "Stellar Objects", "Planets", "Planets_V3")

    # === Core Data Files ===
    COMPONENTS_FILE: str = os.path.join(DATA_DIR, "components.json")
    MODIFIERS_FILE: str = os.path.join(DATA_DIR, "modifiers.json")
    VEHICLE_CLASSES_FILE: str = os.path.join(DATA_DIR, "vehicleclasses.json")
    VEHICLE_LAYERS_FILE: str = os.path.join(DATA_DIR, "vehiclelayers.json")
    RESOURCES_FILE: str = os.path.join(DATA_DIR, "resources.json")

    # === Asset Files ===
    ASSET_MANIFEST_FILE: str = os.path.join(ASSET_DIR, "asset_manifest.json")
    PLANET_CLASSIFICATIONS_FILE: str = os.path.join(PLANETS_V3_DIR, "planet_classifications.json")

    # === Log Files ===
    BATTLE_LOG: str = os.path.join(LOGS_DIR, "battle.log")
    CRASH_LOG: str = os.path.join(LOGS_DIR, "crash_log.txt")
    PROFILING_HISTORY: str = os.path.join(LOGS_DIR, "profiling_history.json")

    # === Simulation Tests Output ===
    SIMULATION_TESTS_OUTPUT_DIR: str = os.path.join(ROOT_DIR, "simulation_tests", "output")

    # === pathlib.Path Accessors ===
    @classmethod
    def get_root(cls) -> Path:
        return _PROJECT_ROOT

    @classmethod
    def get_data_dir(cls) -> Path:
        return _PROJECT_ROOT / "data"

    @classmethod
    def get_assets_dir(cls) -> Path:
        return _PROJECT_ROOT / "assets"

    @classmethod
    def get_output_dir(cls) -> Path:
        return _PROJECT_ROOT / "output"

    @classmethod
    def get_saves_dir(cls) -> Path:
        return _PROJECT_ROOT / "output" / "saves"

    @classmethod
    def get_logs_dir(cls) -> Path:
        return _PROJECT_ROOT / "output" / "logs"

    @classmethod
    def get_planets_v3_dir(cls) -> Path:
        return _PROJECT_ROOT / "assets" / "Images" / "Stellar Objects" / "Planets" / "Planets_V3"


# Backward compatibility exports - Deprecated in favor of Paths class access
# New code should use: from game.core.paths import Paths; Paths.ROOT_DIR
# These module-level exports will be removed in a future version.
ROOT_DIR = Paths.ROOT_DIR
DATA_DIR = Paths.DATA_DIR
ASSET_DIR = Paths.ASSET_DIR
SHIPS_DIR = Paths.SHIPS_DIR
SCREENSHOT_DIR = Paths.SCREENSHOTS_DIR
COMPONENTS_FILE = Paths.COMPONENTS_FILE
MODIFIERS_FILE = Paths.MODIFIERS_FILE
VEHICLE_CLASSES_FILE = Paths.VEHICLE_CLASSES_FILE
