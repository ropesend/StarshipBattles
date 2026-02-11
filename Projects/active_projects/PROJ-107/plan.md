# PROJ-107: Consistency and API Standardization

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-107` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-107 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Error Code Standardization | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Type Hint & Return Type Standardization | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Naming & API Standardization | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI Service DI & Return Type Standardization | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Simulation API Consistency | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Minor Cleanup Batch | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-11
**Active Phase:** Phase 5 Complete - Ready for Phase 6
**Last Action:** Phase 5 complete. Renamed BattleResult -> BattleServiceResult (11 files). Documented get_winner() return type layering. Added ResourceRegistry return convention docstring. Changed ValueError -> StateException in battle_controller.py.
**Next Action:** Begin Phase 6 - Minor Cleanup Batch
**Blockers:** None
**Test Baseline:** 8185 tests passing

## Overview
Standardize APIs, naming conventions, type hints, error handling patterns, and return types across the codebase. The 2026-02-10 sweep found 85 consistency violations across all layers. This project targets the highest-impact items: naming inconsistencies that cause API confusion, missing type hints on critical paths, inconsistent error handling, and return type mismatches.

## Phase Summary

### Phase 1: Error Code Standardization (5 tasks, ~Simple)
Add AI category to ErrorCode enum, replace raw string error codes with enum values, fix invalid error codes in documentation. All CRITICAL error code findings.

### Phase 2: Type Hint & Return Type Standardization (6 tasks, ~Medium)
Add missing return type hints to critical public APIs in AI, simulation, and UI layers. Replace `Any` with `HexCoord` in strategy commands. Standardize `to_dict()` return type annotations.

### Phase 3: Naming & API Standardization (4 tasks, ~Simple)
Delete duplicate `add_ship_instance()`, delete redundant `_stat_*` wrappers, rename ambiguous `check_missiles` parameter, add `is_alive()` semantic documentation.

### Phase 4: UI Service DI & Return Type Standardization (2 tasks, ~Medium)
Standardize DI parameter naming across UI services (`registry_provider`). Document ShipIOAdapter return type convention.

### Phase 5: Simulation API Consistency (4 tasks, ~Medium-Complex)
Rename `BattleResult` -> `BattleServiceResult`, document `get_winner()` return types, document collection return convention, standardize exception types in battle_controller.

### Phase 6: Minor Cleanup Batch (3 tasks, ~Simple)
Document thread safety convention, add strategy layer return type hints, document deferred items (13 findings deferred to other projects).

## Goals
- Standardize error code usage (ErrorCode enum vs raw strings)
- Fix return type inconsistencies (BattleResults vs BattleResult, Optional vs empty collections)
- Add missing type hints to critical public APIs
- Standardize naming conventions (method prefixes, parameter names)
- Unify DI patterns across UI services
- Document deferred items for future projects

## Scope
**In:**
- Critical/Major consistency findings from all 5 shards
- Naming convention standardization
- Type hint additions on public APIs
- Error handling pattern unification
- Return type standardization

**Out:**
- Event handler rename (handle_event vs process_event) - 50+ files, needs own PROJ
- Ability lifecycle method standardization - deferred to PROJ-88
- God class facade patterns - deferred to PROJ-86/87/88/89
- Click handler protocol standardization - needs own PROJ
- Serialization pattern unification - too large for this scope
- Docstring standardization (lower priority, INFO-level findings)
- Comment style unification
- Import organization (cosmetic, use tooling)

## Deferred Findings (Documented in Phase 6)
| Finding | Reason | Destination |
|---------|--------|-------------|
| CON-UI1-001 | 50 files, needs own PROJ | Future UI standardization |
| CON-SIM-006 | Ability lifecycle methods | PROJ-88 |
| CON-SIM-009 | Lazy init patterns | PROJ-86/87/88/89 |
| CON-SIM-010 | Ship facade | PROJ-88 |
| CON-SIM-011 | Serialization | Future PROJ |
| CON-STR-007 | fleet vs fleet_id | PROJ-87 |
| CON-STR-010 | Error handling returns | Future PROJ |
| CON-STR-011 | from_dict signatures | Future PROJ |
| CON-UI2-006 | ShipThemeManager singleton | PROJ-86 |
| CON-UI2-008 | Camera API | PROJ-89 |
| CON-UI2-009 | BattleUIService errors | Future PROJ |
| CON-UI1-004 | Return type inconsistency | Future UI standardization |
| CON-UI1-005 | Click handler params | Future UI standardization |

## Key Files
| Component | File Path |
|-----------|-----------|
| Error codes | `game/core/error_codes.py`, `game/core/exceptions.py` |
| AI naming | `game/ai/controller.py`, `game/ai/target_evaluator.py` |
| Battle results | `game/simulation/battle_state.py`, `game/simulation/services/battle_service.py` |
| Ship stats hints | `game/simulation/entities/ship_stats.py` |
| Strategy commands | `game/strategy/engine/commands.py` |
| UI services DI | `game/ui/services/*.py` |
| Resource manager | `game/simulation/systems/resource_manager.py` |
| Battle controller | `game/simulation/battle_controller.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- **Source sweep:** `Reviews/results/2026-02-10_sweep_full-codebase-sweep/findings/consistency_*.md`

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (8164+ baseline)
- [ ] Type checker passes on modified files
- [ ] Audit passed
- [ ] User verified
