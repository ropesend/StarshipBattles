# Phase 4: Delete Transfer, Production, Research & Repro Duplicates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-263 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove ~1,644 LOC of duplicate tests spanning transfer orders, fleet production, superweapon handler validation, research, AI controller, combat operations, and repro issue files. Most non-repro files require partial deletion (removing duplicate classes while preserving unique ones). All repro issue files are full deletions.

---

## Tasks

### Task 4.1: Delete duplicate load/unload and validation tests from test_fleet_order_transfer.py [Medium]
**File:** `tests/unit/strategy/engine/test_fleet_order_transfer.py` (389 LOC)
**Canonical:** `tests/unit/strategy/engine/test_transfer_order.py`

- [ ] Read `tests/unit/strategy/engine/test_fleet_order_transfer.py` fully
- [ ] Read `tests/unit/strategy/engine/test_transfer_order.py` fully
- [ ] Identify `TestExecuteLoad` + `TestExecuteUnload` (10 mock tests, ~162 LOC) -- confirmed duplicates
- [ ] Identify `TestTransferValidation` (3 tests, ~56 LOC) -- confirmed duplicates
- [ ] Identify `TestProcessTransfer` negative-path tests (no order, wrong type, invalid params) -- these are UNIQUE, keep them
- [ ] Delete `TestExecuteLoad`, `TestExecuteUnload`, and `TestTransferValidation` classes
- [ ] Keep `TestProcessTransfer` negative-path tests
- [ ] Run `pytest tests/unit/strategy/engine/test_fleet_order_transfer.py tests/unit/strategy/engine/test_transfer_order.py -v` -- confirm remaining tests pass

**Notes:** [Filled during implementation]

---

### Task 4.2: Delete duplicate dataclass and creation tests from test_fleet_order_processor.py [Simple]
**File:** `tests/unit/strategy/test_fleet_order_processor.py` (615 LOC)

- [ ] Read `tests/unit/strategy/test_fleet_order_processor.py` fully
- [ ] Identify the 3 dataclass tests (~35 LOC) and `TestOrderProcessorCreation` (1 test, ~10 LOC) -- confirmed duplicates
- [ ] Delete only the duplicate test classes (~45 LOC)
- [ ] Keep all other tests in the file
- [ ] Run `pytest tests/unit/strategy/test_fleet_order_processor.py -v` -- confirm remaining tests pass

**Notes:** [Filled during implementation]

---

### Task 4.3: Delete duplicate movement blocking and save/load tests from test_fleet_production_e2e.py [Simple]
**File:** `tests/integration/strategy/production/test_fleet_production_e2e.py` (440 LOC)

- [ ] Read `tests/integration/strategy/production/test_fleet_production_e2e.py` fully
- [ ] Identify the 2 movement blocking tests (~51 LOC) and 1 save/load test (~31 LOC) -- confirmed duplicates
- [ ] Delete the 3 duplicate tests (~82 LOC)
- [ ] Keep remaining tests in the file
- [ ] Run `pytest tests/integration/strategy/production/test_fleet_production_e2e.py -v` -- confirm remaining tests pass

**Notes:** [Filled during implementation]

---

### Task 4.4: Delete duplicate "rejects" tests from test_superweapon_handler_validation.py [Simple]
**File:** `tests/unit/strategy/engine/test_superweapon_handler_validation.py` (459 LOC)

- [ ] Read `tests/unit/strategy/engine/test_superweapon_handler_validation.py` fully
- [ ] Identify the 5 direct-handler "rejects" tests (~100 LOC) -- confirmed duplicates
- [ ] Keep the 10 "passes_component_registry" tests -- these are UNIQUE
- [ ] Delete only the 5 duplicate "rejects" tests
- [ ] Run `pytest tests/unit/strategy/engine/test_superweapon_handler_validation.py -v` -- confirm remaining tests pass

**Notes:** [Filled during implementation]

---

### Task 4.5: Delete test_research_tracker_edge_cases.py [Simple]
**File:** `tests/unit/research/test_research_tracker_edge_cases.py` (149 LOC)
**Canonical:** `tests/unit/research/test_research_tracker.py`

- [ ] Read `tests/unit/research/test_research_tracker_edge_cases.py` fully
- [ ] Read `tests/unit/research/test_research_tracker.py` -- confirm all edge cases are covered
- [ ] Confirm entire file is a duplicate with no unique tests
- [ ] Delete `tests/unit/research/test_research_tracker_edge_cases.py`
- [ ] Run `pytest tests/unit/research/test_research_tracker.py -v` -- confirm canonical tests pass

**Notes:** [Filled during implementation]

---

### Task 4.6: Delete EngageDistance and CapabilitiesCache from test_ai_controller_edge_cases.py [Simple]
**File:** `tests/unit/ai/test_ai_controller_edge_cases.py` (413 LOC)

