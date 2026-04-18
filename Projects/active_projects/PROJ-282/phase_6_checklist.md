# Phase 6: Extract BattleSetupController (mutation + launch)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract mutation operations (fleet/TF/squadron CRUD, complex toggles, side add/remove, save/load, battle launch) from `FleetBattleSetupScreen` into a `BattleSetupController` class. The Controller is the only code that mutates `BattleSetupState`.

**Prerequisite:** Phase 5 complete — InputHandler exists and calls Controller methods. Phase 6 replaces the Controller stub with the real implementation.

---

## Tasks

### Task 6.1: Inventory mutation operations to extract [Simple]
**File:** `.agent_reports/PROJ-282-audit/controller_methods.md` (NEW or extend existing)
**Tests:** N/A (research)

Enumerate every mutation on `BattleSetupState` currently performed by the screen:
- [ ] Fleet CRUD: `create_fleet(side_id)`, `duplicate_fleet(side_id, fleet)`, `delete_fleet(side_id, fleet)`, `rename_fleet(fleet, name)`
- [ ] Ship CRUD: `add_ship_to_fleet(fleet, design)`, `remove_ship(fleet, ship)`, `move_ship(fleet, ship, target_tf)`
- [ ] TaskForce CRUD: `create_task_force(fleet)`, `duplicate_task_force(tf)` — calls into FleetHierarchyEditor (Phase 7)
- [ ] Squadron CRUD: `create_squadron(tf)`, `duplicate_squadron(sq)` — calls into FleetHierarchyEditor
- [ ] Complex toggles: `toggle_system_complex(side_id, complex_id)`, `toggle_sector_complex(side_id, complex_id)`
- [ ] Side management: `add_side()`, `remove_side(side_id)`
- [ ] Save/load: `save_setup(path)`, `load_setup(path)`
- [ ] Battle launch: `launch_battle()` — compiles spec via `build_manual_battle_spec`, fires callback

**Notes:**

### Task 6.2: Write tests for BattleSetupController [Complex]
**File:** `tests/unit/ui/screens/battle_setup/test_controller.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_controller.py`

- [ ] One test per mutation method (use `BattleSetupState` directly, no UI mocks needed)
- [ ] Test: `launch_battle()` invokes the registered callback with a valid `BattleSpec`
- [ ] Test: save/load round-trips correctly
- [ ] Test: `remove_side` preserves min-sides constraint (MIN_SIDES=2)
- [ ] Test: `add_side` preserves max-sides constraint (MAX_SIDES=8, PROJ-275)

**Notes:** Keep tests focused on State mutation — avoid UI-layer assertions.

### Task 6.3: Implement `BattleSetupController` [Complex]
**File:** `game/ui/screens/battle_setup/controller.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_controller.py`

- [ ] Constructor takes `state: BattleSetupState`, `launch_callback: Callable[[BattleSpec], None]`
- [ ] Implement every method inventoried in Task 6.1
- [ ] For TF/SQ CRUD: defer to `FleetHierarchyEditor` (out of scope here — Phase 7 creates it; Phase 6 can stub inline)
- [ ] `launch_battle()` calls `build_manual_battle_spec(state, registries)` then `self.launch_callback(spec)`
- [ ] Save/load delegates to existing `setup_data_io.py` if it exists; otherwise implement inline

**Notes:**

### Task 6.4: Wire Controller into InputHandler + Screen [Medium]
**Files:** `game/ui/screens/battle_setup/input_handler.py`, `game/ui/screens/battle_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [ ] Replace the Controller stub from Phase 5 with the real `BattleSetupController`
- [ ] Screen constructs the Controller in `__init__` with state + launch callback
- [ ] InputHandler receives the real Controller
- [ ] Delete all mutation logic from the screen itself (lines 824-1084)
- [ ] Screen line count drops by ~260 lines

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `game/ui/screens/battle_setup/controller.py` exists with full mutation logic
- [ ] Screen no longer contains fleet/TF/squadron/toggle/launch/save mutation code
- [ ] `wc -l game/ui/screens/battle_setup_screen.py` shows another ~260 line drop
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7 (FleetHierarchyEditor)
