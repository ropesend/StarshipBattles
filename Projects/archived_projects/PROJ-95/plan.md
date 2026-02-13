# PROJ-95: Resource API Consistency and Clean-Sheet Conventions

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-95` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-95 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add ResourceType Constants | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Rename is_destroyed to is_alive | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Eliminate None-Means-Full Convention | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Audit & Final Verification | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** Audit Complete
**Last Action:** Phase 4 Audit passed. All verification greps pass. 7595 tests passing.
**Next Action:** Project complete, ready for user verification.
**Blockers:** None
**Context for Next Agent:** PROJ-95 complete. All 4 phases done. ResourceType constants, is_alive rename, None-means-full elimination all verified.

## Overview
Three clean-sheet convention changes to the strategy layer's resource/state API:
1. Replace magic strings `'fuel'`, `'energy'`, `'ammo'` with `ResourceType` constants (66 prod + 585 test occurrences)
2. Rename `is_destroyed` to `is_alive` across strategy layer (invert semantics to match simulation layer)
3. Eliminate "None-means-full" sparse dict convention — always store actual resource values

## Goals
- Eliminate all magic resource type strings from production code
- Unify ship destruction semantics (strategy `is_alive` matches simulation `is_alive`)
- Make resource_levels always contain actual values (no implicit "missing = full")
- Simplify all resource getters (no more `dict.get(key, max_val)` patterns)

## Scope
**In Scope:**
- `ResourceType` constants class in `game/core/constants.py`
- All magic string replacements in `game/` (66 occurrences)
- Magic string replacements in `tests/` (585 occurrences — do in bulk via search/replace)
- `is_destroyed` → `is_alive` rename with logic inversion (14 prod + 32 test files)
- Serialization updates (`to_dict`/`from_dict`) for both changes
- Eliminate None-means-full from `ShipResourceManager`, `ShipInstance`, `FleetResourceAggregator`
- Initialize `resource_levels` with max values during `ShipInstance.create()`
- Remove `del` from `resupply()` (no longer delete keys at max)
- Update `PlanetaryFacility` to match new convention

**Out of Scope:**
- Dual resource system architecture (accepted as-is per Finding #1)
- Simulation layer ResourceRegistry changes (already stores actual values)
- Adding new resource types
- Test magic strings in test data/fixtures (can use literals in test assertions)

## Key Files Reference
| Component | File Path | What Changes |
|-----------|-----------|--------------|
| ResourceType constants | `game/core/constants.py` | NEW: Add ResourceType class |
| ShipInstance | `game/strategy/data/ship_instance.py` | is_destroyed→is_alive, resource init, serialization |
| ShipResourceManager | `game/strategy/data/ship_resource_manager.py` | Remove max-fallback pattern, use constants |
| ShipDisplayFormatter | `game/strategy/data/ship_display_formatter.py` | is_destroyed→is_alive |
| Fleet | `game/strategy/data/fleet.py` | Constant imports |
| FleetResourceAggregator | `game/strategy/data/fleet_resource_aggregator.py` | Constant imports |
| FleetReportFilters | `game/ui/screens/fleet_report_filters.py` | is_destroyed→is_alive, constants, remove None-means-full checks |
| ColumnManager | `game/ui/screens/column_manager.py` | is_destroyed→is_alive |
| ShipStatsRenderer | `game/ui/panels/ship_stats_renderer.py` | Constants |
| StatsConfig | `game/ui/screens/builder/stats_config.py` | Constants |
| ShipSerialization | `game/simulation/entities/ship_serialization.py` | Constants |
| ShipStats | `game/simulation/entities/ship_stats.py` | Constants |
| CombatEndurance | `game/simulation/entities/combat_endurance.py` | Constants |
| ResupplyEngine | `game/strategy/engine/resupply_engine.py` | Constants, remove None-means-full |
| BattleState | `game/simulation/battle_state.py` | Constants |
| Planet | `game/strategy/data/planet.py` | Constants, align convention |
| Protocols | `game/core/protocols.py` | Update IPostBattleShip (is_alive replaces is_destroyed) |
| Resources | `game/core/resources.py` | Constants |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- **Source Review:** `Reviews/results/2026-02-10_general_resource-state-duplication-audit/`
- **Predecessor:** PROJ-94 (Resource API Cleanup) — should complete first
- **Related:** PROJ-91 (Unify Resource/State Logic) — completed

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Accept dual resource systems as-is (Finding #1) | ShipInstance exists in strategy layer without simulation Ship; cannot delegate to ResourceRegistry. Architecturally justified. |
| 2026-02-10 | Full rename is_destroyed → is_alive (not convenience property) | Clean-sheet approach per CLAUDE.md. Eliminates double-negation bugs. Save files are disposable. |
| 2026-02-10 | Eliminate None-means-full convention | Clean-sheet: always store actual values. Aligns with simulation layer. Removes ambiguity and simplifies getters. |
| 2026-02-10 | One project, 4 phases | Three changes are low-coupling cleanups. Constants first (pure addition), then rename (semantic), then convention change (behavioral). |
| 2026-02-10 | Phase 1 is constants (no behavior change) | Safest change, creates foundation for phases 2-3. Can be verified independently. |

---

## Phases

### Phase 1: Add ResourceType Constants [Medium]
**Objective:** Create `ResourceType` constants and replace all magic strings in production code. No behavioral changes.
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md) for detailed tasks.

### Phase 2: Rename is_destroyed to is_alive [Medium]
**Objective:** Replace `is_destroyed` with `is_alive` across strategy layer. Invert all boolean logic. Update serialization.
**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md) for detailed tasks.

### Phase 3: Eliminate None-Means-Full Convention [Medium]
**Objective:** Always store actual resource values in `resource_levels`. Initialize at creation. Remove sparse-dict patterns. Simplify getters.
**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md) for detailed tasks.

### Phase 4: Audit & Final Verification [Simple]
**Objective:** Full test suite, verification greps, document results.
**Status:** Not Started

See [phase_4_checklist.md](phase_4_checklist.md) for detailed tasks.

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Run full test suite: `pytest tests/ -n 12` - all tests pass (establishes baseline)

### After Each Phase
- [ ] Run `pytest tests/ -n 12` - all tests pass
- [ ] Verify no import errors

### Final Verification
- [ ] Grep: No literal `'fuel'`, `'energy'`, `'ammo'` strings in `game/` (except ResourceType definitions)
- [ ] Grep: No `is_destroyed` in `game/` or `tests/`
- [ ] Grep: No `.get(resource_type, max` or `.get('fuel', max` patterns in strategy layer
- [ ] Grep: No `del self._ship.resource_levels` in strategy layer
- [ ] Run full test suite: `pytest tests/ -n 12`

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-02-10 | No issues. All greps pass, 7595 tests pass. | PASSED |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [x] All Phase 4 tasks checked off
- [x] All tests passing (7595)
- [x] Verification grep checks all pass
- [x] Audit passed (no significant issues)
- [ ] User verified
