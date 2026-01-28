# Phase 4: Assets/UI

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-26 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate asset loading and UI files to use centralized paths

---

## Tasks

### Task 4.1: Migrate game/assets/asset_manager.py [Simple]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/unit/assets/ -v`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace `"assets/asset_manifest.json"` (line ~31) with `Paths.ASSET_MANIFEST_FILE`
- [ ] Verify asset manager loads manifest correctly

**Notes:**

### Task 4.2: Migrate game/ui/assets/ship_theme_manager.py [Medium]
**File:** `game/ui/assets/ship_theme_manager.py`
**Tests:** `pytest tests/unit/ui/ -v`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace `"assets/ShipThemes"` (line ~91) with `Paths.SHIP_THEMES_DIR`
- [ ] Check for any dirname chains (line ~302) and replace
- [ ] Verify ship themes load correctly in UI

**Notes:**

### Task 4.3: Migrate game/simulation/systems/tech_preset_loader.py [Medium]
**File:** `game/simulation/systems/tech_preset_loader.py`
**Tests:** `pytest tests/unit/simulation/ -v`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace the fragile relative path (line ~19):
  ```python
  # REMOVE: os.path.join("..", "..", "..", "data", "tech_presets")
  ```
- [ ] Replace with: `Paths.TECH_PRESETS_DIR`
- [ ] Verify tech presets load correctly

**Notes:**

### Task 4.4: Migrate game/ui/screens/setup_data_io.py [Medium]
**File:** `game/ui/screens/setup_data_io.py`
**Tests:** `pytest tests/unit/ui/ -v`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Remove dirname chain (line ~18, 4-level)
- [ ] Replace `os.path.join(base_path, "data", "formations")` with `Paths.FORMATIONS_DIR`
- [ ] Check for any other hardcoded paths in file
- [ ] Verify formations load correctly in game setup

**Notes:**

---

## Additional Files to Check (Lower Priority)
These files were identified but may be addressed opportunistically:

- [ ] `game/ui/screens/workshop_screen.py` - Multiple data paths
- [ ] `game/ui/screens/workshop_data_loader.py` - Default data directory
- [ ] `game/simulation/systems/persistence.py` - ships/ folder
- [ ] `game/core/screenshot_manager.py` - Screenshot directory
- [ ] `game/ui/screens/setup_screen.py` - battles directory
- [ ] `game/ui/screens/formation_editor.py` - formations directory

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No relative "../" path patterns in UI files: `grep -r '"\.\."' game/ui/ --include="*.py"`
- [ ] Asset manager loads successfully
- [ ] Ship themes display correctly
- [ ] Tech presets load in game
- [ ] Formations load in setup screen
- [ ] All existing tests pass: `pytest tests/ -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
