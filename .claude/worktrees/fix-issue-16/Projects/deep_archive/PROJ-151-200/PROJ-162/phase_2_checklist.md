# Phase 2: Refactor Dialogs to Use Service

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-162 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Refactor CargoQuickDialog and TransferDialog to delegate business logic to CargoTransferService. Fix the 5 failing dialog tests.

---

## Tasks

### Task 2.1: Refactor CargoQuickDialog to use service [Medium]
**File:** `game/ui/screens/cargo_quick_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog.py tests/unit/ui/screens/test_cargo_quick_dialog_issuance.py tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py -v`

- [x] Add import: `from game.strategy.services.cargo_transfer_service import CargoTransferService`
- [x] Refactor `_populate_unload_items()`:
  - Replace inline colony resolution with `CargoTransferService.resolve_colonies(self.facade, self.hex_coord, self.fleet)`
  - Replace inline fleet cargo extraction with `CargoTransferService.get_unload_items(self.facade, self.fleet.id, colonies)`
  - Keep UI row creation (`_add_cargo_row()`) — that stays in the dialog
- [x] Refactor `_populate_load_items()`:
  - Replace inline colony resolution with `CargoTransferService.resolve_colonies(self.facade, self.hex_coord, self.fleet)`
  - Replace inline population extraction with `CargoTransferService.get_load_items(self.facade, colonies)`
  - Keep UI row creation (`_add_cargo_row()`) — that stays in the dialog
  - **Removed all 18 DIAG log_info statements**
  - **Removed dead diagnostic code**: fleet cargo capacity/current calls and planet iteration loop
- [x] Refactor `_issue_orders()`:
  - Replace inline command assembly with `CargoTransferService.build_transfer_command(...)` for each item
  - **Removed all DIAG log_info statements**
  - Kept the 3 legitimate operational logs
- [x] Fix import: Remove unused `log_debug` from import line, keep `log_info`
- [x] Verify: `pytest tests/unit/ui/screens/test_cargo_quick_dialog.py -v` — 9 tests pass
- [x] Verify: `pytest tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py -v` — 2 tests pass

**Notes:** Updated test patches from `game.ui.screens.cargo_quick_dialog.IssueTransferCommand` to `game.strategy.services.cargo_transfer_service.IssueTransferCommand` since command is now built via service.

---

### Task 2.2: Fix test_cargo_quick_dialog_issuance.py [Medium]
**File:** `tests/unit/ui/screens/test_cargo_quick_dialog_issuance.py`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog_issuance.py -v`

- [x] Add `import pygame_gui`
- [x] Fix `mock_manager` fixture: Change `MagicMock()` → `pygame_gui.UIManager((800, 600))`
- [x] Fix `mock_scene` fixture: Wire `mock_facade` into scene BEFORE dialog construction
- [x] Remove `dialog.facade = mock_facade` and `dialog._populate_load_items()` calls - `__init__` already populates
- [x] Verify: Both tests pass (2/2)

**Notes:** Tests now work because scene.facade is properly wired before dialog construction.

---

### Task 2.3: Refactor TransferDialog to use service [Medium]
**File:** `game/ui/screens/transfer_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog.py tests/unit/ui/screens/test_transfer_dialog_enhanced.py -v`

- [x] Add import: `from game.strategy.services.cargo_transfer_service import CargoTransferService`
- [x] Replace `_get_inventory_items()` method with call to `CargoTransferService.get_inventory_items(obj_info)`
- [x] In `_update_cargo_list()`: Updated calls to use service, with key conversion (max_amount→max, cargo_type→type)
- [x] In `_issue_order()`: Use `CargoTransferService.build_transfer_command(...)` for fleet-to-planet; manual for fleet-to-fleet (needs target_fleet_id)
- [x] Delete the `_get_inventory_items()` method entirely
- [x] Verify: `pytest tests/unit/ui/screens/test_transfer_dialog_enhanced.py -v` — 2 tests pass

**Notes:** Fleet-to-fleet transfers still use direct IssueTransferCommand since they need target_fleet_id parameter not supported by service.

---

### Task 2.4: Fix test_transfer_dialog.py [Medium]
**File:** `tests/unit/ui/screens/test_transfer_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog.py -v`

- [x] Fix `test_transfer_dialog_init_populates_sources`:
  - Updated assertion to `== 4` (2 fleets + 1 colony + 1 uncolonized planet)
  - Added assertion for uncolonized planet in options
- [x] Fix `test_update_cargo_list_for_colony`:
  - Updated to use proper 2-arg signature: `dialog._update_cargo_list(source, target)`
- [x] Fix `test_issue_order_dispatches_command`:
  - Added `mock_planet_info` mock with empty population_details BEFORE dialog construction
  - Added `direction` key to cargo item
  - Updated patch path to `game.strategy.services.cargo_transfer_service.IssueTransferCommand`
- [x] Verify: All 4 tests pass

**Notes:** Tests properly mock DTOs before dialog construction now.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/ui/screens/test_cargo_quick_dialog*.py -v` — all pass (13 tests)
- [x] `pytest tests/unit/ui/screens/test_transfer_dialog*.py -v` — all pass (6 tests)
- [x] `pytest tests/ -n 12` — 11854 passed, 7 failures (pre-existing input handler/filter tests for Phase 3)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
