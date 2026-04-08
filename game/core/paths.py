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

    # === Output Directory (user/runtime data) ===
    OUTPUT_DIR: str = os.path.join(ROOT_DIR, "output")
    SAVES_DIR: str = os.path.join(OUTPUT_DIR, "saves")
    SHIPS_DIR: str = os.path.join(OUTPUT_DIR, "ships")
    RACES_DIR: str = os.path.join(OUTPUT_DIR, "races")
    SCREENSHOTS_DIR: str = os.path.join(OUTPUT_DIR, "screenshots")
    LOGS_DIR: str = os.path.join(OUTPUT_DIR, "logs")
    SETTINGS_DIR: str = os.path.join(OUTPUT_DIR, "settings")

    # === Data Subdirectories ===
    FORMATIONS_DIR: str = os.path.join(DATA_DIR, "formations")
    BATTLES_DIR: str = os.path.join(DATA_DIR, "battles")
    TECH_PRESETS_DIR: str = os.path.join(DATA_DIR, "tech_presets")

    # === Asset Subdirectories ===
    SHIP_THEMES_DIR: str = os.path.join(ASSET_DIR, "ShipThemes")
    COMPONENTS_IMAGES_DIR: str = os.path.join(ASSET_DIR, "Images", "Components")
    RESOURCE_PORTRAITS_DIR: str = os.path.join(ASSET_DIR, "Images", "Resource Portraits")
    PLANETS_V3_DIR: str = os.path.join(ASSET_DIR, "Images", "Stellar Objects", "Planets", "Planets_V3")

    # Resolution subdirectories within Planets_V3/ (PROJ-54 Phase 7)
    PLANETS_V3_2048_DIR: str = os.path.join(PLANETS_V3_DIR, "Planets_V3_2048")
    PLANETS_V3_1024_DIR: str = os.path.join(PLANETS_V3_DIR, "Planets_V3_1024")
    PLANETS_V3_512_DIR: str = os.path.join(PLANETS_V3_DIR, "Planets_V3_512")
    PLANETS_V3_256_DIR: str = os.path.join(PLANETS_V3_DIR, "Planets_V3_256")
    PLANETS_V3_128_DIR: str = os.path.join(PLANETS_V3_DIR, "Planets_V3_128")

    # Star subdirectories (PROJ-XX Star Expansion)
    STARS_DIR: str = os.path.join(ASSET_DIR, "Images", "Stellar Objects", "Stars")
    STARS_1024_DIR: str = os.path.join(STARS_DIR, "Stars_1024")
    STARS_512_DIR: str = os.path.join(STARS_DIR, "Stars_512")
    STARS_256_DIR: str = os.path.join(STARS_DIR, "Stars_256")
    STARS_128_DIR: str = os.path.join(STARS_DIR, "Stars_128")

    # Stellar Objects subdirectories
    SPHERE_WORLD_DIR: str = os.path.join(ASSET_DIR, "Images", "Stellar Objects", "Sphere world")

    # === Core Data Files ===
    COMPONENTS_FILE: str = os.path.join(DATA_DIR, "components.json")
    MODIFIERS_FILE: str = os.path.join(DATA_DIR, "modifiers.json")
    VEHICLE_CLASSES_FILE: str = os.path.join(DATA_DIR, "vehicleclasses.json")
    VEHICLE_LAYERS_FILE: str = os.path.join(DATA_DIR, "vehiclelayers.json")
    RESOURCES_FILE: str = os.path.join(DATA_DIR, "resources.json")
    PRODUCTION_RATES_FILE: str = os.path.join(DATA_DIR, "production_rates.json")
    SYSTEM_BLUEPRINTS_FILE: str = os.path.join(DATA_DIR, "system_blueprints.json")
    ASTROPHYSICS_FILE: str = os.path.join(DATA_DIR, "astrophysics.json")
    GALAXY_LAYOUTS_FILE: str = os.path.join(DATA_DIR, "galaxy_layouts.json")
    STAR_SYSTEM_NAMES_FILE: str = os.path.join(DATA_DIR, "StarSystemNames.YAML")
    STORMS_FILE: str = os.path.join(DATA_DIR, "storms.json")
    STATS_LAYOUT_FILE: str = os.path.join(DATA_DIR, "stats_layout.json")
    HOMEWORLD_PRESETS_FILE: str = os.path.join(GAME_DIR, "data", "homeworld_presets.json")
    RACE_NAMES_FILE: str = os.path.join(GAME_DIR, "data", "race_names.json")

    # === Settings Files ===
    DEFAULT_KEYBINDINGS_FILE: str = os.path.join(DATA_DIR, "default_keybindings.json")
    USER_KEYBINDINGS_FILE: str = os.path.join(SETTINGS_DIR, "keybindings.json")

    # === Asset Files ===
    ASSET_MANIFEST_FILE: str = os.path.join(ASSET_DIR, "asset_manifest.json")
    DEFAULT_SHIP_PORTRAIT: str = os.path.join(ASSET_DIR, "Images", "Default_Ship_Portrait.png")
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
    def get_ships_dir(cls) -> Path:
        return _PROJECT_ROOT / "output" / "ships"

    @classmethod
    def get_saves_dir(cls) -> Path:
        return _PROJECT_ROOT / "output" / "saves"

    @classmethod
    def get_logs_dir(cls) -> Path:
        return _PROJECT_ROOT / "output" / "logs"

    @classmethod
    def get_planets_v3_dir(cls) -> Path:
        return _PROJECT_ROOT / "assets" / "Images" / "Stellar Objects" / "Planets" / "Planets_V3"

    @classmethod
    def get_stars_dir(cls) -> Path:
        return _PROJECT_ROOT / "assets" / "Images" / "Stellar Objects" / "Stars"

