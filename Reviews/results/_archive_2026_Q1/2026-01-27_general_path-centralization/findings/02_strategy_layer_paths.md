# Finding: Hardcoded Paths in Strategy Layer

**Severity:** Major
**Category:** Architecture
**Agent:** File I/O Operations Mapper

## Description
Strategy layer files use hardcoded relative paths for saves, races, and designs that aren't controlled by central configuration.

## Locations

### game/strategy/systems/save_game_service.py (Line 26)
```python
DEFAULT_SAVES_FOLDER = "saves"
```
**Issue:** Relative path assumes working directory is project root. Not configurable.

### game/strategy/systems/race_library.py (Lines 55-59)
```python
if races_folder is None:
    # Default to races/ in project root
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    self.races_folder = os.path.join(base_path, "races")
```
**Issue:** Complex 4-level dirname calculation repeated from core files.

### game/strategy/systems/design_library.py
```python
# Falls back to temp directory when no savegame
tempfile.gettempdir() + "/starship_battles_temp_designs/empire_{ID}/"
```
**Issue:** Temp folder location not configurable, uses forward slashes on Windows.

### game/strategy/quickstart_builder.py
**Issue:** Similar path calculations for race loading.

## Impact
- Cannot relocate saves folder without code changes
- Races folder requires complex path calculation
- Design temp folder hardcoded to system temp

## Recommendation
```python
from game.core.paths import Paths

DEFAULT_SAVES_FOLDER = Paths.SAVES_DIR
self.races_folder = Paths.RACES_DIR
```

## Files Affected
- `game/strategy/systems/save_game_service.py`
- `game/strategy/systems/race_library.py`
- `game/strategy/systems/design_library.py`
- `game/strategy/quickstart_builder.py`
