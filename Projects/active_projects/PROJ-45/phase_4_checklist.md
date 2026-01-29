# Phase 4: AI System - Target Evaluator & Controller

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-45 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace silent failures with proper exception handling for debuggability.

---

## Tasks

### Task 4.1: Update target_evaluator.py - Remove Silent Failures [Complex]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/test_target_evaluator.py`

- [ ] Fix ERR-002/ERR-02: lines 34-35 - Replace `except Exception: pass` with specific catch + logging
- [ ] Fix ERR-002/ERR-02: lines 49-50 - Replace `except Exception: pass` with specific catch + logging
- [ ] Fix ERR-014: lines 98-252 - Add None checks after `get_position()` calls
- [ ] Fix ERR-03: line 224 - Add division by zero protection
- [ ] Create `TargetingException` for targeting failures
- [ ] Add logging for all error paths with target ID context
- [ ] Update `_get_position()` to log failures before fallback
- [ ] Update `_get_rotation()` to log failures before fallback
- [ ] Verify: Tests pass

**Notes:** Keep fallback behavior but add comprehensive logging for debugging

---

### Task 4.2: Update controller.py Error Handling [Medium]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/test_controller.py`

- [ ] Fix ERR-09: line 334 - Add logging and safe default for targeting failures
- [ ] Add try/catch around `TargetEvaluator.evaluate()` calls
- [ ] Log when targets are rejected with reason
- [ ] Add context (ship ID, target ID, rule name) to all errors
- [ ] Verify: Tests pass

**Notes:**

---

### Task 4.3: Update strategy_manager.py Error Handling [Simple]
**File:** `game/ai/strategy_manager.py`
**Tests:** `pytest tests/unit/ai/test_strategy_manager.py`

- [ ] Fix ERR-003: line 40 - Replace `raise Exception()` with specific type
- [ ] Use `ValidationException` for invalid strategy configurations
- [ ] Verify: Tests pass

**Notes:**

---

### Task 4.4: Create AI Exception Tests [Simple]
**File:** `tests/unit/ai/test_ai_exceptions.py` (NEW)
**Tests:** Self-testing

- [ ] Test targeting failure logging
- [ ] Test fallback behavior when exceptions occur
- [ ] Test error context preservation
- [ ] Verify: `pytest tests/unit/ai/test_ai_exceptions.py` passes

**Notes:**

---

### Task 4.5: Update AI Module Documentation [Simple]
**File:** `game/ai/__init__.py` or inline docstrings
**Tests:** N/A (documentation)

- [ ] Document exception handling patterns for AI modules
- [ ] Document logging expectations for debugging
- [ ] Verify: Documentation is clear and complete

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/ai/`
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Run battle with AI ships - no crashes
- [ ] Check logs for targeting errors - should see context now
- [ ] Verify AI behavior unchanged - fallbacks still work
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
