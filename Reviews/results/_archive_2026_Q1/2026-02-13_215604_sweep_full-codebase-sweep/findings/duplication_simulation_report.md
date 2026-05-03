# Duplication Analysis Report: game/simulation/

**Sweep Agent:** duplication
**Shard:** game/simulation/
**Date:** 2026-02-13
**Files Analyzed:** 69

---

## Executive Summary

The simulation layer demonstrates **excellent code hygiene** with minimal duplication. The architecture follows a **God-class decomposition pattern** where large classes delegate to specialized helper classes (Ship -> ShipStatsCalculator, ShipCombatEngine, etc.). This is the **correct** approach and should not be conflated with duplication.

**Key Findings:**
- 4 MINOR issues (low-impact natural patterns)
- 2 INFO observations (acceptable design patterns)
- 0 CRITICAL or MAJOR issues

The codebase shows evidence of deliberate DRY-conscious design with:
- Centralized ability system with base class inheritance
- Single source of truth for physics constants
- Shared validation framework with template method pattern
- Consistent modifier/stat binding system

---

## Findings

### DUP-SIM-001
**Severity:** MINOR
**Type:** Structural Similarity
**Pattern:** Ability class boilerplate

**Locations:**
1. `game/simulation/components/abilities/defense.py` - ShieldProjection, ShieldRegeneration, ToHitAttackModifier, ToHitDefenseModifier, EmissiveArmor
2. `game/simulation/components/abilities/propulsion.py` - CombatPropulsion, ManeuveringThruster, StrategicMovement, WarpJump
3. `game/simulation/components/abilities/crew.py` - CrewCapacity, LifeSupportCapacity, CrewRequired
4. `game/simulation/components/abilities/superweapons.py` - DestroyPlanet, DestroyStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere, SelfDestruct

**Description:**
All ability classes follow the same structural pattern:
```python
class SomeAbility(Ability):
    STAT_BINDINGS: List[AbilityStatBinding] = [...]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.value = float(val)
        self._base_value = self.value

    def recalculate(self):
        self.value = self._base_value * self.get_effective_stat('some_mult', 1.0)

    def get_ui_rows(self): ...
    def get_primary_value(self) -> float: ...
```

**Assessment:**
This is **intentional and correct**. The pattern exists because:
1. All abilities must implement the same interface (defined by base `Ability` class)
2. The STAT_BINDINGS system requires explicit declarations per ability type
3. Different abilities have different stats to modify

**Action:** NONE REQUIRED. This is proper use of inheritance with specialization. The base class (`Ability`) already provides shared logic. Each subclass only implements what differs.

---

### DUP-SIM-002
**Severity:** MINOR
**Type:** Structural Similarity
**Pattern:** Data parsing pattern in ability constructors

**Locations:**
1. `game/simulation/components/abilities/resources.py` - ResourceConsumption, ResourceStorage, ResourceGeneration
2. `game/simulation/components/abilities/cargo.py` - CargoStorage
3. `game/simulation/components/abilities/harvester.py` - ResourceHarvesterAbility, EmpireStorageAbility

**Description:**
Multiple abilities use similar patterns for parsing dict vs primitive data:
```python
if isinstance(data, dict):
    self.resource_type = data.get('resource', '')
    self.amount = data.get('amount', 0.0)
elif isinstance(data, (int, float)):
    self.amount = float(data)
```

**Assessment:**
This pattern handles JSON shorthand syntax flexibility (e.g., `"ResourceStorage": 100` vs `"ResourceStorage": {"resource": "fuel", "amount": 100}`). Each ability needs different fields parsed, so a generic helper wouldn't reduce complexity.

**Action:** LOW PRIORITY. Could potentially add a `parse_dict_or_scalar()` utility to base `Ability` class, but the benefit is marginal given each ability needs different fields.

---

### DUP-SIM-003
**Severity:** MINOR
**Type:** Structural Similarity
**Pattern:** sync_data() method pattern

**Locations:**
1. `game/simulation/components/abilities/propulsion.py` - CombatPropulsion.sync_data(), ManeuveringThruster.sync_data(), StrategicMovement.sync_data()
2. `game/simulation/components/abilities/resources.py` - ResourceConsumption.sync_data(), ResourceStorage.sync_data(), ResourceGeneration.sync_data()
3. `game/simulation/components/abilities/cargo.py` - CargoStorage.sync_data()

**Description:**
All sync_data() implementations follow the same pattern:
```python
def sync_data(self, data: Any):
    super().sync_data(data)
    if isinstance(data, dict):
        self.field = data.get('field', self.field)
        self._base_field = self.field
    elif isinstance(data, (int, float)):
        self.field = float(data)
        self._base_field = self.field
```

**Assessment:**
This is necessary boilerplate for the modifier system's two-stage calculation (base value -> modified value). Each ability syncs different fields.

**Action:** LOW PRIORITY. The pattern is necessary for the modifier binding system. No action needed.

---

### DUP-SIM-004
**Severity:** MINOR
**Type:** Semantic Similarity
**Pattern:** Validation result aggregation

