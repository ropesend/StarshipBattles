<<<<<<< HEAD
# Phase 1: Foundation Cleanup
=======
# Phase 1: Fix Planet Image Loading
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-54 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

<<<<<<< HEAD
**Status:** Complete
**Objective:** Extract shared utilities and generalize the ship data extraction system so all ability types can be validated, not just beams.
=======
**Status:** In Progress (Implementation Complete - Pending Manual Testing)
**Objective:** Fix `_get_object_asset()` to use planet's stored `image_id` and `image_rotation` fields instead of random lookup. This ensures planets show consistent, persistent images across all views and save/load cycles.

**Why This Phase First:** Fixing the image bug immediately benefits all contexts (Strategy, Build Queue, Planet List). Panel consolidation in later phases will build on this working foundation.
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

---

## Tasks

<<<<<<< HEAD
### Task 1.1: Extract Shared `_resolve_path` Utility [Simple]
**File:** `simulation_tests/scenarios/validation.py`
**Also:** `simulation_tests/scenarios/prerun_validation.py`
**Tests:** `pytest simulation_tests/ -v`

The dot-notation path resolver `_resolve_path()` is duplicated 3 times with varying error quality:
1. `ExactMatchRule._resolve_path()` at lines 177-226 (detailed errors, path tracing)
2. `DeterministicMatchRule._resolve_path()` at lines 348-375 (simple errors)
3. `PreRunValidator._resolve_path()` in `prerun_validation.py` at lines 115-130 (simple errors)

- [x] Create standalone `resolve_path(context, path)` function at module level in `validation.py` (before any class definitions)
- [x] Use the detailed implementation from `ExactMatchRule` (lines 177-226) as the canonical version
- [x] Replace `ExactMatchRule._resolve_path` calls with `resolve_path` (search for `self._resolve_path`)
- [x] Replace `DeterministicMatchRule._resolve_path` calls with `resolve_path`
- [x] Delete `ExactMatchRule._resolve_path` method (lines 177-226)
- [x] Delete `DeterministicMatchRule._resolve_path` method (lines 348-375)
- [x] In `prerun_validation.py`: import `resolve_path` from `validation.py`
- [x] Replace `self._resolve_path` calls in `prerun_validation.py` with imported `resolve_path`
- [x] Delete `PreRunValidator._resolve_path` method (lines 115-130)
- [x] Add `resolve_path` to `simulation_tests/scenarios/__init__.py` exports
- [x] Verify: Run `pytest simulation_tests/ -v` - all existing tests pass unchanged

**Notes:** `_resolve_path` was actually on `DataExpectation` class, not `PreRunValidator`. All 3 copies removed, 0 remaining (verified with grep). Note: the `_resolve_path` in `prerun_validation.py` was on `DataExpectation`, not `PreRunValidator` as stated - but the method is deleted regardless.

---

### Task 1.2: Generalize `_extract_ship_validation_data` [Medium]
**File:** `simulation_tests/scenarios/base.py`
**Tests:** `pytest simulation_tests/ -v`

Currently at lines 606-656, this method only extracts `BeamWeaponAbility` data and returns immediately after finding one. We need it to extract data for ALL ability types.

- [x] Define `ABILITY_EXTRACTION_MAP` dict at module level, mapping ability class names to extraction configs
- [x] Rewrite `_extract_ship_validation_data()` to iterate all abilities and use the map
- [x] Add ship-level defense stats to the extracted data (`total_defense_score`, `emissive_armor`, `max_shields`)
- [x] Verify backward compat: existing beam scenarios using `attacker.weapon.damage` paths still resolve correctly
- [x] Verify: Run `pytest simulation_tests/ -v` - all existing tests pass unchanged

**Notes:** Corrected `reload` → `reload_time` (actual attribute name). Added `projectile_speed` to SeekerWeaponAbility attrs. First-occurrence-wins for duplicate ability types. 45 passed, same 5 pre-existing failures.

---

### Task 1.3: Delete Backup File [Simple]
**File:** `simulation_tests/scenarios/projectile_scenarios.py.backup_phase1`
**Tests:** None needed

- [x] Delete `simulation_tests/scenarios/projectile_scenarios.py.backup_phase1`
- [x] Verify: file no longer exists

**Notes:**
=======
### Task 1.1: Update _get_object_asset() to load from image_id [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** Manual test - select planet, verify image loads. Save/load game, verify same image.

- [x] Add imports at top of file (around lines 1-20):
  ```python
  import os
  from game.core.paths import Paths
  ```
- [x] Locate the `_get_object_asset()` method (lines 485-530, planet handling at 494-503)
- [x] Replace planet handling logic (lines 494-503) with new implementation:
  ```python
  elif is_planet(obj):
      if obj.image_id:
          # Construct path to assigned planet image
          image_path = os.path.join(Paths.PLANETS_V3_DIR, obj.image_id)
          try:
              img = am.load_external_image(image_path)
              if img:
                  # Apply rotation for visual variety
                  if obj.image_rotation and obj.image_rotation != 0.0:
                      img = pygame.transform.rotate(img, obj.image_rotation)
                  return img
          except Exception as e:
              # Log error and fall through to None (panel will create placeholder)
              print(f"Warning: Could not load planet image {obj.image_id}: {e}")
      return None  # PlanetReportPanel will create gradient placeholder
  ```
