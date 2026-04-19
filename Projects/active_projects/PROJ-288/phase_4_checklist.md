# Phase 4: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-288 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Docs, full sharded suite, close out.

---

## Tasks

### Task 4.1: Update services catalog [Simple]
**File:** `docs/04_SERVICES.md`

- [ ] Add `### Planet Economy Projector (PROJ-288)` under strategy-layer services:
  - `PlanetEconomyProjector` at `game/strategy/services/planet_economy_projector.py`.
  - `ResourceProjection` frozen dataclass.
  - Cross-reference `projected_growth_rate` in `colony_output.py`.
  - Cross-reference `ColonyDemographicView` DTO on the facade.

**Notes:**

### Task 4.2: Update strategy-layer doc [Simple]
**File:** `docs/systems/strategy_layer.md`

- [ ] Under §8 (Colony Demographics Loop) or §9 (Economy Multiplier), add a "Projection helpers" paragraph pointing to `colony_output.projected_growth_rate` and `PlanetEconomyProjector.project`.
- [ ] Note the equivalence contract: projection math tracks engine math; CI pins parity via the integration test.

**Notes:**

### Task 4.3: Final full sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green.
- [ ] Net new tests: ~20 (6 TestProjectedGrowthRate + 6 TestPlanetEconomyProjector + 7 TestColonyDemographicView + 12 equivalence-matrix).

**Notes:**

### Task 4.4: Close project [Simple]

- [ ] Update `plan.md § Current State` to complete.
- [ ] Verify `projects_index.md` shows PROJ-288 complete.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
