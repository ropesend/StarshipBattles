# Phase 3: Documentation update

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-279 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (verified 2026-04-18)
**Objective:** Update Combat Lab and simulation-testing docs to reflect (a) the deletion of the `to_spec` monkey-patch, (b) the new explicit-composition contract, (c) the documented escape hatch for subclass `to_spec` overrides.

---

## Tasks

### Task 3.1: Update `docs/guides/simulation_testing.md` [Simple]
**File:** `docs/guides/simulation_testing.md`
**Tests:** N/A

- [x] Updated "TestScenario Class" section to describe `build_test_battle_spec(scenario)` as the production entry, with PROJ-279 callout
- [x] Added "Authoring rule (PROJ-279)" blockquote: do NOT add `to_spec` to scenarios as convenience; only legitimate use is the documented escape hatch for non-canonical layouts
- [x] Updated the worked example's inline comment to drop the misleading "inherited from TestScenario" wording

**Notes:**

### Task 3.2: Update `combat_lab/COMBAT_LAB_DOCUMENTATION.md` [Simple]
**File:** `combat_lab/COMBAT_LAB_DOCUMENTATION.md`
**Tests:** N/A

- [x] Replaced the `to_spec()` method definition in the TestScenario API description with a comment block explaining the new contract: production calls `build_test_battle_spec(scenario)` directly; subclasses can opt-in to overrides for custom layouts
- [x] Added a PROJ-279 footer note documenting the deletion of the historical monkey-patch

**Notes:** The existing "PROJ-270 Phase 11" footer also kept (different concern — `setup` → `wire_ships` migration); PROJ-279 footer added separately.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All `to_spec` references in docs reflect the new explicit-composition contract
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to closure
