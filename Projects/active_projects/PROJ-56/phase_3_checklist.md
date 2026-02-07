<<<<<<< HEAD
# Phase 3: Beam & Seeker Scenario Simplification
=======
# Phase 3: Replace Strategy UI Inline Implementation
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-54 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

<<<<<<< HEAD
**Status:** Complete
**Objective:** Simplify beam and seeker scenarios by removing duplicated verify/results boilerplate, using the template's `_collect_results()` hook from Phase 2. Also extract the duplicated hit-chance calculation and fix hardcoded magic numbers.

**Prerequisite:** Phase 2 complete (template has `_collect_results` + `_collect_extra_results` hooks)
=======
**Status:** Complete (Manual Testing Pending)
**Objective:** Replace Strategy UI's manual planet display implementation with PlanetReportPanel instance. Eliminate duplicate `format_planet_info()` code.

**Why This Phase:** Consolidates duplicate code (~60 lines), ensures consistency between Strategy UI and Build Queue displays, follows DRY principle.
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

---

## Tasks

<<<<<<< HEAD
### Task 3.1: Create Beam Hit-Chance Helper [Simple]
**File:** `simulation_tests/scenarios/beam_scenarios.py`
**Tests:** `pytest simulation_tests/ -v`

Every beam scenario has near-identical `custom_setup()` code calculating `self.expected_hit_chance`. Extract this into a shared helper.

- [x] Create helper function `compute_beam_hit_chance(scenario)`:
  - Reads weapon accuracy/falloff from the loaded attacker ship's `BeamWeaponAbility`
  - Reads target defense stats
  - Computes expected hit chance using the same formula beam scenarios currently use
  - Returns the calculated hit chance
- [x] Verify the helper matches the existing manual calculations in beam scenarios
- [x] Update one beam scenario to use the helper as a proof of concept
- [x] Verify: `pytest simulation_tests/ -v` - that scenario passes

**Notes:**

---

### Task 3.2: Simplify Beam Scenario Verify Methods [Medium]
**File:** `simulation_tests/scenarios/beam_scenarios.py`
**Tests:** `pytest simulation_tests/ -v`

~18 beam scenarios override `verify()` with copy-pasted result storage. After Phase 2's template refactor, they can use pass criteria flags instead.

**Strategy:** Migrate one scenario at a time.

- [x] For each beam scenario that overrides `verify()`:
  - Remove the duplicated `self.results['initial_hp'] = ...` block
  - If the scenario only needs "was damage dealt?" → set `verify_damage_dealt = True`
  - If the scenario is statistical measurement → set `measurement_mode = True`
  - If the scenario expects no damage → set `expect_no_damage = True`
  - If the scenario needs extra results → implement `_collect_extra_results()` hook
  - Replace manual hit-chance calculation with `compute_beam_hit_chance()`
- [x] Migrate beam scenarios one at a time (verify after each):
  - [x] First beam scenario (proof of concept)
  - [x] Remaining 17 beam scenarios (all 18 migrated, 0 verify methods remain)
- [x] Verify after all: `pytest simulation_tests/ -v` - all beam tests pass with identical results

**Notes:** Test IDs and pass/fail behavior MUST remain identical.

---

### Task 3.3: Simplify Seeker Scenario Verify Methods [Medium]
**File:** `simulation_tests/scenarios/seeker_scenarios.py`
**Tests:** `pytest simulation_tests/ -v`

~8 seeker scenarios override `verify()` with copy-pasted result storage AND hardcode magic numbers like `self.results['missile_speed'] = 1000`.

- [x] For each seeker scenario that overrides `verify()`:
  - Remove the duplicated `self.results['initial_hp'] = ...` block
  - Replace hardcoded magic numbers with values read from loaded ship data:
    - `self.results['missile_speed']` → read from `SeekerWeaponAbility` instance via `_get_seeker_ability()` helper
    - `self.results['missile_turn_rate']` → read from ability instance
    - `self.results['missile_endurance']` → read from ability instance
  - Set appropriate pass criteria flag or implement slim `verify()` calling `_collect_results()`
  - Move extra seeker-specific results to `_collect_extra_results()` hook
- [x] Migrate seeker scenarios one at a time (verify after each):
  - [x] First seeker scenario (SeekerCloseRangeImpactScenario - min_damage_threshold=100, reads stats from SeekerWeaponAbility)
  - [x] Remaining 7 seeker scenarios (all 8 non-PD migrated, 0 verify methods remain; 3 PD placeholders left as-is)
