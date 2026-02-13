# PROJ-116: God Class Decomposition

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-116` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-116 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Simulation | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Strategy | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI-Screens | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-12 18:39
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-11_sweep_full-codebase-sweep. Total findings selected: 19 (Critical: 0, Major: 15, Other: 4).

## Goals
- Address ADR-SIM-005: God class - battle_controller.py (848 li
- Address ADR-SIM-006: God class - ship.py (809 lines)
- Address ADR-SIM-007: God class - component.py (719 lines)
- Address ADR-STR-003: ProductionEngine God Class (701 lines, 1
- Address ADR-STR-004: Galaxy God Class (698 lines, 26 methods)
- Address ADR-STR-005: ShipInstance God Class (658 lines, 44 me
- Address ADR-STR-006: Fleet God Class (353 lines, 41 methods)
- Address ADR-UI1-003: TestLabScreen God Class (1877 lines, 75
- Address ADR-UI1-004: BuilderScreen God Class (1042 lines, 44
- Address ADR-UI1-005: FormationEditorScreen God Class (701 lin
- ...and 9 more findings

## Scope
**In:**
- game/simulation/battle_control
- game/simulation/components/com
- game/simulation/entities/ship.
- game/strategy/data/fleet.py
- game/strategy/data/galaxy.py
- game/strategy/data/ship_instan
- game/strategy/engine/productio
- game/ui/panels/race_summary_pa
- game/ui/screens/battle_screen.
- game/ui/screens/build_queue_sc
- game/ui/screens/builder/main.p
- game/ui/screens/builder/weapon
- game/ui/screens/empire_build_q
- game/ui/screens/fleet_report_w
- game/ui/screens/formation_edit
- ...and 4 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `game/simulation/battle_control` |
| [TBD] | `game/simulation/components/com` |
| [TBD] | `game/simulation/entities/ship.` |
| [TBD] | `game/strategy/data/fleet.py` |
| [TBD] | `game/strategy/data/galaxy.py` |
| [TBD] | `game/strategy/data/ship_instan` |
| [TBD] | `game/strategy/engine/productio` |
| [TBD] | `game/ui/panels/race_summary_pa` |
| [TBD] | `game/ui/screens/battle_screen.` |
| [TBD] | `game/ui/screens/build_queue_sc` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
