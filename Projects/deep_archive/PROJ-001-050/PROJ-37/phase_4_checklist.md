# Phase 4: Refactor strategy_scene.py

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-37 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (pending manual verification)
**Objective:** Replace hardcoded asset loading with RaceAssetLoader calls and manifest-based color lookup

---

## Tasks

### Task 4.1: Refactor _load_assets method [Medium]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/repro_issues/test_bug_13_colony_flags.py -v`

Replace the 55+ lines of hardcoded path logic with delegated loader calls.

- [x] Open `game/ui/screens/strategy_scene.py`
- [x] Add import near top (line 32):
  ```python
  from game.ui.screens.race_asset_loader import RaceAssetLoader
  ```
- [x] In `__init__` method, after `self.empire_assets = {}` (line 85):
  ```python
  self._race_loader = RaceAssetLoader()
  ```
- [x] In `_load_assets()` method, replace 55+ lines with:
  ```python
  for emp in self.empires:
      self.empire_assets[emp.id] = self._race_loader.load_all_empire_assets(
          emp,
          asset_base
      )
  ```
- [x] Keep the lines BEFORE the loop intact:
  - `am = get_asset_manager()`
  - `am.load_manifest()`
  - `asset_base = GameConfig().asset_base_path`
- [x] Run BUG-13 regression test: `pytest tests/repro_issues/test_bug_13_colony_flags.py -v` - 6 tests pass

**Notes:** Reduced _load_assets from ~55 lines to ~15 lines. Preserves empire_assets structure for renderer.

---

### Task 4.2: Refactor _get_object_asset star color logic [Medium]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/unit/ui/test_star_color_mapping.py -v`

Replace the 12 lines of magic number color logic with manifest lookup.

- [x] Locate `_get_object_asset()` method (line 468)
- [x] Replace 11 lines of hardcoded threshold logic with:
  ```python
  if is_star(obj):
      asset_key = am.get_star_color_key(obj.color)
      return am.get_image('stars', asset_key)
  ```
- [x] Update tests to mock `get_star_color_key` method
- [x] Run star color tests: `pytest tests/unit/ui/test_star_color_mapping.py -v` - 15 tests pass

**Notes:** Reduced 11 lines to 3 lines. Eliminated magic numbers (100, 150, 200).

---

### Task 4.3: Update imports and cleanup [Simple]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/strategy/test_strategy_scene.py -v`

Clean up any unused imports and verify the refactored code.

- [x] Check if `ASSET_DIR` import is still needed - NO, removed (was local import in removed code)
- [x] Check if `os` import is still needed - NO, removed (no longer used)
- [x] Verify all imports are still required (no unused imports)
- [x] Remove any dead code or comments from the refactoring
- [x] Run full test suite: `pytest tests/` - 4998 tests pass

**Notes:** Removed `import os` from top of file. ASSET_DIR was a local import that was removed with the old code. Also updated test files to work with new implementation.

---

### Task 4.4: Manual verification [Simple]
**Tests:** Manual testing in-game

Verify the refactored code works correctly in the actual game.

- [ ] Start the game
- [ ] Create a new game with 4 empires using different races/themes
- [ ] Verify colony flags appear on owned planets
- [ ] Verify fleet icons appear correctly
- [ ] Verify stars render with correct colors (look for red, blue, yellow, white, orange stars)
- [ ] Save and reload the game - verify assets persist correctly
- [ ] Load an older save file (if available) - verify backward compatibility

**Notes:** Manual verification to be done by user

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (except manual verification - requires user)
- [x] `strategy_scene._load_assets()` uses RaceAssetLoader (not hardcoded paths)
- [x] `strategy_scene._get_object_asset()` uses AssetManager.get_star_color_key()
- [x] Run `pytest tests/repro_issues/test_bug_13_colony_flags.py -v` - all 6 pass
- [x] Run `pytest tests/` - full suite passes (4998 tests)
- [ ] Manual verification complete - game works correctly (requires user)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
