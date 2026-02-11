# PROJ-81: Sector Build Queue Window Fixes

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-81` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-81 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix Stats Display + Cost Calculation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Build Queue Display Fixes | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Build Yards Panel Width | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Queue Item Selection + Design Identity | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-08
**Active Phase:** All phases complete - ready for audit
**Last Action:** Phase 4 complete - Queue item click updates design report, identity labels added to DesignReportPanel
**Next Action:** Trigger audit
**Blockers:** None

## Overview
The Sector Build Queue window has 7 UI/logic bugs that make it unusable for production management. Stats show all dashes ("--"), production costs are missing, the Build Yards list is too narrow, terminology is wrong, queue selection doesn't update the design panel, design identity info is missing, and production time always shows 1 turn regardless of cost.

## Goals
- Fix all stats displaying as "--" in the right panel
- Fix production time calculation (currently always returns 1)
- Show per-turn resource costs in queue items
- Widen Build Yards list for readability
- Fix header terminology ("Build Queue - [Name]")
- Enable queue item click to show design details
- Show design name, vehicle type, and class in right panel

## Scope
**In:** All 7 reported issues (a-g), all in the build queue UI screen and its supporting panels/controllers

**Out:** Production engine tick processing, empire-wide build queue window, design workshop, save/load changes

## Key Files
| Component | File Path |
|-----------|-----------|
| Build Queue Screen | `game/ui/screens/build_queue_screen.py` |
| Build Queue Controller | `game/ui/panels/build_queue_controller.py` |
| Design Report Panel | `game/ui/panels/design_report_panel.py` |
| Design Stats Panel | `game/ui/panels/design_stats_panel.py` |
| Drag Handler | `game/ui/panels/build_queue_drag_handler.py` |
| Design Metadata | `game/strategy/data/design_metadata.py` |
| Ship Stats Calculator | `game/simulation/entities/ship_stats.py` |
| Build Queue Source | `game/strategy/data/build_queue_source.py` |
| Stats Config | `game/ui/screens/builder/stats_config.py` |

## Root Cause Analysis

| Issue | Root Cause | Fix Location |
|-------|-----------|--------------|
| (a) Stats show "--" | `DesignReportPanel.update_design()` creates `DesignStatsPanel(ship=ship)` but never calls `update_stats(ship)` to populate values | `design_report_panel.py:132` |
| (b) No costs in queue | `DesignMetadata._calculate_resource_cost()` reads `comp_data.get("cost", {})` from design JSON, but design files don't store cost. Returns `{}` | `build_queue_controller.py:170-211` |
| (c) Build Yards too narrow | Panel width hardcoded to 280px | `build_queue_screen.py:261` |
| (d) Wrong header | Hardcoded `"Build Yard"` singular | `build_queue_screen.py:461` |
| (e) Queue click no update | `handle_mouse_up()` returns index but never calls `refresh_design_report()` | `build_queue_screen.py:1098` |
| (f) No design identity | No UILabels for name/type/class in report panel | `design_report_panel.py` |
| (g) Always 1 turn | `_calculate_build_turns()` uses `design.resource_cost` which is `{}` (see b), so `max_cost=0` -> returns 1 | `build_queue_controller.py:186` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Manual verification of all 7 issues resolved
- [ ] User verified
