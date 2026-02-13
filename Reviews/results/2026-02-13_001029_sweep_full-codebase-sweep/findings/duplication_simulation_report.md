# Duplication & Fragmentation Report: game/simulation/

**Scan Date:** 2026-02-13
**Agent:** Duplication & Fragmentation Sweep Agent
**Scope:** `game/simulation/` (all subdirectories)
**Files Scanned:** 72 Python files

---

## Executive Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| MAJOR | 4 |
| MINOR | 5 |
| INFO | 3 |

**Total Issues Found:** 13

---

## Top 5 Priority Issues

1. **[CRITICAL] Duplicate Exception Handling Pattern in design_loader.py** - Unreachable code block with identical exception types
2. **[MAJOR] Ability Lookup Pattern Duplication** - Same pattern repeated across ship.py, component.py, and multiple ability files
3. **[MAJOR] Resource Type Iteration Duplication** - ResourceStorage/ResourceGeneration aggregation patterns duplicated in ship_stats.py
4. **[MAJOR] Ship Design Helper Pattern Fragmentation** - Similar helper initialization patterns across ship_stat_querier.py, ship_validator_helper.py, ship_physics.py
5. **[MAJOR] Modifier Validation Logic Spread** - Modifier validation scattered across modifier_schema.py, modifier_service.py, and modifier_effects.py

---

## Findings

### CRITICAL

#### DUP-SIM-001: Duplicate Exception Handling Block in design_loader.py

**File:** `C:\Dev\Starship Battles\game\simulation\services\design_loader.py`
**Lines:** 118-133

**Description:**
The `load_ship_from_file` method has duplicate exception handling blocks where the second block (lines 130-133) handles the same exception types as earlier blocks (lines 118-129), making it unreachable code.

**Code Pattern:**
```python
# Lines 118-129: First exception handlers
except json.JSONDecodeError as e:
    log_error(f"SimulationDesignLoader: Invalid JSON in {file_path}: {e}")
    return None, f"Failed to load design: Invalid JSON format"
except (KeyError, TypeError, ValueError) as e:
    log_error(f"SimulationDesignLoader: Invalid design data in {file_path} - {type(e).__name__}: {e}")
    return None, f"Failed to load design: Invalid design data"
except OSError as e:
    log_error(f"SimulationDesignLoader: I/O error loading {file_path}: {e}")
    return None, f"Failed to load design: {str(e)}"
# Lines 130-133: UNREACHABLE - duplicate exception types
except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
    log_error(f"SimulationDesignLoader: Failed to load design from {file_path} - {type(e).__name__}: {e}")
    return None, f"Failed to load design: {str(e)}"
```

**Impact:** Code quality issue, unreachable dead code, maintenance confusion.

**Recommendation:** Remove the second (unreachable) exception block at lines 130-133.

---

### MAJOR

#### DUP-SIM-002: Ability Lookup Pattern Duplication

**Files:**
- `C:\Dev\Starship Battles\game\simulation\entities\ship.py` (lines 585-610)
- `C:\Dev\Starship Battles\game\simulation\components\component.py` (lines 192-231)
- `C:\Dev\Starship Battles\game\simulation\entities\ship_stat_querier.py`

**Description:**
The pattern for looking up abilities by name appears in multiple forms across the codebase with slight variations. Ship.get_total_ability_value(), Ship.get_ability_total(), Component.get_abilities(), and ShipStatQuerier all implement variations of the same concept.

