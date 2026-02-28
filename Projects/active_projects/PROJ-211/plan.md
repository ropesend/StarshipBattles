# PROJ-211: Eradicate DI Fallback Anti-Pattern

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-211` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-211 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. GameSession Foundation | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Strategy Data Objects | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Initialization Functions | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI Services | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. UI Screens & Cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-27 21:39
**Active Phase:** Phase 1
**Last Action:** Project created from DI inconsistency review
**Next Action:** Begin Phase 1 - Add registries to GameSession, wire to TurnEngine
**Blockers:** None

## Overview
Systematic eradication of the `get_default_registry_provider()` fallback anti-pattern across the entire codebase. The DI infrastructure exists (PROJ-38 added parameters, PROJ-50 partially enforced them) but is in a half-migrated state where 13 production files silently fall back to global state.

**Source Review:** [2026-02-27_211222_general_di-inconsistency-strategy](../../Reviews/results/2026-02-27_211222_general_di-inconsistency-strategy/)

## Goals
- Make all DI parameters **required** (no Optional + fallback patterns)
- Thread registries from composition root (`app.py`) through all layers
- Remove all `get_default_registry_provider()` calls except in `app.py` and `conftest.py`
- Establish `VehicleClassService` strict-DI pattern as the standard
- Update docstrings that teach the anti-pattern

## Scope
**In:**
- 13 production files with DI violations (see design.md for full list)
- 2 legitimate composition roots (app.py, conftest.py) - verify only
- Test files that rely on global state for DI
- Docstrings teaching the anti-pattern

**Out:**
- `StrategyMetadataService.instance()` singleton (read-only metadata, acceptable)
- Minor severity items in leaf UI components (can be deferred)
- New feature development beyond DI remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| Composition Root | `game/app.py` |
| GameSession | `game/strategy/engine/game_session.py` |
| TurnEngine | `game/strategy/engine/turn_engine.py` |
| ShipInstance | `game/strategy/data/ship_instance.py` |
| FleetCapabilityCalc | `game/strategy/data/fleet_capability_calculator.py` |
| Fleet | `game/strategy/data/fleet.py` |
| StrategySessionFacade | `game/strategy/facade/strategy_session_facade.py` |
| component.py | `game/simulation/components/component.py` |
| ship_loader.py | `game/simulation/entities/ship_loader.py` |
| WorkshopContext | `game/ui/screens/workshop_context.py` |
| ComponentService | `game/ui/services/component_service.py` |
| ShipFactory | `game/ui/services/ship_factory.py` |
| DesignLoaderAdapter | `game/ui/services/design_loader_adapter.py` |
| Gold Standard | `game/ui/services/vehicle_class_service.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis, DI flow diagram, full findings
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (baseline: 7353)
- [ ] Zero `get_default_registry_provider()` calls outside composition roots
- [ ] Audit passed
- [ ] User verified
