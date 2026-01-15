# Combat Lab Test Utilities

## Test Log Analyzer

Utility for comparing UI and headless test executions to ensure consistency.

### Usage

#### Generate Full Comparison Report

```bash
python simulation_tests/utils/test_log_analyzer.py
```

Shows comparison of all tests that have been run in both UI and headless modes.

**Example Output:**
```
======================================================================
Combat Lab Test Log Comparison Report
Generated: 2026-01-14 19:44:01
======================================================================

Total Tests: 38
Total Log Entries: 42

✓ BEAM360-001: Results match
✗ PROJ360-002: MISMATCH DETECTED
    - Damage mismatch: UI=250, Headless=248
? SEEK360-001: Missing runs (UI: 0, Headless: 1)

======================================================================
Summary:
  Matching: 36
  Mismatches: 1
  Incomplete: 1
======================================================================
```

**Status Codes:**
- ✓ = Results match (UI and headless produce identical results within tolerance)
- ✗ = Mismatch detected (UI and headless produce different results)
- ? = Incomplete (test only run in one mode)

#### View Test Execution History

```bash
python simulation_tests/utils/test_log_analyzer.py <TEST_ID>
```

Shows chronological execution history for a specific test.

**Example:**
```bash
python simulation_tests/utils/test_log_analyzer.py BEAM360-001
```

**Output:**
```
======================================================================
Test Execution History: BEAM360-001
======================================================================

1. 2026-01-14 19:40:27 | HEADLESS | PASS |  500 ticks |  262.0 dmg
2. 2026-01-14 19:45:12 | UI       | PASS |  500 ticks |  262.0 dmg
3. 2026-01-14 19:50:33 | HEADLESS | PASS |  500 ticks |  265.0 dmg

======================================================================
```

### Comparison Tolerances

The analyzer uses these tolerances when comparing UI vs headless:

- **Pass/Fail:** Must match exactly (no tolerance)
- **Damage Dealt:** ±1.0 tolerance
- **Tick Count:** ±1 tick tolerance

These tolerances account for minor floating-point differences and timing variations.

### Log File Format

Test executions are logged to `combat_lab_test_log.jsonl` in the project root.

**Format:** JSON Lines (one JSON object per line)

**Entry Structure:**
```json
{
  "timestamp": "2026-01-14T19:40:27.423029",
  "test_id": "BEAM360-001",
  "test_name": "Low Accuracy Beam - Point Blank (50px)",
  "mode": "headless",
  "passed": true,
  "ticks_run": 500,
  "damage_dealt": 262.0,
  "duration_real": 0.037,
  "results": { ... }
}
```

### When to Use

**During Development:**
- Run tests in both UI and headless modes
- Use analyzer to verify consistency
- Investigate any mismatches

**Before Releases:**
- Run full test suite in both modes
- Generate comparison report
- Confirm all tests match

**When Debugging:**
- View test history to check for regressions
- Compare results across multiple runs
- Identify timing or determinism issues

### Troubleshooting

**"No log entries found"**
- Run some tests first to generate log data
- Log file is created automatically when tests run

**"Missing runs (UI: 0, Headless: N)"**
- Test has only been run in one mode
- Run the test in the other mode to enable comparison

**"MISMATCH DETECTED"**
- UI and headless are producing different results
- This indicates a potential bug or timing issue
- Review the specific discrepancies listed
- Check if test is non-deterministic
