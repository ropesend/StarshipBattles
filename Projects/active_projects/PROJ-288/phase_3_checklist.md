# Phase 3: ColonyDemographicView facade DTO

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-288 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `ColonyDemographicView` + `SpeciesDemographicView` frozen DTOs and `StrategySessionFacade.get_colony_demographic_view(planet_id)` method. UI panels in PROJ-289+ will read this single DTO instead of pulling from engines + projectors ad-hoc.

---

## Tasks

### Task 3.1: Define DTOs + write failing tests [Medium]
**File:** `tests/unit/strategy/facade/test_colony_demographic_view.py` (NEW)
**Tests:** `pytest tests/unit/strategy/facade/test_colony_demographic_view.py`

- [ ] Test: uncolonized planet → facade returns None.
- [ ] Test: colonized planet → returns view with expected planet_id + planet_name.
- [ ] Test: species tuple ordered largest-first.
- [ ] Test: each `SpeciesDemographicView` has populated habitability, happiness, growth_rate, food_ratio, food_allocation.
- [ ] Test: `resource_projections` tuple includes every resource in `economy.population_consumption` (upkeep > 0 for each).
- [ ] Test: `total_upkeep` dict sums across species per resource.
- [ ] Test: multi-species multi-resource end-to-end snapshot matches manual calculation.

**Notes:**

### Task 3.2: Implement DTOs [Simple]
**File:** `game/strategy/facade/dto/colony_demographic_view.py` (NEW)
**Tests:** `pytest tests/unit/strategy/facade/test_colony_demographic_view.py`

- [ ] Define `SpeciesDemographicView` frozen dataclass with fields per design.md § 3.
- [ ] Define `ColonyDemographicView` frozen dataclass with:
  - `planet_id: int`
  - `planet_name: str`
  - `species: Tuple[SpeciesDemographicView, ...]` (largest-first)
  - `resource_projections: Tuple[ResourceProjection, ...]`
  - `total_upkeep: Mapping[str, float]` (immutable mapping; use `frozendict` from `types.MappingProxyType` or store a frozen tuple of tuples)

**Notes:**

### Task 3.3: Implement `get_colony_demographic_view` on facade [Medium]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/test_colony_demographic_view.py`

- [ ] Resolve `planet = galaxy.get_planet_by_id(planet_id)`.
- [ ] Return None if planet is None OR planet.owner_id is None.
- [ ] Build projector instance + race_registry.
- [ ] For each species on planet.populations, build a `SpeciesDemographicView`:
  - Resolve `race_config = race_registry.get_race(pop.race_id)`; skip species whose race can't be resolved.
  - Compute habitability = `score_planet_for_race(planet, race_config)`.
  - Compute growth_rate = `projected_growth_rate(planet, pop, race_config, cfg)`.
  - Resolve race_name = `getattr(race_config, "race_name", "") or getattr(race_config, "name", None) or pop.race_id`.
- [ ] Sort species by count descending.
- [ ] Build resource_projections tuple from `projector.project(planet)`.
- [ ] Compute total_upkeep = dict summing upkeep across species per resource.
- [ ] Return the assembled `ColonyDemographicView`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 4: docs + cleanup)
