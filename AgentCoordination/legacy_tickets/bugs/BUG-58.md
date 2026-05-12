# BUG-58: Race Setup - Racial Points Not Displayed in Environment Window

## Description

RAce setup --> racial points should be displayed in the Environment windows, so that I know how fast I'm using them.

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log

### Fix Applied (2026-02-07)

**Root Cause:** The racial points budget was only displayed in the Aptitudes tab. The Environment tab (where tolerance sliders are) had no points indicator, making it hard to see the cost impact of environment preferences.

**Changes:**

1. **`game/ui/panels/race_environment_panel.py`**:
   - Added `points_label` UILabel at the top of the panel (before Homeworld Type)
   - Added `_update_points_display()` method that calculates remaining points and tolerance cost using `RacePointBudget`
   - Label shows: `"Points: X / 100 remaining  |  Environment cost: Y"`
   - Called from `update_labels()` so it refreshes whenever any slider changes
   - Used `getattr(self, 'points_label', None)` guard for test compatibility

**Tests:** All 29 race environment panel tests pass.
