# Architecture and Infrastructure Findings

## File: architecture_reviewer_report.md

# Architecture Reviewer Report

## Summary
- **Total issues found:** 16
- **Critical:** 4, **Major:** 6, **Minor:** 4, **Info:** 2

---

## Critical Issues

### AR-001: Core Layer Dependency on Strategy Layer
**ID:** AR-001
**Location:** `game/core/registry.py:10` -> `game/strategy/services/ship_stats_service.py`
**Issue:** The core layer (game/core) imports from the strategy layer (game/strategy), violating the dependency hierarchy. Specifically, registry.py uses ShipStatsService in its module docstring example code.
**Impact:** Creates circular dependency risk, violates layering principle, core becomes less reusable
**Recommendation:** Move registry-strategy integration to a higher layer adapter. Keep core independent of all application layers.
**Effort:** Medium

---

### AR-002: Core Layer Dependency on Strategy Layer - Type Hints
**ID:** AR-002
**Location:** `game/core/protocols.py:37` -> `game/strategy/data/hex_math.py`
**Issue:** Core protocols module imports HexCoord type from strategy layer inside TYPE_CHECKING block. While this uses TYPE_CHECKING, it still creates a hard dependency on strategy layer internals.
**Impact:** Makes core aware of strategy implementation details, violates separation of concerns
**Recommendation:** Move HexCoord to a shared data types module or core layer
**Effort:** Medium

---

### AR-003: Engine Layer Dependency on Simulation Layer
**ID:** AR-003
**Location:** `game/engine/collision.py:56` (TYPE_CHECKING) -> `game/simulation/entities/ship.py`
**Issue:** Engine layer (core infrastructure) depends on simulation layer's Ship class, even if only in TYPE_CHECKING. Engine should be simulation-agnostic.
**Impact:** Engine cannot be reused for different simulation implementations
**Recommendation:** Use protocol-based type hints instead of concrete Ship class. Define IShip protocol in core/protocols.py
**Effort:** Medium

---

### AR-004: Excessive Deferred Imports Indicating Circular Dependencies
**ID:** AR-004
**Location:** Multiple files across strategy and simulation layers
**Issue:** 20+ late imports (inside function bodies) detected in files like:
- `game/strategy/data/fleet.py:88,110,128,573` (FleetMobilityService, ShipStatsService, ShipInstance)
- `game/strategy/engine/turn_engine.py:72,92,100,108,116,124,165` (SimulationBattleResolver, validation)
- `game/simulation/entities/ship.py:262,517,558` (Abilities, ModifierService)
- `game/simulation/systems/stats.py:20,172,173,337,429` (ResourceManager, Abilities, WeaponAbility)

**Impact:** Runtime import overhead, harder to detect import errors at startup, maintainability issues
**Recommendation:** Restructure modules to eliminate circular dependency chains. Use dependency injection to pass dependencies rather than importing them.
**Effort:** Complex

---

## Major Issues

### AR-005: UI Layer Importing Directly from Simulation Layer
**ID:** AR-005
**Location:** Multiple UI files importing simulation components
**Issue:** UI screens directly import from simulation layer:
- `game/ui/screens/battle_scene.py:23,26-27` imports BattleService, BattleController, Ship
- `game/ui/screens/build_queue_screen.py:21` imports SimulationDesignLoader
- `game/ui/hud/panels.py:15` imports ComponentStatus

**Impact:** UI tightly coupled to simulation implementation, violates MVC/MVVM principles, UI cannot be tested without simulation
**Recommendation:** Create UI adapter layer. Use facade pattern (like StrategySessionFacade) for simulation access. Pass data objects instead of domain objects.
**Effort:** Complex

---

### AR-006: Circular Import in UI Package
**ID:** AR-006
**Location:** `game/ui/__init__.py:4` (comment) and workshop_screen.py
**Issue:** Documentation explicitly states "workshop_screen is NOT eagerly imported here to avoid circular dependency with ui.builder package"
**Impact:** Forces lazy imports, complicates module initialization, test discovery issues
**Recommendation:** Refactor builder and workshop_screen to remove circular dependency. Extract shared interfaces to separate module.
**Effort:** Complex

---

### AR-007: UI Layer Importing from Strategy Layer Too Directly
**ID:** AR-007
**Location:** Multiple UI screens importing strategy data models directly
**Issue:** UI screens import strategy data structures directly:
- `game/ui/screens/build_queue_screen.py:19-20` imports Planet, DesignLibrary
- `game/ui/screens/race_setup_screen.py:23-24` imports RaceConfig, RaceLibrary
- `game/ui/screens/builder/component_ref.py:31-32` imports LayerType, Component

**Impact:** UI tightly coupled to strategy/simulation data models, API fragility, testing difficulty
**Recommendation:** Create data transfer objects (DTOs) layer. UI should work with UI-specific models, not domain models.
**Effort:** Complex

---

### AR-008: God Module - BuilderSceneGUI
**ID:** AR-008
**Location:** `game/ui/screens/builder/main.py`
**Issue:** BuilderSceneGUI class (lines 72-1200+) imports from:
- Simulation layer: Ship, VEHICLE_CLASSES, components, ShipIO, MODIFIER_REGISTRY
- AI layer: StrategyManager
- 12 distinct game module imports

**Impact:** Difficult to test, maintain, or refactor independently
**Recommendation:** Refactor to use dependency injection and facade pattern.
**Effort:** Medium

---

### AR-009: Constructor Parameter Overload - UI Components
**ID:** AR-009
**Location:** `game/ui/screens/builder/structure_list_items.py`
**Issue:** Multiple UI component classes have excessive constructor parameters (9+ params):
- `IndividualComponentItem.__init__` (9 params)
- `LayerHeaderItem.__init__` (9 params)
- `ComponentGroupItem.__init__` (10+ params)

**Impact:** Difficult to instantiate, violates Single Responsibility Principle
**Recommendation:** Use builder pattern or configuration objects.
**Effort:** Simple

---

### AR-010: Deferred Imports in Strategy Layer - Structural Issue
**ID:** AR-010
**Location:** `game/strategy/engine/turn_engine.py:37-42,72,92,100,108,116,124,165`
**Issue:** TurnEngine imports core engines at module level but then re-imports them inside methods. This indicates circular dependency or initialization order sensitivity.
**Impact:** Fragile initialization, performance degradation, maintainability
**Recommendation:** Ensure all imports are at module level. If circular, restructure to break cycle.
**Effort:** Medium

---

## Minor Issues

### AR-011: Global Singletons Overuse
**ID:** AR-011
**Location:** 30+ files using .instance() pattern
**Issue:** Extensive use of singletons for RegistryManager, SpriteManager, StrategyManager, AIController. Testing challenges and prevents proper DI migration.
**Impact:** Hard to test, violates DI principles, state sharing issues
**Recommendation:** Complete PROJ-38 migration to DI. Make .instance() private/deprecated.
**Effort:** Medium

---

### AR-012: Deprecated API Still in Heavy Use
**ID:** AR-012
**Location:** `game/core/registry.py:298-365`
**Issue:** Deprecated functions are marked with DeprecationWarning but still widely used. No actual removal deadline.
**Impact:** Legacy code paths difficult to refactor, PROJ-38 migration stalled
**Recommendation:** Set removal date (3-6 months), actively migrate consumers to GameRegistries DI pattern
**Effort:** Medium

