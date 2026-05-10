# BUG-13: Ship Builder - Clear Design Removes Hull

## Description
Ship Builder:
Clear design, should not remove the hull component. currently it does.

## Status
[Awaiting Confirmation]

## Work Log
- 2026-01-09: Ticket created.
- 2026-01-09: Phase 1: Reproduction. Created `tests/repro_issues/test_bug_13_clear_removes_hull.py`. Test confirmed failure.
- 2026-01-09: Phase 2: The Fix. Modified `game/ui/screens/builder_screen.py`. Updated `_clear_design` to skip `LayerType.HULL` when clearing layers. This ensures the mandatory hull component is preserved while all user-added components are removed.
- 2026-01-09: Phase 3: Verification. Reproduction test `tests/repro_issues/test_bug_13_clear_removes_hull.py` now passes. Regression tests in `tests/unit/builder/test_builder_logic.py` also pass.


