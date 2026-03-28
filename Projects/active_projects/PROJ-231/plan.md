# PROJ-231: Star List Panel

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-231` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-231 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Data Layer | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Core Logic | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Star List Window | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Strategy Screen Integration | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-03-28
**Active Phase:** Complete
**Last Action:** All 4 phases complete. Full test suite passes (13900 passed, 0 failed).
**Next Action:** User verification — launch game and test the Star List Window.
**Blockers:** None
**Context for Next Agent:** All code implemented. 6 new files created, 6 existing files modified, 6 test files updated for mock compatibility. 33 new tests added.

## Overview
Create a new Star List Panel UI window that displays all stars in the galaxy with sortable/reorderable columns for every star attribute, sidebar filters for all attributes (type, mass, temperature, luminosity, age, radius, name search), navigation to the star's system on the strategy map, and preset save/load. Mirrors the existing Planet List Window architecture exactly.

## Goals
- Display all stars in the galaxy in a filterable, sortable table
- Allow filtering by star type (8 types), mass, temperature, luminosity, age, radius
- Support sorting and column reordering via the existing VirtualTable infrastructure
- Navigate to a star's system location on the strategy map
- Include all star attributes as columns (including 9 spectrum bands, hidden by default)
- Add a "Stars" button to the strategy screen top bar

## Scope
**In:**
- StarListWindow (UIWindow) with VirtualTable, sidebar filters, presets
- Stars button in strategy screen top bar
- Navigation to star's system location
- All star attributes as sortable columns
- Filter by type, mass, temperature, luminosity, age, radius, name

**Out:**
- Star detail panel (no equivalent to PlanetReportPanel — stars don't need one)
- Keyboard shortcut / InputAction for opening star list (can be added later)
- Star icon/portrait rendering in table rows (can be added later)
- Spectrum band filtering via range sliders (can be added later; columns exist for display)

## Key Files
| Component | File Path |
|-----------|-----------|
| Star domain model | `game/strategy/data/stars.py` |
| StarInfo DTO | `game/strategy/facade/dto/system_dto.py` |
| StrategySessionFacade | `game/strategy/facade/strategy_session_facade.py` |
| Planet list window (template) | `game/ui/screens/planet_list_window.py` |
| Planet list filters (template) | `game/ui/screens/planet_list_filters.py` |
| Planet filter manager (template) | `game/ui/screens/planet_list_filter_manager.py` |
| Planet sidebar (template) | `game/ui/screens/planet_list_sidebar.py` |
| Planet data source (template) | `game/ui/screens/planet_data_source.py` |
| Planet presets (template) | `game/ui/screens/planet_list_presets.py` |
| VirtualTable | `game/ui/components/table/virtual_table.py` |
| TableColumnManager | `game/ui/components/table/column_manager.py` |
| ITableDataSource | `game/ui/components/table/data_source.py` |
| SingleSelect | `game/ui/components/table/selection.py` |
| Strategy panel manager | `game/ui/screens/strategy_panel_manager.py` |
| Strategy UI | `game/ui/screens/strategy_ui.py` |
| Strategy window manager | `game/ui/screens/strategy_window_manager.py` |
| Strategy event router | `game/ui/screens/strategy_event_router.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest for parallel execution

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing: `python -m pytest tests/ -n 12`
- [ ] Launch game, open strategy screen, click "Stars" button — window opens
- [ ] All columns display correct data, sort works, reorder works
- [ ] Filters work (type, ranges, name search)
- [ ] Navigate to star centers camera on system
- [ ] Preset save/load works
- [ ] Audit passed
- [ ] User verified
