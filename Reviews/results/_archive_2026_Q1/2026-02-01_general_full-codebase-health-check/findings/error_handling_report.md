### Summary
- Total issues found: 3
- Critical: 0, Major: 1, Minor: 2, Info: 0

### Findings

#### MAJOR: Swallowed Exceptions
**ID:** ERR-01
**Location:** `scripts/apply_resource_costs.py`
**Issue:** `except: pass` usage.
**Impact:** Hides failures.
**Recommendation:** Log errors.
**Effort:** Simple

#### MINOR: Console Printing
**ID:** ERR-02
**Location:** General
**Issue:** Widespread use of `print()` instead of `logging`.
**Impact:** Hard to control verbosity or capture logs in production.
**Recommendation:** Switch to `logging` module.
**Effort:** Medium

### Top 5 Priority Issues
1. Fix swallowed exceptions (ERR-01)
