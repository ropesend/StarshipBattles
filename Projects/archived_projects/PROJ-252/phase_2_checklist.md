# Phase 2: Session-Scoped Event Bus

**Objective:** Replace the module-level `_event_handler` global in `event_logging.py` with a session-scoped `EventBus` class that is injected into simulation services.

**Key Principle:** No module-level mutable state for event routing. Each GameSession owns its own EventBus instance.

---

## Background

`event_logging.py` defines `_event_handler: Optional[Callable] = None` at module level. `GameSession.__init__` calls `set_event_handler()` which overwrites this global. This means:
- Multiple GameSessions cannot coexist (last one wins)
- Tests that create GameSessions leak event handler state
- Background simulations (AI planning) would route events to the wrong session

## Design

1. Create `EventBus` class in `event_logging.py` — a simple callable holder with `log_event()` method
2. `GameSession.__init__` creates `self._event_bus = EventBus(handler)` instead of calling `set_event_handler()`
3. Inject `EventBus` into services that currently call `log_event()` (primarily `BattleEngine`, `TurnEngine`, sub-engines)
4. Keep module-level `log_event()` function as a deprecated fallback that delegates to a thread-local or warns
5. Incremental migration: services that receive EventBus use it directly; others fall back to global until migrated

---

## Checklist

### Discovery
- [ ] Grep for all `log_event(` calls across the codebase — document every call site
- [ ] Grep for all `set_event_handler(` calls — document where the global is set
- [ ] Grep for all `from game.core.event_logging import` — document consumers
- [ ] Categorize call sites: simulation-layer vs strategy-layer vs UI-layer

### Tests First (TDD)
- [ ] Write test: `EventBus` created with handler receives events via `log_event()`
- [ ] Write test: `EventBus` created without handler silently drops events (no crash)
- [ ] Write test: two `EventBus` instances route events independently
- [ ] Write test: `GameSession` creates its own `EventBus` — events route to correct session
- [ ] Write test: creating a second `GameSession` does NOT affect first session's event routing
- [ ] Run tests — confirm isolation tests fail (global handler means second session overwrites first)

### Implementation
- [ ] Create `EventBus` class in `game/core/event_logging.py` with `log_event()` method
- [ ] Update `GameSession.__init__` to create `self._event_bus = EventBus(...)` instead of `set_event_handler()`
- [ ] Add `event_bus` parameter to `TurnEngine.__init__` — store and use for event logging
- [ ] Add `event_bus` parameter to `BattleEngine.__init__` — store and use for event logging
- [ ] Update module-level `log_event()` to log a deprecation warning on first use (optional, for migration tracking)
- [ ] Thread `event_bus` through the GameSession → TurnEngine → sub-engine chain
- [ ] Run tests — confirm they pass

### Verification
- [ ] Run full test suite (`python Tools/test_sharded/test_sharded.py`) — no regressions
- [ ] Verify `set_event_handler()` is no longer called from `GameSession.__init__`
- [ ] Verify new `EventBus` instances are isolated (test from TDD step confirms this)
