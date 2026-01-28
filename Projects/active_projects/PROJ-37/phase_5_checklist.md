# Phase 5: Update Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-37 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (audit verified)
**Objective:** Update existing tests and ensure comprehensive test coverage for refactored code

---

## Tasks

### Task 5.1: Update star color tests for manifest [Simple]
**File:** `tests/unit/ui/test_star_color_mapping.py`
**Tests:** `pytest tests/unit/ui/test_star_color_mapping.py -v`

Update Phase 1 tests to use the new manifest-based approach.

- [x] Open `tests/unit/ui/test_star_color_mapping.py`
- [x] Update tests to call `AssetManager.get_star_color_key()` instead of directly testing strategy_scene logic
- [x] Add test for manifest loading of star_colors section:
  - Tests exist in `tests/unit/core/test_asset_manager.py::TestGetStarColorKey`
  - Tests verify manifest parsing with proper thresholds
- [x] Add test for missing star_colors section fallback:
  - `test_get_star_color_key_no_manifest` in test_asset_manager.py (line 263)
  - `test_get_star_color_key_no_star_colors_section` in test_asset_manager.py (line 269)
- [x] Run updated tests: `pytest tests/unit/ui/test_star_color_mapping.py -v` - 15 tests passing

**Notes:** Tests updated during Phase 4. Manifest tests located in test_asset_manager.py (more appropriate location)

---

### Task 5.2: Verify BUG-13 regression test still passes [Simple]
**File:** `tests/repro_issues/test_bug_13_colony_flags.py`
**Tests:** `pytest tests/repro_issues/test_bug_13_colony_flags.py -v`

Run the critical BUG-13 regression test suite.

- [x] Run full BUG-13 test suite: `pytest tests/repro_issues/test_bug_13_colony_flags.py -v`
- [x] Verify all 6 tests pass:
  - `test_colony_flag_loaded_when_theme_path_valid` ✓
  - `test_renderer_uses_flag_image_not_circle_fallback` ✓
  - `test_fallback_to_circle_when_no_flag` ✓
  - `test_empire_theme_path_from_game_config` ✓
  - `test_load_assets_uses_empire_theme_id_not_saved_path` ✓
  - `test_load_assets_works_with_different_theme_ids` ✓ (additional test)
- [x] All tests pass - no issues found

**Notes:** All 6 BUG-13 regression tests passing. Verified during audit 2026-01-28.

---

### Task 5.3: Run full test suite [Simple]
**Tests:** `pytest tests/ -v`

Run the complete test suite to ensure no regressions.

- [x] Run full test suite: `pytest tests/`
- [x] Verify all tests pass (should be 100+ tests)
- [x] No test failures - all passing
- [x] Test count: 4998 passed, 1 skipped, 196 warnings

**Notes:** Full test suite verified during audit 2026-01-28. Baseline exceeded.

---

### Task 5.4: Final manual verification [Simple]
**Tests:** Manual testing checklist

Complete final manual verification of the refactored functionality.

- [ ] Start new game with Federation theme
- [ ] Start new game with Atlantians theme
- [ ] Start new game with custom race (flag_id set)
- [ ] Verify all star colors render (red, blue, yellow, white, orange)
- [ ] Verify colony flags on planets
- [ ] Verify fleet icons
- [ ] Load old save file (before refactor) - verify works
- [ ] Save new game, exit, reload - verify assets persist

**Notes:** Requires user manual verification. Cannot be automated.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (except manual verification)
- [x] Star color tests updated for manifest-based approach
- [x] BUG-13 regression tests all passing (6/6)
- [x] Full test suite passing: `pytest tests/` (4998 passed)
- [ ] Manual verification complete (requires user)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete" (pending manual verification)

---

## Project Completion

When Phase 5 is complete, the project is done. Final steps:

- [ ] Update `Projects/projects_index.md` to mark PROJ-37 as Complete
- [ ] Create git commit with all changes:
  ```
  git add -A
  git commit -m "PROJ-37: Refactor fragile asset loading to use centralized config"
  ```
- [ ] Run final audit: `python Projects/scripts/audit_project.py PROJ-37`
