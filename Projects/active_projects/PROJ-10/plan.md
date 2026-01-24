# PROJ-10: Security & Data Integrity Fixes

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-10` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-10 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Security Vulnerabilities | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Data Integrity Issues | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Error Handling Hardening | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-01-24 05:15
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 - Security fixes
**Blockers:** None

## Overview
This project addresses **critical security vulnerabilities and data integrity issues** identified in the code review. These issues must be fixed before other architectural improvements to ensure the codebase is safe and reliable.

**Total Findings:** 12 (Critical: 7, Major: 5)

## Goals
### Phase 1: Security Vulnerabilities (CRITICAL)
- Fix formula_system.py eval() security risk (MOD-SIM-04)
- Fix shell command injection in screenshot_manager.py (ERR-11)

### Phase 2: Data Integrity Issues (CRITICAL)
- Implement fleet order deserialization (MOD-STR-01)
- Fix save metadata mismatch risk (MOD-STR-13)
- Fix race condition in design migration (ERR-13)

### Phase 3: Error Handling Hardening (MAJOR)
- Fix bare except clauses (ERR-01, ERR-02)
- Fix formula eval silent return (ERR-05)
- Add logging to swallowed exceptions
- Improve error context in component loading

## Scope
**In:**
- `game/simulation/formula_system.py` - Replace eval() with safe parser
- `game/core/screenshot_manager.py` - Fix shell injection
- `game/strategy/data/fleet.py` - Implement order deserialization
- `game/strategy/systems/save_game_service.py` - Fix save integrity issues
- `game/ui/screens/save_selection_window.py` - Fix bare except
- `game/simulation/systems/persistence.py` - Fix silent exceptions
- Error handling patterns across codebase

**Out:**
- Architectural refactoring (separate project)
- Performance optimization (separate project)
- UI improvements (separate project)

## Key Files
| Component | File Path |
|-----------|-----------|
| Formula System | `game/simulation/formula_system.py` |
| Screenshot Manager | `game/core/screenshot_manager.py` |
| Fleet Orders | `game/strategy/data/fleet.py` |
| Save Service | `game/strategy/systems/save_game_service.py` |
| Save Selection | `game/ui/screens/save_selection_window.py` |
| Persistence | `game/simulation/systems/persistence.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [Review Report](../../Reviews/results/2026-01-24_general_maintainability-extensibility-health/report.md)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Security vulnerabilities addressed
- [ ] Data integrity verified with save/load tests
- [ ] Audit passed
