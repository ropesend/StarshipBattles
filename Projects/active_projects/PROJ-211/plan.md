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
| 1. GameSession Foundation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Strategy Data Objects | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Initialization Functions | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI Services | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. UI Screens & Cleanup | In Progress | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-28
**Active Phase:** Phase 5 (Tasks 5.5.1 + 5.6 COMPLETE)
**Last Action:** Task 5.6 COMPLETE - Removed ShipInstance fallback, updated ~18 test files
**Next Action:** Task 5.7 - Remove FleetCapabilityCalculator fallbacks
**Blockers:** None
**Note:** MAJOR MILESTONE - ShipInstance.get_calculated_stats() fallback REMOVED. Now raises ValueError if _registries=None.
**Progress this session:**
- REMOVED get_default_registry_provider() fallback from ShipInstance.get_calculated_stats()
- Updated 18 test files to pass registries where needed
- Key files updated:
  - tests/conftest.py make_mock_ship_instance - accepts registries param
  - tests/integration/save_load/conftest.py - game_session_with_state uses fresh_registries
  - tests/integration/strategy/production/*.py - ProductionEngine gets fresh_registries
  - tests/integration/strategy/turn_engine/conftest.py - create_mock_ship_instance updated
  - tests/repro_issues/test_bug_27_ordertype.py - local helper + tests updated
  - tests/unit/strategy/ship_instance/test_registries_di.py - test expects ValueError now
  - tests/unit/strategy/test_ship_resource_manager.py - fixture uses fresh_registries
  - tests/unit/strategy/test_fleet_battle_adapter.py - 9 tests updated
  - tests/unit/strategy/test_fleet_capability_calculator_di.py - 1 test updated
  - tests/unit/test_advanced_fleet_orders.py - 2 tests updated
- All tests pass: 12884 passed, 1 skipped, 4 pre-existing bug_13 failures

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
