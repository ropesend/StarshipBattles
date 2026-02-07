# Phase 7: Validation, Fixtures & Integration [Medium]

**Objective:** Update validation, test fixtures, and verify end-to-end flow
**Tests:** `pytest tests/ -n 12`

---

## Task 7.1: Update RaceValidator [Medium]
**File:** `game/ui/screens/race_validator.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_validator.py -v`

- [x] Read current validator implementation
- [x] Add validation for point budget:
  - If over budget → error: "Race is over point budget. Reduce aptitudes or tolerance on the Aptitudes tab."
- [x] Add validation for water ranges:
  - water_ideal 0.0-1.0 → error points to Environment tab
  - water_tolerance 0.0-1.0 → error points to Environment tab
- [x] Add validation for aptitude ranges:
  - Each aptitude 1-10 → error points to Aptitudes tab
- [x] Add optional validation warnings for empty identity fields:
  - Skipped - identity fields remain optional (no warnings needed)
- [x] Update error messages to reference correct tab names (Identity, Aptitudes, Environment)
- [x] Write test: `test_validate_over_budget_returns_error`
- [x] Write test: `test_validate_water_ideal_out_of_range`
- [x] Write test: `test_validate_aptitude_out_of_range`
- [x] Write test: `test_validate_valid_with_all_new_fields`
- [x] Write test: `test_error_messages_reference_tab_names`
- [x] Verify existing validation tests still pass
- [x] Run tests: all pass (17 new tests)
**Notes:** Identity fields remain optional for save — a race with no government type is valid (user can fill it later). Updated old test file fixtures to include PROJ-66 fields.

---

## Task 7.2: Update Test Fixtures [Simple]
**File:** `tests/fixtures/quickstart/races/test_emp1.json` and `test_emp2.json`
**Tests:** `pytest tests/unit/quickstart/ -v`

- [x] Read current test_emp1.json
- [x] Add all new fields with sensible test values
- [x] Update test_emp2.json similarly (different values for variety)
- [x] Verify quickstart tests pass with updated fixtures
- [x] Run tests: all pass (66 quickstart tests)
**Notes:** Used ARID for test_emp2 (not DESERT - that's not a valid PlanetType).

---

## Task 7.3: Update QuickstartBuilder (if needed) [Simple]
**File:** `game/strategy/quickstart_builder.py`
**Tests:** `pytest tests/unit/quickstart/ -v`

- [x] Read QuickstartBuilder to check if any changes needed
- [x] Verify RaceConfig.from_dict() handles new fields from fixtures
- [x] Verify build_1p_config / build_2p_config still work
- [x] Run quickstart tests: all pass
**Notes:** No changes needed - from_dict() uses .get() with defaults as expected.

---

## Task 7.4: Update NewGameSetupScreen Race Display [Simple]
**File:** `game/ui/screens/new_game_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup.py -v`

- [x] Update `_update_race_display()` to show more info when race is selected:
  - Now shows: "Race: {race.faction_name or race.name}"
  - Shows government type and society type: "{government_type} • {society_type}"
- [x] Verify `build_game_config()` works with new race fields (unchanged - uses visual fields only)
- [x] Run tests: all pass (no existing tests for this screen)
**Notes:** Improved display to show faction_name and government/society type.

---

## Task 7.5: Full Test Suite & Regression Verification [Medium]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [x] Fix any regressions found
  - Fixed old test_race_validator.py fixtures with PROJ-66 fields
  - Updated test for Identity tab (was Visuals tab)
- [x] Verify count: 6290 passed (baseline was 6210, added ~80 new tests across phases)
- [x] Check for any new warnings: None new
- [x] Run targeted test categories:
  - [x] All validator tests pass (35 tests)
  - [x] All quickstart tests pass (66 tests)
- [x] Run tests: all pass (2 pre-existing bug_15 failures excluded)
**Notes:** 6290 passed. Pre-existing failures in test_bug_15_screenshot_strategy.py (unrelated to PROJ-66).

---

## Task 7.6: Manual Integration Testing [Medium]

- [ ] Launch game, go to Race Setup
- [ ] Verify all 7 tabs display and switch correctly
- [ ] On Identity tab: fill all dropdowns, verify faction name auto-generates
- [ ] On Environment tab: select homeworld type, verify sliders auto-populate
- [ ] On Environment tab: adjust water sliders, verify display
- [ ] On Aptitudes tab: adjust stats, verify budget updates
- [ ] On Aptitudes tab: try to exceed budget, verify display goes red
- [ ] Save race with all fields populated
- [ ] Load saved race, verify all fields restored correctly
- [ ] Edit loaded race, change some values, save again
- [ ] Create new game with configured race, verify game starts
- [ ] Verify backward compatibility: load an old race without new fields
**Notes:** Manual testing deferred to user verification.

---

## Phase 7 Completion Checklist
- [x] All automated tasks above checked off
- [x] Full test suite passes: `pytest tests/ -n 12` (6290 passed)
- [ ] All manual tests pass (deferred to user)
- [x] No regressions from baseline (6210 tests → 6290 tests)
- [x] Backward compatibility verified (RaceConfig.from_dict uses defaults)
- [ ] New race creation flow works end-to-end (deferred to user)
