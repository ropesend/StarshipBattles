# Phase 3: Test Rename

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-298 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace every old-name reference in `tests/` with the canonical new name. After this phase, NO source-tree references to old names remain except the alias declarations themselves.

**Prerequisites:** Phase 2 complete; production source uses only new names.

---

## Tasks

### Task 3.1: Strategy unit tests [Simple]
**File:** Files under `tests/unit/strategy/` (per `findings/rename_plan.md`)
**Tests:** `pytest tests/unit/strategy/`

- [ ] For each file in `findings/rename_plan.md` under `tests/unit/strategy/`: apply word-boundary rename
- [ ] Specific known hits (verify in inventory):
  - [ ] `tests/unit/strategy/engine/test_planet_action_engine.py`
  - [ ] `tests/unit/strategy/engine/test_planet_command_handlers.py`
  - [ ] `tests/unit/strategy/facade/test_facade_dispatch.py`
  - [ ] `tests/unit/strategy/test_fleet_orders_logic.py` (may use `FleetOrder` symbol — distinct from filename)
- [ ] Run targeted tests
- [ ] **Verification:** `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b" tests/unit/strategy/` returns zero hits

**Notes:**

---

### Task 3.2: UI unit tests [Simple]
**File:** Files under `tests/unit/ui/screens/`
**Tests:** `pytest tests/unit/ui/screens/`

- [ ] Specific known hits (verify in inventory):
  - [ ] `tests/unit/ui/screens/test_strategy_ui_menu.py`
  - [ ] `tests/unit/ui/screens/test_sub_window_hotkeys.py`
  - [ ] `tests/unit/ui/screens/test_strategy_window_manager.py`
  - [ ] `tests/unit/ui/screens/test_strategy_event_router.py`
  - [ ] `tests/unit/ui/screens/test_fleet_orders_refresh.py`
  - [ ] `tests/unit/ui/screens/test_event_log_window.py`
  - [ ] `tests/unit/ui/screens/test_click_gate_integration.py`
- [ ] Pay special attention to imports of `FleetOrdersWindow` — replace with `OrdersWindow` from `game.ui.screens.orders_window`
- [ ] Run targeted tests
- [ ] **Verification:** `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bFleetOrdersWindow\b" tests/unit/ui/` returns zero hits

**Notes:**

---

### Task 3.3: Integration tests [Simple]
**File:** Files under `tests/integration/`
**Tests:** `pytest tests/integration/`

- [ ] Specific known hits (verify in inventory):
  - [ ] `tests/integration/ui/test_fleet_build_button.py`
- [ ] Rename per inventory
- [ ] Run integration tests
- [ ] **Verification:** `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bFleetOrdersWindow\b" tests/integration/` returns zero hits

**Notes:**

---

### Task 3.4: Test fixtures [Simple]
**File:** `tests/fixtures/`, `tests/conftest.py`, any `conftest.py` under `tests/`
**Tests:** `pytest tests/`

- [ ] Sweep all conftest/fixture files for old names
- [ ] Rename per inventory
- [ ] Run a broad subset to check fixture wiring still works
- [ ] **Verification:** `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bFleetOrdersWindow\b" tests/fixtures/ tests/conftest.py` returns zero hits

**Notes:**

---

### Task 3.5: Final sweep across tests/ [Simple]
**File:** All of `tests/`
**Tests:** `python Tools/test_sharded/test_sharded.py` (full sharded suite)

- [ ] Final grep: `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bClearFleetOrdersCommand\b\|\bDeleteFleetOrderCommand\b\|\bReorderFleetOrderCommand\b\|\bFleetOrdersWindow\b" tests/`
- [ ] **Expected:** zero hits
- [ ] **Run full sharded suite — must remain at 15112+ passing.** Tests still rely on aliases existing (they are still declared in source); the suite confirms the renames are consistent
- [ ] If any hits remain, address them before phase completion

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bClearFleetOrdersCommand\b\|\bDeleteFleetOrderCommand\b\|\bReorderFleetOrderCommand\b\|\bFleetOrdersWindow\b" game/ tests/` returns ONLY the 5 alias declarations + the shim module
- [ ] Full sharded suite at 15112+ passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 4: Delete Aliases & Shim Module)
