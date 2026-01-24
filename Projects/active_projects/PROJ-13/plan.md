# PROJ-13: Code Quality & Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-13` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Dead Code Removal | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Documentation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Minor Fixes | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-01-24 05:30
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 - Dead code removal (quick wins)
**Blockers:** None - can start immediately for quick wins

## Overview
This project addresses **code quality issues, dead code, and documentation gaps**. These are lower priority than security and architecture but improve overall codebase health.

**Total Findings:** 80+ (Minor: 60+, Info: 20+)

**Dependencies:**
- Phase 1 (Dead Code) can start immediately
- Phases 2-3 should wait for PROJ-11 (architecture changes will affect docs)

## Goals
### Phase 1: Dead Code Removal (QUICK WINS)
- Delete marked-for-deletion directories (DC-02)
- Delete backup files (DC-01)
- Remove commented debug code (DC-04, DC-05, DC-06)
- Clean up empty __init__ files (DC-03)

### Phase 2: Documentation (MAJOR)
- Add Ship class docstrings (DOC-02)
- Add Component architecture docs (DOC-06)
- Complete type hints on critical methods (DOC-04)
- Add module-level documentation (DOC-01)

### Phase 3: Minor Fixes
- Remaining error handling improvements
- Code style consistency
- Naming conventions
- Technical debt markers (TODO/FIXME cleanup)

## Scope
**In:**
- Dead code directories and files
- Documentation in `game/simulation/`, `game/strategy/`
- Type hints on public APIs
- Minor error handling fixes

**Out:**
- Security fixes (PROJ-10)
- Architecture refactoring (PROJ-11)
- Performance optimization (PROJ-12)

## Key Files
| Component | File Path |
|-----------|-----------|
| Dead Directories | `Marked_For_Deletion_*`, `Debugging/Marked_for_Deletion_*` |
| Backup Files | `ui/test_lab_scene.py.backup` |
| Ship Docs | `game/simulation/entities/ship.py` |
| Component Docs | `game/simulation/components/component.py` |

## Verification
- [ ] All phase checklists complete
- [ ] No dead code directories
- [ ] Critical classes have docstrings
- [ ] Type hints on public methods
- [ ] All tests passing
