# Phase 5: Turn Engine Error Boundary

**Objective:** Replace the broad `except Exception` in `_time_phase()` with a halt-and-rollback mechanism. A failed phase stops the turn immediately and restores pre-turn state.

**Key Principle:** A partially-processed turn is worse than no turn. If any phase fails, halt immediately and roll back. The player is informed; the game state is clean.

**Depends On:** Phase 4 (snapshot/rollback mechanism exists)

---

## Problem Statement

`TurnEngine._time_phase()` (lines 239-247) catches `Exception`, logs it, returns `None`, and lets the turn continue. This means:
- Phase N+1 operates on state that Phase N failed to mutate
- If HarvestingEngine fails, ConsumableManagementEngine processes stale resource data
- If FleetMovementEngine fails, ConflictResolutionEngine checks combat at wrong locations
- The 12 existing error handling tests verify this "continue on failure" behavior — they must be rewritten

## Design

### New `_time_phase()` Behavior

```python
def _time_phase(self, key: str, fn, *args, **kwargs):
    """Execute a phase function and accumulate its duration.
    
    On failure: raises EnginePhaseError to halt the entire turn.
    The caller (process_turn) is responsible for rollback via snapshot.
    """
    t0 = time.perf_counter()
    try:
        result = fn(*args, **kwargs)
    except EnginePhaseError:
        # Already wrapped by a sub-engine — re-raise as-is
        self._phase_times[key] += time.perf_counter() - t0
        raise
    except Exception as e:
        self._phase_times[key] += time.perf_counter() - t0
        logger.error(
            "Sub-engine phase '%s' failed during tick processing",
            key, exc_info=True,
        )
        raise EnginePhaseError(
            f"Phase '{key}' failed: {e}",
            code=ErrorCode.PHASE_FAILED.value,
            context={
                "phase_name": key,
                "tick": self._current_tick,
                "original_error": str(e),
                "original_type": type(e).__name__,
            }
        ) from e
    self._phase_times[key] += time.perf_counter() - t0
    return result
```

Key changes:
- Still catches `Exception` but **re-raises as `EnginePhaseError`** instead of returning `None`
- Preserves the original exception chain (`from e`)
- Adds structured context (phase name, tick number, original error)
- Keeps the performance timing and logging
- If an `EnginePhaseError` comes in (from a sub-engine that raised it directly), re-raise as-is

### New `process_turn()` Behavior

```python
def process_turn(self, empires, galaxy, save_path=None, *, session=None):
    """Process a complete turn (100 ticks).
    
    Takes a pre-turn snapshot. If any phase fails, restores state
    from snapshot, dumps crash data for debugging, and raises
    EnginePhaseError to the caller.
    """
    # 1. Capture snapshot
    snapshot = TurnStateSnapshot.capture(self._turn_number, empires, galaxy)
    
    try:
        # 2. Process all ticks and post-tick phases (existing logic)
        self._reset_phase_times()
        for tick in range(1, 101):
            self._current_tick = tick
            self._process_tick(tick, empires, galaxy, save_path)
        
        # Post-tick phases (population, quality, atmosphere)
        self._time_phase("population", self.population_engine.process_population_growth, empires)
        self._time_phase("quality", QualityEngine(self._registries).process_quality_improvement, empires)
        self._time_phase("atmosphere", AtmosphereEngine(self._registries).process_atmosphere, empires)
        
    except EnginePhaseError as e:
        # 3. On failure: rollback + crash dump
        logger.error(f"Turn {self._turn_number} failed at tick {e.context.get('tick', '?')}, "
                     f"phase '{e.context.get('phase_name', '?')}'. Rolling back.")
        
        if save_path:
            self._dump_crash_snapshot(snapshot, e, save_path)
        
        if session is not None:
            snapshot.restore(session)
            logger.info(f"Turn {self._turn_number} state restored from snapshot.")
        
        raise  # Propagate to GameSession
```

### New `GameSession.process_turn()` Behavior

```python
def process_turn(self):
    """Process one turn. On failure, state is rolled back and error is raised."""
    logger.info(f"GameSession: Processing Turn {self.turn_number}...")
    try:
        self.turn_engine.process_turn(
            self.empires, self.galaxy, self.save_path,
            session=self  # Pass self so TurnEngine can rollback
        )
        self.turn_number += 1
    except EnginePhaseError as e:
        # State already rolled back by TurnEngine
        # Re-raise for UI layer to handle (show dialog, etc.)
        logger.error(f"Turn {self.turn_number} failed: {e}")
        raise
```

