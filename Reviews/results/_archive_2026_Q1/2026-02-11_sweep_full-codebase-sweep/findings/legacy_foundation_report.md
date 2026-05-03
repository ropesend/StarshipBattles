# Legacy System Holdovers Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 43
- **Total Issues Found:** 14
- **Critical:** 1 | **Major:** 4 | **Minor:** 7 | **Info:** 2

## Findings

#### CRITICAL: Backward Compatibility Wrapper `load_resources()` in resources.py
**ID:** LEG-FND-001
**Location:** `game/core/resources.py:101-143`
**Issue:** The `load_resources()` function is explicitly documented as "a thin wrapper around load_resources_data() for backward compatibility" (line 105-106). It mutates global state via `RegistryManager.instance().resources` directly, duplicating the entire loading logic already present in `load_resources_data()`. Both functions contain identical error-handling blocks (6 exception handlers each). The project policy states "When a new system replaces an old one, ERADICATE the old system completely." The DI-based `load_resources_data()` is the new system; `load_resources()` is the old system that should have been removed.
**Impact:** Confusion about which function is authoritative. Two code paths for the same operation means bugs fixed in one may not be fixed in the other. The backward compat wrapper bypasses DI, undermining testability.
**Recommendation:** Migrate the single production caller (`game/app.py:97`) to use `load_resources_data()` and populate the registry via `RegistryManager.hydrate()`. Delete `load_resources()` entirely. Update tests that call `load_resources()` to use the DI-based function.
**Effort:** Medium (one production call site, ~30 test call sites)

#### MAJOR: StrategyMetadataService Uses Hand-Rolled Singleton Instead of SingletonMeta
**ID:** LEG-FND-002
**Location:** `game/core/strategy_metadata.py:34-94`
**Issue:** `StrategyMetadataService` implements its own singleton pattern with manual `_instance`, `_lock`, `instance()`, and `reset()` methods (lines 50-94). The project has a canonical `SingletonMeta` metaclass (in `game/core/singleton.py`) that provides identical thread-safe singleton behavior. Other singletons in the assigned shard (`ScreenshotManager`, `Logger`, `Profiler`, `RegistryManager`, `StrategyManager`) all use `SingletonMeta`. This class is the only holdout with a hand-rolled implementation.
**Impact:** Inconsistent pattern across the codebase. The hand-rolled version has a constructor guard that raises `StateException` if called directly (line 60-65), which `SingletonMeta` handles transparently. This adds unnecessary complexity and a divergent API.
**Recommendation:** Migrate `StrategyMetadataService` to use `metaclass=SingletonMeta`. Remove the manual `_instance`, `_lock`, `instance()`, and `reset()` methods.
**Effort:** Simple

#### MAJOR: Dead Instance Attributes `attack_state` and `attack_timer` on AIController
**ID:** LEG-FND-003
**Location:** `game/ai/controller.py:90-91`
**Issue:** `AIController.__init__()` sets `self.attack_state = 'approach'` and `self.attack_timer = 0` (lines 90-91). These attributes are never read or written anywhere in `AIController`. The attack run state is fully managed by `AttackRunBehavior` which has its own `self.attack_state` and `self.attack_timer` (see `game/ai/behaviors.py:185-191`). These are leftover attributes from before the behavior extraction.
**Impact:** Dead code that suggests AIController still manages attack state directly, causing confusion about the architecture.
**Recommendation:** Delete lines 90-91 from `AIController.__init__()`.
**Effort:** Simple

#### MAJOR: Duplicate Path Resolution Logic in resources.py Bypasses Paths Class
**ID:** LEG-FND-004
**Location:** `game/core/resources.py:31-52`
**Issue:** `_resolve_resource_path()` manually calculates the project root by walking parent directories (`os.path.dirname()` chain at lines 45-47), duplicating the path resolution logic in `game/core/paths.py` which has a robust `_find_project_root()` function (lines 21-40) and a `Paths.DATA_DIR` constant. This manual resolution predates the centralized `Paths` class and should use it instead.
**Impact:** If the project structure changes, this function would break independently of `Paths`. It also adds unnecessary complexity with its own fallback logic.
**Recommendation:** Replace `_resolve_resource_path()` with `Paths`-based resolution, or remove it entirely if the caller uses absolute paths (which `app.py` does via `Paths.RESOURCES_FILE`).
**Effort:** Simple

