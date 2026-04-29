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
Awaiting Confirmation

## Work Log
- 2026-04-28: Created from QA Session 20260428_052952.
- 2026-04-28: Implemented per investigation
  `.agent_reports/deep-dive-session/investigations/FEAT-24_investigation.md`.
  Files modified:
  - `game/ui/screens/new_game_setup_screen.py` — 4 edits (lines 150, 154,
    582, 592) per ticket spec.
  - `tests/unit/ui/test_new_game_setup.py` — added
    `TestNewGameSetupSystemCountDefault` class with two tests asserting
    `build_game_config` default is 5 (TDD red-green: tests authored first,
    confirmed failing 50≠5, then production edits made them pass).
  Test results:
  - Targeted: `pytest tests/unit/ui/test_new_game_setup.py
    tests/unit/ui/screens/test_new_game_setup_extended.py` — 37 passed.
  - Full suite: `pytest tests/` — 15905 passed, 3 skipped (exit 0).
  - Sharded runner (`Tools/test_sharded/test_sharded.py`) reported all 16
    shards FAILED with TOTAL=0 aggregated; investigation showed shards
    completed in 50–90s but no JUnit XML was written to
    `.pytest_cache/shard_results/`. Suspected pre-existing path-handling
    issue in `Tools/test_sharded/test_sharded.py:213-226` where
    `xml_path` (containing `feat+feat-24` worktree path with backslashes)
    is interpolated into an inline Python script via f-string, causing
    escape-sequence corruption. Direct `pytest tests/` is the
    authoritative measurement and shows zero failures.
  Docs updated: None — no `docs/` file references the slider default,
  range, or "default galaxy size" (verified via grep).
