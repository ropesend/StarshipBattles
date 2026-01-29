# Phase 4: Weak Assertion Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace 875 weak assertions with specific value checks.
**Issues Addressed:** TSR-004, TC-03

---

## Tasks

### Task 4.1: Fix Bare `assert success` Patterns [Medium]
**Tests:** `pytest tests/unit/strategy/ -v --tb=short`

#### Priority 1: test_save_game_service.py (25+ instances)
**File:** `tests/unit/strategy/test_save_game_service.py`

- [ ] Search for all `assert success` in file
- [ ] For each occurrence, replace with:
  ```python
  # Before
  success, message, save_path = SaveGameService.save_game(session, "TestGame")
  assert success

  # After
  success, message, save_path = SaveGameService.save_game(session, "TestGame")
  assert success, f"Save failed: {message}"
  ```
- [ ] Verify: `pytest tests/unit/strategy/test_save_game_service.py -v`

#### Priority 2: test_design_library.py (5 instances)
**File:** `tests/unit/strategy/test_design_library.py`

- [ ] Search for all `assert success` in file
- [ ] Replace with context messages
- [ ] Verify: `pytest tests/unit/strategy/test_design_library.py -v`

#### Priority 3: test_auto_save.py (4 instances)
**File:** `tests/unit/strategy/test_auto_save.py`

- [ ] Search for all `assert success` in file
- [ ] Replace with context messages
- [ ] Verify: `pytest tests/unit/strategy/test_auto_save.py -v`

#### Priority 4: test_save_selection.py (1 instance)
**File:** `tests/unit/ui/test_save_selection.py`

- [ ] Find and fix the `assert success`
- [ ] Verify: `pytest tests/unit/ui/test_save_selection.py -v`

**Notes:**

---

### Task 4.2: Fix Weak Length Assertions [Medium]
**Tests:** `pytest tests/ -v --tb=short`

#### test_workshop_viewmodel.py (5 instances)
**File:** `tests/unit/workshop/test_workshop_viewmodel.py`

- [ ] Search for `assert len(` patterns without messages
- [ ] Add context message to each:
  ```python
  # Before
  assert len(events) == 1

  # After
  assert len(events) == 1, "Should have exactly one event after selection"
  ```
- [ ] Verify: `pytest tests/unit/workshop/test_workshop_viewmodel.py -v`

#### test_collision_edge_cases.py (2 instances)
**File:** `tests/unit/engine/test_collision_edge_cases.py`

- [ ] Find weak length assertions at lines 468, 540
- [ ] Add context messages
- [ ] Verify: `pytest tests/unit/engine/test_collision_edge_cases.py -v`

#### test_extract_phase.py (6 instances)
**File:** `tests/projects/test_extract_phase.py`

- [ ] Search for weak length assertions
- [ ] Add context messages
- [ ] Verify: `pytest tests/projects/test_extract_phase.py -v`

**Notes:**

---

### Task 4.3: Fix Boolean Equality Assertions [Simple]
**Tests:** `pytest tests/unit/core/ tests/unit/ai/ -v --tb=short`

#### test_profiling.py (lines 318, 322)
**File:** `tests/unit/core/test_profiling.py`

- [ ] Find `assert result == False` and `assert result == True`
- [ ] Replace with:
  ```python
  # Before
  assert result == False

  # After
  assert result is False
  # Or simply: assert not result
  ```
- [ ] Verify: `pytest tests/unit/core/test_profiling.py -v`

#### test_target_evaluator.py (line 646)
**File:** `tests/unit/ai/test_target_evaluator.py`

- [ ] Find `assert result == False`
- [ ] Replace with `assert result is False` or `assert not result`
- [ ] Verify: `pytest tests/unit/ai/test_target_evaluator.py -v`

**Notes:**

---

### Task 4.4: Create Assertion Helper Functions [Simple]
**File:** `tests/conftest.py`
**Tests:** `pytest tests/ -v --tb=short`

- [ ] Add helper functions to `tests/conftest.py`:
  ```python
  def assert_success(success: bool, message: str = ""):
      """Assert that an operation succeeded with context message."""
      assert success, f"Operation failed: {message}"

  def assert_list_length(items, expected_length: int, description: str = ""):
      """Assert list length with context."""
      assert len(items) == expected_length, \
          f"{description}: Expected {expected_length} items, got {len(items)}"
  ```
- [ ] Document helpers in `tests/README.md`
- [ ] Verify: Helpers can be imported and used

**Notes:**

---

### Task 4.5: Scan for Remaining Weak Assertions [Simple]
**Tests:** N/A - verification only

- [ ] Run grep to find remaining weak assertions:
  ```bash
  grep -r "assert result$\|assert success$\|assert found$" tests/
  grep -r "assert len.*== [0-9]$" tests/
  grep -r "assert .* == True$\|assert .* == False$" tests/
  ```
- [ ] Fix any remaining issues found
- [ ] Document count of remaining issues (should be 0 or near 0)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No bare `assert success` patterns remain
- [ ] No `assert x == True/False` patterns remain
- [ ] Assertion helpers added to conftest.py
- [ ] Run `pytest tests/ -v --tb=short` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
