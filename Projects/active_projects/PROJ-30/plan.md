# PROJ-30: Strategy Mode: Layer Boundary Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-30` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-30 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical Fixes | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-01-27 14:30
**Active Phase:** Phase 1
**Last Action:** Implemented STRAT-01 fix - created SimulationDesignLoader and updated UI callers
**Next Action:** IDE/linter keeps reverting file changes - need to manually review and commit changes
**Blockers:** IDE auto-revert issue - files being restored to original state

### Session Progress (2026-01-27)
Successfully created the fix but IDE keeps reverting changes. The implementation is:

1. **Created:** `game/simulation/services/design_loader.py` - SimulationDesignLoader class
   - `load_ship_from_design_data()` - creates Ship from dict
   - `load_ship_from_file()` - loads Ship from JSON file

2. **Created:** `tests/unit/simulation/test_simulation_design_loader.py` - 9 tests, all passing

3. **Need to apply (keep getting reverted):**
   - Remove `load_design()` method from `game/strategy/systems/design_library.py`
   - Remove `from game.simulation.entities.ship import Ship` import
   - Update `game/ui/screens/workshop_screen.py` - 2 call sites
   - Update `game/ui/screens/build_queue_screen.py` - 1 call site
   - Update `tests/unit/strategy/test_design_library.py` - remove 2 obsolete tests

4. **Pattern for UI callers:**
   ```python
   # Before (strategy layer instantiating Ship):
   ship, msg = library.load_design(design_id, width, height)

   # After (simulation layer instantiating Ship):
   design_data = library.load_design_data(design_id)
   if design_data:
       loader = SimulationDesignLoader()
       ship = loader.load_ship_from_design_data(design_data, center_x=w//2, center_y=h//2)
   ```

## Overview
Systematic remediation of findings from review: 2026-01-27_general_self-contained-systems. Total findings selected: 1 (Critical: 1, Major: 0, Other: 0).

## Goals
- Address STRAT-01: Cross-layer import violation

## Scope
**In:**
- Medium

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| SimulationDesignLoader (new) | `game/simulation/services/design_loader.py` |
| DesignLibrary (to modify) | `game/strategy/systems/design_library.py` |
| Workshop Screen | `game/ui/screens/workshop_screen.py` |
| Build Queue Screen | `game/ui/screens/build_queue_screen.py` |
| Design Loader Tests | `tests/unit/simulation/test_simulation_design_loader.py` |
| Design Library Tests | `tests/unit/strategy/test_design_library.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
