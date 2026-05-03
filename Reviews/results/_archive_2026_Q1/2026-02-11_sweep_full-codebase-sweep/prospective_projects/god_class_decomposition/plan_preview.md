# PROJ-XX: God Class Decomposition

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-XX` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-XX [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Simulation God Classes | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Strategy God Classes | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI Screen God Classes | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-11
**Active Phase:** Planning
**Last Action:** Project created from sweep findings
**Next Action:** Evaluate overlap with PROJ-86 through PROJ-89 before starting
**Blockers:** Potential full overlap with existing god class decomposition projects

## Overview
Decompose 15 god classes (353-1877 lines each) across simulation, strategy, and UI layers using the facade/delegate extraction pattern. Each god class is split into focused delegate classes while the original class remains as a thin public API facade. This project heavily overlaps with the existing PROJ-86 through PROJ-89 decomposition series.

## Goals
- Reduce all identified god classes to under 400 lines each
- Extract cohesive responsibility groups into dedicated delegate classes
- Maintain backward-compatible public APIs via facade pattern
- Achieve testability for extracted delegate classes
- Coordinate with or supersede existing PROJ-86 through PROJ-89

## Scope
**In:**
- 15 god classes in simulation, strategy, and UI layers
- 4 oversized file observations (Info severity)
- Facade/delegate extraction for each class

**Out:**
- Layer violation fixes (separate project)
- Legacy dead code removal (separate project)
- New feature development beyond decomposition

## Key Files
| Component | File Path |
|-----------|-----------|
| BattleController (848 lines) | `game/simulation/battle_controller.py` |
| Ship (809 lines) | `game/simulation/entities/ship.py` |
| Component (719 lines) | `game/simulation/components/component.py` |
| ProductionEngine (701 lines) | `game/strategy/engine/production_engine.py` |
| Galaxy (698 lines) | `game/strategy/data/galaxy.py` |
| ShipInstance (658 lines) | `game/strategy/data/ship_instance.py` |
| Fleet (353 lines) | `game/strategy/data/fleet.py` |
| TestLabScreen (1877 lines) | `game/ui/screens/test_lab/screen.py` |
| StrategyScreen (768 lines) | `game/ui/screens/strategy_screen.py` |
| BuilderScreen (1042 lines) | `game/ui/screens/builder/main.py` |
| BattleScreen (621 lines) | `game/ui/screens/battle_screen.py` |
| FleetReportWindow (1075 lines) | `game/ui/screens/fleet_report_window.py` |
| BuildQueueScreen (1057 lines) | `game/ui/screens/build_queue_screen.py` |
| EmpireBuildQueueWindow (791 lines) | `game/ui/screens/empire_build_queue_window.py` |
| FormationEditorScreen (701 lines) | `game/ui/screens/formation_editor_screen.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] No class exceeds 400 lines (target)
- [ ] All extracted delegates have unit tests
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
