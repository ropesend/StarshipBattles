# PROJ-254: Identity, Indexing & Correctness

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-254` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-254 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Spatial Narrow-Phase Distance Check | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Thread Ship Instance ID Through Battle | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Single Stat Path / Remove expected_stats Fallback | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Strategy Facade Indexed Reads | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Documentation Update | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-06
**Active Phase:** Complete
**Next Action:** Project complete — all 5 phases done
**Blockers:** None
**Context for Next Agent:** All phases complete. Spatial `query_radius_exact()`, ship `instance_id` through battle, expected_stats fallback removed, facade planet index + star cache. Full suite: 14691+ passed.

## Overview

Four correctness and scalability issues in the identity-mapping and query paths:

1. **Broad-Phase Leakage** (Finding 5 — High): `SpatialGrid.query_radius()` returns all entities in overlapping grid cells without an exact-distance check. `_find_enemies_in_radius()` applies team/alive filters but no distance filter. Dense battles over-evaluate targets beyond true range.

2. **Fragile Battle Identity Mapping** (Finding 8 — High): `FleetBattleAdapter.update_from_battle_results()` matches surviving ships by name (`survivors_by_name` dict). Duplicate ship names cause silent data loss — last one wins in the dict. `ShipInstance.instance_id` exists but isn't threaded through the battle layer.

3. **Redundant Stat Work / Fallback Drift** (Finding 9 — Medium): `calculate_design_stats()` re-scans components for resource totals after `recalculate_stats()` already computed them. Falls back to `expected_stats` on error, serving stale data silently.

4. **Scan-Heavy Strategy Facade** (Finding 7 — Medium): `StrategySessionFacade` performs O(n) linear scans across systems, planets, and fleets for common queries. No spatial/ID indices. UI reads degrade as galaxy grows.

## Goals
- Spatial queries return only entities within exact radius — no false positives from grid cell overlap
- Battle survivor matching uses `instance_id`, not `name` — correct even with duplicate ship names
- Ship stat calculation has one canonical path with no stale-data fallback
- Strategy facade queries use indexed lookups for common operations

## Scope

**In Scope:**
- `game/engine/spatial.py` — add narrow-phase distance check
- `game/ai/controller.py` — use exact-distance query
- `game/strategy/data/fleet_battle_adapter.py` — match by instance_id
- `game/simulation/interfaces/` — extend `IPostBattleShip` with instance_id
- `game/simulation/entities/ship.py` — store instance_id metadata
- `game/strategy/ship_design_stats.py` — remove redundant scans and expected_stats fallback
- `game/strategy/facade/strategy_session_facade.py` — add indexed lookups
- `game/strategy/data/galaxy.py` — maintain index dicts

**Out of Scope:**
- Spatial grid cell size tuning (that's a parameter, not architecture)
- ShipInstance.instance_id generation (already exists, just needs threading)
- Full CQRS read-model separation (we add lightweight indices, not a separate store)

## Findings Summary

| Finding | File | Lines | Issue |
|---------|------|-------|-------|
| 5 (Spatial) | spatial.py | 35-47 | `query_radius()` returns all in overlapping cells, no distance check |
| 5 (Spatial) | controller.py | 119-144 | `_find_enemies_in_radius()` filters team/alive but not distance |
| 8 (Identity) | fleet_battle_adapter.py | 101-123 | `survivors_by_name` dict — duplicates cause silent loss |
| 9 (Stats) | ship_design_stats.py | 53-101 | Re-scans components after recalculate; expected_stats fallback |
| 7 (Facade) | strategy_session_facade.py | 281, 347, 436 | O(n) scans for fleets-at-hex, all-stars, planet-by-id |

## Key Files Reference

| Component | File Path |
|-----------|-----------|
| Spatial grid | `game/engine/spatial.py` |
| AI controller | `game/ai/controller.py` |
| Fleet battle adapter | `game/strategy/data/fleet_battle_adapter.py` |
| Post-battle protocol | `game/simulation/interfaces/` |
| Ship entity | `game/simulation/entities/ship.py` |
| Ship design stats | `game/strategy/ship_design_stats.py` |
| Strategy facade | `game/strategy/facade/strategy_session_facade.py` |
| Galaxy data | `game/strategy/data/galaxy.py` |

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Add `query_radius_exact()` as a new method rather than changing existing `query_radius()` | Existing callers may rely on the broad-phase behavior for performance-tolerant uses. New method is opt-in. |
| 2026-04-06 | Thread instance_id through IPostBattleShip protocol, not Ship metadata dict | Protocol property is type-safe and discoverable. Metadata dict would be stringly-typed. |
| 2026-04-06 | Remove expected_stats fallback entirely, not make it opt-in | Per CLAUDE.md "Clean-Sheet Design" rule: if Ship.from_dict() fails, that's a real error. Silencing it with stale data hides bugs. |
| 2026-04-06 | Lightweight index dicts on Galaxy, not a separate index service | The indices are simple dicts maintained at mutation points. A separate service would be overengineering for the current scale. |

## Dependency Chain

```
Phase 1 (Spatial) -- independent, lowest risk
    |
Phase 2 (Ship ID) -- independent of Phase 1
    |
Phase 3 (Stat Path) -- independent of Phases 1-2
    |
Phase 4 (Facade Indices) -- independent but largest; benefits from patterns established in 1-3
    |
    +---> Phase 5 (Documentation) -- after all code phases
```

All code phases are independent and could be worked in any order.

---

## Phases

### Phase 1: Spatial Narrow-Phase Distance Check [Simple]
**Objective:** Add exact-distance filtering to spatial queries so only entities within true radius are returned
**Status:** Not Started
**Estimated Size:** ~30 lines changed, ~40 lines tests
**Depends On:** Nothing
**Risk:** Very low — purely additive
See `phase_1_checklist.md`

### Phase 2: Thread Ship Instance ID Through Battle [Medium]
**Objective:** Match battle survivors by `instance_id` instead of `name`; eliminate silent data loss from duplicate names
**Status:** Not Started
**Estimated Size:** ~60 lines changed across 4-5 files, ~50 lines tests
**Depends On:** Nothing
**Risk:** Low — instance_id already exists on ShipInstance
See `phase_2_checklist.md`

### Phase 3: Single Stat Path / Remove expected_stats Fallback [Simple]
**Objective:** Remove redundant component re-scanning from `calculate_design_stats()` and eliminate the expected_stats fallback
**Status:** Not Started
**Estimated Size:** ~40 lines removed/changed, ~30 lines tests
**Depends On:** Nothing
See `phase_3_checklist.md`

### Phase 4: Strategy Facade Indexed Reads [Medium-High]
**Objective:** Add lightweight index dicts to Galaxy for common facade queries (fleets-by-hex, planets-by-id)
**Status:** Not Started
**Estimated Size:** ~120 lines changed across 3-4 files, ~80 lines tests
**Depends On:** Nothing (but largest phase, benefits from completing 1-3 first)
See `phase_4_checklist.md`

### Phase 5: Documentation Update [Simple]
**Objective:** Update architecture docs to reflect new spatial API, identity mapping, and indexing patterns
**Status:** Not Started
**Estimated Size:** ~30 lines docs
**Depends On:** Phases 1-4
See `phase_5_checklist.md`
