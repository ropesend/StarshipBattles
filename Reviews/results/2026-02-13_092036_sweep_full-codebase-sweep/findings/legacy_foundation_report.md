# Legacy System Holdovers Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 42
- **Total Issues Found:** 8
- **Critical:** 0 | **Major:** 2 | **Minor:** 5 | **Info:** 1

## Findings

#### MAJOR: Unused Import - RegistryManager in resources.py
**ID:** LEG-FND-001
**Location:** `game/core/resources.py:16`
**Issue:** The module imports `RegistryManager` from `game.core.registry` but never uses it. The docstring mentions loading data into RegistryManager, but the actual implementation only loads and returns raw JSON data without registering it.
**Impact:** Dead import increases cognitive load and suggests incomplete migration or abandoned integration code. The docstring and code are inconsistent.
**Recommendation:** Either remove the unused import and update the docstring, or complete the integration to actually register the loaded resources.
**Effort:** Simple

#### MAJOR: Extensive getattr() Defensive Patterns Suggesting Incomplete Interface Standardization
**ID:** LEG-FND-002
**Location:** `game/ai/combat_utils.py:63-181`, `game/ai/controller.py:125-420`, `game/ai/behaviors.py:281-336`, `game/ai/target_evaluator.py:87-194`, `game/engine/collision.py:107-148`
**Issue:** The AI and engine layers contain extensive `getattr()` calls with default values to access entity attributes (e.g., `getattr(entity, 'position', None)`, `getattr(candidate, 'mass', 100)`, `getattr(s, 'hp', 100)`). While this provides robustness, it suggests that entity interfaces are not fully standardized. Key observations:
- `combat_utils.py` has `get_position()` that falls back from interface method to direct attribute
- `target_evaluator.py` uses `getattr(candidate, 'mass', 100)` with arbitrary defaults
- `collision.py` uses `getattr(s, 'hp', 100)` suggesting ships may not always have hp attribute
- Multiple places check for both `get_X()` methods and `X` attributes on the same entities

This pattern is appropriate for defensive programming but indicates the underlying interfaces could be cleaner.
**Impact:** Code is harder to maintain and understand; the actual contract between layers is unclear. New code might not know whether to use methods or attributes.
**Recommendation:** Consider defining explicit protocols/interfaces in `game/core/protocols.py` for all entity types that AI/engine interact with. The `IControllable` protocol exists but isn't used everywhere. Standardize on either method-based or attribute-based access.
**Effort:** Complex

#### MINOR: Singleton Pattern Still Used Extensively
**ID:** LEG-FND-003
**Location:** `game/core/singleton.py`, `game/core/registry.py:122`, `game/core/logger.py:9`, `game/core/profiling.py:14`, `game/core/strategy_metadata.py:33`, `game/ai/strategy_manager.py:20`
**Issue:** The project has embraced dependency injection (PROJ-27, PROJ-38 via `GameRegistries`, `DefaultRegistryProvider`, `TestRegistryProvider`) but the singleton pattern via `SingletonMeta` is still used in multiple places within the scanned scope:
- `RegistryManager` (core)
- `Logger` (core)
- `Profiler` (core)
- `StrategyMetadataService` (core)
- `StrategyManager` (ai)

The registry layer has both old singleton access (`RegistryManager.instance()`) and new DI patterns (`get_default_registry_provider()`).
**Impact:** Mixed patterns create confusion about the preferred access method. Tests may need to reset multiple singletons.
**Recommendation:** The DI transition is partially complete. Continue migration by wrapping singleton access in provider classes. Low priority since singletons are appropriate for certain cross-cutting concerns (logging, profiling).
**Effort:** Complex

#### MINOR: hasattr() Checks for Mock Detection in Production Code
**ID:** LEG-FND-004
**Location:** `game/ai/combat_utils.py:43-47`
**Issue:** The `is_vector2_like()` function contains mock detection code in production:
```python
# Check for MagicMock by looking for tell-tale attributes
if hasattr(obj, '_mock_name') or hasattr(obj, 'assert_called'):
    return False
```
This is test-specific logic that has leaked into production code.
**Impact:** Production code is checking for test constructs, indicating coupling between test and production. Performance impact is minimal but design is suboptimal.
**Recommendation:** Consider using proper type hints and protocols. If mock detection is truly needed (e.g., for defensive programming during battles), document why. Otherwise, remove or move to test utilities.
**Effort:** Simple

