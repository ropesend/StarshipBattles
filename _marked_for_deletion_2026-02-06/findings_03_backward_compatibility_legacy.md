# Backward Compatibility & Legacy Patterns

**Theme:** Deprecated code, dual registry systems, legacy format support, incomplete migrations, and backward compatibility shims.

---

## Critical Issues

### BCD-001: DUAL REGISTRY SYSTEM (IRegistryProvider vs GameRegistries)
**ID:** BCD-001
**Location:**
- `game/core/registry.py:40-74`
- `game/simulation/services/vehicle_design_service.py:56-98`
- `game/simulation/services/modifier_service.py:36-98`
- `game/simulation/entities/ship_serialization.py:113-150`

**Issue:** The codebase maintains TWO parallel dependency injection patterns:

**OLD (PROJ-27 - IRegistryProvider):**
```python
service = VehicleDesignService(registry=provider)  # Deprecated pattern
```

**NEW (PROJ-38 - GameRegistries):**
```python
service = VehicleDesignService(registries=game_registries)  # Preferred pattern
```

Multiple classes implement fallback logic:
```python
if registries is not None:
    self._registries = registries
    self._registry = None
elif registry is not None:
    self._registry = registry
    self._registries = None
else:
    try:
        self._registries = get_default_registries()
    except RuntimeError:
        self._registry = get_default_registry_provider()
```

**Impact:** Code complexity, duplicated logic in 15+ files, confusion for new developers
**Recommendation:** Complete deprecation of IRegistryProvider pattern - migrate all callers to GameRegistries
**Effort:** Complex

---

### LPH-001: Deprecated Registry Access Functions Still Widely Used
**ID:** LPH-001
**Location:** `game/core/registry.py:299-362`
**Issue:** Six utility functions (`get_component_registry()`, `get_modifier_registry()`, `get_vehicle_classes()`, `get_validator()`, `get_resource_registry()`, `get_default_registries()`) are marked as deprecated in documentation but are still actively used throughout the codebase. They emit DeprecationWarning but code paths still rely on them as fallbacks.
**Impact:** Prevents full transition to PROJ-38's dependency injection pattern. Creates dual code paths - new DI pattern alongside legacy singleton-based access. Makes it impossible to completely remove legacy registry access until all consumers migrate.
**Recommendation:** Phase 2 migration: audit all imports of deprecated functions, migrate to `GameRegistries` with DI, remove fallback paths in services, establish timeline for deprecation.
**Effort:** Complex (requires coordinated changes across 20+ files)
**Files affected:** `game/strategy/services/ship_stats_service.py`, `game/simulation/services/modifier_service.py`, `game/simulation/entities/ship.py` and others

---

### LPH-002: FleetMovementSimulator Module Deprecated but Still Importable
**ID:** LPH-002
**Location:** `game/strategy/engine/fleet_movement.py:1-13, 67-82`
**Issue:** Entire module marked as deprecated (PROJ-35). FleetMovementSimulator class emits DeprecationWarning on init but remains fully functional. Module documentation says "will be removed in a future release" but no removal timeline exists.
**Impact:** Developers might accidentally use deprecated class instead of FleetNavigationService. Parallel implementations create confusion about which is authoritative for fleet movement logic.
**Recommendation:** Remove module entirely OR establish hard deprecation deadline. If kept, add stack trace capture to track usage. Create migration script to automatically replace imports.
**Effort:** Medium (module is isolated but used in pathfinding)
**Alternative path:** `game/strategy/services/fleet_navigation_service.py` (replacement)

---

