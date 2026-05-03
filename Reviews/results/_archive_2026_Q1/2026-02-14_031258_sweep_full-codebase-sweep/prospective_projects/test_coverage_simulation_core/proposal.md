# Project Proposal: Test Coverage - Simulation Core

## Overview

This project addresses critical test coverage gaps in the simulation layer, focusing on core gameplay systems including ship entities, propulsion, combat mechanics, and battle services. These are foundational systems that affect all battles in the game.

## Rationale

The simulation layer contains the core gameplay logic but has significant test gaps:
- Ship entity (800+ lines) has no dedicated unit tests for critical methods like `die()`, `update()`, and component management
- Propulsion abilities (4 classes) have zero tests - movement is fundamental to combat
- Combat systems (WeaponFiringSystem, BattleEngine) lack edge case coverage
- Battle serialization is untested - save corruption during combat would be catastrophic

## Findings Included

| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|
| TCG-SIM-001 | Critical | No Direct Tests for Ship Entity Core Methods | game/simulation/entities/ship.py | Complex |
| TCG-SIM-002 | Critical | No Tests for Propulsion Abilities | game/simulation/components/abilities/propulsion.py | Medium |
| TCG-SIM-003 | Major | ResourceConsumption and ResourceGeneration Lack Tests | game/simulation/components/abilities/resources.py | Medium |
| TCG-SIM-004 | Major | WeaponFiringSystem Tests Missing Edge Cases | game/simulation/combat/weapon_firing_system.py | Medium |
| TCG-SIM-005 | Major | BattleEngine Missing Tick Processing Edge Cases | game/simulation/systems/battle_engine.py | Complex |
| TCG-SIM-007 | Major | No Tests for BattleService Serialization | game/simulation/services/battle_service.py | Medium |
| TCG-SIM-008 | Major | No Tests for DesignLoader Error Recovery | game/simulation/services/design_loader.py | Medium |
| TCG-SIM-010 | Minor | ShipStatQuerier Not Directly Tested | game/simulation/entities/ship_stat_querier.py | Simple |
| TCG-SIM-011 | Minor | ShipValidatorHelper Not Directly Tested | game/simulation/entities/ship_validator_helper.py | Simple |
| TCG-SIM-014 | Minor | BattleConfig Tests Could Be More Thorough | game/simulation/battle_config.py | Simple |
| TCG-SIM-015 | Minor | PhysicsConstants Could Test Derived Values | game/simulation/physics_constants.py | Simple |
| TCG-SIM-018 | Minor | Superweapons Ability Tests Missing Activation | game/simulation/components/abilities/superweapons.py | Medium |

## Summary Statistics

- **Total Findings:** 12
- **Critical:** 2 | **Major:** 5 | **Minor:** 5
- **Estimated Effort:** Complex (due to Ship entity tests and BattleEngine edge cases)
- **Primary Location:** game/simulation/

## Overlap with Active Projects

Potential overlap with:
- PROJ-143: 3_test_coverage_strategy_ai (different shard - Strategy/AI vs Simulation)
- PROJ-135: Test Coverage - Strategy Engine (different layer)
- PROJ-130: test-coverage-core-systems (may overlap on core systems)
- PROJ-118: Test Coverage -- Core and Simulation (likely duplicate)

**Recommendation:** Verify PROJ-118 and PROJ-130 status before starting. This project focuses specifically on simulation-layer test gaps identified in this sweep.

## Success Criteria

1. Ship entity has dedicated test file with coverage for `die()`, `update()`, `recalculate_stats()`, component management
2. All 4 propulsion ability classes have unit tests
3. Combat systems have edge case tests (negative damage, zero speed, dead targets)
4. Battle save/load roundtrip is tested
5. All tests pass and coverage increases for simulation/
