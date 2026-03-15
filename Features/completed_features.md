# Completed Features Archive

**APPEND ONLY - DO NOT DELETE ENTRIES**

This file serves as the permanent index of all completed features with implementation summaries.

**Entry Format:**
```markdown
## [FEAT-ID] - [Feature Title]
* **Date Completed:** YYYY-MM-DD HH:MM
* **Original Request:** [Summary of what was requested]
* **Implementation Summary:** [Technical details of what was built]
* **Test Case:** [Reference to the test file that covers this]
* **Notes:** [Any future considerations, warnings for refactors]
---
```

---

<!-- New entries should be appended below this line -->

## [FEAT-01] - Pre-populate Save Game Name
* **Date Completed:** 2026-03-14
* **Original Request:** Auto-populate the save name field with "save game" plus a timestamp for new games.
* **Implementation Summary:** Added `generate_default_save_name()` static method to `NewGameSetupScreen` returning `"save game YYYY-MM-DD HHMM"` format. Called `set_text()` on the input after creation.
* **Test Case:** `tests/unit/ui/test_new_game_setup.py::TestNewGameSetupDefaultSaveName`
* **Notes:** Timestamp uses `HHMM` format (no colon) because colons are invalid filesystem characters.
---

## [FEAT-02] - Add "Generate Random" Buttons to Species Setup
* **Date Completed:** 2026-03-14
* **Original Request:** Add "Generate Random" buttons to Identity, Visual, and Ships tabs in Species Setup to randomize all fields with thematically appropriate data.
* **Implementation Summary:** Created `RaceRandomizer` service class with portrait-aware name generation. Added `race_names.json` data file with entries for all 14 portraits. Single button in navigation area dispatches by current tab.
* **Test Case:** `tests/unit/strategy/test_race_randomizer.py` (23 tests)
* **Notes:** Portrait-aware name generation pulls from portrait-specific pools when a portrait is selected.
---

## [FEAT-03] - Randomize All Properties in Identity Setup
* **Date Completed:** 2026-03-14
* **Original Request:** Clicking "Generate random" should fully randomize all identity dropdown fields (physical type, government type, organization, leader title, society type).
* **Implementation Summary:** Fixed dropdown visual update issue — replaced `_set_dropdown_value()` with `_recreate_dropdown()` in `RaceIdentityPanel` using kill-and-recreate pattern (matching `transfer_dialog.py`).
* **Test Case:** `tests/unit/ui/panels/test_race_identity_panel.py::TestSetFromConfig`
* **Notes:** pygame_gui `UIDropDownMenu` has no public API to change displayed selection after creation; must kill and recreate.
---

## [FEAT-04] - Event Log 'Go To Location' Navigation
* **Date Completed:** 2026-03-14
* **Original Request:** Add clickable/double-click navigation to event log entries that moves the camera to the event's location on the map, with a Location column showing where each event occurred.
* **Implementation Summary:** Added `location_hex` and `location_name` to all `log_event()` calls across production, combat, colonization, and superweapon engines. Added Location column to event log via `EVENT_LOG_COLUMNS`. Implemented double-click detection in `EventLogWindow` with navigate callback that closes the log and centers camera via `center_on_hex()`.
* **Test Case:** `tests/unit/ui/screens/test_event_log_data_source.py` (5 tests), `tests/unit/ui/screens/test_event_log_window.py` (5 tests), `tests/unit/ui/screens/test_camera_navigator.py` (3 tests)
* **Notes:** None.
---

## [FEAT-05] - Save/Update Species Workflow Dialog
* **Date Completed:** 2026-03-14
* **Original Request:** When modifying and saving an existing species, prompt a dialog offering to overwrite the old species or save as a new one.
* **Implementation Summary:** Added save/update dialog to `RaceSetupScreen._on_save()` that detects `is_editing` + existing `race_id`. Dialog offers Overwrite (preserves race_id), Save as New (clears race_id), or Cancel.
* **Test Case:** `tests/unit/ui/screens/test_race_setup_screen.py::TestSaveUpdateDialog` (5 tests)
* **Notes:** None.
---