### LPH-003: Dual Static/Instance Method Pattern in ShipStatsService
**ID:** LPH-003
**Location:** `game/strategy/services/ship_stats_service.py:41-150`
**Issue:** `calculate_stats()` method uses complex parameter overloading to support both static (`ShipStatsService.calculate_stats(design_data)`) and instance usage (`service.calculate_stats(design_data)`). Method signature has 8 parameters with 3 different calling conventions documented.
**Impact:** Confusing API with four different calling patterns. Hard to maintain - changing signature affects backward compatibility. Tests must cover all patterns. Code reviewers must understand the overload detection logic (checks `isinstance(self_or_design, ShipStatsService)`).
**Recommendation:** Remove static method pattern completely. Establish factory function for migration: `from_legacy_static(design_data) -> ShipStatsService` that handles old calls gracefully, then deprecate over 2 releases.
**Effort:** Medium (need to identify all 3 calling patterns in codebase)

---

### LPH-004: Lazy Validator Proxy Pattern
**ID:** LPH-004
**Location:** `game/simulation/entities/ship.py:29-34`
**Issue:** `_ValidatorProxy` class created to defer validator initialization. Allows Ship class to use `VALIDATOR` without import-time coupling. Works but is a workaround for circular import issues rather than proper architectural fix.
**Impact:** Hidden initialization logic. Runtime behavior depends on first access. Complicates debugging (where is VALIDATOR actually coming from?). Same pattern replicated in `_ProfilerProxy` in `game/core/profiling.py:137-140`.
**Recommendation:** Resolve circular import root cause instead. Use dataclass decorators or factory methods. Replace proxy patterns with explicit DI container.
**Effort:** Complex (requires refactoring Ship class initialization)

---

### STR-001: Incomplete PROJ-35 Migration - Dual Movement Logic
**ID:** STR-001
**Location:** `game/strategy/engine/fleet_movement.py:1-331` AND `game/strategy/services/fleet_navigation_service.py:1-468`
**Issue:** PROJ-35 aimed to unify fleet movement logic, but the deprecated `FleetMovementSimulator` class (331 LOC) still exists in `/engine/` with deprecation warnings while the new `FleetNavigationService` exists in `/services/`. Both implementations provide similar path projection and calculation logic.
**Impact:**
- UI and turn engine may use different movement calculations
- Maintenance burden (code duplication across two modules)
- Risk of behavior divergence in path projection vs. execution
**Recommendation:**
1. Audit all `FleetMovementSimulator` usage to ensure all call sites migrated to `FleetNavigationService`
2. Remove deprecated `FleetMovementSimulator` entirely
3. Add integration test verifying UI projection matches turn execution
**Effort:** Medium

---

### STR-002: Type-Checking and String-Based Ship Identification
**ID:** STR-002
**Location:** `game/strategy/data/fleet.py:433-459`, `game/strategy/engine/fleet_movement.py:63-82`
**Issue:** Fleet still supports legacy string ship references mixed with modern `ShipInstance` objects. The `to_battle_ships()` method explicitly documents "Only works with ShipInstance objects - legacy strings cannot be converted." Multiple `isinstance(target, dict)` type checks scattered through pathfinding and serialization code.
**Impact:**
- Type checking spreads through codebase (fragile)
- Cannot reliably convert old fleets to battle
- Violates single responsibility (code checks types instead of polymorphism)
**Recommendation:**
1. Audit codebase for remaining string ship references
2. Implement complete migration of old save files to `ShipInstance` format
3. Remove all `isinstance(x, dict)` type checks for ship data
**Effort:** Complex

---

## Major Issues

### BCD-002: DEPRECATED REGISTRY UTILITY FUNCTIONS
**ID:** BCD-002
**Location:** `game/core/registry.py:298-361`
**Issue:** Five utility functions (`get_component_registry()`, `get_modifier_registry()`, `get_vehicle_classes()`, `get_validator()`, `get_resource_registry()`) are marked deprecated with DeprecationWarning but still widely used throughout the codebase. They emit runtime warnings on every call.
**Backward Compat Pattern:**
- Functions fallback to global RegistryManager singleton
- New pattern should use GameRegistries dependency injection
- 119 PROJ references show incomplete migration

