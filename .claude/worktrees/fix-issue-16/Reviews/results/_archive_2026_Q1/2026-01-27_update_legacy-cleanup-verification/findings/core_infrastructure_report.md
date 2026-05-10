# Core Infrastructure Scout Report

## Summary
- Files Reviewed: 14
- Issues Found: 11
- Critical: 1, Major: 4, Minor: 6, Info: 0

---

## Findings

### CRITICAL: Layer Violation in protocols.py
**ID:** NEW-CORE-001
**Location:** `game/core/protocols.py:37`
**Issue:** Core module imports from strategy layer at module level (inside TYPE_CHECKING block). The import `from game.strategy.data.hex_math import HexCoord` violates the layering principle where core should not depend on higher-level layers, even for type hints.
**Impact:** Creates subtle coupling between core and strategy modules. If HexCoord changes, core module must update. Violates dependency inversion principle.
**Recommendation:** Define HexCoord-like protocol in core module (ICoordinate) or use forward references/strings for type annotations. Keep core layer truly independent.
**Effort:** Medium

---

### MAJOR: Global State in logger.py
**ID:** NEW-CORE-002
**Location:** `game/core/logger.py:65, 83`
**Issue:** Module-level global state created at import time: `_logger = Logger()` and `_event_handler = None`. The Logger singleton is instantiated immediately when module is imported, creating a global logging instance that cannot be easily replaced for testing.
**Impact:** Difficult to mock logger in tests, particularly in parallel test execution. File handler is created immediately even if logging is disabled.
**Recommendation:** Use lazy initialization pattern (like profiling.py uses _ProfilerProxy) or dependency injection. Make logger a property function instead of module-level global.
**Effort:** Medium

---

### MAJOR: Undocumented Feature in registry.py
**ID:** NEW-CORE-003
**Location:** `game/core/registry.py:250-344`
**Issue:** DefaultRegistryProvider and TestRegistryProvider classes (lines 253-323) are part of PROJ-27 but have no clear discovery path from public API. The `get_default_registry_provider()` function is not exported in `__init__.py` and not mentioned in module docstring's TIER system.
**Impact:** New developers won't find these provider implementations when looking for dependency injection patterns. The pattern is invisible to casual code review.
**Recommendation:** Add DefaultRegistryProvider and TestRegistryProvider to __all__ export list in registry.py. Update module docstring to document PROJ-27 as TIER 3 (Domain Services with DI).
**Effort:** Simple

---

### MAJOR: Inconsistent Error Handling in resources.py
**ID:** NEW-CORE-004
**Location:** `game/core/resources.py:13-40, 41-60`
**Issue:** load_resources() has two separate fallback patterns that repeat default_resources definition (lines 33-37 and 55-59). If default resources need to change, they must be updated in two places.
**Impact:** Code duplication creates maintenance burden and risk of inconsistent defaults. Difficult to understand intended behavior.
**Recommendation:** Define DEFAULT_RESOURCES constant at module level, use in both fallback paths. Extract path resolution logic into separate function.
**Effort:** Simple

---

### MAJOR: Hard-coded Magic Numbers in input_handler.py
**ID:** NEW-CORE-005
**Location:** `game/core/input_handler.py:27, 29, 31, 33`
**Issue:** Speed multiplier constants are hard-coded as magic numbers: 0.00390625, 16.0, 1.0, 100.0. No justification for these specific values, and they cannot be configured.
**Impact:** Cannot adjust game speed behavior without code changes. Values appear arbitrary without documentation of their purpose.
**Recommendation:** Move to InputConfig class in game/core/config.py with named constants (MIN_SPEED_MULTIPLIER, MAX_SPEED_MULTIPLIER, NORMAL_SPEED, MAX_SPEED). Document rationale.
**Effort:** Simple

---

### MINOR: Singleton Pattern Duplication
**ID:** NEW-CORE-006
**Location:** `game/core/logger.py:7-32, game/core/profiling.py:14-57, game/core/screenshot_manager.py:8-44`
**Issue:** Three separate singleton implementations with identical double-checked locking pattern. Code duplication across Logger, Profiler, and ScreenshotManager increases maintenance burden.
**Impact:** Bug fixes to singleton pattern must be applied in three places. Inconsistency in reset() behavior and implementation details.
**Recommendation:** Extract singleton metaclass or base class to game/core/singleton.py. Use it in all three classes to reduce duplication.
**Effort:** Medium

