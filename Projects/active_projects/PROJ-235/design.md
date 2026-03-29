# PROJ-235: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**`_process_tick()` (lines 393-511, 119 lines)** contains 12 phases, each wrapped in identical timing boilerplate:
```python
t0 = time.perf_counter()
self.<engine>.<method>(args...)
self._phase_times['<key>'] += time.perf_counter() - t0
```

Three BUG-109 debug blocks (tick==1 only) are interspersed at lines 419-427, 436-444, and 468-476. Two more BUG-109 blocks exist in `process_turn()` at lines 323-333 and 341-351.

The tick loop uses `range(1, 101)` while `production_engine.py:30` defines `TICKS_PER_TURN = 100`.

## Swarm Findings Summary

### Architecture
- **TurnEngine is a pure orchestrator** — zero business logic, all work delegated to 11 sub-engines
- **Timing is diagnostic-only** — `_phase_times` dict is logged at WARNING level in `process_turn()`, not consumed by UI, save system, or tests
- **Implicit side-effect contract**: `process_turn()` returns None but populates `self.last_scuttle_events` (consumed by facade + UI) and `self.last_environmental_events` (consumed by tests only)

### Dependencies
- **Zero circular import risk**: `production_engine.py` does not import from `turn_engine.py` at module level; `turn_engine.py` only lazily imports `ProductionEngine` inside a property
- **TICKS_PER_TURN** is used in 3 locations within `production_engine.py` (lines 407, 418, 556)
- Other hardcoded `100.0` divisors exist in `resource_management_engine.py`, `resupply_engine.py`, `environmental_hazard_engine.py` (out of scope)

### Test Impact
- **CRITICAL test**: `test_tick_calls_phases_in_order` in `test_turn_processing.py` verifies the exact 12-phase execution order
- **Method signature**: `_process_tick(self, tick, empires, galaxy, save_path=None)` is patched by tests — must not change
- **100-tick assertion**: `test_process_turn_calls_subticks` asserts `mock_tick.call_count == 100`
- **Event accumulation**: `last_scuttle_events` and `last_environmental_events` verified by facade and integration tests

### Key Patterns to Reuse
- **Helper method extraction**: Engine files use private `_` prefixed methods for extracted logic (e.g., `FleetOrderProcessor._execute_fleet_merge()`, `ConflictResolutionEngine._log_combat_result()`)
- **Module-level constants**: `UPPER_SNAKE_CASE` with inline comments (see `production_engine.py:30-33`)

### Risks Identified
1. **Phase ordering** (MEDIUM) — Must use sequential calls, never dict iteration. Test `test_tick_calls_phases_in_order` catches reordering immediately.
2. **kwargs forwarding** (LOW) — Verified: `action_engine.process_action_ticks()` accepts `component_registry` and `all_empires` kwargs; `production_engine.process_construction_tick()` accepts `save_path` kwarg. Names match exactly.
3. **BUG-109 timing shift** (LOW) — Block before harvesting is currently INSIDE harvesting timing. After refactor, it will be OUTSIDE. Acceptable: makes timing consistent across all phases.
4. **Return value safety** (LOW) — Both `maintenance_engine.process_maintenance_tick()` and `environmental_engine.process_environmental_tick()` always return lists, never None.

### Opportunities Discovered
- `process_turn()` docstring doesn't document side effects (`last_scuttle_events`, `last_environmental_events`). Adding documentation is low-effort.
- The `environmental_events` list has no production UI consumer — only tests read it. Not in scope but worth noting.

## Design Decisions

### `_time_phase()` helper
```python
def _time_phase(self, key: str, fn, *args, **kwargs):
    """Execute a phase function and accumulate its duration to _phase_times."""
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    self._phase_times[key] += time.perf_counter() - t0
    return result
```

**Why this design:**
- Returns result so callers can use return values (maintenance events, environmental events, move_queue)
- Uses `*args, **kwargs` to handle the 2 phases that use keyword arguments (action_engine, production_engine)
- Exception propagation matches current behavior (timing not recorded if exception raises)
- No decorator/context manager — keeps the pattern as a simple private method

**Why not a decorator or context manager:**
- Pattern Scout found NO existing `*args/**kwargs` wrappers in engine files
- Helper method pattern matches codebase conventions (`ConflictResolutionEngine._log_combat_result()`, etc.)
- Context managers add complexity for no benefit in sequential code

### `_log_empire_state()` helper
```python
def _log_empire_state(self, empires, label: str) -> None:
    """Log empire resource state for debugging (BUG-109)."""
    for empire in empires:
        try:
            logger.debug(
                f"[BUG-109] {label}: empire {empire.id} "
                f"resource_pool={dict(empire.resource_pool)}"
            )
        except (AttributeError, TypeError):
            pass
```

**Why simplify the turn-level blocks:** The 2 blocks in `process_turn()` include extra fields (facilities count, ships count). The simplified form matches the 3 blocks in `_process_tick()` and is sufficient for debugging — the extra fields were only needed during initial BUG-109 triage.

### TICKS_PER_TURN placement
- Define in `turn_engine.py` (authoritative owner of the tick loop)
- `production_engine.py` imports it: `from game.strategy.engine.turn_engine import TICKS_PER_TURN`
- No circular import risk (verified by Dependency Mapper)

See [decisions.md](decisions.md) for the full log with rationale.