**Recommendation:**
1. Audit all callers of these deprecated functions
2. Complete migration to GameRegistries dependency injection (PROJ-38)
3. Remove deprecated functions after verification
4. Consider keeping one compatibility layer if total migration will take multiple sprints
**Effort:** Complex (affects multiple systems)

---

### BCD-003: MODULAR SERVICE STATIC/INSTANCE METHOD OVERLOADING
**ID:** BCD-003
**Location:** `game/simulation/services/modifier_service.py:54-98`
**Issue:** ModifierService.is_modifier_allowed() supports BOTH patterns:
```python
# Static-style (legacy)
ModifierService.is_modifier_allowed('mod_id', component)

# Instance-style (new)
service = ModifierService()
service.is_modifier_allowed('mod_id', component)
```
Uses parameter introspection to detect calling pattern:
```python
if isinstance(self_or_mod_id, ModifierService):
    # Instance method call
else:
    # Static-style call
```
**Impact:** Confusing API, harder to maintain, violates single calling pattern principle
**Recommendation:** Choose one pattern (instance methods preferred), deprecate the other
**Effort:** Medium

---

### BCD-004: LEGACY COMPONENT PANEL RETENTION
**ID:** BCD-004
**Location:** `game/ui/screens/builder/legacy_components.py` (189 lines)
**File Header Indicates:**
```
Note: This file contains legacy modifier editing functionality.
Consider migration to ModifierLogic for new code.
```
This is an entire legacy UI panel that's been retained for backward compatibility.
**Recommendation:**
1. Verify all functionality exists in ModifierLogic replacement
2. Audit which code paths still use legacy_components.py
3. Migrate or remove
**Effort:** Medium

---

### BCD-005: SAVE GAME VERSION MIGRATION WITH FALLBACK
**ID:** BCD-005
**Location:** `game/strategy/systems/save_game_service.py:26-415`
**Issue:** Save system maintains compatibility with 4 previous versions:
```python
SAVE_VERSION = "2.0.0"
MIGRATABLE_VERSIONS = ["1.0.0", "1.1.0", "1.2.0", "1.9.0"]
```
Functions like `_can_migrate_version()`, `_is_compatible_version()` handle old format detection. Also has disabled migration code:
```python
# BUG-29 FIX: Do NOT migrate designs from temp folder
# SaveGameService._migrate_temp_designs(game_session, designs_folder)
```
Commented-out migration helper at line 114-147: `_migrate_temp_designs()`

**Recommendation:**
1. Decide on minimum supported version
2. Remove support for versions below that
3. Clean up disabled migration code
4. Update MIGRATABLE_VERSIONS
**Effort:** Medium

---

### LPH-005: V1/V2 Format Dual Support in Modifier Effects
**ID:** LPH-005
**Location:** `game/simulation/components/modifier_schema.py:1-50`, `game/simulation/components/modifier_effects.py:188-195`
**Issue:** Code supports both V1 (dict-based with 'special' handlers) and V2 (array-based with formulas) modifier formats. V1 is marked "deprecated: no longer supported in production" but validation still checks for it.
**Impact:** Defensive code that will never execute if all modifiers are V2 format. Creates false sense of backwards compatibility when V1 isn't actually tested or maintained.
**Recommendation:** Remove V1 format checks. Add validation to reject V1 modifiers at load time with clear error message. Document migration path for any legacy mods.
**Effort:** Simple (localized to modifier validation)

---

### LPH-006: Multiple Backward Compatibility Layers
**ID:** LPH-006
**Location:** `game/core/constants.py:29-31` (screen dimensions re-export), `game/core/validation.py:25-128` (dual construction patterns), `game/simulation/components/component_constants.py:17-19` (LayerType re-export)
**Issue:** Three separate backward compatibility shims for DisplayConfig, ValidationResult construction, and LayerType. Each adds a thin alias layer for old code patterns. Code comments explicitly say "for backward compatibility" but no deprecation timeline.
**Impact:** Makes codebase harder to understand - new developers see multiple ways to access same data. Complicates refactoring (changes need to update all entry points). No consistency in how backward compatibility is managed.
**Recommendation:** Establish compatibility policy: 2-release deprecation window with warnings. Consolidate: pick one canonical way, create adapter for legacy access, add deprecation warnings, document migration in changelog.
**Effort:** Simple (straightforward aliasing)

