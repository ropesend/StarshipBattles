# PROJ-26 Design: Path Centralization

## Source Review Summary

**Review:** [2026-01-27_general_path-centralization](../../../Reviews/results/2026-01-27_general_path-centralization/report.md)

The codebase has partial path centralization in `game/core/constants.py` but **47+ files** contain hardcoded paths that bypass these constants.

## Current State

### Existing Centralization (Partial)
**File:** `game/core/constants.py` (lines 39-53)

```python
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DIR = os.path.dirname(CORE_DIR)
ROOT_DIR = os.path.dirname(GAME_DIR)

ASSET_DIR = os.path.join(ROOT_DIR, "assets")
DATA_DIR = os.path.join(ROOT_DIR, "data")
SHIPS_DIR = os.path.join(ROOT_DIR, "ships")
SCREENSHOT_DIR = os.path.join(ROOT_DIR, "screenshots")

COMPONENTS_FILE = os.path.join(DATA_DIR, "components.json")
MODIFIERS_FILE = os.path.join(DATA_DIR, "modifiers.json")
VEHICLE_CLASSES_FILE = os.path.join(DATA_DIR, "vehicleclasses.json")
```

### Good Pattern (Tests)
**File:** `tests/fixtures/paths.py`

Uses modern `pathlib` with marker-based root detection - this is the pattern to follow.

## Proposed Solution

### Create `game/core/paths.py`

```python
"""
Centralized path configuration for StarshipBattles.

Usage:
    from game.core.paths import Paths

    # Access directories
    data_path = Paths.DATA_DIR

    # Access specific files
    components = Paths.COMPONENTS_FILE

    # Get Path objects for modern code
    data_path = Paths.get_data_dir()  # Returns pathlib.Path
"""
import os
from pathlib import Path


def _find_project_root() -> Path:
    """Find project root by looking for game/ and data/ directories."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    raise RuntimeError("Could not find project root.")


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

    # === User/Runtime Directories ===
    SAVES_DIR: str = os.path.join(ROOT_DIR, "saves")
    RACES_DIR: str = os.path.join(ROOT_DIR, "races")
    SCREENSHOTS_DIR: str = os.path.join(ROOT_DIR, "screenshots")

    # === Data Subdirectories ===
    FORMATIONS_DIR: str = os.path.join(DATA_DIR, "formations")
    TECH_PRESETS_DIR: str = os.path.join(DATA_DIR, "tech_presets")
    BATTLES_DIR: str = os.path.join(DATA_DIR, "battles")

    # === Asset Subdirectories ===
    SHIP_THEMES_DIR: str = os.path.join(ASSET_DIR, "ShipThemes")
    IMAGES_DIR: str = os.path.join(ASSET_DIR, "Images")
    COMPONENTS_IMAGES_DIR: str = os.path.join(IMAGES_DIR, "Components")

    # === Core Data Files ===
    COMPONENTS_FILE: str = os.path.join(DATA_DIR, "components.json")
    MODIFIERS_FILE: str = os.path.join(DATA_DIR, "modifiers.json")
    VEHICLE_CLASSES_FILE: str = os.path.join(DATA_DIR, "vehicleclasses.json")
    VEHICLE_LAYERS_FILE: str = os.path.join(DATA_DIR, "vehiclelayers.json")
    RESOURCES_FILE: str = os.path.join(DATA_DIR, "resources.json")
    COMBAT_STRATEGIES_FILE: str = os.path.join(DATA_DIR, "combat_strategies.json")

    # === Asset Files ===
    ASSET_MANIFEST_FILE: str = os.path.join(ASSET_DIR, "asset_manifest.json")

    # === Log Files ===
    BATTLE_LOG: str = os.path.join(ROOT_DIR, "battle.log")
    CRASH_LOG: str = os.path.join(ROOT_DIR, "crash_log.txt")
    PROFILING_HISTORY: str = os.path.join(ROOT_DIR, "profiling_history.json")

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
    def get_saves_dir(cls) -> Path:
        return _PROJECT_ROOT / "saves"

    @classmethod
    def get_ships_dir(cls) -> Path:
        return _PROJECT_ROOT / "ships"


# Backward compatibility exports
ROOT_DIR = Paths.ROOT_DIR
GAME_DIR = Paths.GAME_DIR
CORE_DIR = Paths.CORE_DIR
DATA_DIR = Paths.DATA_DIR
ASSET_DIR = Paths.ASSET_DIR
SHIPS_DIR = Paths.SHIPS_DIR
SCREENSHOT_DIR = Paths.SCREENSHOTS_DIR
COMPONENTS_FILE = Paths.COMPONENTS_FILE
MODIFIERS_FILE = Paths.MODIFIERS_FILE
VEHICLE_CLASSES_FILE = Paths.VEHICLE_CLASSES_FILE
```

## Migration Examples

### Before/After: game/app.py

**Before:**
```python
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_components(os.path.join(base_path, "data", "components.json"))
load_modifiers(os.path.join(base_path, "data", "modifiers.json"))
```

**After:**
```python
from game.core.paths import Paths

load_components(Paths.COMPONENTS_FILE)
load_modifiers(Paths.MODIFIERS_FILE)
```

### Before/After: game/strategy/systems/save_game_service.py

**Before:**
```python
DEFAULT_SAVES_FOLDER = "saves"
# ...
saves_path = os.path.join(os.getcwd(), DEFAULT_SAVES_FOLDER)
```

**After:**
```python
from game.core.paths import Paths

saves_path = Paths.SAVES_DIR
```

### Before/After: game/strategy/systems/race_library.py

**Before:**
```python
base_path = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
self.races_folder = os.path.join(base_path, "races")
```

**After:**
```python
from game.core.paths import Paths

self.races_folder = Paths.RACES_DIR
```

## Path Categories

| Category | Paths | Notes |
|----------|-------|-------|
| **Root** | ROOT_DIR, GAME_DIR, CORE_DIR | Base directories |
| **Core Data** | DATA_DIR, COMPONENTS_FILE, MODIFIERS_FILE, VEHICLE_CLASSES_FILE | Game data |
| **Assets** | ASSET_DIR, ASSET_MANIFEST_FILE, SHIP_THEMES_DIR | Visual assets |
| **User Data** | SHIPS_DIR, SAVES_DIR, RACES_DIR, SCREENSHOTS_DIR | Player content |
| **Config** | FORMATIONS_DIR, TECH_PRESETS_DIR, BATTLES_DIR | Configuration data |
| **Logs** | BATTLE_LOG, CRASH_LOG, PROFILING_HISTORY | Runtime logs |

## Benefits

1. **Single source of truth** - All paths defined in one file
2. **Easy relocation** - Change one constant, all code updates
3. **Consistent resolution** - No more `os.getcwd()` vs `__file__` inconsistencies
4. **Backward compatible** - Existing imports from `constants.py` still work
5. **Modern support** - `pathlib.Path` accessors for new code
6. **Deployment flexibility** - Optional environment variable overrides possible
