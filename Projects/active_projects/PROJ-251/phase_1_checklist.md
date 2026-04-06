# Phase 1: Exception Hierarchy & Error Codes

**Objective:** Extend the existing exception hierarchy with strategy-layer error types and error codes needed by later phases.

**Key Principle:** Build on the existing hierarchy in `game/core/exceptions.py`. Do not create a parallel system.

---

## New Exception Types

Add to `game/core/exceptions.py`:

```
GameException (existing)
    +-- StrategyException (NEW) — base for strategy-layer errors
            +-- EnginePhaseError (NEW) — a sub-engine phase failed during turn processing
```

### StrategyException
- **Purpose:** Base class for all strategy-layer errors (turn processing, fleet management, empire operations)
- **Why a new base:** The existing hierarchy has `SimulationException` for combat. Strategy-layer errors (turn processing, empire management) are a different domain. Having a separate base allows catching "all strategy errors" without catching combat errors.
- **Inherits from:** `GameException`

### EnginePhaseError
- **Purpose:** Raised when a sub-engine phase fails during turn tick processing
- **Inherits from:** `StrategyException`
- **Required context fields:**
  - `phase_name` (str): Which phase failed (e.g., "harvesting", "production", "combat")
  - `tick` (int): Which tick (1-100) the failure occurred on
  - `turn` (int): Which turn number
- **Usage:** Raised by `TurnEngine._time_phase()` when a phase throws. Caught by `GameSession.process_turn()` to trigger rollback and user notification.

## New Error Codes

Add to `game/core/error_codes.py`:

| Code | Name | Description |
|------|------|-------------|
| T001 | `PHASE_FAILED` | Sub-engine phase failed during turn processing |
| T002 | `TURN_ROLLBACK` | Turn was rolled back due to phase failure |
| T003 | `SNAPSHOT_FAILED` | Failed to create pre-turn state snapshot |

### Category: Turn Processing (T001-T099)
This is a new category. Update the module docstring and any category documentation.

---

## Checklist

### Tests First (TDD)
- [ ] Write tests for `StrategyException` construction (message, code, context)
- [ ] Write tests for `EnginePhaseError` construction with phase_name, tick, turn in context
- [ ] Write tests for `EnginePhaseError` inherits from both `StrategyException` and `GameException`
- [ ] Write tests for new error codes exist and have correct string values
- [ ] Write test that `EnginePhaseError` can be caught as `StrategyException`
- [ ] Write test that `EnginePhaseError` can be caught as `GameException`
- [ ] Write test that `EnginePhaseError` is NOT caught by `except SimulationException`
- [ ] Run tests — confirm they all fail

### Implementation
- [ ] Add `StrategyException` to `game/core/exceptions.py`
- [ ] Add `EnginePhaseError` to `game/core/exceptions.py`
- [ ] Add both to `__all__` exports
- [ ] Add `PHASE_FAILED`, `TURN_ROLLBACK`, `SNAPSHOT_FAILED` to `game/core/error_codes.py`
- [ ] Run tests — confirm they all pass

### Verification
- [ ] Run full test suite — no regressions
- [ ] Verify no circular imports introduced
