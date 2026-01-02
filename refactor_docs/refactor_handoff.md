# Ability System Refactor - Handoff & Test Ledger

## 1. High-Level Context
**Refactor Goal**: Transition from Inheritance-based Components (`Engine`, `Weapon`) to Composition-based Components (`Component` + `Abilities`).
**Current Phase**: Phase 2 (Completed - Verified & Fixed Shield Shim) / Pre-Phase 3
**Strategy**: `Component` class is refactored. `abilities` are now instantiated from data. A **Legacy Shim** is active to auto-create abilities from legacy fields (`thrust_force`, `damage`).
**Next Focus**: Phase 3 - Stats & Physics Integration. Decouple `ship_stats.py` and `ship_physics.py` from specific component classes.

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
| `unit_tests/test_ship_stats.py` | **Missing** | File referenced in plan but does not exist. Created `test_ship.py` as regression baseline. Needs creation. | Phase 3 |
| `unit_tests/test_ship.py` | **Active** | General ship regression. PASSED. | Phase 3 |
| `unit_tests/test_weapons.py` | **Active** | Verifies firing logic. Critical for Phase 4. | Phase 4 |
| `unit_tests/test_ui_dynamic_update.py` | **Active** | UI logic. Will need update when Component.type checks are removed. | Phase 5 |
| `unit_tests/test_fighter_launch.py` | **Active** | Hangar logic. Critical for Phase 4. | Phase 4 |
| `unit_tests/test_pdc.py` | **Active** | Point Defense targeting. Critical for Phase 4. | Phase 4 |
| `unit_tests/test_component_modifiers_extended.py` | **Active** | Modifier stacking. Critical for Phase 2. | Phase 2 |
| `unit_tests/test_bridge_requirement_removal.py` | **Active** | Bridge logic verification. Critical for Phase 2. | Phase 2 |
| `unit_tests/test_ship_physics_mixin.py` | **Active** | Physics calcs. Critical to verify removal of duplicated loop. | Phase 3 |
| `unit_tests/test_ai.py` | **Active** | AI logic. Critical to verify PDC/Formation checks refactor. | Phase 4 |
| `unit_tests/test_battle_panels.py` | **Active** | UI logic. Verify refactor of `draw_ship_details`. | Phase 5 |
| `unit_tests/test_builder_validation.py` | **Active** | validation logic. Critical for data integrity. | Phase 6 |
| `unit_tests/test_component_composition.py` | **Active** | NEW. Verifies generic component ability composition. PASSED. | Phase 2 |
| `unit_tests/test_legacy_shim.py` | **Active** | NEW. Verifies legacy component data backward compatibility. PASSED. | Phase 2 |

## 4. Next Agent Instructions
*   **Current Focus**: Audit Phase 2 & Begin Phase 3 (Stats/Physics).
*   **Audit**: Review `components.py` changes. Ensure Legacy Shim covers all necessary cases (Thrust, Turn, Damage, Shields). **(DONE: Added Shield Shims)**
*   **Verify**: Run `python -m unittest unit_tests/test_legacy_shim.py unit_tests/test_component_composition.py`.
*   **Phase 3 Goal**: Stop calculating stats by iterating `isinstance(c, Engine)`. Instead, iterate components and sum `c.get_ability('CombatPropulsion').value`.
*   **Caution**: `ship_stats.py` uses explicit type checks. These must be replaced with `c.has_ability()` or `c.get_abilities()`. Do NOT remove the component subclasses (`Engine`, `Weapon`) yet—just decouple the *calculations* from them.
*   **CRITICAL IMPLEMENTATION GAP**: Currently, `Component.recalculate_stats` updates *legacy attributes* (e.g., `self.thrust_force`) with modifiers, but does **NOT** update the corresponding `Ability` instances (e.g., `CombatPropulsion.thrust_force` stays at base value). **Before switching stats calculations to use Abilities in Phase 3, you MUST update `recalculate_stats` to apply modifiers to the Ability instances.** Failure to do this will break all modifier effects (bonuses/penalties).
