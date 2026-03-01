# PROJ-216: Fix Global Fleet Order Registration Failure

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-216` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-216 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Diagnostic Logging | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Fix Click Gate | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fix Confirmation Dialog Flow | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Integration Tests | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-28
**Active Phase:** Phase 2 (Fix Click Gate)
**Last Action:** Phase 1 complete - diagnostic logging added
**Next Action:** Phase 2 - Replace get_hovering_any_element() with explicit window check
**Blockers:** None
**Test Baseline:** 13,091 passed, 1 skipped

## Overview

ALL fleet orders (move, colonize, stellerate star, etc.) fail to register in the order queue. The user can select fleets, enter input modes (press M for move, etc.), see path preview lines, and even get confirmation dialogs - but confirming never results in an order being added to the fleet's queue. This is 100% reproducible on every new game.

**Root Cause:** `strategy_event_router.py:271` uses `pygame_gui.UIManager.get_hovering_any_element()` as a click gate. This method returns True when the mouse is over ANY registered UI element, including hidden/invisible elements (buttons with `visible=0`, UIImage with empty surfaces, container panels). When it returns True, ALL map clicks are consumed and never reach the `ClickModeDispatcher`, so no orders are ever dispatched.

A secondary issue exists in the confirmation dialog flow: even if map clicks reach the dispatcher for superweapon targeting, the confirmation callback may not execute because the click-gate fires when the dialog is open.

## Goals
- Fix the click gate so map clicks reach the ClickModeDispatcher correctly
- Ensure confirmation dialog callbacks execute properly
- Add diagnostic logging so similar issues are visible at runtime
- Add integration tests to prevent regression

## Scope
**In:**
- Fix `get_hovering_any_element()` click-gate in `strategy_event_router.py`
- Fix confirmation dialog event flow
- Add diagnostic logging to click dispatch chain
- Add integration tests for click-to-order pipeline

**Out:**
- Galaxy registry fleet cleanup (identified by data flow agent but is a separate issue)
- Refactoring the entire event handling architecture
- Changes to the command handler registry or GameSession internals

## Key Files
| Component | File Path |
|-----------|-----------|
| Click Gate (BUG SITE) | `game/ui/screens/strategy_event_router.py` |
| Input Handler | `game/ui/screens/strategy_input_handler.py` |
| Click Dispatcher | `game/ui/screens/strategy_click_dispatcher.py` |
| Fleet Operations | `game/ui/screens/strategy_fleet_ops.py` |
| Superweapon Ops | `game/ui/screens/strategy_superweapons.py` |
| Window Manager | `game/ui/screens/strategy_window_manager.py` |
| Panel Manager | `game/ui/screens/strategy_panel_manager.py` |
| Strategy UI | `game/ui/screens/strategy_ui.py` |
| Triage File | `Projects/active_projects/PROJ-216/findings/global_orders_registration.md` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/global_orders_registration.md](findings/global_orders_registration.md) - Original triage report with screenshots

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-28 | Replace `get_hovering_any_element()` with explicit modal/window check | The pygame_gui method is too broad - it catches hidden/invisible elements. We should only block clicks when actual modal windows or interactive panels are under the cursor. |
| 2026-02-28 | Add diagnostic logging before implementing fix | Need to confirm the hypothesis at runtime before committing to a fix approach. |
| 2026-02-28 | Scope galaxy registry cleanup out | Data flow agent found missing `galaxy.unregister_fleet()` calls in fleet_order_processor.py, but this is a separate bug that doesn't cause the 100% order failure. |

## Initial Analysis

### The Click Dispatch Chain
```
StrategyInputHandler.handle_event() (line 66-83)
  ├── scene.ui.handle_event(event)           → processes pygame_gui events
  └── handle_click(mx, my, button) (line 134-147)
       ├── scene.ui.handle_click(mx, my, button)  → GATE (returns True = consumed)
       │    └── StrategyEventRouter.handle_click() (line 254-274)
       │         ├── Check sidebar area (x > width - sidebar_width) → True = consumed
       │         └── get_hovering_any_element() → True = consumed  ← BUG HERE
       └── ClickModeDispatcher.dispatch_click() → routes to mode handler
            ├── MOVE → fleet_ops.handle_move_designation() → execute_move()
            ├── COLONIZE_TARGET → colonization.handle_colonize_designation()
            ├── STELLERATE_STAR_TARGET → superweapons.handle_stellerate_star_designation()
            └── SELECT → _handle_picking()
