# BUG-06: Combat Propulsion Error

## Description
I get an error reporting that I need combat propulsion when I have a Engine on my ship:
C:\Dev\Starship Battles\screenshots\screenshot_20260103_153938_218820_mouse_focus.png
C:\Dev\Starship Battles\screenshots\screenshot_20260103_153950_626104_mouse_focus.png

## Status
[Pending]

## Work Log
[2026-01-03 16:35] Phase 1 - Reproduction: Created `tests/repro_issues/test_bug_06_combat_propulsion.py`. Confirmed failure: `missing_reqs` contains 'Needs Combat Propulsion' error.
[2026-01-03 16:55] Phase 2 - Fix: Identified two root causes:
1. `ShipStatsCalculator` ignored `CombatPropulsion` values because it didn't check for the `thrust_force` attribute.
2. `ShipDesignValidator` ignored the candidate component during addition validation, creating a circular dependency where a component couldn't be added to fix a missing requirement because the requirement was checked before addition.

Fix applied:
- Updated `ship_stats.py` to checking for `thrust_force`.
- Updated `ship_validator.py` to include the candidate component in validation logic.
- Verified with reproduction test.

## Solution Summary
The issue was caused by two separate bugs:
1. **Ability Aggregation**: `ShipStatsCalculator` (ship_stats.py) was missing a check for the `thrust_force` attribute, causing `CombatPropulsion` abilities to be ignored during stat calculation.
2. **Validation Logic**: `ClassRequirementsRule` (ship_validator.py) calculated requirements based only on *existing* ship components, ignoring the new component being added. This prevented adding a required component (like an Engine) because validation would fail before the component was added.

**Fix Details**:
- Modified `ship_stats.py` to extract `thrust_force` from ability instances.
- Modified `ship_validator.py` to include the candidate `component` in the `all_components` list during validation.
- Validated with `tests/repro_issues/test_bug_06_combat_propulsion.py`.