---

### LPH-007: Formation Data Format Migration (Lists vs Dicts)
**ID:** LPH-007
**Location:** `game/ui/screens/formation_editor.py:204-205`, `game/ui/screens/formation_editor.py:178-192`
**Issue:** Formation arrows support both legacy list format and new dict format. On load: `if isinstance(item, list): # Legacy`. On save: converts to new format but still reads old format.
**Impact:** Silent format conversion could lose metadata. Tests may not cover edge cases (half-migrated files, corrupted format detection).
**Recommendation:** One-time migration script to convert all saves. Hard error if old format detected. Add format version field to JSON.
**Effort:** Medium (need data migration utility)

---

### LPH-008: Lazy Initialization Pattern with hasattr Checks
**ID:** LPH-008
**Location:** `game/ui/screens/race_setup_screen.py:379-381`, `game/ui/screens/planet_list_window.py:887-888`, `game/ui/screens/battle_scene.py:279-280`
**Issue:** Pattern of `if not hasattr(self, 'attr_name'): initialize` used for lazy initialization across 15+ files. Creates implicit state machine. Hard to track initialization order.
**Impact:** Non-deterministic initialization order. Missing attribute might indicate uninitialized state or actual missing feature. Complicates testing (must mock entire initialization path).
**Recommendation:** Use `@property` with lazy evaluation OR explicit initialization method. Track initialized state in `__init__`. Add assertions for required attributes.
**Effort:** Medium (systematic refactoring)

---

### LPH-009: BattleEngine Legacy Paths
**ID:** LPH-009
**Location:** `game/simulation/systems/battle_engine.py:220-224, 279-281`
**Issue:** `create_battle()` and `add_ship()` methods have "Legacy path: create controllers internally (backward compatibility)" branches that still execute. Suggests new path (with pre-created controllers) not yet universally used.
**Impact:** Code handles two different controller initialization approaches. Unclear which is canonical. Tests might not cover both paths equally.
**Recommendation:** Audit all battle engine usage - count how often legacy paths execute. If <5%, remove and migrate. If common, make it the canonical path.
**Effort:** Medium (audit + selective removal)

---

### LPH-010: Proxy Properties for Backward Compatibility
**ID:** LPH-010
**Location:** `game/ui/screens/workshop_screen.py:343-366` (ship, selected_components, available_components properties all proxy to viewmodel)
**Issue:** WorkshopScreen has 4+ properties that directly delegate to viewmodel with explicit comments "for backward compatibility". These allow old code to access properties on screen instead of screen.viewmodel.
**Impact:** Duplicates interface definition. Makes refactoring dangerous - easy to change one but not the other. Creates inconsistency (some access patterns go through proxy, others direct).
**Recommendation:** Complete migration to viewmodel access. Remove proxy properties and fix all internal uses. Update external API documentation that this is the new pattern.
**Effort:** Simple (straightforward find-replace)

---

### SIM-007: Dual Support for Old/New Component System (Dependency Injection)
**ID:** SIM-007
**Location:** `game/simulation/components/component.py:79-100`, `game/simulation/entities/ship.py:38-74`, `game/simulation/battle_state.py:230-263`
**Issue:** All major classes support two initialization patterns:
  1. With registries (PROJ-38 new pattern): `Component(..., registries=GameRegistries())`
  2. Without registries (legacy): `Component(...)` then falls back to `get_default_registries()`
**Impact:** Two code paths to maintain, confusing constructor signatures, inconsistent error handling between paths.
**Recommendation:** Complete migration to PROJ-38 pattern. Phase 1: Make registries required. Phase 2: Remove fallback logic.
**Effort:** Medium

---

