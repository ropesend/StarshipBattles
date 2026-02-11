# Phase 1: Empire Resource Pool Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-75 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add global resource tracking to Empire class

---

## Tasks

### Task 1.1: Write TDD tests for Empire resources [Simple]
**File:** `tests/unit/strategy/data/test_empire_resources.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_empire_resources.py -v`

- [x] Create test file with TestEmpireResources class
- [x] Test: resource_pool initializes as empty dict
- [x] Test: max_storage initializes as empty dict
- [x] Test: add_resources() basic - adds to pool
- [x] Test: add_resources() - respects max_storage, returns overflow
- [x] Test: add_resources() - no max_storage means unlimited
- [x] Test: consume_resources() success - deducts and returns True
- [x] Test: consume_resources() failure - insufficient returns False
- [x] Test: consume_resources() - partial consumption not allowed
- [x] Test: has_resources() with single resource type
- [x] Test: has_resources() with multiple resource types
- [x] Test: has_resources() returns False if any insufficient
- [x] Test: get_resource() returns 0 for missing type
- [x] Test: to_dict() includes resource_pool and max_storage
- [x] Test: from_dict() restores resource_pool and max_storage
- [x] Test: from_dict() handles missing fields (old save compatibility)

**Notes:** 26 tests written across 6 test classes. All pass.

---

### Task 1.2: Add resource_pool field to Empire [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_resources.py -v`

- [x] Add field: `resource_pool: Dict[str, float] = field(default_factory=dict)`
- [x] Add field: `max_storage: Dict[str, float] = field(default_factory=dict)`
- [x] Implement `add_resources(resource_type: str, amount: float) -> float`
- [x] Implement `consume_resources(resource_type: str, amount: float) -> bool`
- [x] Implement `has_resources(costs: Dict[str, float]) -> bool`
- [x] Implement `get_resource(resource_type: str) -> float`

**Notes:** All 4 methods implemented with docstrings, following existing patterns.

---

### Task 1.3: Update Empire serialization [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire_resources.py tests/integration/strategy/test_empire.py -v`

- [x] Update `to_dict()` to include new fields
- [x] Update `from_dict()` with safe defaults
- [x] Verify existing Empire tests still pass

**Notes:** resource_pool and max_storage added to both to_dict() and from_dict() with safe {} defaults for old saves.

---

### Task 1.4: Run full test suite [Simple]
**Tests:** `pytest tests/ --testmon`

- [x] All tests pass
- [x] No serialization regressions
- [x] Document any issues found

**Notes:** 6846 passed (full suite, -n 12). Only pre-existing test_protocols.py mock spec failure excluded.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
