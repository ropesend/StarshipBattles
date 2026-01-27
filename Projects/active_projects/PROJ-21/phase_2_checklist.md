# Phase 2: Exception Type Standardization

**Objective:** Replace generic Exception with RuntimeError for singleton violations
**Status:** Not Started
**Complexity:** Simple

## Tasks

### Task 2.1: Update Profiler singleton exception [Simple]
**File:** `game/core/profiling.py`
**Tests:** `pytest tests/ -k profil -v`

- [ ] Line 35: Change `raise Exception("Profiler is a singleton. Use Profiler.instance()")`
      to `raise RuntimeError("Profiler is a singleton. Use Profiler.instance()")`
- [ ] Verify no tests depend on exact exception type (grep for `except Exception`)

**Notes:**

---

### Task 2.2: Update RegistryManager singleton exception [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/ -k registry -v`

- [ ] Line 66: Change `raise Exception("RegistryManager is a singleton. Use RegistryManager.instance()")`
      to `raise RuntimeError("RegistryManager is a singleton. Use RegistryManager.instance()")`
- [ ] Verify no tests depend on exact exception type

**Notes:**

---

### Task 2.3: Update ScreenshotManager singleton exception [Simple]
**File:** `game/core/screenshot_manager.py`
**Tests:** `pytest tests/ -k screenshot -v`

- [ ] Line 27: Change `raise Exception("ScreenshotManager is a singleton. Use ScreenshotManager.instance()")`
      to `raise RuntimeError("ScreenshotManager is a singleton. Use ScreenshotManager.instance()")`
- [ ] Verify no tests depend on exact exception type

**Notes:**

---

## Phase 2 Verification
- [ ] All 3 singleton classes now raise RuntimeError instead of Exception
- [ ] `pytest tests/ -k "profil or registry or screenshot" -v` passes
- [ ] No tests catch generic Exception for these singletons