### STR-005: Backward Compatibility Code Scattered Everywhere
**ID:** STR-005
**Location:** `game/strategy/services/fleet_navigation_service.py:84-91`, `game/strategy/data/pathfinding.py:275-283`, `game/strategy/data/fleet.py:604-616`
**Issue:** Multiple backward compatibility patterns without central location:
- `PathSegment.to_dict()` includes legacy `'hex'` field alongside `'end'`
- `_ChaserProxy` class created just to handle NavigationState vs Fleet differences
- Fleet order deserialization handles 3+ different target formats
**Impact:** Hard to identify what's legacy vs. new; multiple code paths need maintenance
**Recommendation:**
1. Create `LegacyCompatibilityLayer` module
2. Move all backward-compat code into it (explicit, versioned)
3. Mark each compat handler with target version
**Effort:** Medium

---

## Minor Issues

### BCD-006: SHIP SERIALIZATION WITH STAT MISMATCH FALLBACK
**ID:** BCD-006
**Location:** `game/simulation/entities/ship_serialization.py:208-246`
**Issue:** Serializer includes "expected_stats" that are verified on load with auto-correction:
```python
if mismatches:
    log_warning(f"Ship '{s.name}' stats mismatch after loading!")
    for m in mismatches:
        log_warning(f"  - {m}")
```
This is a backward compatibility fallback for stats mismatch handling.
**Recommendation:**
1. Verify these stats are accurately calculated during from_dict()
2. Consider if this fallback is still needed
3. If format changed, implement explicit versioning instead
**Effort:** Medium

---

### BCD-007: BACKWARD COMPATIBILITY ALIASES IN APP.PY
**ID:** BCD-007
**Location:** `game/app.py:49-58`
**Issue:** Scene state aliases for backward compatibility:
```python
# Scene States (Aliased for compatibility)
MENU = GameState.MENU
BUILDER = GameState.BUILDER
BATTLE = GameState.BATTLE
...
```
These module-level aliases duplicate the enum values instead of using them directly.
**Recommendation:** Remove aliases, use GameState enum directly throughout codebase
**Effort:** Simple

---

### BCD-008: LEGACY CREW REQUIREMENT PATTERN
**ID:** BCD-008
**Location:** `game/ui/screens/builder/stats_config.py:67-83`
**Issue:** Helper function for extracting crew requirements from old format:
```python
def _get_legacy_crew_requirement(ship):
    """Get crew requirement from negative CrewCapacity values (legacy pattern)."""
    crew_capacity = ship.get_ability_total('CrewCapacity')
    if crew_capacity < 0:
        return abs(crew_capacity)
    return 0
```
Old components used negative CrewCapacity instead of CrewRequired ability.
**Recommendation:** Migrate all old components to use CrewRequired ability, remove this helper
**Effort:** Medium (requires component migration)

---

### BCD-009: GETATTR WITH DEFAULTS FOR BACKWARDS COMPAT
**ID:** BCD-009
**Location:** `game/simulation/entities/ship_serialization.py:41-66`
**Issue:** Multiple uses of `getattr()` with defaults for potentially-missing attributes:
```python
"vehicle_type": getattr(ship, 'vehicle_type', 'Ship'),
"strategic_movement": getattr(ship, 'total_strategic_movement', 0),
"warp_max_tonnage": getattr(ship, 'warp_max_tonnage', 0),
```
These suggest optional attributes that may not exist on all ship objects (backward compat fallback).
**Recommendation:** Make these attributes mandatory on Ship class
**Effort:** Simple

---

### BCD-010: COMPONENT FORMAT MIGRATION IN SERIALIZATION
**ID:** BCD-010
**Location:** `game/simulation/entities/ship_serialization.py:168-172`
**Issue:** Component deserialization supports TWO formats:
```python
if isinstance(c_entry, str):
    # Old format: just component ID
    comp_id = c_entry
elif isinstance(c_entry, dict):
    # New format: dict with id and modifiers
    comp_id = c_entry.get("id", "")
    modifiers_data = c_entry.get("modifiers", [])
```
This is format versioning without explicit version checking.
**Recommendation:** Standardize on dict format, handle migration explicitly
**Effort:** Medium

