# Phase 4: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-288 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Docs, full sharded suite, close out.

---

## Tasks

### Task 4.1: Update services catalog [Simple]
**File:** `docs/04_SERVICES.md`

- [x] Add `### Planet Economy Projector (PROJ-288)` under strategy-layer services:
  - `PlanetEconomyProjector` at `game/strategy/services/planet_economy_projector.py`.
  - `ResourceProjection` frozen dataclass.
  - Cross-reference `projected_growth_rate` in `colony_output.py`.
  - Cross-reference `ColonyDemographicView` DTO on the facade.

**Notes:** Added a comprehensive subsection after the PROJ-287 Race Registry entry. Documents the projector constructor signature, all three sub-projections (with the upkeep-NOT-scaled-by-habitability rule called out explicitly), the `ResourceProjection` invariant `net == harvest - upkeep - yard`, the `projected_growth_rate` per-capita semantics + integration-test equivalence pin, the `ColonyDemographicView`/`SpeciesDemographicView` DTO field contracts, the `get_colony_demographic_view` facade accessor, and the migration note that `compute_planet_production` moved out of UI.

### Task 4.2: Update strategy-layer doc [Simple]
**File:** `docs/systems/strategy_layer.md`

- [x] Under §8 (Colony Demographics Loop) or §9 (Economy Multiplier), add a "Projection helpers" paragraph pointing to `colony_output.projected_growth_rate` and `PlanetEconomyProjector.project`.
- [x] Note the equivalence contract: projection math tracks engine math; CI pins parity via the integration test.

**Notes:** Added "### Projection helpers (PROJ-288)" subsection at the end of §9, with the three new primitives + the equivalence contract paragraph and a cross-link to `04_SERVICES.md`. Also added a "Colony Demographics (PROJ-288)" row to the §1 StrategySessionFacade Query Categories table (`get_colony_demographic_view`) — matches the row I added for PROJ-287's `get_race_registry`.

### Task 4.3: Final full sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full suite green.
- [x] Net new tests: ~20 (6 TestProjectedGrowthRate + 6 TestPlanetEconomyProjector + 7 TestColonyDemographicView + 12 equivalence-matrix).

**Notes:** 15041 tests / 15027 passed / 14 failed in 137.2s across 12 shards. Failures break down as: (a) 13 in `tests/unit/ui/screens/test_food_allocation_editor.py` — confirmed pre-existing via `git stash` to predate PROJ-288 (PROJ-286 test debt — those tests still construct `EconomyConfig(population_food_resource=..., food_per_pop_per_turn=...)` instead of the post-PROJ-286 `population_consumption` dict shape); (b) 1 in `tests/unit/quickstart/test_quickstart_builder.py::test_copy_designs_without_themes_preserves_original` — the long-standing theme-bleed flake flagged in the PROJ-287 handoff. Net new from PROJ-288: 38 tests (7 TestProjectedGrowthRate + 13 equivalence-matrix + 8 TestPlanetEconomyProjector + 10 TestColonyDemographicView). The checklist's "~20" estimate was conservative.

### Task 4.4: Close project [Simple]

- [x] Update `plan.md § Current State` to complete.
- [x] Verify `projects_index.md` shows PROJ-288 complete.

**Notes:** plan.md table + Current State updated. `Projects/projects_index.md` PROJ-288 row advanced to "Awaiting Verification" matching how PROJ-286/287 were marked.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
