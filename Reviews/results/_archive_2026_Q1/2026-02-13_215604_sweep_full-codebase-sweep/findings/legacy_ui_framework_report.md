# Legacy System Holdovers Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 22
- **Total Issues Found:** 11
- **Critical:** 0 | **Major:** 3 | **Minor:** 6 | **Info:** 2

## Files Scanned
- `game/ui/__init__.py`
- `game/ui/utils.py`
- `game/ui/config.py`
- `game/ui/colors.py`
- `game/ui/services/validation_service.py`
- `game/ui/services/vehicle_class_service.py`
- `game/ui/services/component_service.py`
- `game/ui/services/ship_factory.py`
- `game/ui/services/design_loader_adapter.py`
- `game/ui/services/ship_io_adapter.py`
- `game/ui/services/battle_factories.py`
- `game/ui/services/__init__.py`
- `game/ui/services/battle_ui_service.py`
- `game/ui/services/input_mapper.py`
- `game/ui/services/screenshot_manager.py`
- `game/ui/services/ship_io.py`
- `game/ui/renderer/camera.py`
- `game/ui/renderer/game_renderer.py`
- `game/ui/renderer/sprites.py`
- `game/ui/interfaces/battle_ui.py`
- `game/ui/orchestration/battle_orchestrator.py`
- `game/ui/assets/ship_theme_manager.py`

## Findings

#### MAJOR: Singleton Pattern Still Used Where DI Available
**ID:** LEG-UI2-001
**Location:** `game/ui/services/screenshot_manager.py:11-24`, `game/ui/renderer/sprites.py:8-21`, `game/ui/assets/ship_theme_manager.py:11-25`
**Issue:** Three classes still use the `SingletonMeta` pattern: `ScreenshotManager`, `SpriteManager`, and `ShipThemeManager`. The project has migrated many areas to dependency injection, but these managers remain as singletons accessed via `.instance()` throughout the codebase.
**Impact:** Reduces testability, creates hidden dependencies, and makes it harder to reason about state. Multiple screens and services call `.instance()` directly instead of receiving the manager via constructor injection.
**Recommendation:** Consider refactoring to accept these managers via dependency injection. The singletons themselves could remain as default providers, but call sites should receive instances rather than calling `.instance()` directly.
**Effort:** Complex - would require updating many call sites across screens and panels

#### MAJOR: ShipFactory Legacy Registries Fallback Pattern
**ID:** LEG-UI2-002
**Location:** `game/ui/services/ship_factory.py:15-16, 49-56`
**Issue:** The docstring explicitly states "When registries is not provided, uses global RegistryManager (legacy behavior)" and the `_get_registries()` method falls back to `get_default_registries()`. While PROJ-50 mandated strict DI for VehicleClassService, ShipFactory retained the legacy fallback pattern.
**Impact:** Creates inconsistent DI behavior across services. Some services (VehicleClassService) raise ValueError when registries is None, while others (ShipFactory, ComponentService) silently fall back to globals. This inconsistency makes the codebase harder to understand and maintain.
**Recommendation:** Either migrate to strict DI (require registries parameter) or document this as an intentional exception. If keeping the fallback, remove "legacy behavior" from docstring since it's now the intended behavior.
**Effort:** Medium - requires deciding on policy and updating either the fallback services or the strict services to be consistent

#### MAJOR: ComponentService Inconsistent DI Pattern
**ID:** LEG-UI2-003
**Location:** `game/ui/services/component_service.py:31-49`
**Issue:** ComponentService uses the "lazy resolution via get_default_registry_provider()" pattern, which the docstring explicitly contrasts with VehicleClassService's "strict required pattern." This creates two competing patterns within the same services package.
**Impact:** Developers must check each service to understand its DI requirements. The docstring acknowledges this inconsistency but doesn't resolve it.
**Recommendation:** Standardize on one pattern across all UI services - either all strict DI with required parameters, or all optional with lazy resolution. The comment about PROJ-50 "explicitly mandating" strict DI for some services suggests this was a partial migration.
**Effort:** Medium - requires policy decision and updates to affected services

#### MINOR: Unused Method get_type_for_class in VehicleClassService
**ID:** LEG-UI2-004
**Location:** `game/ui/services/vehicle_class_service.py:116-129`
**Issue:** The `get_type_for_class()` method is defined but only referenced in tests, not in any production code.
**Impact:** Dead code that adds maintenance burden and test overhead.
**Recommendation:** If the method is not used by any production code, consider removing it. Run grep to verify there are no production callers before deletion.
**Effort:** Simple

#### MINOR: Potentially Unused Method is_modifier_allowed in ComponentService
**ID:** LEG-UI2-005
**Location:** `game/ui/services/component_service.py:82-126`
**Issue:** The `is_modifier_allowed()` method performs modifier restriction checking but is only called from tests and `game/ui/screens/builder/modifier_logic.py`. The method duplicates logic that should exist in the core modifier service.
**Impact:** Potential code duplication with simulation layer's ModifierService. UI service performing validation logic that may belong in simulation.
**Recommendation:** Verify if this logic should be delegated to ModifierService in the simulation layer, or if this is intentional UI-layer duplication for isolation purposes.
**Effort:** Simple to investigate, Medium if refactoring needed

