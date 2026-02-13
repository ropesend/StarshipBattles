# PROJ-117: Legacy Dead Code Eradication

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-117` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-117 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simulation | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI-Framework | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI-Screens | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-12
**Active Phase:** Audit
**Last Action:** Phase 4 Complete - 16 UI-Screens findings (5 fixed, 5 false positives, 6 acceptable)
**Next Action:** Run project audit per Protocol 04
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-11_sweep_full-codebase-sweep. Total findings selected: 65 (Critical: 6, Major: 24, Other: 35).

## Goals
- Address LEG-FND-001: Backward Compatibility Wrapper `load_res
- Address LEG-SIM-001: Empty ABILITY_CLASS_MAP dict still impor
- Address LEG-SIM-007: resource_manager.py re-exports ability c
- Address LEG-SIM-008: component.py uses get_default_registry_p
- Address LEG-UI2-001: Legacy widgets.py Module - Entire File i
- Address LEG-UI1-001: Legacy BuilderScreen (builder/main.py) -
- Address LEG-FND-002: StrategyMetadataService Uses Hand-Rolled
- Address LEG-FND-003: Dead Instance Attributes `attack_state`
- Address LEG-FND-004: Duplicate Path Resolution Logic in resou
- Address LEG-FND-005: Unused Protocol Classes and TypeGuard Fu
- ...and 55 more findings

## Scope
**In:**
- Unknown
- game/ai/controller.py
- game/core/constants.py
- game/core/profiling.py
- game/core/protocols.py
- game/core/resources.py
- game/core/screenshot_manager.p
- game/core/strategy_metadata.py
- game/simulation/battle_control
- game/simulation/components/abi
- game/simulation/components/com
- game/simulation/components/mod
- game/simulation/designs.py
- game/simulation/entities/abili
- game/simulation/entities/comba
- ...and 28 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `Unknown` |
| [TBD] | `game/ai/controller.py` |
| [TBD] | `game/core/constants.py` |
| [TBD] | `game/core/profiling.py` |
| [TBD] | `game/core/protocols.py` |
| [TBD] | `game/core/resources.py` |
| [TBD] | `game/core/screenshot_manager.p` |
| [TBD] | `game/core/strategy_metadata.py` |
| [TBD] | `game/simulation/battle_control` |
| [TBD] | `game/simulation/components/abi` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
