# Finding: Hardcoded Paths in Assets/UI Layer

**Severity:** Major
**Category:** Architecture
**Agent:** File I/O Operations Mapper

## Description
Asset and UI files use hardcoded relative paths for asset manifest, ship themes, and data files.

## Locations

### game/assets/asset_manager.py (Line 31)
```python
self.manifest_path = "assets/asset_manifest.json"
```
**Issue:** Relative path, not using `ASSET_DIR` from constants.

### game/ui/assets/ship_theme_manager.py (Line 91)
```python
themes_folder = "assets/ShipThemes"
```
**Issue:** Hardcoded relative path for ship themes.

### game/simulation/systems/tech_preset_loader.py (Line 19)
```python
TECH_PRESETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "tech_presets")
```
**Issue:** Complex relative path from file location.

### game/ui/screens/setup_data_io.py (Line 51)
```python
formations_dir = os.path.join("data", "formations")
```
**Issue:** Relative path assumes working directory.

### game/ui/screens/workshop_data_loader.py
```python
default_data_dir = os.path.join(os.getcwd(), "data")
```
**Issue:** Uses `os.getcwd()` which is unreliable.

## Impact
- Asset manifest location not configurable
- Ship themes folder cannot be relocated
- Tech presets use fragile relative paths
- Workshop depends on current working directory

## Recommendation
```python
from game.core.paths import Paths

self.manifest_path = Paths.ASSET_MANIFEST_FILE
themes_folder = Paths.SHIP_THEMES_DIR
TECH_PRESETS_DIR = Paths.TECH_PRESETS_DIR
formations_dir = Paths.FORMATIONS_DIR
```

## Files Affected
- `game/assets/asset_manager.py`
- `game/ui/assets/ship_theme_manager.py`
- `game/simulation/systems/tech_preset_loader.py`
- `game/ui/screens/setup_data_io.py`
- `game/ui/screens/workshop_data_loader.py`
- `game/ui/screens/workshop_screen.py`
