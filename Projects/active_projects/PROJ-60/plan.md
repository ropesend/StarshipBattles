# PROJ-60: Break Down GalaxyTestScreen

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-60` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-60 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create Package & Extract Constants | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract Galaxy Mode Module | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract System Mode Module | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Slim Main Screen to Coordinator | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-06 20:05
**Active Phase:** Planning - Awaiting Approval
**Last Action:** Completed analysis and wrote detailed plan
**Next Action:** User approves plan, then begin Phase 1
**Blockers:** None

## Overview
Decompose `game/ui/screens/galaxy_test_screen.py` (1160 lines) into a `galaxy_test/` package with 4 modules, getting the main screen coordinator under 500 lines. Follows the `formation/` package pattern (absolute imports, `__all__`, docstrings).

## Goals
- Get `galaxy_test/screen.py` under 500 lines
- Each extracted module has a single, clear responsibility
- No behavior changes - pure refactor
- All existing tests continue to pass
- Only one import change needed: `game/app.py` line 31

## Scope
**In:**
- Decompose `galaxy_test_screen.py` into `galaxy_test/` package
- Update the single import in `game/app.py`
- Delete the original `galaxy_test_screen.py` file

**Out:**
- No new features or behavior changes
- No new tests (UI test tool with no existing tests)
- No changes to any other screen files

## Key Files
| Component | File Path |
|-----------|-----------|
| Original monolith | `game/ui/screens/galaxy_test_screen.py` (1160 lines) |
| Only consumer | `game/app.py` (line 31: import, line 403: instantiation) |
| Package pattern | `game/ui/screens/formation/__init__.py` (reference) |

## Target Structure
```
game/ui/screens/galaxy_test/
├── __init__.py          (~10 lines, re-export GalaxyTestScreen)
├── constants.py         (~40 lines, PLANET_TYPE_COLORS, layout constants)
├── galaxy_mode.py       (~260 lines, galaxy generation + rendering + UI)
├── system_mode.py       (~370 lines, system generation + rendering + inspector + UI)
└── screen.py            (~400 lines, coordinator: init, events, draw, update, modes)
```

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (baseline: 1185 passed, 1 pre-existing failure, 1 pre-existing error)
- [ ] Manual verification: launch Galaxy Test from main menu, test both modes
- [ ] Audit passed
- [ ] User verified