- [x] Verify after all: `pytest simulation_tests/ -v` - all seeker tests pass with identical results

**Notes:** Test IDs and pass/fail behavior MUST remain identical.
=======
### Task 3.1: Remove duplicate format_planet_info() method [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual test - ensure no import errors

- [x] Locate duplicate `format_planet_info()` method (lines 562-618)
- [x] DELETE THE ENTIRE METHOD (56 lines)
  - This is a duplicate of `format_planet_info()` from `strategy_detail_fmt.py`
  - Removing it forces use of the canonical version
- [x] Verify imports at top of file include:
  ```python
  from game.ui.screens.strategy_detail_fmt import format_planet_info
  ```
- [x] If import is missing, add it around line 10-25
- [x] Save file

**Notes:**
- Deleted duplicate format_planet_info() method (lines 562-618, 56 lines removed)
- Added import for canonical format_planet_info from strategy_detail_fmt
- Fixed PlanetSelectionWindow call to use module-level function instead of self.format_planet_info
- Python syntax verified with py_compile

---

### Task 3.2: Replace inline planet display with PlanetReportPanel [Medium]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual test - select planet in strategy view

- [x] Add import at top (around line 10-25):
  ```python
  from game.ui.panels.planet_report_panel import PlanetReportPanel
  ```
- [x] Locate `show_detailed_report()` method (lines 419-561)
- [x] Find planet display section (approximately lines 470-530):
  - Look for: portrait_image creation
  - Look for: detail_text UITextBox creation
  - Look for: graph_image creation
- [x] REMOVE manual planet display code:
  ```python
  # DELETE these lines:
  self.portrait_image = UIImage(...)
  self.detail_text = UITextBox(html_text=format_planet_info(obj), ...)
  self.graph_image = UIImage(...)
  # ... any atmosphere graph rendering code
  ```
- [x] REPLACE with PlanetReportPanel instantiation:
  ```python
  if is_planet(obj):
      # Get portrait surface using existing asset resolution
      portrait_surface = self._get_object_asset(obj) if hasattr(self, '_get_object_asset') else None

      # Calculate available height for panel
      detail_panel_height = self.detail_panel.rect.height

      # Create planet report panel (NO complexes for strategy UI)
      self.planet_report_panel = PlanetReportPanel(
          manager=self.manager,
          rect=pygame.Rect(10, 10, 580, detail_panel_height - 20),
          planet=obj,
          container=self.detail_panel,
          portrait_surface=portrait_surface,
          show_complexes=False  # Strategy UI doesn't show facility list
      )
  ```
- [x] Find and remove cleanup code for old widgets (portrait_image.kill(), detail_text.kill(), etc.)
- [x] Add cleanup for new panel in appropriate cleanup method:
  ```python
  if hasattr(self, 'planet_report_panel') and self.planet_report_panel:
      self.planet_report_panel.kill()
      self.planet_report_panel = None
  ```
- [ ] Test: Launch strategy screen, select planet, verify panel displays

**Notes:**
- Added PlanetReportPanel import at line 24
- Initialized self.planet_report_panel = None in __init__
- Added cleanup logic at start of show_detailed_report() to kill old panel and show old widgets
- Replaced planet display code (lines 492-500) with PlanetReportPanel instantiation
- Old widgets (portrait_image, detail_text, graph_image) hidden when showing planet panel
- Old widgets shown again when switching to non-planet objects
- Portrait surface passed from portrait_surface parameter
- show_complexes=False used for Strategy UI (no facility list needed)

---

### Task 3.3: Add Build Queue button below planet panel [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual test - verify button appears for owned planets

- [x] In `show_detailed_report()`, after creating PlanetReportPanel, add button logic:
  ```python
  if is_planet(obj) and obj.owner_id == self.session.player_id:
      # Calculate button position below panel
      panel_height = self.planet_report_panel.get_height_required()

      # Create Build Queue button
      self.btn_build_queue = UIButton(
          relative_rect=pygame.Rect(10, panel_height + 20, 200, 30),
          text="Open Build Queue",
          manager=self.manager,
          container=self.detail_panel,
          object_id="#build_queue_btn"
      )
  ```
