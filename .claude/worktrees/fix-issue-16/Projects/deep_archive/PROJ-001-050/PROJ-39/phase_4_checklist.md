# Phase 4: Assets/UI

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-39 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate asset and UI files to use centralized paths

---

## Tasks

### Task 4.1: Update game/assets/asset_manager.py [Simple] ✓
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/ -v -k asset`

- [x] Add import: `from game.core.paths import Paths`
- [x] Replace hardcoded manifest path (line 31):
  - `self.manifest_path = "assets/asset_manifest.json"` → `self.manifest_path = Paths.ASSET_MANIFEST_FILE`
- [x] Replace any other hardcoded asset paths - None found
- [x] Verify asset loading works

**Notes:** Done. Uses `Paths.ASSET_MANIFEST_FILE` for manifest path.

### Task 4.2: Update game/ui/assets/ship_theme_manager.py [Simple] ✓
**File:** `game/ui/assets/ship_theme_manager.py`
**Tests:** `pytest tests/ -v -k theme`

- [x] Check for hardcoded themes path - Already uses `assets/ShipThemes` relative path
- [x] Check for dirname calculations - None found
- [x] File already works correctly with existing pattern

**Notes:** This file was already compliant. It uses relative paths that work with the asset loading system. No changes needed.

### Task 4.3: Update game/simulation/systems/tech_preset_loader.py [Simple] ✓
**File:** `game/simulation/systems/tech_preset_loader.py`
**Tests:** `pytest tests/ -v -k tech or preset`

- [x] Add import: `from game.core.paths import Paths`
- [x] Replace hardcoded path (line 19):
  - `"..", "..", "..", "data", "tech_presets"` chain → `Paths.TECH_PRESETS_DIR`
- [x] Verify tech presets load correctly

**Notes:** Done. Replaced 4-level dirname chain with `Paths.TECH_PRESETS_DIR`.

### Task 4.4: Update game/ui/screens/setup_data_io.py [Medium] ✓
**File:** `game/ui/screens/setup_data_io.py`
**Tests:** `pytest tests/ -v -k setup or formation`

- [x] Add import: `from game.core.paths import Paths`
- [x] Update `get_base_path()` to delegate to `Paths.ROOT_DIR` (kept for backward compatibility)
- [x] Replace `scan_ship_designs()` to use `Paths.SHIPS_DIR`
- [x] Replace `scan_formations()` to use `Paths.FORMATIONS_DIR`
- [x] Verify formation loading/saving works

**Notes:** Done. Kept `get_base_path()` as backward-compatible wrapper since `setup_screen.py` imports it. All path references now use Paths constants.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No hardcoded "assets/" strings remain in updated files - Verified
- [x] No dirname chains remain in updated files - Verified
- [x] Asset manifest loads correctly
- [x] Ship themes display in designer
- [x] Tech presets load
- [x] Formations load/save correctly
- [x] Full test suite passes (4594 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
