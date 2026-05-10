## Description

**Category:** Bug
**Title:** New Game Setup fails to populate loaded species data
**Description:** In the New Game Setup screen, selecting a previously saved species and clicking 'Setup Species' loads default/blank values instead of correctly populating the setup fields with the selected species' data.
**Screenshot:**
[![Screenshot](c:\Developer\StarshipBattles\tools\qa_observer\session_data\20260228_125515\images\bug_capture_125602.png)](c:\Developer\StarshipBattles\tools\qa_observer\session_data\20260228_125515\images\bug_capture_125602.png)
*Note: This screenshot shows the initial start up screen. The issue specifically occurs on the subsequent race stats screen where the selected species data should be populated, which currently loads with default/blank values.*

## Priority
High

## Status (Awaiting Confirmation)

## Work Log

### 2026-02-28 — Fix Applied

**Root Cause:** In `game/ui/screens/new_game_setup_screen.py`, the `_on_setup_race_clicked()` method creates a `RaceSetupScreen` but never passes the already-loaded race data. When a player has previously selected a species via "Load Species" (stored in `self.player_races[player_index]`), clicking "Setup Species" opens the race setup screen with a blank `RaceConfig()` instead of the loaded data.

The `RaceSetupScreen` constructor already supports a `race_to_edit` parameter for editing existing races, but `_on_setup_race_clicked()` was not passing it.

**Fix:** Added `race_to_edit=self.player_races[player_index]` to the `RaceSetupScreen()` constructor call in `_on_setup_race_clicked()`. When `player_races[player_index]` is `None` (no race loaded), this is equivalent to the previous behavior (blank form). When a race has been loaded, it populates the form with the loaded species data.

**Files Modified:**
- `game/ui/screens/new_game_setup_screen.py` — Pass `race_to_edit` to RaceSetupScreen constructor
- `tests/unit/ui/test_new_game_setup.py` — Added 2 new tests:
  - `test_setup_race_passes_loaded_race` — Verifies loaded race data is passed to RaceSetupScreen
  - `test_setup_race_no_loaded_race_passes_none` — Verifies None is passed when no race loaded

**Regression:** 3243 UI tests passed (0 failures).
