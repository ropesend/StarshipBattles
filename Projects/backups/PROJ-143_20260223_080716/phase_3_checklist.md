# Phase 3: Other

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-143 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings not mapped to a specific shard
**Priority:** Normal

---

## Tasks

### Task 3.1: UNK-01 - Missing integration tests for component destruction cascade [DONE]
**File:** `game/simulation/combat/damage_calculator.py`
**Tests:** `pytest tests/integration/fleet_combat/test_component_destruction_cascade.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added 13 integration tests covering: engine destruction -> thrust=0, shield destruction -> max_shields reduced, damage cascade through DamageCalculator, partial damage edge cases, combat flow integration.

### Task 3.2: UNK-04 - Resource consumption during combat tick [DONE]
**File:** `game/simulation/systems/resource_manager.py`
**Tests:** `pytest tests/integration/fleet_combat/test_combat_resource_consumption.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added 25 tests covering: ResourceState basics (consume, has_sufficient, add, update), ResourceRegistry integration (multi-resource tracking, stacking storage/generation, reset), ship resource consumption, combat resource flow (depletion, regeneration), edge cases.

### Task 3.3: UNK-02 - Defense ability classes undertested in isolation [ALREADY DONE]
**File:** `game/simulation/components/abilities/defense.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_defense_isolation.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** File already exists with 67 comprehensive tests covering ShieldProjection, ShieldRegeneration, ToHitAttackModifier, ToHitDefenseModifier, EmissiveArmor classes - all __init__, recalculate, get_ui_rows, get_primary_value methods and edge cases.

### Task 3.4: UNK-03 - Crew ability classes have minimal test coverage [DONE]
**File:** `game/simulation/components/abilities/crew.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/test_crew_abilities.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added 55 tests covering CrewCapacity, LifeSupportCapacity, CrewRequired - all __init__ variants, recalculate with modifiers, get_ui_rows, get_primary_value, stat bindings, edge cases (large values, zero multipliers, sqrt scaling for CrewRequired).

### Task 3.5: UNK-05 - BattleLogger tests exist but outside sim [DONE]
**File:** `game/simulation/systems/battle_engine.py` (BattleLogger class)
**Tests:** `pytest tests/unit/simulation/systems/test_battle_logger.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Created comprehensive test file at correct location (tests/unit/simulation/systems/test_battle_logger.py) with 28 tests. Deleted old misplaced test file (tests/unit/combat/test_battle_logger.py). Tests cover: init, context manager, start_session, log, close, destructor, integration scenarios.

### Task 3.6: UNK-06 - Formula system exception handling edge c [ALREADY DONE]
**File:** `game/simulation/formula_system.py`
**Tests:** `pytest tests/unit/simulation/test_formula_exceptions.py tests/unit/refactor/test_formula_*.py tests/unit/systems/test_formula_system.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Comprehensive tests already exist across multiple files: test_formula_exceptions.py (17 tests), test_formula_error_handling.py (13 tests), test_formula_edge_cases.py (25 tests), test_formula_validation.py, test_formula_system.py (21 tests) - covering syntax errors, undefined vars, div by zero, dangerous functions, security sandbox, edge cases, real-world formulas.

### Task 3.7: UNK-07 - ShipStatQuerier class lacks dedicated te [ALREADY DONE]
**File:** `game/simulation/entities/ship_stat_querier.py`
**Tests:** `pytest tests/unit/entities/test_ship_stat_querier.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Comprehensive tests already exist (843+ lines) in tests/unit/entities/test_ship_stat_querier.py covering: initialization, get_ability_total, get_total_ability_value, sensor/ECM scores, max_weapon_range, cached_summary, edge cases for all methods.

### Task 3.8: UNK-08 - ship_serialization module could use erro [ALREADY DONE]
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_serialization.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Comprehensive tests already exist (860+ lines) in tests/unit/simulation/entities/test_ship_serialization.py covering: to_dict serialization, from_dict deserialization, round-trip tests, edge cases (empty data, missing fields, invalid data), helper methods (_load_components, _restore_resources, _verify_stats), modifiers, multiple components.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
