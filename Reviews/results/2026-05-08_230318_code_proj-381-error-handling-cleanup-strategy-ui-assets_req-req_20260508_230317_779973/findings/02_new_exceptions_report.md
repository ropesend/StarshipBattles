# New Exceptions Assessment

## Summary

All 4 new PROJ-381 exceptions are properly raised in production code (none are dead). OWNERSHIP_MISMATCH/V005 is used in production. The exception hierarchy is correct across all 4 classes. ImageUnexpectedError is fully symmetric with LLMUnexpectedError. Two MAJOR issues found: TurnFailedError docstring claims 4 properties but only defines 2; docs/05_ERROR_HANDLING.md hierarchy tree is missing all 4 new exceptions. Several MINOR issues: context key naming inconsistency, BattleResolutionError rich context gets buried through re-wrap chain, and the TurnFailedError test fixture omits `turn_number`.

---

## Exception-by-Exception Analysis

### ImageUnexpectedError

- **Base class:** ImageException → GameException (correct per hierarchy)
- **Raised at (files:line):** `game/ui/services/image/background.py:229-232`
- **Caught at (files:line or NEVER):** Not caught externally; stored as `self._error` in `ImageBackgroundCall`. Tested in `tests/unit/ui/services/image/test_background.py:51-64`.
- **Context fields:** `{"original_exception_type": str}`
- **Symmetric with LLMUnexpectedError?:** Yes — identical constructor shape (`message`, `context={...}`), same `original_exception_type` context key, same intent (keep worker thread from leaking with `_status` stuck on RUNNING), both use manual `wrapped.__cause__ = e` instead of `raise from` (correct for the worker-thread pattern where the exception is stored, not re-raised), both set `code=None` intentionally.
- **Issues:** None.

### SessionInitializationError

- **Base class:** StrategyException → GameException (correct per hierarchy)
- **Raised at (files:line):** `game/strategy/engine/game_session.py:171-174`
- **Caught at (files:line or NEVER):** Tested at `tests/unit/strategy/test_game_session.py:307`. Not caught in production UI code — an uncaught SessionInitializationError would propagate to the top-level crash handler, which is arguably the correct behavior for a fatal initialization failure.
- **Context fields:** `{"original_type": str}` (note: inconsistent key name vs. `original_exception_type` used by ImageUnexpectedError/LLMUnexpectedError)
- **Issues:**
  - MINOR: Context key `original_type` differs from `original_exception_type` used by the UnexpectedError family. No functional impact but inconsistent.
  - `code` is not set (defaults to `None`) — acceptable since the init failure is fatal and no programmatic branching on code is expected.

### TurnFailedError

- **Base class:** StrategyException → GameException (correct per hierarchy)
- **Raised at (files:line):** `game/strategy/facade/strategy_session_facade.py:197-201`
- **Caught at (files:line):** `game/ui/screens/strategy_game_state_manager.py:129` (and defensive fallback at line 149 for raw EnginePhaseError). Tested at `tests/integration/ui/test_strategy_turn_error_boundary.py:159-185`.
- **Context fields:** Propagated from EnginePhaseError via `dict(e.context or {})`. Canonical fields: `phase_name`, `tick`, `turn_number`, `original_error`, `original_type`, `save_path`.
- **Issues:**
  - **MAJOR:** Docstring at `exceptions.py:235-237` claims `tick`, `turn_number`, and `original_type` are "surfaced as properties for the modal dialog rendering." Only `phase_name` (line 240-243) and `recoverable` (line 245-248) are defined as properties. The values are accessible via `context` dict (and the UI at `strategy_game_state_manager.py:283-286` reads them from context directly), but the class does not deliver the advertised property interface.
  - MINOR: The test fixture at `test_strategy_turn_error_boundary.py:167-175` creates a TurnFailedError with context `{"phase_name", "tick", "original_type"}` but omits `turn_number` — a field that EnginePhaseError always includes (`turn_engine.py:303`). Not a bug, but the test does not exercise the full canonical context shape.

### BattleResolutionError

