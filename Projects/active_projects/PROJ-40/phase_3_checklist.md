# Phase 3: Core Infrastructure Improvements

**Status:** Not Started
**Estimated Effort:** 4-5 hours
**Priority:** Medium-High

## Overview
Address issues in `game/core/` infrastructure modules to improve maintainability, testability, and documentation.

---

## Tasks

### 3.1 Fix Global State in Logger (NEW-CORE-002)
**Location:** `game/core/logger.py:65, 83`
**Effort:** Medium

- [ ] Create lazy initialization pattern for `_logger`
- [ ] Use `_LoggerProxy` pattern similar to `_ProfilerProxy` in profiling.py
- [ ] Delay file handler creation until first log call
- [ ] Add `reset()` method for test isolation
- [ ] Run: `pytest tests/unit/ -v --tb=short`

---

### 3.2 Document Registry Providers (NEW-CORE-003)
**Location:** `game/core/registry.py:250-344`
**Effort:** Simple

- [ ] Add `DefaultRegistryProvider` to `__all__` in registry.py
- [ ] Add `TestRegistryProvider` to `__all__` in registry.py
- [ ] Export `get_default_registry_provider()` function
- [ ] Update module docstring to document TIER 3 (PROJ-27 DI pattern)
- [ ] Add usage examples in docstring

---

### 3.3 Consolidate Default Resources (NEW-CORE-004)
**Location:** `game/core/resources.py:13-40, 41-60`
**Effort:** Simple

- [ ] Define `DEFAULT_RESOURCES` constant at module level
- [ ] Update first fallback path (lines 33-37) to use constant
- [ ] Update second fallback path (lines 55-59) to use constant
- [ ] Extract path resolution into `_resolve_resource_path()` helper
- [ ] Run: `pytest tests/unit/ -v -k resource`

---

### 3.4 Extract Input Handler Constants (NEW-CORE-005)
**Location:** `game/core/input_handler.py:27, 29, 31, 33`
**Effort:** Simple

- [ ] Create `SpeedConfig` dataclass or add to `game/core/config.py`
- [ ] Define named constants:
  - `MIN_SPEED_MULTIPLIER = 0.00390625` (1/256)
  - `MAX_SPEED_MULTIPLIER = 16.0`
  - `NORMAL_SPEED = 1.0`
  - `PAUSE_SPEED = 100.0` (max speed for UI)
- [ ] Add docstring explaining the speed scaling rationale
- [ ] Update input_handler.py to use new constants
- [ ] Run: `pytest tests/ -v -k input`

---

### 3.5 Extract Singleton Base Class (NEW-CORE-006)
**Location:** Multiple files
**Effort:** Medium

- [ ] Create `game/core/singleton.py` with `SingletonMeta` metaclass
- [ ] Implement double-checked locking pattern
- [ ] Add `_reset()` method for test isolation
- [ ] Refactor `Logger` to use `SingletonMeta`
- [ ] Refactor `Profiler` to use `SingletonMeta`
- [ ] Refactor `ScreenshotManager` to use `SingletonMeta`
- [ ] Run: `pytest tests/ -v`

---

### 3.6 Add Type Hints to Validation Properties (NEW-CORE-007)
**Location:** `game/core/validation.py:60-72, 84-95, 105-117`
**Effort:** Simple

- [ ] Add return type annotation to `message` property
- [ ] Add return type annotation to `is_valid` property
- [ ] Add return type annotation to `errors` property
- [ ] Run mypy if available: `mypy game/core/validation.py`

---

### 3.7 Fix Screenshot Manager Security (NEW-CORE-010)
**Location:** `game/core/screenshot_manager.py:117-132`
**Effort:** Medium

- [ ] Replace `os.system()` with `subprocess.run()`
- [ ] Properly escape text for clipboard command
- [ ] Add platform detection for clipboard handling
- [ ] Test on Windows with special characters in path
- [ ] Consider using `pyperclip` library if available

---

### 3.8 Complete json_utils Docstring (NEW-CORE-011)
**Location:** `game/core/json_utils.py:1-17`
**Effort:** Simple

- [ ] Update module docstring to list all 4 functions
- [ ] Document `encoding` parameter
- [ ] Document `ensure_ascii` behavior
- [ ] Add example for each function

---

## Verification

- [ ] Run full core tests: `pytest tests/unit/core/ -v`
- [ ] Import check: `python -c "from game.core import *"`
- [ ] Optional: Run type checker on core module

---

## Notes
- Task 3.5 (singleton refactor) has the most risk - test thoroughly
- Task 3.7 (security fix) should be prioritized if screenshots are used
- Consider adding unit tests for any new utility classes created
