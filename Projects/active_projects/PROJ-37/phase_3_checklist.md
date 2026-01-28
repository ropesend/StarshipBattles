# Phase 3: Extend RaceAssetLoader

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-37 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add empire-specific asset loading methods to RaceAssetLoader

---

## Tasks

### Task 3.1: Add load_empire_race_assets method [Medium]
**File:** `game/ui/screens/race_asset_loader.py`
**Tests:** `pytest tests/unit/ui/test_race_asset_loader.py -v`

Add method to load race flags (rectangle, shield) for empire display.

- [x] Open `game/ui/screens/race_asset_loader.py`
- [x] Add import at top if needed: `from typing import Dict, Optional`
- [x] Add new method after existing methods
- [x] Verify method works: 6 tests passing
- [x] Run existing tests to check for regressions: `pytest tests/unit/ui/test_race_asset_loader.py -v`

**Notes:** Reuses existing `load_flag_full()` which already has resolution hierarchy logic. Implemented per spec with empty dict fallback for missing flag_id.

---

### Task 3.2: Add load_empire_theme_assets method [Medium]
**File:** `game/ui/screens/race_asset_loader.py`
**Tests:** `pytest tests/unit/ui/test_race_asset_loader.py -v`

Add method to load theme assets (colony flag, fleet icon) for empire display.

- [x] Add import at top: `from game.assets.asset_manager import get_asset_manager`
- [x] Add new method (implemented per spec)
- [x] Add `log_warning` import if needed: Already present from existing imports
- [x] Run existing tests: `pytest tests/unit/ui/test_race_asset_loader.py -v` (6 tests passing)

**Notes:** Uses AssetManager.load_external_image for caching benefits. Returns empty dict for missing theme dirs.

---

### Task 3.3: Add load_all_empire_assets method [Simple]
**File:** `game/ui/screens/race_asset_loader.py`
**Tests:** `pytest tests/unit/ui/test_race_asset_loader.py -v`

Add combined method that loads all empire assets with proper precedence.

- [x] Add new method (implemented per spec)
- [x] Run all tests: `pytest tests/unit/ui/test_race_asset_loader.py -v` (29 tests passing)

**Notes:** Order matters - race assets loaded second to overwrite theme's 'colony' key. Handles empire objects missing flag_id/theme_id attributes gracefully.

---

### Task 3.4: Add unit tests for new methods [Medium]
**File:** `tests/unit/ui/test_race_asset_loader.py`
**Tests:** `pytest tests/unit/ui/test_race_asset_loader.py -v`

Add tests for the new empire asset loading methods.

- [x] Open `tests/unit/ui/test_race_asset_loader.py`
- [x] Add new test class `TestEmpireAssetLoading` with 17 tests:
  - 6 tests for load_empire_race_assets (returns dict, empty/None flag_id, colony key, fleet_flag key, partial shapes)
  - 6 tests for load_empire_theme_assets (returns dict, empty theme_id/asset_base, nonexistent dir, loads colony, loads fleet)
  - 5 tests for load_all_empire_assets (returns dict, race precedence, theme fallback, missing attributes, fleet_flag inclusion)
- [x] Run new tests: `pytest tests/unit/ui/test_race_asset_loader.py -v` (29 total tests passing)

**Notes:** Tests written FIRST following Strict TDD - all 17 new tests failed before implementation, all pass after.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `game/ui/screens/race_asset_loader.py` has 3 new methods:
  - `load_empire_race_assets()`
  - `load_empire_theme_assets()`
  - `load_all_empire_assets()`
- [x] Run `pytest tests/unit/ui/test_race_asset_loader.py -v` - all 29 pass
- [x] Run `pytest tests/ --testmon` - 33 affected tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
