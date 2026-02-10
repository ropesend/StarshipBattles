# Phase 2: TestLabScreen Validation Manager [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-86 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract validation logic from TestLabScreen into a new `validation_manager.py` module. This removes ~258 lines of static validation and metadata update logic that depends on the data_extractor from Phase 1.

**File:** `game/ui/screens/test_lab/screen.py`
**New File:** `game/ui/screens/test_lab/validation_manager.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ tests/unit/test_lab/ -x`

---

## Tasks

### Task 2.1: Create validation_manager.py [Medium]
**File:** `game/ui/screens/test_lab/validation_manager.py` (new)

- [x] Create new file `game/ui/screens/test_lab/validation_manager.py`
- [x] Create `class TestLabValidationManager` with constructor accepting:
  - `registry` - TestRegistry instance
  - `data_extractor` - TestLabDataExtractor instance (from Phase 1)
  - `all_scenarios` - dict of all scenarios (or a callable that returns them)
- [x] Move `_validate_all_scenarios` logic (lines 329-393) into `ValidationManager.validate_all(self)` method
- [x] Move `_build_validation_context_from_files` logic (lines 395-446) into `ValidationManager.build_context_from_files(self, test_id, metadata)` method
- [x] Move `_handle_update_expected_values` logic (lines 476-523) into `ValidationManager.handle_update_expected_values(self, selected_test_id, ui_manager, screen_width, screen_height, on_confirm_callback)` method
  - Note: This method creates a `ConfirmationDialog` -- pass the UI manager and screen dimensions as params, or accept a dialog factory callback
- [x] Move `_apply_metadata_updates` logic (lines 525-613) into `ValidationManager.apply_metadata_updates(self, changes)` method
- [x] Ensure imports: `json`, `os`, `simulation_tests.logging_config.get_logger`, `.dialogs.ConfirmationDialog`
- [x] Add docstrings to module and class

**Notes:** `_handle_update_expected_values` creates a `ConfirmationDialog` with `self.game.screen.get_width/Height()` and `self.ui_manager`. To avoid coupling to the screen, accept these as parameters or pass a dialog creation callback. Prefer parameter approach for simplicity.

---

### Task 2.2: Update screen.py to delegate to validation_manager [Simple]
**File:** `game/ui/screens/test_lab/screen.py`

- [x] Add import: `from .validation_manager import TestLabValidationManager`
- [x] In `TestLabScreen.__init__`, create `self._validation_manager = TestLabValidationManager(self.registry, self._data_extractor, lambda: self.all_scenarios)`
- [x] Replace `_validate_all_scenarios` method body with delegation: `self._validation_manager.validate_all()`
- [x] Replace `_build_validation_context_from_files` method body with delegation: `return self._validation_manager.build_context_from_files(test_id, metadata)`
- [x] Replace `_handle_update_expected_values` method body with delegation, passing UI params:
  ```python
  self.confirmation_dialog = self._validation_manager.handle_update_expected_values(
      self.selected_test_id, self.ui_manager,
      self.game.screen.get_width(), self.game.screen.get_height()
  )
  ```
- [x] Replace `_apply_metadata_updates` method body with delegation: `self._validation_manager.apply_metadata_updates(changes)`
- [x] Remove now-unused imports from screen.py (check: `Validator` import at line 338, `json` if only used here)

**Notes:** The `_handle_update_expected_values` wrapper needs to store the returned dialog in `self.confirmation_dialog` for the event handler to process.

---

### Task 2.3: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/ui/test_lab_scene/ tests/unit/test_lab/ -x`

- [x] Run targeted tests for TestLabScreen - 114 passed
- [x] Run full test suite: `pytest tests/ -n 12` - 7524 passed
- [x] Verify no import errors
- [x] Verify line count of `screen.py` decreased by ~200+ lines (2382 → 2164, 218 lines saved)
- [x] Fix any failures discovered (none)

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to Complete
- [x] Update plan.md phase table row to Complete
- [x] Update plan.md Current State to point to next phase
