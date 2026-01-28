# Phase 5: Test Integration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-26 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update test path utilities to delegate to game.core.paths

---

## Tasks

### Task 5.1: Update tests/fixtures/paths.py [Medium]
**File:** `tests/fixtures/paths.py`
**Tests:** `pytest tests/ -v` (full suite)

- [ ] Review current implementation in `tests/fixtures/paths.py`
- [ ] Add import: `from game.core.paths import Paths`
- [ ] Update `get_project_root()` to return `Paths.get_root()`
- [ ] Update `get_data_dir()` to return `Paths.get_data_dir()`
- [ ] Update `get_assets_dir()` to return `Paths.get_assets_dir()`
- [ ] Keep test-specific paths (test_data_dir, unit_test_data_dir, etc.) as they don't belong in game code
- [ ] Verify all test fixtures still work
- [ ] Run full test suite to confirm no regressions

**Before:**
```python
def _find_project_root() -> Path:
    """Find project root by looking for game/ and data/ directories."""
    # ... local implementation
```

**After:**
```python
from game.core.paths import Paths

def get_project_root() -> Path:
    """Get the project root directory."""
    return Paths.get_root()

def get_data_dir() -> Path:
    """Get the data directory."""
    return Paths.get_data_dir()

# Keep test-specific paths with local implementation
def get_test_data_dir() -> Path:
    """Get the test data directory (tests/data)."""
    return get_project_root() / "tests" / "data"
```

**Notes:**

---

## Final Verification

### Comprehensive Testing
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Run simulation tests: `pytest simulation_tests/ -v`
- [ ] Launch game and verify all data loads
- [ ] Test save/load functionality
- [ ] Test ship designer

### Code Quality Checks
- [ ] No `os.getcwd()` patterns remain:
  ```bash
  grep -r "os.getcwd()" game/ --include="*.py"
  ```
- [ ] No multi-level dirname chains remain:
  ```bash
  grep -r "dirname.*dirname.*dirname" game/ --include="*.py"
  ```
- [ ] No hardcoded relative paths remain in key files:
  ```bash
  grep -r '"data/' game/ --include="*.py"
  grep -r '"assets/' game/ --include="*.py"
  ```

### Documentation
- [ ] Update any relevant documentation about path configuration
- [ ] Consider adding docstring to paths.py explaining usage

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes
- [ ] Game runs correctly end-to-end
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
- [ ] Move project to `Projects/completed_projects/PROJ-26/`
