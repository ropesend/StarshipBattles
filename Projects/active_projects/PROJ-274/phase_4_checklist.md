# Phase 4: Wire into ApplicationContext

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-274 4`

**Status:** Not Started
**Objective:** Add materializer to ApplicationContext following the 10-service pattern from PROJ-258.

---

## Tasks

### Task 4.1: Write failing tests for context accessors [Simple]
**File:** `tests/unit/test_context.py` (or wherever context tests live — verify)
**Tests:** `pytest tests/unit/test_context.py -v`

- [ ] Test: `get_default_ship_materializer()` returns an `InstanceBackedMaterializer` instance by default
- [ ] Test: `get_default_ship_materializer()` returns a singleton (same instance on repeated calls)
- [ ] Test: `set_default_ship_materializer(x)` replaces the instance; subsequent `get_*` returns `x`
- [ ] Test: `set_default_ship_materializer(None)` followed by `get_*` returns a fresh `InstanceBackedMaterializer` (lazy init)
- [ ] Run — failing

**Notes:**

### Task 4.2: Implement accessors [Simple]
**File:** `game/context.py`
**Tests:** `pytest tests/unit/test_context.py -v`

- [ ] Add module-level private var: `_default_ship_materializer: Optional[IShipMaterializer] = None`
- [ ] Add `get_default_ship_materializer() -> IShipMaterializer`:
  - Lazy-init to `InstanceBackedMaterializer()` if None
  - Return the stored instance
- [ ] Add `set_default_ship_materializer(materializer: Optional[IShipMaterializer]) -> None`
- [ ] Follow the exact pattern of existing services (e.g. `get_default_xxx` entries elsewhere in the file)
- [ ] Run tests — pass

**Notes:**

### Task 4.3: Add a resetter for tests [Simple]
**File:** `game/context.py` + `tests/conftest.py` (or relevant fixture file)
**Tests:** `pytest tests/unit/test_context.py -v`

- [ ] Ensure any session-level "reset all defaults" helper includes resetting the ship materializer
- [ ] Add a conftest fixture that resets the materializer between tests to avoid cross-test contamination
- [ ] Run full context-test suite — passes

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-274 4`
