# PROJ-89: God Class Decomposition - Remaining UI Tier

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-89` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-89 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. DesignSelectorWindow Image Helper | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. EmpireBuildQueueWindow Formatter | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. EmpireBuildQueueWindow Filter Manager | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-09
**Active Phase:** Phase 1
**Last Action:** Project planning complete
**Next Action:** Begin Phase 1 - Extract design image helper
**Blockers:** None

## Overview
Decompose the two remaining oversized UI classes: DesignSelectorWindow (716 lines, 17 methods) and EmpireBuildQueueWindow (948 lines, 30 methods). Extracts pure utility/formatting/state-management concerns into focused helper modules, reducing each class to its core UI orchestration responsibility. This is the final pass of the UI tier god class decomposition effort.

## Goals
- Extract image loading utilities from DesignSelectorWindow into a reusable helper (~168 lines)
- Extract data formatting methods from EmpireBuildQueueWindow into a standalone formatter (~100+ lines)
- Extract filter state management from EmpireBuildQueueWindow into a dedicated filter manager (~150 lines)
- Maintain 100% backward compatibility via facade pattern (original classes remain public API)
- All existing tests pass without modification

## Scope
**In:**
- `game/ui/screens/design_selector_window.py` (716 lines) - extract image helper
- `game/ui/screens/empire_build_queue_window.py` (948 lines) - extract formatter and filter manager
- New helper modules in `game/ui/screens/`
- New unit tests for extracted modules
- Updating existing classes to delegate to new modules

**Out:**
- RaceSetupScreen, FleetReportWindow, FormationEditor, StrategyScreen (already well-decomposed or marginal gains)
- Any behavioral changes to the UI
- Changes to non-UI layers
- Any new UI features

## Key Files
| Component | File Path |
|-----------|-----------|
| DesignSelectorWindow | `game/ui/screens/design_selector_window.py` |
| EmpireBuildQueueWindow | `game/ui/screens/empire_build_queue_window.py` |
| New: Design Image Helper | `game/ui/screens/design_image_helper.py` |
| New: Build Queue Formatter | `game/ui/screens/empire_build_queue_formatter.py` |
| New: Build Queue Filter Manager | `game/ui/screens/empire_build_queue_filter_manager.py` |
| Existing Tests (Design Selector) | `tests/integration/ui/test_design_selector.py` |
| Existing Tests (Build Queue) | `tests/unit/ui/screens/test_empire_build_queue_window.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
