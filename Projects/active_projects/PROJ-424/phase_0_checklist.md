# Phase 0: Preflight + remaining-consumer inventory

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-424 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** none
**Review Mode:** lightweight
**Files (planned):** (no production edits — inventory only)

**Objective:** capture the current consumer inventory for the duplicated metadata surfaces and confirm the per-constant production reader counts match the TD-03 audit. Produce a record of every test file that imports the duplicated constants directly so Phases 4 and 5 know what to update.

---

## Tasks

### Task 0.1: Run the two TD-03 grep baselines [Simple]
**File:** `Projects/active_projects/PROJ-424/findings/phase_0_baseline.md` (worker-owned, optional)
**Tests:** n/a (preflight only)

- [ ] `rg -n "MOVEMENT_ORDER_TYPES|ACTION_ORDER_TYPES|PLANET_ACTION_ORDER_TYPES|PLANET_FMS_ACTION_ORDER_TYPES|ORDER_TO_ABILITY_MAP" game tests docs` and capture the output
- [ ] `rg -n "subcategories\s*=|@command_spec\(" game/strategy/engine/handlers game/strategy/engine/commands` and capture the output
- [ ] Verify the per-constant reader counts match the [design.md](design.md) "Consumer Inventory" section (any drift means a new consumer landed and the manifest needs updating)
- [ ] Verify: `PLANET_FMS_ACTION_ORDER_TYPES` still has exactly one production consumer (`game/strategy/engine/action_execution_engine.py`)

**Notes:** [Filled during implementation]

### Task 0.2: Inventory tests that import duplicated constants [Simple]
**File:** `Projects/active_projects/PROJ-424/findings/phase_0_test_imports.md` (worker-owned, optional)
**Tests:** n/a

- [ ] From the Task 0.1 grep over `tests/`, list every test module that imports any of the five constants by name
- [ ] Verify the list is a superset of the eight test modules already enumerated in [manifest.md](manifest.md). Any extras are added to the manifest in this phase
- [ ] Verify: no new test files outside the manifest will need touches in Phases 3/4/5

**Notes:** [Filled during implementation]

### Task 0.3: Confirm no new command handlers added since TD-03 verification [Simple]
**File:** n/a
**Tests:** n/a

- [ ] Compare the `@command_spec(...)` count from Task 0.1 against the 41 command DTOs noted in the TD-03 audit
- [ ] Verify: count matches, or any delta is documented so Phase 1's "exactly five planet_fms specs" assertion is calibrated correctly

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Baseline outputs captured (in session file or findings dir)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 1
