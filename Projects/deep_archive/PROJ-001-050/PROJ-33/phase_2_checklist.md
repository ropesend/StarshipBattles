# Phase 2: Audit Fixes (Cycle 1)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-33 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix direct entity mutations found in Audit Cycle 1
**Priority:** Immediate

---

## Audit Cycle 1 - Confirmed Issues

### Confirmed Issue 1: Theme dropdown bypasses ViewModel
**File:** `game/ui/screens/workshop_event_router.py:346`
**Severity:** Major
**Evidence:** Direct mutation `gui.ship.theme_id = event.text` bypasses `viewmodel.set_ship_theme()`

### Confirmed Issue 2: AI strategy dropdown bypasses ViewModel
**File:** `game/ui/screens/workshop_event_router.py:415,418`
**Severity:** Major
**Evidence:** Direct mutation `gui.ship.ai_strategy = ...` with no ViewModel method available

---

## Tasks

### Task 2.1: Fix theme dropdown handler [Medium] [Complete]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/builder/test_builder_viewmodel.py -k theme`

- [x] Update theme dropdown handler to use `gui.viewmodel.set_ship_theme(event.text)`
- [x] Verify handler still calls `gui.right_panel.update_portrait_image()` after ViewModel call
- [x] Verify: tests pass, no regressions

**Notes:** Changed line 346 from `gui.ship.theme_id = event.text` to `gui.viewmodel.set_ship_theme(event.text)`. All 108 builder tests pass.


### Task 2.2: Add set_ship_ai_strategy to ViewModel [Medium] [Complete]
**File:** `game/ui/screens/workshop_viewmodel.py`
**Tests:** `pytest tests/unit/builder/test_builder_viewmodel.py -k ai_strategy`

- [x] Add `set_ship_ai_strategy(strategy_id: str)` method to WorkshopViewModel
- [x] Method should check for null ship
- [x] Method should skip emission if value unchanged
- [x] Method should emit SHIP_UPDATED event
- [x] Write test: `test_set_ship_ai_strategy_updates_and_emits`
- [x] Write test: `test_set_ship_ai_strategy_no_change_if_same`
- [x] Verify: tests pass, no regressions

**Notes:** Added `set_ship_ai_strategy()` method following same pattern as `set_ship_name()` and `set_ship_theme()`. 2 new tests written and pass. All 110 builder tests pass.


### Task 2.3: Fix AI strategy dropdown handler [Simple] [Complete]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/builder/test_builder_viewmodel.py -k ai_strategy`

- [x] Update AI strategy dropdown handler to use `gui.viewmodel.set_ship_ai_strategy(strategy_id)`
- [x] Verify: tests pass, no regressions

**Notes:** Changed lines 415 and 418 from `gui.ship.ai_strategy = ...` to `gui.viewmodel.set_ship_ai_strategy(...)`. All 110 builder tests pass.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate ready for re-audit
