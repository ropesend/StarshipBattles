# FEAT-20: Dev "Run 10 turns" button next to End Turn

## Description
Add a development button next to **End Turn** that automatically advances the
turn 10 times in a row. Each iteration runs the full end-turn flow for every
player (using whatever fleet orders / build queues are already configured)
until 10 turns have completed.

Purpose: faster iteration when testing economy / population / build queue
behaviour over multiple turns. Intended as a dev-time shortcut — to be
removed (or hidden behind a debug flag) before release.

Reproduced layout in QA Session 20260427_151244 at 15:52:

[![End Turn button location — Run 10 Turns belongs immediately to its right](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_155251.png)](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_155251.png)

## Required changes
- Strategy UI top bar — add "Run 10 Turns" button immediately next to "End
  Turn" (likely in `game/ui/screens/strategy_*` or
  `game/ui/screens/strategy_window_manager.py`).
- Click handler — calls the existing end-turn pipeline 10 times in sequence.
  No animations / pauses between turns; spinner or progress indicator while
  running.
- **Gate the button behind a dev flag** so it's easy to hide in builds. A
  config switch or a debug-mode environment variable is fine.
- Cancel/abort affordance — long sequences shouldn't lock the UI; allow Esc
  or a Cancel modal to stop after the current turn finishes.

## Acceptance
- Button is visible next to End Turn while in dev mode.
- Clicking advances the simulation 10 turns; UI updates between/after.
- A cancellation path stops cleanly without corrupting the save.

## Out of scope
- Configurable turn count (10 is fine for dev needs).
- Replaying or recording the run.

## Priority
Low

## Status
Pending

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
