# BUG-10: Hull Components Missing Required Abilities

## Description
From the recent Refactor: `active_refactor.md`
- All hull components should include a requirement for command and control
- All ship and fighter hulls should include a requirement for combat propulsion

## Status
Pending

## Work Log
| Date | Action |
| :--- | :--- |
| 2026-01-07 | Ticket created via Protocol 01. |
| 2026-01-07 |- Phase 1: Analyzed hull and ship logic. Discovered missing baseline abilities. Created reproduction test.
- Phase 2: Implemented `CommandAndControl` and `CombatPropulsion` on hulls. Passed tests.
- Phase 3: **Correction Phase.** Per User feedback, moved to **Requirement Abilities** pattern.
    - Created `RequiresCommandAndControl` and `RequiresCombatMovement` in `abilities.py`.
    - Updated `ship_validator.py` to enforce these markers.
    - Updated `ship_stats.py` to correctly tally marker abilities.
    - Reverted manual requirements in `vehicleclasses.json`.
    - Verified all 31 regression tests pass.
 All tests in `test_bug_10_repro.py`, `test_ship_core.py`, and `test_builder_validation.py` passed. |
