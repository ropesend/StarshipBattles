# Phase 2: PlanetEconomyProjector service

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-288 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** New service `PlanetEconomyProjector` returns per-planet per-resource projections (harvest / upkeep / yard / net). Move `compute_planet_production` out of the UI file. Full test coverage including multi-resource upkeep + multi-queue yard aggregation.

---

## Tasks

### Task 2.1: Define `ResourceProjection` dataclass + write failing tests [Medium]
**File:** `tests/unit/strategy/services/test_planet_economy_projector.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_planet_economy_projector.py`

- [x] Test: uncolonized planet with harvesters → project has harvest > 0, upkeep = 0 (no pops), yard = 0 (no queues), net = harvest.
- [x] Test: multi-species fed colony → upkeep per resource = `sum(pop * allocation * per_pop_rate)` per resource in `economy.population_consumption`.
- [x] Test: single queued complex → yard drain per resource = `production_rate[res]` for whatever's being built.
- [x] Test: multi-queue colony (planetary yard + 2 shipyards, each building something) → yard drain sums across queues.
- [x] Test: empty queue → yard drain = 0.
- [x] Test: net column = harvest - upkeep - yard for every resource.

**Notes:** Added 8 tests in `tests/unit/strategy/services/test_planet_economy_projector.py` (the 6 listed + 2 extras: `TestHabitabilityScalesHarvestAndYardOnly` to lock in the PROJ-285 stacking rule that upkeep is NOT habitability-scaled, and `TestUnownedPlanetReturnsEmpty` to pin `compute_planet_production`'s short-circuit on `owner_id=None`). Helpers: `_planet`, `_harvester_facility`, `_planetary_yard_facility`, `_shipyard_facility`, `_StubRegistry`, `_economy`. The empty-queue test asserts the projector returns `{}` (rather than entries with `harvest=0, upkeep=0, yard=0`) — keeps UI consumers from rendering all-zero rows for resources that genuinely don't apply to this planet.

### Task 2.2: Implement `PlanetEconomyProjector` [Complex]
**File:** `game/strategy/services/planet_economy_projector.py` (NEW)
**Tests:** `pytest tests/unit/strategy/services/test_planet_economy_projector.py`

- [x] Define `ResourceProjection` frozen dataclass.
- [x] Implement `PlanetEconomyProjector.__init__(*, registries, economy_config, race_registry)`.
- [x] Implement `.project(planet) -> Dict[resource_id, ResourceProjection]`.
- [x] Sub-method `_project_harvest(planet)` — moves the current `compute_planet_production` logic from `planet_report_panel.py:498`. Preserves signature + behavior.
- [x] Sub-method `_project_upkeep(planet)` — iterates `planet.populations` × `economy.population_consumption.items()`.
- [x] Sub-method `_project_yard_drain(planet)` — iterates `planet.construction_queue` (base) + each `facility.construction_queue` where `facility.is_shipyard`. For each active queue's head item, compute per-turn drain as `production_rate[res]`. Sum across queues.
- [x] Apply habitability multiplier to both harvest AND yard drain (PROJ-285 stacking rule).

**Notes:** Implementation calls `_collect_planet_sources` from `game/strategy/data/build_queue_source.py` (the `_`-prefix is "non-public-API" but inside the same strategy layer; reusing it is cheaper than reimplementing the queue + rate-resolution logic). Build-rate boosters are intentionally NOT factored in — `project(planet)` doesn't carry galaxy/empire context, and `get_build_rate_booster_mult(galaxy=None, empire=None)` short-circuits to 1.0. Documented in the projector module docstring. Habitability comes from the existing `planet_habitability_multiplier(planet, race_registry)` helper (PROJ-285) — same call the engines make, so harvest + yard projections track engine output. Module exports `ResourceProjection`, `PlanetEconomyProjector`, `compute_planet_production` via `__all__`.

### Task 2.3: Migrate UI caller [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Delete the old `compute_planet_production` function body; keep a thin compatibility wrapper OR update all call sites to import from `game.strategy.services.planet_economy_projector`.
- [x] Verify no layer violation: UI imports strategy services (OK); strategy doesn't import UI (no change).

**Notes:** Chose the no-shim option per CLAUDE.md "DO NOT add backward-compatibility hacks like... re-exports". Deleted both `compute_planet_production` and `_get_harvester_info` from `planet_report_panel.py` and removed the now-unused `get_component_abilities` import + the `IPlanet`/`IFacility`/`GameRegistries` TYPE_CHECKING imports + the unused `TYPE_CHECKING` import itself. Updated 3 production callers (`build_queue_panel_factory.py`, `planet_list_window.py`, `strategy_detail_formatter.py`) to import `compute_planet_production` from the new service location. Updated 3 test files (`tests/unit/ui/panels/test_compute_planet_production.py`, `tests/unit/ui/panels/test_planet_report_panel.py`, `tests/unit/ui/screens/test_strategy_detail_formatter.py`) — these tests live under `tests/unit/ui/` but exercise what is now strategy-layer code; relocating them is a separate cleanup, out of scope here. Pre-existing failures in `tests/unit/ui/screens/test_food_allocation_editor.py` (13) confirmed via `git stash` to predate PROJ-288 — they're PROJ-286 test debt (still using the old `population_food_resource`/`food_per_pop_per_turn` kwargs replaced by the `population_consumption` dict). Combined targeted suite: 355/355 green.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 3: facade DTO)
