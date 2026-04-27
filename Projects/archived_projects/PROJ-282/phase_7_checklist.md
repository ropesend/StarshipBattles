# Phase 7: Extract FleetHierarchyEditor (kills TF/SQ clone duplication)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract fleet/TaskForce/Squadron CRUD (especially the duplicated ship-cloning logic in `_duplicate_task_force` lines 854-912 and `_duplicate_squadron` lines 925-958) into a single `FleetHierarchyEditor` helper. Stateless — operates on a `Fleet` argument.

**Prerequisite:** Phase 6 complete — Controller exists and currently stubs-in the TF/SQ operations inline. Phase 7 centralizes them.

---

## Tasks

### Task 7.1: Audit TF/SQ duplication [Simple]
**Tests:** N/A (research)

- [x] Phase 1 audit already documented the duplication (see [delegate_map.md](../../../.agent_reports/PROJ-282-audit/delegate_map.md) "Flagged mixed-concerns" item 4 + migration_plan.md Phase 7 section)
- [x] `_duplicate_task_force` (58 LOC) and `_duplicate_squadron` (33 LOC) both instantiate `ShipInstance.create(design_data=..., owner_id=..., name=..., registries=...)` inline — identical 6-line block
- [x] Phase 6 already centralized the inline instantiation into `BattleSetupController._clone_ship` (staticmethod) — Phase 7 pulls that helper + the duplicate-then-reparent flow into the editor
- [x] Shared helper: `FleetHierarchyEditor._clone_ship(ship, registries) -> ShipInstance`

**Notes:** No new report needed — the Phase 1 audit + Phase 6 interim dedup already described the shape. Phase 7 finishes the extraction.

### Task 7.2: Write tests for FleetHierarchyEditor [Medium]
**File:** `tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py`

- [x] Test: `duplicate_task_force(fleet, tf)` returns a new TaskForce with cloned ships, appended to the fleet + fleet master ship list
- [x] Test: `duplicate_squadron(fleet, tf, sq)` returns a new Squadron with cloned ships, appended to TF + fleet master list
- [x] Test: duplicate preserves `policy` (targeting/movement/retreat) + `battle_role` + `spatial_behavior` + `spatial_behavior_params` (dict copy)
- [x] Test: `create_task_force(fleet, name)` appends an empty TF; default name is `f"Task Force {N}"`
- [x] Test: `create_squadron(tf, name)` appends an empty SQ; default name is `f"Squadron {N}"`
- [x] Test: `delete_task_force(fleet, tf)` removes the TF and all its ships from `fleet.ships`; `delete_squadron(fleet, tf, sq)` likewise removes SQ + its ships
- [x] Test: editor has no instance state (`__dict__ == {}` on a fresh instance) — all methods are `@staticmethod`

**Notes:** 11 tests in new file. Uses `pytest.MonkeyPatch` to stub `ShipInstance.create` since full ship materialization requires registries. Tests started red (11 fail), green after Task 7.3.

### Task 7.3: Implement `FleetHierarchyEditor` [Medium]
**File:** `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py`

- [x] Class with all `@staticmethod` methods — no instance state. Shape chosen to match the rest of the `battle_setup` package (each delegate is a class with a focused responsibility).
- [x] Centralized `_clone_ship(ship, registries)` — called from both `duplicate_task_force` and `duplicate_squadron`. Kills the Phase 6 inline dedup's code-path divergence potential.
- [x] Operates on real `Fleet` / `TaskForce` / `Squadron` types imported from `game.strategy.data.*`. No UI layer dependencies (the editor could be reused by future screens editing fleet hierarchies — e.g. fleet-orders window).
- [x] Module also owns `_get_registries()` (private helper) — pulled from the controller's copy for self-containment.
- [x] All 11 Task 7.2 tests pass.

**Notes:** ~180 LOC total. `_get_registries` is duplicated between controller.py and fleet_hierarchy_editor.py for now — Phase 8 can consolidate into a shared helper in `battle_setup/__init__.py` or a tiny `registries.py`.

### Task 7.4: Rewire Controller to use FleetHierarchyEditor [Simple]
**File:** `game/ui/screens/battle_setup/controller.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_controller.py`

- [x] Replaced the controller's 6 TF/SQ methods with one-line delegations to `FleetHierarchyEditor.*`:
  - `add_task_force` → `FleetHierarchyEditor.create_task_force(fleet)`
  - `add_squadron` → `FleetHierarchyEditor.create_squadron(tf)` (with auto-TF-create if needed)
  - `duplicate_task_force(tf_index)` → `FleetHierarchyEditor.duplicate_task_force(fleet, tf)`
  - `delete_task_force(tf_index)` → `FleetHierarchyEditor.delete_task_force(fleet, tf)`
  - `duplicate_squadron(tf_index, sq_index)` → `FleetHierarchyEditor.duplicate_squadron(fleet, tf, sq)`
  - `delete_squadron(tf_index, sq_index)` → `FleetHierarchyEditor.delete_squadron(fleet, tf, sq)`
- [x] Deleted the inline clone logic (~130 LOC of TF/SQ duplication bodies) and the `_clone_ship` staticmethod — now in editor
- [x] Cleaned up unused imports from controller: `TaskForce`, `Squadron`, `CombatPolicy`
- [x] Existing 31 controller tests still pass; added FleetHierarchyEditor 11 tests; 3545 UI regression tests green

**Notes:** Controller went 458 → ~400 LOC (−58). The saved lines moved to the editor, but the editor adds ~60 LOC of its own (docstring + `_get_registries` helper); net package lines roughly flat, but the duplication is GONE — ship-cloning now lives in exactly one place.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` exists
- [x] Ship-cloning logic lives in ONE place (`FleetHierarchyEditor._clone_ship`)
- [x] Controller delegates TF/SQ operations to the editor
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 8 (slim screen)
