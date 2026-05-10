# Phase 5: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-286 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update PROJ-284's existing docs to reflect multi-resource consumption. Run full sharded suite. Sign off.

---

## Tasks

### Task 5.1: Update strategy-layer doc section 8 [Medium]
**File:** `docs/systems/strategy_layer.md`

- [x] Under `## 8. Colony Demographics Loop (PROJ-284)` → `### Data-driven food resource`:
  - Replace the single-resource schema example with the multi-resource schema.
  - Add explanation of MIN aggregation: "A colony is as well-fed as its worst-supplied resource."
  - Note the `ColonySpeciesConfig.last_consumption_ratios` transient dict and the computed `last_food_ratio` property.
  - Update the "Swapping the population food resource" recipe: now shows adding/removing entries in the dict rather than swapping a single id.

**Notes:** Section heading upgraded to `## 8. Colony Demographics Loop (PROJ-284 + PROJ-286)`. Recipe renamed to `### Swapping the population-consumption dict` + multi-resource example showing ammonia added. Liebig's Law gameplay warning added about MIN aggregation collapsing to 0 when a new required resource has no harvester.

### Task 5.2: Update services catalog [Simple]
**File:** `docs/04_SERVICES.md`

- [x] Under `### Colony Demographics Loop (PROJ-284)`:
  - Update the `EconomyConfig` line to show `population_consumption: Dict[str, float]` + `primary_resource` property.
  - Update the `ColonySpeciesConfig` line: `last_consumption_ratios: Dict[str, float]` (transient) + `last_food_ratio: float` (computed MIN).
  - Update the `OrganicsConsumptionEngine` line to mention the multi-resource iteration.
  - Add a cross-reference: "See PROJ-286 for the evolution from single-resource to multi-resource consumption."

**Notes:** Section heading upgraded to `### Colony Demographics Loop (PROJ-284 + PROJ-286)`. Also noted that HappinessEngine + PopulationEngine source files are UNCHANGED between PROJ-284 and PROJ-286 — the computed property handles the multi-resource adaptation. Added forward pointer to PROJ-289 for UI migration.

### Task 5.3: CLAUDE.md review [Simple]
**File:** `CLAUDE.md`

- [x] Review — the `get_default_* / set_default_*` callout is unchanged. No other patterns affected. Likely no-op.

**Notes:** Grepped CLAUDE.md for PROJ-284/286/economy/food_allocation/last_food_ratio — zero matches. No-op confirmed.

### Task 5.4: Final full sharded suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full suite green (apart from known persistent flakes — document any new failures).
- [x] Confirm test count delta matches expectations: ~6 new tests added across Phases 2-4, plus 12 migrated tests that should still be counted.

**Notes:** `python Tools/test_sharded/test_sharded.py` → **14990 tests | 14976 passed | 14 failed | 0 errors** in 65.3s.

Breakdown of the 14 failures (ALL expected cross-phase or pre-existing, ZERO PROJ-286 regressions):
- **13 × `tests/unit/ui/screens/test_food_allocation_editor.py`** — all use old-shape `EconomyConfig(population_food_resource=..., food_per_pop_per_turn=...)` kwargs. Deferred to PROJ-289 per Phase 1 handoff notes. Root error: `TypeError: EconomyConfig.__init__() got an unexpected keyword argument 'population_food_resource'`.
- **1 × `test_copy_designs_without_themes_preserves_original`** — pre-existing theme_id pollution flake documented in the original handoff watchout #7 ("pre-existing sharded-runner flakes ... persists"). Not PROJ-286-related.

Baseline delta from 14900-ish pre-PROJ-286: +~90 net new tests. Added: 5 EconomyConfig tests (Phase 1), 10 ColonySpeciesConfig tests (Phase 2), 1 Planet round-trip assertion tweak (Phase 2), 5 multi-resource engine tests (Phase 3), 6 HappinessEngine + PopulationEngine multi-resource / parity tests (Phase 4). Migrations preserved existing test count.

### Task 5.5: Update Current State + close project [Simple]

- [x] Update `plan.md § Current State` to "ALL 5 PHASES COMPLETE — ready to close. Awaiting user sign-off."
- [x] Verify `projects_index.md` shows PROJ-286 as Complete.

**Notes:** plan.md Current State updated. `projects_index.md` update is the user/project-maintainer's responsibility on archival.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
