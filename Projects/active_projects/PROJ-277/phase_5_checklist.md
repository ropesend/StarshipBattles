# Phase 5: Migrate Existing Comparison Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-277 5`

**Status:** Not Started
**Objective:** Every ComparisonScenario subclass migrated to new `build_baseline_spec` / `build_variant_spec` / `validate(ab_outcome)` API.

---

## Tasks

### Task 5.1: Enumerate ComparisonScenario subclasses [Simple]
**File:** Multiple — read-only sweep
**Tests:** N/A

- [ ] Run `grep -rn "class.*(ComparisonScenario)" combat_lab/` — list every subclass
- [ ] For each: note which file, which test IDs
- [ ] Write to `findings/comparison_scenario_subclasses.md`
- [ ] Expected: ~10-20 classes across pipeline / stacking / seeker / modifier scenarios

**Notes:**

### Task 5.2: Migrate in groups of 5 [Complex]
**File:** Multiple ComparisonScenario subclasses
**Tests:** `python -m combat_lab.run_tests -v`

- [ ] For each subclass:
  - Replace old attribute-based baseline setup (e.g. `self._baseline_outcome = ...`) with `build_baseline_spec(base_spec)` returning a modified spec
  - Replace variant setup similarly with `build_variant_spec`
  - Update `validate()` signature to take `ab_outcome: ABBattleOutcome`
  - Read `ab_outcome.baseline_outcome`, `ab_outcome.variant_outcome`, `ab_outcome.baseline_telemetry`, `ab_outcome.variant_telemetry` instead of stashed attributes
  - Remove all `_baseline_*` references
- [ ] Group 1: 5 subclasses — migrate + run test for each
- [ ] Group 2: 5 subclasses — migrate + run test for each
- [ ] Continue until all migrated

**Notes:**

### Task 5.3: Full Combat Lab suite [Medium]
**File:** N/A
**Tests:** `python -m combat_lab.run_tests`

- [ ] Complete Combat Lab suite runs
- [ ] Baseline test count maintained (per memory: combat_lab tests in hundreds)
- [ ] Zero failures
- [ ] Grep: `grep -rn "_baseline_outcome\|_baseline_telemetry\|_run_baseline_battle\|_visual_baseline" combat_lab/` returns ZERO results (except in deleted code — confirm deleted)

**Notes:**

### Task 5.4: Full pytest suite [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green
- [ ] Baseline maintained

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-277 5`
