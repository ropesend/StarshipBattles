# Phase 4: Slim Down Ship.__init__

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-240 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Group remaining __init__ properties into logical sections, remove dead code, verify line count targets.

---

## Tasks

### Task 4.1: Organize remaining __init__ properties [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `python scripts/test_sharded.py`

- [ ] Group into sections: Identity, Registries, Layers, Stats, Resources, Combat Stats, Budget, AI, Formation/Physics, Delegates
- [ ] Remove any properties now owned by delegates (cache vars, combat state)
- [ ] Verify no duplicate initialization between Ship and delegates
- [ ] Run full test suite

**Notes:**

---

### Task 4.2: Verify line count targets [Simple]
- [ ] Ship.__init__ should be ~80 lines (down from ~160)
- [ ] Ship total should be ~300 lines (down from 850)
- [ ] ShipComponentManager should be ~250 lines
- [ ] ShipCombatManager should be ~150 lines
- [ ] Document final line counts in plan.md Current State

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
