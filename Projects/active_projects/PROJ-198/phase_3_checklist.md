# Phase 3: Monkey-Patch Elimination

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-198 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace 3 monkey-patching anti-patterns (stamping attributes on library UIButton objects) with proper dict lookups.

---

## Tasks

### Task 3.1: DesignSelectorWindow — Button Identification [Medium]
**File:** `game/ui/screens/design_selector_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k design --testmon`

- [x] Add `self._button_design_map: Dict[UIButton, str] = {}` in `__init__`
- [x] Add `self._obsolete_buttons: Set[UIButton] = set()` in `__init__`
- [x] Add `self._obsolete_state_map: Dict[UIButton, bool] = {}` in `__init__`
- [x] L403-405: Replace monkey-patches with dict/set entries
- [x] L417: Replace `select_btn.design_id = ...` with dict entry
- [x] L459: Replace `hasattr(event.ui_element, 'is_obsolete_button')` with `event.ui_element in self._obsolete_buttons`
- [x] L464: Replace `hasattr(event.ui_element, 'design_id')` with `event.ui_element in self._button_design_map`
- [x] Clear dicts/sets at top of `_rebuild_design_list()` before rebuilding
- [x] Update references to `current_obsolete_state` to use map
- [x] Verify: button clicks still work correctly for select and obsolete toggle

**Notes:** Also updated test helper `_make_selector_window()` to include new attributes.

### Task 3.2: BuildQueueSelector — Button Index [Medium]
**File:** `game/ui/screens/build_queue_selector.py`
**Tests:** `pytest tests/unit/ui/screens/ -k build_queue --testmon`

- [x] Add `self._button_index_map: Dict[UIButton, int] = {}` in `__init__`
- [x] L117: Replace `btn.queue_source_index = idx` with dict entry
- [x] L140: Replace `hasattr(button, 'queue_source_index')` with `button in self._button_index_map`
- [x] Replace all `button.queue_source_index` access with dict lookup
- [x] Clear dict when rebuilding buttons
- [x] Verify: queue source selection still works

**Notes:** Also updated integration test `test_queue_selector_has_queue_source_index_tags` to use new dict pattern.

### Task 3.3: FleetOrdersWindow — Row Cleanup [Simple]
**File:** `game/ui/screens/fleet_orders_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k fleet --testmon`

- [x] L93-95: Replace `hasattr(element, 'kill')` with key exclusion:
  ```python
  for key, element in row.items():
      if key != 'order_ref':
          element.kill()
  ```
- [x] Verify: fleet orders window cleanup still works

**Notes:** Simple fix - the row dict has known keys, with 'order_ref' being the only non-UI value.

### Task 3.4: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] All tests pass
- [x] No new failures introduced

**Notes:** 12728 passed, 1 skipped

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
