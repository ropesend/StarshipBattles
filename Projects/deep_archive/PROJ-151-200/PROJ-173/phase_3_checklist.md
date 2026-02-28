# Phase 3: StrategyInputHandler Router Decomposition

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-173 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Decompose StrategyInputHandler (898 lines) into an event router with 3 specialized sub-routers: FleetCommandRouter, ClickModeDispatcher, and UIActionRouter. The main handler keeps event dispatch, scroll handling, and per-frame input. Sub-routers handle domain-specific logic.

---

## Tasks

### Task 3.1: Extract FleetCommandRouter [Medium]
**File:** `game/ui/screens/strategy_input_handler.py` (read)
**New File:** `game/ui/screens/strategy_fleet_command_router.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/unit/ui/screens/test_superweapon_input_modes.py -v`

- [x] Read `strategy_input_handler.py` fully, identify fleet command methods:
  - [x] `_handle_fleet_mode_action(action)` (lines 128-191, ~64L) — MOVE, JOIN, COLONIZE, TRANSFER, DROP/LOAD_CARGO, CANCEL
  - [x] `_handle_superweapon_action(action)` (lines 192-234, ~43L) — IMPLODE, STELLERATE, OPEN/CLOSE_WARP, DYSON, SELF_DESTRUCT
  - [x] `_finish_move_action(fleet)` (lines 600-606, ~7L) — post-move cleanup
  - [x] `_handle_detail_panel_action(action)` (lines 293-313, ~21L) — detail panel commands
- [x] Create `game/ui/screens/strategy_fleet_command_router.py`:
  - [x] `FleetCommandRouter` class
  - [x] Constructor: `__init__(self, handler)` — receives StrategyInputHandler reference
  - [x] Accesses: `self._handler.scene`, `self._handler.input_mode`
  - [x] Methods: `handle_fleet_action(action) -> bool`, `handle_superweapon_action(action) -> bool`, `handle_detail_action(action) -> bool`, `finish_move_action(fleet)`
  - [x] Returns `True` if action was handled
  - [x] Does NOT import StrategyInputHandler (uses parent reference, TYPE_CHECKING only)
- [x] Update `strategy_input_handler.py`:
  - [x] In `__init__`: `self._fleet_router = FleetCommandRouter(self)`
  - [x] `_handle_keydown_mapped()`: delegate fleet/superweapon/detail actions to router
  - [x] Remove moved methods
- [x] Run tests: `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/unit/ui/screens/test_superweapon_input_modes.py -v`

**Notes:** 101 passed

---

### Task 3.2: Extract ClickModeDispatcher [Complex]
**File:** `game/ui/screens/strategy_input_handler.py` (read)
**New File:** `game/ui/screens/strategy_click_dispatcher.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py tests/unit/ui/screens/test_strategy_input_handler_transfer.py -v`

- [x] Identify all click mode handlers:
  - [x] `_handle_select_mode_click()` (lines 562-599, ~38L)
  - [x] `_handle_move_mode_click()` (lines 355-393, ~39L)
  - [x] `_handle_join_mode_click()` (lines 394-411, ~18L)
  - [x] `_handle_colonize_mode_click()` (lines 412-444, ~33L)
  - [x] `_handle_transfer_mode_click()` (lines 445-458, ~14L)
  - [x] `_handle_drop_cargo_mode_click()` (lines 459-472, ~14L)
  - [x] `_handle_load_cargo_mode_click()` (lines 473-486, ~14L)
  - [x] `_handle_implode_planet_click()` (lines 487-501, ~15L)
  - [x] `_handle_stellerate_star_click()` (lines 502-516, ~15L)
  - [x] `_handle_open_warp_click()` (lines 517-531, ~15L)
  - [x] `_handle_close_warp_click()` (lines 532-546, ~15L)
  - [x] `_handle_dyson_sphere_click()` (lines 547-561, ~15L)
- [x] Also include picking methods (only called from SELECT mode click):
  - [x] `_handle_picking()` (lines 748-832, ~85L)
  - [x] `_hit_test_planets()` (lines 607-716, ~110L)
  - [x] `_resolve_click_target()` (lines 717-747, ~31L)
