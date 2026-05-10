# PROJ-91: Unify Resource/State Logic Between Strategy and Simulation Layers

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-91` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-91 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix Bugs & Add Infrastructure | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate Callers to Generic API | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Remove Type-Specific Methods & Clean Up | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** All Phases Complete — Ready for Audit
**Last Action:** Phase 3 complete - all 7 type-specific methods deleted from ShipInstance
**Next Action:** Trigger audit
**Blockers:** None
**Context for Next Agent:** All 3 phases complete. Deleted 7 type-specific methods from ShipInstance (-68 lines), deleted TestResourceConvenienceMethods test class (-4 tests), cleaned up mock helpers. Tests: 7557 passed.

## Overview
ShipInstance (strategy layer) duplicates resource management logic that already exists in generic form. Seven type-specific methods (`get_current_fuel`, `consume_fuel`, `get_current_energy`, `consume_energy`, `get_fuel_cost_per_hex`, `get_warp_fuel_cost`, `get_warp_energy_cost`) independently reimplement the same logic as the generic `get_current_resource()`, `consume_resource()`, etc. Additionally, two methods (`resupply()` and `get_resource_percentage()`) have bugs from incorrect key lookups. Bridge methods between layers use defensive `hasattr` checks and hardcoded resource name lists.

## Goals
- Eliminate 7 redundant type-specific resource methods from ShipInstance
- Fix bugs in `resupply()` and `get_resource_percentage()`
- Add `IResourceHolder` protocol to formalize the Ship-to-ShipInstance interface contract
- Add `get_resource_names()` to ResourceRegistry for dynamic resource discovery
- Eliminate hardcoded `['fuel', 'energy', 'ammo']` lists in bridge methods
- Remove type-specific wrappers from Fleet that depend on removed methods

## Scope
**In:**
- ShipInstance type-specific method removal and caller migration
- Bug fixes in `resupply()` and `get_resource_percentage()`
- `IResourceHolder` protocol in `game/core/protocols.py`
- `get_resource_names()` on ResourceRegistry
- Fleet type-specific method refactoring
- Un-hardcoding resource name lists in `from_ship()`, `update_from_ship()`
- Un-hardcoding resource name lists in `BattleState.ShipState`
- Test updates (mock helpers, deleted tests)

**Out:**
- Changing the fundamental architecture (Dict vs ResourceState)
- Refactoring ResupplyEngine to be fully generic (supports all resources, not just fuel)
- Changing how ShipStatsCalculator works
- Changing save file format
- Adding new resource types

## Key Files
| Component | File Path |
|-----------|-----------|
| ShipInstance | `game/strategy/data/ship_instance.py` |
| Fleet | `game/strategy/data/fleet.py` |
| ResourceRegistry | `game/simulation/systems/resource_manager.py` |
| Protocols | `game/core/protocols.py` |
| ResupplyEngine | `game/strategy/engine/resupply_engine.py` |
| BattleState | `game/simulation/battle_state.py` |
| ShipStatsCalc (sim) | `game/simulation/entities/ship_stats.py` |
| Test: convenience | `tests/unit/strategy/ship_instance/test_convenience_methods.py` |
| Test: resupply engine | `tests/unit/strategy/engine/test_resupply_engine.py` |
| Test: resupply system | `tests/integration/strategy/test_resupply_system.py` |
| Test: turn resupply | `tests/integration/strategy/turn_engine/test_resupply.py` |
| Test: warp resources | `tests/unit/strategy/fleet/test_warp_resources.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Fix Bugs & Add Infrastructure [Medium]
**Objective:** Fix existing bugs and add the infrastructure needed for migration (protocol, ResourceRegistry method).
**Status:** Complete

See [phase_1_checklist.md](phase_1_checklist.md) for detailed tasks.

### Phase 2: Migrate Callers to Generic API [Medium]
**Objective:** Update all production code and test callers to use generic resource methods instead of type-specific ones. Also remove Fleet type-specific wrappers.
**Status:** Complete

See [phase_2_checklist.md](phase_2_checklist.md) for detailed tasks.

### Phase 3: Remove Type-Specific Methods & Clean Up [Simple]
**Objective:** Delete the 7 type-specific methods from ShipInstance, delete deprecated tests, and verify everything.
**Status:** Complete

See [phase_3_checklist.md](phase_3_checklist.md) for detailed tasks.

---

## Verification
- [x] All phase checklists complete
- [x] All tests passing (7557 passed)
- [x] No hardcoded `['fuel', 'energy', 'ammo']` lists remain in bridge methods
- [x] No `hasattr(ship, 'resources')` checks remain
- [x] No type-specific resource methods on ShipInstance
- [x] No type-specific resource wrappers on Fleet (internal to FleetResourceAggregator)
- [ ] Audit passed
- [ ] User verified
