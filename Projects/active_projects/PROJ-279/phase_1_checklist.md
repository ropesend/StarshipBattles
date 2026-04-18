# Phase 1: Audit & migrate all `scenario.to_spec()` callers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-279 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Find every caller of `scenario.to_spec()` (production + tests + dynamic `getattr` lookups) and replace with explicit `build_test_battle_spec(scenario, registries)` calls. Do not delete the monkey-patch yet — Phase 2 does that, after Phase 1 verifies all callers migrated.

---

## Tasks

### Task 1.1: Audit all callers [Simple]
**File:** `.agent_reports/PROJ-279-caller-audit/report.md` (new — for tracking)
**Tests:** N/A (research task)

- [ ] Grep for `\.to_spec\(` across the entire repo (production + tests)
- [ ] Grep for `getattr.*to_spec` to catch dynamic lookups
- [ ] Grep for `hasattr.*to_spec` to catch capability checks
- [ ] Document each hit with file:line, caller type (prod/test), and intended replacement
- [ ] Confirm zero callers in non-Combat Lab code (the patch only attaches to `TestScenario`, but check anyway)

**Notes:**

### Task 1.2: Migrate production callers [Medium]
**File:** Multiple (see Task 1.1 audit output)
**Tests:** `pytest tests/unit/combat_lab/ -n 4` after each file changed

For each production caller identified in Task 1.1:
- [ ] Add explicit import: `from combat_lab.spec_compiler import build_test_battle_spec`
- [ ] Replace `scenario.to_spec(registries)` with `build_test_battle_spec(scenario, registries)`
- [ ] Run targeted tests for the changed file
- [ ] Verify behavior unchanged (same spec produced)

**Notes:**

### Task 1.3: Migrate test callers [Medium]
**File:** Multiple test files (see Task 1.1 audit output)
**Tests:** `pytest tests/` for each migrated test

- [ ] For each test that calls `scenario.to_spec()`, replace with `build_test_battle_spec(scenario, registries)`
- [ ] Add explicit import to each test file
- [ ] Run tests, confirm pass

**Notes:**

### Task 1.4: Verify no dynamic callers remain [Simple]
**File:** N/A (verification)
**Tests:** Grep + full sharded suite

- [ ] Re-grep `\.to_spec\(`, `getattr.*to_spec`, `hasattr.*to_spec` — confirm zero hits outside [combat_lab/spec_compiler.py](../../../combat_lab/spec_compiler.py) itself
- [ ] Run full sharded suite: `python Tools/test_sharded/test_sharded.py` — all green

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Caller audit report saved to `.agent_reports/PROJ-279-caller-audit/`
- [ ] Full sharded test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2 (delete the monkey-patch)
