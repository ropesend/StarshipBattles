# Phase 2: NewGameSetupScreen Extended Coverage [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-266 2`
> 2. Only proceed if output shows PASSED

**Objective:** Write tests for UI behavior of new_game_setup_screen.py (only static methods currently tested).
**Status:** Not Started

---

## Task 2.1: Create test_new_game_setup_extended.py [Medium]
**File:** `tests/unit/ui/screens/test_new_game_setup_extended.py` (NEW)
**Source:** `game/ui/screens/new_game_setup_screen.py` (645 LOC, 30.2% coverage)
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_extended.py -v`

### Empire visibility tests
- [ ] `test_empire_visibility_shows_correct_count`
- [ ] `test_empire_visibility_clears_race_for_hidden`
- [ ] `test_empire_visibility_two_players`
- [ ] `test_empire_visibility_four_players`

### Race display tests
- [ ] `test_race_display_updates_preview_label`
- [ ] `test_race_display_hides_name_input_when_race_set`
- [ ] `test_race_display_shows_name_input_when_no_race`

### Event routing tests
- [ ] `test_dropdown_change_updates_player_count`
- [ ] `test_dropdown_change_updates_galaxy_type`
- [ ] `test_slider_updates_system_count`

### Start game validation
- [ ] `test_start_validates_save_name`
- [ ] `test_start_collects_empire_names_from_race`
- [ ] `test_start_collects_manual_empire_name`
- [ ] `test_start_builds_config_and_calls_callback`
- [ ] `test_start_shows_error_on_empty_name`

### Race selection callbacks
- [ ] `test_on_race_selected_sets_player_race`
- [ ] `test_on_race_created_sets_new_race`
- [ ] `test_on_race_dialog_cancelled_no_change`

### Cancel
- [ ] `test_on_cancel_calls_callback`

## Phase 2 Verification
- [ ] New test file passes independently
- [ ] No regressions: `pytest tests/ --testmon`
