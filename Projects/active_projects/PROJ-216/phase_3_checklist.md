# Phase 3: Fix Confirmation Dialog Flow

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-216 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Ensure confirmation dialog callbacks execute correctly regardless of the click gate.

---

## Tasks

### Task 3.1: Verify confirmation events are processed via `route_event()` [Simple]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/strategy/ --testmon`

- [ ] Verify that `UI_CONFIRMATION_DIALOG_CONFIRMED` events reach `route_event()` line 129-134
- [ ] Verify that `route_event()` is called from `handle_event()` in `strategy_input_handler.py` line 66 (via `scene.ui.handle_event(event)`)
- [ ] Confirm that the confirmation flow does NOT depend on `handle_click()` - it goes through the `handle_event()` -> `route_event()` path instead
- [ ] If confirmation flow is already independent of the click gate (likely), document this and mark task complete

**Notes:** The confirmation event is a pygame_gui event, not a MOUSEBUTTONDOWN. It flows through `route_event()`, not `handle_click()`. This task is primarily verification that the Phase 2 fix is sufficient.

### Task 3.2: Test superweapon confirmation end-to-end [Simple]
**Tests:** Manual test - launch game, test stellerate star confirmation

- [ ] Start new game, select fleet with stellerate star ability
- [ ] Press Ctrl+Shift+S, click on a star
- [ ] Verify confirmation dialog appears
- [ ] Click "Confirm" in dialog
- [ ] Verify order appears in fleet's order queue

**Notes:** This tests the full superweapon confirmation flow after the Phase 2 fix.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
