# Phase 3: StrategyInputHandler Router Decomposition

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-173 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Decompose StrategyInputHandler (898 lines) into an event router with 3 specialized sub-routers: FleetCommandRouter, ClickModeDispatcher, and UIActionRouter. The main handler keeps event dispatch, scroll handling, and per-frame input. Sub-routers handle domain-specific logic.

---

## Tasks

### Task 3.1: Extract FleetCommandRouter [Medium]
**File:** `game/ui/screens/strategy_input_handler.py` (read)
**New File:** `game/ui/screens/strategy_fleet_command_router.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/unit/ui/screens/test_superweapon_input_modes.py -v`

- [ ] Read `strategy_input_handler.py` fully, identify fleet command methods:
  - [ ] `_handle_fleet_mode_action(action)` (lines 128-191, ~64L) — MOVE, JOIN, COLONIZE, TRANSFER, DROP/LOAD_CARGO, CANCEL
  - [ ] `_handle_superweapon_action(action)` (lines 192-234, ~43L) — IMPLODE, STELLERATE, OPEN/CLOSE_WARP, DYSON, SELF_DESTRUCT
  - [ ] `_finish_move_action(fleet)` (lines 600-606, ~7L) — post-move cleanup
  - [ ] `_handle_detail_panel_action(action)` (lines 293-313, ~21L) — detail panel commands
- [ ] Create `game/ui/screens/strategy_fleet_command_router.py`:
  - [ ] `FleetCommandRouter` class
  - [ ] Constructor: `__init__(self, handler)` — receives StrategyInputHandler reference
  - [ ] Accesses: `self._handler.scene`, `self._handler.input_mode`
  - [ ] Methods: `handle_fleet_action(action) -> bool`, `handle_superweapon_action(action) -> bool`, `handle_detail_action(action) -> bool`, `finish_move_action(fleet)`
  - [ ] Returns `True` if action was handled
  - [ ] Does NOT import StrategyInputHandler (uses parent reference, TYPE_CHECKING only)
- [ ] Update `strategy_input_handler.py`:
  - [ ] In `__init__`: `self._fleet_router = FleetCommandRouter(self)`
  - [ ] `_handle_keydown_mapped()`: delegate fleet/superweapon/detail actions to router
  - [ ] Remove moved methods
- [ ] Run tests: `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/unit/ui/screens/test_superweapon_input_modes.py -v`

**Notes:**

---

### Task 3.2: Extract ClickModeDispatcher [Complex]
**File:** `game/ui/screens/strategy_input_handler.py` (read)
**New File:** `game/ui/screens/strategy_click_dispatcher.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py tests/unit/ui/screens/test_strategy_input_handler_transfer.py -v`

- [ ] Identify all click mode handlers:
  - [ ] `_handle_select_mode_click()` (lines 562-599, ~38L)
  - [ ] `_handle_move_mode_click()` (lines 355-393, ~39L)
  - [ ] `_handle_join_mode_click()` (lines 394-411, ~18L)
  - [ ] `_handle_colonize_mode_click()` (lines 412-444, ~33L)
  - [ ] `_handle_transfer_mode_click()` (lines 445-458, ~14L)
  - [ ] `_handle_drop_cargo_mode_click()` (lines 459-472, ~14L)
  - [ ] `_handle_load_cargo_mode_click()` (lines 473-486, ~14L)
  - [ ] `_handle_implode_planet_click()` (lines 487-501, ~15L)
  - [ ] `_handle_stellerate_star_click()` (lines 502-516, ~15L)
  - [ ] `_handle_open_warp_click()` (lines 517-531, ~15L)
  - [ ] `_handle_close_warp_click()` (lines 532-546, ~15L)
  - [ ] `_handle_dyson_sphere_click()` (lines 547-561, ~15L)
- [ ] Also include picking methods (only called from SELECT mode click):
  - [ ] `_handle_picking()` (lines 748-832, ~85L)
  - [ ] `_hit_test_planets()` (lines 607-716, ~110L)
  - [ ] `_resolve_click_target()` (lines 717-747, ~31L)
