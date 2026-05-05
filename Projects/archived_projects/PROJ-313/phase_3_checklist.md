# Phase 3: Migrate Event-Listener-Only Windows (6 windows)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-313 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate the 6 windows that currently rely entirely on `_handle_window_close` event-driven cleanup (no `kill()` override, no registrar callback). These have the riskiest existing cleanup style — they vanish from the slot when pygame_gui posts `UI_WINDOW_CLOSE`, but if any code path bypassed that event they would leak. Migrating them first under the OR-bridge protection makes the rest of the project simpler.

**Per-window pattern (apply six times, one commit per window):**
1. Subclass `StrategyModalWindow` instead of `UIWindow` directly.
2. Update `__init__` to forward `window_manager` keyword.
3. Update spawn site in `strategy_event_router.py` to pass `window_manager=self.window_manager`.
4. Delete the window's slot field on `StrategyWindowManager`.
5. Delete the slot's clause in `has_modal_open()`.
6. Delete the slot's clause in `_is_blocking_ui_element_at()`.
7. Delete the slot's clause in `_handle_window_close`.
8. Run targeted tests for that window plus the contract test.

---

## Tasks

### Task 3.1: Migrate `OrdersWindow` (slot: `fleet_orders_window`) [Medium]
**File:** `game/ui/screens/orders_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_orders_window.py tests/unit/ui/screens/test_strategy_event_router.py tests/unit/ui/screens/test_strategy_window_manager_public_api.py`

- [x] Change class declaration to `class OrdersWindow(StrategyModalWindow):`
- [x] Add import for `StrategyModalWindow`
- [x] Update `__init__` signature to accept `window_manager: "StrategyWindowManager"` as keyword-only param
- [x] Pass `window_manager=window_manager` to `super().__init__(...)`
- [x] In `strategy_event_router.py` find the `OrdersWindow(...)` spawn site (around line 105 of `orders_window_ctrl.py` per audit) and add `window_manager=self.window_manager` argument
- [x] In `strategy_window_manager.py`, delete the `fleet_orders_window: Optional[UIWindow] = None` slot field
- [x] In `strategy_event_router.py`, delete the `if self.window_manager.fleet_orders_window is not None:` clause from `has_modal_open()`
- [x] In `strategy_event_router.py`, delete the same slot from `_is_blocking_ui_element_at()`
- [x] In `strategy_event_router.py`, delete the `event.ui_element == wm.fleet_orders_window` branch from `_handle_window_close` (around line 413-446)
- [x] Run `pytest tests/unit/ui/screens/test_orders_window.py` — pass
- [x] Run `python Tools/test_sharded/test_sharded.py` — 15893 baseline preserved
**Notes:** [Filled during implementation]

### Task 3.2: Migrate `TransferDialog` (slot: `transfer_dialog`) [Medium]
**File:** `game/ui/screens/transfer_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog.py tests/unit/ui/screens/test_strategy_event_router.py`

- [x] Same migration steps as Task 3.1, applied to `TransferDialog`
- [x] Spawn site: `transfer_dialogs.py:43` per audit
- [x] Run targeted tests — pass
- [x] Run full sharded — 15893 preserved
**Notes:**

### Task 3.3: Migrate `CargoQuickDialog` (slot: `cargo_quick_dialog`) [Medium]
**File:** `game/ui/screens/cargo_quick_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog.py tests/unit/ui/screens/test_strategy_event_router.py`

- [x] Same migration steps
- [x] Spawn site: `transfer_dialogs.py:69`
- [x] Run targeted tests — pass
- [x] Run full sharded — 15893 preserved
**Notes:**

### Task 3.4: Migrate `PlanetSelectionWindow` (slot: `planet_selection_window`) [Medium]
**File:** `game/ui/screens/planet_selection_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_selection_window.py tests/unit/ui/screens/test_strategy_event_router.py`

- [x] Same migration steps
- [x] Spawn site: `selection_prompts.py:45`
- [x] **Note:** This window has a `kill()` override at line 174 already (per audit) but it does NOT invoke any callback — verify this and decide whether to keep, simplify, or delete the override. After base-class migration the override should only do whatever non-callback work it was doing (if any); the base-class `kill()` handles deregistration.
- [x] Run targeted tests — pass
- [x] Run full sharded — 15893 preserved
**Notes:**

### Task 3.5: Migrate `SystemSelectionWindow` (slot: `system_selection_window`) [Medium]
**File:** `game/ui/screens/system_selection_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_system_selection_window.py tests/unit/ui/screens/test_strategy_event_router.py`

- [x] Same migration steps
- [x] Spawn site: `selection_prompts.py:63`
- [x] Run targeted tests — pass
- [x] Run full sharded — 15893 preserved
**Notes:**

### Task 3.6: Migrate `FleetSelectionWindow` (slot: `fleet_selection_window`) [Medium]
**File:** `game/ui/screens/fleet_selection_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_selection_window.py tests/unit/ui/screens/test_strategy_event_router.py`

- [x] Same migration steps
- [x] Spawn site: `selection_prompts.py:80`
- [x] Run targeted tests — pass
- [x] Run full sharded — 15893 preserved
**Notes:**

### Task 3.7: Phase verification [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] All 6 windows successfully migrated
- [x] `has_modal_open()` and `_is_blocking_ui_element_at()` chains have shrunk by 6 clauses each
- [x] `_handle_window_close` has shrunk by 6 branches
- [x] Full sharded suite still 15893 passing
- [x] Manual smoke: open and close one of the migrated windows (e.g. transfer dialog) — confirm `has_modal_open()` returns False after close
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4 (Migrate dual-cleanup windows)
