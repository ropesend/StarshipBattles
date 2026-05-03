# Dead Code Hunter Report: UI Screens (`game/ui/screens/`)

### Summary
- Total dead code items found: 2
- Estimated removable lines: 37 (+ ~80 lines orphaned test code)
- Critical: 0, Major: 0, Minor: 2, Info: 0

### Findings

#### Minor: Unused `format_star_system_info()` function
**ID:** DC-SCR-01
**Location:** `game/ui/screens/strategy_detail_fmt.py:159-179`
**Issue:** Function defined but never called from any production code. Has test coverage but no production callers. Likely replaced during refactoring by logic in `strategy_detail_formatter.py`.
**Evidence:** Grep for `format_star_system_info` shows only definition and test file references. Note: `_format_star_info` in `galaxy_test/system_mode.py` is a different local method (with underscore prefix).
**Removable Lines:** 21
**Effort:** Simple

#### Minor: Unused `format_star_info()` function
**ID:** DC-SCR-02
**Location:** `game/ui/screens/strategy_detail_fmt.py:182-197`
**Issue:** Function defined but never called from any production code. Has test coverage but no production callers. Similar to DC-SCR-01, appears replaced during refactoring.
**Evidence:** Grep for `format_star_info` shows only definition and test file references.
**Removable Lines:** 16
**Effort:** Simple

### Top 5 Priority Items
1. DC-SCR-01 + DC-SCR-02: Remove both unused star formatting functions from `strategy_detail_fmt.py` (37 lines) and corresponding test classes (~80 lines)
