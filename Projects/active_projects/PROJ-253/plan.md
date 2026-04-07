# PROJ-253: Hot-Loop & Cache Optimization

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-253` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-253 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Dirty-Flagged Ship Stat Invalidation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Planet Energy Caching | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fleet Aura Aggregation Reuse & Caching | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Performance Verification | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Documentation Update | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-06
**Active Phase:** Phase 2 — Planet Energy Caching
**Next Action:** Begin Phase 2 — Planet Energy Caching
**Blockers:** None
**Context for Next Agent:** Phase 1 complete. Ship now has `_stats_dirty` flag and `mark_stats_dirty()` / `recalculate_stats_if_dirty()` methods. Combat manager uses `recalculate_stats_if_dirty()` in tick loop, tracking operational status changes. `component_health_manager.take_damage()` calls `mark_stats_dirty()`. External callers still use `recalculate_stats()` (always runs). 6 new tests. Full suite: 14670 passed (4 flaky pre-existing). Simulation: 162/162 passed.

## Overview

Three hot-loop paths in the codebase perform redundant work on every tick/update, scaling with entity count rather than state changes:

1. **Ship Stat Recompute** (Finding 1 — Critical): Every combat tick, `ShipCombatManager.update()` calls `recalculate_stats()` unconditionally. The 5-phase `ShipStatsCalculator.calculate()` pipeline iterates all components 4+ times. No dirty-flagging exists — even when no component state changed, the full pipeline runs. In a 4X battle with many ships/components, this is the dominant performance cost.

2. **Planet Energy Scans** (Finding 2 — High): `PlanetEnergyEngine._process_planet()` rescans all facilities, components, and activation states on each energy tick (3 separate iteration passes). CC ~18. For colony-heavy late-game turns with dozens of planets, this adds up.

3. **Fleet Aura Duplication** (Finding 3 — High): `FleetAuraManager._recalculate()` (CC ~20-25) reimplements the MAX-then-SUM stacking pattern already available in `ability_aggregator.py`. It also rescans provider ships on every update with no caching.

## Goals
- Ship stat recalculation is dirty-flagged: only runs when component state actually changes
- Planet energy processing uses cached metadata, recalculated only on build/damage/toggle events
- Fleet aura aggregation delegates to the shared aggregator and caches results
- Measurable reduction in per-tick work for battles and strategy turns
- All existing tests continue to pass; new tests verify caching correctness

## Scope

**In Scope:**
- `game/simulation/managers/ship_combat_manager.py` — conditional recalculate
- `game/simulation/entities/ship.py` — dirty flag on Ship
- `game/simulation/entities/ship_stats.py` — skip when clean
- `game/simulation/components/component.py` — set dirty flag on state change
- `game/strategy/engine/planet_energy_engine.py` — cached energy metadata
- `game/strategy/services/fleet_aura_manager.py` — delegate to shared aggregator, add caching
- `game/simulation/entities/ability_aggregator.py` — ensure API supports aura use case

**Out of Scope:**
- Spatial grid optimization (that's PROJ-254, Finding 5)
- Strategy facade query indexing (that's PROJ-254, Finding 7)
- Full profiling infrastructure — we verify with targeted measurements, not a profiling framework

## Findings Summary

| Finding | File | Lines | Issue |
|---------|------|-------|-------|
| 1 (Stats) | ship_combat_manager.py | 97-109 | Unconditional `recalculate_stats()` every tick |
| 1 (Stats) | ship.py | 516-538 | `recalculate_stats()` invalidates cache + runs full pipeline |
| 1 (Stats) | ship_stats.py | 103-184 | 5-phase pipeline iterates all components 4+ times |
| 2 (Energy) | planet_energy_engine.py | 153-208 | 3 separate facility/component scans per energy tick |
| 3 (Aura) | fleet_aura_manager.py | 137-214 | Reimplements MAX-then-SUM, rescans providers each update |
| 3 (Aura) | ability_aggregator.py | 19-61 | Shared aggregator that aura manager should reuse |

## Key Files Reference

| Component | File Path |
|-----------|-----------|
| Ship combat manager | `game/simulation/managers/ship_combat_manager.py` |
| Ship entity | `game/simulation/entities/ship.py` |
| Ship stats calculator | `game/simulation/entities/ship_stats.py` |
| Component (state changes) | `game/simulation/components/component.py` |
| Planet energy engine | `game/strategy/engine/planet_energy_engine.py` |
| Fleet aura manager | `game/strategy/services/fleet_aura_manager.py` |
| Ability aggregator | `game/simulation/entities/ability_aggregator.py` |
| Architecture docs | `docs/01_ARCHITECTURE.md` |
| Patterns docs | `docs/02_PATTERNS.md` |

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Dirty flag on Ship, not on individual components | Ship is the unit of stat recalculation. Component-level dirty flags would add complexity without proportional benefit — the pipeline is all-or-nothing per ship. |
| 2026-04-06 | Debug-mode assertion to catch stale-cache bugs | Run full recalc every N ticks in debug builds and assert against cached values. Catches dirty-flag omissions without production cost. |
| 2026-04-06 | Planet energy cache invalidated by events, not polled | Build/destroy/toggle are discrete events with clear call sites. Polling would just be the current approach with extra steps. |

## Dependency Chain

```
Phase 1 (Ship Stat Dirty Flag) -- largest, most impactful
    |
Phase 2 (Planet Energy Cache) -- independent of Phase 1
    |
Phase 3 (Fleet Aura Reuse) -- independent of Phases 1-2
    |
    +---> Phase 4 (Performance Verification) -- after all code phases
              |
              +---> Phase 5 (Documentation)
```

Phases 1, 2, 3 are independent and could be worked in parallel.

---

## Phases

### Phase 1: Dirty-Flagged Ship Stat Invalidation [Medium-High]
**Objective:** Add `_stats_dirty` flag to Ship; only run `ShipStatsCalculator.calculate()` when state has actually changed
**Status:** Not Started
**Estimated Size:** ~100 lines changed across 4-5 files, ~80 lines tests
**Depends On:** Nothing
**Risk:** Medium-High — dirty-flag bugs cause stale stats. Mitigated by debug-mode assertions.
See `phase_1_checklist.md`

### Phase 2: Planet Energy Caching [Simple-Medium]
**Objective:** Cache facility energy metadata per planet; recalculate only on build/damage/toggle events
**Status:** Not Started
**Estimated Size:** ~60 lines changed, ~50 lines tests
**Depends On:** Nothing
See `phase_2_checklist.md`

### Phase 3: Fleet Aura Aggregation Reuse & Caching [Medium]
**Objective:** Replace inline MAX-then-SUM in FleetAuraManager with shared aggregator; add provider-state caching
**Status:** Not Started
**Estimated Size:** ~80 lines changed, ~60 lines tests
**Depends On:** Nothing
See `phase_3_checklist.md`

### Phase 4: Performance Verification [Simple]
**Objective:** Measure per-tick work reduction with targeted benchmarks
**Status:** Not Started
**Estimated Size:** ~60 lines test/benchmark code
**Depends On:** Phases 1-3
See `phase_4_checklist.md`

### Phase 5: Documentation Update [Simple]
**Objective:** Update architecture docs to reflect caching patterns and dirty-flag conventions
**Status:** Not Started
**Estimated Size:** ~30 lines docs
**Depends On:** Phase 4
See `phase_5_checklist.md`