---

### AR-013: AI Layer Cross-Cutting Concerns
**ID:** AR-013
**Location:** `game/ai/target_evaluator.py` -> `game/simulation/components/component_constants.py`
**Issue:** AI layer imports from simulation to use LayerType constant. This couples AI to simulation implementation details.
**Impact:** AI cannot be evolved independently, component changes break AI
**Recommendation:** Extract shared constants to core/constants.py or create AI-specific enum
**Effort:** Simple

---

### AR-014: Missing Public API Definition
**ID:** AR-014
**Location:** Most packages lack coherent __init__.py exports
**Issue:** Packages have inconsistent __init__.py organization. No clear public vs. private module distinction.
**Impact:** Unclear package contracts, encourages implementation import, refactoring harder
**Recommendation:** Create explicit public API in each package's __init__.py with __all__
**Effort:** Simple

---

## Info Issues

### AR-015: TYPE_CHECKING Pattern Correctly Used
**ID:** AR-015
**Location:** Various files
**Issue:** Positive finding - proper use of TYPE_CHECKING to avoid circular import issues at runtime
**Impact:** Good practice
**Recommendation:** Continue this pattern
**Effort:** N/A

---

### AR-016: Facade Pattern Implemented
**ID:** AR-016
**Location:** `game/strategy/facade/strategy_session_facade.py`
**Issue:** Positive finding - StrategySessionFacade properly encapsulates strategy layer for UI consumption
**Impact:** Reduces coupling, good separation
**Recommendation:** Expand facade pattern to other layers (SimulationFacade, AiFacade)
**Effort:** N/A

---

## Architecture Diagram

```
Current State (PROBLEMATIC):

    game/ui/
        â”œâ”€> game/strategy/ (direct imports of data models)
        â”œâ”€> game/simulation/ (direct imports of entities & services)
        â””â”€> game/core/

    game/strategy/
        â”œâ”€> game/simulation/ (via adapter layer - OK)
        â”œâ”€> game/core/ (direct imports - VIOLATION)
        â””â”€> game/engine/ (via collision.py - VIOLATION)

    game/simulation/
        â””â”€> game/core/ (OK)

    game/engine/
        â””â”€> game/simulation/ (TYPE_CHECKING - VIOLATION)

    game/core/
        â””â”€> game/strategy/ (CRITICAL VIOLATION)

Expected Dependency Flow (Top to Bottom):
1. UI (game/ui/) - depends on Strategy, Core
2. Strategy (game/strategy/) - depends on Simulation, Core, via Adapters
3. Simulation (game/simulation/) - depends on Core, Engine
4. Engine (game/engine/) - depends on Core only
5. Core (game/core/) - standalone
```

---

## Top 5 Priority Issues

1. **AR-001: Core Layer Dependency on Strategy** - Fix registry.py imports to break circular dependency chain
2. **AR-004: Excessive Deferred Imports** - Systematic refactoring needed to eliminate 20+ late imports
3. **AR-005: UI Layer Direct Simulation Import** - Decouple UI from simulation via adapter/facade pattern
4. **AR-007: UI Importing Strategy Data Models** - Implement DTO layer between UI and domain layers
5. **AR-006: Circular Import in UI Package** - Refactor workshop_screen/builder relationship

---


## File: backward_compat_detector_report.md

# Backward Compatibility Detector Report

## Summary
- **Total issues found:** 19
- **Critical:** 2, **Major:** 8, **Minor:** 6, **Info:** 3

---

## Critical Findings

### BCD-001: DUAL REGISTRY SYSTEM (IRegistryProvider vs GameRegistries)
**Severity:** CRITICAL
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

### BCD-002: DEPRECATED REGISTRY UTILITY FUNCTIONS
**Severity:** MAJOR
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

## Major Findings

### BCD-003: MODULAR SERVICE STATIC/INSTANCE METHOD OVERLOADING
**Severity:** MAJOR
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
**Severity:** MAJOR
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
**Severity:** MAJOR
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

### BCD-006: SHIP SERIALIZATION WITH STAT MISMATCH FALLBACK
**Severity:** MEDIUM
**Location:** `game/simulation/entities/ship_serialization.py:208-246`

**Issue:** Serializer includes "expected_stats" that are verified on load with auto-correction:
```python
if mismatches:
    log_warning(f"Ship '{s.name}' stats mismatch after loading!")
    for m in mismatches:
        log_warning(f"  - {m}")
```

This is a backward compatibility fallback for stats mismatch handling. The data includes:
- max_hp, max_fuel, max_energy, max_ammo
- max_speed, acceleration_rate, turn_speed, total_thrust
- armor_hp_pool, warp values, strategic movement

**Recommendation:**
1. Verify these stats are accurately calculated during from_dict()
2. Consider if this fallback is still needed
3. If format changed, implement explicit versioning instead

**Effort:** Medium

---

### BCD-007: BACKWARD COMPATIBILITY ALIASES IN APP.PY
**Severity:** MINOR
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
**Severity:** MINOR
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
**Severity:** MINOR
**Location:** `game/simulation/entities/ship_serialization.py:41-66`

Multiple uses of `getattr()` with defaults for potentially-missing attributes:
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
**Severity:** MEDIUM
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

## Lower Priority Issues

### BCD-011: MODIFIER SCHEMA V1 FORMAT SUPPORT
**File:** `game/simulation/components/modifier_schema.py`
**Issue:** Comments indicate V1 format (deprecated) still supported
**Recommendation:** Remove V1 support if migration is complete
**Effort:** Simple

### BCD-012: SHIP COMBAT DEPRECATION NOTICE
**File:** `game/simulation/entities/ship_combat.py`
**Issue:** Deprecation notice about future removal
**Recommendation:** Either remove or set timeline
**Effort:** Simple

### BCD-013: FLEET MOVEMENT MODULE DEPRECATION
**File:** `game/strategy/engine/fleet_movement.py`
**Header:** "DEPRECATED: This module is deprecated as of PROJ-35"
**Recommendation:** Remove or migrate all callers
**Effort:** Medium

### BCD-014: DISABLED BUG-29 MIGRATION CODE
**File:** `game/strategy/systems/save_game_service.py:74-77`
**Issue:** Commented-out temp design migration
**Recommendation:** Remove if no longer needed
**Effort:** Simple

### BCD-015: MODIFIER LOGIC MANDATORY MODIFIER ENFORCEMENT
**File:** `game/ui/screens/builder/modifier_logic.py:142-150`
**Issue:** ensure_mandatory_modifiers() adds missing mandatory modifiers at runtime
**Recommendation:** Ensure this is only for UI, not data model
**Effort:** Simple

---

## Top 5 Priority Issues (by Impact)

1. **DUAL REGISTRY SYSTEM (PROJ-38 Migration)** - BCD-001
   - 15+ files affected with fallback logic
   - Causes deprecation warnings throughout runtime
   - **Action:** Complete IRegistryProvider deprecation, audit 50+ callers

2. **DEPRECATED UTILITY FUNCTIONS** - BCD-002
   - 5 deprecated functions still widely used
   - Runtime warning spam on startup
   - **Action:** Migrate all callers to GameRegistries

