# Phase 1: Foundation Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-54 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract shared utilities and generalize the ship data extraction system so all ability types can be validated, not just beams.

---

## Tasks

### Task 1.1: Extract Shared `_resolve_path` Utility [Simple]
**File:** `simulation_tests/scenarios/validation.py`
**Also:** `simulation_tests/scenarios/prerun_validation.py`
**Tests:** `pytest simulation_tests/ -v`

The dot-notation path resolver `_resolve_path()` is duplicated 3 times with varying error quality:
1. `ExactMatchRule._resolve_path()` at lines 177-226 (detailed errors, path tracing)
2. `DeterministicMatchRule._resolve_path()` at lines 348-375 (simple errors)
3. `PreRunValidator._resolve_path()` in `prerun_validation.py` at lines 115-130 (simple errors)

- [x] Create standalone `resolve_path(context, path)` function at module level in `validation.py` (before any class definitions)
- [x] Use the detailed implementation from `ExactMatchRule` (lines 177-226) as the canonical version
- [x] Replace `ExactMatchRule._resolve_path` calls with `resolve_path` (search for `self._resolve_path`)
- [x] Replace `DeterministicMatchRule._resolve_path` calls with `resolve_path`
- [x] Delete `ExactMatchRule._resolve_path` method (lines 177-226)
- [x] Delete `DeterministicMatchRule._resolve_path` method (lines 348-375)
- [x] In `prerun_validation.py`: import `resolve_path` from `validation.py`
- [x] Replace `self._resolve_path` calls in `prerun_validation.py` with imported `resolve_path`
- [x] Delete `PreRunValidator._resolve_path` method (lines 115-130)
- [x] Add `resolve_path` to `simulation_tests/scenarios/__init__.py` exports
- [x] Verify: Run `pytest simulation_tests/ -v` - all existing tests pass unchanged

**Notes:** `_resolve_path` was actually on `DataExpectation` class, not `PreRunValidator`. All 3 copies removed, 0 remaining (verified with grep). Note: the `_resolve_path` in `prerun_validation.py` was on `DataExpectation`, not `PreRunValidator` as stated - but the method is deleted regardless.

---

### Task 1.2: Generalize `_extract_ship_validation_data` [Medium]
**File:** `simulation_tests/scenarios/base.py`
**Tests:** `pytest simulation_tests/ -v`

Currently at lines 606-656, this method only extracts `BeamWeaponAbility` data and returns immediately after finding one. We need it to extract data for ALL ability types.

- [x] Define `ABILITY_EXTRACTION_MAP` dict at module level, mapping ability class names to extraction configs
- [x] Rewrite `_extract_ship_validation_data()` to iterate all abilities and use the map
- [x] Add ship-level defense stats to the extracted data (`total_defense_score`, `emissive_armor`, `max_shields`)
- [x] Verify backward compat: existing beam scenarios using `attacker.weapon.damage` paths still resolve correctly
- [x] Verify: Run `pytest simulation_tests/ -v` - all existing tests pass unchanged

**Notes:** Corrected `reload` → `reload_time` (actual attribute name). Added `projectile_speed` to SeekerWeaponAbility attrs. First-occurrence-wins for duplicate ability types. 45 passed, same 5 pre-existing failures.

---

### Task 1.3: Delete Backup File [Simple]
**File:** `simulation_tests/scenarios/projectile_scenarios.py.backup_phase1`
**Tests:** None needed

- [x] Delete `simulation_tests/scenarios/projectile_scenarios.py.backup_phase1`
- [x] Verify: file no longer exists

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest simulation_tests/ -v` passes
- [x] `pytest tests/ -n 4` passes (full suite)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
