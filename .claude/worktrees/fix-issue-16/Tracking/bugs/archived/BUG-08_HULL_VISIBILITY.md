# BUG-08: Hull Visible in Ship Structure List

## Description
From the recent Refactor: `active_refactor.md`
- In the Ship Builder View
- The hull is not supposed to show up in the list of ship Structure. It should automatically be included as part of the ship's components but, it should be hidden from the user.

## Status
Pending

## Work Log
| Date | Action |
| :--- | :--- |
| 2026-01-07 | Ticket created via Protocol 01. |
| 2026-01-07 | Phase 1: Reproduction. Created `tests/repro_issues/test_bug_08_hull_visible.py`. Test confirmed failure. |
| 2026-01-07 | Phase 2: The Fix. Modified `ui/builder/layer_panel.py` to filter out components starting with `hull_`. |
| 2026-01-07 | Phase 3: Verification. Reproduction test passed. Regression tests passed. Status updated to Awaiting Confirmation. |
