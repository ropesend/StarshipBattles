# Ability System Refactor - Handoff & Test Ledger

## 1. High-Level Context
**Refactor Goal**: Transition from Inheritance-based Components (`Engine`, `Weapon`) to Composition-based Components (`Component` + `Abilities`).
**Current Phase**: Phase 1 (Foundation)
**Strategy**: Incremental implementation. We are building the `abilities.py` module first. Existing code is untouched for now.

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
| `unit_tests/test_components.py` | **Active** | Core component tests. Will need updates in Phase 2. | Phase 2 |
| `unit_tests/test_component_resources.py` | **Active** | Resource logic. Will likely break when `Tank` class is deprecated. | Phase 2 |
| `unit_tests/test_ship_stats.py` | **Active** | Verifies stat aggregation. Critical regression test for Phase 3. | Phase 3 |
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

## 4. Next Agent Instructions
*   **Current Focus**: Phase 1 - Foundation.
*   **Immediate Action**: Create `abilities.py` and implement the base `Ability` class and the Resource/Gameplay abilities defined in the task list.
*   **Watch Out For**: Circular imports. `abilities.py` should NOT import `components.py`.
