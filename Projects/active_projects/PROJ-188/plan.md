# PROJ-188: Strategy Layer List UI Consolidation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-188` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-188 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Generic Components (Foundation) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate Fleet Report | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate Planet List | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate Empire Build Queue | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Migrate Event Log | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Cleanup | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 3 Complete
**Last Action:** Migrated PlanetListWindow to VirtualTable + PlanetDataSource + SingleSelect. Created PlanetDataSource with 29 tests. VirtualListRenderer has 0 reverse dependencies.
**Next Action:** Begin Phase 4: Migrate Empire Build Queue
**Blockers:** None
**Context for Next Agent:** 12,601 tests passing (+29 new from PlanetDataSource). PlanetListWindow now uses VirtualTable. Old VirtualListRenderer (planet_list_renderer.py) ready for Phase 6 deletion. ColumnManager (planet_list_columns.py) still used by empire_build_queue_window.py (Phase 4 target). Ready for Phase 4 (BuildQueueDataSource + EmpireBuildQueueWindow migration).

## Overview
Consolidates 4 duplicated list/table UI implementations (Planet List, Fleet Report, Empire Build Queue, Event Log) into a single generic `VirtualTable` component system under `game/ui/components/table/`, with domain-specific `ITableDataSource` adapters. Eliminates ~1,088 lines of duplicated rendering code while giving all lists virtual scrolling, sortable/reorderable columns, and a consistent architecture.

## Goals
- Eliminate duplicated virtual scrolling, column management, header rendering, and row pooling code
- Create reusable generic table components (VirtualTable, TableHeader, TableColumnManager)
- Unify data extraction behind single ITableDataSource base class
- Give all 4 lists virtual scrolling, sortable columns, and reorderable columns
- Add pluggable selection strategies (SingleSelect, MultiSelect, NoSelect)
- Delete ~1,088 lines of old rendering code with zero backward compatibility retention

## Scope
**In:**
- Generic table components in `game/ui/components/table/`
- 4 domain DataSource adapters (Fleet, Planet, BuildQueue, EventLog)
- Migration of all 4 windows to use VirtualTable
- Deletion of FleetListRenderer, VirtualListRenderer, both ColumnManagers
- Test migration and new test creation

**Out:**
- Sidebar UI changes (filter UIs stay as-is)
- ViewModel refactoring (FleetListViewModel, EmpireBuildQueueViewModel stay as-is)
- Filter logic changes (planet_list_filters, fleet_report_filters stay as-is)
- Build Queue screen (per-hex, not empire-wide) — only empire_build_queue_window migrated
- BuildQueueListWindow (simple list window, too different from table pattern)

## Key Files
| Component | File Path |
|-----------|-----------|
| VirtualTable (NEW) | `game/ui/components/table/virtual_table.py` |
| TableHeader (NEW) | `game/ui/components/table/header.py` |
| TableColumnManager (NEW) | `game/ui/components/table/column_manager.py` |
| ITableDataSource (NEW) | `game/ui/components/table/data_source.py` |
| ISelectionStrategy (NEW) | `game/ui/components/table/selection.py` |
| FleetDataSource (NEW) | `game/ui/screens/fleet_data_source.py` |
| PlanetDataSource (NEW) | `game/ui/screens/planet_data_source.py` |
| BuildQueueDataSource (NEW) | `game/ui/screens/empire_build_queue_data_source.py` |
| EventLogDataSource (NEW) | `game/ui/screens/event_log_data_source.py` |
| FleetReportWindow (MODIFY) | `game/ui/screens/fleet_report_window.py` |
| PlanetListWindow (MODIFY) | `game/ui/screens/planet_list_window.py` |
| EmpireBuildQueueWindow (MODIFY) | `game/ui/screens/empire_build_queue_window.py` |
| EventLogWindow (MODIFY) | `game/ui/screens/event_log_window.py` |
| FleetListRenderer (DELETE) | `game/ui/screens/fleet_list_renderer.py` (426 lines) |
| Fleet ColumnManager (DELETE) | `game/ui/screens/column_manager.py` (234 lines) |
| VirtualListRenderer (DELETE) | `game/ui/screens/planet_list_renderer.py` (227 lines) |
| Planet ColumnManager (DELETE) | `game/ui/screens/planet_list_columns.py` (201 lines) |
| UIConfig (REFERENCE) | `game/ui/config.py` |
| Colors (REFERENCE) | `game/ui/colors.py` |
| Protocols (REFERENCE) | `game/core/protocols.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Single ITableDataSource base class (not split protocols) | One entry point for agents; required + optional methods with defaults |
| 2026-02-24 | Pluggable ISelectionStrategy pattern | Most extensible — new modes = new class, not table modification |
| 2026-02-24 | Always virtual scrolling for all 4 lists | Consistency; Build Queue + Event Log gain performance |
| 2026-02-24 | Unified scroll math: start_percentage | 3/4 existing implementations use this; cleaner API |
| 2026-02-24 | VirtualTable owns selection highlighting | Selection is a table concern; DataSource for domain-specific highlights only |
| 2026-02-24 | Fleet Report migrated first (Phase 2) | Best test coverage (~158 tests) validates architecture |
| 2026-02-24 | Migrate Event Log to VirtualTable | Gains virtual scrolling, sortable columns |
| 2026-02-24 | Column value extraction in DataSource | Decouples domain logic from generic component |
| 2026-02-24 | Header sort indicators unified to ▲/▼ | Consistent across all tables |
| 2026-02-24 | EventBus preserved for Build Queue | Important for MVVM pattern |
| 2026-02-24 | Delete old renderers after migration | System Migration Policy: eradicate old system completely |

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing: `pytest tests/ -n 12`
- [ ] No imports reference deleted files
- [ ] All 4 windows use VirtualTable
- [ ] Test count >= 12,366 (plus new tests)
- [ ] Audit passed
- [ ] User verified