- [x] Create `game/ui/screens/strategy_click_dispatcher.py`:
  - [x] `ClickModeDispatcher` class
  - [x] Constructor: `__init__(self, handler)` — receives StrategyInputHandler reference
  - [x] Accesses: `self._handler.scene`, `self._handler.input_mode`, `self._handler._fleet_router.finish_move_action()`
  - [x] Main method: `dispatch_click(mx, my, button) -> bool`
  - [x] Mode dispatch dict: `{'SELECT': self._handle_select, 'MOVE': self._handle_move, ...}`
  - [x] Move all 12 click handlers + 3 picking methods
  - [x] Does NOT import StrategyInputHandler (TYPE_CHECKING only)
- [x] Update `strategy_input_handler.py`:
  - [x] In `__init__`: `self._click_dispatch = ClickModeDispatcher(self)`
  - [x] `handle_click()` becomes: delegates to `self._click_dispatch.dispatch_click(mx, my, button)`
  - [x] Remove all 15 moved methods
- [x] Run tests: `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py tests/unit/ui/screens/test_strategy_input_handler_transfer.py -v`

**Notes:** 57 passed. Updated tests to patch new module locations.

---

### Task 3.3: Extract UIActionRouter [Simple]
**File:** `game/ui/screens/strategy_input_handler.py` (read)
**New File:** `game/ui/screens/strategy_ui_action_router.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/repro_issues/test_bug_15_screenshot_strategy.py -v`

- [x] Identify UI action methods:
  - [x] `_handle_ui_action(action)` (lines 235-292, ~58L)
  - [x] `_take_screenshot_full()` (lines 884-891, ~8L)
  - [x] `_take_screenshot_viewport()` (lines 892-899, ~8L)
- [x] Create `game/ui/screens/strategy_ui_action_router.py`:
  - [x] `UIActionRouter` class
  - [x] Constructor: `__init__(self, handler)` — receives StrategyInputHandler reference
  - [x] Methods: `handle_ui_action(action) -> bool`, `take_screenshot_full()`, `take_screenshot_viewport()`
  - [x] Action dispatch maps: zoom actions, button actions, cycle actions
  - [x] Does NOT import StrategyInputHandler (TYPE_CHECKING only)
- [x] Update `strategy_input_handler.py`:
  - [x] In `__init__`: `self._ui_router = UIActionRouter(self)`
  - [x] `_handle_keydown_mapped()`: delegate UI actions to router
  - [x] Remove moved methods
- [x] Run tests: `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/repro_issues/test_bug_15_screenshot_strategy.py -v`

**Notes:** 49 passed. Updated tests to patch ScreenshotManager in new module.

---

### Task 3.4: Refactor StrategyInputHandler to event router [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/unit/ui/screens/test_strategy_input_handler_transfer.py tests/unit/ui/screens/test_superweapon_input_modes.py -v`

- [x] Verify handler is now thin event router:
  - [x] `__init__()` — creates 3 sub-routers
  - [x] `handle_event()` — top-level event dispatcher (stays)
  - [x] `_handle_button_press()` — UI button routing (stays, ~22L)
  - [x] `_handle_keydown()` / `_handle_keydown_mapped()` — delegates to routers
  - [x] `handle_click()` — delegates to ClickModeDispatcher
  - [x] `_handle_scroll()` — scroll wheel routing (stays, ~25L)
  - [x] `update_input()` — per-frame hover + camera (stays, ~26L)
- [x] Verify: `input_mode` property stays on handler, sub-routers read/write via parent
- [x] Verify: StrategyInputHandler public API unchanged (handle_event, handle_click, update_input)
- [x] Run ALL input handler tests: `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/unit/ui/screens/test_strategy_input_handler_transfer.py tests/unit/ui/screens/test_superweapon_input_modes.py tests/repro_issues/test_bug_15_screenshot_strategy.py -v`
- [x] Fix any test failures from moved methods
- [x] Verify: StrategyInputHandler < 250 lines

**Notes:** 127 passed. Handler is 193 lines (< 250 target).

---

### Task 3.5: Phase 3 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: 12,312 tests pass, 1 skipped, 0 failures
- [x] Verify line counts:
  - [x] `strategy_input_handler.py` 193 lines (< 250)
  - [x] `strategy_fleet_command_router.py` 198 lines
  - [x] `strategy_click_dispatcher.py` 564 lines
  - [x] `strategy_ui_action_router.py` 115 lines
- [x] Verify: Sub-routers do NOT import StrategyInputHandler at runtime (TYPE_CHECKING only)
- [x] Verify: StrategyInputHandler public API unchanged

**Notes:** All verifications passed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
