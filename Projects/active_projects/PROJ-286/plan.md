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
| 1. EconomyConfig + economy.json multi-resource schema | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. ColonySpeciesConfig per-resource ratios | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. OrganicsConsumptionEngine rewrite for multi-resource | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. HappinessEngine + PopulationEngine read aggregated ratio | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Docs + cleanup | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** ALL 5 PHASES COMPLETE — ready to close. Awaiting user sign-off.
**Last Action:** Phase 5 landed. Docs updated: `docs/systems/strategy_layer.md §8` (heading → `Colony Demographics Loop (PROJ-284 + PROJ-286)`, multi-resource schema example, Liebig's-Law MIN aggregation call-out, new `### Swapping the population-consumption dict` recipe showing ammonia added) + `docs/04_SERVICES.md § Colony Demographics Loop` (all five locations updated: EconomyConfig dict shape, ColonySpeciesConfig computed property, engine multi-resource iteration, UI `primary_resource` call-out, PROJ-289 forward pointer). CLAUDE.md review: zero matches — no-op. Full sharded suite: **14990 tests | 14976 passed | 14 failed | 0 errors**. ALL 14 failures are either expected cross-phase red (13 in `test_food_allocation_editor.py` waiting on PROJ-289) or the pre-existing theme_id-pollution flake from the original handoff watchout. ZERO PROJ-286 regressions.
**Next Action:** User verification of end-to-end gameplay: start a game, advance 5 turns, verify organics + metals + radioactives all drain at the documented per-pop rates. Deplete one resource and verify happiness degrades + population declines via the MIN-aggregated `last_food_ratio`.
**Blockers:** None. Unblocks PROJ-288 (projection helpers) and PROJ-289 (UI migration + treasury) and PROJ-290 (treasury aggregation). PROJ-287 was parallel-safe and is independent.
**Deliverables Summary:**
- `data/economy.json` — multi-resource `population_consumption` dict (organics 0.001, metals 0.0001, radioactives 0.00001).
- `EconomyConfig(population_consumption: Dict[str, float])` + `primary_resource` property + `population_food_resource` shim.
- `ColonySpeciesConfig.last_consumption_ratios: Dict[str, float]` (transient, default_factory=dict) + `last_food_ratio` computed property (MIN with 1.0 empty-dict fallback).
- `OrganicsConsumptionEngine` now iterates `economy.population_consumption.items()`, clears + rewrites `last_consumption_ratios` every turn per species.
- HappinessEngine + PopulationEngine SOURCE UNCHANGED — computed property preserves their reads.
- 17 new tests across EconomyConfig/ColonySpeciesConfig/Engine/HappinessEngine/PopulationEngine covering MIN aggregation, shim, primary_resource, multi-resource drain, stale-key clearing, zero-pop per-resource-1.0, parity between single and multi-resource shapes.
- Misnomer `OrganicsConsumptionEngine` retained (rename deferred per decisions.md for git-history clarity).

**Known cross-phase red (waiting on PROJ-289 / not PROJ-286's job):**
- `game/ui/screens/food_allocation_editor.py` still reads `self._economy.food_per_pop_per_turn` on line 258 → runtime AttributeError if the FoodAllocationEditor is opened. PROJ-289's UI migration will replace with per-resource preview.
- `tests/unit/ui/screens/test_food_allocation_editor.py` × 13 failures — all use old-shape EconomyConfig kwargs. PROJ-289 migration.

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