**Code Patterns:**
```python
# ship.py
def get_total_ability_value(self, ability_name: str, operational_only: bool = True) -> float:
    return self.stat_querier.get_total_ability_value(ability_name, operational_only)

def get_ability_total(self, ability_name: str) -> Union[float, int, bool]:
    return self.stat_querier.get_ability_total(ability_name)

# component.py - Three methods with similar logic
def get_abilities(self, ability_name: str):
    if hasattr(self, '_ability_index') and ability_name in self._ability_index:
        return list(self._ability_index[ability_name])
    return AbilityManager.get_abilities(ability_name, self.ability_instances)

def get_ability(self, ability_name: str):
    if hasattr(self, '_ability_index') and ability_name in self._ability_index:
        abilities = self._ability_index[ability_name]
        return abilities[0] if abilities else None
    return AbilityManager.get_ability(ability_name, self.ability_instances)

def has_ability(self, ability_name: str):
    if hasattr(self, '_ability_index') and ability_name in self._ability_index:
        return len(self._ability_index[ability_name]) > 0
    return AbilityManager.has_ability(ability_name, self.ability_instances, self.abilities)
```

**Impact:** Maintenance burden - changes to ability lookup semantics require updates in multiple places.

**Recommendation:** Consider consolidating the ability lookup interface to reduce the number of similar methods. The `_ability_index` fast-path check is duplicated in all three methods - could be extracted.

---

#### DUP-SIM-003: Resource Aggregation Pattern Duplication

**File:** `C:\Dev\Starship Battles\game\simulation\entities\ship_stats.py`
**Lines:** 279-300 (`_aggregate_resource_abilities`)

**Description:**
The resource aggregation logic for ResourceStorage and ResourceGeneration follows a repetitive pattern that checks resource type and adds to accumulators. Similar patterns exist in multiple places.

**Code Pattern:**
```python
# Repeated if-elif chain for each resource type
if res_type == ResourceType.FUEL:
    acc['max_fuel'] += max_amt
elif res_type == ResourceType.AMMO:
    acc['max_ammo'] += max_amt
elif res_type == ResourceType.ENERGY:
    acc['max_energy'] += max_amt

# Same pattern for generation
if res_type == ResourceType.ENERGY:
    acc['energy_gen'] += rate
elif res_type == ResourceType.AMMO:
    acc['ammo_gen'] += rate
```

**Impact:** If a new resource type is added, multiple switch-case blocks need updating.

**Recommendation:** Consider a data-driven approach where resource types map to accumulator keys, eliminating the need for explicit if-elif chains.

---

#### DUP-SIM-004: Ship Helper Class Initialization Pattern

**Files:**
- `C:\Dev\Starship Battles\game\simulation\entities\ship.py` (lines 240-252)
- `C:\Dev\Starship Battles\game\simulation\entities\ship_stat_querier.py`
- `C:\Dev\Starship Battles\game\simulation\entities\ship_validator_helper.py`
- `C:\Dev\Starship Battles\game\simulation\entities\ship_physics.py`

**Description:**
Multiple helper classes follow the same pattern: lazy initialization with property, stored reference to ship. This is a minor structural duplication but represents consistent architecture.

**Code Pattern:**
```python
# In ship.py
@property
def stat_querier(self) -> ShipStatQuerier:
    if self._stat_querier is None:
        self._stat_querier = ShipStatQuerier(self)
    return self._stat_querier

@property
def validator_helper(self) -> ShipValidatorHelper:
    if self._validator_helper is None:
        self._validator_helper = ShipValidatorHelper(self)
    return self._validator_helper
```

**Impact:** Low - this is a reasonable pattern but could benefit from a generic lazy initializer.

**Recommendation:** Consider using `functools.cached_property` or a descriptor class to reduce boilerplate.

---

#### DUP-SIM-005: Modifier Validation Logic Fragmentation

**Files:**
- `C:\Dev\Starship Battles\game\simulation\components\modifier_schema.py` (structural validation)
- `C:\Dev\Starship Battles\game\simulation\components\modifier_effects.py` (semantic validation)
- `C:\Dev\Starship Battles\game\simulation\services\modifier_service.py` (runtime validation)

**Description:**
Modifier validation is spread across three files with different concerns but overlapping responsibilities. The `modifier_schema.py` performs structural validation, while `modifier_effects.py` performs semantic validation, and `modifier_service.py` performs runtime applicability checks.

