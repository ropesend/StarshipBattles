# Phase 4: Integration Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-219 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add integration tests verifying that formerly-buggy locations now work correctly

---

## Background

The following locations previously called `empire.remove_fleet()` WITHOUT `galaxy.unregister_fleet()`, leaving ghost fleets in the registry. With PROJ-219 changes, `remove_fleet()` now auto-unregisters.

| Location | File:Line | Bug |
|----------|-----------|-----|
| Combat destruction | `conflict_resolution_engine.py:186` | Ghost fleet after combat |
| JOIN_FLEET merge | `fleet_order_processor.py:113` | Merged fleet in registry |
| COLONIZE empty | `fleet_order_processor.py:216` | Empty fleet in registry |
| Instant merge | `fleet_order_processor.py:663` | Merged fleet in registry |
| Superweapon finalize | `superweapon_order_processor.py:103` | Consumed fleet in registry |
| Self-destruct | `superweapon_order_processor.py:613` | Consumed fleet in registry |
| Maintenance scuttle | `maintenance_engine.py:286` | Empty fleet in registry |

---

## Tasks

### Task 4.1: Create fleet lifecycle integration test file [Medium]
**File:** `tests/integration/strategy/test_fleet_registration_lifecycle.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_fleet_registration_lifecycle.py`

Create new test file with:
- [ ] Proper fixtures for game session with galaxy and empires
- [ ] Helper to verify fleet is/isn't in galaxy registry

**Notes:**

---

### Task 4.2: Test combat destruction unregisters fleet [Medium]
**File:** `tests/integration/strategy/test_fleet_registration_lifecycle.py`
**Tests:** `pytest tests/integration/strategy/test_fleet_registration_lifecycle.py::test_combat_unregisters_destroyed_fleet`

- [ ] Create `test_combat_unregisters_destroyed_fleet`:
  - Setup: Two empires with fleets at same location
  - Action: Process turn with conflict resolution
  - Assert: Destroyed fleet NOT in `galaxy.get_fleet_by_id()`
  - Assert: Surviving fleet IS in registry

**Notes:**

---

### Task 4.3: Test JOIN_FLEET merge unregisters source fleet [Medium]
**File:** `tests/integration/strategy/test_fleet_registration_lifecycle.py`
**Tests:** `pytest tests/integration/strategy/test_fleet_registration_lifecycle.py::test_join_fleet_unregisters_merged_fleet`

- [ ] Create `test_join_fleet_unregisters_merged_fleet`:
  - Setup: Two fleets at same location, source has JOIN_FLEET order
  - Action: Process fleet orders
  - Assert: Source fleet NOT in registry
  - Assert: Target fleet IS in registry with merged ships

**Notes:** This test also validates the "instant merge" code path at line 663 — both use `remove_fleet()` which now auto-unregisters.

---

### Task 4.4: Test COLONIZE with empty fleet [Medium]
**File:** `tests/integration/strategy/test_fleet_registration_lifecycle.py`
**Tests:** `pytest tests/integration/strategy/test_fleet_registration_lifecycle.py::test_colonize_empty_fleet_unregistered`

- [ ] Create `test_colonize_empty_fleet_unregistered`:
  - Setup: Fleet with only colony ship, COLONIZE order
  - Action: Process colonize order
  - Assert: Fleet NOT in registry (0 ships remaining)
  - Assert: Colony established

**Notes:**

---

### Task 4.5: Test superweapon consumed fleet [Medium]
**File:** `tests/integration/strategy/test_fleet_registration_lifecycle.py`
**Tests:** `pytest tests/integration/strategy/test_fleet_registration_lifecycle.py::test_superweapon_consumed_fleet_unregistered`

- [ ] Create `test_superweapon_consumed_fleet_unregistered`:
  - Setup: Fleet with single superweapon ship
  - Action: Process superweapon order
  - Assert: Fleet NOT in registry (consumed)
  - Assert: Superweapon effect applied

**Notes:**

---

### Task 4.6: Test save/load preserves registry [Medium]
**File:** `tests/integration/strategy/test_fleet_registration_lifecycle.py`
**Tests:** `pytest tests/integration/strategy/test_fleet_registration_lifecycle.py::test_save_load_preserves_fleet_registry`

- [ ] Create `test_save_load_preserves_fleet_registry`:
  - Setup: Game with multiple fleets
  - Action: Save, load, then create new fleet
  - Assert: All original fleets in registry
  - Assert: New fleet auto-registered

**Notes:**

---

### Task 4.7: Test maintenance scuttle unregisters empty fleet [Medium]
**File:** `tests/integration/strategy/test_fleet_registration_lifecycle.py`
**Tests:** `pytest tests/integration/strategy/test_fleet_registration_lifecycle.py::test_maintenance_scuttle_unregisters_empty_fleet`

- [ ] Create `test_maintenance_scuttle_unregisters_empty_fleet`:
  - Setup: Empire with fleet containing single ship, empire has 0 resources
  - Action: Process maintenance tick (ships scuttled due to lack of maintenance)
  - Assert: Fleet NOT in registry (0 ships remaining after scuttle)

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/integration/strategy/test_fleet_registration_lifecycle.py` - all 7 tests pass
- [ ] Run `pytest tests/ --testmon` - no regressions
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
