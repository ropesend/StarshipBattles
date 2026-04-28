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
Awaiting Confirmation

## Work Log
- 2026-04-27: Created from QA Session 20260427_151244.
- 2026-04-27: Implemented (investigator-feat-18).

  **Layout-clipping bug discovered during re-investigation: actions column
  width was 100 px, needed 145 px for 4 buttons. Down button was rendered
  but overpainted by adjacent portrait. Width bumped to 150 + edge-disable
  added.**

  Layout math: 4 buttons × 30 px + 3 spacers × 5 px + 2 × 5 px padding =
  145 px minimum. The down-arrow `v` was created at x = 110..140 inside
  the actions cell that ended at x = 100, overlapping into the portrait
  column (x = 100..150) and being overdrawn by the portrait `UIImage`
  widget (created in the next loop iteration of the same `row_bg`
  parent, so painted on top by pygame_gui's creation-order draw rule).

  Files modified:
  - `game/ui/screens/build_queue_queue_data_source.py` — actions column
    width 100 → 150 (1 line).
  - `game/ui/components/table/virtual_table.py` — replaced no-op
    `elif widget["type"] == "actions": pass` in `update_visible_rows`
    with enable/disable logic for up button on row 0 and down button on
    last row (12 LOC).
  - `tests/unit/ui/components/table/test_virtual_table.py` —
    parametrised `test_update_visible_rows_disables_edge_action_buttons`
    on a 3-row queue (first/middle/last/single-row cases).
  - `tests/unit/ui/screens/test_build_queue_queue_data_source.py` —
    `test_actions_column_wide_enough_for_four_buttons` regression guard
    asserting width >= 145.

  Test results: 5 new tests pass; 621 build-queue + table unit and
  integration tests pass; full sharded suite shows 15 unrelated
  pre-existing failures in `test_strategy_detail_fmt.py` from FEAT-19
  in-flight `SpeciesDemographicView` / `food_surplus` work — NOT caused
  by this change.
