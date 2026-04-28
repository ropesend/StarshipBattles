# FEAT-17: Build queue pause/unpause toggle button

## Description
Add a "Pause Build Queue" button at the bottom-left of the build queue panel
(Build Yards view, per-planet/per-sector). When pressed:
- The queue stops consuming any resources for the affected yard.
- The button label flips to "Unpause Build Queue".
- The currently-progressing item retains its accumulated progress
  (no rollback).
- Pressing Unpause resumes consumption from the saved progress on the next
  turn tick.

The queue's order, contents, and reorder up/down arrows remain operable while
paused.

Reproduced layout in QA Session 20260427_151244 at 15:42:

[![Empty per-yard build queue panel — "Verona I - Planetary Yard"](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_154228.png)](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_154228.png)

## Required changes
- `game/ui/screens/empire_build_queue_window.py` (or per-yard build queue panel
  file) — add the toggle button at bottom-left.
- `game/strategy/` build yard / queue model — add a `paused: bool` flag per
  yard. Resource-consumption tick respects the flag.
- Save/load — serialise the paused flag with the queue state.

## Acceptance
- Toggle button visible and functional on every per-yard build queue panel.
- Paused yard consumes 0 resources per turn while paused.
- Toggle persists across save/load.
- Resuming continues progress from where it left off (no progress reset).

## Priority
Medium

## Status
Pending

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