**Locations:**
1. `game/simulation/validation/ship_validator.py` - ShipDesignValidator.validate_addition() and validate_design()
2. `game/simulation/services/battle_service.py` - BattleServiceResult pattern

**Description:**
Both locations aggregate errors from multiple sources:
```python
final_result = ValidationResult(True)
for rule in self.addition_rules:
    res = rule.validate(ship, component, layer_type)
    if not res.is_valid:
        final_result.is_valid = False
        final_result.errors.extend(res.errors)
return final_result
```

**Assessment:**
This is a standard aggregation pattern. The ValidationResult class from `game.core.validation` is already shared. The BattleServiceResult is a different domain object with different fields (engine, success vs is_valid).

**Action:** NONE REQUIRED. These are different result types for different domains. Consolidation would create inappropriate coupling.

---

### DUP-SIM-005
**Severity:** INFO
**Type:** Design Pattern Observation
**Pattern:** God-class decomposition (POSITIVE)

**Locations:**
1. `game/simulation/entities/ship.py` -> delegates to:
   - `game/simulation/entities/ship_stats.py` (ShipStatsCalculator)
   - `game/simulation/entities/ship_combat_engine.py` (ShipCombatEngine)
   - `game/simulation/entities/ship_serialization.py` (ShipSerializer)
   - `game/simulation/entities/ship_stat_querier.py` (ShipStatQuerier)
   - `game/simulation/entities/ship_validator_helper.py` (ShipValidatorHelper)
   - `game/simulation/entities/ship_formation.py` (ShipFormation)

2. `game/simulation/components/component.py` -> delegates to:
   - `game/simulation/components/ability_manager.py` (AbilityManager)
   - `game/simulation/components/modifier_manager.py` (ModifierManager)
   - `game/simulation/components/component_stats_calculator.py` (ComponentStatsCalculator)
   - `game/simulation/components/component_resource_manager.py` (ComponentResourceManager)
   - `game/simulation/components/component_health_manager.py` (ComponentHealthManager)

**Description:**
Ship and Component classes use composition to delegate specialized behavior to helper classes. This might appear as "fragmentation" but is actually proper separation of concerns.

**Assessment:**
This is **excellent architecture**. Each helper class:
- Has a single responsibility
- Is independently testable
- Reduces cognitive load
- Allows for specialized optimization

**Action:** DOCUMENT AS EXEMPLAR. This pattern should be followed for future large classes.

---

### DUP-SIM-006
**Severity:** INFO
**Type:** Design Pattern Observation
**Pattern:** Registry pattern consistency (POSITIVE)

**Locations:**
1. `game/simulation/components/abilities/__init__.py` - ABILITY_REGISTRY
2. `game/simulation/components/component.py` - Uses RegistryManager.components
3. `game/simulation/services/registry_loader.py` - Centralized loading

**Description:**
The codebase consistently uses a registry pattern for extensible types (abilities, components, modifiers, vehicle classes). Registration happens in `__init__.py` files with explicit mappings.

**Assessment:**
This is proper extensibility architecture. Each registry:
- Has a single source of truth
- Uses dependency injection for testability
- Supports data-driven configuration

**Action:** DOCUMENT AS EXEMPLAR.

---

## Areas with NO Duplication Found

The following patterns were specifically checked and found to have NO duplication:

1. **Physics constants** - Single source at `game/simulation/physics_constants.py` (K_SPEED, K_THRUST, K_TURN)

2. **Formula evaluation** - Single implementation at `game/simulation/formula_system.py` (safe_evaluate_math_formula)

3. **Stat key definitions** - Single enum at `game/simulation/components/abilities/stat_keys.py` (StatKey)

4. **Validation base classes** - Template method pattern at `game/simulation/validation/base.py` eliminates guard clause duplication

5. **Battle state serialization** - Single implementation at `game/simulation/battle_state.py` (to_dict/from_dict patterns)

6. **Projectile management** - Single implementation at `game/simulation/projectile_manager.py`

7. **Resource management** - Clean separation between:
   - `game/simulation/systems/resource_manager.py` (ResourceRegistry, ResourceState)
   - `game/simulation/components/component_resource_manager.py` (per-component consumption)

---

## Recommendations

### No Immediate Action Required

The simulation layer is well-architected with minimal duplication. The minor findings are:
- Intentional structural patterns (ability inheritance)
- Necessary boilerplate for extensibility systems
- Standard aggregation patterns

### Future Considerations

1. **Document the decomposition pattern** - The Ship/Component delegation patterns are exemplary and should be documented for future maintainers.

2. **Monitor ability class growth** - As more abilities are added, consider whether additional shared utilities would help, but do not pre-optimize.

3. **Keep DI strict** - The `PROJ-50` strict dependency injection pattern is working well. Continue requiring explicit registry injection.

---

## Conclusion

**No refactoring action needed.** The simulation layer demonstrates mature, DRY-conscious architecture with appropriate use of inheritance, composition, and dependency injection. The patterns flagged as MINOR are intentional design choices that enable extensibility and testability.

