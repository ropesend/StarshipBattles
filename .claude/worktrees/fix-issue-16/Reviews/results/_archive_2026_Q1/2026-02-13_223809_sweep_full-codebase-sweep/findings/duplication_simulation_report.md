# Duplication & Fragmentation Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 71
- **Total Issues Found:** 12
- **Critical:** 0 | **Major:** 4 | **Minor:** 6 | **Info:** 2

## Findings

#### MAJOR: Ability `__init__` Pattern Duplication Across Defense/Crew/Propulsion Abilities
**ID:** DUP-SIM-001
**Location:** `game/simulation/components/abilities/defense.py:15-26,40-52,63-67,89-94,112-116` AND `game/simulation/components/abilities/crew.py:14-19,36-41,72-77` AND `game/simulation/components/abilities/propulsion.py:14-19,44-49,91-95`
**Issue:** Multiple ability classes (ShieldProjection, ShieldRegeneration, ToHitAttackModifier, ToHitDefenseModifier, EmissiveArmor, CrewCapacity, LifeSupportCapacity, CrewRequired, CombatPropulsion, ManeuveringThruster, StrategicMovement) all share an almost identical `__init__` pattern:
```python
def __init__(self, component, data: Dict[str, Any]):
    super().__init__(component, data)
    val = data if isinstance(data, (int, float)) else data.get('value', 0)
    self.base_xxx = float(val)  # or int(val)
    self.xxx = self.base_xxx
```
This 5-line initialization pattern is repeated with minor variations across 11+ ability classes.
**Impact:** Maintenance burden when the pattern needs to change; easy to introduce subtle inconsistencies.
**Recommendation:** Extract a base method `_init_single_value_stat(attr_name, default=0, cast=float)` in the `Ability` base class that handles this common pattern.
**Effort:** Simple

#### MAJOR: Repeated `sync_data` Pattern Across Propulsion Abilities
**ID:** DUP-SIM-002
**Location:** `game/simulation/components/abilities/propulsion.py:21-25,50-54,97-101` AND `game/simulation/components/abilities/resources.py:31-41,168-176,208-215`
**Issue:** Multiple ability classes implement nearly identical `sync_data` methods:
```python
def sync_data(self, data: Any):
    super().sync_data(data)
    val = data if isinstance(data, (int, float)) else data.get('value', 0) if isinstance(data, dict) else 0
    self.base_xxx = float(val)
    self.xxx = self.base_xxx
```
This pattern appears in CombatPropulsion, ManeuveringThruster, StrategicMovement, ResourceConsumption, ResourceStorage, and ResourceGeneration.
**Impact:** Copy-paste drift risk; if one sync_data implementation is fixed, others may be missed.
**Recommendation:** Extract `_sync_single_value_stat(attr_name, data, cast=float)` into the base Ability class.
**Effort:** Simple

#### MAJOR: Repeated `recalculate` Pattern for Single-Stat Abilities
**ID:** DUP-SIM-003
**Location:** `game/simulation/components/abilities/propulsion.py:27-28,56-57,103-104` AND `game/simulation/components/abilities/defense.py:21-24,46-49` AND `game/simulation/components/abilities/crew.py:20-21,42-43`
**Issue:** Many ability `recalculate` methods follow the same pattern:
```python
def recalculate(self):
    self.xxx = self._base_xxx * self.get_effective_stat('yyy_mult', 1.0)
```
This single-line recalculation pattern is repeated in: CombatPropulsion, ManeuveringThruster, StrategicMovement, ShieldProjection, ShieldRegeneration, CrewCapacity, LifeSupportCapacity, ResourceStorage, ResourceGeneration.
**Impact:** Low maintenance risk but indicates missing abstraction.
**Recommendation:** Consider a declarative approach where STAT_BINDINGS could auto-apply during recalculate, reducing boilerplate. The STAT_BINDINGS metadata already exists but isn't used for auto-application.
**Effort:** Medium

#### MAJOR: `to_dict` / `from_dict` Serialization Pattern Duplication
**ID:** DUP-SIM-004
**Location:** `game/simulation/battle_state.py:40-59,118-174,344-385` AND `game/simulation/entities/ship_serialization.py:22-107,124-161`
**Issue:** ComponentState, ShipState, ProjectileState, and BattleState all implement similar to_dict/from_dict patterns with field-by-field serialization. ShipSerializer.to_dict and from_dict follow the same manual field serialization approach. The pattern involves:
1. Creating a dict with explicit key assignments
2. from_dict using `data.get('key', default)` for each field
3. Converting nested objects recursively

