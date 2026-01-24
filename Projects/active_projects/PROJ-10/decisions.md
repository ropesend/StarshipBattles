# PROJ-10: Decisions Log

## Decision 001: Project Created from Review Findings
**Date:** 2026-01-24
**Status:** Approved
**Context:** Code review identified 47 error handling issues. These are isolated, low-risk fixes that significantly improve debuggability.
**Decision:** Create dedicated project for error handling remediation as "quick wins" that can be completed independently of architectural changes.
**Rationale:**
- Fixes are localized and low-risk
- Immediate improvement to production debugging
- No dependencies on other projects
- Can be completed in parallel with larger refactoring efforts

## Decision 002: Logging Strategy
**Date:** 2026-01-24
**Status:** Approved
**Context:** Need consistent approach to adding logging.
**Decision:** Use existing `game.core.logger` module functions: `log_error()`, `log_warning()`, `log_debug()`
**Rationale:**
- Consistent with existing codebase patterns
- Already configured for file output
- No new dependencies required

## Decision 003: Exception Specificity
**Date:** 2026-01-24
**Status:** Approved
**Context:** Should we catch specific exceptions or use `Exception`?
**Decision:** Prefer specific exceptions where the failure mode is known. Use `Exception` only when multiple unknown errors are possible, always with logging.
**Rationale:**
- Specific exceptions make intent clear
- Prevents catching KeyboardInterrupt/SystemExit
- Logging ensures visibility even with broad catches
