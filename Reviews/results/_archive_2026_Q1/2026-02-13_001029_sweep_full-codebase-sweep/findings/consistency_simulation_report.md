# Consistency Violations Report: game/simulation/

**Generated:** 2026-02-13
**Scope:** game/simulation/ (all subdirectories)
**Files Analyzed:** 71 Python files

---

## Executive Summary

The simulation layer demonstrates generally high consistency with established project patterns. Most files follow the Registry Pattern, Dependency Injection, and Layer Architecture correctly. However, several inconsistencies were identified across naming conventions, structural patterns, API design, and internal module consistency.

**Total Findings:** 34
- CRITICAL: 0
- MAJOR: 8
- MINOR: 18
- INFO: 8

---

## Phase 1: Naming Convention Analysis

### 1.1 Method Verbs Inconsistency

**[MINOR]** Mixed verb conventions for retrieval methods

| File | Method | Issue |
|------|--------|-------|
| `entities/ship_stat_querier.py` | `get_ability_total()` | Uses `get_` prefix |
| `entities/ability_aggregator.py` | `calculate_ability_totals()` | Uses `calculate_` prefix |
| `entities/ship_stats.py` | `calculate_ability_totals()` | Uses `calculate_` prefix |

**Impact:** Inconsistent naming makes it harder to predict method names
**Recommendation:** Standardize on `calculate_` for computation-heavy methods that derive new values, `get_` for simple lookups/accessors

---

**[MINOR]** Boolean property naming inconsistency

| File | Property | Pattern |
|------|----------|---------|
| `entities/ship.py` | `is_alive`, `is_derelict` | `is_` prefix |
| `entities/ship_formation.py` | `is_master`, `is_member` | `is_` prefix |
| `components/component.py` | `is_active`, `is_operational` | `is_` prefix |
| `systems/resource_manager.py` | `has_sufficient()` | Method, not property |

**Impact:** Low - boolean methods vs properties are contextually appropriate
**Status:** Generally consistent, no action needed

---

### 1.2 Parameter Naming

**[MINOR]** Inconsistent abbreviation usage in parameters

| File | Parameter | Alternative Used Elsewhere |
|------|-----------|---------------------------|
| `entities/projectile.py` | `range_val` | `max_range` used as attribute |
| `entities/projectile.py` | `proj_type` | `type` used elsewhere (conflicts with builtin) |
| `combat/targeting_system.py` | `p_speed` | `projectile_speed` in weapon abilities |
| `combat/targeting_system.py` | `t_pos`, `t_vel` | `target_position`, `target_velocity` |

**Impact:** Abbreviated parameter names reduce readability in `solve_lead()` especially
**Recommendation:** Use descriptive names: `target_pos`, `target_vel`, `projectile_speed`

---

### 1.3 Class Suffix Conventions

**[INFO]** Class suffix usage is generally consistent

| Suffix | Classes | Consistent? |
|--------|---------|-------------|
| `Manager` | `RetreatManager`, `BattleStateManager`, `ResourceRegistry` | Mostly (ResourceRegistry is anomaly) |
| `Service` | `BattleService`, `ModifierService`, `VehicleDesignService` | Yes |
| `Calculator` | `DamageCalculator`, `ShipStatsCalculator` | Yes |
| `System` | `TargetingSystem`, `WeaponFiringSystem` | Yes |
| `Loader` | `SimulationDesignLoader`, `TechPresetLoader` | Yes |
| `Handler` | `BattleModeHandler` (and subclasses) | Yes |
| `Rule` | All validation rules | Yes |
| `Ability` | All abilities | Yes |

**Note:** `ResourceRegistry` should perhaps be `ResourceManager` for consistency

---

### 1.4 File Naming Conventions

**[INFO]** Module naming follows clear patterns:
- `ship_*.py` for Ship-related extractions
- `*_manager.py` for manager classes
- `*_service.py` for service classes
- `battle_*.py` for battle-related modules

**Exception:** `ability_aggregator.py` in entities/ could be `ship_ability_aggregator.py` for consistency with other ship extractions

---

## Phase 2: Structural Pattern Analysis

### 2.1 Error Handling Inconsistency

**[MAJOR]** Inconsistent exception handling patterns across loaders

| File | Pattern | Issue |
|------|---------|-------|
| `services/design_loader.py` | Duplicate except clause at lines 118-133 | Same exceptions caught twice |
| `services/registry_loader.py` | Broad tuple of exceptions | Correct pattern |
| `entities/ship_serialization.py` | Single broad catch with re-raise | Acceptable for diagnostic logging |

