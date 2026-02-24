# Phase 4: Guardrails & Documentation

**Goal:** Prevent regression with documentation and verification. Ensure future developers follow the established patterns.

**Estimated effort:** 1-2 hours
**Risk:** LOW — documentation and verification only

## Pre-Phase
- [ ] Phases 1-3 must be complete
- [ ] Run full test suite, record baseline: `pytest tests/ -n 12`

## Task 1: Logging Level Guidelines (ERR-011)
- [ ] Read `docs/ERROR_HANDLING_GUIDELINES.md`
- [ ] Add "Logging Level Guidelines" section with:

| Level | When to Use | Examples |
|-------|-------------|---------|
| `logger.error()` | Unrecoverable failures, data corruption | Failed to save game, missing critical data file |
| `logger.warning()` | Recoverable issues, degraded behavior | Fallback to default config, deprecated API usage |
| `logger.info()` | Normal operations worth recording | Game started, battle ended, save completed |
| `logger.debug()` | Detailed diagnostic info | File loaded, cache hit/miss, calculation details |
| `log_event()` | Structured simulation events | Damage dealt, movement completed, turn started |

- [ ] Add "Standard Logging Pattern" example:
  ```python
  import logging
  logger = logging.getLogger(__name__)
  ```
- [ ] Add "Event Logging Pattern" example:
  ```python
  from game.core.event_logging import log_event
  log_event("damage", ship_id=42, amount=100)
  ```
- [ ] Add "Anti-patterns" section:
  - Do NOT create custom logger classes or singletons
  - Do NOT use `print()` for diagnostic output
  - Do NOT import `json` for file I/O (use `json_utils`)

## Task 2: Update event_logging.py Docstring
- [ ] Verify `game/core/event_logging.py` has clear module docstring explaining:
  - Purpose (structured event callbacks for simulation/tests)
  - Difference from standard logging (events are typed callbacks, not log messages)
  - Usage examples
  - Lifecycle (handler set by GameSession, cleared in test fixtures)

## Task 3: Update json_utils.py Documentation
- [ ] Verify `game/core/json_utils.py` docstring documents it as canonical JSON utility
- [ ] Verify examples show `load_json`, `save_json`, `load_json_required`
- [ ] Add note: "All file-based JSON operations in game/ should use these functions"

## Task 4: Final Comprehensive Verification
- [ ] Verify ONE logging pattern: `grep -rn "from game.core.logger" game/ --include="*.py"` returns NOTHING
- [ ] Verify logger.py deleted: file does not exist
- [ ] Verify standard logging in use: `grep -rn "logging.getLogger" game/ --include="*.py"` returns many results
- [ ] Verify ZERO direct JSON file I/O: `grep -rn "json\.load\b\|json\.dump\b" game/ --include="*.py" | grep -v json_utils` returns nothing (or only json_utils.py)
- [ ] Verify event_logging exists and is tested
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Run full test suite serial (check for test isolation): `pytest tests/ -n 1 -x --timeout=300`
- [ ] Confirm zero regressions

## Completion Checklist
- [ ] Logging level guidelines added to ERROR_HANDLING_GUIDELINES.md
- [ ] event_logging.py documented
- [ ] json_utils.py documented as canonical
- [ ] All verification checks pass
- [ ] All tests pass (both parallel and serial)
- [ ] Update plan.md Phase 4 status to "Complete"
- [ ] Update plan.md Current State to "Project Complete"