3. **MODIFIER SERVICE DUAL CALLING PATTERN** - BCD-003
   - Parameter type introspection for backward compat
   - Confusing API for 2 calling conventions
   - **Action:** Choose instance or static pattern, standardize all callers

4. **SAVE FILE VERSION MIGRATION** - BCD-005
   - Supports 4 old formats unnecessarily
   - Disabled migration code cluttering logic
   - **Action:** Define minimum supported version, remove old code

5. **LEGACY COMPONENT PANEL** - BCD-004
   - Entire 189-line module for backward compat
   - Not actively maintained
   - **Action:** Verify replacement exists, remove if safe

---

## Recommendations Summary

1. **Immediate (Sprint 1):** Remove module-level aliases (app.py), clean up disabled code
2. **Short-term (Sprint 2-3):** Complete PROJ-38 migration, consolidate registry patterns
3. **Medium-term (Sprint 4-5):** Migrate component formats, ship serialization
4. **Long-term:** Establish minimum version policy for future backward compat decisions

All findings suggest the codebase is in active migration with partial completion. Focus should be completing PROJ-38 before adding new backward compatibility features.

---


## File: core_infrastructure_reviewer_report.md

# Core Infrastructure Reviewer Report

## Summary
- **Total Issues Found:** 12
- **Critical:** 2, **Major:** 4, **Minor:** 4, **Info:** 2

---

## Critical Issues

### CORE-001: Missing Return Type Hints on Logger Functions
**ID:** CORE-001
**Location:** `game/core/logger.py:67-80`
**Issue:** Functions `log_debug()`, `log_info()`, `log_warning()`, `log_error()`, and `set_logging()` lack return type hints (`-> None`). The Logger class methods similarly lack type hints.
**Impact:** Reduces type safety and IDE support. Makes code harder to understand and prone to misuse.
**Recommendation:** Add `-> None` return type hints to all logger functions. Add parameter type hints (`msg: str`, `enabled: bool`) and method return types to Logger class.
**Effort:** Simple

---

### CORE-002: Incomplete Type Hint Coverage in Core Registry
**ID:** CORE-002
**Location:** `game/core/registry.py:94-256`
**Issue:** RegistryManager methods like `set_validator()` lack parameter type hints. The `_validator` attribute is typed as `Any` without documentation on expected type.
**Impact:** Unclear what type of validator is expected. Makes debugging difficult when wrong types are passed.
**Recommendation:** Add type hint `validator: Optional[ShipDesignValidator]` to `set_validator()`. Document the expected validator interface in class docstring.
**Effort:** Simple

---

## Major Issues

### CORE-003: Inconsistent Singleton Pattern Implementation
**ID:** CORE-003
**Location:** `game/core/logger.py:11-18`, `game/core/registry.py:184-198`, `game/core/profiling.py:44-57`, `game/core/screenshot_manager.py:32-45`
**Issue:** Four different singleton implementations use slightly different patterns. Logger uses `__new__` with `_initialized` flag; RegistryManager and others use double-checked locking with `instance()`. Inconsistent patterns make maintenance harder.
**Impact:** Code reviewers must understand multiple patterns. Higher chance of bugs if pattern isn't correctly replicated.
**Recommendation:** Standardize all singletons to use the thread-safe double-checked locking pattern (RegistryManager/Profiler style). Consider extracting into a base class or using a decorator.
**Effort:** Medium

---

### CORE-004: Deprecated Functions Still Exported and Callable
**ID:** CORE-004
**Location:** `game/core/registry.py:37-57, 298-364`
**Issue:** Five deprecated functions (`get_component_registry()`, `get_modifier_registry()`, `get_vehicle_classes()`, `get_validator()`, `get_resource_registry()`) are in `__all__` exports and actively used in `game/core/resources.py:92` and `game/simulation/battle_state.py`. PROJ-38 deprecation not enforced; no migration timeline specified.
**Impact:** Code emits DeprecationWarnings at runtime. Migration is incomplete (battle_state.py still uses deprecated functions). No clear migration path for consumers.
**Recommendation:** Phase 2 of PROJ-38: Set deprecation deadline (e.g., next release). Update all internal usage to use DI. Add migration guide in registry docstring.
**Effort:** Medium

---

### CORE-005: Backward Compatibility Module-Level Exports Not Documented
**ID:** CORE-005
**Location:** `game/core/paths.py:89-98`
**Issue:** Module-level exports (`ROOT_DIR`, `DATA_DIR`, `ASSET_DIR`, etc.) re-export from Paths class for backward compatibility, but no comment explains why. Similarly, `game/core/constants.py:29-33` re-exports display config from DisplayConfig class without explanation.
**Impact:** New developers don't understand the migration pattern. Risk of accidental removal of backward-compat exports.
**Recommendation:** Add comments: `# Backward compatibility: prefer Paths.ROOT_DIR in new code` on line 89. Document the migration pattern in constants.py.
**Effort:** Simple

---

### CORE-006: Broad Exception Catching Without Context
**ID:** CORE-006
**Location:** `game/core/resources.py:77-79, 111-113` and `game/core/screenshot_manager.py:115-116, 216-217`
**Issue:** Bare `except Exception:` blocks suppress all errors without logging specifics. In resources.py line 77, silently falls back to defaults without logging context.
**Impact:** Makes debugging harder. Hides genuine bugs under fallback behavior.
**Recommendation:** Log exception type/message in except blocks: `except Exception as e: log_warning(f"Failed to load resources: {type(e).__name__}: {e}")`. Distinguish recoverable vs critical errors.
**Effort:** Simple

---

## Minor Issues

### CORE-007: Type Hint Inconsistency - Union vs str | (Python 3.10+)
**ID:** CORE-007
**Location:** `game/core/resources.py:22`
**Issue:** Uses `str | None` (PEP 604 style, Python 3.10+) while other files use `Optional[str]` (typing module). Inconsistent type hint style across codebase.
**Impact:** Reduces consistency. May confuse readers familiar with older typing style.
**Recommendation:** Standardize on `Optional[str]` or `str | None` project-wide. Current codebase uses `Optional`, so fix resources.py line 22.
**Effort:** Simple

---

### CORE-008: Missing Input Validation in ValidationResult
**ID:** CORE-008
**Location:** `game/core/validation.py:51-57`
**Issue:** `__post_init__` checks `if self.errors is None` but dataclass with `default_factory=list` can't be None. Defensive check is redundant.
**Impact:** Slight code smell; suggests developer wasn't confident in dataclass semantics.
**Recommendation:** Remove lines 54-57 (the None checks). Keep the docstring explaining field behavior.
**Effort:** Simple

---

### CORE-009: Inconsistent Error Messages and Formatting
**ID:** CORE-009
**Location:** `game/core/registry.py:269, 296` and `game/core/screenshot_manager.py:28`
**Issue:** Error messages vary in capitalization and punctuation. Inconsistent tone.
**Impact:** Professional polish; makes code feel less polished.
**Recommendation:** Standardize error message format across modules.
**Effort:** Simple

---

### CORE-010: Indentation Inconsistency in Frozen Check
**ID:** CORE-010
**Location:** `game/core/registry.py:175, 269`
**Issue:** Lines use single-space incorrect indentation (13 spaces instead of 12). This is a PEP 8 violation.
**Impact:** Hard to spot in review; violates PEP 8.
**Recommendation:** Fix indentation to standard 12 spaces (3 levels).
**Effort:** Simple

