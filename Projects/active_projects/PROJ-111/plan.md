# PROJ-111: Test Coverage - UI and Framework

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-111` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-111 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. UI Framework Services | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Framework Complex (Singletons & Rendering) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Battle Layer (Screens & Panels) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Strategy Core Screens | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Strategy Support Screens | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Workshop, Setup, and Complex Screens | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Test Quality Improvements | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-02-11
**Active Phase:** Phase 2 Complete - Ready for Phase 3
**Last Action:** Phase 2 complete - added +50 new tests for framework complex (SpriteManager singleton/error/threading, ShipThemeManager singleton/caching/errors/threading, GameRenderer draw_ship/draw_hud/layers)
**Next Action:** Begin Phase 3 (Battle Layer - BattleScreen, battle panels)
**Blockers:** None

## Overview
Address test coverage gaps in the UI layer: UI-Framework (game/ui/ root + services/renderer/assets/interfaces/orchestration) and UI-Screens (game/ui/screens/ + game/ui/panels/). The 2026-02-10 sweep identified 59 test coverage findings, including 11 CRITICAL (completely untested core screens) and 23 MAJOR gaps. Expected impact: +500-700 new tests.

## Goals
- Create unit test suites for untested core screens (BattleScreen, StrategyScreen, etc.)
- Add error path and edge case tests for UI services
- Test critical rendering pipeline functions
- Verify DTO conversion and state management correctness
- Improve assertion quality in existing weak tests

## Scope
**In:**
- UI-Framework findings: TCG-UI2-001 through TCG-UI2-012
- UI-Screens findings: TCG-UI1-001 through TCG-UI1-024
- Test quality improvements: TCG-UI1-020 through TCG-UI1-024

**Out:**
- Core system test coverage (PROJ-110)
- Visual regression testing (separate effort)
- Full integration test suites (slow, separate project)
- INFO-level organizational findings (TCG-UI1-025 through TCG-UI1-029)

## Phase Summary

| Phase | Findings | Est. Tests | Complexity |
|-------|----------|------------|------------|
| 1. Framework Services | TCG-UI2-004 to TCG-UI2-012 | 120-150 | Simple-Medium |
| 2. Framework Complex | TCG-UI2-001 to TCG-UI2-003 | 80-100 | Complex |
| 3. Battle Layer | TCG-UI1-001, 008, 009, 010 | 100-130 | Medium-Complex |
| 4. Strategy Core | TCG-UI1-002, 011, 012 | 80-100 | Medium-Complex |
| 5. Strategy Support | TCG-UI1-013 to 016 | 80-100 | Medium |
| 6. Workshop & Setup | TCG-UI1-003 to 007, 017-019 | 100-140 | Complex |
| 7. Quality | TCG-UI1-020 to 024 | 40-60 | Simple-Medium |
| **Total** | **47 findings** | **600-780** | |

## Key Files
| Component | File Path |
|-----------|-----------|
| Game renderer | `game/ui/renderer/game_renderer.py` |
| Sprites | `game/ui/renderer/sprites.py` |
| Theme manager | `game/ui/assets/ship_theme_manager.py` |
| Camera | `game/ui/renderer/camera.py` |
| BattleUIService | `game/ui/services/battle_ui_service.py` |
| BattleScreen | `game/ui/screens/battle_screen.py` |
| StrategyScreen | `game/ui/screens/strategy_screen.py` |
| BuildQueueScreen | `game/ui/screens/build_queue_screen.py` |
| FleetReportWindow | `game/ui/screens/fleet_report_window.py` |
| Battle panels | `game/ui/panels/battle_panels.py` |
| WorkshopScreen | `game/ui/screens/workshop_screen.py` |
| RaceSetupScreen | `game/ui/screens/race_setup_screen.py` |
| FormationEditor | `game/ui/screens/formation_editor.py` |
| StrategyRenderer | `game/ui/screens/strategy_renderer.py` |
| StrategyInputHandler | `game/ui/screens/strategy_input_handler.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis, test patterns, and design rationale
- [decisions.md](decisions.md) - Full decisions log
- **Source sweep:** `Reviews/results/2026-02-10_sweep_full-codebase-sweep/findings/test_coverage_{ui_framework,ui_screens}_report.md`

## Verification
- [ ] All phase checklists complete
- [ ] All new tests passing
- [ ] Coverage improved for all targeted screens/panels
- [ ] Audit passed
- [ ] User verified
