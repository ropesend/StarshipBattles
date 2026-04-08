## Description
I can't give orders to newly constructed shiops: PS C:\Dev\Starship Battles> python launcher.py
pygame-ce 2.5.6 (SDL 2.32.10, Python 3.10.11)
WARNING: StaticTargetScenario in beam_scenarios.py has no metadata
WARNING: PropulsionScenario in propulsion_scenarios.py has no metadata
WARNING: StaticTargetScenario in seeker_scenarios.py has no metadata
WARNING: DuelScenario in templates.py has no metadata
WARNING: PropulsionScenario in templates.py has no metadata
WARNING: StaticTargetScenario in templates.py has no metadata
INFO: Discovered 51 scenarios
INFO: Loaded 25 test histories from C:\Dev\Starship Battles\combat_lab\test_history.json
INFO: 
=== Static Validation: Checking test metadata against component data ===
INFO:   BEAMWEAPON-010: 4 pass, 1 fail, 0 warn
INFO:   BEAMWEAPON-009: 4 pass, 1 fail, 0 warn
INFO:   PROP-001: Could not build validation context
INFO:   PROP-001b: Could not build validation context
INFO:   PROP-002: Could not build validation context
INFO:   PROP-003b: Could not build validation context
INFO:   PROP-004: Could not build validation context
INFO:   PROP-003: Could not build validation context
INFO: === Static Validation Complete ===

C:\Users\rossr\AppData\Local\Programs\Python\Python310\lib\site-packages\pygame_gui\core\ui_font_dictionary.py:405: UserWarning: Finding font with id: noto_sans_bold_aa_14 that is not already loaded.
Preload this font with {'name': 'noto_sans', 'point_size': 14, 'style': 'bold', 'antialiased': '1'}
  warnings.warn(warning_string, UserWarning)
C:\Users\rossr\AppData\Local\Programs\Python\Python310\lib\site-packages\pygame_gui\elements\ui_label.py:176: UserWarning: Label Rect is too small for text: Total Maneuvering Points: - size diff: (-5, 0)
  warnings.warn(warn_text, UserWarning)
C:\Users\rossr\AppData\Local\Programs\Python\Python310\lib\site-packages\pygame_gui\elements\ui_label.py:176: UserWarning: Label Rect is too small for text: 1 turns remaining | Type: complex - size diff: (-34, 0)
  warnings.warn(warn_text, UserWarning)
C:\Users\rossr\AppData\Local\Programs\Python\Python310\lib\site-packages\pygame_gui\elements\ui_label.py:176: UserWarning: Label Rect is too small for text: 1 turns remaining | Type: ship - size diff: (-6, 0)
  warnings.warn(warn_text, UserWarning)
Traceback (most recent call last):
  File "C:\Dev\Starship Battles\launcher.py", line 9, in <module>
    main()
  File "C:\Dev\Starship Battles\game\app.py", line 581, in main
    raise e
  File "C:\Dev\Starship Battles\game\app.py", line 573, in main
    game.run()
  File "C:\Dev\Starship Battles\game\app.py", line 326, in run
    self._handle_normal_events(events)
  File "C:\Dev\Starship Battles\game\app.py", line 361, in _handle_normal_events
    self._handle_click(event)
  File "C:\Dev\Starship Battles\game\app.py", line 430, in _handle_click
    self.strategy_scene.handle_click(mx, my, event.button)
  File "C:\Dev\Starship Battles\game\ui\screens\strategy_scene.py", line 176, in handle_click
    return self._input.handle_click(mx, my, button)
  File "C:\Dev\Starship Battles\game\ui\screens\strategy_input_handler.py", line 126, in handle_click
    return self._handle_move_mode_click(mx, my, button)
  File "C:\Dev\Starship Battles\game\ui\screens\strategy_input_handler.py", line 165, in _handle_move_mode_click
    self._finish_move_action(result['fleet'])
  File "C:\Dev\Starship Battles\game\ui\screens\strategy_input_handler.py", line 269, in _finish_move_action
    self.scene.on_ui_selection(fleet)
  File "C:\Dev\Starship Battles\game\ui\screens\strategy_scene.py", line 313, in on_ui_selection
    self.ui.show_detailed_report(obj, img)
  File "C:\Dev\Starship Battles\game\ui\screens\strategy_screen.py", line 508, in show_detailed_report
    if order.type == OrderType.MOVE:
NameError: name 'OrderType' is not defined

## Status
Awaiting Confirmation

## Work Log
- 2026-01-20: Ticket created by Project Manager.

### 2026-01-20 - Phase 1: Reproduction (Red)

**Test File Created:** `tests/repro_issues/test_bug_27_ordertype.py`

**Error Trace Analysis:**
```
File "C:\Dev\Starship Battles\game\ui\screens\strategy_screen.py", line 508, in show_detailed_report
    if order.type == OrderType.MOVE:
NameError: name 'OrderType' is not defined
```

**Root Cause:** `OrderType` enum is used in `show_detailed_report()` method at lines 508, 510, and 515 to display fleet orders, but `OrderType` was never imported from `game.strategy.data.fleet`.

---

### 2026-01-20 - Phase 2: The Fix (Green)

**File Modified:** `game/ui/screens/strategy_screen.py`

**Changes Made (line 10):**
Added missing import:
```python
from game.strategy.data.fleet import OrderType
```

**Test Results:**
```
======================== 3 passed in 1.76s ========================
```

**Regression Tests:**
```
tests/ui/test_strategy_buttons.py - 4 passed
```

All tests pass with no regressions.
