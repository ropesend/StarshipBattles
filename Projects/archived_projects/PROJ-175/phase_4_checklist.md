# Phase 4: Guardrails & Documentation

**Goal:** Prevent regression with documentation and verification. Ensure future developers follow the established patterns.

**Estimated effort:** 1-2 hours
**Risk:** LOW — documentation and verification only

## Pre-Phase
- [x] Phases 1-3 must be complete
- [x] Run full test suite, record baseline: `pytest tests/ -n 12` — 11968 passed, 1 skipped

## Task 1: Logging Level Guidelines (ERR-011)
- [x] Read `docs/architecture/ERROR_HANDLING_GUIDELINES.md`
- [x] Updated logging levels section to use standard `logger.info()` pattern (not `log_info()`)
- [x] Added `log_event()` section for structured simulation events
- [x] Updated all code examples to use `logger.method()` pattern
- [x] Added Anti-patterns section:
  - Anti-Pattern 6: Custom Logger Classes or Singletons
  - Anti-Pattern 7: Using print() for Diagnostics
  - Anti-Pattern 8: Direct JSON File I/O

## Task 2: Update event_logging.py Docstring
- [x] Verified `game/core/event_logging.py` has clear module docstring explaining:
  - Purpose (structured event callbacks for simulation/tests)
  - Difference from standard logging (events are typed callbacks, not log messages)
  - Usage examples
  - Lifecycle (handler set by GameSession, cleared in test fixtures)

## Task 3: Update json_utils.py Documentation
- [x] Verified `game/core/json_utils.py` docstring documents it as canonical JSON utility
- [x] Verified examples show `load_json`, `save_json`, `load_json_required`
- [x] Added note: "All file-based JSON operations in game/ should use these functions"

## Task 4: Final Comprehensive Verification
- [x] Verify ONE logging pattern: `grep -rn "from game.core.logger" game/` returns NOTHING ✓
- [x] Verify logger.py deleted: file does not exist ✓
- [x] Verify standard logging in use: 123 files use `logging.getLogger` ✓
- [x] Verify ZERO direct JSON file I/O: no json.load/dump outside json_utils ✓
- [x] Verify event_logging exists and is tested ✓
- [x] Run full test suite: 11968 passed, 1 skipped ✓
- [x] Confirm zero regressions ✓

## Completion Checklist
- [x] Logging level guidelines updated in ERROR_HANDLING_GUIDELINES.md
- [x] event_logging.py documented
- [x] json_utils.py documented as canonical
- [x] All verification checks pass
- [x] All tests pass (parallel)
- [x] Update plan.md Phase 4 status to "Complete"
- [x] Update plan.md Current State to "Project Complete"
