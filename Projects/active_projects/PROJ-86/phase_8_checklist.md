# Phase 8: BuildQueueScreen Re-decomposition [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-86 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Analyze BuildQueueScreen's growth from PROJ-63's 603-line target to 1185 lines, identify new responsibility clusters from feature additions (PROJ-67/69/76/82), and extract appropriate helper modules to bring it back to ~700 lines.

**File:** `game/ui/screens/build_queue_screen.py`
**New Files:** TBD during analysis (Task 8.1)
**Tests:** `pytest tests/integration/ui/test_build_queue_*.py tests/unit/ui/panels/test_build_queue_*.py -x`

---

## Tasks

### Task 8.1: Analyze BuildQueueScreen method clusters [Simple]
**File:** `game/ui/screens/build_queue_screen.py`

- [ ] Read all 28 methods and measure line counts for each
- [ ] Group methods into responsibility clusters:
  - **Queue Selector** (PROJ-69): `_create_queue_selector_panel`, `_refresh_queue_selector`, `_on_queue_selected`, `_on_queue_toggled`, `_update_queue_header`
  - **Layout/Panel Creation**: `_create_background`, `_create_planet_report_panel`, `_create_fleet_info_panel`, `_create_design_report_panel`, `_create_items_list_panel`, `_create_build_queue_panel`, `_create_filter_panel`, `_create_bottom_bar`
  - **Refresh/Display**: `_refresh_items_list`, `_refresh_queue_display`, `_apply_tooltips`
  - **Formatting**: `_format_empire_resources`, `_format_resource_cost`
  - **Event Handling**: `handle_event`, `_handle_keydown`, `_handle_remove_hotkey`, `_prompt_target_planet`, `_close`
  - **Lifecycle**: `__init__`, `update`, `draw`, `_take_screenshot`, `_show_screenshot_toast`
- [ ] Identify the largest cluster(s) that can be cleanly extracted
- [ ] Document the extraction plan with target file names and line estimates
- [ ] Update this checklist with concrete extraction tasks (Tasks 8.3-8.5)

**Notes:** The queue selector panel (PROJ-69 addition) is likely the cleanest extraction target -- it is a self-contained sub-component managing multi-queue selection. The filter panel and formatting functions are also good candidates.

---

### Task 8.2: Extract queue selector into helper module [Medium]
**File:** `game/ui/screens/build_queue_selector.py` (new, name TBD from analysis)

- [ ] Create new helper module based on Task 8.1 analysis
- [ ] Move queue selector methods:
  - `_create_queue_selector_panel` (lines 252-289) -- Creates the queue source selector panel
  - `_refresh_queue_selector` (lines 290-332) -- Refreshes queue selector buttons
  - `_on_queue_selected` (lines 333-349) -- Handles single queue selection
  - `_on_queue_toggled` (lines 350-386) -- Handles queue toggle for multi-select
  - `_update_queue_header` (lines 387-398) -- Updates queue panel header text
- [ ] Create `class BuildQueueSelector` with constructor accepting:
  - `manager` - pygame_gui.UIManager
  - `build_context` - Planet/Fleet build context
  - `on_queue_change` - callback when selected queue changes
  - Layout parameters (rect, container panel)
- [ ] Wire delegation in BuildQueueScreen
- [ ] Update all references from `self._on_queue_*` to `self._queue_selector.*`

**Notes:** The queue selector manages `self.queue_sources`, `self.active_queue_index`, `self.active_queue_sources`, `self.queue_selector_panel`, `self.queue_buttons`. These all become owned by the selector.

---

### Task 8.3: Extract formatting and filter helpers [Simple]
**File:** `game/ui/screens/build_queue_helpers.py` (new, name TBD from analysis)

- [ ] Extract `_format_empire_resources` (static method, lines 603-625) as module-level function
- [ ] Extract `_format_resource_cost` (static method, lines 626-644) as module-level function
- [ ] Evaluate extracting `_create_filter_panel` (lines 524-602) -- 78 lines of filter UI creation
- [ ] Wire delegation in BuildQueueScreen
- [ ] Update all call sites within BuildQueueScreen

**Notes:** Both format functions are already `@staticmethod` -- they are pure functions with no instance dependencies. Straightforward extraction.

---

### Task 8.4: Update BuildQueueScreen with delegation [Simple]
**File:** `game/ui/screens/build_queue_screen.py`

- [ ] Add imports for new helper modules
- [ ] Replace extracted method bodies with delegation calls
- [ ] Remove now-unused imports
- [ ] Verify all `self.*` state references are correctly wired through the helpers

**Notes:**

---

### Task 8.5: Run tests and verify [Simple]
**Tests:** `pytest tests/integration/ui/test_build_queue_*.py tests/unit/ui/panels/test_build_queue_*.py -x`

- [ ] Run targeted tests for BuildQueueScreen
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify no import errors
- [ ] Verify line count of `build_queue_screen.py` decreased to ~700 lines or less
- [ ] Fix any failures discovered

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to Complete
- [ ] Update plan.md phase table row to Complete
- [ ] Update plan.md Current State to point to next phase