**Code Patterns:**
```python
# modifier_schema.py - validate_modifier_v2() calls modifier_effects for formula validation
formula_errors = ModifierEffectEvaluator.validate_formula(effect['formula'])

# modifier_service.py - is_modifier_allowed() performs restriction checks
if 'allow_abilities' in mod_def.restrictions:
    required = mod_def.restrictions['allow_abilities']
    has_ability = False
    for abil in required:
        if abil in component.abilities or abil in component.data.get('abilities', {}):
            has_ability = True
            break
```

**Impact:** Understanding which validation happens where requires reading multiple files. Risk of inconsistent validation.

**Recommendation:** Document the validation pipeline clearly or consolidate into a single validation entry point.

---

### MINOR

#### DUP-SIM-006: BattleModeHandler Boilerplate

**File:** `C:\Dev\Starship Battles\game\simulation\combat\battle_mode_handler.py`
**Lines:** 102-277

**Description:**
The four battle mode handlers (Manual, Test, Strategy, Hypothetical) implement nearly identical patterns with only a few boolean differences. Three of four have empty `configure()` and `apply_results()` methods.

**Code Pattern:**
```python
class ManualBattleModeHandler(BattleModeHandler):
    def configure(self, controller, config): pass
    def can_retreat(self): return False
    def can_reinforce(self): return False
    def should_clone_ships(self): return False
    def is_headless_default(self): return False
    def apply_results(self, controller, results): pass

class TestBattleModeHandler(BattleModeHandler):
    def configure(self, controller, config): pass
    def can_retreat(self): return False
    def can_reinforce(self): return False
    def should_clone_ships(self): return False
    def is_headless_default(self): return True  # Only difference
    def apply_results(self, controller, results): pass
```

**Impact:** High boilerplate-to-logic ratio. Adding a new mode requires copying significant template code.

**Recommendation:** Consider a data-driven approach where mode behavior is defined in a dict/dataclass and a single handler interprets it.

---

#### DUP-SIM-007: Ship ID Mapping Pattern in RetreatManager

**File:** `C:\Dev\Starship Battles\game\simulation\managers\retreat_manager.py`
**Lines:** 64-130, 231-267

**Description:**
Multiple methods take `ship_id_map: Dict[int, str]` parameter and perform the same lookup pattern:

**Code Pattern:**
```python
ship_id = ship_id_map.get(id(ship))
if not ship_id:
    return False, "Ship not found in battle"
if ship_id in self.retreating_ships:
    # ...
```

This pattern appears in `request_retreat()`, `cancel_retreat()`, `is_retreating()`, and `get_retreat_state()`.

**Impact:** Maintenance burden - the ship ID lookup is duplicated in every public method.

**Recommendation:** Extract the ship_id lookup to a helper method like `_get_ship_id(ship, ship_id_map) -> Optional[str]`.

---

#### DUP-SIM-008: Turret Mount Arc Lookup Duplication in ModifierService

**File:** `C:\Dev\Starship Battles\game\simulation\services\modifier_service.py`
**Lines:** 165-176, 219-230

**Description:**
The logic for finding a component's base firing arc from nested ability dicts is duplicated in `get_initial_value()` and `get_local_min_max()`.

**Code Pattern:**
```python
# Appears twice with same logic
base_arc = component.data.get('firing_arc')
if base_arc is None:
    abilities = component.data.get('abilities', {})
    for ab_name in ['ProjectileWeaponAbility', 'BeamWeaponAbility', 'SeekerWeaponAbility', 'WeaponAbility']:
        ab_data = abilities.get(ab_name, {})
        if isinstance(ab_data, dict) and 'firing_arc' in ab_data:
            base_arc = ab_data['firing_arc']
            break
```

**Impact:** Changes to firing arc lookup require updating two places.

**Recommendation:** Extract to a helper method `_get_component_base_arc(component) -> Optional[float]`.

---

#### DUP-SIM-009: Registries None Check Pattern

