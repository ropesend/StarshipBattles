# FEAT-18: Build queue — add reorder-down arrow button

## Description
Each build queue row in the per-yard build queue panel currently has `+`, `-`,
and `^` (up-arrow) buttons. There is no `v` (down-arrow) to reorder a row
downward. Users can only reorder upward, which forces them to perform the
inverse operation (move every other row up) to push something down.

Add a down-arrow button next to the existing up-arrow with the symmetric
behaviour (swap the row with the one below it). The button is disabled on the
last row.

Reproduced in QA Session 20260427_151244 at 15:46:

[![Build queue rows showing +, -, ^ buttons but no down-arrow](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_154624.png)](../../../tools/qa_observer/session_data/20260427_151244/images/bug_capture_154624.png)

## Required changes
- Build queue per-row layout (likely
  `game/ui/screens/empire_build_queue_window.py` or a row factory) — add a
  down-arrow button with mirror styling/positioning of the up-arrow.
- Queue model — reuse the existing reorder mechanism with index +1.

## Acceptance
- Down-arrow is visible on every row except the last.
- Pressing it swaps the row with the row below.
- Up-arrow is still disabled on the first row.

## Priority
Low

## Status
Pending

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
