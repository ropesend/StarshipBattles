# PROJ-101: Fleet Report Screen Enhancements

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-101` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-101 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Replace Detail Panel with DesignReportPanel | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. New Columns | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. New Filters | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Multi-Select + Remove Ships | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** All phases complete — Ready for Audit
**Last Action:** Phase 4 complete — Added Ctrl+click multi-select and "Remove Selected" button
**Next Action:** Trigger project audit (Protocol 04)
**Blockers:** None
**Context for Next Agent:** 7779 tests passing (baseline 7760 + 19 new). Modified: fleet_report_window.py (multi-select, removal logic), strategy_window_manager.py (empire pass-through), 1 new test file.

## Overview
Enhance the Fleet Report screen with: (1) Replace the right-side ShipDetailPanel with the shared DesignReportPanel used in Build Queue and Design Workshop, (2) Add 7 new data columns, (3) Add 2 new filter pairs, (4) Add multi-select ship removal that creates new fleets.

## Goals
- Replace right-side detail panel with DesignReportPanel (same component as Build Queue/Workshop)
- Add columns: Speed, Tonnage, Warp, Spaceyard, Transport, Resources, Cargo
- Add filters: Has Spaceyard, Has Cargo (including population)
- Add Ctrl+click multi-select and "Remove Selected" button that creates a new fleet from removed ships
- Keep column/filter names concise and consistent

## Scope
**In:** Detail panel replacement, new columns, new filters, multi-select, ship removal to new fleet
**Out:** Fleet splitting UI, fleet merge UI, drag-and-drop ship transfer, column width resizing

## Key Files
| Component | File Path |
|-----------|-----------|
| Fleet Report Window | `game/ui/screens/fleet_report_window.py` |
| ShipDetailPanel (to replace) | `game/ui/panels/ship_detail_panel.py` |
| DesignReportPanel (replacement) | `game/ui/panels/design_report_panel.py` |
| DesignStatsPanel (delegate) | `game/ui/panels/design_stats_panel.py` |
| DesignLoaderAdapter | `game/ui/services/design_loader_adapter.py` |
| SimulationDesignLoader | `game/simulation/services/design_loader.py` |
| Column Manager | `game/ui/screens/column_manager.py` |
| View Model | `game/ui/screens/fleet_report_view_model.py` |
| Filters/Sort | `game/ui/screens/fleet_report_filters.py` |
| Fleet model | `game/strategy/data/fleet.py` |
| Fleet Capability Calculator | `game/strategy/data/fleet_capability_calculator.py` |
| Empire | `game/strategy/data/empire.py` |
| Strategy Window Manager | `game/ui/screens/strategy_window_manager.py` |
| Fleet Speed Calculator | `game/strategy/services/fleet_speed_calculator.py` |
| Ship Stats Calculator | `game/strategy/services/ship_stats_calculator.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (baseline 7648 + new tests)
- [ ] Audit passed
- [ ] User verified
