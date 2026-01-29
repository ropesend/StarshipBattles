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
| 2C. UI-Simulation Decoupling - Workshop/Battle | Complete | [phase_2c_checklist.md](phase_2c_checklist.md) |
| 3. Workshop Circular Import Fix | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. TurnEngine Constructor DI | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Registry Access Consolidation | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Simulation Deferred Imports | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Strategy Deferred Imports | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. BattleEngine-AI Decoupling | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Constant Consolidation | Not Started | [phase_9_checklist.md](phase_9_checklist.md) |
| 10. Package API Definition | Not Started | [phase_10_checklist.md](phase_10_checklist.md) |
| 11. Validation Consolidation | Not Started | [phase_11_checklist.md](phase_11_checklist.md) |
| 12. UI-Battle Interface | Not Started | [phase_12_checklist.md](phase_12_checklist.md) |

## Current State
**Last Updated:** 2026-01-28
**Active Phase:** Phase 6 COMPLETE - Ready for Phase 7
**Last Action:** Completed Phase 6 - Simulation Deferred Import analysis and refactoring
**Next Action:** Phase 7 - Strategy Deferred Imports
**Blockers:** None
**Context for Next Agent:**
- Phase 6 COMPLETE: Simulation Deferred Import Elimination
- Analysis: Documented 10 deferred imports across ship.py and stats.py
- Eliminated 5 deferred imports:
  - stats.py: Moved ResourceStorage/ResourceGeneration/ResourceConsumption to module level
  - stats.py: Removed redundant ability imports (code uses get_abilities())
  - ship.py: Removed redundant ShipStatsCalculator import (already at module level)
- Documented 5 intentional late imports (cannot be eliminated):
  - ship.py: WeaponAbility/SeekerWeaponAbility in max_weapon_range
  - ship.py: ModifierService in add_component/add_components_bulk
  - ship.py: ShipSerializer in to_dict/from_dict
- Updated docs/ARCHITECTURE.md with detailed late import documentation
- Added INTENTIONAL LATE IMPORT comments in ship.py
- IModifierApplicator interface SKIPPED (not beneficial after analysis)
- All tests passing: 5290 passed, 1 skipped
- Ready for Phase 7: Strategy Deferred Imports

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
- **5249 passed**, 3 skipped
- **~28363 warnings** (many are deprecation warnings to be addressed)

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
