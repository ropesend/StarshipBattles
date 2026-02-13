# PROJ-126: architecture-layer-fixes

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-126` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-126 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simulation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI-Framework | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI-Screens | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-13 06:11
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-13_sweep_full-codebase-sweep. Total findings selected: 29 (Critical: 3, Major: 13, Other: 13).

## Goals
- Address ADR-SIM-001: AI Layer Imports in Simulation Factory
- Address ADR-UI1-001: Test Framework Coupling in Production UI
- Address ADR-UI1-002: Test Framework Import in Battle Screen
- Address ADR-SIM-002: TYPE_CHECKING Import of AI Controller
- Address ADR-SIM-003: God Class - BattleController
- Address ADR-SIM-004: God Class - Ship Entity
- Address ADR-SIM-005: Documented Circular Import in Ship.add_c
- Address ADR-UI2-002: God Class Potential in ShipThemeManager
- Address ADR-UI1-003: God Class - TestLabScreen (1908 lines, 7
- Address ADR-UI1-004: God Class - StrategyScreen (811 lines, 4
- ...and 19 more findings

## Scope
**In:**
- Unknown
- game/ai/behaviors.py
- game/simulation/battle_control
- game/simulation/entities/ship.
- game/simulation/entities/ship_
- game/simulation/factories/ai_f
- game/simulation/systems/battle
- game/ui/assets/ship_theme_mana
- game/ui/orchestration/battle_o
- game/ui/screens/battle_screen.
- game/ui/screens/build_queue_sc
- game/ui/screens/builder/main.p
- game/ui/screens/column_manager
- game/ui/screens/keybindings_sc
- game/ui/screens/planet_list_fi
- ...and 9 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `Unknown` |
| [TBD] | `game/ai/behaviors.py` |
| [TBD] | `game/simulation/battle_control` |
| [TBD] | `game/simulation/entities/ship.` |
| [TBD] | `game/simulation/entities/ship_` |
| [TBD] | `game/simulation/factories/ai_f` |
| [TBD] | `game/simulation/systems/battle` |
| [TBD] | `game/ui/assets/ship_theme_mana` |
| [TBD] | `game/ui/orchestration/battle_o` |
| [TBD] | `game/ui/screens/battle_screen.` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
