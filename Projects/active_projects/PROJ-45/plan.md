# PROJ-45: Error Handling and Exception Management Refactor

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-45` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-45 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation - Exception Hierarchy & Error Codes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Core Layer - Fix Core Module Error Handling | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Simulation Layer - Components & Formulas | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. AI System - Target Evaluator & Controller | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Strategy Layer - Save/Load & Services | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. UI Layer - Asset Manager & Screens | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Documentation & Guidelines | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-01-30
**Active Phase:** Phase 6 - UI Layer
**Last Action:** Phase 5 complete - Strategy Layer Save/Load & Services updated
**Next Action:** Begin Phase 6 - UI Layer Asset Manager & Screens
**Blockers:** None

## Overview
Comprehensive refactoring of error handling across the Starship Battles codebase to improve maintainability, debuggability, and extensibility. This includes creating a custom exception hierarchy, standardizing error codes, fixing all 46+ broad exception handlers, and establishing guidelines for future development.

## Goals
- Create custom exception hierarchy for semantic error handling
- Standardize error codes for programmatic handling
- Fix ALL overly broad exception handlers (46+ instances)
- Eliminate silent exception swallowing
- Add proper exception context chaining (`raise from e`)
- Establish error handling guidelines for future development

## Scope
**In Scope:**
- All 30+ issues from `findings_04_error_handling.md`
- Custom exception hierarchy (`game/core/exceptions.py`)
- Error code enumeration (`game/core/error_codes.py`)
- All 46+ broad exception catches across 68 files
- 11 bare `except Exception:` clauses
- 6 silent `except: pass` patterns
- 12+ missing `raise from e` patterns
- Error handling documentation/guidelines

**Out of Scope:**
- Architectural layer violations (separate project)
- Performance optimizations beyond error handling
- New feature development

## Key Files
| Component | File Path |
|-----------|-----------|
| Exception Hierarchy | `game/core/exceptions.py` (NEW) |
| Error Codes | `game/core/error_codes.py` (NEW) |
| Formula System | `game/simulation/formula_system.py` |
| Component Loading | `game/simulation/components/component.py` |
| AI Targeting | `game/ai/target_evaluator.py` |
| Save/Load | `game/strategy/systems/save_game_service.py` |
| JSON Utils (Reference) | `game/core/json_utils.py` |
| Validation | `game/core/validation.py` |
| Guidelines | `docs/ERROR_HANDLING_GUIDELINES.md` (NEW) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- Source findings: `findings_04_error_handling.md`

## Verification
- [x] Baseline tests passing (5199 passed, 3 skipped)
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
