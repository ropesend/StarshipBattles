# Phase 1: TestLabScreen Data Extraction [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-86 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract data loading functions from TestLabScreen into a new `data_extractor.py` module within the `test_lab/` package. This removes ~211 lines of pure data logic with zero UI dependencies.

**File:** `game/ui/screens/test_lab/screen.py`
**New File:** `game/ui/screens/test_lab/data_extractor.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ tests/unit/test_lab/ -x`

---

## Tasks

### Task 1.1: Create data_extractor.py with extracted functions [Simple]
**File:** `game/ui/screens/test_lab/data_extractor.py` (new)

- [x] Create new file `game/ui/screens/test_lab/data_extractor.py`
- [x] Move `get_test_data_dir()` module-level function from `screen.py` (lines 35-49) into `data_extractor.py`
- [x] Create `class TestLabDataExtractor` with constructor accepting `registry` parameter
- [x] Move `_extract_ships_from_scenario(self, test_id)` logic (lines 198-327) into `TestLabDataExtractor.extract_ships(self, test_id)` method
- [x] Move `_load_component_data(self, component_id)` logic (lines 448-474) into `TestLabDataExtractor.load_component(self, component_id)` method
- [x] Add `self._components_cache = None` to `TestLabDataExtractor.__init__`
- [x] Ensure imports: `os`, `json`, `game.core.json_utils.load_json`, `simulation_tests.logging_config.get_logger`
- [x] Add docstrings to module and class

**Notes:** Also added helper method `_extract_component_ids()` to reduce duplication in ship extraction logic. 210 lines in new file.

---

### Task 1.2: Update screen.py to delegate to data_extractor [Simple]
**File:** `game/ui/screens/test_lab/screen.py`

- [x] Add import: `from .data_extractor import TestLabDataExtractor, get_test_data_dir`
- [x] Remove the `get_test_data_dir()` function definition from `screen.py` (lines 35-49)
- [x] In `TestLabScreen.__init__`, after `self.registry` is initialized, create `self._data_extractor = TestLabDataExtractor(self.registry)`
- [x] Replace `_extract_ships_from_scenario` method body with delegation: `return self._data_extractor.extract_ships(test_id)`
- [x] Replace `_load_component_data` method body with delegation: `return self._data_extractor.load_component(component_id)`
- [x] Update `self._components_cache` references to use `self._data_extractor._components_cache` where needed (check `_build_validation_context_from_files` at line 422)
- [x] Remove now-unused imports from screen.py if any (check `os.path` usage -- may still be needed elsewhere)
- [x] Verify `get_test_data_dir` is still accessible to other callers via the import

**Notes:** Added `_components_cache` as a property delegating to data extractor for backward compatibility. Removed self._components_cache = None from __init__. os and load_json still needed elsewhere in screen.py.

---

### Task 1.3: Update test_lab package __init__.py [Simple]
**File:** `game/ui/screens/test_lab/__init__.py`

- [x] Add `data_extractor` to exports if `__init__.py` has an `__all__` list
- [x] If `__init__.py` is empty or minimal, no changes needed

**Notes:** Added TestLabDataExtractor and get_test_data_dir to __all__ and imports.

---

### Task 1.4: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/ui/test_lab_scene/ tests/unit/test_lab/ -x`

- [x] Run targeted tests for TestLabScreen
- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify no import errors
- [x] Verify line count of `screen.py` decreased by ~160+ lines (wrapper methods add back ~10 lines)
- [x] Fix any failures discovered

**Notes:** screen.py: 2536 -> 2382 lines (154 lines saved). Updated test fixtures in test_data_paths.py to properly set up _data_extractor and patch at data_extractor.load_json instead of screen.load_json. 7524 tests pass.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to Complete
- [x] Update plan.md phase table row to Complete
- [x] Update plan.md Current State to point to next phase