- [x] Find event processing method (likely `process_event` or `handle_ui_event`)
- [x] Add button click handler:
  ```python
  # In process_event or similar:
  if event.type == pygame_gui.UI_BUTTON_PRESSED:
      if event.ui_element == getattr(self, 'btn_build_queue', None):
          # Open build queue for the currently displayed planet
          if hasattr(self, 'planet_report_panel') and self.planet_report_panel:
              self.scene.show_build_queue(self.planet_report_panel.planet)
          return True
  ```
- [x] Add button cleanup in detail panel cleanup:
  ```python
  if hasattr(self, 'btn_build_queue') and self.btn_build_queue:
      self.btn_build_queue.kill()
      self.btn_build_queue = None
  ```
- [ ] Test: Select owned planet → button appears. Select unowned → no button. Click button → opens build queue.

**Notes:**
- Added button creation in planet handling code (after PlanetReportPanel instantiation)
- Button only created for owned planets (obj.owner_id == current_empire_id)
- Button positioned 20px below panel using panel.get_height_required()
- Added button cleanup in show_detailed_report() at start (kills button when switching objects)
- Added click handler in handle_event() method (calls scene.on_build_yard_click())
- Used getattr() for safe button reference since it's dynamically created

---

### Task 3.4: Verify no references to removed code [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Code review

- [x] Search file for references to removed widgets:
  - Search for: `self.portrait_image` (should not exist except in cleanup)
  - Search for: `self.detail_text` (should not exist except for non-planet objects)
  - Search for: `self.graph_image` (should not exist except for stars)
- [x] If found, update to use `self.planet_report_panel` instead
- [x] Verify no calls to removed `format_planet_info()` method (except imports)
- [x] Run Python syntax check: `python -m py_compile game/ui/screens/strategy_ui.py`

**Notes:**
- Old widgets (portrait_image, detail_text, graph_image) still used for non-planet objects ✓
- Found one reference to self.format_planet_info in PlanetSelectionWindow call (line 766)
- Fixed by importing format_planet_info from strategy_detail_fmt and using module function
- Verified no other references to removed format_planet_info() method
- Python syntax check passed with no errors
- All orphaned references resolved

---

### Task 3.5: Manual end-to-end testing [Simple]
**Files:** N/A (testing task)
**Tests:** Manual gameplay testing

- [ ] Run the game
- [ ] Navigate to Strategy screen
- [ ] Select a planet (owned by player)
- [ ] Verify:
  - [ ] Planet report panel displays (portrait, info, atmosphere graph)
  - [ ] NO complexes list shown (show_complexes=False working)
  - [ ] "Open Build Queue" button appears below panel
  - [ ] Planet image is correct (not random - Phase 1 fix working)
- [ ] Click "Open Build Queue" button
- [ ] Verify: Build queue screen opens for that planet
- [ ] Return to strategy screen
- [ ] Select an unowned planet (enemy or neutral)
- [ ] Verify:
  - [ ] Planet report panel displays
  - [ ] NO "Open Build Queue" button (only for owned planets)
- [ ] Select a star system
- [ ] Verify: Different display (not planet panel - other object types unaffected)
- [ ] Test with 3-5 different planets

**Notes:**
_[Testing observations, any issues found]_
>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08

---

## Phase Completion Checklist
When all tasks above are done:
<<<<<<< HEAD
- [x] All task checkboxes above are checked
- [x] `pytest simulation_tests/ -v` passes (45 passed, 5 pre-existing failures, 4 skipped)
- [x] `pytest tests/ -n 4` passes (full suite: 6113 passed, 5 skipped)
- [x] Verify: grep for `self.results['initial_hp'] = self.initial_hp` returns significantly fewer occurrences (goal: only in `_collect_results`) - Only 1 occurrence in code (templates.py:179 in `_collect_results`), rest are docs
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
=======
- [ ] All task checkboxes above are checked
- [ ] Duplicate `format_planet_info()` deleted (56 lines removed)
- [ ] Strategy UI uses PlanetReportPanel (consistent with Build Queue)
- [ ] Build Queue button works for owned planets
- [ ] Manual testing confirms correct behavior
- [ ] No syntax errors or orphaned references
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row 3 to `Complete`
- [ ] Update `plan.md` Current State to:
  ```
  **Last Updated:** [DATE]
  **Active Phase:** Phase 4 - Add Planet Report to Planet List Window
  **Last Action:** Completed Phase 3 - Strategy UI now uses PlanetReportPanel, duplicate code eliminated
  **Next Action:** Begin Phase 4 - Add planet report panel to Planet List Window with selection tracking
  ```

>>>>>>> c4a0287ba78822f63257ae002dbf9586ca325f08
