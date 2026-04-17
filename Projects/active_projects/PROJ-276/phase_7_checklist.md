# Phase 7: Update Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-276 7`

**Status:** Not Started
**Objective:** All 10 test files × ~29 occurrences migrated. Some are renames; some assert lossy behavior and need rewriting.

---

## Tasks

### Task 7.1: Audit test classifications [Simple]
**File:** `findings/component_damage_test_audit.md` (created Phase 1)
**Tests:** N/A

- [ ] Re-read Phase 1's test audit
- [ ] For each of the 10 files: classify as SIMPLE RENAME (just uses the attribute name) or LOSSY-ASSERTION (asserts the flattened behavior that's now invalid)
- [ ] Lossy-assertion tests need REWRITE to assert per-instance behavior

**Notes:**

### Task 7.2: Simple rename migrations [Medium]
**File:** Multiple (per audit)
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] For each SIMPLE RENAME test: change `instance.component_damage[key] = value` to `instance.components[component_state_key(...)] = ComponentState(current_hp=value, ...)`
- [ ] For each READ: change `instance.component_damage.get(key)` to `instance.components.get(component_state_key(...)).current_hp`
- [ ] Run each file's tests after migration

**Notes:**

### Task 7.3: Lossy-assertion rewrites [Complex]
**File:** Multiple
**Tests:** `pytest tests/unit/strategy/ -n 12`

- [ ] For each LOSSY-ASSERTION test: understand what it was checking
- [ ] Rewrite to assert per-instance behavior (each instance has its own HP)
- [ ] Add a "new-behavior" test: multi-instance ship with partial damage only affects the targeted instance
- [ ] Run — all pass

**Notes:**

### Task 7.4: Serializer tests [Medium]
**File:** `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_ship_instance_serializer.py -v`

- [ ] 5 occurrences — likely all reference the old field
- [ ] Each must be rewritten to test `components` serialization
- [ ] Run — all pass

**Notes:**

### Task 7.5: Roundtrip integration [Medium]
**File:** `tests/integration/save_load/test_roundtrip_ships.py`
**Tests:** `pytest tests/integration/save_load/test_roundtrip_ships.py -v`

- [ ] 3 occurrences — update to round-trip `components` dict
- [ ] Add multi-instance roundtrip test
- [ ] Run — all pass

**Notes:**

### Task 7.6: Full suite final [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] ZERO failures across the whole suite
- [ ] Grep `grep -rn "component_damage" tests/` returns ZERO results
- [ ] Baseline maintained or expanded

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-276 7`
