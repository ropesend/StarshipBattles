# Phase 7: Documentation Update

**Objective:** Update all relevant documentation to reflect the new error boundary architecture.

**Depends On:** All previous phases (Phases 1-6)

---

## Checklist

### docs/05_ERROR_HANDLING.md
- [ ] Add `StrategyException` and `EnginePhaseError` to the hierarchy diagram
- [ ] Add Turn Processing error codes (T001-T003) to the error codes table
- [ ] Add new section: "Turn Engine Error Boundary" explaining snapshot/rollback behavior
- [ ] Add new section: "Sub-Engine Validation" explaining _validate_tick_inputs() pattern
- [ ] Update "Intentional Broad Catch Convention" section:
  - Note that `_time_phase()` no longer uses broad catch (it wraps and re-raises)
  - Note that `_log_empire_state()` still has an acceptable broad catch for logging
  - Note that serialization chain no longer silently drops entries
- [ ] Add `DesignLoadResult` as an example of the "result object" pattern
- [ ] Update anti-patterns: add "catching Exception and returning None in data loading" as anti-pattern
- [ ] Update the exception handler template to show the wrap-and-re-raise pattern

### docs/01_ARCHITECTURE.md
- [ ] Add "Turn Engine Error Model" subsection to the Strategy Layer section
- [ ] Document the snapshot/rollback lifecycle: capture → process → rollback-on-failure
- [ ] Document how `EnginePhaseError` flows: sub-engine → `_time_phase()` → `process_turn()` → `GameSession` → UI
- [ ] Add `TurnStateSnapshot` to the key classes list

### docs/02_PATTERNS.md
- [ ] Add "Error Boundary Pattern" — snapshot, halt, rollback, re-raise
- [ ] Add "Precondition Validation" — `_validate_tick_inputs()` in sub-engines
- [ ] Add "Result Object Pattern" — `DesignLoadResult` as alternative to exceptions for non-critical operations
- [ ] Update pattern count in the header (was 14, now 17)

### docs/03_CONVENTIONS.md
- [ ] Add convention: "Sub-engines must validate preconditions before mutating state"
- [ ] Add convention: "Serialization `from_dict()` methods propagate errors, not swallow them"
- [ ] Add convention: "`except Exception` in strategy layer must wrap and re-raise, not return None"

### Code-Level Documentation
- [ ] Verify `TurnStateSnapshot` has complete docstring explaining capture/restore lifecycle
- [ ] Verify `EnginePhaseError` docstring explains when it's raised and what context it carries
- [ ] Verify `_time_phase()` docstring updated to reflect new behavior (halt, not continue)
- [ ] Verify `process_turn()` docstring explains snapshot/rollback behavior
- [ ] Verify `DesignLoadResult` has complete docstring with usage examples
- [ ] Verify each engine's `_validate_tick_inputs()` has docstring listing preconditions checked

### Verification
- [ ] Read through all updated docs for consistency
- [ ] Verify no stale references to the old "continue on failure" behavior
- [ ] Verify doc examples compile/run (code blocks are valid Python)
- [ ] Run full test suite one final time
