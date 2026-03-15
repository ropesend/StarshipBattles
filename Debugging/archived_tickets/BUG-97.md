# BUG-97: Crash when clicking confirmation dialog to clear fleet orders

## Description

The program crashed when I tried to clear the orders for a fleet, it actually occurred when I clicked on the confirmation button.

### Console Output

```
Traceback (most recent call last):
  File "C:\Dev\Starship Battles\launcher.py", line 9, in <module>
    main()
  File "C:\Dev\Starship Battles\game\app.py", line 721, in main
    game.run()
  File "C:\Dev\Starship Battles\game\app.py", line 522, in run
    self._handle_normal_events(events)
  File "C:\Dev\Starship Battles\game\app.py", line 567, in _handle_normal_events
    self._forward_event_to_scene(event)
  File "C:\Dev\Starship Battles\game\app.py", line 584, in _forward_event_to_scene
    self.active_scene.handle_event(event)
  File "C:\Dev\Starship Battles\game\ui\screens\strategy_screen.py", line 222, in handle_event
    self._input.handle_event(event)
  File "C:\Dev\Starship Battles\game\ui\screens\strategy_input_handler.py", line 61, in handle_event
    self.scene.ui.handle_event(event)
  File "C:\Dev\Starship Battles\game\ui\screens\strategy_ui.py", line 331, in handle_event
    self._event_router.route_event(event)
  File "C:\Dev\Starship Battles\game\ui\screens\strategy_event_router.py", line 133, in route_event
    elif self.ui.window_manager.process_confirmation_event(event):
  File "C:\Dev\Starship Battles\game\ui\screens\strategy_window_manager.py", line 589, in process_confirmation_event
    self._pending_confirmation_dialog is not None
AttributeError: 'StrategyWindowManager' object has no attribute '_pending_confirmation_dialog'. Did you mean: 'show_confirmation_dialog'?
```

## Priority

**Critical** — Crash when interacting with confirmation dialog; blocks clearing fleet orders.

## Status (Awaiting Confirmation)

## Work Log

### Phase 0: Architectural Context
**Recent refactors:** PROJ-198 added confirmation dialog support; PROJ-86 extracted StrategyWindowManager from StrategyUI.
**Active projects touching this code:** None active.
**Relevant architecture rules:** All instance attributes must be initialized in `__init__()`.
**Documentation discrepancies:** None — code matches docs.

### Phase 1: Reproduction (Red)
Two tests added to `tests/unit/ui/screens/test_strategy_window_manager.py`:
- `test_init_confirmation_dialog_attributes` — asserts `_pending_confirmation_dialog` and `_pending_confirmation_callback` are initialized to `None`
- `test_process_confirmation_event_no_dialog_shown` — calls `process_confirmation_event()` before any dialog is shown; reproduced the `AttributeError`

### Phase 3: Implementation (Green)
**Root cause:** `_pending_confirmation_dialog` and `_pending_confirmation_callback` were set only inside `show_confirmation_dialog()` but never initialized in `__init__()`. The event router calls `process_confirmation_event()` for every `UI_CONFIRMATION_DIALOG_CONFIRMED` event, including when no confirmation dialog exists yet.

**Fix:** Added initialization of both attributes to `None` in `StrategyWindowManager.__init__()`.

**Files modified:**
- `game/ui/screens/strategy_window_manager.py` — Added `self._pending_confirmation_dialog = None` and `self._pending_confirmation_callback = None` to `__init__()`
- `tests/unit/ui/screens/test_strategy_window_manager.py` — Added 2 regression tests

### Phase 2.5: Design Review
- **Is this what I would build from scratch?** Yes — all attributes should be initialized in `__init__()`.
- **Would I approve this in a code review?** Yes — minimal, correct fix.
- **Root cause or symptom?** Root cause — missing attribute initialization.
- **Readable diff?** Yes — two lines added to `__init__()`.

**Regression:** 1680/1680 UI screen tests pass. No docs updates needed.