- [ ] Read `tests/unit/ai/test_ai_controller_edge_cases.py` fully
- [ ] Identify `EngageDistance` tests (6 tests, ~50 LOC) -- confirmed duplicates
- [ ] Identify `CapabilitiesCache` tests (4 tests, ~60 LOC) -- confirmed duplicates
- [ ] Keep all remaining tests in the file (they are unique)
- [ ] Delete only the `EngageDistance` and `CapabilitiesCache` test classes (~110 LOC)
- [ ] Run `pytest tests/unit/ai/test_ai_controller_edge_cases.py -v` -- confirm remaining tests pass

**Notes:** [Filled during implementation]

---

### Task 4.7: Delete facade duplicate tests from test_combat_ops.py [Medium]
**File:** `tests/unit/simulation/ship_combat_engine/test_combat_ops.py` (257 LOC)
**Canonical:** `tests/unit/simulation/combat/test_damage_calculator.py` + `tests/unit/simulation/combat/test_weapon_firing_system.py`

- [ ] Read `tests/unit/simulation/ship_combat_engine/test_combat_ops.py` fully
- [ ] Read `tests/unit/simulation/combat/test_damage_calculator.py` -- identify overlapping tests
- [ ] Read `tests/unit/simulation/combat/test_weapon_firing_system.py` -- identify overlapping tests
- [ ] Identify facade tests that duplicate the direct tests (~210 LOC)
- [ ] Delete duplicate facade tests
- [ ] If remaining content is minimal (~47 LOC), evaluate whether to keep or delete entire file
- [ ] Run `pytest tests/unit/simulation/combat/ tests/unit/simulation/ship_combat_engine/ -v` -- confirm no regressions

**Notes:** [Filled during implementation]

---

### Task 4.8: Delete repro issue files -- batch 1 (bug 01-05) [Simple]
**Files:** 6 files, 697 LOC total
Each repro file has been verified (V4) as fully covered by proper unit tests.

- [ ] Read `tests/repro_issues/test_bug_01_crew_delay.py` (113 LOC) -- confirm coverage exists elsewhere
- [ ] Read `tests/repro_issues/test_bug_02_seeker.py` (37 LOC) -- confirm coverage exists elsewhere
- [ ] Read `tests/repro_issues/test_bug_03_validation.py` (104 LOC) -- confirm coverage exists elsewhere
- [ ] Read `tests/repro_issues/test_bug_05_logistics.py` (108 LOC) -- confirm coverage exists elsewhere
- [ ] Read `tests/repro_issues/test_bug_05_rejected_fix.py` (91 LOC) -- confirm coverage exists elsewhere
- [ ] Read `tests/repro_issues/test_bug_05_deep_repro.py` (157 LOC) -- confirm coverage exists elsewhere
- [ ] Delete all 6 files
- [ ] Run `pytest tests/repro_issues/ -v --tb=short` -- confirm remaining repro tests pass (bug_06 onward)

**Notes:** [Filled during implementation]

---

### Task 4.9: Delete repro issue files -- batch 2 (bug 06-10) [Simple]
**Files:** 5 files, 447 LOC total

- [ ] Read `tests/repro_issues/test_bug_06_combat_propulsion.py` (147 LOC) -- confirm coverage exists elsewhere
- [ ] Read `tests/repro_issues/test_bug_07_crash.py` (59 LOC) -- confirm coverage exists elsewhere
- [ ] Read `tests/repro_issues/test_bug_08_fuel_validation.py` (59 LOC) -- confirm coverage exists elsewhere
- [ ] Read `tests/repro_issues/test_bug_09_endurance.py` (80 LOC) -- confirm coverage exists elsewhere
- [ ] Read `tests/repro_issues/test_bug_10_logistics_update.py` (112 LOC) -- confirm coverage exists elsewhere
- [ ] Delete all 5 files
- [ ] Run `pytest tests/repro_issues/ -v --tb=short` -- confirm remaining repro tests pass (if any)

**Notes:** [Filled during implementation]

---

### Task 4.10: Delete miscellaneous repro/duplicate files [Simple]
**Files:** 2 files, 77 LOC total

- [ ] Read `tests/unit/test_builder_refactor.py` (36 LOC) -- confirm coverage by workshop tests
- [ ] Read `tests/unit/performance/reproduce_scaling.py` (41 LOC) -- confirm coverage exists elsewhere
- [ ] Delete both files
- [ ] Check if `tests/unit/performance/` directory is now empty; clean up if so
- [ ] Check if `tests/repro_issues/` directory is now empty or only has non-duplicate files; clean up if appropriate

**Notes:** [Filled during implementation]

---

### Task 4.11: Run full test suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded test suite
- [ ] Confirm zero failures
- [ ] Record final test count and total LOC removed across all 4 phases
- [ ] Verify: no test collection errors or import warnings
- [ ] Compare final test count against baseline to confirm expected reduction

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Negative-path tests preserved in test_fleet_order_transfer.py
- [ ] "passes_component_registry" tests preserved in test_superweapon_handler_validation.py
- [ ] Remaining unique tests preserved in all partially-deleted files
- [ ] All 13 repro issue / miscellaneous files deleted
- [ ] Empty directories cleaned up
- [ ] Full test suite passes with zero failures
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