```

### Why `get_hovering_any_element()` Breaks Everything

The strategy screen creates ~30 UI elements, of which **9 are hidden/invisible** but still registered with pygame_gui's UIManager:
- `portrait_image` (UIImage with empty surface)
- `graph_image` (UIImage with empty surface)
- `btn_raw_data` (explicitly hidden via `.hide()`)
- `btn_colonize` (created with `visible=0`)
- `btn_build_yard` (created with `visible=0`)
- `btn_orders` (created with `visible=0`)
- `btn_fleet_report` (created with `visible=0`)
- `btn_build_fleet` (created with `visible=0`)
- `detail_text` (hidden in initial state)

Additionally, the top_bar panel (height 50px, full width minus sidebar) and resource_bar panel (height 24px) span the entire non-sidebar area and their container UIPanel elements may have hover rects that extend beyond their visual bounds due to pygame_gui's internal margin/padding.

### User's Description
> "I press m, then a path is drawn between my mouse cursor to the fleet, when I left click to select a sector no order is queued, and the line continues to show unless I press esc. Clearly the star destroyer registers the mouse click, since the warning dialog shows, but there is no indication that the order is placed into the queue."

This confirms the hypothesis: the MOVE mode is entered (M key works via keyboard handler, not click handler), the path preview renders correctly (path preview uses mouse position, not clicks), but the left-click to confirm the destination never reaches `ClickModeDispatcher`.

## Swarm Findings Summary

### Architecture (Agent: a14c921)
- Complete UI element inventory documented (~30 elements, 9 hidden)
- Confirmed `get_hovering_any_element()` is the sole click gate
- All hidden elements still registered in UIManager's element list
- Recommended whitelist approach for blocking UI elements

### Test Impact (Agent: a49e164)
- **CRITICAL GAP**: Zero integration tests for the click-to-order pipeline
- Unit tests mock every layer boundary, so individual components pass but the chain is untested
- Existing tests: `test_strategy_input_handler_core.py` (mocks fleet_ops), `test_strategy_fleet_ops_facade.py` (mocks facade), `test_command_handlers.py` (creates commands directly)
- Need: End-to-end test that verifies clicking the map registers an order

### Risk Assessment (Agent: abd48b1)
- Primary risk: Hidden button hover rects (visible=0 still hit-testable in pygame_gui)
- Secondary risk: UIPanel container margins extending hover areas
- Tertiary risk: Tooltip persistence after mouse leaves buttons
- All risks stem from the same root: `get_hovering_any_element()` is too broad

### Data Flow (Agent: a156148)
- Found separate issue: `fleet_order_processor.py` calls `empire.remove_fleet()` in 3 places without calling `galaxy.unregister_fleet()` (lines 113, 216, 649)
- This causes orphaned fleet references but does NOT cause the 100% order failure
- The superweapon processor does it correctly (calls both) - scoped out for a separate fix

### Pattern Scout (Agent: ac34af2)
- Identified confirmation dialog flow as a secondary issue
- When UIConfirmationDialog is created, it registers as a UI element, causing `get_hovering_any_element()` to return True
- The confirmation event (`UI_CONFIRMATION_DIALOG_CONFIRMED`) is processed in `route_event()` (line 129-134), NOT in `handle_click()`, so this path works independently
- However, any clicks AFTER dialog dismissal may still be blocked if stale elements remain

### Dependency Mapper (Agent: a46f5b4)
- Full initialization chain mapped from app.py through GameSession to StrategyScreen
- Facade is correctly wired: each sub-module captures facade at init, all point to same session
- No stale facade risk in normal new-game flow (only possible after load-game replaces session)
- `create_default_registry()` correctly imports and registers all 25+ handlers

### Risks Identified
1. **Primary**: `get_hovering_any_element()` blocks ALL map clicks
2. **Secondary**: Confirmation dialog elements persist in UIManager after creation
3. **Out of scope**: Missing `galaxy.unregister_fleet()` calls in fleet_order_processor.py

---

## Phases

### Phase 1: Diagnostic Logging [Simple]
**Objective:** Add temporary diagnostic logging to confirm the root cause at runtime before implementing the fix.
**Status:** Complete

#### Task 1.1: Add diagnostic log to click gate [Simple]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/strategy/ -k "event_router" --testmon`
- [ ] Add `import logging; logger = logging.getLogger(__name__)` at top of file if not present
- [ ] Add diagnostic logging inside `handle_click()` method (line 254-274):
  ```python
  def handle_click(self, mx: int, my: int, button: int) -> bool:
      # 1. Check logical sidebar area
      if mx > self.ui.width - self.ui.sidebar_width:
          return True

      # 2. Check if ANY UI element is being hovered
      hovering = self.ui.manager.get_hovering_any_element()
      if hovering:
          logger.debug(f"Click at ({mx},{my}) BLOCKED by UI hover check")
          return True

      return False
  ```
