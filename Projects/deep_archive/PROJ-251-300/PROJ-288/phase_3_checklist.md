# Phase 3: ColonyDemographicView facade DTO

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-288 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `ColonyDemographicView` + `SpeciesDemographicView` frozen DTOs and `StrategySessionFacade.get_colony_demographic_view(planet_id)` method. UI panels in PROJ-289+ will read this single DTO instead of pulling from engines + projectors ad-hoc.

---

## Tasks

### Task 3.1: Define DTOs + write failing tests [Medium]
**File:** `tests/unit/strategy/facade/test_colony_demographic_view.py` (NEW)
**Tests:** `pytest tests/unit/strategy/facade/test_colony_demographic_view.py`

- [x] Test: uncolonized planet → facade returns None.
- [x] Test: colonized planet → returns view with expected planet_id + planet_name.
- [x] Test: species tuple ordered largest-first.
- [x] Test: each `SpeciesDemographicView` has populated habitability, happiness, growth_rate, food_ratio, food_allocation.
- [x] Test: `resource_projections` tuple includes every resource in `economy.population_consumption` (upkeep > 0 for each).
- [x] Test: `total_upkeep` dict sums across species per resource.
- [x] Test: multi-species multi-resource end-to-end snapshot matches manual calculation.

**Notes:** Added 10 tests in `tests/unit/strategy/facade/test_colony_demographic_view.py` covering the 7 listed cases plus three extras: `test_missing_planet_returns_none` (resolves a non-existent planet_id), `test_species_with_unknown_race_skipped` (save-drift defence — DTO drops species the registry can't resolve), and two `TestFrozenness` cases pinning the `@dataclass(frozen=True)` contract on both `ColonyDemographicView` and `SpeciesDemographicView`. Test helper `_facade_for(planet, race_registry, economy)` pre-seeds `facade._planet_index` and `facade._race_registry` so the implementation doesn't need to walk the galaxy/system tree to resolve the planet (keeps tests focused on the new method, not on facade plumbing).

### Task 3.2: Implement DTOs [Simple]
**File:** `game/strategy/facade/dto/colony_demographic_view.py` (NEW)
**Tests:** `pytest tests/unit/strategy/facade/test_colony_demographic_view.py`

- [x] Define `SpeciesDemographicView` frozen dataclass with fields per design.md § 3.
- [x] Define `ColonyDemographicView` frozen dataclass with:
  - `planet_id: int`
  - `planet_name: str`
  - `species: Tuple[SpeciesDemographicView, ...]` (largest-first)
  - `resource_projections: Tuple[ResourceProjection, ...]`
  - `total_upkeep: Mapping[str, float]` (immutable mapping; use `frozendict` from `types.MappingProxyType` or store a frozen tuple of tuples)

**Notes:** `total_upkeep` is typed as `Mapping[str, float]` but stored as a plain `dict` — `Mapping` is the read-only protocol so consumers can't mutate via index assignment without a type-check warning, and a `dict` is cheaper than a `MappingProxyType` wrapper or a tuple-of-tuples. Frozen-dataclass `__setattr__` blocks reassignment of the field itself. UI consumers should treat the dict as immutable. Both DTOs re-exported from `game/strategy/facade/dto/__init__.py` (FleetInfo / SystemInfo / ... package convention).

### Task 3.3: Implement `get_colony_demographic_view` on facade [Medium]
**File:** `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/test_colony_demographic_view.py`

- [x] Resolve `planet = galaxy.get_planet_by_id(planet_id)`.
- [x] Return None if planet is None OR planet.owner_id is None.
- [x] Build projector instance + race_registry.
- [x] For each species on planet.populations, build a `SpeciesDemographicView`:
  - Resolve `race_config = race_registry.get_race(pop.race_id)`; skip species whose race can't be resolved.
  - Compute habitability = `score_planet_for_race(planet, race_config)`.
  - Compute growth_rate = `projected_growth_rate(planet, pop, race_config, cfg)`.
  - Resolve race_name = `getattr(race_config, "race_name", "") or getattr(race_config, "name", None) or pop.race_id`.
- [x] Sort species by count descending.
- [x] Build resource_projections tuple from `projector.project(planet)`.
- [x] Compute total_upkeep = dict summing upkeep across species per resource.
- [x] Return the assembled `ColonyDemographicView`.

**Notes:** Used `self._get_planet_by_id(planet_id)` (the existing facade primitive that uses the lazy `_planet_index`) instead of `self._session.galaxy.get_planet_by_id` — keeps the facade method consistent with `get_planet`, `get_planets_at_hex`, etc. that already share the same resolver. New helper `_resolve_economy_config()` pulls `EconomyConfig` from `self._session.economy_config` if present, else falls back to `get_default_economy_config()` (lazy-loads `data/economy.json`) — avoids requiring every test session to wire the economy. Inline imports (`projected_growth_rate`, `score_planet_for_race`, `PlanetEconomyProjector`) keep the facade's top-level import surface narrow, matching the `get_race_registry` (PROJ-287) convention. All facade tests pass: 224/224 in `tests/unit/strategy/facade/`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 4: docs + cleanup)
