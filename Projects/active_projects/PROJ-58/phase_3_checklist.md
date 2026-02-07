# Phase 3: Formation Delegation Removal [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-56 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update AI adapter to use `ship.formation.*` directly, then remove 6 delegation properties from Ship.

---

## Tasks

### Task 3.1: Update ShipControllableAdapter to Use ship.formation Directly [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/ -x`

The adapter currently accesses `ship.formation_master`, `ship.formation_offset`, etc. (the backward compat properties). Update to use `ship.formation.master`, `ship.formation.offset`, etc.

- [ ] Find all formation property accesses in the adapter (~lines 423-443)
- [ ] Change `self._ship.formation_master` → `self._ship.formation.master`
- [ ] Change `self._ship.formation_offset` → `self._ship.formation.offset`
- [ ] Change `self._ship.formation_rotation_mode` → `self._ship.formation.rotation_mode`
- [ ] Change `self._ship.formation_members` → `self._ship.formation.members`
- [ ] Change `self._ship.in_formation` → `self._ship.formation.active`
- [ ] Run tests: `pytest tests/unit/ai/ -x`
**Notes:** The ShipFormation object has `.master`, `.offset`, `.rotation_mode`, `.members`, `.active` as direct attributes.

### Task 3.2: Verify No Other Callers Use Formation Delegation Properties [Simple]
**Tests:** Research only, no changes
- [ ] Search codebase for `\.formation_master`, `\.formation_offset`, `\.formation_rotation_mode`, `\.formation_members`, `\.in_formation` (excluding ship.py definition)
- [ ] If any callers found besides the adapter, update them to use `ship.formation.*`
- [ ] Document any unexpected callers in Notes
**Notes:**

### Task 3.3: Remove Formation Delegation Properties from Ship [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/ -x`
- [ ] Remove `formation_master` property and setter (~lines 216-226)
- [ ] Remove `formation_offset` property and setter (~lines 228-238)
- [ ] Remove `formation_rotation_mode` property and setter (~lines 240-248)
- [ ] Remove `formation_members` property and setter (~lines 250-258)
- [ ] Remove `in_formation` property and setter (~lines 260-268)
- [ ] Remove section comment "Formation Delegation Properties (backward compatibility)" (~line 215)
- [ ] Run full test suite: `pytest tests/ -x`
**Notes:** Only do this AFTER Tasks 3.1 and 3.2 are complete.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
- [ ] No remaining `formation_master`, `formation_offset`, etc. properties on Ship
- [ ] AI adapter accesses `ship.formation.*` directly
