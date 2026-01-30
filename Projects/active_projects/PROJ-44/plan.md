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
| 2. Registry & Service Extraction | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Ship Helper Methods | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Component Decomposition | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. ShipCombatEngine Decomposition | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. BattleController Mode Handlers | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. UI God Class Decomposition | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Long Method Refactoring | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Minor Cleanup | Not Started | [phase_9_checklist.md](phase_9_checklist.md) |

## Current State
**Last Updated:** 2026-01-30
**Active Phase:** Phase 7 - UI God Class Decomposition (in progress)
**Last Action:** Phase 7 Task 7.3 complete - Extracted BuilderStateManager
**Next Action:** Continue Phase 7 - Task 7.4 (FleetReportWindow)
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
| Component (refactored) | `game/simulation/components/component.py` | 665 |
| Ship (god class) | `game/simulation/entities/ship.py` | 834 |
| ShipCombatEngine (refactored) | `game/simulation/entities/ship_combat_engine.py` | 217 |
| TargetingSystem (new) | `game/simulation/combat/targeting_system.py` | 198 |
| DamageCalculator (new) | `game/simulation/combat/damage_calculator.py` | 99 |
| WeaponFiringSystem (new) | `game/simulation/combat/weapon_firing_system.py` | 221 |
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
