# Phase 2: Convert Singletons to SingletonMeta

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-108 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Convert 7 singleton classes to use SingletonMeta metaclass, removing ~175 lines of boilerplate.
**Findings:** DUP-FND-001, DUP-UI2-004
**Depends on:** Phase 1 (SingletonMeta must exist and pass tests)

---

## Tasks

### Task 2.1: Convert Profiler [Simple]
**File:** `game/core/profiling.py:14-68`
**Tests:** `pytest tests/unit/core/ -v -k profil`

- [ ] Add `from game.core.singleton import SingletonMeta` import
- [ ] Change class declaration to `class Profiler(metaclass=SingletonMeta):`
- [ ] Remove `_instance = None` class attribute (line 31)
- [ ] Remove `_lock = threading.Lock()` class attribute (line 32)
- [ ] Remove `__init__` guard: `if Profiler._instance is not None: raise RuntimeError(...)` (lines 35-36)
- [ ] Remove `instance()` classmethod (lines 43-57)
- [ ] Remove `reset()` classmethod (lines 59-68)
- [ ] Keep `clear()` method as-is (instance-level data reset)
- [ ] Remove `import threading` if no other usage
- [ ] Verify: `pytest tests/ -n 12` passes

**Callers of instance():** `game/core/profiling.py` (5 internal calls via module functions)
**Callers of reset():** test fixtures

### Task 2.2: Convert ScreenshotManager [Simple]
**File:** `game/core/screenshot_manager.py:10-58`
**Tests:** `pytest tests/ -n 12`

- [ ] Add `from game.core.singleton import SingletonMeta` import
- [ ] Change class declaration to `class ScreenshotManager(metaclass=SingletonMeta):`
- [ ] Remove `_instance = None` class attribute (line 24)
- [ ] Remove `_lock = threading.Lock()` class attribute (line 25)
- [ ] Remove `__init__` guard: `if ScreenshotManager._instance is not None: raise RuntimeError(...)` (lines 28-29)
- [ ] Remove `instance()` classmethod (lines 32-46)
- [ ] Remove `reset()` classmethod (lines 49-58)
- [ ] Remove `import threading` if no other usage
- [ ] Verify: `pytest tests/ -n 12` passes

**Callers of instance():** `game/core/screenshot_manager.py` (2 calls)

### Task 2.3: Convert StrategyManager [Simple]
**File:** `game/ai/strategy_manager.py:19-98`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] Add `from game.core.singleton import SingletonMeta` import
- [ ] Change class declaration to `class StrategyManager(metaclass=SingletonMeta):`
- [ ] Remove `_instance` class attribute (line 35)
- [ ] Remove `_lock = threading.Lock()` class attribute (line 36)
- [ ] Remove `__init__` guard: `if StrategyManager._instance is not None: raise StateException(...)` (lines 45-50)
- [ ] Remove `instance()` classmethod (lines 62-76)
- [ ] Remove `reset()` classmethod (lines 78-87)
- [ ] Keep `clear()` method as-is
- [ ] Remove `import threading` if no other usage
- [ ] Verify: `pytest tests/ -n 12` passes

**Callers of instance():** `game/ai/strategy_manager.py` (2 calls), `game/ai/controller.py` (1)

### Task 2.4: Convert AssetManager [Simple]
**File:** `game/assets/asset_manager.py:10-64`
**Tests:** `pytest tests/ -n 12`

- [ ] Add `from game.core.singleton import SingletonMeta` import
- [ ] Change class declaration to `class AssetManager(metaclass=SingletonMeta):`
- [ ] Remove `_instance = None` class attribute (line 25)
- [ ] Remove `_lock = threading.Lock()` class attribute (line 26)
- [ ] Remove `__init__` guard: `if AssetManager._instance is not None: raise StateException(...)` (lines 29-33)
- [ ] Remove `instance()` classmethod (lines 39-53)
- [ ] Remove `reset()` classmethod (lines 55-64)
- [ ] Keep `clear()` method as-is
- [ ] Remove `import threading` if no other usage
- [ ] Verify: `pytest tests/ -n 12` passes