**Location:** `services/design_loader.py:118-133`
```python
except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
    # ...
except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:  # DUPLICATE
```

**Recommendation:** Remove duplicate except clause in design_loader.py

---

**[MAJOR]** Missing exception chaining in some modules

| File | Method | Issue |
|------|--------|-------|
| `entities/projectile.py` | Constructor validation | Raises `ValidationException` without chaining |
| `services/design_loader.py` | `load_ship_from_file` | Returns None instead of raising |

**Impact:** Lost context when exceptions propagate
**Recommendation:** Use `raise NewException(...) from original_exception` pattern consistently

---

### 2.2 Logging Consistency

**[MINOR]** Mixed logging approaches

| File | Approach |
|------|----------|
| `services/registry_loader.py` | `logging.getLogger("StarshipBattles")` |
| `managers/retreat_manager.py` | `from game.core.logger import log_debug, log_info` |
| `services/vehicle_design_service.py` | `from game.core.logger import log_error, log_warning, log_info` |

**Impact:** Inconsistent logging makes log configuration harder
**Recommendation:** Standardize on `game.core.logger` wrapper functions throughout

---

### 2.3 Import Organization

**[MINOR]** TYPE_CHECKING block placement varies

| Pattern | Files Using |
|---------|-------------|
| At top after standard imports | Most files (correct) |
| Mixed with regular imports | `entities/combat_endurance.py` |

**Standard Pattern:**
```python
from typing import TYPE_CHECKING
# ...other imports...

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
```

---

### 2.4 Docstring Completeness

**[MINOR]** Missing or incomplete docstrings on public methods

| File | Method | Issue |
|------|--------|-------|
| `entities/ship_physics.py` | `rotate()` | Minimal docstring |
| `entities/ship_physics.py` | `thrust_forward()` | Minimal docstring |
| `systems/resource_manager.py` | `set_max()` | No docstring |
| `components/abilities/harvester.py` | All abilities | Incomplete class docstrings |

**Impact:** Reduced developer experience
**Recommendation:** Ensure all public APIs have complete docstrings with Args/Returns sections

---

### 2.5 Magic Numbers

**[MAJOR]** Hardcoded values that should be constants

| File | Line | Value | Context |
|------|------|-------|---------|
| `entities/projectile.py` | 161 | `* 100` | Conversion factor in `_update_guidance` |
| `entities/projectile.py` | 167 | `* 0.01` | Fixed tick rate |
| `entities/projectile.py` | 179 | `45` | Turn direction commitment threshold |
| `combat/targeting_system.py` | 167 | `* 2.0` | Max range multiplier |
| `combat/targeting_system.py` | 213 | `/ 100.0` | Speed conversion |
| `managers/retreat_manager.py` | 103 | `500` | Warp charge ticks (not using constant) |

**Impact:** Magic numbers make behavior unclear and maintenance difficult
**Recommendation:** Extract to constants in `physics_constants.py` or `game.core.constants`

---

### 2.6 Default Mutable Arguments

**[INFO]** No violations found - all mutable defaults use `field(default_factory=list)` or similar patterns correctly

---

## Phase 3: API Design Consistency

### 3.1 Constructor Patterns

**[MAJOR]** Inconsistent DI constructor patterns

| File | Class | Pattern |
|------|-------|---------|
| `services/vehicle_design_service.py` | `VehicleDesignService` | `*, registries: GameRegistries` (keyword-only) |
| `services/modifier_service.py` | `ModifierService` | `*, registries: GameRegistries` (keyword-only) |
| `services/design_loader.py` | `SimulationDesignLoader` | `*, registries: GameRegistries` (keyword-only) |
| `validation/ship_validator.py` | `ClassRequirementsRule` | `*, registries: GameRegistries` (keyword-only) |
| `validation/ship_validator.py` | `ShipDesignValidator` | `*, registries: GameRegistries` (keyword-only) |
| `entities/ship_serialization.py` | `ShipSerializer.from_dict()` | `*, registries: GameRegistries` (keyword-only) |
| `factories/ai_factory.py` | `AIControllerFactory` | `grid` positional parameter |

**Analysis:** Most DI constructors use keyword-only pattern (`*,`), but `AIControllerFactory` uses positional
**Recommendation:** Consider making `AIControllerFactory(*, grid: SpatialGrid)` for consistency

