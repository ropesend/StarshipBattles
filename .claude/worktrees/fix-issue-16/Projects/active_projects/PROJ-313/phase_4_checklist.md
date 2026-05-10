# Phase 4: Migrate Dual-Cleanup Windows (3 windows)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-313 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate the 3 windows that use BOTH a registrar callback AND `_handle_window_close` event-driven cleanup. Each migration deletes the manual `kill()` override on the window, the registrar's `_on_closed` callback, the `on_close_callback` constructor parameter, the slot field, and the relevant clauses in router scans + event listener.

**Per-window pattern:**
1. Subclass `StrategyModalWindow`.
2. Forward `window_manager` keyword in `__init__`.
3. Update spawn site to pass `window_manager=self.window_manager`.
4. Delete the window's manual `kill()` override.
5. Delete the `on_close_callback` parameter from the window's `__init__`.
6. Delete the registrar's `_on_closed` method and the `on_close_callback=...` argument at spawn.
7. Delete the slot field on `StrategyWindowManager`.
8. Delete clauses in `has_modal_open()`, `_is_blocking_ui_element_at()`, `_handle_window_close`.

---

## Tasks

### Task 4.1: Migrate `EmpireBuildQueueWindow` [Medium]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Registrar:** `game/ui/screens/strategy_windows/build_queue_windows.py` (`_on_closed` at line 82 per audit)
**Spawn site:** `build_queue_windows.py:64`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py tests/unit/ui/screens/test_strategy_event_router.py`

- [x] Subclass migration steps
- [x] Delete `kill()` override at line 554
- [x] Delete `on_close_callback` param from `__init__`
- [x] Delete registrar `_on_closed` method
- [x] Delete slot field, `has_modal_open` clause, `_is_blocking_ui_element_at` clause, `_handle_window_close` clause
- [x] Run targeted tests — pass
- [x] Run full sharded — 15893 preserved
**Notes:**

### Task 4.2: Migrate `EventLogWindow` [Medium]
**File:** `game/ui/screens/event_log_window.py`
**Registrar:** `game/ui/screens/strategy_windows/event_log_window_ctrl.py` (`_on_closed` at line 68)
**Spawn site:** `event_log_window_ctrl.py:47`
**Tests:** `pytest tests/unit/ui/screens/test_event_log_window.py tests/unit/ui/screens/test_strategy_event_router.py`

- [x] Same migration steps
- [x] Delete `kill()` override at line 378
- [x] Run targeted tests — pass
- [x] Run full sharded — 15893 preserved
**Notes:**

### Task 4.3: Migrate `EmpirePanelWindow` [Medium]
**File:** `game/ui/screens/empire_panel_window.py`
**Registrar:** `game/ui/screens/strategy_windows/empire_panel_ctrl.py` (`_on_closed` at line 52)
**Spawn site:** `empire_panel_ctrl.py:42`
**Tests:** `pytest tests/unit/ui/screens/test_empire_panel_window.py tests/unit/ui/screens/test_strategy_event_router.py`

- [x] Same migration steps
- [x] Delete `kill()` override at line 527
- [x] **CARE:** This file also handles `settings_window` which is the only intentionally non-modal slot. Do NOT migrate `settings_window` — leave its slot, its `_on_closed` (line 81), and its construction (line 74) untouched. The settings_window is also at `empire_panel_ctrl.py:74` so be precise about which window's `_on_closed` you're deleting.
- [x] Run targeted tests — pass
- [x] Run full sharded — 15893 preserved
**Notes:**

### Task 4.4: Phase verification [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] All 3 windows migrated
- [x] Router scans shrunk by 3 clauses each; `_handle_window_close` shrunk by 3
- [x] `settings_window` slot untouched (the only non-modal slot remaining at this point)
- [x] Full sharded suite still 15893 passing
- [x] Manual smoke: open Empire Panel, then open Settings from inside it; close both; verify `has_modal_open()` returns False after each
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5 (Migrate registrar-callback-only windows)
