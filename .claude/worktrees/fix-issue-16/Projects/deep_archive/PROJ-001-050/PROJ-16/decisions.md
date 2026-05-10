# PROJ-16: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-25 | Project initialized | Starting point for Consolidate Re-exports (Phase 3) |
| 2026-01-25 | Phase re-exports by risk (lowest first) | Order: PLANET_RESOURCES → Component constants → AI → Ship loader. Allows incremental verification and reduces blast radius of issues. |
| 2026-01-25 | Keep ModifierLogic in UI layer | `calculate_snap_value()` contains UI-specific snap-button logic. Moving to ModifierService would violate layer separation (simulation should not know about UI snap behavior). |
| 2026-01-25 | Keep _ProfilerProxy wrapper | Tests directly mutate `PROFILER.active` and `PROFILER.records`. Proxy enables lazy initialization and provides stable API. Removing gains nothing. |
| 2026-01-25 | **KEEP** ShipControllableAdapter backward compat | Production code (controller.py) extensively uses direct ship attribute access (self.ship.position, self.ship.turn_throttle, etc.). Removing delegation breaks 50+ tests. Refactoring controller.py is out of scope. |
| 2026-01-25 | No new `__init__.py` exports | Creating formal package exports (e.g., `game/simulation/__init__.py`) is out of scope for this project. Could be a future enhancement. |
| 2026-01-25 | Update mock patches if they break | Some tests patch re-export paths. These must be updated when re-exports are removed. |
| 2026-01-26 | **AUDIT CYCLE 1 FAILED** | Phase 3 never completed (all checkboxes unchecked, re-exports still exist). Phase 2 has 9 files still using old imports. Added Phase 6 for fixes. |

## Detailed Rationale

### Why Keep ModifierLogic?

The `calculate_snap_value()` method has UI-specific parameters like `smart_floor` that control Size Mount special behavior for snap buttons. This is presentation logic, not business logic:

```python
@staticmethod
def calculate_snap_value(current, step, direction, min_val, max_val, smart_floor=False):
    """Calculates value for snap buttons. UI-specific logic."""
    if smart_floor and direction < 0 and current <= step:
        return max(min_val, 1)  # Size Mount special case
```

Moving this to `ModifierService` would:
1. Pollute simulation layer with UI concerns
2. Make ModifierService depend on presentation logic
3. Violate separation of concerns

### Why Keep _ProfilerProxy?

The proxy pattern provides:
1. **Lazy initialization** - Profiler.instance() not called until first access
2. **Stable API** - Tests can do `PROFILER.active = False` without caring about singleton internals
3. **Backward compatibility** - Existing code works unchanged

Tests in `test_profiler_perf.py` directly mutate fields:
```python
PROFILER.active = False
PROFILER.records = []
```

Removing the proxy would require all these to change to `Profiler.instance().active = False`, which is more verbose and gains nothing.

### Why Phase by Risk?

1. **PLANET_RESOURCES (8 files)** - Trivial, explicitly marked as PROJ-11 backward compat bridge
2. **Component constants (65 files)** - Isolated to simulation/test layers, no circular import risk
3. **AI re-exports (40 files)** - Requires test infrastructure updates (conftest.py, fixtures)
4. **Ship loader (67 files)** - Critical initialization path (app.py, session fixtures)

This order allows us to build confidence before tackling riskier changes.

### Why Keep ShipControllableAdapter Backward Compat?

**Attempted:** Staged removal of `.ship` property, `__getattr__`, and `__setattr__`.

**Discovery:** The production `AIController` in `game/ai/controller.py` extensively uses direct ship attribute access through the adapter:

```python
# Examples from controller.py - MANY occurrences like:
self.ship.position          # needs __getattr__
self.ship.turn_throttle     # needs __getattr__
self.ship.engine_throttle   # needs __setattr__
self.ship.current_target    # needs both
self.ship.formation_members # needs __getattr__
```

**Impact of removal:** 50+ test failures when `__getattr__`/`__setattr__` were removed.

**Decision:** KEEP all delegation features. Refactoring `controller.py` to use interface methods exclusively (e.g., `self.ship.get_position()` instead of `self.ship.position`) is a significant undertaking out of scope for PROJ-16.

**Future work:** If we want to remove these delegation features, we need to:
1. Refactor `AIController` to use only `IControllable` interface methods
2. Update any other production code that accesses ship attributes through the adapter
3. Then remove the delegation methods