**Callers of instance():** `game/assets/asset_manager.py` (3 calls), multiple UI files

### Task 2.5: Convert SpriteManager [Simple]
**File:** `game/ui/renderer/sprites.py:6-56`
**Tests:** `pytest tests/ -n 12`

- [ ] Add `from game.core.singleton import SingletonMeta` import
- [ ] Change class declaration to `class SpriteManager(metaclass=SingletonMeta):`
- [ ] Remove `_instance = None` class attribute (line 20)
- [ ] Remove `_lock = threading.Lock()` class attribute (line 21)
- [ ] Remove `__init__` guard: `if SpriteManager._instance is not None: raise Exception(...)` (lines 24-25)
- [ ] Remove `instance()` classmethod (lines 30-44)
- [ ] Remove `reset()` classmethod (lines 47-56)
- [ ] Remove `import threading` if no other usage
- [ ] Verify: `pytest tests/ -n 12` passes

**Callers of instance():** `game/ui/renderer/sprites.py` (2 calls), multiple UI files

### Task 2.6: Convert ShipThemeManager [Simple]
**File:** `game/ui/assets/ship_theme_manager.py:10-78`
**Tests:** `pytest tests/ -n 12`

- [ ] Add `from game.core.singleton import SingletonMeta` import
- [ ] Change class declaration to `class ShipThemeManager(metaclass=SingletonMeta):`
- [ ] Remove `_instance = None` class attribute (line 25)
- [ ] Remove `_lock = threading.Lock()` class attribute (line 26) -- the CLASS-level lock only
  - **Keep** `self._init_lock` and `self._io_lock` in `__init__` (line 67-68, for cache operations)
- [ ] Remove `__init__` guard: `if ShipThemeManager._instance is not None: raise StateException(...)` (lines 46-50)
- [ ] Remove `instance()` classmethod (lines 28-42)
- [ ] Keep `clear()` method as-is
- [ ] **Note:** No explicit `reset()` exists; SingletonMeta provides it automatically
- [ ] Remove `import threading` only if `_init_lock`/`_io_lock` don't use it (they do -- keep it)
- [ ] Verify: `pytest tests/ -n 12` passes

**Callers of instance():** `game/ui/assets/ship_theme_manager.py` (2 calls), multiple UI files

### Task 2.7: Convert RegistryManager [Medium]
**File:** `game/core/registry.py:123-210`
**Tests:** `pytest tests/unit/core/ -v && pytest tests/ -n 12`

This is the most complex singleton. Convert last after validating the pattern works.

- [ ] Add `from game.core.singleton import SingletonMeta` import
- [ ] Change class declaration to `class RegistryManager(metaclass=SingletonMeta):`
- [ ] Remove `_instance` class attribute (line 159)
- [ ] Remove `_lock = threading.Lock()` class attribute (line 160)
- [ ] Remove `__init__` guard: `if RegistryManager._instance is not None: raise StateException(...)` (lines 169-174)
- [ ] Remove `instance()` classmethod (lines 183-197)
- [ ] Remove `reset()` classmethod (lines 199-210)
- [ ] Keep `freeze()`, `hydrate()`, `clear()`, `set_validator()`, `_check_frozen()` as-is
- [ ] Remove `import threading` if no other usage in file
- [ ] Verify: `pytest tests/unit/core/ -v` passes
- [ ] Verify: `pytest tests/ -n 12` -- full suite passes

**Callers of instance():** `game/core/registry.py` (9 internal calls), `game/app.py` (1), `game/core/resources.py` (1), etc.
**Callers of reset():** `game/core/registry.py` (internally), test fixtures (`conftest.py`)

**Critical:** Ensure conftest.py fixtures still call `RegistryManager.reset()` successfully.
The metaclass provides this automatically, so no fixture changes should be needed.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 7 singleton classes use `metaclass=SingletonMeta`
- [ ] No class has its own `_instance`, `_lock`, `instance()`, or `reset()`
- [ ] `pytest tests/ -n 12` -- full suite passes (8164+ tests)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
