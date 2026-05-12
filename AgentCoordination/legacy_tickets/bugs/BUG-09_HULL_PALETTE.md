# BUG-09: Hull Components Visible in Component List

## Description
From the recent Refactor: `active_refactor.md`
- The hull components are not supposed to show up in the list of components

## Status
Awaiting Confirmation

## Work Log
| Date | Action |
| :--- | :--- |
| 2026-01-07 | Ticket created via Protocol 01. |
| 2026-01-07 | Phase 1 Reproduction: Created `tests/repro_issues/test_bug_09_hull_in_palette.py`. Test failed as expected, finding 11 hull components in the palette. |
| 2026-01-07 | Phase 2 Fix: Modified `ui/builder/left_panel.py` to filter out components with `type == "Hull"` in `update_component_list()`. |
| 2026-01-07 | Phase 3 Verification: Verified fix with `test_bug_09_hull_in_palette.py` (Passed). Ran regression tests in `tests/unit/builder/` (Passed). |
