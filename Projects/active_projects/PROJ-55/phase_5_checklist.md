# Phase 5: Integration & Testing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-55 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** End-to-end testing and regression verification

---

## Tasks

### Task 5.1: Create Comprehensive Integration Tests [Medium]
**File:** `tests/integration/colonization/test_planet_specific_colonization.py` (new file)
**Tests:** `pytest tests/integration/colonization/test_planet_specific_colonization.py -v`

- [ ] Create new file `tests/integration/colonization/test_planet_specific_colonization.py`
- [ ] Write test: `test_colonize_with_matching_pod_succeeds()`
  - Create Ice Dwarf planet, fleet with Ice Dwarf pod ship
  - Issue colonize command
  - Execute colonization
  - Assert: Planet colonized, colony ship removed, fleet remains
- [ ] Write test: `test_colonize_with_wrong_pod_fails()`
  - Create Ice Dwarf planet, fleet with Continental pod ship
  - Try to issue colonize command
  - Assert: Validation fails with NO_COLONY_POD error
- [ ] Write test: `test_chain_colonization_with_multiple_pods()`
  - Create 2 Continental planets, fleet with 2 Continental pod ships
  - Queue both colonizations
  - Execute turn
  - Assert: Both planets colonized, both ships removed
- [ ] Write test: `test_chain_exhaustion_prevents_overcommit()`
  - Create 3 Ice Dwarf planets, fleet with 2 Ice Dwarf pod ships
  - Queue 2 colonizations (succeeds)
  - Try to queue 3rd colonization
  - Assert: Validation fails with COLONY_POD_EXHAUSTED error
- [ ] Write test: `test_mixed_fleet_colonizes_multiple_types()`
  - Create Ice Dwarf + Continental planets, fleet with both pod types
  - Queue both colonizations
  - Execute
  - Assert: Both colonized, both ships removed, fleet empty
- [ ] Write test: `test_last_ship_colonization_removes_fleet()`
  - Create planet, fleet with single colony ship
  - Execute colonization
  - Assert: Planet colonized, fleet removed from empire
- [ ] Write test: `test_partial_fleet_colonization_preserves_fleet()`
  - Create planet, fleet with colony ship + combat ship
  - Execute colonization
  - Assert: Planet colonized, colony ship removed, combat ship remains, fleet exists
- [ ] Write test: `test_multiple_planets_in_sector_shows_correct_options()`
  - Create sector with Ice + Continental planets
  - Fleet with only Ice pod
  - Assert: Only Ice planet shown as option
- [ ] Run tests: `pytest tests/integration/colonization/test_planet_specific_colonization.py -v`
- [ ] Verify: All tests pass

**Notes:**

---

### Task 5.2: Run Full Test Suite (Regression Check) [Simple]
**File:** All tests
**Tests:** `pytest tests/`

- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Review output for failures
- [ ] Identify any regressions (tests that passed before but fail now)
- [ ] Fix regressions:
  - Most likely: Tests that create fleets without colony pods
  - Solution: Add colony pod components to test ships
- [ ] Re-run full suite: `pytest tests/`
- [ ] Verify: All tests pass (6119+ tests)

**Notes:** Expected changes - tests that assume any fleet can colonize

---

### Task 5.3: Manual Testing Scenarios [Medium]
**File:** Manual gameplay testing
**Tests:** Launch game and test scenarios

- [ ] Scenario 1: Design colony ship in workshop
  - Launch game
  - Open ship designer
  - Create new ship design
  - Add Continental Colony Pod component
  - Verify: Component appears, can be added, ship saves
- [ ] Scenario 2: Build and deploy colony ship
  - Build colony ship from design
  - Add to fleet
  - Navigate to system with Continental planet
  - Issue colonize command
  - Verify: Planet colonized, only colony ship removed
- [ ] Scenario 3: Queue multiple colonizations
  - Create fleet with 3 Continental pod ships
  - Find system with multiple Continental planets
  - Queue 3 colonizations
  - Execute turn
  - Verify: All 3 planets colonized, all 3 ships removed
- [ ] Scenario 4: Chain validation prevents overcommit
  - Fleet with 2 Ice Dwarf pods
  - Try to queue 3 Ice Dwarf colonizations
  - Verify: 3rd colonization rejected with error message
- [ ] Scenario 5: UI filters planets by available pods
  - Fleet with only Arid pod
  - Navigate to system with Arid + Continental planets
  - Click colonize
  - Verify: Only Arid planet shown as option
- [ ] Scenario 6: Error message when no pods
  - Fleet without colony pods
  - Try to colonize
  - Verify: Message "No colony pods in fleet" displayed

**Notes:** Document any unexpected behavior or bugs

---

### Task 5.4: Fix Discovered Issues [Variable]
**File:** Various files as needed
**Tests:** Dependent on issues found

- [ ] Review manual testing notes
- [ ] Review test failures from full suite
- [ ] Create list of issues to fix
- [ ] Fix each issue systematically
- [ ] Re-test after each fix
- [ ] Verify: All issues resolved

**Notes:**

---

### Task 5.5: Update Documentation [Simple]
**File:** Update project README or docs
**Tests:** N/A

- [ ] Update project plan.md Current State to "Complete"
- [ ] Update all phase checklists to "Complete"
- [ ] Document any deviations from original plan in decisions.md
- [ ] Update verification checklist in plan.md

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/` - ALL tests pass (no failures, no regressions)
- [ ] All manual testing scenarios completed successfully
- [ ] All discovered issues fixed
- [ ] Documentation updated
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table - all phases marked Complete
- [ ] Update plan.md Current State to "Project Complete"
- [ ] Ready for user verification
