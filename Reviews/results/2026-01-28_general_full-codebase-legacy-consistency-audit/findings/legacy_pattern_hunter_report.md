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
