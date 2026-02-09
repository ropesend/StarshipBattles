# PROJ-80: Unify Design Details Panel

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-80` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-80 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create DesignStatsPanel + Move StatRow | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Integrate into BuilderRightPanel | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Integrate into DesignReportPanel + Widen Build Queue | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Update Tests + Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-08 17:36
**Active Phase:** Planning
**Last Action:** Project created, plan finalized
**Next Action:** Begin Phase 1 - create DesignStatsPanel
**Blockers:** None

## Overview
The Design Workshop and Build Queue screens each have their own implementation of a "Design Details" stats panel. The workshop's `BuilderRightPanel` uses a two-column layout at 750px wide, while the Build Queue's `DesignReportPanel` uses a single-column layout at 400px. They display similar stat sections with divergent code. This project extracts a shared `DesignStatsPanel` widget that both screens embed, with the workshop's two-column layout as the canonical form, and widens the Build Queue panel to 750px.

## Goals
- Single shared code path for ship stats display in both Design Workshop and Build Queue
- Two-column layout is the canonical form (matching Design Workshop)
- Build Queue panel widens to 750px (narrower queue list is acceptable)
- Build Queue panel omits Requirements/Recommendations sections
- Both panels show identical stat sections

## Scope
**In:**
- Extract stats layout/update logic into shared `DesignStatsPanel`
- Move `StatRow` to the new shared module
- Refactor `BuilderRightPanel` to delegate stats to `DesignStatsPanel`
- Refactor `DesignReportPanel` to embed `DesignStatsPanel`
- Widen Build Queue design report panel to 750px
- Update tests for new import paths and dimensions

**Out:**
- Portrait rendering (fundamentally different between workshop and build queue)
- Workshop controls (name, type, class, AI dropdowns)
- `ShipDetailPanel` (doesn't use DesignReportPanel's stats code)
- `stats_config.py` changes (data layer already shared)

## Key Files
| Component | File Path |
|-----------|-----------|
| New shared widget | `game/ui/panels/design_stats_panel.py` |
| Workshop right panel | `game/ui/screens/builder/right_panel.py` |
| Build queue report panel | `game/ui/panels/design_report_panel.py` |
| Build queue screen | `game/ui/screens/build_queue_screen.py` |
| Stats config (unchanged) | `game/ui/screens/builder/stats_config.py` |
| Layout constants | `game/ui/screens/builder_utils.py` |
| Build queue controller | `game/ui/panels/build_queue_controller.py` |
| Stats render test | `tests/unit/ui/test_stats_render.py` |
| Design report test | `tests/integration/ui/test_build_queue_design_report.py` |
| Build queue format test | `tests/integration/ui/test_build_queue_formatting.py` |
| Bug repro test | `tests/repro_issues/test_bug_04_display.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`, baseline 6246)
- [ ] Design Workshop shows two-column stats with Requirements/Recommendations
- [ ] Build Queue shows two-column stats WITHOUT Requirements/Recommendations
- [ ] Both panels show identical stat sections
- [ ] Build Queue design report is 750px wide
- [ ] Audit passed
- [ ] User verified
