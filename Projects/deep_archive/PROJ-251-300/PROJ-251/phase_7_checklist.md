# Phase 7: Documentation Update

**Objective:** Update all relevant documentation to reflect the new error boundary architecture.

**Status:** Complete

---

## Checklist

### docs/05_ERROR_HANDLING.md
- [x] Added `StrategyException` and `EnginePhaseError` to hierarchy diagram
- [x] Added Turn Processing error codes (T001-T003) to error codes table
- [x] Added "Turn Engine Error Boundary (PROJ-251)" section with snapshot/rollback pattern
- [x] Updated "Intentional Broad Catch Convention" with PROJ-251 changes note
- [x] Added sub-engine `_validate_tick_inputs()` guidance

### docs/01_ARCHITECTURE.md
- [x] Updated `engine/` description with TurnStateSnapshot and error model note

### docs/02_PATTERNS.md
- [x] Added Pattern 19: Error Boundary (Turn Engine)
- [x] Added Pattern 20: Precondition Validation (Sub-Engines)
- [x] Updated Quick Reference table with new patterns
- [x] Updated header to "20 patterns"

### docs/03_CONVENTIONS.md
- [x] Added Section 6.4: Error Handling Conventions (PROJ-251) with 4 rules:
  - Sub-engines validate preconditions via `_validate_tick_inputs()`
  - `from_dict()` propagates errors
  - `except Exception` must wrap and re-raise
  - DesignLibrary uses result objects
