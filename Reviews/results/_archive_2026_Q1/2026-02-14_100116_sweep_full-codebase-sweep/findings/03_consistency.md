# Consistency Violations Sweep: Antigravity

## Summary
- **Shard:** Antigravity (Full Sweep)
- **Files Scanned:** 370+
- **Total Issues Found:** 3
- **Critical:** 0 | **Major:** 2 | **Minor:** 1 | **Info:** 0

## Findings

#### MAJOR: Widespread Usage of `print()` Statements
**ID:** CON-AG-001
**Location:** 70+ files, primarily in `game/ui/`
**Issue:** Debug `print()` statements are left in the codebase instead of using `game.core.logger`.
**Impact:** Clutters console output, bypasses log levels/files, look unprofessional.
**Recommendation:** Mass replace `print()` with `log_info()` or `log_debug()`.
**Effort:** Medium (easy search/replace but many files)

#### MAJOR: Inconsistent Logging Pattern
**ID:** CON-AG-002
**Location:** `game/ai/` vs `game/core/`
**Issue:** `game/ai/` modules tend to use `logging.getLogger(__name__)` while other modules use `from game.core.logger import log_info`.
**Impact:** Inconsistent log formatting and control. The wrapper functions differ from standard python logging in how they handle context/formatting.
**Recommendation:** Standardize on `game.core.logger` wrappers for application code.
**Effort:** Low

#### MINOR: Missing Type Hints in UI Layer
**ID:** CON-AG-003
**Location:** `game/ui/screens/*.py`
**Issue:** Many UI methods lack return type hints (e.g., `def draw(self, surface):`).
**Impact:** Reduced static analysis coverage and IDE support.
**Recommendation:** Enforce type hints on all new code and backfill during refactors.
**Effort:** High (many files)

## Top Priority Issues
1. **Remove `print()` statements**: This is a quick win for code hygiene.
2. **Standardize Logging**: ensure all subsystems use the central logger.