---

## Info Issues

### CORE-011: PROJ-38 Deprecation Status Unclear
**ID:** CORE-011
**Location:** `game/core/registry.py:1-35`
**Issue:** PROJ-38 deprecation plan documented but no deadline, migration priority, or completion criteria. Utility functions have DeprecationWarning but code actively using them isn't flagged.
**Impact:** Unclear when deprecated functions can be removed. No sense of urgency for migration.
**Recommendation:** Add to registry.py docstring: "PROJ-38 Migration Timeline: Phase 1 (done) - Add DI. Phase 2 (TODO) - Migrate internal usage. Phase 3 (TODO) - Remove deprecated functions (v2.0)".
**Effort:** Simple

---

### CORE-012: Engine Collision System Using hasattr/getattr Over Protocols
**ID:** CORE-012
**Location:** `game/engine/collision.py:109-121, 149, 157-159`
**Issue:** CollisionSystem uses `hasattr()/getattr()` checks instead of protocol-based duck typing. Protocols exist in `game/core/protocols.py` (ICombatant, IDamageable) but aren't used here.
**Impact:** Reduces type safety and IDE support. Doesn't leverage existing protocol infrastructure.
**Recommendation:** Replace hasattr checks with protocol checks or add type hints.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **CORE-002: Incomplete Type Hint Coverage** - Type safety foundation affects entire core infrastructure
2. **CORE-001: Missing Return Type Hints on Logger** - Logger is heavily used throughout codebase
3. **CORE-004: Deprecated Functions Not Enforced** - PROJ-38 migration incomplete
4. **CORE-003: Inconsistent Singleton Pattern** - Four different implementations makes codebase harder to maintain
5. **CORE-006: Broad Exception Catching** - Silently fails make debugging difficult

---

## Architecture Notes

**Dependency Injection Status (PROJ-27/38):**
- Protocol-based DI pattern well-designed (`IRegistryProvider`, `DefaultRegistryProvider`, `TestRegistryProvider`)
- PROJ-27 protocols implemented correctly in `game/core/protocols.py`
- PROJ-38 migration incomplete - deprecated utility functions still used in core code

**Singleton Pattern:**
- 4 different singleton implementations (Logger, RegistryManager, Profiler, ScreenshotManager)
- Recommend standardization for maintainability

**Configuration Management:**
- Excellent consolidation in `game/core/config.py` (centralized magic numbers)
- DisplayConfig, AIConfig, PhysicsConfig, BattleConfig well-organized

---


## File: dead_code_hunter_report.md

# Dead Code Hunter Report

## Summary
- **Total Issues Found:** 11
- **Critical:** 2, **Major:** 4, **Minor:** 5

---

## Critical Issues

### DC-001: Duplicate Battle Panel Systems
**ID:** DC-001
**Location:**
- `game/ui/hud/panels.py` (705 lines)
- `game/ui/panels/battle_panels.py` (20KB)

**Issue:** Two parallel implementations of ShipStatsPanel, SeekerMonitorPanel, and BattleControlPanel classes exist in different locations. This creates confusion about which version is canonical:
- `game/ui/hud/battle.py` imports from `game.ui.hud.panels`
- `game/ui/screens/battle_screen.py` imports from `game.ui.panels.battle_panels`

**Impact:** Code duplication, maintenance burden, potential sync issues between implementations.

**Recommendation:** Consolidate into single location (suggest `game/ui/panels/battle_panels.py` as it has more recent refactoring with `ship_stats_renderer.py` imports).
**Effort:** Medium

---

### DC-002: Stub Functions with NotImplementedError
**ID:** DC-002
**Location:** `game/ai/behaviors.py:79`
**Issue:** Base class `AIBehavior.update()` raises `NotImplementedError` but is never actually called - appears to be incomplete design pattern.
**Code:**
```python
def update(self, target: Any, strategy: Dict[str, Any]) -> None:
    """Execute behavior logic."""
    raise NotImplementedError
```
**Impact:** Dead code if subclasses override before parent is used, confusing interface contract.
**Recommendation:** Use `@abstractmethod` if truly abstract.
**Effort:** Simple

---

## Major Issues

### DC-003: Unreachable Draw Methods
**ID:** DC-003
**Location:**
- `game/ui/hud/panels.py:28` - BattlePanel.draw()
- `game/ui/panels/battle_panels.py:18` - BattlePanel.draw()

**Issue:** Base class methods raise `NotImplementedError` but should use `@abstractmethod` if truly abstract.
**Impact:** Misleading interface, potential for accidental instantiation.
**Recommendation:** Convert to `@abstractmethod`
**Effort:** Simple

---

### DC-004: Empty Service Module
**ID:** DC-004
**Location:** `game/strategy/services/__init__.py` (1 line only comment)
**Issue:** Package is empty except for comment "# Strategy services package"
**Impact:** Dead package namespace, no exports defined
**Recommendation:** Either populate with real services or delete package and import directly from submodules.
**Effort:** Simple

---

### DC-005: Unimplemented Method with TODO
**ID:** DC-005
**Location:** `game/app.py:671`
**Issue:**
```python
available_tech_ids = []  # TODO: Replace with empire.available_tech or similar
```
**Impact:** Placeholder code left in production, no available tech returned to workshop.
**Recommendation:** Implement proper empire tech tracking or remove placeholder.
**Effort:** Medium

---

### DC-006: _ValidatorProxy Never Used
**ID:** DC-006
**Location:** `game/simulation/entities/ship.py:29-34`
**Issue:** `_ValidatorProxy` class is instantiated as `VALIDATOR = _ValidatorProxy()` but the VALIDATOR constant is never referenced in the codebase. Validator is accessed directly via `get_or_create_validator()`.
**Impact:** Dead code adds maintenance burden, confuses developers.
**Recommendation:** Remove `_ValidatorProxy` class and VALIDATOR global.
**Effort:** Simple

---

## Minor Issues

### DC-007: Dead pycache Directories
**ID:** DC-007
**Location:** 36 `__pycache__` directories throughout game/
**Issue:** Compiled Python bytecode cached directories should not be in version control.
**Impact:** Bloats repository.
**Recommendation:** Add to .gitignore if not already present.
**Effort:** Simple

---

### DC-008: Empty Module Exports
**ID:** DC-008
**Location:**
- `game/ai/__init__.py` (0 bytes)
- `game/__init__.py` (0 bytes)
- `game/simulation/__init__.py` (0 bytes)

**Issue:** Package __init__ files are completely empty with no exports defined.
**Impact:** Reduces code discoverability, requires importing from submodules.
**Recommendation:** Define meaningful `__all__` exports.
**Effort:** Simple

---

### DC-009: Debug Flag Always Enabled
**ID:** DC-009
**Location:** `game/core/constants.py:56`
**Issue:**
```python
DEBUG_SCREENSHOTS = True
```
**Impact:** Debug feature cannot be toggled at runtime, potential performance issue if screenshots are continuously saved.
**Recommendation:** Make configurable or disable by default.
**Effort:** Simple

---

### DC-010: Obsolete Commented Code Reference
**ID:** DC-010
**Location:** `game/ui/screens/test_lab.py:88-99`
**Issue:** Obsolete commented code referencing non-existent `menu_screen.create_particles()` method.
**Impact:** Confusion about what code is still valid.
**Recommendation:** Remove obsolete comments.
**Effort:** Simple

