# Phase 3: Core Infrastructure Improvements

**Status:** Complete
**Estimated Effort:** 3-4 hours
**Priority:** Medium-High

## Overview
Address issues in `game/core/` infrastructure modules to improve maintainability, testability, and documentation.

> **Note:** This phase was reduced from 8 tasks to 6 after Category 3 audit verification:
> - Task 3.1 (NEW-CORE-002) REMOVED - Proper singleton + event dispatcher pattern
> - Task 3.5 (NEW-CORE-006) REMOVED - Singleton pattern already implemented correctly

---

## Tasks

### 3.1 Document Registry Providers (NEW-CORE-003)
**Location:** `game/core/registry.py:250-344`
**Effort:** Simple

- [x] Add `DefaultRegistryProvider` to `__all__` in registry.py
- [x] Add `TestRegistryProvider` to `__all__` in registry.py
- [x] Export `get_default_registry_provider()` function
- [x] Update module docstring to document TIER 3 (PROJ-27 DI pattern)
- [x] Add usage examples in docstring

**Notes:** Added comprehensive `__all__` list and updated docstring with TIER 3 DI pattern examples.

---

### 3.2 Consolidate Default Resources (NEW-CORE-004)
**Location:** `game/core/resources.py:13-40, 41-60`
**Effort:** Simple

- [x] Define `DEFAULT_RESOURCES` constant at module level
- [x] Update first fallback path (lines 33-37) to use constant
- [x] Update second fallback path (lines 55-59) to use constant
- [x] Extract path resolution into `_resolve_resource_path()` helper
- [x] Run: `pytest tests/unit/ -v -k resource`

**Notes:** Created `_resolve_resource_path()` helper to eliminate duplicate path resolution code. Both `load_resources_data()` and `load_resources()` now use this helper.

---

### 3.3 Extract Input Handler Constants (NEW-CORE-005)
**Location:** `game/core/input_handler.py:27, 29, 31, 33`
**Effort:** Simple

- [x] Create named constants at module level
- [x] Define `MIN_SPEED_MULTIPLIER = 0.00390625` (1/256)
- [x] Define `MAX_SPEED_MULTIPLIER = 16.0`
- [x] Define `NORMAL_SPEED = 1.0`
- [x] Define `UI_PAUSE_SPEED = 100.0` (renamed from PAUSE_SPEED for clarity)
- [x] Add docstring explaining the speed scaling rationale
- [x] Update input_handler.py to use new constants

**Notes:** Added constants with clear comments explaining the values (min is 1/256 for slow-mo, max is 16x fast-forward).

---

### 3.4 Add Type Hints to Validation Properties (NEW-CORE-007)
**Location:** `game/core/validation.py:60-72, 84-95, 105-117`
**Effort:** Simple

- [x] Add return type annotation to `message` property
- [x] Add return type annotation to `is_valid` property
- [x] Add return type annotation to `errors` property
- [x] Run mypy if available: `mypy game/core/validation.py`

**Notes:** VERIFIED - Already complete. All properties and methods already have proper type annotations. Dataclass fields have explicit types at lines 46-49.

---

### 3.5 Fix Screenshot Manager Security (NEW-CORE-010)
**Location:** `game/core/screenshot_manager.py:117-132`
**Effort:** Medium

- [x] Replace `os.system()` with `subprocess.run()`
- [x] Properly escape text for clipboard command
- [x] Add platform detection for clipboard handling
- [x] Test on Windows with special characters in path
- [x] Consider using `pyperclip` library if available

**Notes:** Replaced `os.system(f'echo {text}| clip')` with `subprocess.run(['clip'], input=text.encode())`. This avoids command injection vulnerabilities by passing text as stdin rather than shell command argument.

---

### 3.6 Complete json_utils Docstring (NEW-CORE-011)
**Location:** `game/core/json_utils.py:1-17`
**Effort:** Simple

- [x] Update module docstring to list all 4 functions
- [x] Document `encoding` parameter
- [x] Document `ensure_ascii` behavior
- [x] Add example for each function

**Notes:** VERIFIED - Already complete. Module has comprehensive docstrings with examples, including documentation for all parameters (`encoding`, `ensure_ascii`).

---

## Removed Tasks (Audit Verification)

### ~~3.1 Fix Global State in Logger (NEW-CORE-002)~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** The logger implementation uses proper singleton + event dispatcher pattern:
- Line 65: `_logger = Logger()` - Controlled singleton with thread safety
- Line 83: `_event_handler = None` - Event callback registry with proper mutation
- Has `reset()` method for test isolation

### ~~3.5 Extract Singleton Base Class (NEW-CORE-006)~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** Logger, Profiler, and ScreenshotManager all correctly implement the singleton pattern already.

---

## Verification

- [x] Run full core tests: `pytest tests/unit/core/ -v`
- [x] Import check: `python -c "from game.core import *"`
- [x] Optional: Run type checker on core module

---

## Notes
- Task 3.5 (security fix) should be prioritized if screenshots are used
- Consider adding unit tests for any new utility classes created
