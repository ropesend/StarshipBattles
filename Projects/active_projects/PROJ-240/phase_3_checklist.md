# Phase 3: Fix Cache Safety and Mixin Issues

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-240 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add regression tests for cache safety fixes (done in Phase 1), fix change_class fallback bug, document mixin initialization order.

---

## Tasks

### Task 3.1: Regression tests for cache safety [Simple]
**File:** `tests/unit/simulation/entities/test_ship_component_manager.py` (extend)
**Tests:** `pytest tests/unit/simulation/entities/test_ship_component_manager.py -v`

- [ ] Test: append to `get_all_components()` result, call again, verify original length unchanged
- [ ] Test: add_component triggers weapons cache invalidation (next get_weapon_components_cached returns updated list)
- [ ] Test: remove_component triggers weapons cache invalidation
- [ ] Run tests -- should PASS (fixes applied in Phase 1)

**Notes:**

---

### Task 3.2: Fix change_class fallback [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py -v`

- [ ] Write test: `change_class("nonexistent_class")` raises ValidationException
- [ ] Replace empty dict fallback (line ~462) with ValidationException raise
- [ ] Run tests

**Notes:**

---

### Task 3.3: Document mixin initialization order [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py -v` (no behavior change)

- [ ] Add class-level docstring explaining MRO: PhysicsBody.__init__ via super(), ShipPhysicsMixin has no __init__
- [ ] List all delegates with their responsibilities
- [ ] Run tests

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