---

### MINOR: Missing Type Hints in validation.py
**ID:** NEW-CORE-007
**Location:** `game/core/validation.py:60-72, 84-95, 105-117`
**Issue:** Public class methods `create()`, `add_error()`, `add_warning()`, and `merge()` use proper type hints, but they're inconsistent with the property methods `message` (line 74) which returns `str` without annotating return type on the property itself.
**Impact:** Type checkers may not properly infer return types of properties. IDE autocomplete less accurate for property access.
**Recommendation:** Add explicit return type annotations to @property methods. Add type: ignore comments if type checker has issues with property declarations.
**Effort:** Simple

---

### MINOR: Dead Code Pattern in input_handler.py
**ID:** NEW-CORE-008
**Location:** `game/core/input_handler.py:5, 11-34`
**Issue:** InputHandler class is a static-only utility class with all methods marked @staticmethod. The class itself serves no purpose and makes the code harder to test (cannot inject dependencies). Only `handle_keydown` is called (line 15 references _handle_battle_keydown).
**Impact:** Cannot easily mock or test InputHandler behavior. Violates dependency injection patterns used elsewhere in codebase.
**Recommendation:** Convert to functions or inject as dependency. Document why class wrapper is needed if it serves a purpose.
**Effort:** Simple

---

### MINOR: Unused Parameter Validation in config.py
**ID:** NEW-CORE-009
**Location:** `game/core/config.py:221-229`
**Issue:** TestConfig class defines DEFAULT_TIMEOUT_MS and LONG_TIMEOUT_MS but no code validates these values are reasonable. DEFAULT_RANDOM_SEED value (42) is not documented why this specific seed was chosen.
**Impact:** Magic values without clear purpose. Difficult to understand testing philosophy or adjust test timeouts consistently.
**Recommendation:** Add docstring comments explaining purpose of each TestConfig value. Consider making timeouts configurable via environment variables.
**Effort:** Simple

---

### MINOR: Screenshot Manager Path Handling
**ID:** NEW-CORE-010
**Location:** `game/core/screenshot_manager.py:117-132`
**Issue:** _copy_to_clipboard() uses os.system() with echo command for Windows clipboard fallback (line 132). This is vulnerable to shell injection if text contains special characters or quotes.
**Impact:** Security vulnerability: screenshot paths with special characters could execute arbitrary commands. The echo command is also Windows-specific and would fail on other platforms.
**Recommendation:** Use subprocess.run() with proper escaping instead of os.system(). Better yet, use pyperclip or similar library if available. Handle platform differences explicitly.
**Effort:** Medium

---

### MINOR: Incomplete Docstring in json_utils.py
**ID:** NEW-CORE-011
**Location:** `game/core/json_utils.py:1-17`
**Issue:** Module docstring lists 3 functions in examples but there are actually 4 functions: load_json, load_json_required, save_json, and the error handling is incomplete. No mention of encoding parameter or ensure_ascii behavior in module docstring.
**Impact:** Developers reading module docstring won't understand all available functions or their parameters. Documentation doesn't match implementation.
**Recommendation:** Update module docstring to include all functions and key parameters. Add examples for encoding and ensure_ascii options.
**Effort:** Simple

---

## Files Reviewed

1. `game/core/__init__.py`
2. `game/core/config.py`
3. `game/core/constants.py`
4. `game/core/input_handler.py`
5. `game/core/json_utils.py`
6. `game/core/logger.py`
7. `game/core/math.py`
8. `game/core/paths.py`
9. `game/core/profiling.py`
10. `game/core/protocols.py`
11. `game/core/registry.py`
12. `game/core/resources.py`
13. `game/core/screenshot_manager.py`
14. `game/core/validation.py`

---

**Report Generated:** 2026-01-27
**Scout:** Core Infrastructure Scout
**Coverage:** 100% (14/14 files)