While not identical, this structural duplication could be reduced.
**Impact:** Adding new fields requires changes in multiple places (both to_dict and from_dict); easy to miss a field.
**Recommendation:** Consider using dataclasses with `asdict()` + custom encoders, or a shared serialization mixin that uses `__dataclass_fields__` for introspection.
**Effort:** Medium

#### MINOR: `get_ui_rows` Return Pattern Duplication
**ID:** DUP-SIM-005
**Location:** `game/simulation/components/abilities/propulsion.py:30-31,59-60,106-107` AND `game/simulation/components/abilities/defense.py:26-27,51-52,75-78,98-101,121-122` AND `game/simulation/components/abilities/crew.py:23-24,45-46,87-88`
**Issue:** Multiple abilities return UI rows in an identical format:
```python
def get_ui_rows(self):
    return [{'label': 'Label', 'value': f"{self.xxx:.0f} unit", 'color_hint': '#XXXXXX'}]
```
This single-row-return pattern is repeated ~15 times across ability classes.
**Impact:** Low risk, but verbose.
**Recommendation:** Create a helper method `_ui_row(label, value, color)` in base Ability class that returns the properly formatted dict.
**Effort:** Simple

#### MINOR: Registry Null Check Pattern
**ID:** DUP-SIM-006
**Location:** `game/simulation/entities/ship.py:48-49` AND `game/simulation/components/component.py:93-94` AND `game/simulation/services/design_loader.py:49-51` AND `game/simulation/services/modifier_service.py:50-51` AND `game/simulation/validation/ship_validator.py:282-284,390-391`
**Issue:** The same null-check pattern for strict DI is repeated across multiple classes:
```python
if registries is None:
    raise TypeError("registries is required for XXX")
```
This exact pattern appears in Ship, Component, SimulationDesignLoader, ModifierService, ClassRequirementsRule, and ShipDesignValidator constructors.
**Impact:** Verbose boilerplate; if error message format needs to change, multiple locations need updating.
**Recommendation:** Extract a utility function `require_registries(registries, context_name)` or use a decorator `@requires_registries` for constructors.
**Effort:** Simple

#### MINOR: Ability Aggregation Logic Split Between Two Locations
**ID:** DUP-SIM-007
**Location:** `game/simulation/entities/ability_aggregator.py:70-166` AND `game/simulation/entities/ship_stat_querier.py:30-78`
**Issue:** Ability aggregation has two parallel implementations:
1. `ability_aggregator.calculate_ability_totals()` - general-purpose aggregation with stacking rules
2. `ShipStatQuerier.get_total_ability_value()` - simpler sum using `get_primary_value()`

These serve slightly different purposes but have overlapping concerns. `get_ability_total` in ShipStatQuerier delegates to `calculate_ability_totals`, but `get_total_ability_value` is a separate implementation.
**Impact:** Confusion about which method to use; potential for inconsistent results if stacking rules differ.
**Recommendation:** Clarify the API - consider whether `get_total_ability_value` should also delegate to a unified aggregation function or document the intentional difference.
**Effort:** Simple

#### MINOR: WeaponAbility Formula Handling Pattern
**ID:** DUP-SIM-008
**Location:** `game/simulation/components/abilities/weapons.py:50-67,69-82,84-97` AND `game/simulation/components/abilities/weapons.py:126-149`
**Issue:** WeaponAbility.__init__ and sync_data both handle damage/range/reload values with identical formula-checking patterns:
```python
if isinstance(raw_xxx, str) and raw_xxx.startswith('='):
    from game.simulation.formula_system import safe_evaluate_math_formula
    self.xxx = float(max(0, safe_evaluate_math_formula(raw_xxx[1:], {})))
else:
    self.xxx = float(raw_xxx) if raw_xxx else default
```
This 5-line block is repeated for damage, range, and reload in both __init__ and sync_data.
**Impact:** If formula evaluation logic needs to change, multiple places need updating.
**Recommendation:** Extract `_parse_formula_or_value(raw_value, default, context={})` method.
**Effort:** Simple

