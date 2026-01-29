# Phase 8: Test Quality Improvements

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Clean up remaining minor issues.
**Issues Addressed:** TSR-002, TSR-009, TSR-010, TSR-011, TSR-012, TSR-013, TSR-014, TSR-015

---

## Tasks

### Task 8.1: Remove Print Statements from Tests [Simple]
**Tests:** `pytest tests/ -v --tb=short`

- [ ] Find all print statements in test files:
  ```bash
  grep -rn "print(" tests/ --include="test_*.py" | head -50
  ```
- [ ] For each print statement, either:
  - **Debug output**: Remove entirely
  - **Test feedback**: Replace with assertion or `caplog` fixture
  - **Benchmark output**: Keep if in benchmark file, add comment

**Example replacement:**
```python
# Before
print(f"Result: {result}")
assert result is not None

# After
assert result is not None, f"Expected result but got None"
# Or with caplog:
assert "expected_log_message" in caplog.text
```

- [ ] Verify: `pytest tests/ -v --tb=short` - no print output during tests

**Notes:**

---

### Task 8.2: Complete Stub Test Classes [Medium]
**Tests:** `pytest tests/unit/builder/ -v --tb=short`

- [ ] Search for `pass` statements in test files:
  ```bash
  grep -rn "^\s*pass$" tests/ --include="test_*.py" | head -20
  ```
- [ ] For `tests/unit/builder/test_builder_validation.py:233`:
  - Read context around line 233
  - Either complete the test with assertions, OR
  - Delete the stub class with comment explaining why
- [ ] For other stub tests found:
  - Complete or delete with documentation
- [ ] Verify: No test methods contain only `pass`

**Notes:**

---

### Task 8.3: Add Missing Test Docstrings [Simple]
**Tests:** N/A - documentation only

- [ ] Find test classes without docstrings:
  ```bash
  # Use grep to find class definitions followed by def (no docstring)
  grep -A1 "^class Test" tests/ -r --include="test_*.py" | grep -B1 "def test_"
  ```
- [ ] For high-priority test files (monoliths split in Phase 3):
  - Add class docstring explaining what's being tested
  - Example: `"""Tests for ShipStatsService damage calculations."""`
- [ ] Document guideline in `tests/README.md`:
  ```markdown
  ## Docstrings
  - All test classes should have a docstring
  - Test methods only need docstrings for complex scenarios
  - Pattern: "Tests for <feature/class>."
  ```

**Notes:**

---

### Task 8.4: Review Skipped Tests [Medium]
**Tests:** `pytest tests/ -v --tb=short`

- [ ] Find all pytest.skip usages:
  ```bash
  grep -rn "pytest.skip" tests/ --include="test_*.py" | head -30
  ```
- [ ] Categorize skips:
  - **Snapshot creation**: Normal behavior, keep
  - **Missing data**: Document what data is needed
  - **Platform/environment**: Convert to `@pytest.mark.skipif`
  - **Conditional state**: Review if still needed

- [ ] For conditional skips based on file presence:
  ```python
  # Before
  if not os.path.exists(data_file):
      pytest.skip("Data file not found")

  # After
  @pytest.mark.skipif(
      not os.path.exists(DATA_FILE),
      reason="Data file required for this test"
  )
  ```

- [ ] Document intentionally skipped tests in `tests/README.md`

**Notes:**

---

### Task 8.5: Review Duplicate Test Setup [Simple]
**Tests:** `pytest tests/ -v --tb=short`

- [ ] Identify duplicate ship setup patterns:
  ```bash
  grep -rn "Ship(" tests/unit/entities/ tests/unit/combat/ | head -20
  ```
- [ ] If similar setup appears in 3+ files:
  - Create shared fixture in appropriate conftest.py
  - Document fixture purpose
- [ ] For hardcoded test data:
  - Move to `tests/fixtures/` if used by multiple tests
  - Keep inline if test-specific

**Notes:**

---

### Task 8.6: Final Cleanup and Verification [Simple]
**Tests:** Full test suite

- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Verify same test count as baseline (5244)
- [ ] Verify no new failures introduced
- [ ] Run with random order: `pytest tests/ --random-order -x`
- [ ] Run with parallel execution: `pytest tests/ -n 4`
- [ ] Document any remaining known issues

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No unnecessary print statements in tests
- [ ] No stub test classes with only `pass`
- [ ] Test docstrings added where missing
- [ ] Skipped tests reviewed and documented
- [ ] Duplicate setup consolidated where possible
- [ ] Full test suite passes (5244+ tests)
- [ ] Random order execution passes
- [ ] Parallel execution passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"

---

## PROJECT COMPLETION

When Phase 8 is complete:
1. Run final verification: `pytest tests/ -v`
2. Update `Projects/projects_index.md` with completion status
3. Archive project or mark as complete
4. Summarize achievements:
   - Issues resolved: 36
   - Files split: 50
   - Assertions improved: 875
   - Documentation added: README.md, fixture docs
