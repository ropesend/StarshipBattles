# FEAT-24: Default new-game galaxy size to 5 systems

## Description
Lower the default galaxy size on the New Game Setup screen from 50
systems to 5 systems so first-time and iteration runs start with a tiny
galaxy. Also lower the slider's minimum from 25 to 5 so the slider can
actually represent the new default.

The user wants a small default for fast iteration. The full slider
range stays available for users who want a larger galaxy.

## Required changes

In [game/ui/screens/new_game_setup_screen.py](../../../game/ui/screens/new_game_setup_screen.py):
- Line 150: `self.system_count = 50  # Default` → `self.system_count = 5  # Default`
- Line 154: slider `value_range=(25, 150)` → `value_range=(5, 150)`
- Line 582: `build_game_config(..., system_count: int = 50)` → `= 5`
- Line 592: docstring `"default: 50"` → `"default: 5"`

Also audit `tests/unit/ui/screens/test_new_game_setup*.py` and any
related fixtures for hardcoded `50` / `25` assertions on the system
count default and slider minimum, and update them to match.

## Acceptance
- Opening the New Game Setup screen shows the system count slider
  positioned at 5.
- The slider can be dragged from 5 to 150.
- Starting a new game without changing the slider produces a 5-system
  galaxy.

## Out of scope
- Persisting the user's last-chosen value across runs.
- Adding presets ("Tiny / Small / Medium / Large").
- Changing the click_increment (currently 5).

## Priority
Low (developer ergonomics — speeds up iteration)

## Status
Pending

## Work Log
- 2026-04-28: Created from QA Session 20260428_052952.
