# Phase 5: Foundation Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-109 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Clean up foundation-layer proxy patterns (Logger, Profiler). These are cross-cutting changes that touch many files or have subtle initialization implications.

---

## Tasks

### Task 5.1: Remove Logger module-level global proxy [Medium]
**Finding:** LEG-FND-002
**File:** `game/core/logger.py:68-81`
**Tests:** `pytest tests/ -n 12` (broad impact)

The module-level `_logger = Logger()` global is instantiated at import time, bypassing the `Logger.instance()` singleton pattern. The convenience functions `log_debug/log_info/log_warning/log_error` are imported by 109 files and must be preserved.

- [x] Remove `_logger = Logger()` (line 69)
- [x] Rewrite `log_debug()` to call `Logger.instance().log(msg)` instead of `_logger.log(msg)`
- [x] Rewrite `log_info()` to call `Logger.instance().info(msg)` instead of `_logger.info(msg)`
- [x] Rewrite `log_warning()` to call `Logger.instance().warning(msg)` instead of `_logger.warning(msg)`
- [x] Rewrite `log_error()` to call `Logger.instance().error(msg)` instead of `_logger.error(msg)`
- [x] Rewrite `set_logging()` to call `Logger.instance().set_enabled(enabled)` instead of `_logger.set_enabled(enabled)`
- [x] Verify: `Logger.instance()` uses double-checked locking (now via SingletonMeta)
- [x] Verify: no code references `_logger` directly (outside logger.py)
- [x] Updated test files: test_singleton.py, test_logger_system.py

**Notes:** Converted Logger to use SingletonMeta metaclass for consistency with other singletons.

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

- [x] Delete the `_ProfilerProxy` class (lines 136-143)
- [x] Delete `PROFILER = _ProfilerProxy()` (line 146)
- [x] In `profile_action()` decorator: Use `Profiler.instance()` directly
- [x] In `profile_block()` context manager: Use `Profiler.instance()` directly
- [x] In `game/app.py`: replaced `PROFILER.` with `Profiler.instance().`
- [x] In test files: updated all `PROFILER.` references to `Profiler.instance().`
- [x] Remove `# Global accessor for backwards compatibility` comment

**Notes:** Updated test_decorators.py and test_profiler_perf.py to use Profiler.instance().

---

### Task 5.3: Remove unused target_evaluator parameters [Simple]
**Finding:** LEG-FND-005
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/ -n 12`

- [x] Audit helper methods for unused `stat_helpers` and `ship_capabilities_cache` parameters
- [x] For each method: check if `stat_helpers` is ever used (not just `if stat_helpers:` checks)
- [x] For each method: check if `ship_capabilities_cache` is ever used
- [x] Remove truly unused parameters from signatures: **NONE FOUND**
- [x] Update any callers that pass these parameters: **N/A**
- [x] Verify: no behavioral change (parameters defaulted to None and were unused): **N/A**

**Notes:** Audit result: ALL parameters are actively used in production code:
- `stat_helpers` used in `_eval_damage_rule` and `_eval_pdc_arc_rule`
- `ship_capabilities_cache` used in `_eval_has_weapons_rule`
- `controller.py:213` passes both caches for performance optimization
The original finding was incorrect - no unused parameters exist.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/ -n 12` passes (8238 passed)
- [x] No `_logger` global in logger.py
- [x] No `_ProfilerProxy` class in profiling.py
- [x] No `PROFILER` global in profiling.py
- [x] No "backward compat" comments in modified files
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to audit
