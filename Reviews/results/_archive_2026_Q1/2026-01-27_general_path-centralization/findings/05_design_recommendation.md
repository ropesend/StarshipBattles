# Finding: Design Recommendation - Centralized Path System

**Severity:** N/A (Recommendation)
**Category:** Architecture
**Agent:** Path Configuration Designer

## Recommendation Overview

Create a new `game/core/paths.py` module as the single source of truth for all file paths.

## Proposed Solution

### New File: game/core/paths.py

```python
"""
Centralized path configuration for StarshipBattles.

Usage:
    from game.core.paths import Paths

    data_path = Paths.DATA_DIR
    components = Paths.COMPONENTS_FILE
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

    # === Asset Subdirectories ===
    SHIP_THEMES_DIR: str = os.path.join(ASSET_DIR, "ShipThemes")

    # === Core Data Files ===
    COMPONENTS_FILE: str = os.path.join(DATA_DIR, "components.json")
    MODIFIERS_FILE: str = os.path.join(DATA_DIR, "modifiers.json")
    VEHICLE_CLASSES_FILE: str = os.path.join(DATA_DIR, "vehicleclasses.json")
    VEHICLE_LAYERS_FILE: str = os.path.join(DATA_DIR, "vehiclelayers.json")
    RESOURCES_FILE: str = os.path.join(DATA_DIR, "resources.json")

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


# Backward compatibility exports
ROOT_DIR = Paths.ROOT_DIR
DATA_DIR = Paths.DATA_DIR
ASSET_DIR = Paths.ASSET_DIR
SHIPS_DIR = Paths.SHIPS_DIR
SCREENSHOT_DIR = Paths.SCREENSHOTS_DIR
COMPONENTS_FILE = Paths.COMPONENTS_FILE
MODIFIERS_FILE = Paths.MODIFIERS_FILE
VEHICLE_CLASSES_FILE = Paths.VEHICLE_CLASSES_FILE
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Class-based (`Paths.X`) | Namespace organization, IDE autocomplete |
| String paths as default | Backward compatibility with existing `os.path` code |
| `pathlib` accessors | Modern code can use `Paths.get_data_dir()` |
| Marker-based root detection | Works from any working directory |
| Backward compatibility exports | Existing `from constants import ROOT_DIR` still works |

## Migration Strategy

1. Create `game/core/paths.py`
2. Update `game/core/constants.py` to import from `paths.py`
3. Update files in priority order (core → strategy → UI)
4. Update test fixtures to use `game.core.paths`

## Benefits

- **Single source of truth** - One file controls all paths
- **Easy relocation** - Change one constant to move a folder
- **Consistent resolution** - No more working directory dependencies
- **Backward compatible** - No breaking changes to existing code
