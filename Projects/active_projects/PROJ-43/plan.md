# PROJ-43: Architecture Layer Violations Remediation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-43` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-43 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Verification of Previous Fixes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2A. UI-Simulation Decoupling - Setup | Complete | [phase_2a_checklist.md](phase_2a_checklist.md) |
| 2B. UI-Simulation Decoupling - Builder | Complete | [phase_2b_checklist.md](phase_2b_checklist.md) |
| 2C. UI-Simulation Decoupling - Workshop/Battle | Not Started | [phase_2c_checklist.md](phase_2c_checklist.md) |
| 3. Workshop Circular Import Fix | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. TurnEngine Constructor DI | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Registry Access Consolidation | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Simulation Deferred Imports | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Strategy Deferred Imports | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. BattleEngine-AI Decoupling | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Constant Consolidation | Not Started | [phase_9_checklist.md](phase_9_checklist.md) |
| 10. Package API Definition | Not Started | [phase_10_checklist.md](phase_10_checklist.md) |
| 11. Validation Consolidation | Not Started | [phase_11_checklist.md](phase_11_checklist.md) |
| 12. UI-Battle Interface | Not Started | [phase_12_checklist.md](phase_12_checklist.md) |

## Current State
**Last Updated:** 2026-01-28
**Active Phase:** Phase 2B Complete / Ready for Phase 2C
**Last Action:** Completed Phase 2B - Created UI services and decoupled builder package from simulation
**Next Action:** Begin Phase 2C - UI-Simulation Decoupling for Workshop/Battle screens
**Blockers:** None
**Context for Next Agent:**
- Phase 2B COMPLETE: Created 3 new UI services and updated 6 builder files
- New services created:
  - `game/ui/services/component_service.py` - Component and modifier registry access
  - `game/ui/services/vehicle_class_service.py` - Vehicle class data access
  - `game/ui/services/validation_service.py` - Ship validation facade
- New tests: 30 tests across 3 service test files (all passing)
- Builder files updated to use services:
  - `game/ui/screens/builder/main.py` - Uses ShipFactory, all 3 new services
  - `game/ui/screens/builder/legacy_components.py` - Uses ComponentService
  - `game/ui/screens/builder/modifier_logic.py` - Uses ComponentService (class-level injection)
  - `game/ui/screens/builder/schematic_view.py` - Uses VehicleClassService
  - `game/ui/screens/builder/right_panel.py` - Uses VehicleClassService
  - `game/ui/screens/builder/layer_panel.py` - Uses ValidationService
- Test files fixed for service injection:
  - `tests/unit/builder/test_schematic_cache_key.py`
  - `tests/unit/repro_issues/test_slider_increment.py`
- Test baseline: 5235 passed, 3 skipped (up from 5199 due to new service tests)
- Builder package no longer imports directly from simulation layer (except ShipIO for persistence)
- Services use lazy initialization pattern with dependency injection for testing

## Overview
This project addresses **21 architecture layer violations** identified in `findings_01_architecture_layer_violations.md`. The focus is on decoupling UI from simulation layer, completing DI migration, refactoring TurnEngine for extensibility, eliminating circular dependencies, and establishing clean package APIs.

## Goals
1. Re-verify Previous Fixes - Confirm PROJ-11/PROJ-38 completions
2. Decouple UI from Simulation - Remove direct imports of Ship, registries, services
3. Complete DI Migration - Finish deprecation of global registry access
4. Refactor TurnEngine to Constructor DI - Full dependency injection for extensibility
5. Eliminate Circular Dependencies - Resolve deferred imports with proper structure
6. Establish Clean APIs - Define __all__ exports for all packages
7. Consolidate Validation - Unify scattered validation logic

## Scope
**In:**
- All findings from `findings_01_architecture_layer_violations.md`
- AR-001 through AR-016, AR-01 through AR-10
- STR-004, SIM-002, SIM-008
- CQ-036, UI-024

**Out:**
- God class decomposition (separate project)
- New feature development
- Performance optimization (unless required for DI)

## Key Files
| Component | File Path |
|-----------|-----------|
| Core Registry | `game/core/registry.py` |
| Core Protocols | `game/core/protocols.py` |
| Core Constants | `game/core/constants.py` |
| UI Builder Main | `game/ui/screens/builder/main.py` |
| Workshop Screen | `game/ui/screens/workshop_screen.py` |
| Ship Entity | `game/simulation/entities/ship.py` |
| Fleet Data | `game/strategy/data/fleet.py` |
| Turn Engine | `game/strategy/engine/turn_engine.py` |
| Battle Engine | `game/simulation/systems/battle_engine.py` |
| Architecture Doc | `docs/ARCHITECTURE.md` |

## Test Baseline
- **5235 passed**, 3 skipped
- **~28354 warnings** (many are deprecation warnings to be addressed)

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [Source Findings](../../findings_01_architecture_layer_violations.md)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (5198+ passed)
- [ ] No new circular import warnings
- [ ] Deprecation warnings reduced
- [ ] Audit passed
- [ ] User verified
