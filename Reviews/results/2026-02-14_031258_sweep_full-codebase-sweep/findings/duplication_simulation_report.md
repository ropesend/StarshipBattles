# Duplication & Fragmentation Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 69
- **Total Issues Found:** 12
- **Critical:** 0 | **Major:** 4 | **Minor:** 6 | **Info:** 2

## Findings

#### MAJOR: Ability Pattern Boilerplate Duplication
**ID:** DUP-SIM-001
**Location:** `game/simulation/components/abilities/propulsion.py:7-110` AND `game/simulation/components/abilities/defense.py:8-126` AND `game/simulation/components/abilities/resources.py:9-230` AND `game/simulation/components/abilities/crew.py:8-92`
**Issue:** All ability classes follow an identical structural pattern with repetitive boilerplate:
1. Constructor extracts value from data dict (5-8 lines each)
2. `sync_data()` method repeats same logic (5-10 lines each)
3. `recalculate()` method applies effective stat multiplier (2-4 lines each)
4. `get_ui_rows()` returns list with dict (2-5 lines each)
5. `get_primary_value()` returns the main value (2 lines each)

This pattern is repeated across 15+ ability classes with nearly identical structure. The value extraction logic (`val = data if isinstance(data, (int, float)) else data.get('value', 0)`) appears in ~20 places.
**Impact:** Adding new abilities requires copying significant boilerplate. Bug fixes or changes to the pattern require touching many files.
**Recommendation:** Create a `NumericAbility` or `SimpleAbility` base class that handles common patterns:
- Constructor accepts data, stat_key, base_attr_name
- `sync_data` and `recalculate` implemented once with parameters
- Only override `get_ui_rows` for custom formatting
**Effort:** Medium

#### MAJOR: Formula Evaluation Pattern Duplication
**ID:** DUP-SIM-002
**Location:** `game/simulation/components/abilities/weapons.py:51-150` (damage, range, reload formulas) AND `game/simulation/components/component_stats_calculator.py:118-210` (component formulas) AND `game/simulation/formula_system.py`
**Issue:** Formula evaluation logic (`if isinstance(value, str) and value.startswith('=')`) is duplicated across multiple locations:
1. WeaponAbility.__init__ evaluates damage/range/reload formulas
2. WeaponAbility.sync_data re-evaluates the same formulas
3. ComponentStatsCalculator.reset_and_evaluate_formulas evaluates component attributes
4. ComponentStatsCalculator._evaluate_formulas_in_abilities has recursive evaluation

The pattern `if isinstance(raw, str) and raw.startswith('=')` followed by `safe_evaluate_math_formula(raw[1:], context)` appears ~12 times.
**Impact:** Inconsistent formula handling could cause bugs. Changes to formula evaluation need multiple updates.
**Recommendation:** Create a unified `evaluate_formula_field(raw_value, context, default=0)` utility that handles the type check, prefix strip, and evaluation consistently.
**Effort:** Simple

#### MAJOR: Resource Type Handling Duplication
**ID:** DUP-SIM-003
**Location:** `game/simulation/entities/ship_stats.py:279-302` (ResourceStorage/ResourceGeneration aggregation) AND `game/simulation/components/abilities/resources.py:24-150` (ResourceConsumption handling) AND `game/simulation/validation/ship_validator.py:332-370` (ResourceDependencyRule)
**Issue:** Resource type checking and handling is duplicated:
1. ship_stats.py checks `res_type == ResourceType.FUEL/AMMO/ENERGY` in aggregation
2. resources.py checks resource_type in get_ui_rows and consumption logic
3. ship_validator.py iterates abilities checking isinstance(ab, ResourceConsumption/ResourceStorage)

The pattern of iterating components -> checking ability instances -> extracting resource_type appears in multiple places.
**Impact:** Adding a new resource type requires changes in multiple locations. Inconsistent handling could cause resources to work in one context but not another.
**Recommendation:** Consider a ResourceTypeRegistry or use the ability_aggregator pattern to centralize resource ability extraction.
**Effort:** Medium