### Tracking `_current_tick`

Add `self._current_tick = 0` to `TurnEngine.__init__()`. Updated at the start of each tick in `_process_tick()`. Included in `EnginePhaseError` context for diagnostics.

### `_log_empire_state()` Cleanup

The `_log_empire_state()` method (lines 251-261) has a separate `except (AttributeError, TypeError): pass` block for debug logging. This is fine — logging should never crash the turn. Keep this block but add a comment explaining why it's acceptable.

---

## Checklist

### Tests First (TDD)

#### _time_phase() Raises Instead of Swallowing
- [ ] Write test: `_time_phase()` with a function that raises `ValueError` → raises `EnginePhaseError`
- [ ] Write test: `EnginePhaseError` context contains `phase_name`, `tick`, `original_error`
- [ ] Write test: `EnginePhaseError.__cause__` is the original `ValueError` (chain preserved)
- [ ] Write test: `_time_phase()` with a function that raises `EnginePhaseError` → re-raises same error (not double-wrapped)
- [ ] Write test: `_time_phase()` still accumulates timing on failure
- [ ] Write test: `_time_phase()` still works normally when function succeeds

#### process_turn() Snapshot and Rollback
- [ ] Write test: `process_turn()` calls `TurnStateSnapshot.capture()` before processing
- [ ] Write test: when a phase fails, `process_turn()` raises `EnginePhaseError`
- [ ] Write test: when a phase fails, state is restored to pre-turn values (verify empire resources, fleet locations)
- [ ] Write test: when a phase fails on tick 50, ticks 1-49 mutations are undone
- [ ] Write test: when no phase fails, turn completes normally and state is mutated
- [ ] Write test: `turn_number` is NOT incremented when turn fails
- [ ] Write test: `turn_number` IS incremented when turn succeeds

#### Crash Snapshot Dump
- [ ] Write test: on failure with `save_path`, crash snapshot JSON file is written
- [ ] Write test: on failure without `save_path`, no crash file attempted (no error)
- [ ] Write test: crash snapshot file contains phase_name, tick, error details, empire/galaxy data

#### GameSession.process_turn() Integration
- [ ] Write test: `GameSession.process_turn()` raises `EnginePhaseError` on turn failure
- [ ] Write test: `GameSession.turn_number` unchanged after failed turn
- [ ] Write test: `GameSession.turn_number` incremented after successful turn
- [ ] Write test: game state is consistent after failed turn (can process another turn successfully)

- [ ] Run tests — confirm they fail

### Rewrite Existing Error Handling Tests

The 12 tests in `test_turn_error_handling.py` verify the OLD behavior (continue-on-failure). They must be rewritten:

- [ ] `test_tick_continues_when_*_raises` → rewrite as `test_turn_halts_when_*_raises` 
- [ ] Each test should verify: `EnginePhaseError` raised, correct phase in context, state rolled back
- [ ] Remove tests that assert "later phases still called after failure" (that's the old behavior we're eliminating)
- [ ] Add tests that assert "later phases NOT called after failure"
- [ ] Keep tests that verify logging on failure (logging is still desired)

### Implementation

#### TurnEngine Changes
- [ ] Add `self._current_tick: int = 0` to `__init__()`
- [ ] Set `self._current_tick = tick` at start of `_process_tick()`
- [ ] Rewrite `_time_phase()` — catch Exception, wrap in EnginePhaseError, raise
- [ ] Add `EnginePhaseError` pass-through (don't double-wrap)
- [ ] Add `session` parameter to `process_turn()`
- [ ] Add snapshot capture at start of `process_turn()`
- [ ] Add try/except EnginePhaseError in `process_turn()` — rollback + crash dump + re-raise
- [ ] Add `_dump_crash_snapshot()` private method
- [ ] Update `_log_empire_state()` with comment explaining why its broad catch is acceptable

#### GameSession Changes
- [ ] Update `process_turn()` to pass `session=self` to turn engine
- [ ] Add try/except for `EnginePhaseError` — log and re-raise
- [ ] Only increment `turn_number` on success (move increment inside try, before except)

- [ ] Run tests — confirm they pass

### Verification
- [ ] Run full test suite — no regressions
- [ ] Verify the 12 rewritten error handling tests pass with new behavior
- [ ] Verify integration tests in `test_turn_execution.py` still pass
- [ ] Verify that a normal turn (no failures) has identical behavior to before
