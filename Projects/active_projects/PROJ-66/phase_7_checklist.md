# Phase 7: Validation, Fixtures & Integration [Medium]

**Objective:** Update validation, test fixtures, and verify end-to-end flow
**Tests:** `pytest tests/ -n 12`

---

## Task 7.1: Update RaceValidator [Medium]
**File:** `game/ui/screens/race_validator.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_validator.py -v`

- [ ] Read current validator implementation
- [ ] Add validation for point budget:
  - If over budget → error: "Race is over point budget. Reduce aptitudes or tolerance on the Aptitudes tab."
- [ ] Add validation for water ranges:
  - water_ideal 0.0-1.0 → error points to Environment tab
  - water_tolerance 0.0-1.0 → error points to Environment tab
- [ ] Add validation for aptitude ranges:
  - Each aptitude 1-10 → error points to Aptitudes tab
- [ ] Add optional validation warnings for empty identity fields:
  - If government_type empty → warning (not error): "Consider selecting a Government Type on the Identity tab"
- [ ] Update error messages to reference correct tab names (Identity, Aptitudes, Environment)
- [ ] Write test: `test_validate_over_budget_returns_error`
- [ ] Write test: `test_validate_water_ideal_out_of_range`
- [ ] Write test: `test_validate_aptitude_out_of_range`
- [ ] Write test: `test_validate_valid_with_all_new_fields`
- [ ] Write test: `test_error_messages_reference_tab_names`
- [ ] Verify existing validation tests still pass
- [ ] Run tests: all pass
**Notes:** Identity fields remain optional for save — a race with no government type is valid (user can fill it later).

---

## Task 7.2: Update Test Fixtures [Simple]
**File:** `tests/fixtures/quickstart/races/test_emp1.json` and `test_emp2.json`
**Tests:** `pytest tests/unit/quickstart/ -v`

- [ ] Read current test_emp1.json
- [ ] Add all new fields with sensible test values:
  ```json
  {
    "faction_name": "TestEmp1 Federation",
    "race_name": "TestEmp1",
    "race_name_plural": "TestEmp1s",
    "government_type": "Federation",
    "government_organization": "Democracy",
    "leader_title": "President",
    "physical_type": "Humanoid",
    "society_type": "Scientists",
    "homeworld_type": "CONTINENTAL",
    "water_ideal": 0.6,
    "water_tolerance": 0.2,
    "aptitude_strength": 5,
    "aptitude_intelligence": 7,
    "aptitude_constitution": 5,
    "aptitude_dexterity": 5,
    "aptitude_tolerance_other_species": 6,
    "aptitude_cooperation": 6,
    "aptitude_happiness": 5,
    "aptitude_population_growth": 5,
    "aptitude_conflict_tolerance": 4
  }
  ```
- [ ] Update test_emp2.json similarly (different values for variety)
- [ ] Verify quickstart tests pass with updated fixtures
- [ ] Run tests: all pass
**Notes:** These fixtures are used by QuickstartBuilder for rapid testing.

---

## Task 7.3: Update QuickstartBuilder (if needed) [Simple]
**File:** `game/strategy/quickstart_builder.py`
**Tests:** `pytest tests/unit/quickstart/ -v`

- [ ] Read QuickstartBuilder to check if any changes needed
- [ ] Verify RaceConfig.from_dict() handles new fields from fixtures
- [ ] Verify build_1p_config / build_2p_config still work
- [ ] Run quickstart tests: all pass
**Notes:** Should work automatically since from_dict() uses .get() with defaults.

---

## Task 7.4: Update NewGameSetupScreen Race Display [Simple]
**File:** `game/ui/screens/new_game_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup.py -v`

- [ ] Update `_update_race_display()` to show more info when race is selected:
  - Currently shows: "Race: {race.name}"
  - Change to: "Race: {race.faction_name or race.name}" (use faction_name if available)
  - Optionally show government type below: "{government_type} • {society_type}"
- [ ] Verify `build_game_config()` works with new race fields (should be fine — it only uses visual fields)
- [ ] Run tests: all pass
**Notes:** Minimal change — just improving the display label.

---

## Task 7.5: Full Test Suite & Regression Verification [Medium]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [ ] Fix any regressions found
- [ ] Verify count: should be ~6244 + ~65 new tests ≈ 6309 passed
- [ ] Check for any new warnings
- [ ] Run targeted test categories:
  - [ ] `pytest tests/unit/strategy/data/ -v` — all data model tests
  - [ ] `pytest tests/unit/ui/ -v -k "race"` — all race UI tests
  - [ ] `pytest tests/unit/quickstart/ -v` — quickstart tests
- [ ] Run tests: all pass
**Notes:**

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
**Notes:**

---

## Phase 7 Completion Checklist
- [ ] All tasks above checked off
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] All manual tests pass
- [ ] No regressions from baseline (6244 tests)
- [ ] Backward compatibility verified
- [ ] New race creation flow works end-to-end
