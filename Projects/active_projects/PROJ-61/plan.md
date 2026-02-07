# PROJ-61: Workshop Screen Breakdown

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Extract Ship I/O Handler | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Push Dropdown Logic into Right Panel | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract Data Reload Orchestration | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Final Cleanup & Verification | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** Phase 2
**Next Action:** Execute Phase 2 - Push dropdown logic into right_panel
**Test Baseline:** 6246 passed, 0 failed
**Line Count:** 759 lines (was 943)

## Overview
Reduce `workshop_screen.py` from 943 lines to under 500 by extracting Ship I/O orchestration, pushing dropdown manipulation into the right panel, and extracting data reload UI coordination.

## Scope
**In:** Ship I/O extraction (~175 lines), dropdown logic to right_panel (~60 lines), data reload UI coordination (~65 lines), dead code removal (~35 lines)
**Out:** draw/update (orchestrators), properties (thin proxies), _create_ui (delegates already), missing handle_resize bug

## Key Files
| Component | File Path |
|-----------|-----------|
| Workshop Screen (target) | `game/ui/screens/workshop_screen.py` |
| Event Router | `game/ui/screens/workshop_event_router.py` |
| Right Panel | `game/ui/screens/builder/right_panel.py` |
| Ship I/O Handler | `game/ui/screens/workshop_ship_io.py` |

## Decisions Log
| Decision | Rationale |
|----------|-----------|
| Keep draw/update in main class | Touch 10+ subsystems |
| Extract Ship I/O as composition class | Follows EventRouter pattern |
| Push dropdowns to right_panel | Already has refresh_controls() |
| Use lambda for weapons_report_panel_ref | Allows deferred access during tests |

## Verification
- [x] Baseline: 6246 passed
- [x] Phase 1: 759 lines, all tests pass
- [ ] Final: under 500 lines, all tests pass
