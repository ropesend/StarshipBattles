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
| 1. `projected_growth_rate` helper | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. `PlanetEconomyProjector` service | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. `ColonyDemographicView` facade DTO | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Docs + cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Planning complete; ready to begin Phase 1 (BLOCKED on PROJ-286 + PROJ-287)
**Last Action:** Project scaffolded. Depends on PROJ-286 (multi-resource consumption) and PROJ-287 (race registry facade) — do not start until both land.
**Next Action:** After PROJ-286 + PROJ-287 complete, Phase 1 Task 1.1 — extract `projected_growth_rate` pure function to `game/strategy/formulas/colony_output.py`.
**Blockers:**
- **PROJ-286** — multi-resource `population_consumption` dict is read by `PlanetEconomyProjector`.
- **PROJ-287** — `facade.get_race_registry()` and `Empire.resident_species()` are consumed by projectors and by the `ColonyDemographicView` DTO.
**Context for Next Agent:** This project extracts the per-planet per-species projection math into reusable pure helpers so the UI layer (PROJ-289, 290) reads from ONE source of truth rather than duplicating formulas. Three new primitives:
1. **`projected_growth_rate(planet, pop, race_config, cfg) -> float`** — replicates PROJ-284's `PopulationEngine._grow_species` math without mutating state. Returns the % growth rate that would apply next turn. Used by per-species UI lines.
2. **`PlanetEconomyProjector`** — per-planet per-resource projector returning `{resource_id: ResourceProjection(harvest, upkeep, yard, net)}`. Reuses existing `compute_planet_production` for harvest; adds yard-consumption aggregation across the planet's queues; reads multi-resource upkeep from `EconomyConfig.population_consumption`.
3. **`ColonyDemographicView`** — frozen DTO on the facade aggregating everything a "colony demographics" UI needs in one read: per-species habitability/happiness/growth, per-resource harvest/upkeep/yard/net, aggregate empire upkeep contribution.

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
