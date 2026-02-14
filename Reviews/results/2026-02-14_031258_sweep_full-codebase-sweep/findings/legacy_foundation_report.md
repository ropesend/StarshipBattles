# Legacy System Holdovers Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 37
- **Total Issues Found:** 10
- **Critical:** 0 | **Major:** 4 | **Minor:** 5 | **Info:** 1

## Findings

#### MAJOR: Unused Error Codes in error_codes.py
**ID:** LEG-FND-001
**Location:** `game/core/error_codes.py:82-109`
**Issue:** Multiple ErrorCode enum values are defined but never used anywhere in the codebase. The following codes have no usages outside their definition file:
- RESOURCE_LOAD_FAILED (R003)
- SAVE_FAILED (P001)
- LOAD_FAILED (P002)
- IO_ERROR (P005)
- VERSION_MISMATCH (P004)
- FORMULA_SYNTAX_ERROR (F001)
- FORMULA_UNDEFINED_VAR (F002)
- EVAL_ERROR (F003)
- FORMULA_GENERAL_ERROR (F004)
- COMPONENT_NOT_FOUND (C001)
- INVALID_FORMAT (R002)
**Impact:** Code bloat and maintenance burden. Developers may think these codes are actively used when they are not, creating confusion about the error handling architecture.
**Recommendation:** Either remove unused error codes or ensure they are used consistently when raising exceptions. FormulaException is raised but uses ad-hoc error messages instead of standardized codes.
**Effort:** Simple

#### MAJOR: Singleton Pattern Pervasive Despite DI Push
**ID:** LEG-FND-002
**Location:** `game/core/singleton.py` and 9 dependent files
**Issue:** The project has moved toward dependency injection (PROJ-27, PROJ-50) but still maintains a SingletonMeta metaclass actively used by 9 classes:
- Logger, Profiler, RegistryManager, StrategyManager (core/ai)
- AssetManager, SpriteManager, ShipThemeManager, ScreenshotManager (ui layer)
- StrategyMetadataService
The policy states "Dependency injection replaced singletons in many areas" but the singleton infrastructure is still heavily used, creating inconsistent patterns.
**Impact:** Inconsistent architecture - some services use DI while others use singletons. Makes testing harder and creates confusion about which pattern to use for new code.
**Recommendation:** Document explicitly which services should remain singletons (Logger, Profiler are reasonable) vs. which should migrate to DI. Consider deprecating SingletonMeta for service classes that could be injected.
**Effort:** Complex

#### MAJOR: Defensive getattr Fallbacks in AI Module
**ID:** LEG-FND-003
**Location:** `game/ai/controller.py:125-127, 391, 411, 420` and `game/ai/target_evaluator.py:87, 118, 166, 184, 194`
**Issue:** Extensive use of `getattr(obj, 'attribute', default)` patterns to defensively access entity attributes. Comments indicate these are for "robustness" but the codebase has well-defined protocols (ICombatant, IPostBattleShip) that should guarantee these attributes exist.
Examples:
- `getattr(obj, 'type', '') == 'missile'` - should use protocol
- `getattr(candidate, 'mass', 100)` - mass should be required by protocol
- `getattr(comp, 'current_hp', 1)` - components should always have hp
**Impact:** Creates ambiguity about which attributes are required vs. optional. Masks bugs where entities don't implement expected interfaces. Makes it harder to add type checking.
**Recommendation:** Strengthen protocols to require these attributes, then remove defensive getattr patterns. Use TypeGuard functions consistently.
**Effort:** Medium

#### MAJOR: Strategy Fallback Patterns in AI Documentation
**ID:** LEG-FND-004
**Location:** `game/ai/__init__.py:38-48`
**Issue:** The AI module docstring explicitly documents "Fallback Behaviors" as a design pattern, listing fallback strategies when AI operations fail. While defensive programming is appropriate, the explicit documentation of fallback behaviors suggests the system was designed to work around unreliable interfaces rather than fixing them.
**Impact:** Normalizes partial failures rather than treating them as bugs. Encourages addition of more fallbacks rather than fixing root causes.
**Recommendation:** Review each documented fallback. If the underlying issue is fixable, fix it. If fallbacks are truly necessary for edge cases, document them as exception handling, not as expected behavior.
**Effort:** Medium

