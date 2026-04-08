---
### 📝 User Update 2026-01-03 15:30
BUG-03

Stats Panel: I think that the stats panel recommendations for Fuel, Energy, or Ammo is satisfied by adding any one of them, it is probably simply accepting any resource as being necessary rather than a specific resource

## Work Log
*   **[2026-01-03 15:45] Reproduction Attempt:** Created `tests/repro_issues/test_bug_03_validation.py`.
    *   Test checks if adding Energy Storage clears "Needs Fuel Storage" warning.
    *   **Result:** Test Passed (Warning persisted). Unable to reproduce the "accepts any resource" behavior with synthetic test.
    *   **Plan:** Refactoring `ResourceDependencyRule` in `ship_validator.py` to use a robust Set-based approach instead of hardcoded if/else chains. This will eliminate any potential subtle logic errors and support dynamic resources.
*   **[2026-01-03 15:55] Fix Implemented:** Refactored `ResourceDependencyRule` to use `needed_resources` and `stored_resources` sets.
    *   Logic: `missing = needed - stored`.
    *   This guarantees that adding 'Energy' (stored) cannot remove 'Fuel' (needed).
    *   **Verification:** Ran `tests/repro_issues/test_bug_03_validation.py` (Passed) and `tests/unit/test_warnings.py` (Passed).
    *   **Status:** Fix applied and verified. Ready for confirmation.
---