#### MINOR: Fallback Behavior Documented Extensively But May Mask Bugs
**ID:** LEG-FND-005
**Location:** `game/ai/__init__.py:34-52`, `game/ai/combat_utils.py:7-11`, `game/ai/target_evaluator.py:7-16`
**Issue:** The AI layer documents extensive "fallback behavior" as a design philosophy:
- "Combat must not crash due to individual entity errors"
- "Fallback behavior is used when possible"
- Position/rotation access failures fall back to direct attributes
- Missing data uses "safe defaults"

While robustness is valuable, this can mask integration bugs where entities don't properly implement expected interfaces.
**Impact:** Bugs in entity implementations may go undetected in production. The system "works" but with incorrect data (e.g., default mass of 100, default position of None).
**Recommendation:** Consider adding a debug/strict mode that logs warnings at WARNING level for all fallback uses, making them visible during development without crashing production. Some of this is already done but inconsistently.
**Effort:** Medium

#### MINOR: Commented Strategy Hints in Controller Code
**ID:** LEG-FND-006
**Location:** `game/ai/controller.py:346`
**Issue:** Comment `# (Same logic as original, just encapsulated)` in `_handle_formation_master` suggests this was refactored from somewhere else but the comment references the "original" location without specifics. This is a minor documentation smell.
**Impact:** Minor confusion about code history.
**Recommendation:** Remove or update comment to be self-contained.
**Effort:** Simple

#### MINOR: Potential Dead Parameters in navigate_to
**ID:** LEG-FND-007
**Location:** `game/ai/controller.py:434`
**Issue:** The `navigate_to` method has a `precise: bool = False` parameter that is used in the method but always passed as explicit values (True or False) by all callers in behaviors.py. The default value of `False` may never be exercised.
**Impact:** Minor - the default exists but may be unnecessary since all callers are explicit.
**Recommendation:** Verify if any callers use the default; if not, consider removing the default value or documenting when the default should be used.
**Effort:** Simple

#### INFO: Well-Structured Research Module (Clean)
**ID:** LEG-FND-008
**Location:** `game/research/`
**Issue:** The research module appears to be cleanly implemented with:
- Clear data models (TechNode, TechTree, ResearchTracker)
- Service layer (ResearchService)
- UI components (ResearchControlPanel, ResearchRenderer, ResearchTreeScene)
- Proper use of ICamera protocol
- No legacy patterns detected

This is a positive finding demonstrating good architecture.
**Impact:** N/A - this is a clean implementation.
**Recommendation:** Use as a reference for other modules.
**Effort:** N/A

## Top 5 Priority Issues

1. **LEG-FND-002 (MAJOR)**: Extensive getattr() patterns in AI/engine suggest incomplete interface standardization. This affects maintainability and makes the contract between layers unclear.

2. **LEG-FND-001 (MAJOR)**: Unused RegistryManager import in resources.py with inconsistent docstring. Simple fix but indicates incomplete or abandoned work.

3. **LEG-FND-005 (MINOR)**: Fallback behavior may mask integration bugs. Consider adding strict mode for development.

4. **LEG-FND-003 (MINOR)**: Mixed singleton/DI patterns in registry access. DI migration is partially complete.

5. **LEG-FND-004 (MINOR)**: Mock detection in production code is a test/production coupling smell.

## Analysis Notes

### Files Scanned by Directory
- **game/core/**: 18 files (math.py, json_utils.py, paths.py, input_actions.py, singleton.py, __init__.py, strategy_metadata.py, profiling.py, protocols.py, registry.py, hex_math.py, exceptions.py, resources.py, validation.py, logger.py, config.py, constants.py, error_codes.py)
- **game/ai/**: 9 files (__init__.py, interfaces/__init__.py, interfaces/controllable.py, target_evaluator.py, strategy_manager.py, behaviors.py, ai_factory.py, combat_utils.py, controller.py)
- **game/research/**: 11 files (__init__.py, data/__init__.py, data/tech_node.py, data/tech_tree.py, data/research_tracker.py, systems/__init__.py, systems/research_service.py, ui/__init__.py, ui/research_controls.py, ui/research_renderer.py, ui/research_scene.py)
- **game/engine/**: 4 files (__init__.py, physics.py, collision.py, spatial.py)

### Patterns NOT Found (Good)
- No ImportError fallback patterns (try/except ImportError)
- No "legacy", "deprecated", "old_", "_old" naming in code (except legitimate variable names like `old_chance`)
- No TODO/FIXME/HACK comments
- No commented-out code blocks
- No circular import workarounds
- No backward compatibility layers for save files
- No feature flags or configuration toggles for old systems

### Architecture Observations
- The core layer correctly has no dependencies on other game layers
- The AI layer properly depends on core and uses protocols for type safety
- The research module is well-isolated with clear boundaries
- The engine layer is minimal and focused (physics, collision, spatial)
- DI patterns are being adopted but migration is incomplete
