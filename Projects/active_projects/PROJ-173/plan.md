# PROJ-173: God Class Decomposition - Domain & Strategy Layer

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-173` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-173 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. FleetReportWindow Completion | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Galaxy Internal Delegation | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. StrategyInputHandler Router Decomposition | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. StrategyScreen Minimal Extraction | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 3 Complete
**Last Action:** Extracted 3 sub-routers from StrategyInputHandler (fleet_command, click_dispatch, ui_action)
**Next Action:** Phase 4 - StrategyScreen Minimal Extraction
**Blockers:** None
**Test Baseline:** 12,312 passed, 1 skipped, 0 failures

### Phase 3 Results
- StrategyInputHandler: 898 → 193 lines (78% reduction)
- New: strategy_fleet_command_router.py (198 lines) - fleet commands, superweapons, detail panel
- New: strategy_click_dispatcher.py (564 lines) - click mode handling, picking, hit testing
- New: strategy_ui_action_router.py (115 lines) - zoom, screenshots, UI panel actions
- All 12,312 tests passing

### Phase 1 Results
- FleetReportWindow: 1,109 → 359 lines (68% reduction)
- New: FleetReportSidebar (554 lines) - sidebar widgets, filters, columns, summary
- New: FleetListRenderer (425 lines) - virtual scrolling, headers, row pool, images

### Phase 2 Results
- Galaxy: 928 → 585 lines (37% reduction, includes WarpPoint+StarSystem classes)
- New: galaxy_warp_generator.py (370 lines) - MST, density edges, angle validation
- New: galaxy_system_generator.py (142 lines) - system placement, planet generation
- New: galaxy_entity_registry.py (160 lines) - planet/fleet/zone lifecycle
- New: galaxy_spatial_index.py (190 lines) - spatial queries, object location
- All 12,312 tests passing

## Overview
Decompose the remaining god classes identified in the tech debt review (2026-02-23) that were not covered by PROJ-172 (UI screens). This project handles domain/strategy layer files: FleetReportWindow (finish MVVM), Galaxy (internal delegation), StrategyInputHandler (router decomposition), and StrategyScreen (minimal extraction).

## Goals
- Reduce FleetReportWindow from 1,108 to <500 lines by completing the MVVM extraction
- Reduce Galaxy from 928 to <400 lines via internal delegation (facade preserved)
- Reduce StrategyInputHandler from 898 to <250 lines via router decomposition
- Optionally reduce StrategyScreen from 823 to ~530 lines via manager extraction
- Zero external API changes — all decompositions preserve public interfaces
- All 12,023+ tests continue to pass

## Scope
**In:**
- FleetReportWindow (1,108 lines) — finish MVVM with sidebar + renderer extraction
- Galaxy (928 lines) — internal delegation to WarpLaneGenerator, SpatialIndex, PlanetRegistry
- StrategyInputHandler (898 lines) — extract 4 sub-routers
- StrategyScreen (823 lines) — extract BuildQueueManager + GameStateManager (optional)

**Out:**
- Ship (810 lines) — ACCEPT verdict, cohesive entity
- Component (723 lines) — ACCEPT verdict, already delegated
- app.py (705 lines) — ACCEPT verdict, composition root
- BattleController (659 lines) — ACCEPT verdict, well-delegated
- StrategyRenderer (764 lines) — ACCEPT verdict, focused renderer
- RaceSetupScreen (946 lines) — ACCEPT verdict, already 8 panels
- CI guardrails and line count tooling (separate effort)

## Key Files
| Component | File Path | Lines | Target |
|-----------|-----------|-------|--------|
| FleetReportWindow | `game/ui/screens/fleet_report_window.py` | 1,108 | <500 |
| FleetListViewModel | `game/ui/screens/fleet_report_view_model.py` | 280 | (existing) |
| ColumnManager | `game/ui/screens/column_manager.py` | 234 | (existing) |
| Galaxy | `game/strategy/data/galaxy.py` | 928 | <400 |
| StrategyInputHandler | `game/ui/screens/strategy_input_handler.py` | 898 | <250 |
| StrategyScreen | `game/ui/screens/strategy_screen.py` | 823 | ~530 |

## Decomposition Patterns Used
| File | Pattern | Reference |
|------|---------|-----------|
| FleetReportWindow | MVVM (finish existing) | FleetListViewModel, WorkshopViewModel |
| Galaxy | Facade/Internal Delegation | Fleet (833→413), GameSession (834→357) |
| StrategyInputHandler | Router Composition | FormationInputHandler |
| StrategyScreen | Manager Extraction | StrategyScreen existing delegates |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- Prior review: `Reviews/results/2026-02-23_182728_tech-debt_god-class-decomposition-planning/report.md`

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (12,023+)
- [ ] Audit passed
- [ ] User verified
