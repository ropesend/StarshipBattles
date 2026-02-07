# Phase 6: Final Integration and Testing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-54 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Final integration testing across all 4 contexts (Strategy, Build Queue, Planet List, Colonize). Update affected tests. Verify no regressions.

**Why This Phase:** Ensures all changes work together harmoniously. Catches integration issues. Provides confidence in the consolidation.

---

## Tasks

### Task 6.1: Update test_build_queue_enhanced_planet_report.py [Medium]
**File:** `tests/integration/ui/test_build_queue_enhanced_planet_report.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_enhanced_planet_report.py -v`

- [ ] Review all 20 tests in the file
- [ ] Update tests that create PlanetReportPanel to use new parameters if beneficial:
  ```python
  # Example - test can now pass portrait_surface at init:
  panel = PlanetReportPanel(
      manager=manager,
      rect=rect,
      planet=planet,
      portrait_surface=test_portrait  # NEW parameter
  )
  ```
- [ ] Add new tests for Phase 2 features:
  - [ ] Test for `portrait_surface` at init (if not already added in Phase 2)
  - [ ] Test for `show_complexes=False` (if not already added in Phase 2)
- [ ] Run tests: `pytest tests/integration/ui/test_build_queue_enhanced_planet_report.py -v`
- [ ] Verify all tests pass
- [ ] Fix any failures

**Notes:**
_[Test results, failures fixed]_

---

### Task 6.2: Update test_planet_complexes_list.py [Simple]
**File:** `tests/integration/ui/test_planet_complexes_list.py`
**Tests:** `pytest tests/integration/ui/test_planet_complexes_list.py -v`

- [ ] Review all 8 tests
- [ ] Verify tests still pass with `show_complexes=True` (default)
- [ ] Add test for `show_complexes=False` if not already present:
  ```python
  def test_no_complexes_list_when_disabled(session_with_planet, manager):
      """Test that complexes list is not created when show_complexes=False."""
      planet = session_with_planet.galaxy.planets[0]

      panel = PlanetReportPanel(
          manager=manager,
          rect=pygame.Rect(0, 0, 580, 350),
          planet=planet,
          show_complexes=False
      )

      # Verify container is None
      assert panel.complexes_container is None
      assert panel.complex_items == []
  ```
- [ ] Run tests: `pytest tests/integration/ui/test_planet_complexes_list.py -v`
- [ ] Verify all pass
- [ ] Fix any failures

**Notes:**
_[Test results]_

---

### Task 6.3: Run full test suite [Medium]
**Files:** All tests
**Tests:** `pytest tests/`

- [ ] Run full test suite: `pytest tests/`
- [ ] Compare results to baseline (6106 passed, 5 skipped, 8 failed pre-existing)
- [ ] Verify NO NEW FAILURES introduced
- [ ] If new failures:
  - [ ] Investigate each failure
  - [ ] Determine if related to PROJ-54 changes
  - [ ] Fix issues
  - [ ] Re-run until clean
- [ ] Document final test counts

**Expected:** 6106+ passed, 5 skipped, 8 failed (same pre-existing failures)

**Notes:**
_[Final test counts: ___ passed, ___ skipped, ___ failed]_

---

### Task 6.4: Manual Test - Strategy Viewport [Simple]
**Files:** N/A (manual testing)
**Tests:** Run game, test strategy screen

- [ ] Run the game
- [ ] Navigate to Strategy screen
- [ ] **Test 1: Planet image consistency**
  - [ ] Select planet "Alpha" (or any planet)
  - [ ] Note the planet's visual appearance (color, features)
  - [ ] Select a different planet
  - [ ] Re-select planet "Alpha"
  - [ ] Verify: Same image appears (not random)
- [ ] **Test 2: Panel displays correctly**
  - [ ] Select a planet
  - [ ] Verify: Planet report panel shows (portrait, info, atmosphere graph)
  - [ ] Verify: NO complexes list (show_complexes=False working)
- [ ] **Test 3: Build Queue button**
  - [ ] Select an owned planet
  - [ ] Verify: "Open Build Queue" button appears below panel
  - [ ] Click button
  - [ ] Verify: Build queue screen opens for that planet
  - [ ] Return to strategy screen
  - [ ] Select an unowned planet
  - [ ] Verify: NO button appears
- [ ] **Test 4: Image persistence**
  - [ ] Note planet "Alpha" image
  - [ ] Save game
  - [ ] Exit game
  - [ ] Reload save
  - [ ] Select planet "Alpha"
  - [ ] Verify: Same image appears

**Notes:**
_[Any issues found]_

---

### Task 6.5: Manual Test - Build Queue [Simple]
**Files:** N/A (manual testing)
**Tests:** Run game, test build queue

- [ ] From strategy screen, select owned planet
- [ ] Click "Open Build Queue" button
- [ ] **Test 1: Panel displays**
  - [ ] Verify: Planet report panel shows at top
  - [ ] Verify: Portrait displays (Phase 2 portrait_surface working)
  - [ ] Verify: Complexes list shows (if planet has facilities)
- [ ] **Test 2: Image matches strategy view**
  - [ ] Note planet image in build queue
  - [ ] Close build queue, return to strategy
  - [ ] Verify: Same planet shows same image
- [ ] **Test 3: Panel updates correctly**
  - [ ] In build queue, build a new facility
  - [ ] Complete construction (advance turns if needed)
  - [ ] Verify: Complexes list updates to show new facility

**Notes:**
_[Any issues found]_

---

### Task 6.6: Manual Test - Planet List Window [Simple]
**Files:** N/A (manual testing)
**Tests:** Run game, test planet list