---

### DC-011: Protocol Ellipsis Stubs
**ID:** DC-011
**Location:** `game/core/protocols.py` (10 instances)
**Issue:** Protocol property definitions use ellipsis (...) as placeholder implementation.
**Impact:** Acceptable for Protocols, but indicates incomplete specification.
**Recommendation:** Document expected behavior in docstrings.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **DC-001: Duplicate Panel Systems** - Critical - Consolidate to single implementation
2. **DC-005: Unfinished Tech Availability** - Major - Implement proper empire tech tracking
3. **DC-004: Empty Service Package** - Major - Delete or populate
4. **DC-002/DC-003: Stub Methods with NotImplementedError** - Major - Convert to @abstractmethod
5. **DC-006: _ValidatorProxy Never Used** - Major - Remove dead code

---

## Code Quality Observations

**Strengths:**
- Most code is actively used and maintained
- Minimal commented-out code blocks
- No wildcard imports detected (good practice)
- TYPE_CHECKING blocks used correctly for forward references

**Weaknesses:**
- Duplicate implementations create maintenance risk
- Missing @abstractmethod decorators on abstract base classes
- Unfinished TODOs left in production code
- Empty service package suggests architectural rework in progress

---


## File: legacy_pattern_hunter_report.md

# Legacy Pattern Hunter Report

## Summary
- **Total issues found:** 23
- **Critical:** 4, **Major:** 9, **Minor:** 8, **Info:** 2

---

## Findings

### CRITICAL: Deprecated Registry Access Functions Still Widely Used
**ID:** LPH-001
**Location:** `game/core/registry.py:299-362`
**Issue:** Six utility functions (`get_component_registry()`, `get_modifier_registry()`, `get_vehicle_classes()`, `get_validator()`, `get_resource_registry()`, `get_default_registries()`) are marked as deprecated in documentation but are still actively used throughout the codebase. They emit DeprecationWarning but code paths still rely on them as fallbacks.
**Impact:** Prevents full transition to PROJ-38's dependency injection pattern. Creates dual code paths - new DI pattern alongside legacy singleton-based access. Makes it impossible to completely remove legacy registry access until all consumers migrate.
**Recommendation:** Phase 2 migration: audit all imports of deprecated functions, migrate to `GameRegistries` with DI, remove fallback paths in services, establish timeline for deprecation.
**Effort:** Complex (requires coordinated changes across 20+ files)
**Files affected:** `game/strategy/services/ship_stats_service.py`, `game/simulation/services/modifier_service.py`, `game/simulation/entities/ship.py` and others

---

### CRITICAL: FleetMovementSimulator Module Deprecated but Still Importable
**ID:** LPH-002
**Location:** `game/strategy/engine/fleet_movement.py:1-13, 67-82`
**Issue:** Entire module marked as deprecated (PROJ-35). FleetMovementSimulator class emits DeprecationWarning on init but remains fully functional. Module documentation says "will be removed in a future release" but no removal timeline exists.
**Impact:** Developers might accidentally use deprecated class instead of FleetNavigationService. Parallel implementations create confusion about which is authoritative for fleet movement logic.
**Recommendation:** Remove module entirely OR establish hard deprecation deadline. If kept, add stack trace capture to track usage. Create migration script to automatically replace imports.
**Effort:** Medium (module is isolated but used in pathfinding)
**Alternative path:** `game/strategy/services/fleet_navigation_service.py` (replacement)

---

### CRITICAL: Dual Static/Instance Method Pattern in ShipStatsService
**ID:** LPH-003
**Location:** `game/strategy/services/ship_stats_service.py:41-150`
**Issue:** `calculate_stats()` method uses complex parameter overloading to support both static (`ShipStatsService.calculate_stats(design_data)`) and instance usage (`service.calculate_stats(design_data)`). Method signature has 8 parameters with 3 different calling conventions documented.
**Impact:** Confusing API with four different calling patterns. Hard to maintain - changing signature affects backward compatibility. Tests must cover all patterns. Code reviewers must understand the overload detection logic (checks `isinstance(self_or_design, ShipStatsService)`).
**Recommendation:** Remove static method pattern completely. Establish factory function for migration: `from_legacy_static(design_data) -> ShipStatsService` that handles old calls gracefully, then deprecate over 2 releases.
**Effort:** Medium (need to identify all 3 calling patterns in codebase)

---

### CRITICAL: Lazy Validator Proxy Pattern
**ID:** LPH-004
**Location:** `game/simulation/entities/ship.py:29-34`
**Issue:** `_ValidatorProxy` class created to defer validator initialization. Allows Ship class to use `VALIDATOR` without import-time coupling. Works but is a workaround for circular import issues rather than proper architectural fix.
**Impact:** Hidden initialization logic. Runtime behavior depends on first access. Complicates debugging (where is VALIDATOR actually coming from?). Same pattern replicated in `_ProfilerProxy` in `game/core/profiling.py:137-140`.
**Recommendation:** Resolve circular import root cause instead. Use dataclass decorators or factory methods. Replace proxy patterns with explicit DI container.
**Effort:** Complex (requires refactoring Ship class initialization)

---

### MAJOR: V1/V2 Format Dual Support in Modifier Effects
**ID:** LPH-005
**Location:** `game/simulation/components/modifier_schema.py:1-50`, `game/simulation/components/modifier_effects.py:188-195`
**Issue:** Code supports both V1 (dict-based with 'special' handlers) and V2 (array-based with formulas) modifier formats. V1 is marked "deprecated: no longer supported in production" but validation still checks for it.
**Impact:** Defensive code that will never execute if all modifiers are V2 format. Creates false sense of backwards compatibility when V1 isn't actually tested or maintained.
**Recommendation:** Remove V1 format checks. Add validation to reject V1 modifiers at load time with clear error message. Document migration path for any legacy mods.
**Effort:** Simple (localized to modifier validation)

---

### MAJOR: Multiple Backward Compatibility Layers
**ID:** LPH-006
**Location:** `game/core/constants.py:29-31` (screen dimensions re-export), `game/core/validation.py:25-128` (dual construction patterns), `game/simulation/components/component_constants.py:17-19` (LayerType re-export)
**Issue:** Three separate backward compatibility shims for DisplayConfig, ValidationResult construction, and LayerType. Each adds a thin alias layer for old code patterns. Code comments explicitly say "for backward compatibility" but no deprecation timeline.
**Impact:** Makes codebase harder to understand - new developers see multiple ways to access same data. Complicates refactoring (changes need to update all entry points). No consistency in how backward compatibility is managed.
**Recommendation:** Establish compatibility policy: 2-release deprecation window with warnings. Consolidate: pick one canonical way, create adapter for legacy access, add deprecation warnings, document migration in changelog.
**Effort:** Simple (straightforward aliasing)

---

### MAJOR: Formation Data Format Migration (Lists vs Dicts)
**ID:** LPH-007
**Location:** `game/ui/screens/formation_editor.py:204-205`, `game/ui/screens/formation_editor.py:178-192`
**Issue:** Formation arrows support both legacy list format and new dict format. On load: `if isinstance(item, list): # Legacy`. On save: converts to new format but still reads old format.
**Impact:** Silent format conversion could lose metadata. Tests may not cover edge cases (half-migrated files, corrupted format detection).
**Recommendation:** One-time migration script to convert all saves. Hard error if old format detected. Add format version field to JSON.
**Effort:** Medium (need data migration utility)

