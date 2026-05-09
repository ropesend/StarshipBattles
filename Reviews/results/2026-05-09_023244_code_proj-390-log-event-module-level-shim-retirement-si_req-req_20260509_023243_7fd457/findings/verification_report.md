# Finding 1: Final Grep Verification — ALL PASS

**Severity:** INFO (pass)
**Verified:** All three grep patterns return zero hits in production/test code.

## grep-1: `from game\.core\.event_logging import (log_event|set_event_handler|get_event_handler)`

ZERO hits under `game/`, `tests/`, `combat_lab/`, `Tools/`. Exit code 1 (no matches).

All current imports from `game.core.event_logging` import **only** `EventBus`:
- `game/core/__init__.py:105` — re-export
- `game/strategy/engine/game_session.py:59`
- `tests/integration/strategy/test_combat_shortcut_paths.py:28`
- `tests/integration/strategy/test_replay_capture_e2e.py:309`
- `tests/unit/core/event_logging/test_event_bus.py:12`
- `tests/unit/strategy/conflict_resolution/test_logging_and_lookups.py:25`
- `tests/unit/strategy/engine/test_conflict_resolution_event_replay.py:15`
- `tests/unit/strategy/engine/test_production_refactor.py:312`
- `tests/unit/strategy/engine/test_superweapon_event_payloads.py:24`
- `tests/unit/strategy/engine/test_superweapon_order_processor.py:189`
- `tests/unit/strategy/test_engine_event_emission.py:10`
- `tests/unit/strategy/test_game_session_events.py:40`

## grep-2: `_event_handler`

All references are to `GameSession._create_event_handler()` (a private method on GameSession class), NOT to the deleted module-level `_event_handler` global:
- `game/strategy/engine/game_session.py:88` — `self._event_bus = EventBus(self._create_event_handler())`
- `game/strategy/events/event_log.py` — docstring reference
- Tests — references to the `_create_event_handler` method name

The old module-level `_event_handler = None` global at `game/core/event_logging.py` is deleted. No production code accesses a module-level `_event_handler`.

## grep-3: `event_logging\.log_event`

ZERO hits. Exit code 1 (no matches).

---

# Finding 2: PROJ-382 'Already-Done' Claim — VERIFIED CORRECT

**Severity:** INFO (pass)
**Verified:** All three files use constructor-injected EventBus, not module-level shim.

## empire.py
- `def remove_fleet(self, fleet, event_bus=None)` — parameter `event_bus` is optional kwarg at line 87
- `event_bus.log_event("EMPIRE_FLEET_REMOVED", ...)` — called on injected bus at line 109
- Guard: `if cancelled and event_bus is not None` prevents None access

## fleet.py
- `def merge_with(self, other_fleet: 'Fleet', event_bus=None)` — parameter at line 379
- `event_bus.log_event("FLEET_MERGE_SOURCE", ...)` — line 408
- `event_bus.log_event("FLEET_MERGE_TARGET", ...)` — line 427
- Guard: `if event_bus is not None` before each call

## conflict_resolution_engine.py
- Constructor: `event_bus=None` parameter at line 57
- `self._event_bus = event_bus` stored at line 83
- `self._event_bus.log_event("CONFLICT_RESOLUTION", ...)` at line 158
- Guard: `if not self._event_bus: return` at line 136

**None of these files import `log_event`, `set_event_handler`, or `get_event_handler` from `game.core.event_logging`.**

---

# Finding 3: EventBus Session-Scoped — CORRECTLY NOT on ApplicationContext

**Severity:** INFO (pass)
**Verified:** EventBus is session-scoped per PROJ-252 architecture. Adding it to ApplicationContext would reintroduce the process-global-state problem.

## Evidence

**GameSession constructs its own EventBus** at `game/strategy/engine/game_session.py:88`:
```python
self._event_bus = EventBus(self._create_event_handler())
```

Each `GameSession` instance creates a fresh `EventBus`. The bus is threaded through to engines via `TurnEngineConfig.create_default()` at line 134:
```python
event_bus=self._event_bus,
```

**`ApplicationContext` does NOT reference EventBus** — grep of `game/context.py` for `EventBus` returns zero hits. The 10 context-managed services are: `RegistryManager`, `Profiler`, `ComponentCacheManager`, `PolicyManager`, `AssetManager`, `SpriteManager`, `ShipThemeManager`, `GameSettings`, `LLMProvider`, `ImageProvider`.

**PROJ-252 design** (`Projects/deep_archive/PROJ-251-300/PROJ-252/decisions.md`):
> "Keep module-level `log_event()` as deprecated convenience during migration. Incremental migration: inject EventBus where available, fall back to global, then ratchet."

PROJ-252 introduced the session-scoped EventBus with the explicit intent of eliminating process-global event state. The `log_event()` module-level shim was always a migration aid. PROJ-390 completes the migration by deleting the aid.

**Isolation impact:** If EventBus were on ApplicationContext (process-scoped):
- Two `GameSession` instances in the same process would share a bus
- Test isolation between function-scoped sessions would break
- Events from one session would leak into another's event log
- This is exactly the problem PROJ-252 was designed to prevent

---

# Finding 4: `_default_event_logger` No-Op — CORRECT SEMANTICS

**Severity:** INFO (pass)
**Verified:** The no-op is the right semantics; all callers that need logging inject their own `event_logger=` callable.

