# Research: Data Persistence & Validation

## 1. Validation Rules (ship_validator.py)

The validation system is largely rule-based and inspects component data dictionaries or attributes.

*   **`LayerConstraintRule`**: Checks `allowed_vehicle_types` against the ship's type. This relies on the `allowed_vehicle_types` list in `Component` (loaded from JSON). **Safe to migrate** (data-driven).
*   **`LayerRestrictionDefinitionRule`**: Checks `block_type` and `allow_type` against `component.type_str` (raw string from JSON).
    *   **Action**: If we standardize all components to `type: "Component"`, this rule will break. We must either maintain the legacy `type` field in JSON for categorization or update this rule to check `major_classification` or `tags`.
*   **`ClassRequirementsRule`**: This is **already ability-aware**.
    *   It uses `ShipStatsCalculator.calculate_ability_totals(all_components)`.
    *   It checks requirements defined in `vehicleclasses.json` against these totals.
    *   **Safe**: This aligns perfectly with the refactor.
*   **`ResourceDependencyRule`**: Checks for `ResourceConsumption` and `ResourceStorage` keys in `component.abilities`.
    *   **Safe**: Safe/Aligned. It explicitly looks for the ability keys we are standardizing.

**Strict Class Checks (Risk Area):**
While `ship_validator.py` is mostly safe, `ship.py` contains getters that check Python types:
*   `Ship.max_weapon_range`: Iterates components and checks `isinstance(comp, Weapon)`.
*   `Ship.get_total_sensor_score`: Checks `isinstance(comp, Sensor)`.
*   `Ship.get_total_ecm_score`: Checks `isinstance(comp, Electronics)` and `isinstance(comp, Armor)`.

**Recommendation**: Replace these `isinstance` checks with ability lookups (e.g., `comp.get_ability('WeaponAbility')`).

## 2. Serialization Risks (save_load_system aka ship.py)

I investigated `ship.py` and `test_ship_loading.py`.

*   **Logic**: `Ship.to_dict` saves the *Design*, not the *State*.
    *   It serializes components as: `{"id": "component_id", "modifiers": [...]}`.
    *   It does **NOT** serialize `current_hp`, `cooldowns`, or dynamic ability state.
*   **Loading**: `Ship.from_dict` calls `add_component`, which looks up the ID in `COMPONENT_REGISTRY` and calls `.clone()`.
*   **Conclusion**:
    *   **Low Risk for State**: We don't need to worry about serializing complex `Ability` objects for saved ships, as they are re-instantiated from the registry upon load.
    *   **High Importance of Registry**: The `COMPONENT_REGISTRY` must be populated with components that have fully instantiated `Ability` objects in their `ability_instances` list.
    *   **Runtime State**: Since runtime state isn't saved, we don't need `Ability.to_dict` for ship files.

## 3. Migration Edge Cases (components.json)

The `components.json` structure is flat but contains implicit hybrid data:

*   **Hybrid Components**:
    *   `Railgun`: Acts as `ProjectileWeapon` AND `ResourceConsumer` (Ammo) AND `CrewReq`.
    *   `ShieldRegen`: Acts as `ShieldRegenerator` AND `ResourceConsumer` (Energy).
    *   `Generator`: Acts as `ResourceGenerator` AND `CrewReq`.
    *   These are all standard "1 Component -> N Abilities" mappings.
*   **Special Cases**:
    *   **`Emissive Armor`**: Has a custom ability key `"EmissiveArmor"`. This will need a corresponding `Ability` class or a generic stackable ability.
    *   **`Sensor` / `Electronics`**: define modifiers like `ToHitAttackModifier` in the `abilities` dict. We can treat these as `PassiveModifierAbility` types.
    *   **Legacy Types**: The `type` field (e.g., "Bridge", "Engine") dictates the Python class instantiated (`COMPONENT_TYPE_MAP` in `components.py`).
        *   **Migration Strategy**: We should eventually map all these to a generic `Component` class, but we can do it incrementally.
        *   **Step 1**: Keep `type` in JSON.
        *   **Step 2**: Update `COMPONENT_TYPE_MAP` to point legacy types to the new generic `Component` class (once it supports all features), OR make the specific classes (like `Engine`) thin wrappers that just configure the `CombatPropulsion` ability.

## Summary

The path is clear:
1.  **Validation** is mostly ready, but `ship.py` helper getters need refactoring to remove `isinstance` checks.
2.  **Serialization** is design-only, so we just need to ensure the Factory/Registry creates components with the correct Abilities.
3.  **Data** in `components.json` maps validly to the new system, provided we create Ability handlers for `EmissiveArmor`, `ToHitAttackModifier`, etc.
