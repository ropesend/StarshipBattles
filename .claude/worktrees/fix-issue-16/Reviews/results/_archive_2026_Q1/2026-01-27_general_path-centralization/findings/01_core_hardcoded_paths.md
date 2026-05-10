# Finding: Hardcoded Paths in Core Files

**Severity:** Major
**Category:** Architecture
**Agent:** File I/O Operations Mapper

## Description
Core startup files calculate paths independently instead of using the existing constants in `game/core/constants.py`.

## Locations

### game/app.py (Lines 107-114)
```python
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_components(os.path.join(base_path, "data", "components.json"))
load_modifiers(os.path.join(base_path, "data", "modifiers.json"))
load_resources(os.path.join(base_path, "data", "resources.json"))
```
**Issue:** Recalculates `base_path` instead of using `ROOT_DIR` from constants.

### game/simulation/entities/ship_loader.py (Line 23)
```python
def load_vehicle_classes(base_path: str = None):
    if base_path is None:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))))
    data_path = os.path.join(base_path, "data", "vehicleclasses.json")
```
**Issue:** Complex 4-level dirname calculation for project root.

### game/simulation/components/component.py
```python
base_path = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
```
**Issue:** Same 4-level calculation pattern repeated.

## Impact
- Duplicated path calculation logic across 6+ files
- Inconsistent behavior if working directory changes
- Harder to relocate data folder

## Recommendation
Import from centralized `Paths` class:
```python
from game.core.paths import Paths
load_components(Paths.COMPONENTS_FILE)
```

## Files Affected
- `game/app.py`
- `game/simulation/entities/ship_loader.py`
- `game/simulation/components/component.py`
- `game/core/resources.py`
