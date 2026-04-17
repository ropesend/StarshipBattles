# Phase 2: Implement InstanceBackedMaterializer

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-274 2`
> 2. Only proceed if output shows PASSED

**Status:** Not Started
**Objective:** Implement InstanceBackedMaterializer such that all tests from Phase 1 pass.

---

## Tasks

### Task 2.1: Implement InstanceBackedMaterializer.materialize [Medium]
**File:** `game/simulation/services/ship_materializer.py`
**Tests:** `pytest tests/unit/simulation/services/test_ship_materializer.py::test_instance_backed -v`

- [ ] Implement `materialize(ship_spec, team_id, registries)`:
  - Pull `instance = ship_spec.instance_ref`
  - If None: raise `ValueError("InstanceBackedMaterializer requires ship_spec.instance_ref. ship_spec.design_id={...!r}")`
  - Call `instance.to_ship(position=ship_spec.spawn_position, team_id=team_id, registries=registries)`
  - Return the Ship
- [ ] Run tests — all InstanceBackedMaterializer tests pass

**Notes:**

### Task 2.2: Verify with real ShipInstance [Medium]
**File:** `tests/unit/simulation/services/test_ship_materializer.py`
**Tests:** `pytest tests/unit/simulation/services/test_ship_materializer.py -v`

- [ ] Add an integration-flavor test that constructs a real `ShipInstance` (from `game/strategy/data/ship_instance.py`) and passes it through the materializer
- [ ] Use an existing test fixture (check `tests/fixtures/strategy_entities.py` for `make_ship_instance` or equivalent)
- [ ] Assert returned Ship has: correct name, correct team_id, correct position, component list non-empty
- [ ] Run — passes

**Notes:**

### Task 2.3: Verify layer boundary not violated [Simple]
**File:** `game/simulation/services/ship_materializer.py`
**Tests:** Grep check

- [ ] Run `grep -n "from game.strategy" game/simulation/services/ship_materializer.py`
- [ ] Expected result: ZERO matches (no strategy imports in simulation layer)
- [ ] If any exist, refactor to use duck-typing (hasattr checks) or move the import to test code only

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-274 2`
