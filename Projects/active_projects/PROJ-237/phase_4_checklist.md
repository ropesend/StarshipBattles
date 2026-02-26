# Phase 4: Verification

**Goal:** Verify complexity reduction and final cleanup.

---

## Checklist

### 4.1 Measure complexity

- [ ] **4.1.1 Run radon on target file**
  ```bash
  radon cc game/ui/screens/fleet_report_filters.py -s -a
  ```
  - Expected: `filter_ships` CC should be < 20 (goal was to reduce from 36)
  - Expected: Each helper function CC should be < 10

- [ ] **4.1.2 Record results**
  - Before: CC 36
  - After: CC ___ (fill in)
  - Helpers: ___ (list CC for each)

### 4.2 Run full test suite

- [ ] **4.2.1 Run all tests**
  ```bash
  pytest tests/ -n 12
  ```
  - Expected: All 6246+ tests pass
  - No regressions

- [ ] **4.2.2 Run with coverage**
  ```bash
  pytest tests/unit/ui/screens/test_fleet_report_filters.py --cov=game.ui.screens.fleet_report_filters --cov-report=term-missing
  ```
  - Verify all new helper functions are covered

### 4.3 Code review

- [ ] **4.3.1 Check docstrings**
  - All helper functions have docstrings
  - Docstrings explain purpose and invariants

- [ ] **4.3.2 Check type hints**
  - All function signatures have type hints
  - Import `Callable` if used

- [ ] **4.3.3 Check late imports**
  - `FleetCapabilityCalculator` imported once at top of `filter_ships`
  - No imports inside loops

- [ ] **4.3.4 Check naming**
  - Helper functions use `_` prefix (private)
  - Names describe what the function does

### 4.4 Final cleanup

- [ ] **4.4.1 Remove any commented-out code**

- [ ] **4.4.2 Verify no TODO comments left behind**

- [ ] **4.4.3 Run linter**
  ```bash
  ruff check game/ui/screens/fleet_report_filters.py
  ```

### 4.5 Update documentation

- [ ] **4.5.1 Update decisions.md**
  - Add final CC measurement
  - Note any deviations from plan

- [ ] **4.5.2 Update plan.md**
  - Mark all phases complete
  - Update Current State

---

## Verification Commands

```bash
# Complexity check
radon cc game/ui/screens/fleet_report_filters.py -s -a

# Full test suite
pytest tests/ -n 12

# Coverage for filter module
pytest tests/unit/ui/screens/test_fleet_report_filters.py --cov=game.ui.screens.fleet_report_filters --cov-report=term-missing

# Linting
ruff check game/ui/screens/fleet_report_filters.py
```

---

## Completion Criteria
- [ ] CC of `filter_ships` is below 20
- [ ] All tests pass
- [ ] Code review items addressed
- [ ] Documentation updated
- [ ] Project ready for user verification
