# Phase 2: Production Rename

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-298 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace every old-name reference in `game/` (production source) with the canonical new name. Aliases remain intact so tests still pass — they will be deleted in Phase 4 once tests are migrated.

**Prerequisites:** Phase 1 inventory complete (`findings/usage_inventory.md` and `findings/rename_plan.md` populated).

---

## Tasks

Work through `findings/rename_plan.md`, file by file. For each file:
1. Open the file
2. Replace each old-name symbol with its new name (use IDE find-and-replace with whole-word matching, OR `sed -i` with `\b` boundaries)
3. Run the file's targeted tests
4. Check the file off below

### Task 2.1: Strategy data layer renames [Simple]
**File:** Files under `game/strategy/data/` (per `findings/rename_plan.md`)
**Tests:** `pytest tests/unit/strategy/data/`

- [ ] For each file in `findings/rename_plan.md` under `game/strategy/data/`: apply word-boundary rename for the symbols listed
- [ ] Run targeted tests
- [ ] **Verification:** `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b" game/strategy/data/` — all remaining hits are the alias declarations themselves (lines 170-171 of `order_types.py`)

**Notes:**

---

### Task 2.2: Strategy engine renames [Simple]
**File:** Files under `game/strategy/engine/` (per `findings/rename_plan.md`)
**Tests:** `pytest tests/unit/strategy/engine/`

- [ ] For each file in `findings/rename_plan.md` under `game/strategy/engine/`: rename
- [ ] Specific known hits (verify in inventory):
  - [ ] `command_handlers.py` (PlanetOrder usages)
  - [ ] `planet_action_engine.py`
  - [ ] `planet_command_handlers.py`
  - [ ] `commands.py` — alias declarations remain (deleted in Phase 4)
- [ ] Run targeted tests
- [ ] **Verification:** `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bClearFleetOrdersCommand\b\|\bDeleteFleetOrderCommand\b\|\bReorderFleetOrderCommand\b" game/strategy/engine/` — only the alias declarations themselves remain

**Notes:**

---

### Task 2.3: Strategy facade + validation renames [Simple]
**File:** `game/strategy/facade/strategy_session_facade.py`, `game/strategy/validation/__init__.py`, `game/strategy/validation/planet_order_validator.py`
**Tests:** `pytest tests/unit/strategy/facade/ tests/unit/strategy/validation/`

- [ ] Rename per inventory
- [ ] Run targeted tests
- [ ] **Verification:** grep returns zero non-alias hits in these files

**Notes:**

---

### Task 2.4: UI screens renames [Medium]
**File:** Files under `game/ui/screens/` (per `findings/rename_plan.md`)
**Tests:** `pytest tests/unit/ui/screens/`

UI is the largest production surface. Rename systematically.

- [ ] Specific known hits (verify in inventory):
  - [ ] `strategy_window_manager.py`
  - [ ] `strategy_event_router.py`
  - [ ] `strategy_screen.py`
  - [ ] `strategy_fleet_command_router.py`
  - [ ] `planet_abilities_window.py`
  - [ ] `orders_window.py` (may itself reference old names internally)
- [ ] Run targeted tests
- [ ] **Verification:** `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bFleetOrdersWindow\b" game/ui/` — only the `fleet_orders_window.py` shim remains (deleted in Phase 4)

**Notes:**

---

### Task 2.5: Sweep for any missed production hits [Simple]
**File:** All of `game/`
**Tests:** `pytest tests/unit/`

- [ ] Final sweep: `grep -rn "\bFleetOrder\b\|\bPlanetOrder\b\|\bClearFleetOrdersCommand\b\|\bDeleteFleetOrderCommand\b\|\bReorderFleetOrderCommand\b\|\bFleetOrdersWindow\b" game/`
- [ ] **Expected remaining hits ONLY:**
  - 5 alias declaration sites in `order_types.py` and `commands.py` (deleted in Phase 4)
  - The `fleet_orders_window.py` shim file (deleted in Phase 4)
  - Any string literals/comments that explicitly reference the old name as historical context (delete the comment if it's "PROJ-238 backward compat" boilerplate)
- [ ] If any other hits exist, file a Notes entry below describing them and decide rename vs keep
- [ ] Run `pytest tests/unit/` to catch any production-only regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `grep` sweep above produces only the expected residual hits
- [ ] `pytest tests/unit/` passes (tests still work because aliases are still in place)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3: Test Rename)
