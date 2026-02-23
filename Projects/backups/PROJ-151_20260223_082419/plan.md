# PROJ-151: test_coverage_simulation_core

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-151` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-151 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Simulation | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-02-14 04:04
**Active Phase:** Phase 1
**Last Action:** Project created from review findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-14_031258_sweep_full-codebase-sweep. Total findings selected: 12 (Critical: 1, Major: 6, Other: 5).

## Goals
- Address TCG-SIM-002: No Tests for Propulsion Abilities
- Address TCG-SIM-001: No Direct Tests for Ship Entity Core Met
- Address TCG-SIM-003: ResourceConsumption and ResourceGenerati
- Address TCG-SIM-004: WeaponFiringSystem Tests Missing Edge Ca
- Address TCG-SIM-005: BattleEngine Missing Tick Processing Edg
- Address TCG-SIM-007: No Tests for BattleService Serialization
- Address TCG-SIM-008: No Tests for DesignLoader Error Recovery
- Address TCG-SIM-018: Superweapons Ability Tests Missing Activ
- Address TCG-SIM-010: ShipStatQuerier Not Directly Tested
- Address TCG-SIM-011: ShipValidatorHelper Not Directly Tested
- ...and 2 more findings

## Scope
**In:**
- game/simulation/battle_config.
- game/simulation/combat/weapon_
- game/simulation/components/abi
- game/simulation/entities/ship.
- game/simulation/entities/ship_
- game/simulation/physics_consta
- game/simulation/services/battl
- game/simulation/services/desig
- game/simulation/systems/battle

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `game/simulation/battle_config.` |
| [TBD] | `game/simulation/combat/weapon_` |
| [TBD] | `game/simulation/components/abi` |
| [TBD] | `game/simulation/entities/ship.` |
| [TBD] | `game/simulation/entities/ship_` |
| [TBD] | `game/simulation/physics_consta` |
| [TBD] | `game/simulation/services/battl` |
| [TBD] | `game/simulation/services/desig` |
| [TBD] | `game/simulation/systems/battle` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
