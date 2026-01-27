# PROJ-21: Legacy Cleanup Phase 8: Tests and Patterns

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-21` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-21 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. ValidationResult Consolidation | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Exception Type Standardization | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Property Naming Standardization | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Test Fixture Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-01-26 21:30
**Active Phase:** Planning Complete - Ready for Implementation
**Last Action:** Comprehensive plan created with 6 phases, all decisions documented
**Next Action:** Begin Phase 1 - Create game/core/validation.py
**Blockers:** None

## Overview
Final phase of the 8-phase legacy code cleanup project. Consolidates 5 duplicate ValidationResult classes into a canonical implementation in game/core/, standardizes exception types and property naming, removes unused test fixture aliases, and documents/categorizes bug reproduction tests.

## Goals
- Consolidate ValidationResult to single canonical class in `game/core/validation.py`
- Standardize singleton exceptions (Exception → RuntimeError)
- Rename ALL_CAPS instance properties to lowercase (HEX_SIZE → hex_size)
- Remove unused test fixture aliases
- Document and categorize bug reproduction tests

## Scope
**In:**
- ValidationResult consolidation (5 implementations → 1)
- Singleton exception standardization (3 files)
- Property naming fixes (6 files)
- Unused fixture alias removal (2 aliases)
- Bug test documentation (27 files)

**Out:**
- Color function consolidation (different thresholds are intentional)
- String formatting migration (only 1 legitimate use)
- Modifier validation consolidation (different purposes)
- Enabling skipped simulation tests (requires separate test data work)

## Key Files
| Component | File Path |
|-----------|-----------|
| ValidationResult (canonical) | `game/core/validation.py` (NEW) |
| ValidationResult (simulation) | `game/simulation/validation/base.py` |
| ValidationResult (legacy) | `game/simulation/systems/validator.py` |
| ValidationResult (strategy) | `game/strategy/engine/turn_engine.py` |
| ValidationResult (UI) | `game/ui/screens/race_validator.py` |
| Singleton exceptions | `game/core/profiling.py`, `registry.py`, `screenshot_manager.py` |
| HEX_SIZE properties | `game/ui/screens/strategy_scene.py` + 5 related files |
| Test fixture aliases | `tests/unit/combat/conftest.py` |
| Bug reproduction tests | `tests/repro_issues/` (27 files) |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-26 | ValidationResult → game/core/validation.py | Clean architecture - all layers can import from core |
| 2026-01-26 | Keep color functions separate | Different thresholds (75%/50% vs 50%/20%) are intentional |
| 2026-01-26 | Remove only unused fixture aliases | basic_combat_ship and armed_combat_ship have zero actual usage |
| 2026-01-26 | Categorize bug tests, don't delete | Document status first, merge fixed bugs in future project |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [Phase 8 Plan](../../legacy_cleanup/PHASE_8_CLEANUP_TESTS_PATTERNS.md) - Original phase 8 specification

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (baseline: 4542 passed, 1 skipped)
- [ ] Application launches and runs
- [ ] No circular imports