---

### MAJOR: Lazy Initialization Pattern with hasattr Checks
**ID:** LPH-008
**Location:** `game/ui/screens/race_setup_screen.py:379-381`, `game/ui/screens/planet_list_window.py:887-888`, `game/ui/screens/battle_scene.py:279-280`
**Issue:** Pattern of `if not hasattr(self, 'attr_name'): initialize` used for lazy initialization across 15+ files. Creates implicit state machine. Hard to track initialization order.
**Impact:** Non-deterministic initialization order. Missing attribute might indicate uninitialized state or actual missing feature. Complicates testing (must mock entire initialization path).
**Recommendation:** Use `@property` with lazy evaluation OR explicit initialization method. Track initialized state in `__init__`. Add assertions for required attributes.
**Effort:** Medium (systematic refactoring)

---

### MAJOR: BattleEngine Legacy Paths
**ID:** LPH-009
**Location:** `game/simulation/systems/battle_engine.py:220-224, 279-281`
**Issue:** `create_battle()` and `add_ship()` methods have "Legacy path: create controllers internally (backward compatibility)" branches that still execute. Suggests new path (with pre-created controllers) not yet universally used.
**Impact:** Code handles two different controller initialization approaches. Unclear which is canonical. Tests might not cover both paths equally.
**Recommendation:** Audit all battle engine usage - count how often legacy paths execute. If <5%, remove and migrate. If common, make it the canonical path.
**Effort:** Medium (audit + selective removal)

---

### MAJOR: Proxy Properties for Backward Compatibility
**ID:** LPH-010
**Location:** `game/ui/screens/workshop_screen.py:343-366` (ship, selected_components, available_components properties all proxy to viewmodel)
**Issue:** WorkshopScreen has 4+ properties that directly delegate to viewmodel with explicit comments "for backward compatibility". These allow old code to access properties on screen instead of screen.viewmodel.
**Impact:** Duplicates interface definition. Makes refactoring dangerous - easy to change one but not the other. Creates inconsistency (some access patterns go through proxy, others direct).
**Recommendation:** Complete migration to viewmodel access. Remove proxy properties and fix all internal uses. Update external API documentation that this is the new pattern.
**Effort:** Simple (straightforward find-replace)

---

### MINOR: Adapter Class for Ship-to-IControllable Interface
**ID:** LPH-011
**Location:** `game/ai/interfaces/controllable.py:242-250`
**Issue:** `ShipControllableAdapter` wraps Ship to implement IControllable interface. Necessary for PROJ-11 Phase 4 but creates wrapper overhead. Suggests Ship and IControllable not fully aligned.
**Impact:** Extra indirection in AI code path. Ship has combat methods, but AI must go through adapter to access them.
**Recommendation:** Consider making Ship directly implement IControllable or use composition. Evaluate if adapter is necessary or if interface definition needs adjustment.
**Effort:** Medium (architectural review needed)

---

### MINOR: ShipCombatMixin Facade Pattern
**ID:** LPH-012
**Location:** `game/simulation/entities/ship_combat.py:1-25`
**Issue:** ShipCombatMixin is explicitly a "thin facade" delegating to ShipCombatEngine. Kept for backward compatibility during PROJ-12 decomposition (2-3 years old).
**Impact:** Extra method layer adds minimal value. Developers must understand mixin delegates to engine. PROJ-12 phase appears incomplete.
**Recommendation:** Either complete PROJ-12 decomposition (make Ship composition-based) or deprecate mixin formally.
**Effort:** Complex (architectural decision required)

---

### MINOR: Commented Legacy Shim
**ID:** LPH-013
**Location:** `game/ui/screens/builder/weapons_panel.py:738-740`
**Issue:** Comment says "Legacy shim removed - always use ability damage". Code references removal but doesn't show old implementation. Suggests code cleanup was incomplete.
**Impact:** Confusing comment. Developers wonder what was removed and why. No git history context in comment.
**Recommendation:** Remove comment entirely - the behavior is now canonical. If conditional logic remains, explain current behavior not historical changes.
**Effort:** Simple

---

### MINOR: ComponentRef Tuple Migration Helpers
**ID:** LPH-014
**Location:** `game/ui/screens/builder/component_ref.py:14-19, 71-99`
**Issue:** ComponentRef provides `from_tuple()` and `to_tuple()` methods explicitly for "backward compatibility during migration". Suggests tuple-based references are being replaced with ComponentRef objects.
**Impact:** Developers must know about both formats. JSON serialization might produce tuples for old code. Increases validation burden.
**Recommendation:** Complete migration to ComponentRef everywhere. Remove tuple helpers. Add migration script for existing saves.
**Effort:** Medium (data structure migration)

---

### MINOR: Legacy/Deprecated Design Format Detection
**ID:** LPH-015
**Location:** `game/strategy/data/design_metadata.py:169-171`
**Issue:** Design loader detects "Old format detected" and warns with log but continues. Suggests design format changed but loader still accepts old format.
**Impact:** Silent format acceptance could corrupt data. No guarantee old format is correctly loaded.
**Recommendation:** Add explicit version field to design JSON. Reject old format with clear error. Provide migration utility.
**Effort:** Medium

---

### MINOR: Obsolete Design Filtering
**ID:** LPH-016
**Location:** `game/ui/screens/design_selector_window.py:5, 62-64, 157-160`
**Issue:** Design selector has `show_obsolete` flag and obsolete filter UI. Suggests designs can be marked obsolete but behavior not fully clear.
**Impact:** Feature partially implemented. UI shows checkbox but unclear what "obsolete" means operationally.
**Recommendation:** Document obsolete semantics. Either fully implement (hide obsolete by default, show with checkbox) or remove feature.
**Effort:** Simple

---

### MINOR: Triple Naming Pattern in Stats
**ID:** LPH-017
**Location:** `game/simulation/systems/stats.py:297-298`
**Issue:** `total_defense_score` computed and assigned, then immediately aliased as `to_hit_profile`. Comment says "Legacy/Alias for UI until fully refactored".
**Impact:** Duplicated data with comment about being temporary. Creates maintenance burden.
**Recommendation:** Complete refactoring - use total_defense_score everywhere, remove alias, update UI.
**Effort:** Simple

---

### MINOR: Fallback Defense Score Calculation
**ID:** LPH-018
**Location:** `game/engine/collision.py:112-115`
**Issue:** Code checks for `total_defense_score` with fallback to `get_total_ecm_score()` for "backward compatibility". Suggests defense scoring was refactored but fallback kept.
**Impact:** Inconsistent target evaluation depending on Ship implementation. Some ships use new scoring, some use old fallback.
**Recommendation:** Audit all Ship implementations - ensure all have total_defense_score. Remove fallback check, add assertion instead.
**Effort:** Simple

---

### MINOR: Legacy Path for AIController Creation
**ID:** LPH-019
**Location:** `game/simulation/systems/battle_engine.py:222-224, 279-281`
**Issue:** Comments explicitly mark two internal controller creation paths as "Legacy path: create controllers internally". Suggests external controller provision is new pattern.
**Impact:** Code handles two initialization approaches. Unclear which is preferred.
**Recommendation:** Establish clear pattern - update comments to explain when each path is used or consolidate into one.
**Effort:** Simple

