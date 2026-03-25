# Phase 4: DI & Reference Integrity

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-223 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Validate registry injection and cross-object reference resolution survive save/load.

---

## Tasks

### Task 4.1: Registry injection verification [Medium]
**File:** `tests/integration/save_load/test_registry_injection.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_registry_injection.py`

- [ ] Test all ShipInstance objects have `_registries` set after GameSession.from_dict()
- [ ] Test `get_calculated_stats()` works after load
- [ ] Test Fleet component_registry is set
- [ ] Test deliberate omission of registries → clear error
- [ ] Test GameSession._registries and TurnEngine receive registries

**Notes:** BUG-107 regression guard.

### Task 4.2: Colony reference integrity [Medium]
**File:** `tests/integration/save_load/test_reference_integrity.py` (NEW)
**Tests:** `pytest tests/integration/save_load/test_reference_integrity.py`

- [ ] Test empire.colonies are actual Planet objects after load
- [ ] Test colony planet.owner_id matches empire.id
- [ ] Test colonies exist in galaxy.get_planet_by_id()
- [ ] Test colony count and IDs match

**Notes:**

### Task 4.3: Fleet order reference resolution [Medium]
**File:** `tests/integration/save_load/test_reference_integrity.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_reference_integrity.py`

- [ ] Test MOVE_TO_FLEET and JOIN_FLEET targets resolved to Fleet objects
- [ ] Test COLONIZE and IMPLODE_PLANET targets resolved to Planet objects
- [ ] Test unresolvable references → order removed with warning

**Notes:**

### Task 4.4: Pursuer tracker rebuild [Simple]
**File:** `tests/integration/save_load/test_reference_integrity.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_reference_integrity.py`

- [ ] Test pursuer_tracker re-registered after load with MOVE_TO_FLEET/JOIN_FLEET orders
- [ ] Test pursuer count matches

**Notes:**

### Task 4.5: Fleet registration with galaxy [Simple]
**File:** `tests/integration/save_load/test_reference_integrity.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_reference_integrity.py`

- [ ] Test all fleets registered with galaxy after load
- [ ] Test fleet count matches

**Notes:**

### Task 4.6: Galaxy back-references [Simple]
**File:** `tests/integration/save_load/test_reference_integrity.py` (extend)
**Tests:** `pytest tests/integration/save_load/test_reference_integrity.py`

- [ ] Test each empire has galaxy reference set after load

**Notes:**

### Task 4.7: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All tests pass, no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 12` — all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
