# Duplication & Fragmentation Report: game/simulation/

**Shard**: `game/simulation/`
**Files Scanned**: 72
**Date**: 2026-02-13

---

## Executive Summary

The `game/simulation/` directory has been designed with good separation of concerns and follows established patterns. However, several areas of code duplication and structural repetition were identified:

- **MAJOR**: Ability class boilerplate pattern repeated across 20+ ability classes
- **MINOR**: Defensive/validation pattern duplication in validator rules
- **INFO**: Battle mode handler pattern (intentional Strategy pattern application)
- **INFO**: Superweapon ability classes (intentional marker pattern with identical structure)

The codebase shows evidence of deliberate refactoring (Phase 12 validation, PROJ-44 decomposition, PROJ-88 god class extraction) that has improved structure, but the ability system remains the largest source of structural duplication.

---

## Findings

### Phase 1: Structural Duplication

#### MAJOR: Ability Class Boilerplate Pattern

**Files Affected**:
- `game/simulation/components/abilities/propulsion.py` (lines 7-166)
- `game/simulation/components/abilities/resources.py` (lines 9-230)
- `game/simulation/components/abilities/defense.py` (lines 8-126)
- `game/simulation/components/abilities/crew.py` (lines 8-92)
- `game/simulation/components/abilities/cargo.py` (lines 13-78)
- `game/simulation/components/abilities/harvester.py` (lines 10-146)
- `game/simulation/components/abilities/markers.py` (lines 8-91)

**Pattern**: Nearly every ability class follows identical structural boilerplate:
```python
class SomeAbility(Ability):
    STAT_BINDINGS: List[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.SOME_MULT, 'attr', 'multiply', '_base_attr'),
    ]

    def __init__(self, component, data: Dict[str, Any]):
        super().__init__(component, data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0)
        self.attr = float(val)
        self._base_attr = self.attr

    def sync_data(self, data: Any):
        super().sync_data(data)
        val = data if isinstance(data, (int, float)) else data.get('value', 0) if isinstance(data, dict) else 0
        self.attr = float(val)
        self._base_attr = self.attr

    def recalculate(self):
        self.attr = self._base_attr * self.get_effective_stat('some_mult', 1.0)

    def get_ui_rows(self):
        return [{'label': 'Label', 'value': f"{self.attr:.0f}", 'color_hint': '#FFFFFF'}]

    def get_primary_value(self) -> float:
        return self.attr
```

**Specific Examples**:
- `CombatPropulsion`, `ManeuveringThruster`, `StrategicMovement` (propulsion.py) - identical structure, differ only in attribute names and UI labels
- `ResourceConsumption`, `ResourceStorage`, `ResourceGeneration` (resources.py) - same pattern
- `ShieldProjection`, `ShieldRegeneration` (defense.py) - same pattern
- `CrewCapacity`, `LifeSupportCapacity`, `CrewRequired` (crew.py) - same pattern

**Root Cause**: The STAT_BINDINGS system is declarative but the __init__, sync_data, recalculate, and get_ui_rows methods are all manually implemented with nearly identical logic.

**Suggested Fix**: Create a metaclass or factory that auto-generates these methods from STAT_BINDINGS declarations. The binding already contains all needed information (stat_key, attribute_name, operation, base_attribute).

---

#### MINOR: Validation Rule _do_validate Guard Clause Duplication

**Files Affected**:
- `game/simulation/validation/ship_validator.py` (lines 57-68, 110-116, 144-152)

**Pattern**: Multiple validation rules check `if layer_type not in ship.layers` at the start of _do_validate:
```python
def _do_validate(self, ship, component, layer_type) -> ValidationResult:
    result = ValidationResult(True)
    if layer_type not in ship.layers:
        # Either return early or add error
```

**Occurrences**:
- `LayerConstraintRule._do_validate` (line 60-62)
- `MountDependencyRule._do_validate` (lines 114-115)
- `LayerRestrictionDefinitionRule._do_validate` (lines 148-150)

**Root Cause**: While the template method pattern was applied (Phase 12 refactoring), the layer existence check is still manually repeated.

**Suggested Fix**: Add a `_check_layer_exists` mixin method or make the base AdditionValidationRule check layer existence in _should_validate by default.

---

### Phase 2: Semantic Duplication

#### MINOR: Data Extraction Pattern in __init__ Methods

**Files Affected**:
- All ability classes in `game/simulation/components/abilities/`

**Pattern**: The same data extraction logic appears in nearly every ability __init__:
```python
val = data if isinstance(data, (int, float)) else data.get('value', 0)
```

This pattern appears 15+ times across ability files.

**Suggested Fix**: Move this to a base class utility method:
```python
@staticmethod
def _extract_value(data: Any, key: str = 'value', default: float = 0) -> float:
    if isinstance(data, (int, float)):
        return float(data)
    return float(data.get(key, default)) if isinstance(data, dict) else default
```

---

#### MINOR: get_effective_stat Default Value Pattern

**Files Affected**:
- `game/simulation/components/abilities/base.py` (lines 165-196)
- All ability recalculate() methods

**Pattern**: Every recalculate method calls `get_effective_stat('some_mult', 1.0)` with explicit defaults, even though the base method already handles default inference from key suffix:
```python
def recalculate(self):
    self.thrust_force = self.base_thrust * self.get_effective_stat('thrust_mult', 1.0)
```

The `1.0` default is redundant since keys ending in `_mult` already default to 1.0 in the base implementation.

