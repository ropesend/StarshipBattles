# Unit Test Audit Protocol

## Context
We are cleaning up a 12,000+ unit test suite. All tests pass, but many may be testing dead, deprecated, or replaced code.
You are an "Audit Agent" assigned to review a specific batch of tests.

## Inputs
1.  **Test File**: The specific Python file you are reviewing.
2.  **Dead Files List**: A list of source files (`dead_code_candidates.txt`) that are NOT reachable from the production application entry point.

## Procedure

### Step 1: Identify System Under Test (SUT)
Read the test file and determine which source modules it imports and tests.
*   Look for `from game.x.y import Z`.
*   Look for `class TestZ:`.
*   **Result**: A list of source file paths (e.g., `game/x/y.py`) that this test exercises.

### Step 2: Liveness Check
Check if the SUT is in the **Dead Files List**.
*   **If SUT is Dead**: The test is testing dead code.
    *   **Verdict**: `DELETE`
    *   **Reason**: "Tests dead code: [Path to SUT]"
*   **If SUT is Live**: Proceed to Step 3.

### Step 3: Semantic Analysis
Read the test code itself.
1.  **Legacy Markers**: Does the test name or SUT name contain "Legacy", "Old", "Deprecated", "V1", "Tmp"?
    *   **Verdict**: `REVIEW` (or `DELETE` if obviously obsolete)
2.  **Mocking Madness**: Does the test mock *everything* and verify nothing but the mocks? (e.g. testing `A`, but mocking `A.method`?).
    *   **Verdict**: `REVIEW` (Low value test)
3.  **Refactoring Leftovers**: Is the test in `tests/unit/refactor`? These were likely temporary tests during a refactor.
    *   **Verdict**: `REVIEW` (Check if superseded by main tests)

### Step 4: Output Format
Append your findings to `audit_results.csv` in the format:
`TestFilePath,Verdict,Reason,SUT_Path`

**Verdict Options:**
*   `KEEP`: Active, useful test.
*   `DELETE`: Tests dead code or is explicitly deprecated.
*   `REVIEW`: Needs human eyes (ambiguous, legacy but active, or low quality).

## Example Output
```csv
tests/unit/core/test_config.py,KEEP,Tests active configuration logic,game/core/config.py
tests/unit/refactor/test_old_movement.py,DELETE,Tests dead code,game/simulation/old_movement.py
tests/unit/ui/test_legacy_dialog.py,REVIEW,Uses 'Legacy' in name but code is active,game/ui/legacy_dialog.py
```
