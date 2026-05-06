# PROJ-372: Strategy: Galaxy/Planet/Star God-Class Decomposition (facade-delegate pattern)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-372` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-372 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist | Depends on |
|-------|--------|-----------|------------|
| 0. Pre-Phase: facade-delegate template + AST/protocol scaffolding | Complete | [phase_0_checklist.md](phase_0_checklist.md) | **PROJ-370 verified** |
| 1. Star decomposition (770 LOC stars.py → ~280 facade + extracted services) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) | **PROJ-370 verified** + phase_0 |
| 2. Planet decomposition (667 LOC → ~350 facade + habitability/query services) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) | **PROJ-370 verified** + phase_0 |
| 3. Galaxy query/spatial-aggregation services | Not Started | [phase_3_checklist.md](phase_3_checklist.md) | **PROJ-370 verified** + phase_0 |
| 4. Galaxy algorithmic services (pathfinding, intercept, warp resolution) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) | **PROJ-370 verified** + phase_3 |
| 5. AST guards, perf bench, doc updates, final audit | Not Started | [phase_5_checklist.md](phase_5_checklist.md) | **PROJ-370 verified** + phases 1-4 |

## Current State
**Last Updated:** 2026-05-05 (Phase 0 complete)
**Active Phase:** Phase 1 (Star decomposition) — pending
**Last Action:** Phase 0 complete. Created `game/strategy/data/galaxy_protocols.py` (5 read protocols: `IHabitabilityCalculator`, `IGalaxySystemGraph`, `IGalaxySpatialQuery`, `IStockpileHolder`, `IStagingYardHolder`); added `get_default_planet_habitability_service` / `set_default_planet_habitability_service` accessors to `game/context.py` (return None until Phase 2 wires PlanetHabitabilityService). LOC ceilings test pinned at today's baseline (galaxy=689, planet=667, stars=770). State-encapsulation AST guard found 5 grandfathered external reads (`movement.py`, `fleet_navigation_service.py`, `hex_outlines.py`); captured for Phase-3 cleanup. Perf baseline JSON committed at `tests/performance/bench_galaxy_planet_star_baseline.json` (50-system synthetic; pathfinding 41us, spatial 369us, habitability 240us). 15 Phase-0 tests pass.
**Next Action:** Phase 1 — Star decomposition. Move `Spectrum` to `data/spectrum.py`, `StarGenerator` to `generation/star_generator.py`, `_kelvin_to_rgb` + math to `core/spectrum_math.py`. Tighten `stars.py` LOC ceiling to 280.
**Blockers:** None. PROJ-370 verified shipped (5 phases + remediation in commit history).

## Overview

