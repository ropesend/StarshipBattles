# Core Architecture Coverage Report

**Date:** 2026-01-02
**Scope:** Core Component System (`components.py`, `abilities.py`, `ship.py`, `component_modifiers.py`)
**Goal:** 100% Test Coverage

## 1. Coverage Summary

| File | Estimated Coverage | Key Strengths | Key Weaknesses |
| :--- | :--- | :--- | :--- |
| `components.py` | ~85% | Basic creation, modifier stacking, `recalculate_stats` flow | Modifier restrictions (`deny_types`), Formula parsing edge cases, `try_activate` flow |
| `abilities.py` | ~70% | Primitive creation, simple resource consumption, basic firing | **Critical Logic**: `check_firing_solution` (geometry), `calculate_hit_chance` (math), `damage_formula` |
| `ship.py` | ~60% | `add_component` constraints, mass calc, damage distribution | **Complex States**: `change_class` (migration), `update_derelict_status`, `remove_component` |
| `component_modifiers.py` | ~50% | `simple_size`, `range_mount`, `turret_mount` | Advanced modifiers (`precision`, `automation`, `rapid_fire`), recursive effects |

## 2. Missing Tests (Detailed Gaps)

### A. Abilities (`abilities.py`)
1.  **Weapon Geometry**: `WeaponAbility.check_firing_solution` is completely untested.
    *   *Need:* Tests checking targets inside/outside arc, angle wrapping (0/360 boundary), and range limits.
2.  **Beam Accuracy Math**: `BeamWeaponAbility.calculate_hit_chance`.
    *   *Need:* Tests for the Sigmoid function, validating falloff at distance, and clamping logic.
3.  **Weapon Formulas**: Parsing of `damage="=10 + range"` is not explicitly tested in `test_abilities.py`.
4.  **Crew/LifeSupport**: `CrewRequired` scaling logic (sqrt of mass) is unused in current tests.

### B. Components (`components.py`)
1.  **Modifier Restrictions**: `add_modifier` has logic for `allow_types` and `deny_types` that is not exercised.
2.  **Activation Logic**: `try_activate`, `can_afford_activation` (trigger='activation') is not fully tested with actual resource checks in `test_components.py`.
3.  **Formula Context**: `_reset_and_evaluate_base_formulas` with missing or complex context variables.

### C. Ship (`ship.py`)
1.  **Class Mutation**: `change_class` is a complex method with migration logic that is completely uncovered.
2.  **Derelict State**: `update_derelict_status` logic (checking boolean vs numeric requirements) is not tested.
3.  **Bulk Operations**: `add_components_bulk`, `remove_component`.

### D. Modifiers (`component_modifiers.py`)
1.  **Advanced Modifiers**: `precision_mount`, `automation`, `rapid_fire`.
2.  **Effect combinations**: Verifying specific niche effects like `arc_set` (Turret) vs `arc_add`.

## 3. Plan: Test Cases to Reach 100%

To achieve 100% coverage, we will implement the following new test cases:

### A. Create `unit_tests/test_abilities_advanced.py`
*   **`test_firing_solution_arcs`**: Create dummy weapon with 90° arc. Test target at 0°, 44°, 46° (fail), 180° (fail). Test wrap-around (359° to 1°).
*   **`test_beam_accuracy_curve`**: Assert hit chance at 0 range (base), max range (falloff), and with attack bonuses.
*   **`test_weapon_damage_formula`**: generic weapon with `damage="=100 - range/10"`. Assert damage at range 0 and 500.

### B. Update `unit_tests/test_components.py`
*   **`test_modifier_restrictions`**:
    *   Define a mock modifier with `deny_types: ["Weapon"]`.
    *   Attempt to add to a Weapon component (assert checks return False).
    *   Attempt to add to an Engine component (assert True).
*   **`test_crew_requirements_scaling`**: Verify `CrewRequired` ability scales non-linearly with mass using a massive mock component.

### C. Update `unit_tests/test_ship.py`
*   **`test_ship_class_change_migration`**:
    *   Create "Frigate" with components in specific layers.
    *   Call `change_class("Destroyer", migrate=True)`.
    *   Assert components are preserved and moved to valid layers.
*   **`test_ship_derelict_logic`**:
    *   Create ship with class requiring "Bridge".
    *   Destroy Bridge component.
    *   Call `update_derelict_status`. Assert `is_derelict` is True.

### D. Update `unit_tests/test_modifiers_advanced.py` (New File)
*   **`test_precision_mount`**: Verify accuracy score increase and mass penalty.
*   **`test_rapid_fire`**: Verify reload time reduction and mass increase formula (`(rate - 1) * 2`).
*   **`test_automation`**: Verify crew requirement reduction.

## Next Steps
1.  Approve this plan.
2.  Execute test creation in the order above.
3.  Run coverage tool to confirm 100%.
