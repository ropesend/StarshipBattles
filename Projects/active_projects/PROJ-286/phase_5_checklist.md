# Phase 5: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-286 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update PROJ-284's existing docs to reflect multi-resource consumption. Run full sharded suite. Sign off.

---

## Tasks

### Task 5.1: Update strategy-layer doc section 8 [Medium]
**File:** `docs/systems/strategy_layer.md`

- [ ] Under `## 8. Colony Demographics Loop (PROJ-284)` → `### Data-driven food resource`:
  - Replace the single-resource schema example with the multi-resource schema.
  - Add explanation of MIN aggregation: "A colony is as well-fed as its worst-supplied resource."
  - Note the `ColonySpeciesConfig.last_consumption_ratios` transient dict and the computed `last_food_ratio` property.
  - Update the "Swapping the population food resource" recipe: now shows adding/removing entries in the dict rather than swapping a single id.

**Notes:**

### Task 5.2: Update services catalog [Simple]
**File:** `docs/04_SERVICES.md`

- [ ] Under `### Colony Demographics Loop (PROJ-284)`:
  - Update the `EconomyConfig` line to show `population_consumption: Dict[str, float]` + `primary_resource` property.
  - Update the `ColonySpeciesConfig` line: `last_consumption_ratios: Dict[str, float]` (transient) + `last_food_ratio: float` (computed MIN).
  - Update the `OrganicsConsumptionEngine` line to mention the multi-resource iteration.
  - Add a cross-reference: "See PROJ-286 for the evolution from single-resource to multi-resource consumption."

**Notes:**

### Task 5.3: CLAUDE.md review [Simple]
**File:** `CLAUDE.md`

- [ ] Review — the `get_default_* / set_default_*` callout is unchanged. No other patterns affected. Likely no-op.

**Notes:**

### Task 5.4: Final full sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green (apart from known persistent flakes — document any new failures).
- [ ] Confirm test count delta matches expectations: ~6 new tests added across Phases 2-4, plus 12 migrated tests that should still be counted.

**Notes:**

### Task 5.5: Update Current State + close project [Simple]

- [ ] Update `plan.md § Current State` to "ALL 5 PHASES COMPLETE — ready to close. Awaiting user sign-off."
- [ ] Verify `projects_index.md` shows PROJ-286 as Complete.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