---

### LPH-011 through LPH-020: Various Minor Legacy Patterns
- **LPH-011:** ShipControllableAdapter wraps Ship for IControllable interface
- **LPH-012:** ShipCombatMixin is "thin facade" kept for backward compatibility during PROJ-12
- **LPH-013:** Commented "Legacy shim removed" comments without cleanup
- **LPH-014:** ComponentRef provides `from_tuple()` and `to_tuple()` for backward compatibility
- **LPH-015:** Design loader detects "Old format detected" and warns but continues
- **LPH-016:** Design selector has `show_obsolete` flag partially implemented
- **LPH-017:** `total_defense_score` aliased as `to_hit_profile` - "Legacy/Alias for UI"
- **LPH-018:** Fallback defense score calculation in collision.py
- **LPH-019:** Legacy path comments in BattleEngine controller creation
- **LPH-020:** Multiple Profiler access patterns with _ProfilerProxy

---

## Info Issues

### LPH-021: Placeholder Technology System
**ID:** LPH-021
**Location:** `game/app.py:670-671`
**Issue:** Comment says "placeholder for now - will be implemented when tech tree exists" with TODO to replace. Tech tree not yet implemented, so available_tech_ids set to empty list.
**Impact:** No actual issue - this is a known stub. Document in architecture notes rather than as TODO comment.
**Recommendation:** Create separate issue tracker item for tech tree feature. Remove TODO, replace with feature reference.
**Effort:** Simple

---

### LPH-022: Dual Module Import Prevention
**ID:** LPH-022
**Location:** `game/ui/__init__.py:8-10`
**Issue:** Comment explains "Pre-import submodules in dependency order (excluding workshop_screen due to circular import)". Circular import exists but is worked around at module load time.
**Impact:** Module initialization has hidden dependency. Changes to workshop_screen could break this.
**Recommendation:** Resolve circular import properly. Document dependency chain. Consider lazy import for workshop_screen.
**Effort:** Medium (architectural refactoring)

---

### LPH-023: Save Game Format Version Strictness
**ID:** LPH-023
**Location:** `game/strategy/systems/save_game_service.py:10, 367-370`
**Issue:** Comment explicitly states "Strict version checking (no backward compatibility)". Code rejects old save format (v1.0.0) with "old save format not supported" error.
**Impact:** Players cannot load old saves. Acceptable if documented but limits player data migration.
**Recommendation:** This is a design choice, not a bug. Document version support policy. Consider adding migration utility if needed for player base.
**Effort:** N/A (acceptable design)

---

## Top Priority Issues

1. **BCD-001/LPH-001: Dual Registry System (PROJ-38 Migration)** - 15+ files affected with fallback logic; causes deprecation warnings throughout runtime
2. **LPH-003/BCD-003: Dual Static/Instance Method Patterns** - Confusing API for multiple services
3. **LPH-002/STR-001: FleetMovementSimulator Deprecated Module** - Entire module marked for removal but still functional
4. **LPH-006: Multiple Backward Compatibility Layers** - Constants, ValidationResult, LayerType all have re-exports without timeline
5. **BCD-005: Save File Version Migration** - Supports 4 old formats unnecessarily with disabled migration code

---

## Incomplete PROJ Migrations

| PROJ | Status | Description |
|------|--------|-------------|
| PROJ-12 | Incomplete | Ship class decomposition - mixins still in place |
| PROJ-27 | Deprecated | IRegistryProvider pattern - still used |
| PROJ-35 | Incomplete | Fleet movement unification - FleetMovementSimulator still exists |
| PROJ-38 | In Progress | GameRegistries DI migration - deprecated functions still active |
| PROJ-41 | Blocking | Fleet/ShipInstance integration - _apply_results_to_fleet is `pass` |