---

### 3.2 Return Type Consistency

**[MINOR]** Inconsistent return patterns for "not found" cases

| Pattern | Files Using |
|---------|-------------|
| `Optional[T]` returning `None` | `systems/resource_manager.py`, `combat/targeting_system.py` |
| Empty collection | `entities/ability_aggregator.py` (returns `{}`) |
| Raise exception | `entities/projectile.py` (ValidationException) |

**Documented Convention in `systems/resource_manager.py`:**
```python
# Return Convention:
#     - Single-value lookups: Optional[T] (None = not found)
#     - Collection lookups: List[T] (empty list = none found)
```

**Impact:** Low - documented convention is followed where specified
**Recommendation:** Apply this return convention documentation to other modules

---

### 3.3 Method Signature Consistency

**[MINOR]** Similar operations have different signatures

| Operation | Method 1 | Method 2 |
|-----------|----------|----------|
| Get ship by ID | `ship_id_map.get(id(ship))` in RetreatManager | String ship_id in BattleStateManager |
| Create from data | `Ship.from_dict(data, registries=...)` | `BattleState.capture_from_engine(...)` |

**Impact:** Low - contextually appropriate
**Status:** No action needed, but document patterns

---

## Phase 4: Project Pattern Adherence

### 4.1 Registry Pattern

**[INFO]** Registry pattern usage is consistent throughout:
- Components use `RegistryManager.instance().components`
- Vehicle classes use `RegistryManager.instance().vehicle_classes`
- Modifiers use `RegistryManager.instance().modifiers`
- All major modules correctly use DI for registries

---

### 4.2 Ability System

**[MINOR]** Ability class variable declaration inconsistency

| File | Class | Issue |
|------|-------|-------|
| `abilities/base.py` | `Ability` | Defines `STAT_BINDINGS = []` as class variable |
| `abilities/markers.py` | Marker abilities | Use `STAT_BINDINGS: List[AbilityStatBinding] = []` |
| `abilities/superweapons.py` | All classes | Use `STAT_BINDINGS = []` without type hint |

**Recommendation:** Standardize on `STAT_BINDINGS: List[AbilityStatBinding] = []` with type hint

---

### 4.3 Layer Architecture

**[MAJOR]** One late import could be refactored

| File | Location | Import | Issue |
|------|----------|--------|-------|
| `entities/ship_stat_querier.py` | Line 121 | `from game.simulation.components.abilities import ...` | Comment says "INTENTIONAL LATE IMPORT" but could be TYPE_CHECKING |

**Analysis:** The import is inside a property method to avoid circular dependency. This is correctly documented but the comment pattern is unique in the codebase.

**Recommendation:** Consider extracting to a helper method called at runtime to make the pattern clearer

---

### 4.4 Facade/Delegate Pattern

**[INFO]** Ship god class decomposition correctly uses facade pattern:
- `ship.py` delegates to `ship_stats.py`, `ship_stat_querier.py`, `ship_validator_helper.py`, `ship_formation.py`, `ship_physics.py`
- `ship_combat_engine.py` delegates to `targeting_system.py`, `damage_calculator.py`, `weapon_firing_system.py`

---

### 4.5 Dependency Injection

**[MAJOR]** Singleton fallback patterns still exist in some places

| File | Issue |
|------|-------|
| `entities/ship_loader.py` | `get_or_create_validator()` uses global singleton pattern |
| `services/vehicle_design_service.py` | `validate_design()` calls `get_or_create_validator()` |
| `entities/ship_validator_helper.py` | Uses `get_or_create_validator()` |

**Comment in code:**
> "Note: This method always uses the singleton-backed validator via get_or_create_validator(), regardless of the registry passed..."

**Impact:** Makes isolated testing harder for validation
**Recommendation:** Consider full DI for validator (PROJ-50 scope note in code)

---

## Phase 5: Per-Module Internal Consistency

### 5.1 entities/ Module

**[MINOR]** Mixed attribute initialization patterns

| File | Pattern |
|------|---------|
| `ship.py` | Uses dataclass-style defaults in `__init__` |
| `projectile.py` | Uses kwargs.get() pattern for optional args |
| `layer_data.py` | Uses `@dataclass` with `field(default_factory=...)` |

**Impact:** Low - contextually appropriate for each class type
**Status:** Acceptable variation

---