#### MAJOR: Unused Protocol Classes and TypeGuard Functions in protocols.py
**ID:** LEG-FND-005
**Location:** `game/core/protocols.py:85-110, 234-248, 274-288, 364-380, 439-466`
**Issue:** Several protocol classes and their TypeGuard functions are defined but never used by any production code:
- `ILocatable` (line 85) - never imported outside protocols.py and tests
- `INamed` (line 94) - never imported outside protocols.py and tests
- `IOwnable` (line 103) - never imported outside protocols.py and tests
- `ISectorEnvironment` (line 234) - defined but only used by 2 UI files via `is_sector_environment` TypeGuard
- `IDamageable` (line 274) - never imported outside protocols.py and tests
- `IStarSystem` (line 116) - never imported outside protocols.py
- `IStar` (line 141) - never imported outside protocols.py
- `IWarpPoint` (line 221) - never imported outside protocols.py
- `IResourceReader` (line 364) - never imported outside protocols.py and tests
- `IResourceHolder` (line 439) - never imported outside protocols.py and tests
- `is_resource_reader()` (line 433) - never called by production code
- `is_resource_holder()` (line 464) - never called by production code
- `is_camera()` (line 550) - never called by production code
- `is_post_battle_ship()` (line 428) - never called by production code

Note: The TypeGuard functions `is_star()`, `is_planet()`, `is_fleet()`, `is_warp_point()`, `is_star_system()`, `is_sector_environment()`, `is_combatant()` ARE used by production code and should be kept.
**Impact:** Protocol classes that are defined but never used as type annotations add dead code bulk. The TypeGuard functions that are never called represent unused API surface.
**Recommendation:** Keep the Protocol classes that back used TypeGuard functions (IFleet, IPlanet, ICombatant, IStarSystem, IStar, IWarpPoint, ISectorEnvironment, IScene, ICamera, IRegistryProvider, IPostBattleShip). Remove the Protocol classes that are never used anywhere: `ILocatable`, `INamed`, `IOwnable`, `IDamageable`. Remove TypeGuard functions that are never called: `is_resource_reader()`, `is_resource_holder()`, `is_camera()`, `is_post_battle_ship()`.
**Effort:** Simple

#### MINOR: `LayerType.from_string()` Static Method Never Called
**ID:** LEG-FND-006
**Location:** `game/core/constants.py:117-119`
**Issue:** `LayerType.from_string()` is a static method that converts a string to a `LayerType` enum via `getattr()`. A codebase-wide search finds zero callers of this method in production or test code.
**Impact:** Small amount of dead code.
**Recommendation:** Delete the method.
**Effort:** Simple

#### MINOR: `ScreenshotManager.capture_step()` Never Called from Production Code
**ID:** LEG-FND-007
**Location:** `game/core/screenshot_manager.py:118-124`
**Issue:** The `capture_step()` method is defined but never called from any production code. It is only referenced in one test file (`tests/unit/test_screenshot_manager.py`). This appears to be a debugging utility that was added but never wired into any render pipeline.
**Impact:** Dead code. The method is trivial (one-line wrapper around `capture()`), so impact is minimal.
**Recommendation:** Delete the method and its test.
**Effort:** Simple

#### MINOR: Python 3.9 Compatibility Shim for TypeGuard in protocols.py
**ID:** LEG-FND-008
**Location:** `game/core/protocols.py:32-36`
**Issue:** The try/except block at lines 33-36 falls back to `typing_extensions.TypeGuard` for Python 3.9 compatibility. The project uses Python 3.x (CLAUDE.md) but `TypeGuard` was added to `typing` in Python 3.10. If the project targets 3.10+, this fallback is dead code. If it targets 3.9, this is still needed.
**Impact:** Minor if Python 3.10+ is the minimum. If the project has moved to 3.10+, this is a compatibility shim that should be removed per project policy.
**Recommendation:** Verify minimum Python version. If 3.10+, remove the try/except and import directly from `typing`.
**Effort:** Simple

#### MINOR: Color Constants (WHITE, BLACK, BLUE, RED, GREEN) Barely Used
**ID:** LEG-FND-009
**Location:** `game/core/constants.py:42-46`
**Issue:** The color constants `WHITE`, `BLACK`, `BLUE`, `RED`, `GREEN` are defined in the core constants module and exported in `__all__`. However, only one production file imports any of them from here (`game/ui/screens/test_lab/screen.py` imports WHITE and BLACK). Most UI code defines colors inline or in local constants. These appear to be holdovers from early development before the UI patterns solidified.
**Impact:** Low. They are exported and technically available but essentially unused.
**Recommendation:** Consider removing from `__all__` export and eventually from the constants module if no callers remain.
**Effort:** Simple

