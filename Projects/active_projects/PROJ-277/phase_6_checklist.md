# Phase 6: Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-277 6`

**Status:** Not Started
**Objective:** Document A/B scenarios as first-class pattern; update memory.

---

## Tasks

### Task 6.1: Add "Writing A/B Scenarios" section [Medium]
**File:** `docs/guides/simulation_testing.md`
**Tests:** Manual review

- [ ] Add new section titled "A/B Comparison Scenarios"
- [ ] Explain the `ComparisonScenario` pattern: `build_baseline_spec`, `build_variant_spec`, `validate(ab_outcome)`
- [ ] Example: a shield-booster complex A/B where baseline has no complex and variant applies one
- [ ] Show how to read `ab_outcome.baseline_outcome.teams[0].ships[0].stats.damage_dealt` vs variant
- [ ] Document the visual-baseline rendering mode — validation STILL RUNS

**Notes:**

### Task 6.2: Update memory [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md`
**Tests:** Manual

- [ ] Add bullet: "ComparisonScenario refactored in PROJ-277 — A/B runs are now first-class via ABBattleRunner; scenarios no longer embed run_battle(); validate() takes ABBattleOutcome; visual-baseline rendering is orthogonal to validation"
- [ ] Remove any stale references to `_baseline_outcome` / `_run_baseline_battle` / `_run_validation` override pattern

**Notes:**

### Task 6.3: Final regression sweep [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py` + `python -m combat_lab.run_tests`

- [ ] Full suites green

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update plan.md — mark project COMPLETE
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-277 6`
- [ ] User verification: manual A/B scenario visual baseline mode — validate() runs, output shown