**Files:** Multiple files with strict DI (PROJ-50)

**Description:**
The pattern `if registries is None: raise TypeError("registries is required...")` appears in many constructors. This is intentional for strict DI but is repetitive.

**Code Pattern:**
```python
# Appears in: Ship.__init__, Component.__init__, create_component, SimulationDesignLoader.__init__,
# ShipDesignValidator.__init__, ClassRequirementsRule.__init__, ModifierService.__init__, etc.
if registries is None:
    raise TypeError("registries is required for <ClassName>")
```

**Impact:** Consistent but verbose. Low priority as this is defensive programming.

**Recommendation:** Consider a decorator `@require_registries` or base class mixin that handles this check.

---

#### DUP-SIM-010: JSON Loading Error Handling Pattern

**Files:**
- `C:\Dev\Starship Battles\game\simulation\components\component.py` (load_components_data, load_modifiers_data)
- `C:\Dev\Starship Battles\game\simulation\services\registry_loader.py`

**Description:**
Multiple JSON loading functions have similar try-except patterns for handling JSONDecodeError, KeyError, TypeError, ValueError with logging.

**Code Pattern:**
```python
try:
    data = load_json_required(file_path)
    # process data
except json.JSONDecodeError as e:
    log_error(f"Invalid JSON in {context}: {e}")
    return {}
except (KeyError, TypeError, ValueError) as e:
    log_error(f"Invalid data: {e}")
    return {}
```

**Impact:** Minor - this is reasonable defensive coding but could be consolidated.

**Recommendation:** Consider a utility function `load_and_validate_json(path, schema_validator, context_name)` that handles common error patterns.

---

### INFO

#### DUP-SIM-011: designs.py Ship Creation Pattern

**File:** `C:\Dev\Starship Battles\game\simulation\designs.py`
**Lines:** 1-69

**Description:**
The `create_brick()` and `create_interceptor()` functions follow an identical pattern: create Ship, add bridge, add specific components via for loops. This is test/example code and duplication is acceptable.

**Impact:** Low - test helper code.

**Recommendation:** None - acceptable for test fixtures.

---

#### DUP-SIM-012: TechPresetLoader Static Method Pattern

**File:** `C:\Dev\Starship Battles\game\simulation\systems\tech_preset_loader.py`

**Description:**
All methods are `@staticmethod` with no instance state. The class acts as a namespace for related functions rather than OOP.

**Impact:** None - this is a valid pattern for utility namespaces.

**Recommendation:** None - acceptable pattern.

---

#### DUP-SIM-013: Validation Rule Base Class Inheritance

**File:** `C:\Dev\Starship Battles\game\simulation\validation\ship_validator.py`

**Description:**
Multiple validation rules inherit from `DesignValidationRule` or `AdditionValidationRule` and override `_do_validate()`. This is the intended template method pattern usage, not duplication.

**Impact:** None - good design pattern usage.

**Recommendation:** None - architecture is sound.

---

## Summary Statistics

- **Files Scanned:** 72 Python files in game/simulation/
- **Total Lines Analyzed:** ~15,000+
- **Structural Duplication Issues:** 5
- **Semantic Duplication Issues:** 4
- **Copy-Paste Drift Issues:** 1
- **Fragmentation Issues:** 3

## Methodology Notes

This report was generated by exhaustively scanning all Python files in `game/simulation/` and its subdirectories, excluding test files, `__pycache__`, and generated files. Analysis focused on:

1. **Structural Duplication:** Functions/classes with similar structure
2. **Semantic Duplication:** Same concept implemented differently
3. **Copy-Paste Drift:** Code that was copied and diverged
4. **Fragmented Implementations:** Single concepts spread across files

The codebase shows evidence of recent refactoring (PROJ-12, PROJ-29, PROJ-44, PROJ-50) which has successfully decomposed the original god classes. The remaining duplication is generally minor and often represents intentional patterns (like strict DI checks).