#### MAJOR: Validation Pattern Repetition in Loaders
**ID:** DUP-SIM-004
**Location:** `game/simulation/components/component.py:475-548` (load_components_data) AND `game/simulation/components/component.py:589-647` (load_modifiers_data) AND `game/simulation/entities/ship_loader.py:37-98` (load_vehicle_classes_data)
**Issue:** All three loader functions follow the same pattern:
1. Check path exists, try absolute path (5-10 lines)
2. Try-except around load_json_required
3. Iterate entries, try-except individual items
4. Log errors, collect error list
5. Return result dict

The error collection pattern (`errors = []; try: ... except: errors.append(); if errors: log_warning(...)`) is nearly identical across all three.
**Impact:** Inconsistent error handling or logging. Adding new data loaders requires copying boilerplate.
**Recommendation:** Create a generic `load_registry_data(file_path, item_key, factory_fn)` function that encapsulates the common pattern. Each loader provides only the factory function for creating items.
**Effort:** Medium

#### MINOR: Target Validation Pattern Duplication
**ID:** DUP-SIM-005
**Location:** `game/simulation/combat/targeting_system.py:96-115` (select_target) AND `game/simulation/combat/targeting_system.py:147-175` (find_valid_target) AND `game/simulation/combat/weapon_firing_system.py:158-186` (_find_valid_target)
**Issue:** Target validation checks are duplicated:
```python
if not getattr(candidate, 'is_alive', True):
    continue
if getattr(candidate, 'team_id', -1) == ship.team_id:
    continue
```
This exact pattern appears in 3 places in the combat subsystem.
**Impact:** Low - code is co-located and well-documented, but any change to target validity logic requires multiple updates.
**Recommendation:** Extract `is_valid_target(ship, candidate)` helper function.
**Effort:** Simple

#### MINOR: Component Iteration Pattern
**ID:** DUP-SIM-006
**Location:** `game/simulation/entities/ship.py:616-634` (get_all_components) AND `game/simulation/entities/ship.py:647-670` (get_components_by_ability) AND `game/simulation/entities/ship_stats.py:83-104` (calculate mass/hp)
**Issue:** Pattern of iterating `ship.layers.values()` then extending/appending is repeated:
```python
for layer_data in ship.layers.values():
    for comp in layer_data.components:
        # process component
```
This exact two-level iteration appears ~8 times across ship-related files.
**Impact:** Low - ship.get_all_components() exists but isn't always used when filtering is needed.
**Recommendation:** Already largely addressed. Consider using get_all_components() more consistently.
**Effort:** Simple

#### MINOR: UI Row Generation Pattern
**ID:** DUP-SIM-007
**Location:** `game/simulation/components/abilities/weapons.py:208-213` AND `game/simulation/components/abilities/propulsion.py:30-31` AND `game/simulation/components/abilities/defense.py:26-27` AND 10+ other ability files
**Issue:** All `get_ui_rows()` methods return similar dict structures:
```python
return [{'label': 'Name', 'value': f"{self.value:.0f}", 'color_hint': '#HEXCOLOR'}]
```
While the specific values differ, the format is identical and could be generated from metadata.
**Impact:** Low - purely cosmetic duplication in presentation layer interface.
**Recommendation:** Consider using STAT_BINDINGS metadata to auto-generate UI rows, similar to how effect_summary works.
**Effort:** Medium

#### MINOR: Physics Constants Duplication
**ID:** DUP-SIM-008
**Location:** `game/simulation/entities/ship_physics.py:32-33` AND `game/simulation/entities/ship_stats.py:227-231` (K_SPEED, K_THRUST usage)
**Issue:** Both files import and use K_SPEED/K_THRUST constants for the same physics calculations:
- ship_physics.py: calculates current_accel and potential_max_speed
- ship_stats.py: calculates ship.acceleration_rate and ship.max_speed

The formulas `(thrust * K_THRUST) / (mass * mass)` and `(thrust * K_SPEED) / mass` appear in both places.
**Impact:** Low - one is for real-time physics updates, other is for stat calculation. Formulas must stay synchronized.
**Recommendation:** Consider extracting to `physics_formulas.py` with `calculate_acceleration(thrust, mass)` and `calculate_max_speed(thrust, mass)`.
**Effort:** Simple