- **Base class:** StrategyException → GameException (correct per hierarchy)
- **Raised at (files:line):** `game/strategy/adapters/simulation_adapter.py:307-316`
- **Caught at (files:line or NEVER):** Never caught directly in production code. It is caught *implicitly* by `TurnEngine._time_phase()` (`turn_engine.py:286` `except Exception`) which re-wraps it as `EnginePhaseError`, and then the facade wraps that as `TurnFailedError`. Tested at `tests/unit/strategy/adapters/test_simulation_adapter.py:377-410`.
- **Context fields:** `{"fleet_ids": list, "empire_ids": list, "hex_coord": tuple|None, "original_type": str}`
- **Issues:**
  - MINOR: Because BattleResolutionError is never caught directly (only via the broad `except Exception` in `_time_phase`), its rich context (`fleet_ids`, `empire_ids`, `hex_coord`) gets buried behind `__cause__` when re-wrapped as `EnginePhaseError`. The `__cause__` chain does preserve it, so a crash dump that walks the chain can recover it, but consumer code that only inspects top-level `TurnFailedError.context` will see only the EnginePhaseError fields (`phase_name`, `tick`, etc.). The original `fleet_ids`/`empire_ids`/`hex_coord` are invisible at the UI layer.
  - MINOR: Uses `original_type` as context key (like SessionInitializationError) rather than `original_exception_type` (like the UnexpectedError family).

### OWNERSHIP_MISMATCH / V005

- **Used in production?:** Yes, at `game/strategy/engine/handlers/base.py:195` (`code=ErrorCode.OWNERSHIP_MISMATCH.value`). Tested at `tests/unit/strategy/engine/test_base_command_handler.py:83-96`.
- **Issues:** None.

---

## Findings

### CRIT-001: No dead exception classes

All 4 new exception classes (`ImageUnexpectedError`, `SessionInitializationError`, `TurnFailedError`, `BattleResolutionError`) are raised in at least one production code path. No dead exception classes found.

### MAJ-001: TurnFailedError docstring claims properties that don't exist

**File:** `game/core/exceptions.py:235-237`

**Summary:** The docstring states that `tick`, `turn_number`, and `original_type` are "surfaced as properties for the modal dialog rendering." Only `phase_name` (line 240) and `recoverable` (line 245) are actually defined as `@property`. The UI accesses the missing fields via `context` dict directly (`strategy_game_state_manager.py:283-286`), so functionality is unaffected, but the class does not deliver the advertised interface. Either add the 3 missing properties or correct the docstring.

### MAJ-002: docs/05_ERROR_HANDLING.md hierarchy tree is stale

**File:** `docs/05_ERROR_HANDLING.md:32-60`

**Summary:** The exception hierarchy tree does not include any of the 4 PROJ-381 exceptions (`SessionInitializationError`, `TurnFailedError`, `BattleResolutionError` under `StrategyException`; `ImageUnexpectedError` under `ImageException`). `ImageUnexpectedError` is mentioned in prose at line 74-75 but not in the tree. The tree should be updated:

```text
StrategyException
  EnginePhaseError
  SessionInitializationError
  TurnFailedError
  BattleResolutionError
ImageException
  ...
  ImageUnexpectedError
```

### MIN-001: Inconsistent original-exception context key naming

**File:** `game/core/exceptions.py` (usage across 4 files)

**Summary:** `ImageUnexpectedError` and `LLMUnexpectedError` use context key `original_exception_type`. `SessionInitializationError` and `BattleResolutionError` use `original_type`. The `EnginePhaseError` also uses `original_type` (and `original_error`). Consider converging on a single key name (preferably `original_type` since it's shorter and already used in the strategy-layer exceptions).

### MIN-002: BattleResolutionError rich context buried by re-wrap chain

**File:** `game/strategy/adapters/simulation_adapter.py:307-316` and `game/strategy/engine/turn_engine.py:286-308`

**Summary:** When `BattleResolutionError` is raised, it carries `fleet_ids`, `empire_ids`, and `hex_coord` in context. It is caught by `TurnEngine._time_phase()`'s broad `except Exception` and re-wrapped as `EnginePhaseError` with a new context that only includes `phase_name`, `tick`, `turn_number`, `original_error`, `original_type`. The facade then wraps that as `TurnFailedError`. The rich battle context is preserved on `__cause__.__cause__` but is invisible to consumers that only inspect `TurnFailedError.context`. Consider propagating the battle context keys into the wrapping EnginePhaseError context so crash-dump consumers don't need to walk the exception chain.

### MIN-003: TurnFailedError test omits `turn_number` context field

**File:** `tests/integration/ui/test_strategy_turn_error_boundary.py:167-175`

**Summary:** The test creates a `TurnFailedError` with context `{"phase_name": "production", "tick": 12, "original_type": "RuntimeError"}` but omits `turn_number`, which `EnginePhaseError` always includes (`turn_engine.py:303`). Not a functional bug, but the test fixture doesn't match the production context shape.
