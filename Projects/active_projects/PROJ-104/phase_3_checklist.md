# Phase 3: StrategyInputHandler._handle_keydown_mapped (CC 50 → ≤8)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-104 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Group the 30+ elif branches into category handlers

---

## Tasks

### Task 3.1: Extract `_handle_fleet_mode_action(self, action)` [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py -x -q`

- [ ] Create method handling FLEET_MOVE, FLEET_JOIN, FLEET_COLONIZE, FLEET_TRANSFER, FLEET_DROP_CARGO, FLEET_LOAD_CARGO, FLEET_CANCEL_MODE (lines 121-168)
- [ ] Pattern: each sets `self.input_mode` if fleet selected
- [ ] Return `True` if action was handled, `False` otherwise
- [ ] Verify tests

**Notes:**

### Task 3.2: Extract `_handle_superweapon_action(self, action)` [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py -x -q`

- [ ] Create method handling FLEET_IMPLODE_PLANET through FLEET_SELF_DESTRUCT (lines 170-198)
- [ ] Return `True` if action was handled
- [ ] Verify tests

**Notes:**

### Task 3.3: Extract `_handle_ui_action(self, action)` [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py -x -q`

- [ ] Create method handling zoom, screenshot, button-triggered actions, and cycle selection (lines 200-232)
- [ ] Return `True` if action was handled
- [ ] Verify tests

**Notes:**

### Task 3.4: Extract `_handle_detail_panel_action(self, action)` [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py -x -q`

- [ ] Create method handling DETAIL_PANEL_ORDERS, DETAIL_PANEL_FLEET_REPORT, DETAIL_PANEL_BUILD (lines 234-243)
- [ ] Return `True` if action was handled
- [ ] Verify tests

**Notes:**

### Task 3.5: Refactor `_handle_keydown_mapped` as dispatcher [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/unit/ui/screens/test_strategy_input_handler_transfer.py -x -q`

- [ ] `_handle_keydown_mapped` becomes: resolve action → try each category handler in order
- [ ] Verify all hotkey tests pass

**Notes:**

### Task 3.6: Verify CC reduction [Simple]
- [ ] Run `radon cc game/ui/screens/strategy_input_handler.py -s -n C` — `_handle_keydown_mapped` should be ≤8
- [ ] Run full suite: `pytest tests/ -n 12 -q`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `_handle_keydown_mapped` CC ≤ 8 confirmed via radon
- [ ] All 8167 tests passing
- [ ] No public API changes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