## Current state

`game/simulation/entities/projectile.py`:
```python
def _default_event_logger(event_type: str, **kwargs: Any) -> None:
    """PROJ-390: no-op default event-log dispatcher. ..."""
    return
```

## Call sites within projectile.py

Two call sites in `Projectile.update()`:
1. `self._event_logger("SEEKER_EXPIRE", seeker_id=str(id(self)), reason="lifetime", tick=0)` — on endurance expiry
2. `self._event_logger("SEEKER_EXPIRE", seeker_id=str(id(self)), reason="max_range", tick=0)` — on range expiry

Both guarded by `if self.type == AttackType.MISSILE` — only seekers emit these events.

## Injection path

```python
self._event_logger: Callable[..., None] = kwargs.get(
    "event_logger", _default_event_logger
)
```

Callers that need telemetry (BattleEngine tests, replay tools) pass `event_logger=mylogger`. Callers that don't care get a silent no-op. The old default lazy-imported and called the process-global `log_event()` shim, which leaked state across sessions.

## Test coverage

The commit message reports 226 projectile tests pass. Tests that assert on event payloads inject their own `event_logger=` callable rather than relying on a process-global fallback.

---

# Finding 5: conftest.py Cleanup Hook Removal — VERIFIED

**Severity:** INFO (pass)
**Verified:** The hook is gone; no dangling reference exists. Replacement comment explains the retirement.

## Removed (from parent commit `f8a396655`)
```python
# PROJ-390: module-level event handler global was retired; each
# GameSession owns its own EventBus, so there's nothing to reset
# at process scope between tests.
```

Previously, the `reset_game_state` fixture's `finally` block would call `set_event_handler(None)` to reset the module-level `_event_handler` global. That global no longer exists — the cleanup was dead code.

## Verification
- No `set_event_handler` or `get_event_handler` imports in conftest.py
- No `event_handler` references in conftest.py
- The `_event_handler` global in `event_logging.py` is fully deleted
- Each `GameSession` creates and owns its EventBus for its lifetime; tests that create sessions manage their own buses
- For tests that don't create sessions (pure unit tests on EventBus), `test_event_bus.py` creates fresh `EventBus()` instances inline — no global to reset

---

# Finding 6: Deleted Test File — VERIFIED SHIM-ONLY

**Severity:** INFO (pass)
**Verified:** Every test in `tests/unit/core/event_logging/test_event_logging.py` tested only the deprecated module-level shim. No coverage regression.

## Deleted test contents (from parent commit `f8a396655`)

### `TestEventHandler` (4 tests)
| Test | Verdict |
|---|---|
| `test_set_and_get_event_handler` | Sets/gets the module-level `_event_handler` global via `set_event_handler`/`get_event_handler` — **DEPRECATED SHIM** |
| `test_clear_event_handler` | Clears the module-level global via `set_event_handler(None)` — **DEPRECATED SHIM** |
| `test_default_handler_is_none` | Asserts default handler is None — **DEPRECATED SHIM** |
| `cleanup_event_handler` fixture | Calls `set_event_handler(None)` in autouse teardown — **DEPRECATED SHIM** |

### `TestLogEvent` (4 tests)
| Test | Verdict |
|---|---|
| `test_log_event_calls_handler` | Calls `log_event()` and asserts handler received args — **DEPRECATED SHIM** |
| `test_log_event_no_handler_does_nothing` | Calls `log_event()` with handler=None — **DEPRECATED SHIM** |
| `test_log_event_handler_exception_isolated` | Asserts module-level handler exception doesn't crash caller — **DEPRECATED SHIM** |
| `test_log_event_multiple_calls` | Calls `log_event()` 3 times, asserts order — **DEPRECATED SHIM** |

Every test exercises the deleted `log_event()`, `set_event_handler()`, and `get_event_handler()` functions. None tests `EventBus` — that class is covered in `tests/unit/core/event_logging/test_event_bus.py` (82 lines, 12 tests covering constructor-injected bus, handler isolation, exception safety, set_handler, no-handler silent drop).

**No coverage regression.**

---

# Finding 7: docs/02_PATTERNS.md §10 Update — VERIFIED ACCURATE

**Severity:** INFO (pass)
**Verified:** Compat-shim sentence removed; constructor injection is the only documented pattern.

## Current §10 text (Strategy/core event logging section):

> `game/core/event_logging.py::EventBus` is separate structured event logging for simulation/strategy events.
> Each `GameSession` creates its own event bus to avoid process-global mutable state.
> Constructor injection is the only supported pattern: every event-emitting engine, handler, or data class takes an `event_bus: EventBus` parameter (or, for projectiles, an `event_logger=` callable that closes over a session-scoped bus). PROJ-390 retired the module-level `log_event()` / `set_event_handler()` / `get_event_handler()` compatibility shim — **there is no fallback path**.

## Verification checklist:
- [x] "compatibility shim" sentence from old version is gone
- [x] "Constructor injection is the only supported pattern" — accurately describes current state
- [x] PROJ-390 retirement explicitly noted
- [x] "no fallback path" — correct; the deleted symbols don't exist anywhere
- [x] No stale references to `log_event()`, `set_event_handler()`, or `get_event_handler()` remain in §10
- [x] Projectile-specific `event_logger=` callable pattern is documented as the variant for that data class