- [ ] From strategy screen, open Planet List window
- [ ] **Test 1: Layout**
  - [ ] Verify: List is on left side (narrower than before)
  - [ ] Verify: Space for panel on right
- [ ] **Test 2: Panel appears on selection**
  - [ ] Click on a planet in the list
  - [ ] Verify: Planet report panel appears on right
  - [ ] Verify: Panel shows portrait, info, atmosphere, complexes
- [ ] **Test 3: Image consistency**
  - [ ] Select planet "Alpha" in list
  - [ ] Note image
  - [ ] Close planet list, select same planet in strategy view
  - [ ] Verify: Same image
- [ ] **Test 4: Build Queue button**
  - [ ] In planet list, select owned planet
  - [ ] Verify: "Open Build Queue" button below panel
  - [ ] Click button
  - [ ] Verify: Build queue opens for that planet
  - [ ] Return to planet list
  - [ ] Select unowned planet
  - [ ] Verify: NO button appears
- [ ] **Test 5: Selection updates**
  - [ ] Select planet A
  - [ ] Verify panel shows planet A info
  - [ ] Select planet B
  - [ ] Verify panel updates to planet B info

**Notes:**
_[Any issues found]_

---

### Task 6.7: Manual Test - Colonize Window [Simple]
**Files:** N/A (manual testing)
**Tests:** Run game, test colonization

- [ ] From strategy screen, select uncolonized planet
- [ ] Trigger colonization command (open colonize dialog)
- [ ] **Test 1: Window opens**
  - [ ] Verify: Colonize window displays
  - [ ] Verify: Planet list on left
  - [ ] Verify: No panel initially (no selection)
- [ ] **Test 2: Panel on selection**
  - [ ] Click on a planet in list
  - [ ] Verify: Full planet report panel appears on right
  - [ ] Verify: Panel fits in window (no cut-off)
  - [ ] Verify: Shows portrait, info, atmosphere, complexes (empty for uncolonized)
- [ ] **Test 3: Image consistency**
  - [ ] Select planet in colonize dialog
  - [ ] Note image
  - [ ] Cancel dialog, view same planet in strategy screen
  - [ ] Verify: Same image
- [ ] **Test 4: Colonization works**
  - [ ] Select a planet
  - [ ] Confirm colonization
  - [ ] Verify: Colony established (no crashes, game continues normally)

**Notes:**
_[Any issues found]_

---

### Task 6.8: Cross-context consistency test [Simple]
**Files:** N/A (manual testing)
**Tests:** Verify same planet shows same data everywhere

- [ ] **Choose a test planet** (e.g., "Alpha" or any specific planet)
- [ ] **View in Strategy screen**
  - [ ] Note: Image, planet type, mass, temperature, etc.
- [ ] **View in Build Queue** (if owned)
  - [ ] Verify: Same image
  - [ ] Verify: Same stats displayed
  - [ ] Verify: Facilities list matches
- [ ] **View in Planet List**
  - [ ] Select same planet
  - [ ] Verify: Same image
  - [ ] Verify: Same stats displayed
- [ ] **View in Colonize window** (if uncolonized)
  - [ ] Verify: Same image
  - [ ] Verify: Same stats
- [ ] **Result:** All 4 contexts show identical planet information

**Notes:**
_[Consistency verified across all contexts]_

---

### Task 6.9: Code review - duplicate elimination [Simple]
**Files:** Code review
**Tests:** Manual review

- [ ] Verify `format_planet_info()` only exists in ONE location:
  - [ ] Present in: `game/ui/screens/strategy_detail_fmt.py` ✓
  - [ ] NOT in: `game/ui/screens/strategy_ui.py` (deleted in Phase 3)
- [ ] Search for any remaining duplicate planet formatting:
  ```bash
  grep -r "planet_type.name.lower()" game/ui/screens/
  ```
- [ ] If duplicates found, document (should only be in deprecated code or unrelated features)
- [ ] Verify all buttons are EXTERNAL to PlanetReportPanel:
  - [ ] Strategy UI: btn_build_queue in strategy_ui.py ✓
  - [ ] Planet List: btn_build_queue in planet_list_window.py ✓
  - [ ] Build Queue: N/A (doesn't need button)
  - [ ] Colonize: N/A (doesn't need button)

**Notes:**
_[Code review findings]_

---

### Task 6.10: Performance spot check [Simple]
**Files:** N/A (performance testing)
**Tests:** Manual - verify no performance degradation

- [ ] Run game, navigate to strategy screen
- [ ] Select multiple planets rapidly (10-15 planets)
- [ ] Observe: Frame rate, responsiveness
- [ ] Expected: Smooth, no lag (planet image caching working)
- [ ] Open planet list, scroll through 20+ planets
- [ ] Select planets rapidly
- [ ] Observe: No lag, panel updates smoothly
- [ ] If lag observed:
  - [ ] Profile where slowdown occurs
  - [ ] Check if images re-loading unnecessarily
  - [ ] Verify asset_manager caching working

**Notes:**
_[Performance observations]_

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass (no new failures)
- [ ] Manual testing complete across all 4 contexts
- [ ] Planet images consistent everywhere (Phase 1 verified)
- [ ] All panels use PlanetReportPanel (consolidation complete)
- [ ] Duplicate `format_planet_info()` eliminated (Phase 3 verified)
- [ ] Buttons positioned externally (design principle verified)
- [ ] Performance acceptable (no degradation)
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row 6 to `Complete`
- [ ] Update `plan.md` Current State to:
  ```
  **Last Updated:** [DATE]
  **Active Phase:** PROJECT COMPLETE
  **Last Action:** Completed Phase 6 - All integration testing passed
  **Next Action:** None - Project complete, ready for user verification
  ```
- [ ] Mark PROJ-54 as COMPLETE in projects_index.md