- [ ] Verify no existing tests break
**Notes:**

#### Task 1.2: Add diagnostic log to click dispatcher entry [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/strategy/ -k "input_handler" --testmon`
- [ ] Add logging to `handle_click()` method (line 134-147):
  ```python
  def handle_click(self, mx, my, button):
      ui_handled = self.scene.ui.handle_click(mx, my, button)
      if ui_handled:
          logger.debug(f"Click at ({mx},{my}) consumed by UI layer")
          return True
      logger.debug(f"Click at ({mx},{my}) reaching dispatcher, mode={self.input_mode}")
      return self._click_dispatch.dispatch_click(mx, my, button)
  ```
- [ ] Verify no existing tests break
**Notes:**

#### Task 1.3: Manual runtime verification [Simple]
**Tests:** Manual test - launch game, open console log, click on map
- [ ] Start new game
- [ ] Select a fleet, press M
- [ ] Click on a destination hex
- [ ] Check console output: confirm "BLOCKED by UI hover check" message appears
- [ ] Document which elements are triggering the false positive
**Notes:**

---

### Phase 2: Fix Click Gate [Medium]
**Objective:** Replace the overly broad `get_hovering_any_element()` check with a targeted check that only blocks clicks when actual modal windows or interactive overlays are under the cursor.
**Status:** Not Started

#### Task 2.1: Replace `get_hovering_any_element()` with explicit window check [Medium]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/strategy/ --testmon`
- [ ] Replace the current click gate logic (lines 269-272) with explicit modal/window checks:
  ```python
  def handle_click(self, mx: int, my: int, button: int) -> bool:
      # 1. Check logical sidebar area
      if mx > self.ui.width - self.ui.sidebar_width:
          return True

      # 2. Check if mouse is over an active modal/window that should block map clicks
      if self._is_blocking_ui_element_at(mx, my):
          return True

      return False
  ```
- [ ] Add `_is_blocking_ui_element_at()` method to StrategyEventRouter:
  ```python
  def _is_blocking_ui_element_at(self, mx: int, my: int) -> bool:
      """Check if a blocking UI element (modal window, menu panel) is at the given position.

      Only actual interactive overlays should block map clicks - NOT hidden buttons,
      container panels, or decorative elements.
      """
      wm = self.ui.window_manager
      # Check active windows that should block clicks
      blocking_windows = [
          wm.fleet_orders_window,
          wm.planet_list_window,
          wm._pending_confirmation_dialog,
      ]
      for window in blocking_windows:
          if window is not None and window.alive() and window.rect.collidepoint((mx, my)):
              return True

      # Check menu panel
      if self.ui.menu_panel is not None:
          if self.ui.menu_panel.get_abs_rect().collidepoint((mx, my)):
              return True

      # Check top bar and resource bar (they are above the map)
      if hasattr(self.ui, 'top_bar') and self.ui.top_bar.rect.collidepoint((mx, my)):
          return True
      if hasattr(self.ui, 'resource_bar') and self.ui.resource_bar.rect.collidepoint((mx, my)):
          return True

      return False
  ```
- [ ] Verify the method correctly checks all windows that should block
**Notes:** The exact attribute names for windows on `window_manager` need to be verified at implementation time. Check `strategy_window_manager.py` for the actual attribute names.

#### Task 2.2: Add unit tests for the new click gate [Medium]
**File:** `tests/unit/ui/strategy/test_strategy_event_router.py` (new or existing)
**Tests:** `pytest tests/unit/ui/strategy/ -k "event_router" --testmon`
- [ ] Test: click on map area with no windows open → returns False (click passes through)
- [ ] Test: click on sidebar area → returns True (blocked)
- [ ] Test: click on map area with fleet_orders_window open and at that position → returns True
- [ ] Test: click on map area with confirmation dialog open at that position → returns True
- [ ] Test: click on top_bar area → returns True (blocked)
- [ ] Test: click on map area with hidden buttons (btn_colonize visible=0) → returns False (NOT blocked)
**Notes:** Use MagicMock for window_manager and ui elements.

