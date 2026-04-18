# Phase 7: Extract FleetHierarchyEditor (kills TF/SQ clone duplication)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract fleet/TaskForce/Squadron CRUD (especially the duplicated ship-cloning logic in `_duplicate_task_force` lines 854-912 and `_duplicate_squadron` lines 925-958) into a single `FleetHierarchyEditor` helper. Stateless — operates on a `Fleet` argument.

**Prerequisite:** Phase 6 complete — Controller exists and currently stubs-in the TF/SQ operations inline. Phase 7 centralizes them.

---

## Tasks

### Task 7.1: Audit TF/SQ duplication [Simple]
**File:** `.agent_reports/PROJ-282-audit/tf_sq_dup.md` (NEW or extend)
**Tests:** N/A (research)

- [ ] Read `_duplicate_task_force` (lines 854-912 in the original screen)
- [ ] Read `_duplicate_squadron` (lines 925-958)
- [ ] Identify duplicated ship-cloning logic — what's literally copy-pasted vs. parameterized
- [ ] Design the extraction: what's the shared `_clone_ships(ships: List[Ship]) -> List[Ship]` helper look like?

**Notes:**

### Task 7.2: Write tests for FleetHierarchyEditor [Medium]
**File:** `tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py`

- [ ] Test: `duplicate_task_force(fleet, tf)` returns a new TaskForce with cloned ships, appended to the fleet
- [ ] Test: `duplicate_squadron(tf, sq)` returns a new Squadron with cloned ships, appended to the task force
- [ ] Test: ship clones are deep-copy-equivalent (same design_id, same theme) but distinct instances
- [ ] Test: `create_task_force(fleet, name)` appends an empty TF
- [ ] Test: `create_squadron(tf, name)` appends an empty SQ
- [ ] Test: `delete_task_force(fleet, tf)` removes the TF; `delete_squadron(tf, sq)` removes the SQ
- [ ] Test: editor is stateless — no instance attrs besides dependencies

**Notes:**

### Task 7.3: Implement `FleetHierarchyEditor` [Medium]
**File:** `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py`

- [ ] Class with stateless methods (or module-level functions — decide during implementation)
- [ ] Centralize the ship-cloning helper so `duplicate_task_force` and `duplicate_squadron` both call it
- [ ] Operate on real `Fleet` / `TaskForce` / `Squadron` domain types — no UI layer dependencies
- [ ] All Task 7.2 tests pass

**Notes:**

### Task 7.4: Rewire Controller to use FleetHierarchyEditor [Simple]
**File:** `game/ui/screens/battle_setup/controller.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_controller.py`

- [ ] Replace Controller's stub TF/SQ methods with calls into `FleetHierarchyEditor`
- [ ] Delete any remaining duplicated clone logic in the controller
- [ ] Existing Controller tests still pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` exists
- [ ] Ship-cloning logic lives in ONE place (FleetHierarchyEditor)
- [ ] Controller delegates TF/SQ operations to the editor
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 8 (slim screen)
