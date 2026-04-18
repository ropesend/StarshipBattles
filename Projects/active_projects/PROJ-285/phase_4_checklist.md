# Phase 4: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-285 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Document the habitability-to-production pipeline. Record the population-weighted-average choice, the per-turn cache, and the stacking behavior with existing boosters.

---

## Tasks

### Task 4.1: Update production docs [Medium]
**File:** `docs/systems/production_system.md`

- [ ] Add a section "Habitability Multiplier (PROJ-285)" covering:
  - Formula: harvest and production rates are multiplied by `planet_habitability_multiplier(planet, race_registry)`.
  - Population-weighted mean across species.
  - Uncolonized planet default = 1.0.
  - Per-turn caching via `Planet.get_cached_habitability_multiplier`.
  - Stacks multiplicatively with existing `BuildRateBooster` / `ResourceHarvestBooster`.

### Task 4.2: Update strategy-layer docs [Simple]
**File:** `docs/systems/strategy_layer.md`

- [ ] Reference the new `colony_output.py` helper in the post-tick pipeline section.
- [ ] Note that habitability now affects both population (PROJ-283/PROJ-284) AND economy (PROJ-285).

### Task 4.3: Update services catalog [Simple]
**File:** `docs/04_SERVICES.md`

- [ ] Add entry for `colony_output.py::planet_habitability_multiplier`.
- [ ] Note the per-turn cache on `Planet`.

### Task 4.4: Update CLAUDE.md if patterns changed [Simple]
**File:** `CLAUDE.md`

- [ ] Review — add a short callout if the per-turn-cache-on-planet pattern warrants broadcast. Otherwise no-op.

### Task 4.5: Final verification [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green.
- [ ] Manual end-to-end from plan.md Verification section.
- [ ] PROJ-285 plan.md Current State updated to "Complete, ready to close."

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