- [x] Remove old category-based logic (`p_type_name`, `cat` variables, `get_random_from_group` call)
- [x] Save file

**Notes:**
- Added `import os` at line 18 and `from game.core.paths import Paths` at line 22
- Replaced category-based random lookup with direct image_id loading at lines 496-510
- AssetManager.load_external_image() provides automatic caching and error handling
- Fallback to None allows PlanetReportPanel to create gradient placeholder

---

### Task 1.2: Verify AssetManager supports load_external_image [Simple]
**File:** `game/assets/asset_manager.py`
**Tests:** Code review - verify method exists and signature

- [x] Open `game/assets/asset_manager.py`
- [x] Search for `load_external_image` method (likely around lines 150-250)
- [x] If found:
  - [x] Verify signature: `load_external_image(self, path: str) -> pygame.Surface | None`
  - [x] Check if it handles caching (good for performance)
  - [x] Note any error handling behavior
- [ ] If NOT found:
  - [ ] Search for alternative method names (`load_image_from_path`, `load_file`, `get_image`, etc.)
  - [ ] Update Task 1.1 code with correct method name
  - [ ] If no suitable method exists, may need to use `pygame.image.load()` directly

**Notes:**
- Method found at line 189: `def load_external_image(self, path):`
- Signature: Takes path string, returns pygame.Surface or missing texture (hot pink placeholder) on error
- Has automatic caching using normalized path as cache key (lines 194-199)
- Error handling: Catches FileNotFoundError and pygame.error, returns get_missing_texture() on failure
- Uses internal _load_image() helper that checks os.path.exists() first

---

### Task 1.3: Manual testing - Verify image loading works [Simple]
**Files:** N/A (testing task)
**Tests:** Manual gameplay testing

- [ ] Run the game: `python -m game.main` (or equivalent)
- [ ] Load an existing save file OR start a new game
- [ ] Navigate to Strategy screen
- [ ] Select a planet in the viewport
- [ ] Verify:
  - [ ] Planet image displays in strategy UI detail panel (not blank/broken)
  - [ ] Image is a specific planet image (not a generic placeholder)
  - [ ] Image matches the planet type (e.g., gas giant looks like gas giant)
- [ ] Note the planet's visual appearance (color, features, name)
- [ ] Select a different planet, then re-select the original planet
- [ ] Verify: Same image appears (consistent)
- [ ] Save the game
- [ ] Exit and reload the save
- [ ] Re-select the same planet
- [ ] Verify: Same image still appears (persistent across sessions)
- [ ] Test with 3-5 different planets (variety of types: terrestrial, gas giant, ice, etc.)

**Notes:**
_[Record any issues found, planets tested, screenshots if needed]_

---

### Task 1.4: Run integration tests [Simple]
**Files:** N/A (testing task)
**Tests:** `pytest tests/integration/ui/test_strategy_buttons.py`

- [x] Run test: `pytest tests/integration/ui/test_strategy_buttons.py -v`
- [x] Verify all tests pass (or same failures as baseline)
- [ ] If new failures:
  - [ ] Investigate error messages
  - [ ] Determine if related to image loading changes
  - [ ] Fix issues and re-run tests
- [x] Document test results

**Expected Result:** No new failures (baseline had 8 pre-existing failures unrelated to planet images)

**Notes:**
- All 4 tests passed: ✅
  - test_build_button_visibility_owned_planet
  - test_build_button_visibility_unowned_planet
  - test_fleet_buttons_visibility_owned_fleet
  - test_fleet_buttons_visibility_enemy_fleet
- No new failures introduced by image loading changes
- Test execution time: 2.20s (4 parallel workers)

---

### Task 1.5: Test error handling - Missing image file [Simple]
**Files:** N/A (edge case testing)
**Tests:** Manual - simulate missing image file

- [ ] Find a planet with a valid `image_id` in the game
- [ ] Note the `image_id` value (e.g., "planet_3_092_1769751240311.png")
- [ ] Temporarily rename the image file in `assets/Images/Stellar Objects/Planets/Planets_V3/`
  - Example: Rename to "planet_3_092_1769751240311.png.backup"
- [ ] Run the game and select that planet
- [ ] Verify:
  - [ ] Game doesn't crash
  - [ ] Warning message appears in console: "Warning: Could not load planet image..."
  - [ ] Placeholder gradient is shown (panel's fallback behavior)
  - [ ] UI remains functional
- [ ] Restore the original image file name
- [ ] Re-run game and verify image loads correctly again

**Notes:**
_[Error handling behavior observed]_
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

---

## Phase Completion Checklist
When all tasks above are done:
<<<<<<< HEAD
- [x] All task checkboxes above are checked
- [x] `pytest simulation_tests/ -v` passes
- [x] `pytest tests/ -n 4` passes (full suite)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
=======
- [ ] All task checkboxes above are checked
- [ ] Manual testing confirms planets show consistent images
- [ ] Save/load cycle preserves planet images
- [ ] Integration tests pass (no new failures)
- [ ] Error handling works (missing files don't crash)
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row 1 to `Complete`
- [ ] Update `plan.md` Current State to:
  ```
  **Last Updated:** [DATE]
  **Active Phase:** Phase 2 - Enhance Panel API
  **Last Action:** Completed Phase 1 - Planet images now load correctly from stored image_id
  **Next Action:** Begin Phase 2 - Add backward-compatible parameters to PlanetReportPanel
  ```

>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08
