# PROJ-288: Colony Output Projection Helpers

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-288` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-288 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. `projected_growth_rate` helper | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. `PlanetEconomyProjector` service | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. `ColonyDemographicView` facade DTO | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Docs + cleanup | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** ALL 4 PHASES COMPLETE — awaiting user sign-off
**Last Action:** Phase 4 done. Updated `docs/04_SERVICES.md` with a comprehensive "Planet Economy Projector (PROJ-288)" subsection covering `PlanetEconomyProjector`, `ResourceProjection`, `projected_growth_rate`, `ColonyDemographicView` + `SpeciesDemographicView`, the `get_colony_demographic_view` facade accessor, and the `compute_planet_production` migration note. Updated `docs/systems/strategy_layer.md`: added a "Colony Demographics (PROJ-288)" row to the §1 Query Categories table and a "### Projection helpers (PROJ-288)" subsection at the end of §9 documenting the equivalence contract. Ran the full sharded suite: 15041 tests / 15027 passed / 14 failed in 137.2s — failures are 13 pre-existing PROJ-286 test debt in `test_food_allocation_editor.py` + 1 long-standing theme-bleed flake in `test_quickstart_builder.py`, neither a PROJ-288 regression. Net new from PROJ-288: 38 tests across 4 test files. `Projects/projects_index.md` PROJ-288 row advanced to "Awaiting Verification".
**Last Action (Phase 3 history):** Phase 3 done. Created `game/strategy/facade/dto/colony_demographic_view.py` with two frozen `@dataclass` DTOs: `SpeciesDemographicView` (race_id, race_name, count, habitability, happiness, growth_rate, food_ratio, food_allocation) and `ColonyDemographicView` (planet_id, planet_name, species tuple, resource_projections tuple, total_upkeep dict). Re-exported both from `game/strategy/facade/dto/__init__.py`. Added `StrategySessionFacade.get_colony_demographic_view(planet_id) -> Optional[ColonyDemographicView]` and helper `_resolve_economy_config()` (pulls `economy_config` off the session if present, else falls back to `get_default_economy_config()` so test sessions don't have to wire it). Method uses the existing `_get_planet_by_id` resolver, builds a `PlanetEconomyProjector` from registries + economy + race_registry, computes per-species rows (skipping species the registry can't resolve), sorts species by count descending, builds the resource projections tuple from `projector.project()`, and sums `total_upkeep` per resource across species. 10 new tests in `tests/unit/strategy/facade/test_colony_demographic_view.py` cover unowned/missing planets returning None, view fields populated correctly, species ordering, save-drift species skipped, resource projections include consumption resources, total_upkeep sums correctly, and both DTOs frozen. 224/224 facade tests green (including all 10 new ones).
**Last Action (Phase 2 history):** Phase 2 done. Implemented `PlanetEconomyProjector` + `ResourceProjection` (frozen dataclass) in new file `game/strategy/services/planet_economy_projector.py`. Three sub-projections: `_project_harvest` (delegates to `compute_planet_production` × habitability), `_project_upkeep` (mirrors `OrganicsConsumptionEngine._process_colony` exactly — pop.count × food_allocation × per_pop_rate), `_project_yard_drain` (calls `_collect_planet_sources` from `build_queue_source.py` to enumerate base + shipyard queues, sums `build_rate × habitability` for non-empty queues). Build-rate boosters intentionally skipped (no galaxy/empire context in v1 contract — documented in module docstring). Habitability via existing PROJ-285 `planet_habitability_multiplier`. MOVED `compute_planet_production` + `_get_harvester_info` from `game/ui/panels/planet_report_panel.py` (layer violation — UI hosting strategy math) into the new projector module; updated 3 production callers (`build_queue_panel_factory.py`, `planet_list_window.py`, `strategy_detail_formatter.py`) AND 3 test files (`test_compute_planet_production.py`, `test_planet_report_panel.py`, `test_strategy_detail_formatter.py`) to import from the new location. No backward-compat shims (per CLAUDE.md). Removed unused `get_component_abilities`, `IPlanet`, `IFacility`, `GameRegistries`, `TYPE_CHECKING` imports from `planet_report_panel.py` after the deletion. 8 new tests in `tests/unit/strategy/services/test_planet_economy_projector.py` cover uncolonized harvest-only, multi-resource upkeep summation, single-queue + multi-queue yard, empty-queue zero contribution, net invariant, habitability scaling rule (harvest + yard scale, upkeep does NOT), unowned-planet returns empty. Combined targeted suite (projector + colony_output + equivalence + UI panels + strategy_detail_formatter, excluding the pre-existing broken `test_food_allocation_editor.py` which is PROJ-286 test debt unrelated to PROJ-288): **355/355 green**.
**Next Action:** None — hand back to user for sign-off and to close PROJ-288 out in `projects_index.md`. Consumers PROJ-289 (Planet Report Panel) and PROJ-290 (Treasury + Uncolonized Habitability) are unblocked.
**Blockers:** None. All Phase 1-3 deliverables in place.
**Context for Next Agent:** This project extracts the per-planet per-species projection math into reusable pure helpers so the UI layer (PROJ-289, 290) reads from ONE source of truth rather than duplicating formulas. Three new primitives:
1. **`projected_growth_rate(planet, pop, race_config, cfg) -> float`** ✅ DONE — replicates PROJ-284's `PopulationEngine._grow_species` math without mutating state. Returns the per-capita rate. Equivalence with the engine pinned by integration test.
2. **`PlanetEconomyProjector`** ✅ DONE — per-planet per-resource projector returning `{resource_id: ResourceProjection(harvest, upkeep, yard, net)}`. `compute_planet_production` now lives in the same module. Habitability + yard rate-resolution match the engine.
3. **`ColonyDemographicView`** ✅ DONE — frozen DTO on the facade aggregating everything a "colony demographics" UI needs in one read. Accessed via `facade.get_colony_demographic_view(planet_id)`. Returns None for unowned/missing planets. Species ordered largest count first; species with unresolvable race_ids silently dropped (save-drift defence).

**Phase 1-2 implementation notes for Phase 3's author:**
- `projected_growth_rate` returns the PER-CAPITA rate. Multiply by `pop.count` for absolute Δpop.
- `cfg.last_food_ratio` is the MIN across `cfg.last_consumption_ratios.values()` (PROJ-286 behavior). Pre-fill the dict in tests rather than running a full consumption pass.
- `PopulationEngine._grow_species` clamps with `max(0, current + int(growth))`. Tests/projections that compare absolute deltas must apply the same floor.
- Habitability is computed via `score_planet_for_race(planet, race_config)` from `game/strategy/formulas/habitability.py` — same call the engine uses, so caching at the projector layer would need to mirror PROJ-285's per-turn cache pattern. Out of scope for v1 (decisions.md).
- `PlanetEconomyProjector(*, registries, economy_config, race_registry)` is the constructor. The Phase 3 facade method should resolve `economy_config = get_default_economy_config()` (or pull from session if available) and `race_registry = self.get_race_registry()` (PROJ-287). `registries` is on the session.
- Empty-queue planets get `result == {}` from `project()`. UI consumers iterating the dict need to tolerate that.
- `ResourceProjection` is a frozen `@dataclass`. The DTO's `resource_projections` field can store a `Tuple[ResourceProjection, ...]` directly — no further wrapping needed.
- Pre-existing broken tests `tests/unit/ui/screens/test_food_allocation_editor.py` (13) are PROJ-286 test debt and unrelated to anything in PROJ-288. Don't get distracted by them when running the full suite.

## Overview

Extract the per-planet per-species + per-resource projection math from PROJ-284/285's engines into reusable pure helpers. UI layers (PROJ-289, 290) consume these instead of rolling their own formulas. Three primitives: a growth-rate function, a planet-scoped resource projector, and a facade DTO that materializes a full "colony demographics view" for the UI in one call.

## Goals

- `projected_growth_rate(planet, pop, race_config, cfg) -> float` in `game/strategy/formulas/colony_output.py`. Matches `PopulationEngine._grow_species` math (logistic + decline) but returns the rate, doesn't mutate state.
- `PlanetEconomyProjector` service — per-planet per-resource projection: harvest (reusing `compute_planet_production`), population upkeep (multi-resource from PROJ-286), yard consumption (aggregated across planet queues), net.
- `ColonyDemographicView` frozen DTO — one read returns everything a planet-demographics UI needs, pre-resolved via facade.
- `StrategySessionFacade.get_colony_demographic_view(planet_id) -> Optional[ColonyDemographicView]` read method.
- Unit + integration tests pinning the helper outputs match PROJ-284/285 engine behavior for equivalent inputs.

## Scope

**In:**
- `game/strategy/formulas/colony_output.py` additions (2nd + 3rd functions).
- `game/strategy/services/planet_economy_projector.py` (NEW).
- `game/strategy/facade/dto/colony_demographic_view.py` (NEW) — frozen dataclass.
- `StrategySessionFacade.get_colony_demographic_view(planet_id)` method.
- Unit tests for each helper.
- Integration test: projected rate matches `PopulationEngine._grow_species` output on identical inputs.

**Out:**
- UI consumption of these primitives — PROJ-289, 290.
- Changes to the engines themselves — they can keep their formulas; the helpers duplicate the math deliberately to preserve pure-function semantics (no state mutation).
- Engine migration to use the helpers internally — tempting for DRY, but requires careful test update; out of scope.

## Key Files

| Component | File Path |
|-----------|-----------|
| `projected_growth_rate` | `game/strategy/formulas/colony_output.py` |
| `PlanetEconomyProjector` | `game/strategy/services/planet_economy_projector.py` (NEW) |
| `ColonyDemographicView` DTO | `game/strategy/facade/dto/colony_demographic_view.py` (NEW) |
| Facade method | `game/strategy/facade/strategy_session_facade.py` |

## Related Documents
- [design.md](design.md) — Architecture rationale (formula duplication vs migration)
- [decisions.md](decisions.md) — Decisions log
- [manifest.md](manifest.md) — Full file manifest

## Related Projects

| PROJ | Relationship |
|------|--------------|
| PROJ-286 | Dependency — `EconomyConfig.population_consumption` dict is the source of truth for population upkeep |
| PROJ-287 | Dependency — `facade.get_race_registry()` resolves race_ids to race_configs for growth-rate computation; `Empire.resident_species()` used by consumers |
| PROJ-284 | Formula source — `_grow_species` math is the canonical expression; this project extracts it |
| PROJ-285 | Formula source — habitability is the per-species factor the growth-rate helper needs |
| PROJ-289 | Consumer — planet report UI |
| PROJ-290 | Consumer — treasury + uncolonized habitability |

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing via `python Tools/test_sharded/test_sharded.py`
- [ ] Equivalence: `projected_growth_rate` output matches `PopulationEngine._grow_species(pop, colony, empire)` delta for the same inputs, verified in an integration test.
- [ ] Docs updated: `docs/04_SERVICES.md` has entries for the two new services.
- [ ] User verified end-to-end.
