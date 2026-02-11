# PROJ-98: Empire Build Yards Screen Enhancement

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-98` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-98 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix Event Handling | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Resource Consumption Columns | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Column Sorting & Reordering | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Final Verification | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-10 16:10
**Active Phase:** Planning Complete - Ready for Implementation
**Last Action:** Plan approved, all project files populated
**Next Action:** Begin Phase 1, Task 1.1 - write event handling tests
**Blockers:** None
**Baseline:** 7595 tests passing, 0 failures

## Overview
The Empire Build Yards window shows all space yards across the empire. Four issues need fixing: (1) column visibility toggles don't respond to clicks, (2) no column sorting or reordering, (3) filter toggles don't respond to clicks, and (4) missing resource consumption columns. Issues #1 and #3 share the same root cause (wrong pygame event type). Issue #2 requires integrating the existing ColumnManager pattern. Issue #4 requires 10 new columns showing per-resource construction costs.

## Goals
- Fix column toggle and filter toggle button clicks (broken event handling)
- Add sortable, reorderable column headers using ColumnManager pattern
- Add 10 resource columns (5 current consumption rate + 5 total cost) for the 5 planet resources
- All 10 resource columns visible by default

## Scope
**In:**
- Fix `process_event()` to use `pygame_gui.UI_BUTTON_PRESSED`
- Integrate `ColumnManager` from `planet_list_columns.py` for header sort/reorder
- Add `sort_sources()` to `BuildQueueFilterManager`
- Add resource rate and total cost formatter functions
- Add 10 column definitions to `DEFAULT_COLUMNS`
- Wire column values through `_get_column_value()`
- Full test coverage for all changes

**Out:**
- Virtual scrolling / VirtualListRenderer (future enhancement)
- Sidebar scrolling for tall column lists (future enhancement)
- PROJ-97 build_rate changes (separate project)
- Visual row highlighting for selected rows (not requested)

## Key Files
| Component | File Path |
|-----------|-----------|
| Main window | `game/ui/screens/empire_build_queue_window.py` (833 lines) |
| Filter/column manager | `game/ui/screens/empire_build_queue_filter_manager.py` (151 lines) |
| Data formatters | `game/ui/screens/empire_build_queue_formatter.py` (132 lines) |
| ColumnManager (reuse) | `game/ui/screens/planet_list_columns.py` (201 lines) |
| Sort pattern (reference) | `game/ui/screens/planet_list_filters.py:97-144` |
| Resource constants | `game/core/constants.py` - `PLANET_RESOURCES` |
| Window tests | `tests/unit/ui/screens/test_empire_build_queue_window.py` (1352 lines) |
| Filter manager tests | `tests/unit/ui/screens/test_empire_build_queue_filter_manager.py` (304 lines) |
| Formatter tests | `tests/unit/ui/screens/test_empire_build_queue_formatter.py` (250 lines) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] Phase 1: Column toggles and filter toggles respond to clicks
- [ ] Phase 2: 10 resource columns display correct data
- [ ] Phase 3: Column headers sort and reorder
- [ ] Phase 4: Full test suite passes (7595+ tests)
- [ ] All phase checklists complete
- [ ] Audit passed
- [ ] User verified