#### MINOR: ShipIOAdapter get_ships_folder Method Unused in Production
**ID:** LEG-UI2-006
**Location:** `game/ui/services/ship_io_adapter.py:64-70`
**Issue:** The `get_ships_folder()` method exists but is only referenced in test files, not in production code.
**Impact:** Minor dead code that adds to maintenance burden.
**Recommendation:** Remove if no production use case exists, or document its intended use.
**Effort:** Simple

#### MINOR: BattleOrchestrator.create_ai_for_ship Unused in Production
**ID:** LEG-UI2-007
**Location:** `game/ui/orchestration/battle_orchestrator.py:82-98`
**Issue:** The `create_ai_for_ship()` method is documented "for reinforcements" but is only called from tests (`test_battle_orchestrator.py` and `test_battle_engine_core.py`), not from any production code that handles reinforcements.
**Impact:** Dead code path. Either the reinforcement feature was never completed, or it uses a different mechanism.
**Recommendation:** Investigate whether reinforcements are implemented elsewhere. If this method has no production use, consider removing it.
**Effort:** Simple

#### MINOR: hasattr Checks in BattleUIService May Indicate Missing Protocol Guarantees
**ID:** LEG-UI2-008
**Location:** `game/ui/services/battle_ui_service.py:160-170, 195-196, 218-235`
**Issue:** Multiple `hasattr()` and `getattr(_, _, default)` patterns exist for accessing Ship and Component attributes like `current_target`, `crew_onboard`, `crew_required`, `status`, etc. This suggests either: (1) The attributes aren't guaranteed by the protocol/interface, or (2) These are legacy compatibility checks for old ship implementations that may no longer exist.
**Impact:** If these attributes are now guaranteed to exist on all Ships/Components, the checks add unnecessary complexity. If they're optional, the protocol should be updated to reflect this.
**Recommendation:** Audit Ship and Component classes to verify which attributes are guaranteed. Remove unnecessary hasattr/getattr guards for guaranteed attributes. Update protocols/type hints if attributes are optional.
**Effort:** Medium - requires auditing simulation layer entities

#### MINOR: InputMapper._defaults_path Stored But Never Read
**ID:** LEG-UI2-009
**Location:** `game/ui/services/input_mapper.py:69, 82`
**Issue:** The `_defaults_path` instance variable is set in `load()` but is never read by any other method. This appears to be stored for potential future use (reset to defaults?) but has no current consumer.
**Impact:** Minor dead state that could cause confusion.
**Recommendation:** Either use this stored path in `reset_to_defaults()` to reload from file, or remove if not needed.
**Effort:** Simple

#### INFO: Fallback Patterns Throughout UI Layer
**ID:** LEG-UI2-010
**Location:** Multiple files (see grep results for "fallback")
**Issue:** There are 80+ uses of "fallback" in UI layer code. Most are legitimate graceful degradation (e.g., fallback images when themes aren't found, fallback colors for missing resources). However, some docstrings still reference "legacy" or "backward compat" patterns:
- `game/ui/services/ship_factory.py:15` - "legacy behavior"
- `game/ui/screens/empire_build_queue_window.py:328` - "Update legacy single-selection fields"
- `game/ui/screens/builder/stats_config.py:70` - "Legacy pattern using negative CrewCapacity was removed in PROJ-42"
**Impact:** Some fallback references are documentation, some are active code patterns. The "legacy" terminology creates confusion about whether code should be preserved or removed.
**Recommendation:** Audit each "legacy" reference. For completed migrations (like PROJ-42), remove the comments mentioning legacy. For active fallback patterns, rename to "default" or "graceful degradation" to clarify these are intentional, not temporary.
**Effort:** Simple

#### INFO: Direct Simulation Layer Imports in UI Services
**ID:** LEG-UI2-011
**Location:** Multiple files in `game/ui/services/`, `game/ui/renderer/`
**Issue:** Several UI framework files import directly from `game.simulation.*` rather than going through the services/adapters layer:
- `battle_factories.py` imports BattleController, BattleConfig, BattleMode, ShipSerializer
- `ship_io.py` imports Ship directly
- `validation_service.py` imports get_or_create_validator
- `design_loader_adapter.py` imports SimulationDesignLoader
**Impact:** These imports are acceptable for services acting as facades/adapters, but they create tight coupling between UI and Simulation layers. The adapter pattern was introduced (PROJ-43) to decouple these layers.
**Recommendation:** This is likely intentional - the services package exists precisely to encapsulate these cross-layer dependencies. No action needed unless the goal is stricter layer separation.
**Effort:** N/A - appears intentional by design

## Top 5 Priority Issues

1. **LEG-UI2-001 (MAJOR):** Singleton Pattern Still Used Where DI Available - Three core managers use singletons, reducing testability and creating hidden dependencies across the UI layer.

2. **LEG-UI2-002 (MAJOR):** ShipFactory Legacy Registries Fallback Pattern - Explicit "legacy behavior" comment indicates incomplete migration; creates inconsistent DI policy across services.

3. **LEG-UI2-003 (MAJOR):** ComponentService Inconsistent DI Pattern - Two competing DI patterns within the same services package creates confusion about project standards.

4. **LEG-UI2-007 (MINOR):** BattleOrchestrator.create_ai_for_ship Unused - Dead code for "reinforcements" feature that appears to never have been integrated.

5. **LEG-UI2-008 (MINOR):** hasattr Checks May Indicate Missing Protocol Guarantees - Multiple defensive attribute checks could be removed if simulation layer provides guarantees.