#### MINOR: Registries DI Guard Clause Pattern
**ID:** DUP-SIM-009
**Location:** `game/simulation/entities/ship.py:48-49` AND `game/simulation/components/component.py:93-94` AND `game/simulation/services/design_loader.py:49-50` AND `game/simulation/validation/ship_validator.py:283-284,390-391`
**Issue:** The strict DI guard clause pattern is repeated identically in 8+ constructors:
```python
if registries is None:
    raise TypeError("registries is required for X initialization")
```
**Impact:** Low - this is intentional defensive programming for PROJ-50.
**Recommendation:** None needed - the duplication is acceptable for explicit error messages. Could use a decorator if scaling to 20+ locations.
**Effort:** N/A (Intentional)

#### MINOR: Projectile Type Check Pattern
**ID:** DUP-SIM-010
**Location:** `game/simulation/combat/targeting_system.py:158-161` AND `game/simulation/combat/weapon_firing_system.py:227-234` AND `game/simulation/projectile_manager.py:150-151`
**Issue:** Missile/projectile type checking appears in multiple combat files:
- targeting_system: `if t_type == AttackType.MISSILE and not is_pdc`
- weapon_firing: `if comp.has_ability('SeekerWeaponAbility')` vs `ProjectileWeaponAbility`
- projectile_manager: `if p.type == AttackType.MISSILE`
**Impact:** Low - different contexts require different checks.
**Recommendation:** Already reasonably factored. The distinctions are intentional.
**Effort:** N/A (Intentional variance)

#### INFO: Well-Factored Delegation Patterns
**ID:** DUP-SIM-011
**Location:** `game/simulation/entities/ship_combat_engine.py` AND `game/simulation/combat/*.py`
**Issue:** (Positive observation) The ShipCombatEngine demonstrates GOOD decomposition:
- Delegates targeting to TargetingSystem
- Delegates damage to DamageCalculator
- Delegates firing to WeaponFiringSystem
- Keeps only combat cooldowns as ship-specific state

The combat subsystem shows how the codebase SHOULD be organized. Similar patterns should be applied elsewhere.
**Impact:** Positive pattern to follow.
**Recommendation:** Use as template for other subsystem decompositions.
**Effort:** N/A

#### INFO: Ability Aggregation Well Centralized
**ID:** DUP-SIM-012
**Location:** `game/simulation/entities/ability_aggregator.py`
**Issue:** (Positive observation) The ability_aggregator module centralizes the complex two-phase aggregation logic (intra-group MAX, inter-group SUM/MULT) in one place. Both `ship_stats.py` and `ship_stat_querier.py` delegate to this module.

This is a good example of DRY - the complex aggregation algorithm exists in one place.
**Impact:** Positive pattern.
**Recommendation:** Maintain this pattern. Consider extending for new aggregation needs.
**Effort:** N/A

## Top 5 Priority Issues

1. **DUP-SIM-001 (MAJOR)**: Ability Pattern Boilerplate - 15+ ability classes share identical structural patterns. Creating a NumericAbility base class would reduce ~200 lines of boilerplate and make adding new abilities trivial.

2. **DUP-SIM-002 (MAJOR)**: Formula Evaluation Pattern - Formula string detection and evaluation is duplicated ~12 times. A single utility function would ensure consistent behavior and reduce copy-paste errors.

3. **DUP-SIM-003 (MAJOR)**: Resource Type Handling - Resource type checks are scattered across stats calculation, consumption abilities, and validation. Centralizing would make adding new resource types a single-point change.

4. **DUP-SIM-004 (MAJOR)**: Validation Pattern in Loaders - Three data loaders follow identical error-handling patterns. A generic loader utility would reduce ~150 lines and ensure consistent error reporting.

5. **DUP-SIM-005 (MINOR)**: Target Validation Pattern - Simple extraction of `is_valid_target()` helper would reduce 3 duplicate checks to 1.

## Notes

The simulation module overall demonstrates good architectural discipline with well-defined layer boundaries and appropriate use of delegation patterns. The duplication found is primarily:

1. **Structural boilerplate** in ability classes that could be addressed with better base class design
2. **Cross-cutting concerns** (formula evaluation, data loading) that could use shared utilities
3. **Minor pattern repetition** that is acceptable in context

The combat subsystem (targeting_system, damage_calculator, weapon_firing_system) shows excellent decomposition and can serve as a model for addressing the remaining duplication.
