# PROJ-129: legacy-system-cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-129` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-129 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simulation | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Strategy | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI-Framework | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-13
**Active Phase:** Phase 3
**Last Action:** Phase 2 complete - all 3 findings ACCEPTABLE (no code changes needed)
**Next Action:** Begin Phase 3 Strategy tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-13_sweep_full-codebase-sweep. Total findings selected: 20 (Critical: 0, Major: 3, Other: 17).

## Goals
- Address LEG-STR-001: Legacy Behavior Branch in FleetOrderProc
- Address LEG-STR-002: Backward Compatibility Comment in GameSe
- Address LEG-STR-003: Legacy Items in ProductionEngine
- Address LEG-FND-003: Raw Ship vs Adapter Access Pattern in Fo
- Address LEG-FND-004: Singleton Pattern Still in Use Despite D
- Address LEG-FND-005: Unused AI_STATE_ERROR ErrorCode
- Address LEG-SIM-006: Module Identity Drift Fallback in Abilit
- Address LEG-SIM-007: Component Ability Index Fallback Pattern
- Address LEG-STR-004: Backward Compatibility Comment in FleetN
- Address LEG-STR-005: Backward Compat Default in Planet.from_d
- ...and 10 more findings

## Scope
**In:**
- Unknown
- game/ai/behaviors.py
- game/core/error_codes.py
- game/simulation/components/abi
- game/simulation/components/com
- game/simulation/systems/tech_p
- game/strategy/data/design_meta
- game/strategy/data/pathfinding
- game/strategy/data/planet.py
- game/strategy/data/race_config
- game/strategy/engine/fleet_ord
- game/strategy/engine/game_sess
- game/strategy/engine/productio
- game/strategy/services/fleet_n
- game/ui/assets/ship_theme_mana
- ...and 3 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `Unknown` |
| [TBD] | `game/ai/behaviors.py` |
| [TBD] | `game/core/error_codes.py` |
| [TBD] | `game/simulation/components/abi` |
| [TBD] | `game/simulation/components/com` |
| [TBD] | `game/simulation/systems/tech_p` |
| [TBD] | `game/strategy/data/design_meta` |
| [TBD] | `game/strategy/data/pathfinding` |
| [TBD] | `game/strategy/data/planet.py` |
| [TBD] | `game/strategy/data/race_config` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
