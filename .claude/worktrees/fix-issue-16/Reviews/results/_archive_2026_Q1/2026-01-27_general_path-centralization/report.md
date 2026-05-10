# Path Centralization Review Report

**Date:** 2026-01-27
**Review Type:** General Code Review - Path Configuration
**Scope:** Entire codebase - file path references and I/O operations

---

## Executive Summary

The StarshipBattles codebase has **partial path centralization** in `game/core/constants.py` but **47+ files** contain hardcoded paths that bypass these constants. This creates maintenance burden when relocating folders and inconsistent path resolution patterns.

**Recommendation:** Create a dedicated `game/core/paths.py` module as the single source of truth for all file paths.

---

## Current State Analysis

### Existing Centralization (Partial)

**File:** [game/core/constants.py:39-53](../../game/core/constants.py#L39-L53)

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

**File:** [tests/fixtures/paths.py](../../tests/fixtures/paths.py)

Uses modern `pathlib` with marker-based root detection - this is the pattern to follow.

---

## Findings: Hardcoded Paths

### Critical (Core/Startup)

| File | Line | Hardcoded Path | Impact |
|------|------|----------------|--------|
| [game/app.py](../../game/app.py#L107) | 107-114 | `os.path.join(base_path, "data", ...)` | Entry point recalculates paths |
| [game/core/logger.py](../../game/core/logger.py#L36) | 36 | `'battle.log'` | Log file in working directory |
| [game/core/profiling.py](../../game/core/profiling.py#L109) | 109 | `'profiling_history.json'` | Profiling data location |

### High (Strategy Layer)

| File | Line | Hardcoded Path | Impact |
|------|------|----------------|--------|
| [game/strategy/systems/save_game_service.py](../../game/strategy/systems/save_game_service.py#L26) | 26 | `DEFAULT_SAVES_FOLDER = "saves"` | Save game location |
| [game/strategy/systems/race_library.py](../../game/strategy/systems/race_library.py#L55) | 55-59 | Complex `os.path.dirname()` chain | Races folder calculation |
| [game/strategy/systems/design_library.py](../../game/strategy/systems/design_library.py) | Multiple | Temp folder fallback | Design storage |

### Medium (Assets/UI)

| File | Line | Hardcoded Path | Impact |
|------|------|----------------|--------|
| [game/assets/asset_manager.py](../../game/assets/asset_manager.py#L31) | 31 | `"assets/asset_manifest.json"` | Asset discovery |
| [game/ui/assets/ship_theme_manager.py](../../game/ui/assets/ship_theme_manager.py#L91) | 91 | `"assets/ShipThemes"` | Ship themes location |
| [game/simulation/systems/tech_preset_loader.py](../../game/simulation/systems/tech_preset_loader.py#L19) | 19 | `"..", "..", "..", "data", "tech_presets"` | Tech presets |
| [game/ui/screens/setup_data_io.py](../../game/ui/screens/setup_data_io.py#L51) | 51 | `data/formations` | Formation definitions |
| [game/simulation/entities/ship_loader.py](../../game/simulation/entities/ship_loader.py#L23) | 23 | `data/vehicleclasses.json` | Vehicle class data |

### Lower (Various)

| File | Hardcoded Path |
|------|----------------|
| [game/ui/screens/workshop_screen.py](../../game/ui/screens/workshop_screen.py) | Multiple data paths |
| [game/ui/screens/workshop_data_loader.py](../../game/ui/screens/workshop_data_loader.py) | Default data directory |
| [game/simulation/systems/persistence.py](../../game/simulation/systems/persistence.py#L21) | `ships/` folder |
| [game/core/screenshot_manager.py](../../game/core/screenshot_manager.py#L60) | Screenshot directory |

---

## Path Categories Identified

| Category | Paths | Current Source |
|----------|-------|----------------|
| **Root** | `ROOT_DIR`, `GAME_DIR`, `CORE_DIR` | `constants.py` |
| **Core Data** | `DATA_DIR`, `COMPONENTS_FILE`, `MODIFIERS_FILE`, `VEHICLE_CLASSES_FILE`, `VEHICLE_LAYERS_FILE`, `RESOURCES_FILE` | Mixed |
| **Assets** | `ASSET_DIR`, `ASSET_MANIFEST_FILE`, `SHIP_THEMES_DIR` | Mixed |
| **User Data** | `SHIPS_DIR`, `SAVES_DIR`, `RACES_DIR`, `SCREENSHOTS_DIR` | Mixed |
| **Config** | `FORMATIONS_DIR`, `TECH_PRESETS_DIR`, `COMBAT_STRATEGIES_FILE` | Hardcoded |
| **Logs** | `BATTLE_LOG`, `CRASH_LOG`, `PROFILING_HISTORY` | Hardcoded |

---

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

    # === Asset Subdirectories ===
    SHIP_THEMES_DIR: str = os.path.join(ASSET_DIR, "ShipThemes")

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


# Backward compatibility exports
ROOT_DIR = Paths.ROOT_DIR
DATA_DIR = Paths.DATA_DIR
ASSET_DIR = Paths.ASSET_DIR
# ... etc
```

---

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

### Before/After: game/core/logger.py

**Before:**
```python
fh = logging.FileHandler('battle.log', mode='w')
```

**After:**
```python
from game.core.paths import Paths

fh = logging.FileHandler(Paths.BATTLE_LOG, mode='w')
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

---

## Implementation Priority

### Phase 1: Infrastructure
1. Create `game/core/paths.py`
2. Update `game/core/constants.py` to import from `paths.py`

### Phase 2: Core Files
3. `game/app.py` - Entry point
4. `game/core/logger.py` - Battle log
5. `game/core/profiling.py` - Profiling history
6. `game/simulation/entities/ship_loader.py` - Vehicle data

### Phase 3: Strategy Layer
7. `game/strategy/systems/save_game_service.py` - Saves folder
8. `game/strategy/systems/race_library.py` - Races folder
9. `game/strategy/systems/design_library.py` - Design storage

### Phase 4: Assets/UI
10. `game/assets/asset_manager.py` - Asset manifest
11. `game/ui/assets/ship_theme_manager.py` - Ship themes
12. `game/simulation/systems/tech_preset_loader.py` - Tech presets
13. `game/ui/screens/setup_data_io.py` - Formations

### Phase 5: Test Integration
14. Update `tests/fixtures/paths.py` to delegate to `game.core.paths`

---

## Verification Checklist

- [ ] All existing tests pass (`pytest tests/ -v`)
- [ ] Simulation tests pass (`pytest simulation_tests/ -v`)
- [ ] Game launches and loads data correctly
- [ ] Save/load game works
- [ ] Ship designer loads assets
- [ ] Folder relocation test: rename folder, update `paths.py`, verify game works

---

## Benefits

1. **Single source of truth** - All paths defined in one file
2. **Easy relocation** - Change one constant, all code updates
3. **Consistent resolution** - No more `os.getcwd()` vs `__file__` inconsistencies
4. **Backward compatible** - Existing imports from `constants.py` still work
5. **Modern support** - `pathlib.Path` accessors for new code
6. **Deployment flexibility** - Optional environment variable overrides
