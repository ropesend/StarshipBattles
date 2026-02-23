# Phase 2: Refactor Dialogs to Use Service

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-162 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Refactor CargoQuickDialog and TransferDialog to delegate business logic to CargoTransferService. Fix the 5 failing dialog tests.

---

## Tasks

### Task 2.1: Refactor CargoQuickDialog to use service [Medium]
**File:** `game/ui/screens/cargo_quick_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog.py tests/unit/ui/screens/test_cargo_quick_dialog_issuance.py tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py -v`

- [ ] Add import: `from game.strategy.services.cargo_transfer_service import CargoTransferService`
- [ ] Refactor `_populate_unload_items()` (lines 113-140):
  - Replace inline colony resolution with `CargoTransferService.resolve_colonies(self.facade, self.hex_coord, self.fleet)`
  - Replace inline fleet cargo extraction with `CargoTransferService.get_unload_items(self.facade, self.fleet.id, colonies)`
  - Keep UI row creation (`_add_cargo_row()`) — that stays in the dialog
- [ ] Refactor `_populate_load_items()` (lines 142-194):
  - Replace inline colony resolution with `CargoTransferService.resolve_colonies(self.facade, self.hex_coord, self.fleet)`
  - Replace inline population extraction with `CargoTransferService.get_load_items(self.facade, colonies)`
  - Keep UI row creation (`_add_cargo_row()`) — that stays in the dialog
  - **Remove all 18 DIAG log_info statements** (lines 145, 149, 152, 155, 157, 162, 167, 172, 185)
  - **Remove dead diagnostic code**: fleet cargo capacity/current calls (lines 159-162) and planet iteration loop (lines 156-157)
- [ ] Refactor `_issue_orders()` (lines 301-357):
  - Replace inline command assembly with `CargoTransferService.build_transfer_command(...)` for each item
  - **Remove all DIAG log_info statements** (lines 303, 316, 318, 328, 343, 346, 353)
  - Keep the 3 legitimate operational logs (lines 349, 351, 355)
- [ ] Fix import: Remove unused `log_debug` from import line (line 13), keep `log_info`
- [ ] Remove stale `# FIX:` and `# DIAGNOSTIC:` comments
- [ ] Verify: `pytest tests/unit/ui/screens/test_cargo_quick_dialog.py -v` — 7 existing tests still pass
- [ ] Verify: `pytest tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py -v` — 2 existing tests still pass

**Notes:**

---

### Task 2.2: Fix test_cargo_quick_dialog_issuance.py [Medium]
**File:** `tests/unit/ui/screens/test_cargo_quick_dialog_issuance.py`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog_issuance.py -v`

- [ ] Add `import pygame_gui` (currently missing)
- [ ] Fix `mock_manager` fixture (line 11-12): Change `MagicMock()` → `pygame_gui.UIManager((800, 600))`
- [ ] Fix `mock_scene` fixture (line 22-23): Wire `mock_facade` into scene BEFORE dialog construction:
  ```python
  @pytest.fixture
  def mock_scene(self, mock_facade):
      scene = MagicMock()
      scene._facade = mock_facade
      scene.facade = mock_facade
      return scene
  ```
- [ ] Fix `mock_fleet` fixture (line 14-19): Add explicit return values for methods called during `_populate_load_items`:
  ```python
  fleet.get_fleet_cargo_capacity.return_value = 200
  fleet.get_fleet_cargo_current.return_value = 0
  ```
  (Only needed if DIAG cleanup not yet done; harmless either way)
- [ ] Fix `test_confirm_issues_command` (line 43):
  - Remove `with patch('...log_info')` wrapper (line 45)
  - Remove `dialog.facade = mock_facade` (line 51) — scene.facade already correct
  - Remove `dialog._populate_load_items()` (line 54) — `__init__` already populates
  - Un-indent test body
- [ ] Fix `test_confirm_all_issues_amount_zero` (line 79):
  - Remove `dialog.facade = mock_facade` (line 85)
  - Remove `dialog._populate_load_items()` (line 86)
- [ ] Verify: Both tests pass

**Notes:**

---

### Task 2.3: Refactor TransferDialog to use service [Medium]
**File:** `game/ui/screens/transfer_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog.py tests/unit/ui/screens/test_transfer_dialog_enhanced.py -v`

- [ ] Add import: `from game.strategy.services.cargo_transfer_service import CargoTransferService`
- [ ] Replace `_get_inventory_items()` method (lines 240-275) with call to `CargoTransferService.get_inventory_items(obj_info)`
- [ ] In `_update_cargo_list()` (line 277): Update calls from `self._get_inventory_items(source_obj)` to `CargoTransferService.get_inventory_items(source_obj)` and same for target_obj
- [ ] In `_issue_order()` (line 413): Use `CargoTransferService.build_transfer_command(...)` for command assembly (lines 427-479)
- [ ] Delete the `_get_inventory_items()` method entirely
- [ ] Verify: `pytest tests/unit/ui/screens/test_transfer_dialog_enhanced.py -v` — 2 at-risk tests still pass

**Notes:**

---

### Task 2.4: Fix test_transfer_dialog.py [Medium]
**File:** `tests/unit/ui/screens/test_transfer_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog.py -v`

- [ ] Fix `test_transfer_dialog_init_populates_sources` (line 40):
  - Test expects `len(dialog.available_sources) == 3` but production now includes uncolonized planets
  - Update assertion to `== 4` (2 fleets + 1 colony + 1 uncolonized planet)
  - Or update mock data to match original intent (remove p2 uncolonized planet)
  - Choose approach that matches the intent: production code is correct, test expectation is stale
- [ ] Fix `test_update_cargo_list_for_colony` (line 101):
  - Call signature changed: `_update_cargo_list(source, target)` now requires 2 args
  - Update: `dialog._update_cargo_list({'type': 'colony', 'id': 10}, None)` or provide proper target
- [ ] Fix `test_issue_order_dispatches_command` (line 139):
  - Failure is during `__init__` → `_populate_initial_data()` → `_on_source_changed()` → `_update_cargo_list()` → `_get_inventory_items()` comparing `MagicMock > 0`
  - Fix: Properly mock `facade.get_fleet()` to return FleetInfo with `passengers_current = 0` (not MagicMock)
  - The mock_fleet_info must be set up BEFORE dialog construction, not just for the later assertions
- [ ] Verify: All 3 previously failing tests now pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/ui/screens/test_cargo_quick_dialog*.py -v` — all pass (0 failures)
- [ ] `pytest tests/unit/ui/screens/test_transfer_dialog*.py -v` — all pass (0 failures)
- [ ] `pytest tests/ --testmon` — no regressions
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
