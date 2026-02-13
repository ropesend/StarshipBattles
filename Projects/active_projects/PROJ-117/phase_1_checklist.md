# Phase 1: Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-117 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Address findings in the Foundation module (14 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 1.1: LEG-FND-001 - Backward Compatibility Wrapper `load_res [Medium]
**File:** `game/core/resources.py:101-143`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.2: LEG-FND-002 - StrategyMetadataService Uses Hand-Rolled [Simple]
**File:** `game/core/strategy_metadata.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.3: LEG-FND-003 - Dead Instance Attributes `attack_state` [Simple]
**File:** `game/ai/controller.py:90-91`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.4: LEG-FND-004 - Duplicate Path Resolution Logic in resou [Simple]
**File:** `game/core/resources.py:31-52`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.5: LEG-FND-005 - Unused Protocol Classes and TypeGuard Fu [Simple]
**File:** `game/core/protocols.py:85-110,`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.6: LEG-FND-006 - `LayerType.from_string()` Static Method [Simple]
**File:** `game/core/constants.py:117-119`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.7: LEG-FND-007 - `ScreenshotManager.capture_step()` Never [Simple]
**File:** `game/core/screenshot_manager.p`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.8: LEG-FND-008 - Python 3.9 Compatibility Shim for TypeGu [Simple]
**File:** `game/core/protocols.py:32-36`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.9: LEG-FND-009 - Color Constants (WHITE, BLACK, BLUE, RED [Simple]
**File:** `game/core/constants.py:42-46`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.10: LEG-FND-010 - `json` Import in resources.py Only Neede [Simple]
**File:** `game/core/resources.py:13`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.11: LEG-FND-011 - `_get_hp_percent` and `_is_in_pdc_arc` W [Simple]
**File:** `game/ai/controller.py:269-273`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.12: LEG-FND-012 - `FONT_MAIN` Constant Defined but Unused [Simple]
**File:** `game/core/constants.py:49`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.13: LEG-FND-013 - `DEBUG_SCREENSHOTS = True` Always Enable [Simple]
**File:** `game/core/constants.py:53`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]

### Task 1.14: LEG-FND-014 - `profiling.py` Comment References "backw [Simple]
**File:** `game/core/profiling.py:104`
**Tests:** `pytest tests/` (add appropriate test path)

- [ ] Investigate the issue at the specified location
- [ ] Write test to verify the fix
- [ ] Implement the fix
- [ ] Verify: tests pass, no regressions

**Notes:** [Filled during implementation]


---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