**Suggested Fix**: Remove explicit defaults from recalculate methods since the base implementation handles this.

---

### Phase 3: Copy-Paste Drift

#### INFO: No significant copy-paste drift detected

The codebase shows good discipline in avoiding copy-paste drift. Where patterns are repeated, they are consistent. The PROJ-44 decomposition (ShipCombatEngine -> TargetingSystem, DamageCalculator, WeaponFiringSystem) created clean separations without drift.

---

### Phase 4: Fragmented Implementations

#### MINOR: Resource Cost Evaluation Logic Split

**Files Affected**:
- `game/simulation/components/component_resource_manager.py` (lines 83-119)
- `game/simulation/formula_system.py`
- `game/simulation/components/component.py`

**Pattern**: Resource cost calculation with formula evaluation is split across multiple locations:
- `ComponentResourceManager.get_resource_cost()` handles formula evaluation inline
- `formula_system.py` provides `safe_evaluate_math_formula`
- Component stores both `evaluated_resource_cost` and raw `resource_cost`

The formula evaluation pattern (checking for `=` prefix, calling safe_evaluate_math_formula) appears in:
- `ComponentResourceManager.get_resource_cost()` (lines 113-117)
- `WeaponAbility.__init__` (lines 59-66, 77-79, 92-96)
- `WeaponAbility.sync_data` (lines 128-149)
- `WeaponAbility.get_damage` (lines 202-206)

**Suggested Fix**: Create a unified formula field class that encapsulates the "is formula or static value" check and evaluation.

---

#### INFO: Marker Ability Classes (Intentional)

**Files Affected**:
- `game/simulation/components/abilities/superweapons.py` (entire file)
- `game/simulation/components/abilities/markers.py` (entire file)

**Pattern**: Six superweapon classes and five marker classes have nearly identical structures:
```python
class SomeMarkerAbility(Ability):
    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF
    STAT_BINDINGS = []

    def __init__(self, component, data):
        super().__init__(component, data)

    def get_ui_rows(self):
        return [{'label': 'X', 'value': 'Y', 'color_hint': '#COLOR'}]

    def get_primary_value(self):
        return 0.0
```

**Assessment**: This is intentional design - marker abilities are meant to be simple presence indicators. The repetition is acceptable because:
1. Each class needs distinct import/registration for the ability registry
2. Future expansion may add class-specific behavior
3. The pattern is explicit and readable

---

#### INFO: Battle Mode Handlers (Intentional Strategy Pattern)

**Files Affected**:
- `game/simulation/combat/battle_mode_handler.py` (entire file)

**Pattern**: Four handler classes (ManualBattleModeHandler, TestBattleModeHandler, StrategyBattleModeHandler, HypotheticalBattleModeHandler) with very similar structures.

**Assessment**: This is a deliberate Strategy pattern implementation (CQ-024 fix). The repetition is intentional to:
1. Eliminate scattered mode conditionals
2. Make each mode's behavior explicit
3. Enable easy addition of new modes

---

## Statistics

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 1 |
| MINOR | 4 |
| INFO | 3 |

---

## Recommendations

### High Priority
1. **Ability Boilerplate Reduction**: Implement a metaclass or factory pattern that generates __init__, sync_data, recalculate, and get_ui_rows from STAT_BINDINGS declarations. This could reduce ~500 lines of boilerplate across ability files.

### Medium Priority
2. **Formula Field Abstraction**: Create a `FormulaField` class that unifies the "static or formula" pattern used in weapon abilities and resource costs.

3. **Base Class Utility Methods**: Add `_extract_value()` and similar utility methods to the Ability base class.

### Low Priority
4. **Validation Rule Refactoring**: Consider adding layer existence checking to the base AdditionValidationRule class.

---

## Files Reviewed

All 72 Python files in `game/simulation/` were examined:
- Core: `__init__.py`, `physics_constants.py`, `battle_state.py`, `battle_config.py`, `formula_system.py`, `projectile_manager.py`, `battle_controller.py`, `designs.py`
- Entities: `ship.py`, `ship_serialization.py`, `ship_stats.py`, `ship_loader.py`, `ship_physics.py`, `ship_stat_querier.py`, `ship_validator_helper.py`, `projectile.py`, `ability_aggregator.py`, `layer_data.py`, `ship_combat_engine.py`, `combat_endurance.py`, `ship_formation.py`
- Components: `component.py`, `modifier_manager.py`, `modifier_effects.py`, `modifier_schema.py`, `modifier_introspection.py`, `modifiers.py`, `component_constants.py`, `component_resource_manager.py`, `component_health_manager.py`, `component_stats_calculator.py`, `ability_manager.py`
- Abilities: `base.py`, `propulsion.py`, `resources.py`, `defense.py`, `weapons.py`, `crew.py`, `cargo.py`, `colonize.py`, `harvester.py`, `superweapons.py`, `markers.py`, `stat_keys.py`
- Combat: `damage_calculator.py`, `targeting_system.py`, `weapon_firing_system.py`, `battle_mode_handler.py`
- Systems: `battle_engine.py`, `resource_manager.py`, `battle_end_conditions.py`, `tech_preset_loader.py`
- Services: `battle_service.py`, `modifier_service.py`, `vehicle_design_service.py`, `design_loader.py`, `registry_loader.py`
- Managers: `retreat_manager.py`, `battle_state_manager.py`
- Validation: `base.py`, `ship_validator.py`
- Interfaces: `ai_controller.py`
- All `__init__.py` files