---

### MINOR: Multiple Profiler Access Patterns
**ID:** LPH-020
**Location:** `game/core/profiling.py:134-140`
**Issue:** `_ProfilerProxy` similar to `_ValidatorProxy` - lazy initialization for backward compatibility. Module-level `profiler` variable uses proxy pattern instead of direct instantiation.
**Impact:** Same issues as ValidatorProxy - hidden initialization, unclear semantics.
**Recommendation:** Consolidate to explicit singleton factory or explicit DI.
**Effort:** Simple

---

### INFO: Placeholder Technology System
**ID:** LPH-021
**Location:** `game/app.py:670-671`
**Issue:** Comment says "placeholder for now - will be implemented when tech tree exists" with TODO to replace. Tech tree not yet implemented, so available_tech_ids set to empty list.
**Impact:** No actual issue - this is a known stub. Document in architecture notes rather than as TODO comment.
**Recommendation:** Create separate issue tracker item for tech tree feature. Remove TODO, replace with feature reference.
**Effort:** Simple

---

### INFO: Dual Module Import Prevention
**ID:** LPH-022
**Location:** `game/ui/__init__.py:8-10`
**Issue:** Comment explains "Pre-import submodules in dependency order (excluding workshop_screen due to circular import)". Circular import exists but is worked around at module load time.
**Impact:** Module initialization has hidden dependency. Changes to workshop_screen could break this.
**Recommendation:** Resolve circular import properly. Document dependency chain. Consider lazy import for workshop_screen.
**Effort:** Medium (architectural refactoring)

---

### INFO: Save Game Format Version Strictness
**ID:** LPH-023
**Location:** `game/strategy/systems/save_game_service.py:10, 367-370`
**Issue:** Comment explicitly states "Strict version checking (no backward compatibility)". Code rejects old save format (v1.0.0) with "old save format not supported" error.
**Impact:** Players cannot load old saves. Acceptable if documented but limits player data migration.
**Recommendation:** This is a design choice, not a bug. Document version support policy. Consider adding migration utility if needed for player base.
**Effort:** N/A (acceptable design)

---

## Top 5 Priority Issues

1. **LPH-001: Deprecated Registry Functions** - Blocks full migration to PROJ-38 DI pattern. Requires coordinated migration across 20+ files. HIGH PRIORITY.

2. **LPH-003: Dual Static/Instance Methods in ShipStatsService** - Most confusing API in codebase. Multiple calling conventions make maintenance error-prone. Should be refactored next.

3. **LPH-002: FleetMovementSimulator Deprecated Module** - Entire module marked for removal but still functional. Create migration timeline and remove duplicate logic.

4. **LPH-006: Multiple Backward Compatibility Layers** - Constants, ValidationResult, LayerType all have re-exports. Establish consistency in how legacy access is handled across codebase.

5. **LPH-008: Lazy Initialization Pattern Abuse** - 15+ files use hasattr-based lazy init. Should be systematized with property decorators or explicit initialization.

---

**Note:** This report intentionally excludes normal version compatibility and feature flags. Focus is on *architectural* legacy patterns that indicate incomplete refactoring or mid-migration code. Several PROJ- tagged efforts (PROJ-12, PROJ-27, PROJ-35, PROJ-38) appear incomplete based on code analysis.

---


## File: architecture_report.md

# Architecture Review Report

## Summary
- **Total issues found:** 15
- **Critical:** 4
- **Major:** 7
- **Minor:** 4
- **Info:** 0

---

## Findings

### CRITICAL: UI Layer Directly Instantiates Simulation Objects
**ID:** AR-01
**Location:** `game/ui/screens/setup.py:94-128`, `game/ui/screens/builder/main.py:90`, `game/ui/screens/workshop_screen.py:18-38`
**Issue:** UI code directly creates `Ship` objects and accesses/modifies their internal attributes. UI layer imports directly from `game.simulation.entities.ship`.
**Impact:** Violates layered architecture. Changes to ship internals break UI code. Cannot swap simulation implementations.
**Recommendation:** Create UI-facing Ship DTO/Command pattern. UI should issue commands rather than directly mutating ships.
**Effort:** Complex

