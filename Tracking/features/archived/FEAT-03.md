# FEAT-03: Randomize all properties in Identity Setup

## Description
Clicking "Generate random" in the BC identity setup window should fully randomize physical type, government type, organization, leader title, and society type.

## Priority
Medium

## Status (Awaiting Confirmation)

## Work Log
- 2026-02-28: **Phase 0 — Deep Review:**
  The randomization logic was already implemented by FEAT-02 (all 5 dropdown properties are randomized by `RaceRandomizer.randomize_identity()`). However, the UI dropdowns do not visually update when `set_from_config()` is called after randomization.

  **Root cause:** `_set_dropdown_value()` in `RaceIdentityPanel` directly set `dropdown.selected_option = (value, value)` which updates the internal attribute but does NOT refresh the visual button text. pygame_gui's `UIDropDownMenu` has no public API to change the displayed selection after creation — the button text is only set during widget construction.

- 2026-02-28: **Phase 1 — Analysis:**
  The codebase already has the correct pattern in `transfer_dialog.py` — kill the old dropdown and create a new one with the correct `starting_option`. Clean implementation: replace `_set_dropdown_value()` with `_recreate_dropdown()`.

- 2026-02-28: **Phase 2 — Tests (Red):**
  Added 3 tests to `TestSetFromConfig` in `tests/unit/ui/panels/test_race_identity_panel.py`:
  - `test_set_from_config_recreates_dropdowns` — verifies old dropdowns are killed and 5 new ones are created
  - `test_set_from_config_passes_correct_starting_option` — verifies correct values (including empty → "-- Select --") are passed as starting_option
  - `test_set_from_config_handles_none_dropdown` — verifies None dropdowns don't error

  Replaced previous `test_set_from_config_populates_dropdowns` (which had no real assertions) and `test_set_from_config_handles_empty_government` (now covered by the None dropdown test).

- 2026-02-28: **Phase 3 — Implementation (Green):**
  Replaced `_set_dropdown_value()` with `_recreate_dropdown()` in `RaceIdentityPanel`:
  - New method kills old dropdown, creates fresh `UIDropDownMenu` with correct `starting_option`
  - `set_from_config()` now calls `_recreate_dropdown()` for all 5 dropdowns and stores the new widget references
  - Follows existing pattern from `transfer_dialog.py`

  **Files modified:**
  - `game/ui/panels/race_identity_panel.py` — Replaced `_set_dropdown_value()` with `_recreate_dropdown()`, updated `set_from_config()` to use kill-and-recreate pattern
  - `tests/unit/ui/panels/test_race_identity_panel.py` — Replaced 2 weak tests with 3 stronger tests verifying the recreate behavior

  **Regression:** 13,005 passed, 0 failures, 1 skipped.