#### Task 2.3: Remove diagnostic logging from Phase 1 [Simple]
**File:** `game/ui/screens/strategy_event_router.py`, `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/strategy/ --testmon`
- [ ] Remove the diagnostic `logger.debug` calls added in Phase 1 (keep the logger import if needed for permanent logging)
- [ ] Or convert to permanent debug-level logging if desired (user decision)
**Notes:**

---

### Phase 3: Fix Confirmation Dialog Flow [Simple]
**Objective:** Ensure confirmation dialog callbacks execute correctly regardless of the click gate.
**Status:** Not Started

#### Task 3.1: Verify confirmation events are processed via `route_event()` [Simple]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/unit/ui/strategy/ --testmon`
- [ ] Verify that `UI_CONFIRMATION_DIALOG_CONFIRMED` events reach `route_event()` line 129-134
- [ ] Verify that `route_event()` is called from `handle_event()` in `strategy_input_handler.py` line 66 (via `scene.ui.handle_event(event)`)
- [ ] Confirm that the confirmation flow does NOT depend on `handle_click()` - it goes through the `handle_event()` → `route_event()` path instead
- [ ] If confirmation flow is already independent of the click gate (likely), document this and mark task complete
**Notes:** The Pattern Scout agent suggested this might be a secondary issue, but the event flow analysis shows that `UI_CONFIRMATION_DIALOG_CONFIRMED` is a pygame_gui event processed in `route_event()`, not in `handle_click()`. The Phase 2 fix should be sufficient.

#### Task 3.2: Test superweapon confirmation end-to-end [Simple]
**Tests:** Manual test - launch game, test stellerate star confirmation
- [ ] Start new game, select fleet with stellerate star ability
- [ ] Press Ctrl+Shift+S, click on a star
- [ ] Verify confirmation dialog appears
- [ ] Click "Confirm" in dialog
- [ ] Verify order appears in fleet's order queue
**Notes:** This tests the full superweapon confirmation flow after the Phase 2 fix.

---

### Phase 4: Integration Tests [Medium]
**Objective:** Add integration tests to prevent regression of the click-to-order pipeline.
**Status:** Not Started

#### Task 4.1: Create click gate integration test [Medium]
**File:** `tests/unit/ui/strategy/test_click_gate_integration.py` (new)
**Tests:** `pytest tests/unit/ui/strategy/test_click_gate_integration.py`
- [ ] Create test class `TestClickGateIntegration`
- [ ] Test: `test_map_click_not_blocked_by_hidden_buttons` - Create StrategyUI with hidden buttons, verify `handle_click()` returns False for map area coordinates
- [ ] Test: `test_map_click_blocked_by_confirmation_dialog` - Create dialog, verify clicks on dialog area are blocked
- [ ] Test: `test_sidebar_click_always_blocked` - Verify clicks in sidebar area return True
- [ ] Test: `test_top_bar_click_blocked` - Verify clicks in top bar area return True
**Notes:** Uses real pygame_gui UIManager with actual element creation.

#### Task 4.2: Create move order end-to-end test [Medium]
**File:** `tests/integration/ui/test_move_order_registration.py` (new)
**Tests:** `pytest tests/integration/ui/test_move_order_registration.py`
- [ ] Create test class `TestMoveOrderRegistration`
- [ ] Test: `test_move_command_reaches_game_session` - Create FleetOperations with real facade and GameSession, call `execute_move()`, verify `fleet.orders` contains a MOVE order
- [ ] Test: `test_click_dispatcher_routes_move_to_fleet_ops` - Create ClickModeDispatcher in MOVE mode, simulate click, verify fleet_ops.handle_move_designation() is called
**Notes:** These tests bypass the UI click gate (already tested in 4.1) and test the command dispatch chain.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - 13,040 passed, 1 skipped (baseline established)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Manual test: start new game, select fleet, press M, click destination → order registered
- [ ] Manual test: stellerate star confirmation dialog → order registered after confirm

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] Manual test: all order types work (move, colonize, join, stellerate, implode, etc.)
- [ ] Verify no UI regressions (sidebar clicks still blocked, top bar still clickable, modals still block map)

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