- [ ] Create `game/ui/screens/strategy_click_dispatcher.py`:
  - [ ] `ClickModeDispatcher` class
  - [ ] Constructor: `__init__(self, handler)` — receives StrategyInputHandler reference
  - [ ] Accesses: `self._handler.scene`, `self._handler.input_mode`, `self._handler._fleet_router.finish_move_action()`
  - [ ] Main method: `dispatch_click(mx, my, button) -> bool`
  - [ ] Mode dispatch dict: `{'SELECT': self._handle_select, 'MOVE': self._handle_move, ...}`
  - [ ] Move all 12 click handlers + 3 picking methods
  - [ ] Does NOT import StrategyInputHandler (TYPE_CHECKING only)
- [ ] Update `strategy_input_handler.py`:
  - [ ] In `__init__`: `self._click_dispatch = ClickModeDispatcher(self)`
  - [ ] `handle_click()` becomes: delegates to `self._click_dispatch.dispatch_click(mx, my, button)`
  - [ ] Remove all 15 moved methods
- [ ] Run tests: `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py tests/unit/ui/screens/test_strategy_input_handler_transfer.py -v`

**Notes:**

---

### Task 3.3: Extract UIActionRouter [Simple]
**File:** `game/ui/screens/strategy_input_handler.py` (read)
**New File:** `game/ui/screens/strategy_ui_action_router.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/repro_issues/test_bug_15_screenshot_strategy.py -v`

- [ ] Identify UI action methods:
  - [ ] `_handle_ui_action(action)` (lines 235-292, ~58L)
  - [ ] `_take_screenshot_full()` (lines 884-891, ~8L)
  - [ ] `_take_screenshot_viewport()` (lines 892-899, ~8L)
- [ ] Create `game/ui/screens/strategy_ui_action_router.py`:
  - [ ] `UIActionRouter` class
  - [ ] Constructor: `__init__(self, handler)` — receives StrategyInputHandler reference
  - [ ] Methods: `handle_ui_action(action) -> bool`, `take_screenshot_full()`, `take_screenshot_viewport()`
  - [ ] Action dispatch maps: zoom actions, button actions, cycle actions
  - [ ] Does NOT import StrategyInputHandler (TYPE_CHECKING only)
- [ ] Update `strategy_input_handler.py`:
  - [ ] In `__init__`: `self._ui_router = UIActionRouter(self)`
  - [ ] `_handle_keydown_mapped()`: delegate UI actions to router
  - [ ] Remove moved methods
- [ ] Run tests: `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/repro_issues/test_bug_15_screenshot_strategy.py -v`

**Notes:**

---

### Task 3.4: Refactor StrategyInputHandler to event router [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/unit/ui/screens/test_strategy_input_handler_transfer.py tests/unit/ui/screens/test_superweapon_input_modes.py -v`

- [ ] Verify handler is now thin event router:
  - [ ] `__init__()` — creates 3 sub-routers
  - [ ] `handle_event()` — top-level event dispatcher (stays)
  - [ ] `_handle_button_press()` — UI button routing (stays, ~22L)
  - [ ] `_handle_keydown()` / `_handle_keydown_mapped()` — delegates to routers
  - [ ] `handle_click()` — delegates to ClickModeDispatcher
  - [ ] `_handle_scroll()` — scroll wheel routing (stays, ~25L)
  - [ ] `update_input()` — per-frame hover + camera (stays, ~26L)
- [ ] Verify: `input_mode` property stays on handler, sub-routers read/write via parent
- [ ] Verify: StrategyInputHandler public API unchanged (handle_event, handle_click, update_input)
- [ ] Run ALL input handler tests: `pytest tests/unit/ui/screens/test_strategy_input_handler_core.py tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/unit/ui/screens/test_strategy_input_handler_transfer.py tests/unit/ui/screens/test_superweapon_input_modes.py tests/repro_issues/test_bug_15_screenshot_strategy.py -v`
- [ ] Fix any test failures from moved methods
- [ ] Verify: StrategyInputHandler < 250 lines

**Notes:**

---

### Task 3.5: Phase 3 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: 12,023+ tests pass, 0 failures
- [ ] Verify line counts:
  - [ ] `strategy_input_handler.py` < 250 lines
  - [ ] `strategy_fleet_command_router.py` exists (~125 lines)
  - [ ] `strategy_click_dispatcher.py` exists (~250+ lines)
  - [ ] `strategy_ui_action_router.py` exists (~75 lines)
- [ ] Verify: Sub-routers do NOT import StrategyInputHandler at runtime (TYPE_CHECKING only)
- [ ] Verify: StrategyInputHandler public API unchanged

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
