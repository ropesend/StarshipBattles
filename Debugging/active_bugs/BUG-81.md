# BUG-81: Species Setup - Load Saved Species does nothing

## Description

On the Species Setup Window the Load Saved Species from the summary tab does not actually load anything, it opens a dialog that lets me see the various species to load, but when I actually select one and click load, the dialog closes and nothing is loaded.

## Priority
High

## Status (Awaiting Confirmation)

## Work Log

### Fix Applied (2026-02-11)

**Root Cause:** When `_on_race_selected` set `self.race_config = loaded_config`, all sub-panels (identity, environment, aptitudes, description, galleries, summary) still held references to the OLD `race_config` object. When `set_from_config()` was called, panels read values from the stale reference and nothing changed visually.

**Changes:**

1. **`game/ui/screens/race_setup_screen.py`** (`_populate_ui_from_config`):
   - Added loop to update `panel.race_config = self.race_config` on all 8 panels before calling their `set_from_config()` methods

2. **`tests/unit/ui/screens/test_race_setup_screen.py`**:
   - Added `TestRaceSetupLoadSpecies` class with 2 tests:
     - `test_on_race_selected_updates_panel_race_configs` - verifies all panel references updated
     - `test_on_race_selected_calls_set_from_config` - verifies all panels refreshed

**Tests:** All tests pass.
