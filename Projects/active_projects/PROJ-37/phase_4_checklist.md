# Phase 4: Refactor strategy_scene.py

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-37 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace hardcoded asset loading with RaceAssetLoader calls and manifest-based color lookup

---

## Tasks

### Task 4.1: Refactor _load_assets method [Medium]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/repro_issues/test_bug_13_colony_flags.py -v`

Replace the 55+ lines of hardcoded path logic with delegated loader calls.

- [ ] Open `game/ui/screens/strategy_scene.py`
- [ ] Add import near top (around line 20):
  ```python
  from game.ui.screens.race_asset_loader import RaceAssetLoader
  ```
- [ ] In `__init__` method, after `self.empire_assets = {}` (around line 80):
  ```python
  self._race_loader = RaceAssetLoader()
  ```
- [ ] In `_load_assets()` method (lines 435-491), replace the empire loop body:

  **BEFORE (lines 452-490):**
  ```python
  for emp in self.empires:
      self.empire_assets[emp.id] = {}

      # ... 35+ lines of hardcoded path logic ...
  ```

  **AFTER:**
  ```python
  for emp in self.empires:
      self.empire_assets[emp.id] = self._race_loader.load_all_empire_assets(
          emp,
          asset_base
      )
  ```
- [ ] Keep the lines BEFORE the loop intact (lines 437-450):
  - `am = get_asset_manager()`
  - `am.load_manifest()`
  - `asset_base = GameConfig().asset_base_path`
- [ ] Run BUG-13 regression test: `pytest tests/repro_issues/test_bug_13_colony_flags.py -v`
- [ ] Verify all 5 tests pass

**Notes:** This is the core refactoring - preserves empire_assets structure for renderer

---

### Task 4.2: Refactor _get_object_asset star color logic [Medium]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/unit/ui/test_star_color_mapping.py -v`

Replace the 12 lines of magic number color logic with manifest lookup.

- [ ] Locate `_get_object_asset()` method (around line 492)
- [ ] Find the star color logic (lines 497-508):

  **BEFORE:**
  ```python
  if is_star(obj):
      color = obj.color
      asset_key = 'yellow'
      if color[0] > 200 and color[1] < 100:
          asset_key = 'red'
      elif color[2] > 200 and color[0] < 100:
          asset_key = 'blue'
      elif color[0] > 200 and color[1] > 200 and color[2] > 200:
          asset_key = 'white'
      elif color[0] > 200 and color[1] > 150:
          asset_key = 'orange'
      return am.get_image('stars', asset_key)
  ```

  **AFTER:**
  ```python
  if is_star(obj):
      am = get_asset_manager()
      asset_key = am.get_star_color_key(obj.color)
      return am.get_image('stars', asset_key)
  ```
- [ ] Verify star rendering still works with manual test (start game, look at stars)
- [ ] Run star color tests: `pytest tests/unit/ui/test_star_color_mapping.py -v`

**Notes:** Reduces 12 lines to 3 lines, eliminates magic numbers

---

### Task 4.3: Update imports and cleanup [Simple]
**File:** `game/ui/screens/strategy_scene.py`
**Tests:** `pytest tests/strategy/test_strategy_scene.py -v`

Clean up any unused imports and verify the refactored code.

- [ ] Check if `ASSET_DIR` import is still needed elsewhere in the file
  - If only used in removed code, remove the import
  - If used elsewhere, keep it
- [ ] Verify all imports are still required (no unused imports)
- [ ] Remove any dead code or comments from the refactoring
- [ ] Run strategy tests: `pytest tests/strategy/test_strategy_scene.py -v`
- [ ] Run full test suite: `pytest tests/`

**Notes:** ASSET_DIR may still be used in other parts of strategy_scene.py

---

### Task 4.4: Manual verification [Simple]
**Tests:** Manual testing in-game

Verify the refactored code works correctly in the actual game.

- [ ] Start the game
- [ ] Create a new game with 4 empires using different races/themes
- [ ] Verify colony flags appear on owned planets
- [ ] Verify fleet icons appear correctly
- [ ] Verify stars render with correct colors (look for red, blue, yellow, white stars)
- [ ] Save and reload the game - verify assets persist correctly
- [ ] Load an older save file (if available) - verify backward compatibility

**Notes:** Document any visual differences or issues in the Notes section below

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `strategy_scene._load_assets()` uses RaceAssetLoader (not hardcoded paths)
- [ ] `strategy_scene._get_object_asset()` uses AssetManager.get_star_color_key()
- [ ] Run `pytest tests/repro_issues/test_bug_13_colony_flags.py -v` - all pass
- [ ] Run `pytest tests/` - full suite passes
- [ ] Manual verification complete - game works correctly
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
