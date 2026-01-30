# PROJ-50: Strict Dependency Injection Refactor

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-50` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-50 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Infrastructure | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. UI Layer Strictness | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Strategy Services | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Strategy Data | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Simulation Services | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Core Entities | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Big Bang Removal | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-01-30
**Active Phase:** Phase 4
**Last Action:** Completed Phase 3 - Strategy Services
**Next Action:** Begin Phase 4 - Strategy Data
**Blockers:** None
**Context:** Strategy services updated for strict DI. Removed get_default_registry_provider from ship_stats_calculator.py, resource_management_engine.py. Made registries required. Updated TurnEngine to pass registries. Updated ShipInstance with fallback for tests. Updated 5 test files. 838 strategy tests passing. Pre-existing failures unrelated to DI.

## Overview
Eliminate the "Service Locator" anti-pattern by removing `get_default_registry_provider()` and `_get_registries_fallback()`. Enforce mandatory `GameRegistries` injection in all core entities.

**Success Metric:** `grep -r "get_default_registry_provider" game/` returns 0 results (excluding registry.py definition).

## Goals
- Remove all `_get_registries_fallback()` methods (4 implementations)
- Remove all direct calls to `get_default_registry_provider()` outside registry.py
- Make `registries` parameter required in Component, Ship, and services
- Ensure all tests use DI fixtures instead of global state
- Keep module-level constants for UI hot-reload (documented exception)

## Scope
**In Scope:**
- Simulation layer: Component, Ship, BattleState, ShipSerializer, ShipValidator
- Strategy layer: ShipStatsCalculator, VehicleDesignService, ShipInstance, Fleet
- UI layer: builder_widgets, workshop_screen, workshop_event_router
- Test infrastructure: fixtures, repro_issues tests

**Out of Scope:**
- `game/core/registry.py` - keeps RegistryManager singleton for initialization
- `game/app.py` - keeps initial registry setup (composition root)
- Module-level COMPONENT_REGISTRY/MODIFIER_REGISTRY - kept for hot-reload

## Key Files
| Component | File Path |
|-----------|-----------|
| Global State | `game/core/registry.py` |
| Component | `game/simulation/components/component.py` |
| Ship | `game/simulation/entities/ship.py` |
| ShipSerializer | `game/simulation/entities/ship_serialization.py` |
| BattleState | `game/simulation/battle_state.py` |
| ShipValidator | `game/simulation/ship_validator.py` |
| ShipStatsCalculator | `game/strategy/services/ship_stats_calculator.py` |
| VehicleDesignService | `game/simulation/services/vehicle_design_service.py` |
| ShipInstance | `game/strategy/data/ship_instance.py` |
| Fleet | `game/strategy/data/fleet.py` |
| BuilderWidgets | `game/ui/panels/builder_widgets.py` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-30 | Strict DI at ViewModel boundary | Single injection point simplifies UI layer |
| 2026-01-30 | Adapt stages to 7 phases | User guidance + discovered gaps (ShipInstance, Fleet) |
| 2026-01-30 | Keep module-level constants | Breaking hot-reload would regress builder UX |
| 2026-01-30 | Defer test baseline fix | Pre-existing failures from another project |

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] `grep -r "get_default_registry_provider" game/` returns 0 (excl registry.py)
- [ ] `grep -r "_get_registries_fallback" game/` returns 0
- [ ] All tests passing: `pytest tests/ -n 4`
- [ ] Game launches and runs
- [ ] Manual testing passed
- [ ] User verified
