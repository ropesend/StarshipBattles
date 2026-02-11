# Phase 1: SingletonMeta Metaclass Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-108 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create thread-safe SingletonMeta metaclass and exhaustive test coverage.
**Findings:** DUP-FND-001 (foundation)

---

## Tasks

### Task 1.1: Create SingletonMeta metaclass [Medium]
**File:** `game/core/singleton.py` (NEW)
**Tests:** `pytest tests/unit/core/test_singleton.py -v`

- [ ] Create `game/core/singleton.py` with `SingletonMeta` metaclass
- [ ] Implement `instance()` classmethod via metaclass `__call__` or explicit injection
  - Must use double-checked locking: check `_instances[cls]`, acquire per-class lock, recheck
  - Per-class lock stored in `SingletonMeta._locks` dict (auto-created on first access)
- [ ] Implement `reset()` classmethod: acquires lock, deletes from `_instances`
  - Must be thread-safe (acquire lock before clearing)
- [ ] Metaclass `__init__` (class creation time): auto-register lock for each new singleton class
- [ ] `__init__` of concrete classes must only run once (guard against re-init on `instance()` calls)
- [ ] Add `__all__ = ['SingletonMeta']` export

**Notes:** The metaclass must handle the case where `__init__` is called on every `instance()` call.
Use a `_initialized` flag per-instance or only call `__init__` on first creation.

### Task 1.2: Write exhaustive tests for SingletonMeta [Medium]
**File:** `tests/unit/core/test_singleton.py` (NEW)
**Tests:** `pytest tests/unit/core/test_singleton.py -v`

- [ ] Test: `instance()` returns same object on repeated calls
- [ ] Test: `instance()` calls `__init__` exactly once
- [ ] Test: `reset()` causes next `instance()` to create new object
- [ ] Test: `reset()` causes `__init__` to run again on next `instance()`
- [ ] Test: Two different singleton classes have independent instances
- [ ] Test: Two different singleton classes have independent reset behavior
- [ ] Test: Thread safety - concurrent `instance()` calls return same object
- [ ] Test: Thread safety - concurrent `reset()` + `instance()` don't crash
- [ ] Test: Subclass with `clear()` method works (preserves instance, clears data)
- [ ] Test: `__init__` with custom args (e.g., `def __init__(self): self.data = {}`)
- [ ] Test: Direct construction (e.g., `MyClass()`) raises or returns singleton
- [ ] Verify: `pytest tests/ -n 12` -- full suite still passes

**Notes:** Thread safety tests should use `concurrent.futures.ThreadPoolExecutor` with 10+ threads.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/core/test_singleton.py -v` passes
- [ ] `pytest tests/ -n 12` -- full suite passes (8164+ tests)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