### CRITICAL: Global Mutable State in Core Registries
**ID:** AR-02
**Location:** `game/simulation/components/component.py:74-75`, `game/core/registry.py:92-93`
**Issue:** Shared global state (`COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, `VEHICLE_CLASSES`) exposed as module-level variables. 77 files import from `game.core.config`.
**Impact:** Cannot safely run tests in parallel. Registry state persists between tests/scenes. Hidden dependencies.
**Recommendation:** Migrate to dependency injection via `GameRegistries` container. Use constructor injection.
**Effort:** Complex

### CRITICAL: Feature Envy - Builder Components Accessing Ship Internals
**ID:** AR-03
**Location:** `game/ui/screens/builder/main.py:90-91,569,859-860,972`
**Issue:** Builder UI extensively accesses and manipulates ship component layers, modifiers, and design data. Performs business logic that belongs in simulation layer.
**Impact:** Duplicate validation logic. Ship design logic spread across UI and simulation.
**Recommendation:** Extract ship builder logic into `ShipDesignService` in simulation layer.
**Effort:** Complex

### CRITICAL: Circular Dependency Risk - Strategy â†” Simulation
**ID:** AR-04
**Location:** `game/strategy/adapters/simulation_adapter.py:24-27`, `game/strategy/services/ship_stats_service.py:27-28`
**Issue:** Strategy layer imports directly from simulation layer. While currently one-directional, tight coupling creates risk.
**Impact:** Strategy layer cannot be tested independently. Changes to simulation break strategy layer.
**Recommendation:** Strategy layer should only depend on `IBattleResolver` interface and DTOs.
**Effort:** Medium

### MAJOR: LayerType Constant Duplication
**ID:** AR-05
**Location:** Multiple files reference `LayerType` from different import paths
**Issue:** `LayerType` defined in `game.simulation.components.component_constants` but imported from `game.core.constants` in UI files.
**Impact:** Confusing and error-prone. Layering violation.
**Recommendation:** Move `LayerType` to single canonical location. Update all files.
**Effort:** Medium

### MAJOR: No Clean Interface Between UI and Battle Layers
**ID:** AR-06
**Location:** `game/ui/screens/battle_scene.py:23-26`, `game/ui/hud/panels.py:3-17`
**Issue:** UI battle code imports directly from simulation. Battle panels directly access ship objects.
**Impact:** Battle UI tightly coupled to simulation internals. Cannot mock for UI testing.
**Recommendation:** Create `IBattleUI` service interface exposing only what UI needs.
**Effort:** Medium

### MAJOR: Ship Class is God Object - 834 Lines
**ID:** AR-07
**Location:** `game/simulation/entities/ship.py`
**Issue:** Ship class handles physics, combat, component management, stats, serialization, resources, formations. 834 lines via mixins.
**Impact:** Difficult to understand. High cognitive load. Testing is complex.
**Recommendation:** Break into ShipPhysics, ShipCombat, ShipComponents, ShipResources using composition.
**Effort:** Complex

### MAJOR: Inappropriate Intimacy - Workshop Screen Manages Simulation Data
**ID:** AR-08
**Location:** `game/ui/screens/workshop_screen.py:68-92`
**Issue:** DesignWorkshopGUI directly manages ship designs, components, modifiers through persistence layer.
**Impact:** Cannot reuse design management logic outside UI. UI changes require business logic changes.
**Recommendation:** Extract design management to `ShipDesignRepository` service.
**Effort:** Medium

### MAJOR: Missing Abstraction for Component System Access
**ID:** AR-09
**Location:** `game/ui/screens/builder/modifier_logic.py:8`, `game/simulation/components/component.py:74-75`
**Issue:** Direct access to `MODIFIER_REGISTRY` and `COMPONENT_REGISTRY` globals from UI code.
**Impact:** UI tightly coupled to registry structure. Cannot change registry implementation.
**Recommendation:** Create `ComponentService` interface with get_components(), get_modifiers() methods.
**Effort:** Simple

### MAJOR: Validation Logic Scattered Across Layers
**ID:** AR-10
**Location:** `game/simulation/systems/validator.py`, `game/ui/screens/race_validator.py`, `game/strategy/validation/base.py`
**Issue:** Validation rules scattered across simulation, UI, and strategy layers.
**Impact:** Consistency issues. UI might allow invalid state that simulation rejects.
**Recommendation:** Create unified `ValidationEngine` in core layer.
**Effort:** Medium

### MINOR: Module Bloat - Large UI Screen Classes
**ID:** AR-11
**Location:** `game/ui/screens/race_setup_screen.py:1231 LOC`, `game/ui/screens/fleet_report_window.py:1034 LOC`
**Issue:** Very large UI screen classes handling multiple concerns.
**Impact:** Difficult to navigate and unit test.
**Recommendation:** Break into smaller focused components with composition.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **AR-02: Global Mutable State in Core Registries** - Root cause of extensibility problems. Makes parallel testing impossible.

2. **AR-01: UI Layer Directly Instantiates Simulation Objects** - Direct violation of layered architecture. Prevents testing and layer independence.

3. **AR-04: Circular Dependency Risk** - Currently works but fragile. Dependency inversion not followed.

4. **AR-03: Feature Envy - Builder Components** - Duplicates business logic from simulation layer (shotgun surgery indicator).

5. **AR-07: Ship Class God Object** - 834 lines with too many responsibilities. High cognitive load blocks extending.

---


## File: dead_code_report.md

# Dead Code Review Report

## Summary
- **Total issues found:** 11
- **Critical:** 2
- **Major:** 4
- **Minor:** 4
- **Info:** 1

---

## Findings

### CRITICAL: Broken Import References in Main Application
**ID:** DC-01
**Location:** `game/app.py:28-29`
**Issue:** App imports non-existent modules:
```python
from Tools.formation_editor import FormationEditorScene
from ui.test_lab_scene import TestLabScene
```
These modules don't exist at the referenced paths.
**Impact:** Runtime ImportError will occur if TEST_LAB or FORMATION states are activated.
**Recommendation:** Update imports to correct paths or move modules into proper game package structure.
**Effort:** Simple

### CRITICAL: Backup File Committed to Repository
**ID:** DC-02
**Location:** `ui/test_lab_scene.py.backup`
**Issue:** A 2,731-line backup file of test_lab_scene.py is committed alongside the active version.
**Impact:** Increases repo size, creates confusion about which version is active.
**Recommendation:** Delete the `.backup` file. Use git history if older version is needed.
**Effort:** Simple

### MAJOR: Marked-for-Deletion Directory Unresolved
**ID:** DC-03
**Location:** `./_marked_for_deletion_2026-01-27/`
**Issue:** Entire directory marked for deletion but still in the repository.
**Impact:** Clutters repo, indicates incomplete cleanup.
**Recommendation:** Delete the entire directory or properly archive.
**Effort:** Simple

### MAJOR: Incorrect Import Path for TestLabScene
**ID:** DC-04
**Location:** `game/app.py:29` / Actual module at `ui/test_lab_scene.py`
**Issue:** app.py imports from `ui.test_lab_scene` but ui/ is outside the game package.
**Impact:** Import will fail at runtime when TEST_LAB state is accessed.
**Recommendation:** Move `ui/` into `game/ui/screens/` or create proper import path handling.
**Effort:** Medium

### MAJOR: Incorrect Import Path for FormationEditorScene
**ID:** DC-05
**Location:** `game/app.py:28` / Actual module at `Tools/formation_editor.py`
**Issue:** app.py imports from `Tools.formation_editor` but Tools/ is outside game package.
**Impact:** Import will fail at runtime when FORMATION state is accessed.
**Recommendation:** Move Tools into proper package structure or fix import paths.
**Effort:** Medium

### MAJOR: Empty Init Files - Incomplete Package Setup
**ID:** DC-06
**Location:** Multiple `__init__.py` files (14 files with 0 lines)
**Issue:** Empty __init__.py files without package-level exports for cleaner imports.
**Impact:** Forces deep import paths, makes package exports unclear.
**Recommendation:** Add meaningful __all__ exports or remove unnecessary package structure.
**Effort:** Medium

### MINOR: Unused Backward Compatibility Path Exports
**ID:** DC-07
**Location:** `game/core/paths.py:89-98`
**Issue:** Module exports old-style path constants for backward compatibility that duplicate the Paths class API.
**Impact:** Code duplication, confusing API surface.
**Recommendation:** Migrate all uses to `Paths.` class API. Remove once converted.
**Effort:** Simple

### MINOR: Unused Path Constants
**ID:** DC-08
**Location:** `game/core/paths.py:59-60, 98`
**Issue:** `VEHICLE_CLASSES_FILE` and `VEHICLE_LAYERS_FILE` defined but rarely used in active code.
**Impact:** Dead API surface.
**Recommendation:** Verify not needed; remove or consolidate.
**Effort:** Simple

### MINOR: Duplicate Imports in constants.py
**ID:** DC-09
**Location:** `game/core/constants.py:1-9, 31-53`
**Issue:** File imports from enum twice. Also re-exports from Paths duplicating paths.py.
**Impact:** Code redundancy.
**Recommendation:** Clean up duplicate imports, consolidate re-exports.
**Effort:** Simple

### MINOR: Legacy Comment Marker
**ID:** DC-10
**Location:** `game/ui/screens/test_lab.py:88-100`
**Issue:** Commented-out code block with notes about removed functionality.
**Impact:** Minor - shows incomplete cleanup from refactoring.
**Recommendation:** Remove once surrounding code is stable.
**Effort:** Simple

### INFO: Debugging Scripts Not Integrated
**ID:** DC-11
**Location:** `Debugging/archive_confirmed.py`, `Debugging/confirm_bugs_ui.py`
**Issue:** Debug automation scripts exist but aren't integrated into CI pipeline.
**Impact:** Unused tooling.
**Recommendation:** Integrate into debug workflow or remove if not needed.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **DC-01: Broken Imports in game/app.py** - Will cause immediate runtime failures

2. **DC-02: Backup File Committed** - Quick win: delete backup file

3. **DC-04/DC-05: Incorrect Import Paths** - Fix requires architectural decision about package structure

4. **DC-03: Marked-for-Deletion Directory** - Quick win: delete entire directory

5. **DC-06: Empty __init__.py Files** - Consolidate package structure for better imports

---


