# PROJ-144: 4_legacy_code_cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-144` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-144 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simulation | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Strategy | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI-Framework | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-14
**Active Phase:** Phase 3
**Last Action:** Phase 2 complete - 4/5 tasks INTENTIONAL DESIGN, 1 task removed dead fallback code
**Next Action:** Begin Phase 3 Strategy tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-13_223809_sweep_full-codebase-sweep. Total findings selected: 24 (Critical: 0, Major: 12, Other: 12).

## Goals
- Address ADR-UI2-002: ShipIO module-level Tkinter initializati
- Address CON-UI2-005: Module-Level Side Effects in ship_io.py
- Address LEG-FND-001: Excessive getattr() Fallbacks in AI Comb
- Address LEG-SIM-001: Module Identity Drift Fallback in Abilit
- Address LEG-SIM-002: Singleton Pattern in Component Cache Man
- Address LEG-SIM-003: Dead Fallback Code in BattleController._
- Address LEG-STR-001: Backward Compatibility Fallback in GameS
- Address LEG-STR-002: Legacy Behavior Comments in FleetOrderPr
- Address LEG-STR-003: Backward Compatibility Default in Planet
- Address LEG-STR-004: Backward Compatibility in FleetNavigatio
- ...and 14 more findings

## Scope
**In:**
- Unknown
- game/ai/__init__.py
- game/ai/combat_utils.py
- game/ai/interfaces/controllabl
- game/core/error_codes.py
- game/simulation/battle_control
- game/simulation/components/abi
- game/simulation/components/com
- game/strategy/data/design_meta
- game/strategy/data/galaxy.py
- game/strategy/data/planet.py
- game/strategy/engine/fleet_ord
- game/strategy/engine/game_conf
- game/strategy/engine/game_sess
- game/strategy/engine/productio
- ...and 4 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `Unknown` |
| [TBD] | `game/ai/__init__.py` |
| [TBD] | `game/ai/combat_utils.py` |
| [TBD] | `game/ai/interfaces/controllabl` |
| [TBD] | `game/core/error_codes.py` |
| [TBD] | `game/simulation/battle_control` |
| [TBD] | `game/simulation/components/abi` |
| [TBD] | `game/simulation/components/com` |
| [TBD] | `game/strategy/data/design_meta` |
| [TBD] | `game/strategy/data/galaxy.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