#### MINOR: Unused hex_lerp and hex_linedraw Functions
**ID:** LEG-FND-005
**Location:** `game/core/hex_math.py:224-250`
**Issue:** Functions `hex_lerp` and `hex_linedraw` are only used within hex_math.py itself and by `game/strategy/data/pathfinding.py`. The functions exist to support potential pathfinding visualization or smooth movement interpolation but may not be actively used features.
**Impact:** Minimal - functions are small and may be useful for future features.
**Recommendation:** Verify these are used by pathfinding. If pathfinding is incomplete/unused, consider removing these helper functions.
**Effort:** Simple

#### MINOR: is_camera TypeGuard Never Used
**ID:** LEG-FND-006
**Location:** `game/core/protocols.py:577-579`
**Issue:** The `is_camera` TypeGuard function is defined but never called anywhere in the codebase. The ICamera protocol is used (via TYPE_CHECKING imports), but the runtime check function is unused.
**Impact:** Minor dead code.
**Recommendation:** Remove `is_camera` if not needed, or use it where ICamera conformance should be checked at runtime.
**Effort:** Simple

#### MINOR: Profiling Module Has Inconsistent API
**ID:** LEG-FND-007
**Location:** `game/core/profiling.py:63-64`
**Issue:** The Profiler class has both `is_active()` method and `active` attribute. The method is used by decorators while the attribute is set directly by start()/stop(). This creates two ways to check the same state.
**Impact:** Minor inconsistency. Could lead to bugs if someone checks `profiler.active` vs `profiler.is_active()`.
**Recommendation:** Make `active` private (`_active`) and use only `is_active()` as the public API.
**Effort:** Simple

#### MINOR: Mock Detection Pattern in combat_utils
**ID:** LEG-FND-008
**Location:** `game/ai/combat_utils.py:44`
**Issue:** Line contains `if hasattr(obj, '_mock_name') or hasattr(obj, 'assert_called'):` which is runtime detection of mock objects. This test-specific logic has leaked into production code.
**Impact:** Production code contains test-framework-specific checks. Could cause issues if mock library changes attribute names.
**Recommendation:** Use a separate test-specific implementation or configure mocks to satisfy the actual interface requirements.
**Effort:** Simple

#### MINOR: PROJ Comments Reference Old Project Numbers
**ID:** LEG-FND-009
**Location:** Multiple files including `game/core/constants.py:41`, `game/core/__init__.py:107`, `game/research/data/research_tracker.py:119`
**Issue:** Comments reference PROJ-11, PROJ-17, PROJ-40, PROJ-113, PROJ-121, etc. These project numbers document historical context but add clutter. Some are useful (explain why code is structured a certain way) while others are simple changelog entries that should be in git history.
**Impact:** Code comments become cluttered with historical project references rather than explaining current intent.
**Recommendation:** Keep PROJ comments that explain architectural decisions (e.g., "PROJ-113: UIConfig moved to game.ui.config"). Remove PROJ comments that are purely changelog entries (e.g., "PROJ-121: Renamed from DEBUG_SCREENSHOTS").
**Effort:** Simple

#### INFO: Singleton Pattern is Intentional for Infrastructure
**ID:** LEG-FND-010
**Location:** `game/core/singleton.py`
**Issue:** The SingletonMeta usage for Logger, Profiler, and RegistryManager appears intentional - these are application-wide infrastructure services where singleton access makes sense. The DI vs Singleton question from LEG-FND-002 may be resolved by documenting which pattern applies where.
**Impact:** None if documented properly.
**Recommendation:** Add docstring to SingletonMeta explaining intended use cases (infrastructure services) vs. recommended DI patterns (domain services).
**Effort:** Simple

## Top 5 Priority Issues

1. **LEG-FND-001 (MAJOR):** Unused Error Codes - 11 error codes defined but never used. Either use them consistently or remove them to reduce confusion.

2. **LEG-FND-002 (MAJOR):** Singleton vs DI inconsistency - Document which services should use which pattern. Current state creates confusion about architectural direction.

3. **LEG-FND-003 (MAJOR):** Defensive getattr patterns - AI code uses many defensive fallbacks that mask missing protocol requirements. Strengthen protocols instead.

4. **LEG-FND-004 (MAJOR):** Documented fallback behaviors - AI module normalizes failures as expected behavior rather than treating them as bugs to fix.

5. **LEG-FND-008 (MINOR):** Mock detection in production code - Test-specific logic has leaked into combat_utils.py.
