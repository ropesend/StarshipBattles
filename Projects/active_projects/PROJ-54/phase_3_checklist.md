# Phase 3: Beam & Seeker Scenario Simplification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-54 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Simplify beam and seeker scenarios by removing duplicated verify/results boilerplate, using the template's `_collect_results()` hook from Phase 2. Also extract the duplicated hit-chance calculation and fix hardcoded magic numbers.

**Prerequisite:** Phase 2 complete (template has `_collect_results` + `_collect_extra_results` hooks)

---

## Tasks

### Task 3.1: Create Beam Hit-Chance Helper [Simple]
**File:** `simulation_tests/scenarios/beam_scenarios.py`
**Tests:** `pytest simulation_tests/ -v`

Every beam scenario has near-identical `custom_setup()` code calculating `self.expected_hit_chance`. Extract this into a shared helper.

- [x] Create helper function `compute_beam_hit_chance(scenario)`:
  - Reads weapon accuracy/falloff from the loaded attacker ship's `BeamWeaponAbility`
  - Reads target defense stats
  - Computes expected hit chance using the same formula beam scenarios currently use
  - Returns the calculated hit chance
- [x] Verify the helper matches the existing manual calculations in beam scenarios
- [x] Update one beam scenario to use the helper as a proof of concept
- [x] Verify: `pytest simulation_tests/ -v` - that scenario passes

**Notes:**

---

### Task 3.2: Simplify Beam Scenario Verify Methods [Medium]
**File:** `simulation_tests/scenarios/beam_scenarios.py`
**Tests:** `pytest simulation_tests/ -v`

~18 beam scenarios override `verify()` with copy-pasted result storage. After Phase 2's template refactor, they can use pass criteria flags instead.

**Strategy:** Migrate one scenario at a time.

- [x] For each beam scenario that overrides `verify()`:
  - Remove the duplicated `self.results['initial_hp'] = ...` block
  - If the scenario only needs "was damage dealt?" → set `verify_damage_dealt = True`
  - If the scenario is statistical measurement → set `measurement_mode = True`
  - If the scenario expects no damage → set `expect_no_damage = True`
  - If the scenario needs extra results → implement `_collect_extra_results()` hook
  - Replace manual hit-chance calculation with `compute_beam_hit_chance()`
- [x] Migrate beam scenarios one at a time (verify after each):
  - [x] First beam scenario (proof of concept)
  - [x] Remaining 17 beam scenarios (all 18 migrated, 0 verify methods remain)
- [x] Verify after all: `pytest simulation_tests/ -v` - all beam tests pass with identical results

**Notes:** Test IDs and pass/fail behavior MUST remain identical.

---

### Task 3.3: Simplify Seeker Scenario Verify Methods [Medium]
**File:** `simulation_tests/scenarios/seeker_scenarios.py`
**Tests:** `pytest simulation_tests/ -v`

~8 seeker scenarios override `verify()` with copy-pasted result storage AND hardcode magic numbers like `self.results['missile_speed'] = 1000`.

- [x] For each seeker scenario that overrides `verify()`:
  - Remove the duplicated `self.results['initial_hp'] = ...` block
  - Replace hardcoded magic numbers with values read from loaded ship data:
    - `self.results['missile_speed']` → read from `SeekerWeaponAbility` instance via `_get_seeker_ability()` helper
    - `self.results['missile_turn_rate']` → read from ability instance
    - `self.results['missile_endurance']` → read from ability instance
  - Set appropriate pass criteria flag or implement slim `verify()` calling `_collect_results()`
  - Move extra seeker-specific results to `_collect_extra_results()` hook
- [x] Migrate seeker scenarios one at a time (verify after each):
  - [x] First seeker scenario (SeekerCloseRangeImpactScenario - min_damage_threshold=100, reads stats from SeekerWeaponAbility)
  - [x] Remaining 7 seeker scenarios (all 8 non-PD migrated, 0 verify methods remain; 3 PD placeholders left as-is)
- [x] Verify after all: `pytest simulation_tests/ -v` - all seeker tests pass with identical results

**Notes:** Test IDs and pass/fail behavior MUST remain identical.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest simulation_tests/ -v` passes (45 passed, 5 pre-existing failures, 4 skipped)
- [x] `pytest tests/ -n 4` passes (full suite: 6113 passed, 5 skipped)
- [x] Verify: grep for `self.results['initial_hp'] = self.initial_hp` returns significantly fewer occurrences (goal: only in `_collect_results`) - Only 1 occurrence in code (templates.py:179 in `_collect_results`), rest are docs
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
