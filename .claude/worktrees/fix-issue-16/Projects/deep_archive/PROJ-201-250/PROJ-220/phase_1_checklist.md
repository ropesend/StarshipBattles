# Phase 1: Foundation — FilterState Enum & FilterStateManager

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-220 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the shared filter infrastructure: FilterState enum, FilterStateManager base class, and unit tests. No UI changes yet.

---

## Tasks

### Task 1.1: Create `game/ui/filters/` package with FilterState enum [Simple]
**File:** `game/ui/filters/filter_state.py` (new)
**Tests:** `pytest tests/unit/ui/filters/test_filter_state.py`

- [x] Create directory `game/ui/filters/`
- [x] Create `game/ui/filters/filter_state.py`:
  - `FilterState(Enum)` with values: `YES = "yes"`, `NO = "no"`, `IGNORE = "ignore"`
  - Class should be importable without pygame
- [x] Create `game/ui/filters/__init__.py`:
  ```python
  from game.ui.filters.filter_state import FilterState
  from game.ui.filters.filter_state_manager import FilterStateManager
  __all__ = ["FilterState", "FilterStateManager"]
  ```
  (Note: FilterStateManager import will be added after Task 1.2)
- [x] Create test directory `tests/unit/ui/filters/`
- [x] Create `tests/unit/ui/filters/__init__.py`
- [x] Create `tests/unit/ui/filters/test_filter_state.py`:
  - Test enum values: `FilterState.YES.value == "yes"`, etc.
  - Test enum iteration: `list(FilterState)` has 3 members
  - Test enum identity: `FilterState("yes") == FilterState.YES`
  - Test string serialization round-trip
- [x] Verify: `pytest tests/unit/ui/filters/test_filter_state.py` passes

**Notes:** 9 tests, all passing. FilterState enum created with string values for serialization. `__init__.py` currently exports only FilterState (FilterStateManager added in Task 1.2).

---

### Task 1.2: Create FilterStateManager base class [Medium]
**File:** `game/ui/filters/filter_state_manager.py` (new)
**Tests:** `pytest tests/unit/ui/filters/test_filter_state_manager.py`

- [x] Create `game/ui/filters/filter_state_manager.py`:
  - `FilterStateManager` class with:
    - `__init__(self, filter_definitions: Dict[str, FilterState])` — accepts initial filter states
    - `_filter_states: Dict[str, FilterState]` — internal state storage
    - `get_state(attribute: str) -> FilterState` — get current state for one filter
    - `set_state(attribute: str, state: FilterState) -> None` — set state for one filter
    - `get_all_states() -> Dict[str, FilterState]` — snapshot of all filter states
    - `reset_all() -> None` — reset all filters to IGNORE
    - `has_active_filters() -> bool` — True if any filter is not IGNORE
    - `should_include(attribute: str, item_value: bool) -> bool` — tri-state inclusion check:
      - `IGNORE` → return `True` (always include)
      - `YES` → return `item_value` (include only if True)
      - `NO` → return `not item_value` (include only if False)
  - No pygame imports. Pure Python.
- [x] Update `game/ui/filters/__init__.py` to export `FilterStateManager`
- [x] Create `tests/unit/ui/filters/test_filter_state_manager.py`:
  - Test initialization with default states
  - Test `get_state()` / `set_state()` round-trip
  - Test `get_all_states()` returns copy (not reference)
  - Test `reset_all()` sets all to IGNORE
  - Test `has_active_filters()` with all IGNORE vs some active
  - Test `should_include()` truth table:
    - `IGNORE, True` → True
    - `IGNORE, False` → True
    - `YES, True` → True
    - `YES, False` → False
    - `NO, True` → False
    - `NO, False` → True
  - Test `set_state()` with invalid attribute raises KeyError
- [x] Verify: `pytest tests/unit/ui/filters/` passes

**Notes:** 20 tests for FilterStateManager, all passing. Pure Python, no pygame deps. `get_all_states()` returns a copy. `set_state()` validates attribute exists.

---

### Task 1.3: Verify no test regressions [Simple]
**Tests:** `pytest tests/ --testmon`

- [x] Run incremental test suite: `pytest tests/ --testmon`
- [x] Verify no existing tests broken by new package creation
- [x] Verify new tests are discovered and pass

**Notes:** 835 passed (testmon subset), 0 failures. All 29 new filter tests discovered and passing.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `game/ui/filters/` package exists with `FilterState` and `FilterStateManager`
- [x] All new tests pass
- [x] No existing tests broken
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
