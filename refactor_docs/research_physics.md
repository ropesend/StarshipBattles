# Physics & Stat Aggregation Research

## 1. Stat Aggregation (`ShipStatsCalculator`)
**Findings**:
*   **Hybrid Approach**: The calculator is in a transitional state between inheritance-based and active-stat-based logic.
*   **Aggregating Mass**: `mass` is calculated by directly iterating over all components in `ship.layers` and summing `c.mass`. It does not use `isinstance` for this, but relies on every component having a `mass` attribute.
    ```python
    l_mass = sum(c.mass for c in layer_data['components'])
    ```
*   **Aggregating Thrust/Turn**: **Heavily relies on `isinstance`**.
    *   Thrust: Checks `if isinstance(comp, Engine): total_thrust += comp.thrust_force`.
    *   Turn Speed: Checks `if isinstance(comp, Thruster): total_turn_speed += comp.turn_speed`.
*   **Aggregating Resources**: **Uses Generic Abilities**.
    *   Uses `comp.ability_instances` to sum `ResourceStorage` (Fuel/Ammo/Energy Max).
    *   Uses `comp.ability_instances` to sum `ResourceGeneration` (Energy/Ammo Gen).
*   **Aggregating Shields/Armor/Hangars**: **Relies on `isinstance`**.
    *   Armor: `isinstance(comp, Armor)` for HP pool.
    *   Shields: `isinstance(comp, Shield)` and `isinstance(comp, ShieldRegenerator)`.
    *   Hangar: `isinstance(comp, Hangar)`.
*   **Redundancy**: There is some redundant logic for `ability_totals`, but the main `calculate` method branches extensively based on Python class types.

**Conclusion**: Moving mass to an ability will break `ship_stats.py` unless the mass summation loop is updated to look for a `Mass` ability (or similar). Moving Thrust/Turn to an ability will definitely break the `isinstance` checks.

## 2. Formula Context (`formula_system.py` usage)
**Findings**:
*   The `formula_system.py` library is agnostic, but its **usage in `components.py` is restrictive**.
*   **Base Attribute Context**: In `Component._reset_and_evaluate_base_formulas`, the `context` dictionary passed to `evaluate_math_formula` contains **ONLY**:
    ```python
    context = {
        'ship_class_mass': ... # from ship.max_mass_budget
    }
    ```
*   **Access Limitations**:
    *   Formulas **CANNOT** access `component.mass`, `component.cost`, or any other component attribute directly. A formula like `=mass * 0.5` would fail (evaluating to 0) because `mass` is not in the context.
    *   Formulas **CANNOT** access `self`.
*   **Specific Contexts**:
    *   **Weapons**: `Weapon.get_damage(range)` creates a specific context `{'range_to_target': dist}`. This allows damage formulas to depend on range.

**Conclusion**: Since formulas currently do not have access to `component.mass` (or any other self-property), moving mass to an ability **will NOT break existing formulas** (because they can't reference it anyway). However, this limitation means we can't easily write "dynamic" formulas that depend on other stats without explicitly injecting them into the context.

## 3. Physics Interaction (`ship_physics.py`)
**Findings**:
*   **Direct Component Access**: `ShipPhysicsMixin` **directly iterates through components** in `update_physics_movement`.
*   **Duplicated Logic**: It re-calculates `current_total_thrust` by iterating components, checking `isinstance(comp, Engine)`, and summing `comp.thrust_force` for operational engines.
    ```python
    if isinstance(comp, Engine) and comp.is_operational:
         current_total_thrust += comp.thrust_force
    ```
*   **Inheritance Dependency**: It explicitly imports and checks for `Engine` class.
*   **Physics Stats**: It uses `self.mass` (aggregated by `ship_stats.py`) but calculates acceleration dynamically based on the *operational* thrust sum.

**Conclusion**: `ship_physics.py` is tightly coupled to the `Engine` class. It does not trust the `ship.total_thrust` (likely because that's a static max-value, whereas physics needs the *current* operational thrust). Refactoring to Composition will require updating `ship_physics.py` to query abilities (e.g., `get_total_ability_value("Thrust", only_operational=True)`) instead of iterating components and checking types.
