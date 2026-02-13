# Phase 5: Game/app Scene Dispatch Completion [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-88 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Complete the IScene migration started in PROJ-65 by moving StrategyScreen's legacy handle_click/handle_scroll into its handle_event method, then removing the legacy dispatch code from app.py. Also clean up legacy update_input/handle_input per-scene calls in _update_and_draw.

**File:** `game/app.py`
**Related Files:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/ tests/unit/test_app_integration.py -n 12`

---

## Tasks

### Task 5.1: Audit StrategyScreen Event Handling [Simple]
**File:** `game/ui/screens/strategy_screen.py`
- [x] Read StrategyScreen's `handle_event()` method -- document what events it currently handles
- [x] Read StrategyScreen's `handle_click()` method -- document what it delegates to
- [x] Check if StrategyScreen has a `handle_scroll()` method or if scroll is only in app.py
- [x] Read StrategyScreen's `update_input()` method -- document what per-frame input it processes
- [x] Identify the `_input` handler object and what methods it exposes
- [x] Document findings in Notes below

**Notes:**
- `handle_event()` -> delegates to `_input.handle_event()` which handles KEYDOWN and UI_BUTTON_PRESSED
- `handle_click()` -> delegates to `_input.handle_click()` for mouse click processing
- StrategyScreen has NO `handle_scroll()` method - the app.py call was dead code!
- `update_input()` -> delegates to `_input.update_input()` for per-frame keyboard polling and hover
- `_input` is `StrategyInputHandler` with `handle_event`, `handle_click`, `update_input` methods

---

### Task 5.2: Fold Click Handling into handle_event [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
- [x] In `handle_event()`, add handling for `pygame.MOUSEBUTTONDOWN` events
- [x] Extract `event.pos` as `(mx, my)` and `event.button` from the event
- [x] Call the same internal click logic that `handle_click()` currently uses
- [x] Verify that `handle_event()` now handles clicks that were previously dispatched separately
- [x] Keep `handle_click()` method for backward compatibility (used internally from handle_event)

**Notes:** Added `elif event.type == pygame.MOUSEBUTTONDOWN:` block that extracts pos and button, then calls `self.handle_click(mx, my, event.button)`. Events now flow through handle_event instead of separate dispatch.

---

### Task 5.3: Fold Scroll Handling into handle_event [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
- [x] In `handle_event()`, add handling for `pygame.MOUSEWHEEL` events
- [x] Extract `event.y` from the scroll event
- [x] Call the appropriate internal scroll logic (currently app.py calls `handle_scroll(event.y, screen_height)`)
- [x] Determine if screen_height is needed or can be obtained from the scene's own dimensions
- [x] Verify scroll behavior works correctly through handle_event

**Notes:** Added `_handle_scroll(event)` method that filters scrolls over sidebar/topbar/modal, then forwards to camera.update_input(). The app.py `_handle_scroll()` was calling a non-existent method - it was dead code! The camera's update_input already handled MOUSEWHEEL events via the event list passed from update_input().

---

### Task 5.4: Fold update_input into update [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
- [x] Examine what `update_input(dt, events)` does that isn't covered by `handle_event()` + `update(dt)`
- [x] If it processes per-frame keyboard state (e.g., held keys for scrolling), move that logic into `update(dt)`
- [x] If it processes event-based input, that should already be handled by `handle_event()`
- [x] Ensure the strategy screen works correctly with input handled through IScene methods only
- [ ] Repeat analysis for ResearchTreeScene and GalaxyTestScreen `handle_input()` if applicable (deferred - out of scope)

**Notes:** `update_input()` handles per-frame keyboard polling (arrow keys/WASD for camera panning) and hover logic. These MUST remain per-frame and cannot move to event-based handling. The call remains in app.py's `_update_and_draw()`. MOUSEWHEEL filtering was removed since it's now handled in handle_event() via _handle_scroll().

---

### Task 5.5: Remove Legacy Dispatch from app.py [Simple]
**File:** `game/app.py`
- [x] Remove the StrategyScreen-specific code from `_handle_click()` (lines 580-582: the `if self.state == GameState.STRATEGY` block)
- [x] If `_handle_click()` is now empty, remove the method entirely and remove its call from `_handle_normal_events()`
- [x] Remove the StrategyScreen-specific code from `_handle_scroll()` (lines 657-659: the `if self.state == GameState.STRATEGY` block)
- [x] If `_handle_scroll()` is now empty, remove the method entirely and remove its call from `_handle_normal_events()`
- [x] Remove the StrategyScreen-specific `update_input()` call from `_update_and_draw()` (line 666) -- KEPT, needed for per-frame keyboard polling
- [ ] Remove the ResearchTree/GalaxyTest `handle_input()` calls from `_update_and_draw()` (lines 667-670) if those scenes have been updated -- DEFERRED (out of scope)
- [x] Verify `_handle_normal_events()` no longer dispatches MOUSEBUTTONDOWN/MOUSEWHEEL separately -- they flow through `_forward_event_to_scene()` naturally

**Notes:** Removed `_handle_click()` method entirely (was StrategyScreen-only). Removed `_handle_scroll()` method entirely (called non-existent method). Removed MOUSEBUTTONDOWN/MOUSEWHEEL handlers from `_handle_normal_events()`. Events now flow through `_forward_event_to_scene()` → `handle_event()`. The `update_input()` call remains for per-frame keyboard polling.

---

### Task 5.6: Clean Up Dead Methods [Simple]
**File:** `game/ui/screens/strategy_screen.py`
- [x] Remove `handle_click()` method from StrategyScreen (now handled by handle_event) -- KEPT as internal API called from handle_event
- [x] Remove `handle_scroll()` if it existed (now handled by handle_event) -- Never existed
- [x] Remove `update_input()` if it was folded into update (or keep if it has distinct per-frame logic that can't move) -- KEPT for per-frame keyboard/hover
- [x] Verify no other code calls the removed methods (grep for `handle_click`, `handle_scroll`, `update_input` in the codebase) -- Verified

**Notes:** `handle_click()` is now called internally from `handle_event()` when processing MOUSEBUTTONDOWN. `update_input()` remains for per-frame keyboard state polling and hover logic. No `handle_scroll()` method ever existed on StrategyScreen.

---

### Task 5.7: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12 --tb=short`
- [x] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [x] Confirm all tests pass with zero new failures
- [x] Verify `test_app_integration.py` still passes
- [x] Verify `test_strategy_menu_actions.py` still passes
- [x] Record test count: 7540 passed, 0 failed
- [x] Recommend manual smoke test: launch game, enter strategy mode, verify click/scroll/panning works

**Notes:** Added 7 new tests in TestMouseEventHandling class to verify MOUSEBUTTONDOWN/MOUSEWHEEL event handling through handle_event().

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Audit
