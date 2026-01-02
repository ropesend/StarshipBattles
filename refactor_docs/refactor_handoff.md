# Ability System Refactor - Handoff & Test Ledger

## 1. High-Level Context
**Refactor Goal**: Transition from Inheritance-based Components (`Engine`, `Weapon`) to Composition-based Components (`Component` + `Abilities`).
**Current Phase**: Phase 3 (Completed) / Pre-Phase 4
**Strategy**: `Component` class is refactored. `abilities` are now instantiated from data. A **Legacy Shim** is active to auto-create abilities from legacy fields (`thrust_force`, `damage`). Stats calculation now uses ability-based iteration instead of `isinstance` checks.
**Next Focus**: Phase 4 - Combat System Migration. Move firing logic to Abilities and refactor `ship_combat.py`.

## 2. Test Management Strategy
*   **Active**: Test is valid and expected to pass.
*   **Ignored**: Test is temporarily disabled (skipped) because it relies on code being refactored. Must be re-enabled by the Target Phase.
*   **Deleted**: Test assumes obsolete implementation details (e.g. inheritance checks) and replaced by new capability tests.

### Protocol for Broken Tests
1.  **Try to Fix**: If the fix is simple (e.g. update a mock), fix it immediately.
2.  **Mark as Ignored**: If fixing requires significant refactoring that is scheduled for a later phase, mark it as `Ignored` in the Ledger below.
3.  **Annotate**: Add a `@unittest.skip("Refactor Phase X")` decorator to the test method/class.
4.  **Track**: Ensure the Ledger reflects the "Target Phase" for reinstatement.

## 3. Test Ledger

| Test File | Status | Reason / Context | Target Phase |
| :--- | :--- | :--- | :--- |
| `unit_tests/test_components.py` | **Active** | Core component tests. PASSED Phase 2. | Phase 2 |
| `unit_tests/test_component_resources.py` | **Active** | Resource logic. PASSED Phase 2. | Phase 2 |
| `unit_tests/test_ship_stats.py` | **Active** | NEW. Baseline tests for stats calculation. PASSED Phase 3. | Phase 3 |
| `unit_tests/test_ship.py` | **Active** | General ship regression. PASSED. | Phase 3 |
| `unit_tests/test_weapons.py` | **Active** | Verifies firing logic. Critical for Phase 4. | Phase 4 |
| `unit_tests/test_ui_dynamic_update.py` | **Active** | UI logic. Will need update when Component.type checks are removed. | Phase 5 |
| `unit_tests/test_fighter_launch.py` | **Active** | Hangar logic. Critical for Phase 4. | Phase 4 |
| `unit_tests/test_pdc.py` | **Active** | Point Defense targeting. Critical for Phase 4. | Phase 4 |
| `unit_tests/test_component_modifiers_extended.py` | **Active** | Modifier stacking. Critical for Phase 2. | Phase 2 |
| `unit_tests/test_bridge_requirement_removal.py` | **Active** | Bridge logic verification. Critical for Phase 2. | Phase 2 |
| `unit_tests/test_ship_physics_mixin.py` | **Active** | Physics calcs. PASSED Phase 3 with ability-based thrust. | Phase 3 |
| `unit_tests/test_ai.py` | **Active** | AI logic. Critical to verify PDC/Formation checks refactor. | Phase 4 |
| `unit_tests/test_battle_panels.py` | **Active** | UI logic. Verify refactor of `draw_ship_details`. | Phase 5 |
| `unit_tests/test_builder_validation.py` | **Active** | validation logic. Critical for data integrity. | Phase 6 |
| `unit_tests/test_component_composition.py` | **Active** | NEW. Verifies generic component ability composition. PASSED. | Phase 2 |
| `unit_tests/test_legacy_shim.py` | **Active** | NEW. Verifies legacy component data backward compatibility. PASSED. | Phase 2 |

## 4. Next Agent Instructions
*   **Current Focus**: Begin Phase 4 (Combat System Migration).
*   **Phase 3 Summary**: 
    - Fixed modifier-to-ability synchronization in `components.py` (line 538-564)
    - Created `test_ship_stats.py` baseline (6 tests)
    - Added `Ship.get_total_ability_value()` helper in `ship.py`
    - Refactored `ship_stats.py` to use ability-based iteration (replaced 6 isinstance checks)
    - Refactored `ship_physics.py` to use `get_total_ability_value('CombatPropulsion')`
*   **Phase 4 Goal**: Move weapon firing logic to `WeaponAbility.fire()`. Refactor `ship_combat.py` to iterate components with `WeaponAbility` instead of `isinstance(Weapon)`.
*   **Key Files for Phase 4**: `ship_combat.py`, `abilities.py` (WeaponAbility classes)
*   **Caution**: PDC targeting logic uses `ability.get('PointDefense')` - this needs to use `ability.tags` like `{'pdc'}` instead.
*   **Test Verification**: Run `python -m unittest unit_tests.test_weapons unit_tests.test_pdc unit_tests.test_fighter_launch -v` before and after changes.