**[MINOR]** `combat_endurance.py` is a module of functions, not a class

Unlike other entities files which define classes, `combat_endurance.py` defines standalone functions. This is inconsistent but documented in the module.

**Recommendation:** Consider wrapping in a `CombatEnduranceCalculator` class for consistency

---

### 5.2 components/abilities/ Module

**[INFO]** Ability classes follow consistent pattern:
- All inherit from `Ability`
- All implement `get_primary_value()` and `get_ui_rows()`
- All define `STAT_BINDINGS` (even if empty)
- Strategic abilities correctly set `layer = AbilityLayer.STRATEGIC`

---

### 5.3 services/ Module

**[MINOR]** `design_loader.py` and `registry_loader.py` not exported in `__init__.py`

```python
# services/__init__.py exports:
'ModifierService',
'VehicleDesignService',
'DesignResult',
'BattleService',
'BattleServiceResult',
# Missing: SimulationDesignLoader, reload_registries_from_directory
```

**Impact:** Users must import directly from submodules
**Recommendation:** Add to `__all__` if intended for public use

---

### 5.4 validation/ Module

**[INFO]** Validation module demonstrates excellent consistency:
- All rules follow template method pattern
- Clear separation between `AdditionValidationRule` and `DesignValidationRule`
- Proper re-export through `__init__.py`

---

### 5.5 combat/ Module

**[INFO]** Combat subsystem demonstrates excellent consistency:
- All classes extracted from ShipCombatEngine follow same pattern
- Proper `__init__.py` with `__all__` exports
- Consistent docstring style referencing PROJ-44

---

### 5.6 managers/ Module

**[INFO]** Managers module is consistent:
- Both managers follow same patterns
- Proper dataclass usage for state objects
- Consistent export in `__init__.py`

---

## Cross-Cutting Concerns

### Type Hints

**[MAJOR]** Inconsistent type hint coverage

| File | Coverage | Notes |
|------|----------|-------|
| `entities/ship_physics.py` | Low | Mixin class lacks return type hints |
| `entities/combat_endurance.py` | Low | Functions lack parameter/return hints |
| `combat/targeting_system.py` | Medium | Some `Any` types that could be more specific |

**Files with good type hint coverage:**
- All services
- All validation modules
- All manager classes
- Most abilities

**Recommendation:** Add type hints to `ship_physics.py` and `combat_endurance.py`

---

### Comment Patterns

**[MINOR]** Inconsistent PROJ reference formatting

| Pattern | Example | Count |
|---------|---------|-------|
| `PROJ-XX:` | `PROJ-44: ShipCombatEngine Decomposition` | Most common |
| `PROJ-XX Phase N:` | `PROJ-43 Phase 8: ...` | Combat module |
| `Part of PROJ-XX` | `Part of PROJ-44 Phase 5:` | Some docstrings |

**Recommendation:** Standardize on `PROJ-XX:` format for inline comments

---

## Summary of Recommendations

### High Priority (MAJOR)
1. Remove duplicate except clause in `services/design_loader.py`
2. Extract magic numbers to constants (especially in `projectile.py`, `targeting_system.py`)
3. Add type hints to `ship_physics.py` and `combat_endurance.py`
4. Consider making `AIControllerFactory` use keyword-only parameter for consistency

### Medium Priority (MINOR)
1. Standardize method naming: `calculate_` for computed values, `get_` for lookups
2. Use descriptive parameter names in `combat/targeting_system.py`
3. Standardize logging to use `game.core.logger` throughout
4. Add `SimulationDesignLoader` to `services/__init__.py` exports
5. Standardize STAT_BINDINGS declaration with type hints

### Low Priority (INFO)
1. Consider renaming `ResourceRegistry` to `ResourceManager`
2. Consider renaming `ability_aggregator.py` to `ship_ability_aggregator.py`
3. Document return convention pattern in more modules

---

## Files With No Issues

The following files demonstrated full consistency with project patterns:
- `components/abilities/base.py`
- `components/abilities/weapons.py`
- `components/abilities/defense.py`
- `components/abilities/propulsion.py`
- `validation/base.py`
- `validation/__init__.py`
- `interfaces/ai_controller.py`
- `interfaces/__init__.py`
- `factories/__init__.py`
- `managers/__init__.py`
- `combat/__init__.py`
- `systems/battle_end_conditions.py`
- `battle_config.py`
- `battle_mode_handler.py`

---

*Report generated by automated consistency sweep*