#### MINOR: `json` Import in resources.py Only Needed for Backward Compat Function
**ID:** LEG-FND-010
**Location:** `game/core/resources.py:13`
**Issue:** `import json` at line 13 is only used in the exception handlers of `load_resources()` (the backward compat wrapper) to catch `json.JSONDecodeError`. The DI function `load_resources_data()` also catches `json.JSONDecodeError` but via the same `import json`. If `load_resources()` is removed (LEG-FND-001), the `import json` can also be removed since `load_json_required()` from `json_utils` handles JSON parsing internally.
**Impact:** Minimal. Cleanup dependency of the backward compat function.
**Recommendation:** Remove alongside LEG-FND-001.
**Effort:** Simple (part of LEG-FND-001 cleanup)

#### MINOR: `_get_hp_percent` and `_is_in_pdc_arc` Wrapper Methods on AIController
**ID:** LEG-FND-011
**Location:** `game/ai/controller.py:269-273`
**Issue:** `AIController._get_hp_percent()` and `_is_in_pdc_arc()` are trivial one-line wrappers that delegate to `combat_utils.get_hp_percent()` and `combat_utils.is_in_pdc_arc()` respectively. They were likely created during PROJ-108 Phase 3 when combat utils were extracted, as a migration shim to avoid changing all callers at once. Only one production caller uses each (`_get_hp_percent` at line 332, `_is_in_pdc_arc` is not called in production). Some tests mock these wrapper methods directly.
**Impact:** Unnecessary indirection. `_is_in_pdc_arc()` is never called by production code at all.
**Recommendation:** Replace the `_get_hp_percent` call at line 332 with direct `get_hp_percent(self.ship)`. Delete both wrapper methods. Update test mocks.
**Effort:** Simple (but requires test updates)

#### MINOR: `FONT_MAIN` Constant Defined but Unused by Core/Foundation
**ID:** LEG-FND-012
**Location:** `game/core/constants.py:49`
**Issue:** `FONT_MAIN = "Arial"` is defined as a core constant and exported in `__all__`. However, it is only used by a handful of test_lab UI files. Most UI code that uses fonts either hardcodes "Arial" directly or uses `pygame.font.SysFont("Arial", ...)`. The constant exists but is not consistently used, suggesting it was an early attempt at font centralization that was never fully adopted.
**Impact:** Low. The constant is not wrong, but its inconsistent adoption means it provides little value.
**Recommendation:** Either enforce its use across all UI code or remove it if the project prefers local font definitions.
**Effort:** Simple

#### INFO: `DEBUG_SCREENSHOTS = True` Always Enabled
**ID:** LEG-FND-013
**Location:** `game/core/constants.py:53`
**Issue:** `DEBUG_SCREENSHOTS` is hardcoded to `True`. This flag controls whether `ScreenshotManager` is enabled. There is no configuration mechanism to toggle it off. If screenshots are always desired, the flag and the conditional check in `ScreenshotManager.__init__` are unnecessary. If they should be configurable, the value should come from a settings file or environment variable.
**Impact:** Informational. The flag has no practical effect since it is always True.
**Recommendation:** Either make it configurable (via settings/environment) or remove the flag and the conditional logic in ScreenshotManager.
**Effort:** Simple

#### INFO: `profiling.py` Comment References "backwards compatibility"
**ID:** LEG-FND-014
**Location:** `game/core/profiling.py:104`
**Issue:** Line 104 contains the comment `# Global accessor for backwards compatibility (lazy, not module-level instantiation)`. The `profile_action` decorator function on the next line is actively used, so this is not dead code. However, the comment implies this was a transitional shim that has become permanent. The function is actually the primary API, not a compatibility layer.
**Impact:** Misleading comment suggests the function may be removed, when it is the canonical API.
**Recommendation:** Update the comment to remove the "backwards compatibility" language.
**Effort:** Simple

## Top 5 Priority Issues

1. **LEG-FND-001 (CRITICAL):** `load_resources()` backward compatibility wrapper - active compat shim that duplicates logic and bypasses DI. Violates project migration policy.
2. **LEG-FND-002 (MAJOR):** StrategyMetadataService hand-rolled singleton - inconsistent pattern when SingletonMeta exists for exactly this purpose.
3. **LEG-FND-004 (MAJOR):** Duplicate path resolution in resources.py - manual project root calculation duplicates Paths class.
4. **LEG-FND-003 (MAJOR):** Dead `attack_state`/`attack_timer` on AIController - confusing leftover from pre-behavior-extraction architecture.
5. **LEG-FND-005 (MAJOR):** Unused protocol classes and TypeGuard functions - dead API surface adding bulk to the protocol module.
