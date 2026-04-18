# Phase 5: Extract BattleSetupInputHandler

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract event-dispatch logic from the screen's `handle_event` method (~120 lines with `hasattr(element, '_fleet_index')` style dispatch) into a `BattleSetupInputHandler` class. The handler translates pygame_gui events into Controller method calls — no direct mutation.

**Prerequisite:** Phase 4 complete — Renderer exists. Phase 6 (Controller) will follow; the handler's method calls will route to Controller methods that Phase 6 creates.

---

## Tasks

### Task 5.1: Write tests for BattleSetupInputHandler [Medium]
**File:** `tests/unit/ui/screens/battle_setup/test_input_handler.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_input_handler.py`

- [ ] Test: handler takes `view_model` + `controller` (Mock in tests) in constructor
- [ ] Test: `UI_BUTTON_PRESSED` on a fleet-create button calls `controller.create_fleet(side_id)` (or equivalent)
- [ ] Test: `UI_DROPDOWN_MENU_CHANGED` on a design dropdown calls the expected Controller method
- [ ] Test: handler does NOT directly mutate `view_model` or `state` — all writes go through Controller
- [ ] Test: events not matching any known dispatch are returned as unhandled (returns False) so the screen can pass them elsewhere
- [ ] Test: test each major event family found in the screen's current `handle_event` method

**Notes:** Use `Mock(spec=BattleSetupController)` (even if Controller isn't extracted yet — can use a stub) so the handler's contract with Controller is explicit.

### Task 5.2: Implement `BattleSetupInputHandler` [Medium]
**File:** `game/ui/screens/battle_setup/input_handler.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_input_handler.py`

- [ ] Port the dispatch logic from `FleetBattleSetupScreen.handle_event` (lines 650-774)
- [ ] Replace inline `hasattr(element, '_fleet_index')` style checks with cleaner attribute-based dispatch
- [ ] Each branch ends by calling a `self.controller.*` method (Controller stub used until Phase 6)
- [ ] Returns `True` if event consumed, `False` otherwise

**Notes:** For now, Controller can be a `Protocol` interface or a lightweight stub. Phase 6 fills in the real implementation.

### Task 5.3: Migrate screen to use BattleSetupInputHandler [Medium]
**File:** `game/ui/screens/battle_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [ ] Wire `self.input_handler = BattleSetupInputHandler(view_model, controller_stub_or_real)`
- [ ] Replace screen's `handle_event` body with delegation: `return self.input_handler.handle(event)`
- [ ] Delete the ~120 lines of dispatch logic from the screen
- [ ] Existing tests still pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `game/ui/screens/battle_setup/input_handler.py` exists with full dispatch logic
- [ ] Screen's `handle_event` is a 1-line delegate to the handler
- [ ] Tests verify handler calls Controller methods (no direct mutation)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6 (extract Controller)
