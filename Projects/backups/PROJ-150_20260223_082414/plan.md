# PROJ-150: legacy_cleanup_ui

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-150` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-150 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simulation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI-Framework | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI-Screens | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-14 04:04
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-14_031258_sweep_full-codebase-sweep. Total findings selected: 27 (Critical: 0, Major: 9, Other: 18).

## Goals
- Address LEG-UI2-001: BattleOrchestrator is Defined but Never
- Address LEG-FND-002: Singleton Pattern Pervasive Despite DI P
- Address LEG-FND-003: Defensive getattr Fallbacks in AI Module
- Address LEG-SIM-002: Unused BattleConfig.isolated Field
- Address LEG-SIM-003: Unused validate_state Method in BattleSt
- Address LEG-UI2-002: Defensive getattr Checks for Attributes
- Address LEG-UI2-003: VehicleClassService Methods Appear Unuse
- Address LEG-UI1-001: Legacy Single-Selection Fields Maintaine
- Address LEG-UI1-003: Fallback Pattern to Direct scene.ships A
- Address LEG-FND-001: Unused Error Codes in error_codes.py
- ...and 17 more findings

## Scope
**In:**
- Unknown
- game/ai/__init__.py
- game/ai/combat_utils.py
- game/ai/controller.py
- game/core/error_codes.py
- game/core/profiling.py
- game/core/protocols.py
- game/core/singleton.py
- game/simulation/battle_config.
- game/simulation/components/abi
- game/simulation/components/com
- game/simulation/managers/battl
- game/simulation/physics_consta
- game/ui/orchestration/battle_o
- game/ui/panels/battle_panels.p
- ...and 9 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `Unknown` |
| [TBD] | `game/ai/__init__.py` |
| [TBD] | `game/ai/combat_utils.py` |
| [TBD] | `game/ai/controller.py` |
| [TBD] | `game/core/error_codes.py` |
| [TBD] | `game/core/profiling.py` |
| [TBD] | `game/core/protocols.py` |
| [TBD] | `game/core/singleton.py` |
| [TBD] | `game/simulation/battle_config.` |
| [TBD] | `game/simulation/components/abi` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
