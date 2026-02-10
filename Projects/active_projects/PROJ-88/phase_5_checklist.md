# Phase 5: Game/app Scene Dispatch Completion [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-88 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Complete the IScene migration started in PROJ-65 by moving StrategyScreen's legacy handle_click/handle_scroll into its handle_event method, then removing the legacy dispatch code from app.py. Also clean up legacy update_input/handle_input per-scene calls in _update_and_draw.

**File:** `game/app.py`
**Related Files:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/ tests/unit/test_app_integration.py -n 12`

---

## Tasks

### Task 5.1: Audit StrategyScreen Event Handling [Simple]
**File:** `game/ui/screens/strategy_screen.py`
- [ ] Read StrategyScreen's `handle_event()` method -- document what events it currently handles
- [ ] Read StrategyScreen's `handle_click()` method -- document what it delegates to
- [ ] Check if StrategyScreen has a `handle_scroll()` method or if scroll is only in app.py
- [ ] Read StrategyScreen's `update_input()` method -- document what per-frame input it processes
- [ ] Identify the `_input` handler object and what methods it exposes
- [ ] Document findings in Notes below

**Notes:**

---

### Task 5.2: Fold Click Handling into handle_event [Medium]
**File:** `game/ui/screens/strategy_screen.py`
- [ ] In `handle_event()`, add handling for `pygame.MOUSEBUTTONDOWN` events
- [ ] Extract `event.pos` as `(mx, my)` and `event.button` from the event
- [ ] Call the same internal click logic that `handle_click()` currently uses
- [ ] Verify that `handle_event()` now handles clicks that were previously dispatched separately
- [ ] Keep `handle_click()` method temporarily for backward compatibility (will remove in Task 5.4)

**Notes:** The app.py `_handle_click()` method currently extracts `mx, my = event.pos` and calls `strategy_scene.handle_click(mx, my, event.button)`. The same logic should now happen inside StrategyScreen's `handle_event()` when it receives the MOUSEBUTTONDOWN event.

---

### Task 5.3: Fold Scroll Handling into handle_event [Medium]
**File:** `game/ui/screens/strategy_screen.py`
- [ ] In `handle_event()`, add handling for `pygame.MOUSEWHEEL` events
- [ ] Extract `event.y` from the scroll event
- [ ] Call the appropriate internal scroll logic (currently app.py calls `handle_scroll(event.y, screen_height)`)
- [ ] Determine if screen_height is needed or can be obtained from the scene's own dimensions
- [ ] Verify scroll behavior works correctly through handle_event

**Notes:** app.py `_handle_scroll()` calls `strategy_scene.handle_scroll(event.y, self.screen.get_size()[1])`. The StrategyScreen should be able to use its own `self.height` instead of receiving screen_height as a parameter.

---

### Task 5.4: Fold update_input into update [Medium]
**File:** `game/ui/screens/strategy_screen.py`
- [ ] Examine what `update_input(dt, events)` does that isn't covered by `handle_event()` + `update(dt)`
- [ ] If it processes per-frame keyboard state (e.g., held keys for scrolling), move that logic into `update(dt)`
- [ ] If it processes event-based input, that should already be handled by `handle_event()`
- [ ] Ensure the strategy screen works correctly with input handled through IScene methods only
- [ ] Repeat analysis for ResearchTreeScene and GalaxyTestScreen `handle_input()` if applicable

**Notes:** `update_input()` may handle continuous key-hold state (e.g., arrow keys for map panning). This needs to be called from `update(dt)` rather than separately from app.py. The events parameter may need to be stored or handled differently.

---

### Task 5.5: Remove Legacy Dispatch from app.py [Simple]
**File:** `game/app.py`
- [ ] Remove the StrategyScreen-specific code from `_handle_click()` (lines 580-582: the `if self.state == GameState.STRATEGY` block)
- [ ] If `_handle_click()` is now empty, remove the method entirely and remove its call from `_handle_normal_events()`
- [ ] Remove the StrategyScreen-specific code from `_handle_scroll()` (lines 657-659: the `if self.state == GameState.STRATEGY` block)
- [ ] If `_handle_scroll()` is now empty, remove the method entirely and remove its call from `_handle_normal_events()`
- [ ] Remove the StrategyScreen-specific `update_input()` call from `_update_and_draw()` (line 666)
- [ ] Remove the ResearchTree/GalaxyTest `handle_input()` calls from `_update_and_draw()` (lines 667-670) if those scenes have been updated
- [ ] Verify `_handle_normal_events()` no longer dispatches MOUSEBUTTONDOWN/MOUSEWHEEL separately -- they flow through `_forward_event_to_scene()` naturally

**Notes:** After this task, `_handle_normal_events()` should only handle QUIT, KEYDOWN (global actions), and VIDEORESIZE. All other events flow to `_forward_event_to_scene()` which calls `active_scene.handle_event()`.

---

### Task 5.6: Clean Up Dead Methods [Simple]
**File:** `game/ui/screens/strategy_screen.py`
- [ ] Remove `handle_click()` method from StrategyScreen (now handled by handle_event)
- [ ] Remove `handle_scroll()` if it existed (now handled by handle_event)
- [ ] Remove `update_input()` if it was folded into update (or keep if it has distinct per-frame logic that can't move)
- [ ] Verify no other code calls the removed methods (grep for `handle_click`, `handle_scroll`, `update_input` in the codebase)

**Notes:**

---

### Task 5.7: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12 --tb=short`
- [ ] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [ ] Confirm all tests pass with zero new failures
- [ ] Verify `test_app_integration.py` still passes
- [ ] Verify `test_strategy_menu_actions.py` still passes
- [ ] Record test count: _____ passed, _____ failed
- [ ] Recommend manual smoke test: launch game, enter strategy mode, verify click/scroll/panning works

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
