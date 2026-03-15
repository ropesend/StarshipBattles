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
| 1. Foundation: FilterState Enum & FilterStateManager | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. TriStateFilterWidget (Pygame Component) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Retrofit Fleet Report | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Retrofit Build Queue | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Planet List State Unification | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Cleanup & Verification | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-03-14 21:00
**Active Phase:** Planning
**Last Action:** Plan approved (pending user confirmation)
**Next Action:** Begin Phase 1 — create FilterState enum and FilterStateManager
**Blockers:** None
**Context for Next Agent:** Test baseline is 13,178 passed, 2 skipped. All decisions are in decisions.md. Design rationale is in design.md. Triage context is in findings/tristate_filter_unification.md.

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
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] All 3 windows render correctly with new filter UI
- [ ] Tri-state filters cycle through Yes/No/Ignore correctly
- [ ] Planet List presets still load/save correctly
- [ ] User verified
