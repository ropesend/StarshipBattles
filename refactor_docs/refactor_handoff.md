# Ability System Refactor - Handoff & Test Ledger

## 1. High-Level Context
**Refactor Goal**: Transition from Inheritance-based Components (`Engine`, `Weapon`) to Composition-based Components (`Component` + `Abilities`).
**Current Phase**: Phase 1 (Foundation)
**Strategy**: Incremental implementation. We are building the `abilities.py` module first. Existing code is untouched for now.

## 2. Test Management Strategy
*   **Active**: Test is valid and expected to pass.
*   **Ignored**: Test is temporarily disabled (skipped) because it relies on code being refactored. Must be re-enabled by the Target Phase.
*   **Deleted**: Test assumes obsolete implementation details (e.g. inheritance checks) and replaced by new capability tests.

## 3. Test Ledger

| Test File | Status | Reason / Context | Target Phase |
| :--- | :--- | :--- | :--- |
| `unit_tests/test_components.py` | **Active** | Core component tests. Will need updates in Phase 2. | Phase 2 |
| `unit_tests/test_component_resources.py` | **Active** | Resource logic. Will likely break when `Tank` class is deprecated. | Phase 2 |
| `unit_tests/test_ship_stats.py` | **Active** | Verifies stat aggregation. Critical regression test for Phase 3. | Phase 3 |
| `unit_tests/test_weapons.py` | **Active** | Verifies firing logic. Critical for Phase 4. | Phase 4 |
| `unit_tests/test_ui_dynamic_update.py` | **Active** | UI logic. Will need update when Component.type checks are removed. | Phase 5 |

## 4. Next Agent Instructions
*   **Current Focus**: Phase 1 - Foundation.
*   **Immediate Action**: Create `abilities.py` and implement the base `Ability` class and the Resource/Gameplay abilities defined in the task list.
*   **Watch Out For**: Circular imports. `abilities.py` should NOT import `components.py`.
