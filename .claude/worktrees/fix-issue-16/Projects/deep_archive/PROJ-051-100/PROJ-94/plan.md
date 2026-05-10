# PROJ-94: Resource API Cleanup and Protocol Wiring

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-94` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-94 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix UI Encapsulation & Extract Bridge Helper | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Delete Dead Type-Specific Methods | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Wire Up IResourceReader Protocol | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Audit & Final Cleanup | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** Audit Complete - Awaiting User Verification
**Last Action:** Audit cycle 1 passed - no significant issues found
**Next Action:** User verification required
**Blockers:** None
**Context for Next Agent:** Project is audit-complete. All 4 phases complete. 7595 tests passing. 175 lines removed total. All 5 goals verified by investigation agents. Ready for user verification and archive.

## Overview
Clean up remaining resource API issues from the duplication audit: delete dead type-specific methods (~157 lines), fix 2 UI encapsulation violations, extract a bridge helper to DRY up resource capture code, and wire up `IResourceReader` typing into `IPostBattleShip`.

## Goals
- Delete all dead type-specific resource methods from ShipResourceManager, FleetResourceAggregator, Fleet
- Fix private `._resources` access in 2 UI files
- DRY up duplicate bridge code in ShipInstance
- Type `IPostBattleShip.resources` properly as `Optional[IResourceReader]`
- Remove unnecessary defensive `getattr` calls

## Scope
**In Scope:**
- Delete 7 type-specific methods from `ShipResourceManager` (lines 40-136)
- Delete 5 type-specific methods from `FleetResourceAggregator` (lines 30-63, 149-165)
- Delete 5 facade methods from `Fleet` (lines 170-182, 204-210)
- Fix `stats_config.py` accessing `ship.resources._resources.keys()` (line 433)
- Fix `ship_stats_renderer.py` accessing `ship.resources._resources.values()` (lines 116-117)
- Add `get_all_resources()` method to `ResourceRegistry`
- Extract `_capture_resource_levels()` helper from duplicate code in `ShipInstance`
- Change `IPostBattleShip.resources` type from `Any` to `Optional[IResourceReader]`
- Add `get_resource_names()` to `IResourceReader` protocol
- Remove defensive `getattr(ship, 'is_derelict', False)` calls
- Delete ~23 corresponding test methods

**Out of Scope:**
- ResourceType constants (PROJ-95)
- is_destroyed -> is_alive rename (PROJ-95)
- None-means-full convention change (PROJ-95)
- Dual resource system architecture

## Key Files Reference
| Component | File Path | What Changes |
|-----------|-----------|--------------|
| ShipResourceManager | `game/strategy/data/ship_resource_manager.py` | Delete lines 40-136 (7 type-specific methods) |
| FleetResourceAggregator | `game/strategy/data/fleet_resource_aggregator.py` | Delete lines 30-63, 149-165 (5 methods) |
| Fleet | `game/strategy/data/fleet.py` | Delete lines 170-182, 204-210 (5 facade methods) |
| stats_config | `game/ui/screens/builder/stats_config.py` | Fix line 433: `._resources.keys()` to `.get_resource_names()` |
| ship_stats_renderer | `game/ui/panels/ship_stats_renderer.py` | Fix lines 116-117: `._resources.values()` to `.get_all_resources()` |
| ResourceRegistry | `game/simulation/systems/resource_manager.py` | Add `get_all_resources()` after line 199 |
| ShipInstance | `game/strategy/data/ship_instance.py` | Extract `_capture_resource_levels()`, remove `getattr` |
| Protocols | `game/core/protocols.py` | Type `resources` as `Optional[IResourceReader]`, add `get_resource_names()` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- **Source Review:** `Reviews/results/2026-02-10_general_resource-state-duplication-audit/`
- **Predecessor:** PROJ-91 (Unify Resource/State Logic) - completed
- **Successor:** PROJ-95 (Resource API Consistency) - should follow this project

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | PROJ-94 before PROJ-95 | Deletes dead code first so PROJ-95 doesn't waste time adding constants to methods about to be deleted |
| 2026-02-10 | Add get_all_resources() to ResourceRegistry | ship_stats_renderer needs ResourceState objects (for .name, .current_value, .max_value), not just names |
| 2026-02-10 | Extract _capture_resource_levels() as static method | Duplicate code in from_ship() and update_from_ship() -- DRY it up |
| 2026-02-10 | Remove getattr for is_derelict | IPostBattleShip declares is_derelict as required property -- getattr is unnecessary defensive code |

---

## Phases

### Phase 1: Fix UI Encapsulation Violations & Extract Bridge Helper [Simple]
**Objective:** Fix live private access violations and DRY up bridge code. Low risk, no API changes.
**Status:** Complete

See [phase_1_checklist.md](phase_1_checklist.md) for detailed tasks.

### Phase 2: Delete Dead Type-Specific Methods [Simple]
**Objective:** Remove all remaining type-specific resource methods that PROJ-91 left behind in extracted managers.
**Status:** Complete

See [phase_2_checklist.md](phase_2_checklist.md) for detailed tasks.

### Phase 3: Wire Up IResourceReader Protocol [Simple]
**Objective:** Type `IPostBattleShip.resources` properly and clean up unused guard functions.
**Status:** Complete

See [phase_3_checklist.md](phase_3_checklist.md) for detailed tasks.

### Phase 4: Audit & Final Cleanup [Simple]
**Objective:** Full test suite, verification greps, line count comparison.
**Status:** Complete

See [phase_4_checklist.md](phase_4_checklist.md) for detailed tasks.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` -- 7616 passed (baseline established)

### After Each Phase
- [ ] Run `pytest tests/ -n 12` -- all tests pass
- [ ] Verify no import errors

### Final Verification
- [x] Grep: No `._resources` in `game/ui/`
- [x] Grep: No `resources.*Any` in `game/core/protocols.py` for IPostBattleShip
- [x] Grep: No `getattr.*is_derelict` in `game/strategy/`
- [x] Grep: No `get_current_fuel|consume_fuel|get_current_energy|consume_energy` in `game/`
- [x] Grep: No `has_fuel_for_movement|consume_fleet_fuel` in `game/`
- [x] Grep: No `get_fuel_cost_per_hex|get_warp_fuel_cost|get_warp_energy_cost` in `game/`
- [x] Run full test suite: `pytest tests/ -n 12` -- 7595 passed

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-02-10 | No significant issues. 4 investigation agents verified all goals. | PASSED |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [x] All Phase 4 tasks checked off
- [x] All tests passing (7595)
- [x] Verification grep checks all pass
- [x] Audit passed (no significant issues)
- [ ] User verified
