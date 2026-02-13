# PROJ-122: PROJ-C_ui-god-class-decomposition

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-122` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-122 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Simulation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Strategy | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI-Framework | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI-Screens | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Other | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-13
**Active Phase:** Phase 5
**Last Action:** Phase 4 complete - 17 findings analyzed, 6 fixed (private->public methods), 11 FALSE POSITIVES (already decomposed, intentional patterns)
**Next Action:** Begin Phase 5 tasks (Other module)
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-13_sweep_full-codebase-sweep. Total findings selected: 23 (Critical: 2, Major: 13, Other: 8).

## Goals
- Address ADR-UI1-001: Test Framework Coupling in Production UI
- Address ADR-UI1-002: Test Framework Import in Battle Screen
- Address ADR-SIM-003: God Class - BattleController
- Address ADR-SIM-004: God Class - Ship Entity
- Address ADR-STR-003: Galaxy Class Approaching God Class Statu
- Address ADR-UI2-002: God Class Potential in ShipThemeManager
- Address ADR-UI1-003: God Class - TestLabScreen (1908 lines, 7
- Address ADR-UI1-004: God Class - StrategyScreen (811 lines, 4
- Address ADR-UI1-005: God Class - BuilderMain (1121 lines, 44
- Address ADR-UI1-006: God Class - BuildQueueScreen (1098 lines
- ...and 13 more findings

## Scope
**In:**
- Unknown
- game/simulation/battle_control
- game/simulation/entities/ship.
- game/strategy/data/galaxy.py
- game/ui/assets/ship_theme_mana
- game/ui/screens/battle_screen.
- game/ui/screens/build_queue_sc
- game/ui/screens/builder/main.p
- game/ui/screens/column_manager
- game/ui/screens/keybindings_sc
- game/ui/screens/planet_list_fi
- game/ui/screens/strategy_event
- game/ui/screens/strategy_rende
- game/ui/screens/strategy_scree
- game/ui/screens/strategy_ui.py
- ...and 4 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `Unknown` |
| [TBD] | `game/simulation/battle_control` |
| [TBD] | `game/simulation/entities/ship.` |
| [TBD] | `game/strategy/data/galaxy.py` |
| [TBD] | `game/ui/assets/ship_theme_mana` |
| [TBD] | `game/ui/screens/battle_screen.` |
| [TBD] | `game/ui/screens/build_queue_sc` |
| [TBD] | `game/ui/screens/builder/main.p` |
| [TBD] | `game/ui/screens/column_manager` |
| [TBD] | `game/ui/screens/keybindings_sc` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
