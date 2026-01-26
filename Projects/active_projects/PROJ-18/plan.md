# PROJ-18: Standardize Registry Access

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-18` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-18 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix ModifierService Anti-Pattern | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Delete DataService | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Add New Registry Utility Functions | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Fix Remaining Anti-Patterns | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-01-25 17:30
**Active Phase:** Planning Complete - Ready for Implementation
**Last Action:** Created detailed phase checklists with specific tasks
**Next Action:** Begin Phase 1 - Fix ModifierService Anti-Pattern
**Blockers:** None

## Overview
This project standardizes registry access patterns across the codebase by:
1. Replacing direct `RegistryManager.instance()` access with utility functions
2. Deleting unused DataService class
3. Adding missing utility functions (freeze_registry, set_validator, clear_registry)

This is Phase 5 of the larger Legacy Code Cleanup initiative.

## Goals
- Replace direct singleton access in production code with Tier 1 utility functions
- Remove unused DataService facade class
- Add missing utility functions for API completeness
- Document the tiered access pattern

## Scope
**In:**
- ModifierService anti-pattern fixes (4 locations)
- DataService deletion (unused class)
- New utility functions in registry.py
- ShipValidator anti-pattern fix (1 location)
- Documentation updates

**Out:**
- Test code anti-patterns (275 occurrences - mostly acceptable `.clear()` calls)
- Pre-existing test failures (5 tests unrelated to registry)
- UI builder code (not needed - already uses utility functions correctly)

## Key Files
| Component | File Path |
|-----------|-----------|
| Registry System | `game/core/registry.py` |
| ModifierService | `game/simulation/services/modifier_service.py` |
| DataService | `game/simulation/services/data_service.py` (DELETE) |
| Services __init__ | `game/simulation/services/__init__.py` |
| ShipValidator | `game/simulation/ship_validator.py` |
| DataService Tests | `tests/unit/services/test_data_service.py` (DELETE) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [Phase 5 Legacy Cleanup](../../legacy_cleanup/PHASE_5_STANDARDIZE_REGISTRY_ACCESS.md) - Original phase document

## Pre-existing Test Failures (Out of Scope)
These 5 tests fail before this project and are unrelated:
- `test_builder_warning_logic.py::test_change_class_empty_ship`
- `test_builder_warning_logic.py::test_change_class_non_empty_ship`
- `test_builder_warning_logic.py::test_change_type_empty_ship`
- `test_builder_warning_logic.py::test_change_type_non_empty_ship`
- `test_advanced_fleet_orders.py::test_intercept_integration`

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (except 5 pre-existing failures)
- [ ] No anti-patterns in production code
- [ ] Audit passed
- [ ] User verified
