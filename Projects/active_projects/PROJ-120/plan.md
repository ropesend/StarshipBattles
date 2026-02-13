# PROJ-120: PROJ-A_simulation-test-coverage

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-120` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-120 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Simulation | In Progress (16/18) | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-02-13 (Session 10)
**Active Phase:** Phase 1
**Last Action:** Completed Task 1.16 (14 new ProjectileManager batch update tests)
**Next Action:** Continue with Task 1.17 (Test Organization Inconsistency)
**Blockers:** None

## Overview
Systematic remediation of findings from review: 2026-02-13_sweep_full-codebase-sweep. Total findings selected: 18 (Critical: 3, Major: 7, Other: 8).

## Goals
- Address TCG-SIM-001: Projectile Entity Has No Unit Tests
- Address TCG-SIM-002: ShipStatQuerier Has No Unit Tests
- Address TCG-SIM-003: ShipValidator Rules Have No Unit Tests
- Address TCG-SIM-004: BattleController Missing Edge Case Tests
- Address TCG-SIM-005: DamageCalculator Armor Penetration Edge
- Address TCG-SIM-006: WeaponFiringSystem Missing Multishot Tes
- Address TCG-SIM-007: TargetingSystem Missing AI Priority Test
- Address TCG-SIM-008: BattleEngine Tick Processing Incomplete
- Address TCG-SIM-009: FormulaSystem Overflow/Underflow Not Tes
- Address TCG-SIM-010: Design System Serialization Roundtrip Ga
- ...and 8 more findings

## Scope
**In:**
- game/simulation/battle_control
- game/simulation/combat/damage_
- game/simulation/combat/targeti
- game/simulation/combat/weapon_
- game/simulation/components/abi
- game/simulation/designs.py
- game/simulation/entities/abili
- game/simulation/entities/proje
- game/simulation/entities/ship_
- game/simulation/formula_system
- game/simulation/projectile_man
- game/simulation/systems/battle
- game/simulation/validation/shi
- tests/integration/
- tests/unit/simulation/
- ...and 2 more files

**Out:**
- Other review findings not selected
- New feature development beyond remediation

## Key Files
| Component | File Path |
|-----------|-----------|
| [TBD] | `game/simulation/battle_control` |
| [TBD] | `game/simulation/combat/damage_` |
| [TBD] | `game/simulation/combat/targeti` |
| [TBD] | `game/simulation/combat/weapon_` |
| [TBD] | `game/simulation/components/abi` |
| [TBD] | `game/simulation/designs.py` |
| [TBD] | `game/simulation/entities/abili` |
| [TBD] | `game/simulation/entities/proje` |
| [TBD] | `game/simulation/entities/ship_` |
| [TBD] | `game/simulation/formula_system` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
