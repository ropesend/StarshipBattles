# Phase 5: Update Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-37 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update existing tests and ensure comprehensive test coverage for refactored code

---

## Tasks

### Task 5.1: Update star color tests for manifest [Simple]
**File:** `tests/unit/ui/test_star_color_mapping.py`
**Tests:** `pytest tests/unit/ui/test_star_color_mapping.py -v`

Update Phase 1 tests to use the new manifest-based approach.

- [ ] Open `tests/unit/ui/test_star_color_mapping.py`
- [ ] Update tests to call `AssetManager.get_star_color_key()` instead of directly testing strategy_scene logic
- [ ] Add test for manifest loading of star_colors section:
  ```python
  def test_star_colors_loaded_from_manifest(self):
      """Test that star colors are read from manifest."""
      am = get_asset_manager()
      am.load_manifest()
      assert 'star_colors' in am.manifest
      assert 'red' in am.manifest['star_colors']
  ```
- [ ] Add test for missing star_colors section fallback:
  ```python
  def test_star_color_fallback_when_manifest_empty(self):
      """Test graceful fallback when manifest has no star_colors."""
      am = get_asset_manager()
      am.manifest = {}
      # Should not raise, should return 'yellow'
      assert am.get_star_color_key((255, 0, 0)) == 'yellow'
  ```
- [ ] Run updated tests: `pytest tests/unit/ui/test_star_color_mapping.py -v`

**Notes:** Tests now validate the refactored manifest-based implementation

---

### Task 5.2: Verify BUG-13 regression test still passes [Simple]
**File:** `tests/repro_issues/test_bug_13_colony_flags.py`
**Tests:** `pytest tests/repro_issues/test_bug_13_colony_flags.py -v`

Run the critical BUG-13 regression test suite.

- [ ] Run full BUG-13 test suite: `pytest tests/repro_issues/test_bug_13_colony_flags.py -v`
- [ ] Verify all 5 tests pass:
  - `test_colony_flag_loaded_when_theme_path_valid`
  - `test_renderer_uses_flag_image_not_circle_fallback`
  - `test_fallback_to_circle_when_no_flag`
  - `test_empire_theme_path_from_game_config`
  - `test_load_assets_uses_empire_theme_id_not_saved_path`
- [ ] If any fail, investigate and fix (do NOT skip this step!)

**Notes:** This is the critical integration test - all tests MUST pass

---

### Task 5.3: Run full test suite [Simple]
**Tests:** `pytest tests/ -v`

Run the complete test suite to ensure no regressions.

- [ ] Run full test suite: `pytest tests/`
- [ ] Verify all tests pass (should be 100+ tests)
- [ ] If any tests fail, investigate and fix before proceeding
- [ ] Document test count and any issues in Notes section

**Notes:** Expected test count should match or exceed baseline from project start

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

**Notes:** Document any issues found

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Star color tests updated for manifest-based approach
- [ ] BUG-13 regression tests all passing
- [ ] Full test suite passing: `pytest tests/`
- [ ] Manual verification complete
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"

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
