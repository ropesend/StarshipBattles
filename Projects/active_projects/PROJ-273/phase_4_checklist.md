# Phase 4: Glob-Driven Coverage Test

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-273 4`
> 2. Only proceed if output shows PASSED

**Status:** Not Started
**Objective:** Replace the hardcoded 10-design list in `test_unified_entry_guard.py` with a glob over every `qs_*_complex.json`. Future content additions auto-covered.

---

## Tasks

### Task 4.1: Write glob-based coverage test [Medium]
**File:** `tests/unit/simulation/combat/test_ability_stat_registry.py`
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py::test_no_placeholder_from_any_real_complex -v`

- [ ] Add `test_no_placeholder_from_any_real_complex()` function
- [ ] Use `Paths.STARTER_DESIGNS_DIR.glob("qs_*_complex.json")` to enumerate all complex designs
- [ ] For each design: load JSON, walk its components via `_iter_components` (or similar helper — reuse from `battle_setup/spec_compiler.py` or move to a shared location)
- [ ] Call `emit_entries_for_ability` for each component ability
- [ ] Assert every emitted `ModifierEntry` has `effect.stat_key != "placeholder"` (placeholder strings were deleted in PROJ-271 Phase 9; any regression to them must fail this test)
- [ ] Assert zero abilities that are in the registry emit empty entries (indicates registry/data mismatch)

**Notes:**

### Task 4.2: Write unknown-ability detection test [Medium]
**File:** `tests/unit/simulation/combat/test_ability_stat_registry.py`
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py::test_all_complex_abilities_in_registry -v`

- [ ] Add `test_all_complex_abilities_in_registry()` function
- [ ] Iterate every `qs_*_complex.json` file
- [ ] For each component ability with a non-SELF scope: assert `ability_name in ABILITY_STAT_REGISTRY`
- [ ] If an ability is found that ISN'T in the registry, fail with a clear message pointing at the design file and ability name
- [ ] This is the forward-compat guard: adding a new complex design with an unmapped ability will fail immediately, not silently drop at runtime

**Notes:**

### Task 4.3: Retire hardcoded list in existing guard [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`
**Tests:** `pytest tests/unit/simulation/test_unified_entry_guard.py -v`

- [ ] Locate `test_no_placeholder_from_any_real_complex` at lines ~540-563
- [ ] Either delete it (coverage moved to new test) OR rewrite it to delegate to the new glob-based version
- [ ] If deleted: update the test module's docstring to point at the new location
- [ ] Run guard suite — still passes

**Notes:**

### Task 4.4: Add new complex design as positive control [Medium]
**File:** `data/designs/qs_sector_test_coverage_complex.json` (TEMPORARY — revert at end)
**Tests:** `pytest tests/unit/simulation/combat/test_ability_stat_registry.py -v`

- [ ] Temporarily create a minimal qs_*_complex.json file with one known ability
- [ ] Run the glob tests — they should pick it up automatically
- [ ] Verify no failures (because ability IS in registry)
- [ ] Temporarily modify it to reference an unknown ability (e.g., "ThrustBooster" — not in registry)
- [ ] Run `test_all_complex_abilities_in_registry` — should fail with clear message
- [ ] **DELETE** the temporary design file
- [ ] Re-run tests to confirm clean state

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-273 4`