#### MINOR: SeekerWeaponAbility Property Pattern
**ID:** DUP-SIM-009
**Location:** `game/simulation/components/abilities/weapons.py:321-343`
**Issue:** SeekerWeaponAbility.__init__ has a repetitive pattern for initializing optional properties:
```python
self.projectile_speed = float(data.get('projectile_speed', 500))
self.endurance = float(data.get('endurance', 3.0))
self.turn_rate = float(data.get('turn_rate', 30.0))
...
```
vs the else branch:
```python
self.projectile_speed = float(getattr(self.component, 'projectile_speed', 500))
self.endurance = float(getattr(self.component, 'endurance', 3.0))
...
```
This dict-vs-getattr pattern is repeated for 7 properties.
**Impact:** Low risk but verbose.
**Recommendation:** Extract a helper `_get_value(data, key, default, cast=float)` that handles both dict and fallback-to-component cases.
**Effort:** Simple

#### MINOR: LayerRestrictionDefinitionRule Block/Allow Parsing
**ID:** DUP-SIM-010
**Location:** `game/simulation/validation/ship_validator.py:168-194,195-232`
**Issue:** `_check_block_rules` and `_check_allow_rules` both iterate through restrictions and call `_parse_restriction` multiple times with similar patterns:
```python
blocked_class = _parse_restriction(r, RestrictionPrefixes.BLOCK_CLASSIFICATION)
if blocked_class:
    if component.data.get('major_classification') == blocked_class:
        result.add_error(...)
    continue
```
The structure is repeated for classification, id, and ability checks in both methods.
**Impact:** Adding new restriction types requires updating both methods.
**Recommendation:** Use a data-driven approach with a restriction handler table mapping prefix to check function.
**Effort:** Medium

#### INFO: Consistent Use of Helper Class Pattern
**ID:** DUP-SIM-011
**Location:** `game/simulation/components/modifier_manager.py` AND `game/simulation/components/ability_manager.py` AND `game/simulation/components/component_stats_calculator.py` AND `game/simulation/components/component_resource_manager.py` AND `game/simulation/components/component_health_manager.py`
**Issue:** These five helper classes were clearly extracted from Component as part of god class decomposition (PROJ-44, PROJ-88). They follow a consistent pattern:
- Static methods in *Manager classes (ModifierManager, AbilityManager, ComponentStatsCalculator)
- Instance wrappers with component reference (*ResourceManager, *HealthManager)

This is good architecture, not duplication. The consistent pattern aids maintainability.
**Impact:** None - this is a positive observation.
**Recommendation:** Continue this pattern for future extractions. Document the distinction between static utility classes and instance helpers.
**Effort:** N/A

#### INFO: Well-Factored Combat Subsystems
**ID:** DUP-SIM-012
**Location:** `game/simulation/combat/targeting_system.py` AND `game/simulation/combat/damage_calculator.py` AND `game/simulation/combat/weapon_firing_system.py`
**Issue:** These three files represent a clean decomposition of ShipCombatEngine (per PROJ-44 Phase 5 comments). Each has a single responsibility with minimal overlap:
- TargetingSystem: solve_lead, select_target, find_valid_target, calculate_firing_solution
- DamageCalculator: apply_damage, _damage_layer
- WeaponFiringSystem: fire_weapons, _process_hangar_launch, _create_attack, etc.

This is well-factored code with no duplication.
**Impact:** None - this is a positive observation.
**Recommendation:** This decomposition pattern should be used as a template for future refactoring.
**Effort:** N/A

## Top 5 Priority Issues

1. **DUP-SIM-001 (Major):** Ability `__init__` pattern duplication - Extract base class helper method for single-value stat initialization across 11+ ability classes.

2. **DUP-SIM-002 (Major):** Repeated `sync_data` pattern - Similar extraction opportunity for data synchronization logic in abilities.

3. **DUP-SIM-004 (Major):** `to_dict/from_dict` serialization duplication - Consider dataclass introspection for battle state serialization to reduce boilerplate.

4. **DUP-SIM-003 (Major):** Repeated `recalculate` pattern - STAT_BINDINGS metadata exists but isn't leveraged for automatic stat application; could eliminate boilerplate.

5. **DUP-SIM-006 (Minor):** Registry null check pattern - Simple utility extraction to reduce repeated strict DI boilerplate.
