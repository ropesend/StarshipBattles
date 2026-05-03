# Phase 3: CAT-3 Dead Test Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-321 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete or relocate the 8 verified CAT-3 dead-test-code items identified by review `2026-05-02_204633_test-review` (repro scripts, empty placeholder classes, files with no unique coverage).

_Note: Task 3.5 is a relocation/rename, not a deletion. The source verification recommends keeping the file as a regression guard under `tests/regression/`. The phase objective is "Delete or relocate the 8 verified CAT-3 dead-test-code items"._

---

## Tasks

### Task 3.1: `tests/regression/test_deprecated_code_removed.py`
**File:** `tests/regression/test_deprecated_code_removed.py`
**Tests:** `pytest tests/regression/test_deprecated_code_removed.py`

- [ ] `test_fleet_movement_simulator_import_fails` (lines 13-16, 4 LOC) - Remove this test. The removed module has been gone long enough that regression risk is negligible.
- [ ] Verify: `pytest tests/regression/test_deprecated_code_removed.py` passes; LOC delta approximate 4

### Task 3.2: `tests/repro_issues/repro_facade_colonies.py`
**File:** `tests/repro_issues/repro_facade_colonies.py`
**Tests:** `pytest tests/repro_issues/repro_facade_colonies.py`

- [ ] `Standalone repro script` (lines 1-93, 93 LOC) - Convert to focused pytest test or delete and add coverage in tests/integration/strategy/facade/test_validation_queries.py.
- [ ] Verify: `pytest tests/repro_issues/repro_facade_colonies.py` passes; LOC delta approximate 93

### Task 3.3: `tests/repro_issues/repro_load_cargo_bug.py`
**File:** `tests/repro_issues/repro_load_cargo_bug.py`
**Tests:** `pytest tests/repro_issues/repro_load_cargo_bug.py`

- [ ] `Standalone repro script` (lines 1-244, 244 LOC) - Review whether bug is still present. If fixed, remove. If still present, convert to focused pytest test in appropriate integration test dir.
- [ ] Verify: `pytest tests/repro_issues/repro_load_cargo_bug.py` passes; LOC delta approximate 244

### Task 3.4: `tests/repro_issues/repro_warp_bug.py`
**File:** `tests/repro_issues/repro_warp_bug.py`
**Tests:** `pytest tests/repro_issues/repro_warp_bug.py`

- [ ] `Standalone repro script` (lines 1-79, 79 LOC) - Delete the file. Bugs are covered by proper pytest tests elsewhere.
- [ ] Verify: `pytest tests/repro_issues/repro_warp_bug.py` passes; LOC delta approximate 79

### Task 3.5: `tests/repro_issues/test_bug_12_energy_gen.py`
**File:** `tests/repro_issues/test_bug_12_energy_gen.py`
**Tests:** `pytest tests/repro_issues/test_bug_12_energy_gen.py`

- [ ] `WORKING-AS-DESIGNED guard` (lines 32-109, 78 LOC) - Move to tests/regression/ with rename; keep as design-intent regression guard.
- [ ] Verify: `pytest tests/repro_issues/test_bug_12_energy_gen.py` passes; LOC delta approximate 78

### Task 3.6: `tests/unit/ai/test_controllable_adapter_edge_cases.py`
**File:** `tests/unit/ai/test_controllable_adapter_edge_cases.py`
**Tests:** `pytest tests/unit/ai/test_controllable_adapter_edge_cases.py`

- [ ] `TestAttributeDelegationRemoved` (lines 339-365, 27 LOC) - Keep as documented removal guard.
- [ ] Verify: `pytest tests/unit/ai/test_controllable_adapter_edge_cases.py` passes; LOC delta approximate 27

### Task 3.7: `tests/integration/strategy/test_commands.py`
**File:** `tests/integration/strategy/test_commands.py`
**Tests:** `pytest tests/integration/strategy/test_commands.py`

- [ ] `test_handle_command` (lines 191-198, 8 LOC) - Remove.
- [ ] Verify: `pytest tests/integration/strategy/test_commands.py` passes; LOC delta approximate 8

### Task 3.8: `tests/unit/entities/test_ship_stat_querier.py`
**File:** `tests/unit/entities/test_ship_stat_querier.py`
**Tests:** `pytest tests/unit/entities/test_ship_stat_querier.py`

- [ ] `TestShipStatQuerierCachedSummary` (lines 252-257, 6 LOC) - Remove the empty class.
- [ ] Verify: `pytest tests/unit/entities/test_ship_stat_querier.py` passes; LOC delta approximate 6

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
