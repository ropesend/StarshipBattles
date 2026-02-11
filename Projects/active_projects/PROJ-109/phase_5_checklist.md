# Phase 5: Foundation Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-109 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Clean up foundation-layer proxy patterns (Logger, Profiler). These are cross-cutting changes that touch many files or have subtle initialization implications.

---

## Tasks

### Task 5.1: Remove Logger module-level global proxy [Medium]
**Finding:** LEG-FND-002
**File:** `game/core/logger.py:68-81`
**Tests:** `pytest tests/ -n 12` (broad impact)

The module-level `_logger = Logger()` global is instantiated at import time, bypassing the `Logger.instance()` singleton pattern. The convenience functions `log_debug/log_info/log_warning/log_error` are imported by 109 files and must be preserved.

- [ ] Remove `_logger = Logger()` (line 69)
- [ ] Rewrite `log_debug()` to call `Logger.instance().log(msg)` instead of `_logger.log(msg)`
- [ ] Rewrite `log_info()` to call `Logger.instance().info(msg)` instead of `_logger.info(msg)`
- [ ] Rewrite `log_warning()` to call `Logger.instance().warning(msg)` instead of `_logger.warning(msg)`
- [ ] Rewrite `log_error()` to call `Logger.instance().error(msg)` instead of `_logger.error(msg)`
- [ ] Rewrite `set_logging()` to call `Logger.instance().set_enabled(enabled)` instead of `_logger.set_enabled(enabled)`
- [ ] Verify: `Logger.instance()` uses double-checked locking (it does via `__new__`)
- [ ] Verify: no code references `_logger` directly (outside logger.py)
- [ ] Commit: "PROJ-109: Remove Logger module-level global, use instance() in proxies"

**Notes:** The convenience functions are preserved with identical signatures. The only change is the internal implementation. This should be transparent to all 109 callers.

---

### Task 5.2: Remove Profiler proxy class [Medium]
**Finding:** LEG-FND-003
**File:** `game/core/profiling.py:135-146`
**Callers:**
- `game/core/profiling.py` itself (profile_action, profile_block decorators)
- `game/app.py`
- `tests/unit/core/profiling/test_decorators.py`
- `tests/unit/performance/test_profiler_perf.py`
**Tests:** `pytest tests/unit/core/profiling/ tests/unit/performance/ -n 12`

- [ ] Delete the `_ProfilerProxy` class (lines 136-143)
- [ ] Delete `PROFILER = _ProfilerProxy()` (line 146)
- [ ] In `profile_action()` decorator (line 149): Replace `PROFILER.is_active()` with `Profiler.instance().is_active()`
- [ ] In `profile_action()` decorator (line 162): Replace `PROFILER.record(...)` with `Profiler.instance().record(...)`
- [ ] In `profile_block()` context manager (line 170): Replace `PROFILER.is_active()` with `Profiler.instance().is_active()`
- [ ] In `profile_block()` context manager (line 179): Replace `PROFILER.record(...)` with `Profiler.instance().record(...)`
- [ ] In `game/app.py`: grep for `PROFILER.` and replace with `Profiler.instance().`
- [ ] In test files: update any `PROFILER.` references to `Profiler.instance().`
- [ ] Remove `# Global accessor for backwards compatibility` comment (line 135)
- [ ] Commit: "PROJ-109: Remove _ProfilerProxy, use Profiler.instance() directly"

**Notes:**

---

### Task 5.3: Remove unused target_evaluator parameters [Simple]
**Finding:** LEG-FND-005
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/ -n 12`

- [ ] Audit helper methods for unused `stat_helpers` and `ship_capabilities_cache` parameters
- [ ] For each method: check if `stat_helpers` is ever used (not just `if stat_helpers:` checks)
- [ ] For each method: check if `ship_capabilities_cache` is ever used
- [ ] Remove truly unused parameters from signatures
- [ ] Update any callers that pass these parameters
- [ ] Verify: no behavioral change (parameters defaulted to None and were unused)

**Notes:** This task requires careful audit. Only remove parameters that are definitively unused.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ -n 12` passes (8164 baseline)
- [ ] No `_logger` global in logger.py
- [ ] No `_ProfilerProxy` class in profiling.py
- [ ] No `PROFILER` global in profiling.py
- [ ] No "backward compat" comments in modified files
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