Three classes — `Galaxy` (689 LOC, 31 methods on 4 lifecycle/state classes + `WarpPoint` + `StarSystem`), `Planet` (667 LOC, 47 dataclass fields + 20 methods + 5 properties), `Star` plus `Spectrum` plus `StarGenerator` (770 LOC mixed in `stars.py`) — bundle data model, query/index lookup, calculation, generation, spectral math, and serialization. PROJ-173 Phase 2 already extracted four `Galaxy` delegates; PROJ-210 already extracted `PlanetaryFacility` and `SpeciesPopulation` from `Planet`; PROJ-285 cached habitability per-turn. The remaining surface still has high test setup cost (full 100-system universes for any pathfinding change), no swap point for habitability calculators (PROJ-285's late-import in `Planet.get_cached_habitability_multiplier` blocks injection), and a 770-LOC `stars.py` that's literally a 130-LOC dataclass + 60-LOC dataclass + 500-LOC generator + 80 LOC of math constants + serde, all in one file.

This project pushes the existing facade/delegate pattern to completion: `Galaxy`/`Planet`/`Star` shrink to data-shape + thin-API facade; algorithmic, query, calculation, spectral, and pathfinding logic moves into focused services obeying the 500-LOC ceiling and accepting protocol-typed dependencies. **Lineage:** PROJ-86/87/88/89 (decomposed UI screens, ShipInstance, Fleet, GameSession, Ship, Component) — Galaxy/Planet/Star were **deliberately deferred** by those projects (verified — none of the four `Out:` sections mention Galaxy/Planet/Star, and the four projects shipped without touching them). PROJ-372 closes that gap; PROJ-86/87/88/89 are NOT superseded — they shipped focused decompositions of different classes.

## Goals

- **G1.** `Galaxy` ≤ 350 LOC (from 689). Remove direct algorithmic logic; every algorithmic / spatial / warp / pathfinding / generation method is a 1-line facade delegate. The class becomes a wired-together composition of ~6 services. Shared mutable state (`systems`, `_global_hex_planets`, `_global_hex_zones`, `_zone_to_system`, `_global_hex_warp_points`, `planets_by_id`, `fleets_by_id`, `_planet_to_system`, `name_map`, the two ID counters) moves to a `GalaxyState` dataclass; services receive `GalaxyState` by reference instead of holding `_galaxy: Galaxy` back-pointers.
- **G2.** `Planet` ≤ 350 LOC (from 667). The 47 dataclass fields stay (save-format invariant, see Risk R1). The 9 query/calc methods/properties (`active_abilities`, `is_ability_active`, `total_pressure_atm`, `max_population`, `total_population`, `has_space_shipyard`, `get_cached_habitability_multiplier`, `can_build_type`, `occupied_hexes`) move to `PlanetQueryService` / `PlanetHabitabilityService` or remain as 1-line facade delegates. Stockpile / staging-yard / order-queue methods consolidate behind explicit protocols defined in `galaxy_protocols.py`.
- **G3.** `Star` data class ≤ 280 LOC (from 770 — actually splitting `stars.py` not just `Star`). `StarGenerator` moves to `game/strategy/generation/star_generator.py` (≤ 500 LOC). `Spectrum` to its own ≤ 80 LOC module. `_kelvin_to_rgb` and Stefan-Boltzmann math move to `game/core/spectrum_math.py` (algorithmic, no domain knowledge — fits architecture rule that `core/` holds pure math).
- **G4.** Habitability calculator becomes injectable: `PlanetHabitabilityService` with an `IHabitabilityCalculator` protocol; `Planet.get_cached_habitability_multiplier` accepts the service or falls back to a default-bound instance via `ApplicationContext` (PROJ-258 pattern). Modders can swap without monkey-patching.
- **G5.** Pathfinding is callable without constructing 100-system universes. `find_path_interstellar` / `find_hybrid_path` / `calculate_intercept_point` / `find_nearest_system` / `get_system_at_hex` move into `GalaxyPathfindingService` + `InterceptCalculator` accepting an `IGalaxySystemGraph` read protocol. Unit tests inject 3-system stubs.
- **G6.** Existing PROJ-173-Phase-2 delegates (`GalaxyEntityRegistry`, `GalaxySpatialIndex`, `GalaxyWarpGenerator`, `GalaxySystemGenerator`) are kept and refactored: their `_galaxy: Galaxy` back-reference is replaced with `_state: GalaxyState`, breaking the circular `Galaxy ↔ delegate` aliasing. No file renames in this scope (avoid churn).
- **G7.** AST guard tests prevent regression: (a) `galaxy.py` ≤ 350 LOC, `planet.py` ≤ 350 LOC, `stars.py` ≤ 280 LOC; (b) zero non-facade method bodies above 5 LOC on the three classes; (c) zero direct mutation of `GalaxyState` private indexes (`_global_hex_planets`, `_planet_to_system`, `_zone_to_system`, `_global_hex_warp_points`, `_global_hex_zones`) outside the registry/spatial-index services.
- **G8.** Perf regression bench: pathfinding (3 routes) + spatial query (1000 lookups) + habitability lookup (1000 calls) over a synthetic 150-system / 600-planet save are within ±5% of pre-PROJ-372 baseline. (Baseline captured in Phase 0; reasserted in Phase 5.)
- **G9.** Save format unchanged. Existing saves load bit-identically: all 47 Planet fields, 13 Star fields, the Galaxy `_next_planet_id` / `_next_fleet_id` counters, all `intrinsic_abilities` dicts, and the `_cached_habitability_multiplier` *transient* (never serialized — confirmed at `planet.py:152-161`).

## Scope

**In:**
- `game/strategy/data/galaxy.py` (689 LOC) → facade + new `GalaxyState` dataclass + 6 services
- `game/strategy/data/planet.py` (667 LOC) → facade + `PlanetHabitabilityService` + `PlanetQueryService` + protocol-driven stockpile/staging/order interfaces
- `game/strategy/data/stars.py` (770 LOC) → split into 4 files: `Star` data, `Spectrum` data, `StarGenerator` (relocated), `spectrum_math.py` (relocated to `core/`)
- Existing companion files (refactor in place, no rename): `galaxy_entity_registry.py`, `galaxy_spatial_index.py`, `galaxy_warp_generator.py`, `galaxy_system_generator.py` — switch from `_galaxy: Galaxy` to `_state: GalaxyState`
- `game/strategy/data/pathfinding.py` (503 LOC) → `GalaxyPathfindingService` (≤ 350 LOC) + `InterceptCalculator` (≤ 150 LOC); free-function shims kept as deprecated 1-line wrappers, deleted at Phase 5 close
- New protocol module: `game/strategy/data/galaxy_protocols.py` (`IGalaxySystemGraph`, `IGalaxySpatialQuery`, `IHabitabilityCalculator`, `IStockpileHolder`, `IStagingYardHolder`); `IZoneOccupant` already exists at `game/core/protocols.py`
- New services in `game/strategy/services/`: `planet_habitability_service.py`, `planet_query_service.py`, `galaxy_pathfinding_service.py`, `intercept_calculator.py`
- `Spectrum` data class extracted to `game/strategy/data/spectrum.py`; `StarGenerator` relocated to `game/strategy/generation/star_generator.py`; `_kelvin_to_rgb` + Wien's law + Stefan-Boltzmann helpers to `game/core/spectrum_math.py`
- Wiring through `ApplicationContext` (`game/context.py`) for habitability + pathfinding services (PROJ-258 pattern)
- Tests: per-service unit suites + AST guard tests + perf regression bench

**Out:**
- `Empire`, `Fleet`, `ShipInstance` (already done in PROJ-87)
- Planet generation pipeline rewrite (`planet_gen.py`, `planet_atmosphere.py`, `planet_physics.py`) — already well-decomposed; only minor co-location moves if a service legitimately needs to hold a generator reference
- `Storm`, `WarpPoint`, `StarSystem` data classes — they are tight and focused; preserve as-is in `galaxy.py` (they account for ~150 of the 689 LOC, so leaving them in place keeps `galaxy.py` ≤ 350 LOC budget honest — `StarSystem` may move to its own file IF the budget pressure requires it; decision deferred to Phase 3)
- Save-format migration (PROJ-372 preserves; old saves load unchanged)
- Mutation-protocol contract tests (resource conservation under TRANSFER, capacity invariants, etc.) — that is **PROJ-370's** scope, not PROJ-372's
- Re-implementing or relocating `PlanetGenerator` (out — it's already its own class in `planet_gen.py`)
- AI-side hot paths that read planet `populations` / `stockpile` directly (call sites are read-only; safe; PROJ-370 will retrofit protocols at write sites)
- TurnEngine, OrderProcessor, command-spec table — items #1, #2, #4 in the same review (separate projects)

## Key Files

| Component | File Path | Today LOC | Target LOC |
|-----------|-----------|----------:|-----------:|
| Galaxy facade | `game/strategy/data/galaxy.py` | 689 | ≤ 350 |
| Galaxy state (new) | `game/strategy/data/galaxy_state.py` | — | ≤ 150 |
| Planet facade | `game/strategy/data/planet.py` | 667 | ≤ 350 |
| Star data | `game/strategy/data/stars.py` | 770 | ≤ 280 |
| Star generator (relocated) | `game/strategy/generation/star_generator.py` | — | ≤ 500 |
| Spectrum (extracted) | `game/strategy/data/spectrum.py` | — | ≤ 80 |
| Spectrum math (relocated) | `game/core/spectrum_math.py` | — | ≤ 200 |
| Galaxy entity registry | `game/strategy/data/galaxy_entity_registry.py` | 188 | ≤ 250 |
| Galaxy spatial index | `game/strategy/data/galaxy_spatial_index.py` | 192 | ≤ 250 |
| Galaxy warp generator | `game/strategy/data/galaxy_warp_generator.py` | 421 | ≤ 421 (no growth) |
| Galaxy system generator | `game/strategy/data/galaxy_system_generator.py` | 354 | ≤ 354 (no growth) |
| Galaxy pathfinding service (new) | `game/strategy/services/galaxy_pathfinding_service.py` | — | ≤ 350 |
| Intercept calculator (new) | `game/strategy/services/intercept_calculator.py` | — | ≤ 150 |
| Pathfinding shim (deprecated) | `game/strategy/data/pathfinding.py` | 503 | ≤ 60 (1-line wrappers) |
| Planet habitability service (new) | `game/strategy/services/planet_habitability_service.py` | — | ≤ 200 |
| Planet query service (new) | `game/strategy/services/planet_query_service.py` | — | ≤ 250 |
| Galaxy protocols (new) | `game/strategy/data/galaxy_protocols.py` | — | ≤ 150 |

## Related Documents
- [design.md](design.md) — diagnosis, per-class method tables, current vs. target architecture, alternatives, risks
- [decisions.md](decisions.md) — design choices and rejected alternatives
- [findings/initial_review.md](findings/initial_review.md) — per-class method-category table + PROJ-370 sequencing recommendation + top 5 surprises
- Source review: `AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md` (item #5)
- Predecessor projects (all complete, archived, NO overlap): `Projects/deep_archive/PROJ-051-100/PROJ-86/` (UI screens), `PROJ-87/` (ShipInstance/Fleet/GameSession), `PROJ-88/` (Ship/Component/app.py), `PROJ-89/` (DesignSelector/EmpireBuildQueue)
- Predecessor delegate split: PROJ-173 Phase 2 (created `galaxy_entity_registry.py`, `galaxy_spatial_index.py`, `galaxy_warp_generator.py`, `galaxy_system_generator.py`)
- Predecessor data-class split: PROJ-210 (extracted `PlanetaryFacility`, `SpeciesPopulation` from `Planet`)
- Predecessor habitability cache: PROJ-285 (`_cached_habitability_multiplier` per-turn caching at `planet.py:152-161,240-264`)
- Style/rigor reference: `Projects/active_projects/PROJ-367/plan.md`, `design.md`, `decisions.md`, `manifest.md`, `phase_1_checklist.md`

## Today's vs. target architecture (one-line diff)

**Today** (`Galaxy`, `Planet`, `stars.py` mix):
```
class Galaxy:                            # 689 LOC, mostly delegation but 9 methods still hold logic
  systems / _global_hex_planets / _global_hex_zones / _zone_to_system /
  _global_hex_warp_points / _planet_to_system / planets_by_id / fleets_by_id /
  name_map / _next_planet_id / _next_fleet_id  ← all live as plain attrs
  add_system / _register_zones_from_system / _rebuild_warp_point_index /
  remove_warp_link / get_next_fleet_id / create_vars_link  ← logic still here
  + 15 1-line delegations to _registry/_spatial/_warp_gen/_sys_gen
  + 4 lifecycle/serialization (__init__/to_dict/from_dict)

class Planet (@dataclass):               # 667 LOC; 47 fields
  9 query/calc properties+methods + 13 mutation methods + serde
  get_cached_habitability_multiplier ← late-imports planet_habitability_multiplier (no swap point)

stars.py (770 LOC):                      # data + generator + math + serde mixed
  Spectrum class (60 LOC) + Star class (130 LOC) + StarGenerator (500 LOC) + spectrum/Kelvin math (80 LOC)
```

**Target** (after PROJ-372):
```
class Galaxy:                            # ≤ 350 LOC; pure facade
  state: GalaxyState                     # GalaxyState owns ALL mutable indexes
  _registry: GalaxyEntityRegistry(state) # constructed from state, not from galaxy
  _spatial: GalaxySpatialIndex(state)
  _warp_gen / _sys_gen / _pathfinder: similarly state-bound
  + 1-line delegations only (no algorithmic methods on Galaxy itself)

class Planet (@dataclass):               # ≤ 350 LOC; 47 fields preserved
  data fields + thin facade methods that delegate to PlanetQueryService /
  PlanetHabitabilityService. ApplicationContext supplies habitability_service;
  modders swap via context.

stars.py:                                # ≤ 280 LOC, data only
  Star data class
spectrum.py:                             # ≤ 80 LOC, data only
  Spectrum data class
generation/star_generator.py:            # ≤ 500 LOC, generation only
  StarGenerator
core/spectrum_math.py:                   # ≤ 200 LOC, pure functions
  _kelvin_to_rgb, Stefan-Boltzmann helpers, Wien's law, _WAVELENGTHS
```

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/README.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, `docs/systems/strategy_layer.md`
- [ ] Read `Projects/protocols/01_initialize_project.md` and `Projects/protocols/03c_phase_aware_execution.md`
- [ ] Read every line of `galaxy.py` (689), `planet.py` (667), `stars.py` (770)
- [ ] Read all four PROJ-173 Phase 2 delegates plus `pathfinding.py`, `planet_atmosphere.py`, `planet_physics.py`, `planet_naming.py`, `planetary_facility.py`, `planet_gen.py`
- [ ] Read PROJ-86/87/88/89 plan.md (in `Projects/deep_archive/PROJ-051-100/`) — confirm no overlap with Galaxy/Planet/Star
- [ ] Read PROJ-370/plan.md and design.md — confirm sequencing relative to PROJ-372 (resolved 2026-05-06: PROJ-370 first, all of PROJ-372 follows)
- [ ] Read PROJ-367 plan.md / design.md / manifest.md / phase_1_checklist.md / decisions.md as the rigor / style reference
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` — pin baseline pass count in plan.md Current State

### After Each Phase
- [ ] Run `pytest tests/unit/strategy/ -v` and `pytest tests/integration/strategy/ -v` — phase-affected tests pass
- [ ] Run `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count grows monotonically
- [ ] AST guard tests pass (introduced in Phase 0; expanded each phase)
- [ ] Update `Current State` in plan.md with handoff context for the next agent

### Final Verification (Phase 5)
- [ ] Sharded suite green; pass count ≥ baseline + new tests
- [ ] `galaxy.py` ≤ 350 LOC (verified via AST guard)
- [ ] `planet.py` ≤ 350 LOC (verified via AST guard)
- [ ] `stars.py` ≤ 280 LOC (verified via AST guard)
- [ ] Every new service ≤ 500 LOC (verified via AST guard)
- [ ] Save load: load 5 fixture saves and assert `to_dict() == loaded.to_dict()` round-trip equality
- [ ] Perf regression bench: pathfinding + spatial query + habitability lookup over a synthetic 150-system / 600-planet save within ±5% of pre-PROJ-372 baseline
- [ ] Zero direct reads of `galaxy._global_hex_*` / `galaxy._planet_to_system` / `galaxy._zone_to_system` outside the registry/spatial-index services (AST regression test)
- [ ] Habitability service is swappable via `ApplicationContext` (acceptance test: registering a stub `IHabitabilityCalculator` returns its value through `Planet.get_cached_habitability_multiplier`)
- [ ] Pathfinding callable on a 3-system stub graph (acceptance test in `tests/unit/strategy/services/test_galaxy_pathfinding_service.py`)
- [ ] `docs/systems/strategy_layer.md` updated to reflect the new service surface
- [ ] Free-function shims in `pathfinding.py` deleted (Phase 5 close); only the service-layer surface remains

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All phase 0-5 checklists complete
- [ ] All tests passing (sharded suite green)
- [ ] Save round-trip green on 5+ saves
- [ ] Perf bench within ±5%
- [ ] AST guards green (LOC ceilings, no internal mutation outside services)
- [ ] Audit passed (no significant issues)
- [ ] User verified
