# Phase 3: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-290 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Docs updates, full sharded suite, project close.

---

## Tasks

### Task 3.1: Update strategy-layer doc [Simple]
**File:** `docs/systems/strategy_layer.md`

- [ ] Under §9 Colony Economy Multiplier, add a "Treasury & Planet Detail Integration" subsection:
  - Treasury "Population Upkeep" row aggregates per-resource drain empire-wide.
  - Uncolonized planet detail shows 0-100 habitability per resident species, best-fit first.

**Notes:**

### Task 3.2: Cross-reference production_system.md [Simple]
**File:** `docs/systems/production_system.md`

- [ ] Add a one-liner under the Habitability Multiplier section: "Empire Treasury shows aggregated populace upkeep; planet detail shows per-species 0-100 habitability on uncolonized worlds (PROJ-290)."

**Notes:**

### Task 3.3: Full sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green.
- [ ] Net new tests: ~15 (aggregator + treasury row + uncolonized-habitability + edge cases).

**Notes:**

### Task 3.4: Manual smoke [Simple]
**Tests:** Manual

- [ ] Open Treasury → see Population Upkeep row when empire has populations; absent on fresh game.
- [ ] Click uncolonized planet → habitability section lists all empire species with 0-100 scores, sorted descending.
- [ ] Click colonized planet → habitability section NOT shown (colonized branch renders per-species sub-blocks).

**Notes:** DEFERRED TO USER.

### Task 3.5: Close project [Simple]

- [ ] Update `plan.md § Current State` to complete.
- [ ] Verify `projects_index.md`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
