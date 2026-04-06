# PROJ-249: PDC Targeting Configuration

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-249` to see what to do next
> - Open the phase checklist file for your current phase

## Overview
PDC weapons can only target missiles and fighters via hardcoded string checks in targeting_system.py (lines 163-173). Adding new targetable entity types requires editing the targeting system directly. The fix: add `pdc_valid_targets` to BeamWeaponAbility, defaulting to `["MISSILE", "FIGHTER"]` for backward compat.

## Goals
- PDC valid target types configurable via component data JSON
- Existing behavior preserved as default
- New target types addable without code changes

## Scope
**In Scope:**
- Add `pdc_valid_targets` field to BeamWeaponAbility
- Read from component JSON if present, default to `["MISSILE", "FIGHTER"]`
- Replace hardcoded checks in targeting_system.py with data-driven lookup
- Update PDC tests

**Out of Scope:**
- Adding new target types (this just enables them)
- Changing PDC damage/accuracy mechanics
- Seeker weapon targeting (separate system)

## Current State
**Last Updated:** 2026-04-06 23:55
**Current Phase:** Planning Complete
**Next Action:** Implementation via Continue Project prompt
**Blockers:** None
**Context for Next Agent:** The hardcoded targeting is at lines 163-173 of targeting_system.py. It checks `candidate.type == AttackType.MISSILE` and `getattr(candidate, 'vehicle_type', '') == 'Fighter'`. Replace with a lookup against the weapon ability's pdc_valid_targets list.

## Key Files Reference
| Component | File Path | Line(s) |
|-----------|-----------|---------|
| Hardcoded PDC targeting | `game/simulation/combat/targeting_system.py` | 163-173 |
| BeamWeaponAbility class | `game/simulation/components/abilities/weapons.py` | ~60-160 |
| PDC tests | `tests/unit/simulation/combat/test_targeting_system.py` | 864-956 |
| Simulation PDC tests | `simulation_tests/scenarios/seeker_scenarios.py` | SEEKER-PD-001/002 |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Weapon ability property | Fits existing ability pattern. Component data is where weapon configuration lives. |
| 2026-04-06 | Default to ["MISSILE", "FIGHTER"] | Backward compat — all existing PDC weapons behave identically without JSON changes. |

---

## Phases

### Phase 1: Add pdc_valid_targets to Ability [Medium]
**Objective:** Data-driven PDC target types
**Status:** Not Started
See `phase_1_checklist.md`

### Phase 2: Update Tests [Simple]
**Objective:** Verify existing behavior + test custom targets
**Status:** Not Started
See `phase_2_checklist.md`

---

## Verification Checklist
- [ ] `pytest tests/unit/simulation/combat/test_targeting_system.py -x` — all pass
- [ ] `python -m simulation_tests.run_tests SEEKER-PD --no-history` — PDC seeker tests pass
- [ ] `python -m simulation_tests.run_tests --fast` — full regression
- [ ] Existing PDC behavior unchanged in game
