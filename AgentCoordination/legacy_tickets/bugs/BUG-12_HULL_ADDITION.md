# BUG-12: Ship Builder - Component Addition to Hull Layer

## Description
Ship Builder:
I should not be able to add any components to the Hull layer, currently I can add a bunch of components.

## Status
Awaiting Confirmation

## Work Log
- 2026-01-09: Ticket created.
- 2026-01-09: Phase 1: Reproduction. Created `tests/repro_issues/test_bug_12_hull_layer_addition.py`. Test confirmed failure: `AssertionError: True is not false : Should NOT be able to add bridge to HULL layer`. Status set to [In-Progress].
- 2026-01-09: Phase 2: The Fix. Modified `game/simulation/ship_validator.py` to enforce the `HullOnly` restriction in `LayerRestrictionDefinitionRule`. It now explicitly blocks any component whose ID does not start with `hull_` when the `HullOnly` restriction is present.
- 2026-01-09: Phase 3: Verification. Reproduction test `tests/repro_issues/test_bug_12_hull_layer_addition.py` passed. Regression tests in `tests/unit/builder/test_builder_logic.py` passed. Status updated to Awaiting Confirmation.
