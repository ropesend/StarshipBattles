# Phase 2: PlanetEconomyProjector service

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-288 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** New service `PlanetEconomyProjector` returns per-planet per-resource projections (harvest / upkeep / yard / net). Move `compute_planet_production` out of the UI file. Full test coverage including multi-resource upkeep + multi-queue yard aggregation.

---

## Tasks

### Task 2.1: Define `ResourceProjection` dataclass + write failing tests [Medium]
**File:** `tests/unit/strategy/services/test_planet_economy_projector.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_planet_economy_projector.py`

- [ ] Test: uncolonized planet with harvesters → project has harvest > 0, upkeep = 0 (no pops), yard = 0 (no queues), net = harvest.
- [ ] Test: multi-species fed colony → upkeep per resource = `sum(pop * allocation * per_pop_rate)` per resource in `economy.population_consumption`.
- [ ] Test: single queued complex → yard drain per resource = `production_rate[res]` for whatever's being built.
- [ ] Test: multi-queue colony (planetary yard + 2 shipyards, each building something) → yard drain sums across queues.
- [ ] Test: empty queue → yard drain = 0.
- [ ] Test: net column = harvest - upkeep - yard for every resource.

**Notes:**

### Task 2.2: Implement `PlanetEconomyProjector` [Complex]
**File:** `game/strategy/services/planet_economy_projector.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_planet_economy_projector.py`

- [ ] Define `ResourceProjection` frozen dataclass.
- [ ] Implement `PlanetEconomyProjector.__init__(*, registries, economy_config, race_registry)`.
- [ ] Implement `.project(planet) -> Dict[resource_id, ResourceProjection]`.
- [ ] Sub-method `_project_harvest(planet)` — moves the current `compute_planet_production` logic from `planet_report_panel.py:498`. Preserves signature + behavior.
- [ ] Sub-method `_project_upkeep(planet)` — iterates `planet.populations` × `economy.population_consumption.items()`.
- [ ] Sub-method `_project_yard_drain(planet)` — iterates `planet.construction_queue` (base) + each `facility.construction_queue` where `facility.is_shipyard`. For each active queue's head item, compute per-turn drain as `production_rate[res]`. Sum across queues.
- [ ] Apply habitability multiplier to both harvest AND yard drain (PROJ-285 stacking rule).

**Notes:**

### Task 2.3: Migrate UI caller [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Delete the old `compute_planet_production` function body; keep a thin compatibility wrapper OR update all call sites to import from `game.strategy.services.planet_economy_projector`.
- [ ] Verify no layer violation: UI imports strategy services (OK); strategy doesn't import UI (no change).

**Notes:** PROJ-289 will further refactor this panel to consume `ColonyDemographicView` instead of calling the projector directly. For PROJ-288 just stop the layer violation.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3: facade DTO)
