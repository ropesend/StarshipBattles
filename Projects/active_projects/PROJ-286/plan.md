# PROJ-286: Multi-Resource Population Consumption

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-286` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-286 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. EconomyConfig + economy.json multi-resource schema | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. ColonySpeciesConfig per-resource ratios | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. OrganicsConsumptionEngine rewrite for multi-resource | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. HappinessEngine + PopulationEngine read aggregated ratio | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Docs + cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Planning complete; ready to begin Phase 1
**Last Action:** Project scaffolded. Scope, decisions, and phase breakdown drafted in this session alongside PROJ-287..290 based on user design session for habitability/reproduction/food UI.
**Next Action:** Phase 1 Task 1.1 — evolve `data/economy.json` to the multi-resource schema + update `EconomyConfig` dataclass + loader.
**Blockers:** None. Independent of PROJ-287 and PROJ-288.
**Context for Next Agent:** User-confirmed 2026-04-18 that population consumes THREE resources: organics (primary, 0.001/pop/turn — the PROJ-284 baseline), metals (10% of organics = 0.0001/pop/turn), radioactives (1% of organics = 0.00001/pop/turn). This is the first test of the "population may consume multiple resources" flexibility that PROJ-284 deferred. The engine needs to iterate all declared resources, drain each from the colony stockpile, compute per-resource ratios, and aggregate to a single `last_food_ratio` (defined as the **minimum** ratio across all required resources) that HappinessEngine and PopulationEngine consume unchanged. This keeps PROJ-284's happiness + population formulas byte-for-byte stable while admitting multi-resource upkeep.

## Overview

Evolve the PROJ-284 single-resource consumption model to support multiple population-upkeep resources declared in `data/economy.json`. Three real resources today: `organics` (primary food, 0.001/pop/turn), `metals` (0.0001), `radioactives` (0.00001). The engine must drain each resource independently from each colony's stockpile, track per-resource supply ratios on `ColonySpeciesConfig`, and aggregate to a single `last_food_ratio` (min across resources) that downstream engines (HappinessEngine, PopulationEngine) consume without behavioral change.

## Goals

- Evolve `data/economy.json` schema from `{population_food_resource, food_per_pop_per_turn}` to `{population_consumption: Dict[resource_id, rate]}`.
- `EconomyConfig` exposes `population_consumption: Dict[str, float]` + a `primary_resource` convenience property (first key in the dict, for UI titles).
- `OrganicsConsumptionEngine` iterates every resource in `EconomyConfig.population_consumption`, drains each, computes per-resource `supplied/needed` ratio.
- `ColonySpeciesConfig` tracks `last_consumption_ratios: Dict[str, float]` (transient, not serialized). Legacy `last_food_ratio` becomes a computed property returning `min(last_consumption_ratios.values(), default=1.0)`.
- HappinessEngine + PopulationEngine unchanged — they still read `cfg.last_food_ratio` which now returns the aggregate min.
- Full sharded suite green. PROJ-284 + PROJ-285 regression tests continue to pass.

## Scope

**In:**
- `data/economy.json` schema change.
- `EconomyConfig` dataclass + loader + defaults.
- `OrganicsConsumptionEngine` rewrite to iterate multiple resources.
- `ColonySpeciesConfig` field change: `last_food_ratio: float` → `last_consumption_ratios: Dict[str, float]` with backward-compat computed property.
- Migration of all existing PROJ-284 tests to the new ratio dict (or the computed-property surface, whichever is cleaner per test).
- Update PROJ-284 docs (`docs/systems/strategy_layer.md §8`, `docs/04_SERVICES.md` PROJ-284 entry) to reflect multi-resource.

**Out:**
- UI changes to show per-resource upkeep — PROJ-289.
- Treasury-level aggregation of multi-resource upkeep — PROJ-290.
- Changes to `HappinessEngine` or `PopulationEngine` formulas (they only read the aggregate `last_food_ratio`, which still returns a single float).
- Renaming `OrganicsConsumptionEngine` to something more generic. The name is misleading post-multi-resource but the rename is a big ripple; defer to a cleanup project.
- Per-resource starvation mechanics (e.g. "starving on metals triggers a different decline than starving on organics"). Aggregation as MIN across resources is sufficient for the current gameplay loop.

## Key Files

| Component | File Path |
|-----------|-----------|
| economy.json schema | `data/economy.json` |
| EconomyConfig dataclass + loader | `game/strategy/config/economy_config.py` |
| OrganicsConsumptionEngine | `game/strategy/engine/organics_consumption_engine.py` |
| ColonySpeciesConfig | `game/strategy/data/colony_species_config.py` |
| HappinessEngine (verify tests) | `game/strategy/engine/happiness_engine.py` |
| PopulationEngine (verify tests) | `game/strategy/engine/population_engine.py` |

## Related Documents
- [design.md](design.md) — Architecture rationale (schema migration + aggregation choice)
- [decisions.md](decisions.md) — Decisions log
- [manifest.md](manifest.md) — Full file manifest

## Related Projects

| PROJ | Relationship |
|------|--------------|
| PROJ-284 | Foundational — PROJ-286 evolves its single-resource consumption to multi-resource |
| PROJ-288 | Consumer — Colony Output Projection Helpers will project per-resource upkeep for UI |
| PROJ-289 | Consumer — Planet Report Panel UI displays per-resource upkeep |
| PROJ-290 | Consumer — Empire Treasury sums multi-resource upkeep empire-wide |

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing via `python Tools/test_sharded/test_sharded.py`
- [ ] Manual scenario:
  - [ ] Start a game; advance 5 turns. Verify organics AND metals AND radioactives drain from colony stockpiles at the documented per-pop rates.
  - [ ] Deplete one resource (e.g. empty the metals stockpile). Verify `cfg.last_food_ratio` drops to the metals ratio (the min), happiness degrades, population declines.
  - [ ] Verify PROJ-284 + PROJ-285 tests + integration tests all still green.
- [ ] Docs updated: `docs/systems/strategy_layer.md §8` + `docs/04_SERVICES.md` PROJ-284 entry reflect multi-resource schema.
- [ ] User verified end-to-end.
