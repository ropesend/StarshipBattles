# BUG-99: "Remove from Fleet" Button in Fleet Report Does Nothing When Clicked

## Description
In the Fleet Report, the "Remove from Fleet" button visually responds to clicks (appears selected) but no ships are actually removed from the fleet. The complete code path exists — button captures click, callback fires, `SplitFleetCommand` is dispatched, and `SplitFleetCommandHandler` validates and processes the request — but the removal doesn't take effect.

The previous investigation (BUG-68 rejection notes from 2026-03-14) noted that the UI callback ignores `ValidationResult` from the command, so validation failures are silent. This may be causing the issue: if the command fails validation (e.g., attempting to remove the last/only ship), there is no error feedback to the user.

### Potential causes to investigate:
1. Command validation failure with silent error (no user feedback)
2. Event routing issue — button press event may not reach the handler
3. `SplitFleetCommand` dispatch may not reach `GameSession.handle_command()` correctly

The fix should also ensure that validation errors from the command are surfaced to the user.

### Key files:
- `game/ui/panels/ship_detail_panel.py` — button definition and click handler
- `game/ui/screens/fleet_report_window.py` — `_on_remove_ship()` callback
- `game/ui/screens/strategy_window_manager.py` — `split_fleet_callback` setup
- `game/strategy/engine/command_handlers.py` — `SplitFleetCommandHandler`

## Priority
Medium

## Status
Awaiting Confirmation

## Investigation Report

### Code Path Trace
```
User clicks "Remove from Fleet" button
  → ShipDetailPanel.process_event() [ship_detail_panel.py:418]
    → Checks event.type == pygame.USEREVENT AND event.user_type == 'ui_button_pressed' [line 429-430]
    → ❌ NEVER MATCHES — pygame_gui 0.6.x uses pygame_gui.UI_BUTTON_PRESSED event type
    → Callback never fires, _on_remove_ship() never called
```

### Root Cause: Wrong Event Type Check (CONFIRMED)

`ship_detail_panel.py` (line 429-430) and `fleet_report_window.py` (line 176-177) use the **deprecated pygame_gui event API**:
```python
if event.type == pygame.USEREVENT:
    if hasattr(event, 'user_type') and event.user_type == 'ui_button_pressed':
```

Every other button handler in the codebase (30+ instances) uses the correct API:
```python
if event.type == pygame_gui.UI_BUTTON_PRESSED:
```

In pygame_gui 0.6.x, button press events are dispatched as `pygame_gui.UI_BUTTON_PRESSED`, not `pygame.USEREVENT`. The old `user_type` string-based API was from pre-0.6 versions. The condition never matches, so the remove button callback is never invoked.

### Secondary Issue: ValidationResult Not Checked

Even after fixing the event type, a second issue exists:
- `strategy_window_manager.py:359` — `split_fleet_callback` ignores `ValidationResult`
- `fleet_report_window.py:261-262` — `_post_removal_refresh()` runs unconditionally
- If command validation fails (e.g., removing last ship), user gets no error feedback

### Dependency Map
**Callers of _on_remove_ship:** ShipDetailPanel.process_event() via on_remove_ship callback
**Callees of _on_remove_ship:** split_fleet_callback → facade.handle_command → SplitFleetCommandHandler.execute

### Similar Patterns Found
All 30+ button handlers use `pygame_gui.UI_BUTTON_PRESSED` correctly. Only `ship_detail_panel.py` and `fleet_report_window.py` use the broken `pygame.USEREVENT` + `user_type` pattern.

### Git History Analysis
The old event pattern was introduced during PROJ-03/PROJ-208 development. The rest of the codebase was migrated to `pygame_gui.UI_BUTTON_PRESSED` but these two files were missed.

### Documentation Discrepancies
None — code vs docs is consistent. The bug is purely a pygame_gui API usage error.

## User Context

**Reproduction Steps:**
1. Open Fleet Report for any fleet with 2+ ships
2. Select a ship in the list
3. Click "Remove from Fleet" button

**Expected Behavior:** Ship removed from fleet, new fleet-of-one created at same location
**Actual Behavior:** Nothing happens — no visual change, no fleet modification
**History:** Never worked (feature added with wrong event API from the start)
**Consistency:** Always fails, regardless of fleet size
**Game State:** Any fleet with 2+ ships selected in Fleet Report
**Known Workarounds:** None

## Hypothesis Log

### Hypothesis 1: Wrong Event Type — CONFIRMED
**Theory:** `ship_detail_panel.py` checks for `pygame.USEREVENT` + `user_type == 'ui_button_pressed'` but pygame_gui 0.6.x dispatches button events as `pygame_gui.UI_BUTTON_PRESSED`
**Evidence For:** 30+ other button handlers in the codebase use `pygame_gui.UI_BUTTON_PRESSED` correctly; user confirms button ALWAYS fails; user confirms NOTHING happens (callback never fires)
**Evidence Against:** None
**Test:** Change event check to `pygame_gui.UI_BUTTON_PRESSED` and verify button works
**Result:** CONFIRMED — this is the root cause

### Hypothesis 2: Command Validation Failure (Silent) — SECONDARY
**Theory:** SplitFleetCommandHandler rejects command but result is ignored
**Evidence For:** Callback doesn't return/check ValidationResult; _post_removal_refresh runs unconditionally
**Evidence Against:** User has 2-5 ship fleets (not single-ship), so "at least one ship must remain" check should pass
**Test:** After fixing Hypothesis 1, test with single-ship fleet to verify error feedback
**Result:** SECONDARY ISSUE — needs fix but not the primary cause

## Work Log
- 2026-03-22: Created from QA Session 20260322_051459. Split from BUG-68 (ship selection confirmed fixed, archived).
- 2026-03-22: Deep dive investigation. Root cause: wrong pygame_gui event type check (deprecated API). Secondary: ValidationResult not checked.
- 2026-03-22: Fix applied. Changes:
  - `game/ui/panels/ship_detail_panel.py`: Changed `pygame.USEREVENT` + `user_type` check to `pygame_gui.UI_BUTTON_PRESSED` (matching all 30+ other button handlers in codebase)
  - `game/ui/screens/fleet_report_window.py`: Same event type fix for header click handling; added ValidationResult checking in `_on_remove_ship()` and `_on_remove_selected_ships()` with logging on failure; added `logging` and `pygame_gui` imports; removed unused `SplitFleetCommand` import
  - `game/ui/screens/strategy_window_manager.py`: `split_fleet_callback` now returns `ValidationResult` from `facade.handle_command()`
  - `tests/unit/ui/panels/test_ship_detail_panel.py`: Updated event tests to use `pygame_gui.UI_BUTTON_PRESSED`
  - All 92 affected tests pass. No docs updates needed (bug was API usage error, not architectural).
