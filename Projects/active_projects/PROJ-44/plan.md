# PROJ-44: Code Quality & God Classes Refactoring

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-44` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-44 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Quick Wins (DRY, Magic Numbers) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Registry & Service Extraction | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Ship Helper Methods | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Component Decomposition | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. ShipCombatEngine Decomposition | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. BattleController Mode Handlers | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. UI God Class Decomposition | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Long Method Refactoring | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Minor Cleanup | Not Started | [phase_9_checklist.md](phase_9_checklist.md) |

## Current State
**Last Updated:** 2026-01-29
**Active Phase:** Phase 2 - Registry & Service Extraction
**Last Action:** Phase 1 complete - DRY violations fixed, SimulationConstants created, damage threshold unified
**Next Action:** Begin Phase 2, Task 2.1 - see phase_2_checklist.md
**Blockers:** None

## Overview
A comprehensive refactoring project to address 35+ code quality issues including 8 god classes (1000+ LOC files), DRY violations, SOLID violations, magic numbers, and code smells. Uses a **risk-based approach** - tackling the most tightly-coupled code first to reduce cascading changes.

## Goals
- Break down god classes into focused, testable components
- Extract duplicate code into reusable utilities
- Centralize magic numbers into constants
- Fix SOLID violations and reduce cross-layer coupling
- Unify damage threshold model (50% everywhere)

## Scope
**In:**
- All 35 issues from `findings_02_code_quality_god_classes.md`
- God classes: Component, Ship, ShipCombatEngine, BattleController, RaceSetupScreen, FormationEditor, BuilderSceneGUI, FleetReportWindow
- DRY violations, magic numbers, SOLID violations

**Out:**
- New features or gameplay changes
- Performance optimization beyond scope of refactoring
- UI redesign (only structural refactoring)

## Key Files
| Component | File Path | LOC |
|-----------|-----------|-----|
| Component (god class) | `game/simulation/components/component.py` | 878 |
| Ship (god class) | `game/simulation/entities/ship.py` | 834 |
| ShipCombatEngine | `game/simulation/entities/ship_combat_engine.py` | 655 |
| BattleController | `game/simulation/battle_controller.py` | 889 |
| BuilderSceneGUI | `game/ui/screens/builder/main.py` | 1100 |
| RaceSetupScreen | `game/ui/screens/race_setup_screen.py` | 1231 |
| FormationEditor | `game/ui/screens/formation_editor.py` | 1103 |
| FleetReportWindow | `game/ui/screens/fleet_report_window.py` | 1034 |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [Full plan details](C:\Users\rossr\.claude\plans\cheerful-spinning-candy.md) - Detailed task breakdown

## Test Baseline
- **Date:** 2026-01-29 (Phase 1 complete)
- **Tests:** 5398 passed, 3 skipped
- **Warnings:** 213 (reduced from 28291 after PROJ-42 completion)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
