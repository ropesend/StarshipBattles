# Phase 1: TestLabScreen Data Extraction [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-86 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract data loading functions from TestLabScreen into a new `data_extractor.py` module within the `test_lab/` package. This removes ~211 lines of pure data logic with zero UI dependencies.

**File:** `game/ui/screens/test_lab/screen.py`
**New File:** `game/ui/screens/test_lab/data_extractor.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ tests/unit/test_lab/ -x`

---

## Tasks

### Task 1.1: Create data_extractor.py with extracted functions [Simple]
**File:** `game/ui/screens/test_lab/data_extractor.py` (new)

- [ ] Create new file `game/ui/screens/test_lab/data_extractor.py`
- [ ] Move `get_test_data_dir()` module-level function from `screen.py` (lines 35-49) into `data_extractor.py`
- [ ] Create `class TestLabDataExtractor` with constructor accepting `registry` parameter
- [ ] Move `_extract_ships_from_scenario(self, test_id)` logic (lines 198-327) into `TestLabDataExtractor.extract_ships(self, test_id)` method
- [ ] Move `_load_component_data(self, component_id)` logic (lines 448-474) into `TestLabDataExtractor.load_component(self, component_id)` method
- [ ] Add `self._components_cache = None` to `TestLabDataExtractor.__init__`
- [ ] Ensure imports: `os`, `json`, `game.core.json_utils.load_json`, `simulation_tests.logging_config.get_logger`
- [ ] Add docstrings to module and class

**Notes:** `_extract_ships_from_scenario` uses `self.registry` and `get_test_data_dir()`. `_load_component_data` uses `self._components_cache` and `get_test_data_dir()`. Both are pure data operations with no pygame dependencies.

---

### Task 1.2: Update screen.py to delegate to data_extractor [Simple]
**File:** `game/ui/screens/test_lab/screen.py`

- [ ] Add import: `from .data_extractor import TestLabDataExtractor, get_test_data_dir`
- [ ] Remove the `get_test_data_dir()` function definition from `screen.py` (lines 35-49)
- [ ] In `TestLabScreen.__init__`, after `self.registry` is initialized, create `self._data_extractor = TestLabDataExtractor(self.registry)`
- [ ] Replace `_extract_ships_from_scenario` method body with delegation: `return self._data_extractor.extract_ships(test_id)`
- [ ] Replace `_load_component_data` method body with delegation: `return self._data_extractor.load_component(component_id)`
- [ ] Update `self._components_cache` references to use `self._data_extractor._components_cache` where needed (check `_build_validation_context_from_files` at line 422)
- [ ] Remove now-unused imports from screen.py if any (check `os.path` usage -- may still be needed elsewhere)
- [ ] Verify `get_test_data_dir` is still accessible to other callers via the import

**Notes:** Keep the thin wrapper methods `_extract_ships_from_scenario` and `_load_component_data` on `TestLabScreen` so that all internal callers continue to work without changes.

---

### Task 1.3: Update test_lab package __init__.py [Simple]
**File:** `game/ui/screens/test_lab/__init__.py`

- [ ] Add `data_extractor` to exports if `__init__.py` has an `__all__` list
- [ ] If `__init__.py` is empty or minimal, no changes needed

**Notes:**

---

### Task 1.4: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/ui/test_lab_scene/ tests/unit/test_lab/ -x`

- [ ] Run targeted tests for TestLabScreen
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify no import errors
- [ ] Verify line count of `screen.py` decreased by ~160+ lines (wrapper methods add back ~10 lines)
- [ ] Fix any failures discovered

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to Complete
- [ ] Update plan.md phase table row to Complete
- [ ] Update plan.md Current State to point to next phase
