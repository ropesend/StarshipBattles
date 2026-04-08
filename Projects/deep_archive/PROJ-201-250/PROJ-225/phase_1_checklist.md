# Phase 1: StaticValueAbility + Physics Formulas
**Status:** Complete

## Task 1.1: Extract StaticValueAbility Base Class [Simple]
**Findings:** DUP-CMP-001, DUP-CMP-002
**Tests:** tests/unit/simulation/components/abilities/test_static_value_ability.py (new)
- [x] Write tests for StaticValueAbility behavior (value parsing, no-op recalculate, get_primary_value, get_ui_rows)
- [x] Create `StaticValueAbility` in `game/simulation/components/abilities/base.py` extending `Ability`
- [x] Refactor `ToHitAttackModifier` to extend `StaticValueAbility` with class attrs only
- [x] Refactor `ToHitDefenseModifier` to extend `StaticValueAbility` with class attrs only
- [x] Refactor `EmissiveArmor` to extend `StaticValueAbility` with class attrs only
- [x] Run tests, verify all pass
**Notes:** Created `StaticValueAbility` with class attrs: ui_label, ui_color, ui_format, int_result. EmissiveArmor now uses `.value`/`._base_value` instead of `.amount`/`._base_amount`. Updated 3 test files referencing the old attribute names.

## Task 1.2: Extract Shared Physics Formulas [Simple]
**Finding:** DUP-SIM-001
**Tests:** tests/unit/simulation/test_physics_formulas.py (extended with 10 new tests)
- [x] Write tests for `compute_acceleration(thrust, mass)` and `compute_max_speed(thrust, mass)`
- [x] Add `compute_acceleration()` and `compute_max_speed()` to `game/simulation/physics_constants.py`
- [x] Update `ShipStatsCalculator._phase_physics_and_limits()` to call shared functions
- [x] Update `ShipPhysicsMixin.update_physics_movement()` to call shared functions
- [x] Run tests, verify all pass
**Notes:** Both functions include mass <= 0 guard. Updated test_physics.py consolidation test to check for shared functions instead of raw K_SPEED/K_THRUST imports.

## Completion Checklist
- [x] All Phase 1 tests pass
- [x] Incremental regression passes (`pytest tests/ --testmon`)
