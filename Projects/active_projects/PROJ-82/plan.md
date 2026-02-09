# PROJ-82: Planet Resources Panel Redesign

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-82` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-82 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Remove Resources from Text & Add Resource Grid | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Tests & Polish | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-02-08 21:30
**Active Phase:** Planning (Awaiting Approval)
**Last Action:** Plan complete, awaiting user approval
**Next Action:** Begin Phase 1, Task 1.1 — Remove resource section from format_planet_info
**Blockers:** None

## Overview
The PlanetReportPanel currently displays resource information (quantity, quality) as inline text within the scrollable UITextBox. This project creates a dedicated, visually distinct resource grid panel at the bottom of the planet report, with resource icons as column headers and rows for quantity, quality, and production. This improves readability and gives resources the visual prominence they deserve.

## Goals
- Replace inline resource text with a structured resource grid panel at the bottom of the planet report
- Display resource icons from `assets/Images/Resource Portraits/` as column headers
- Show quantity, quality, and production rate per resource in dedicated rows
- Keep the scrollable info text focused on planet stats and colony info (no resources)

## Scope
**In:**
- New resource grid sub-panel in PlanetReportPanel
- Resource icon loading (reusing existing RESOURCE_PORTRAIT_FILES mapping)
- Production rates as an optional parameter (computed by caller)
- Removing resource info from format_planet_info()
- Updated and new tests

**Out:**
- Changes to HarvestingEngine or production logic
- Changes to Planet data model
- Changes to save/load system
- New resource icon artwork

## Key Files
| Component | File Path |
|-----------|-----------|
| Planet Report Panel | `game/ui/panels/planet_report_panel.py` |
| Detail Formatter | `game/ui/screens/strategy_detail_fmt.py` |
| Portrait Constants | `game/ui/panels/build_queue_portraits.py` |
| Strategy UI | `game/ui/screens/strategy_ui.py` |
| Resource Constants | `game/core/constants.py` |
| Planet Data | `game/strategy/data/planet.py` |
| Tests | `tests/integration/ui/test_build_queue_enhanced_planet_report.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Manual test: Colony planet shows production values, non-colony shows 0
- [ ] Manual test: Resource icons display correctly for all 5 resources
- [ ] Manual test: Switching planets updates grid correctly
- [ ] User verified
