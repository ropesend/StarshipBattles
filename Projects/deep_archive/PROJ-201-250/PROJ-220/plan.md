# PROJ-220: Tri-State Filter Widget & Filter Unification

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-220` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-220 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation: FilterState Enum & FilterStateManager | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. TriStateFilterWidget (Pygame Component) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Retrofit Fleet Report | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Retrofit Build Queue | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Planet List State Unification | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Cleanup & Verification | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-03-15
**Active Phase:** PROJECT COMPLETE
**Last Action:** Phase 6 complete — All dead code verified clean, full test suite passes (13,300 passed, 2 skipped)
**Next Action:** User manual verification of tri-state widget rendering (Task 6.2)
**Blockers:** None
**Context for Next Agent:** All 6 phases complete. Tri-state filter infrastructure built and deployed across Fleet Report (8 binary filters → 8 tri-state), Build Queue (6 toggles → 3 tri-state groups), and Planet List (state unified via PlanetListFilterManager). 122 net new tests added. Owner filter preset restore bug fixed (BUG-27 gap). Only remaining item: manual visual verification by user (Task 6.2 in phase_6_checklist.md).

## Overview
Replace paired Yes/No toggle buttons across Fleet Report and Build Queue windows with a unified tri-state filter control (Yes / No / Ignore). Create shared filter infrastructure (FilterState enum, FilterStateManager, TriStateFilterWidget) that all filter windows adopt. Planet List adopts the state manager for future extensibility but has no current binary filters to convert.

## Goals
- Create a reusable `TriStateFilterWidget` with 3 radio buttons (Yes/No/Ignore) per attribute
- Create a shared `FilterStateManager` base class for unified filter state management
- Retrofit Fleet Report's 8 binary filters (warp, spaceyard, cargo, 5 special capabilities)
- Retrofit Build Queue's 3 binary filter groups (location type, queue status, capabilities)
- Migrate Planet List to use FilterStateManager infrastructure (no tri-state conversion yet)
- Eliminate 3 divergent filter state patterns in favor of one consistent approach

## Scope
**In (tri-state conversion):**
- Fleet Report: Warp Capable, Spaceyard, Cargo, 5× Special Capabilities (8 binary filters → 8 tri-state widgets)
- Build Queue: Location Type (Planet/Fleet), Queue Status (Active/Empty), Capabilities (Ships/Complexes) (3 filter groups → 3 tri-state widgets each with 2 attributes... actually these are paired toggles per category, so 6 individual toggles → 3 tri-state widgets)
- Shared infrastructure: FilterState enum, FilterStateManager, TriStateFilterWidget

**In (state unification only):**
- Planet List: Adopt FilterStateManager for state management; existing multi-select/range filters unchanged

**Out:**
- Fleet Report Status filter (4-state: damaged/undamaged/derelict/destroyed — not binary)
- Planet List type filter (11-way multi-select)
- Planet List owner filter (3-way multi-select)
- Planet List range filters (numeric sliders)
- Any new filter capabilities (this project is infrastructure + retrofit only)

## Key Files
| Component | File Path |
|-----------|-----------|
| Triage findings | `Projects/active_projects/PROJ-220/findings/tristate_filter_unification.md` |
| **New: FilterState enum** | `game/ui/filters/filter_state.py` |
| **New: FilterStateManager** | `game/ui/filters/filter_state_manager.py` |
| **New: Filters package init** | `game/ui/filters/__init__.py` |
| **New: TriStateFilterWidget** | `game/ui/components/filters/tri_state_widget.py` |
| **New: Filter widget package init** | `game/ui/components/filters/__init__.py` |
| Fleet Report ViewModel | `game/ui/screens/fleet_report_view_model.py` |
| Fleet Report filters | `game/ui/screens/fleet_report_filters.py` |
| Fleet Report sidebar | `game/ui/screens/fleet_report_sidebar.py` |
| Fleet Report window | `game/ui/screens/fleet_report_window.py` |
| Fleet Data Source | `game/ui/screens/fleet_data_source.py` |
| Build Queue filter manager | `game/ui/screens/empire_build_queue_filter_manager.py` |
| Build Queue viewmodel | `game/ui/screens/empire_build_queue_viewmodel.py` |
| Build Queue sidebar | `game/ui/screens/empire_build_queue_sidebar.py` |
| Build Queue window | `game/ui/screens/empire_build_queue_window.py` |
| Planet List window | `game/ui/screens/planet_list_window.py` |
| Planet List sidebar | `game/ui/screens/planet_list_sidebar.py` |
| Planet List filters | `game/ui/screens/planet_list_filters.py` |
| Planet List presets | `game/ui/screens/planet_list_presets.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [x] All phase checklists complete
- [x] All tests passing (`pytest tests/ -n 12`) — 13,300 passed, 2 skipped
- [ ] All 3 windows render correctly with new filter UI (PENDING: manual user verification)
- [ ] Tri-state filters cycle through Yes/No/Ignore correctly (PENDING: manual user verification)
- [ ] Planet List presets still load/save correctly (PENDING: manual user verification)
- [ ] User verified
