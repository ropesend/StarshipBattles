# Architecture & Rules Compliance

## Summary

Overall compliance is strong. All four error boundaries (B-4, B-5, B-6, B-11) follow Rule 3 — no compatibility shims, no fallback systems, proper fail-loud behavior. No cross-layer import violations found in any of the specified files. Pattern #19 (Error Boundary) is fully compliant in `TurnEngine`. One CRITICAL finding: the B-5 turn-failed error dialog bypasses Pattern #31 (StrategyModalWindow), using a raw `UIMessageWindow` that does not block strategy-screen input.

## Rule 3 Compliance

### B-11 GameSession null-object recovery
**File:** `game/strategy/engine/game_session.py:149-174`
**Verdict: FAILS LOUDLY — COMPLIANT**

The `try/except` in `__init__` catches any exception from `GameInitializer.initialize()`, sets `self.galaxy = None`, `self.empires = []`, `self.systems = []`, `self.human_player_ids = []`, `self.active_empire = None`, then **re-raises** as `SessionInitializationError` (with `from e` for cause chaining). The null-object state leaves the session deterministic rather than partially constructed, but callers must handle the exception — the session cannot be used successfully after this. The broad catch has a proper justification comment. This is a clean error boundary, not a silent mask.

### B-4 EnginePhaseError → TurnFailedError
**File:** `game/strategy/facade/strategy_session_facade.py:192-202`
**Verdict: PROPER ERROR BOUNDARY — COMPLIANT**

The facade `process_turn()` catches `EnginePhaseError` and re-raises as `TurnFailedError`, preserving `__cause__`, `code`, and `context`. The docstring explicitly states the intent: "so the UI never has to import a sub-engine exception type." `TurnFailedError` is a proper `StrategyException` subclass in `game/core/exceptions.py:227` with convenience properties (`phase_name`, `recoverable`). This is exactly the facade boundary pattern the architecture prescribes — not a shim to make old code work, but a deliberate API contract.

### B-6 SimulationException wrap
**File:** `game/strategy/adapters/simulation_adapter.py:292-316`
**Verdict: PROPER ERROR BOUNDARY — COMPLIANT**

The adapter catches `SimulationException` from `run_battle()` and wraps it as `BattleResolutionError`, enriching the context with `fleet_ids`, `empire_ids`, and `hex_coord` before re-raising with `from e`. `BattleResolutionError` (at `game/core/exceptions.py:251`) is a proper `StrategyException` subclass. No fallback to old behavior exists — the only code paths lead through this adapter. The `_resolve_registries` helper at line 39-52 centralizes the `None → get_default_registry_provider()` fallback, which is a documented PROJ-306 allowance, not a shim.

### B-5 UI error boundary
**File:** `game/ui/screens/strategy_game_state_manager.py:128-158, 272-317`
**Verdict: COMPLIANT for Rule 3, NON-COMPLIANT for Pattern #31**

The `process_full_turn()` method catches `TurnFailedError` (primary) and `EnginePhaseError` (defensive fallback) and surfaces a modal dialog via `_show_turn_failed_dialog()`. No fallback system — either the modal shows or it doesn't, and the logging path (headless/manager=None) is a genuine degraded case, not a compatibility shim. However, the dialog itself is a raw `pygame_gui.windows.UIMessageWindow`, not a `StrategyModalWindow` — see CRIT-002 below.

### TurnStateSnapshot save_json migration
**File:** `game/strategy/engine/turn_state_snapshot.py:128-136`
**Verdict: NO FALLBACK — COMPLIANT**

The crash dump write was changed from a manual `os.makedirs` + file write to `save_json()` (atomic temp-file+rename pattern). The comment notes "the prior os.makedirs call is redundant" — the old manual write code is deleted, not kept as a fallback. The old behavior is fully replaced.

## Layer Violations

| File | Import | Allowed? | Severity |
|---|---|---|---|
| `game/ui/screens/strategy_game_state_manager.py:97` | `from game.strategy.systems.save_game_service import SaveGameService` | Yes (UI → Strategy) | None |
| `game/ui/services/image/background.py` (all imports) | `game.core.*`, `game.ui.services.image.*` only | Yes (Core + UI-local) | None |
| `game/assets/asset_manager.py` (all imports) | `game.core.*` only | Yes (Core only) | None |
| `game/strategy/services/design_validator.py:73` | `from game.simulation.entities.ship import Ship` | Yes (Strategy → Simulation) | None |
| `game/strategy/services/design_validator.py:83` | `from game.simulation.validation.ship_validator import ShipDesignValidator` | Yes (Strategy → Simulation) | None |
| `game/ui/services/tkinter_utils.py` (all imports) | `os`, `tkinter`, stdlib only | Yes (no game imports) | None |

**Cross-layer search results:**
- `from game.strategy` in `game/assets/` — **0 matches** (Compliant)
- `from game.ui` in `game/strategy/` — **0 matches** (Compliant)
- `from game.strategy` in `game/ui/` — **214 matches** (All allowed: UI → Strategy per architecture §Layer Model)

No layer violations detected in any of the specified files or via cross-layer search.

## Pattern Compliance

| Pattern # | File | Compliant? | Issues |
|---|---|---|---|
| #19 (Error Boundary) | `game/strategy/engine/turn_engine.py` | **Yes** | Snapshot captured before mutation (line 530-537), `_time_phase()` wraps raw exceptions as `EnginePhaseError` (line 258-310), `process_turn()` restores snapshot and re-raises (line 591-605). Fully conformant. |
| #31 (Strategy Modal) | `game/ui/screens/strategy_game_state_manager.py:312` | **No** | `_show_turn_failed_dialog()` creates a raw `pygame_gui.windows.UIMessageWindow` — does NOT subclass `StrategyModalWindow`, does NOT call `window_manager.register_modal()`. CRIT-002 below. |
| #10 (Event Bus) | `game/strategy/engine/conflict_resolution_engine.py:98,173,195` | **Yes** | `ConflictResolutionEngine` receives `EventBus` via constructor injection (line 98). Uses `self._event_bus.log_event(...)` explicitly (line 195), not module-level compatibility shim. Null-guarded at line 173. |
| #10 (Event Bus) | `game/core/event_logging.py:57-88` | **Drift** | Module-level `log_event()`, `set_event_handler()`, `get_event_handler()` are documented as "backward compatibility" shims (line 57-59). Pattern #10 contract says: "New code should prefer explicit `EventBus` injection." Not a PROJ-381 regression — pre-existing drift documented in patterns. MAJ-002 below. |

## Accidental Shim Detection

Search scope: all `game/` Python files, focused on PROJ-381 modified files.

| Pattern | Matches | Assessment |
|---|---|---|
| `try: ... except Exception: pass` | 0 | Clean |
| `hasattr(x, 'old_method')` compatibility checks | 0 | Clean |
| `# TODO: remove after migration` / `# DEPRECATED` | 0 | Clean |
| Dual code paths (`if new_way: ... else: old_way:`) | 0 | Clean |
| `getattr(x, 'field', default_fallback)` safety net for missing attributes | ~443 matches (ubiquitous pattern) | Reviewed in PROJ-381 files — all uses are legitimate defensive access (e.g., `getattr(session, "turn_number", 0)` for optional attributes on injected objects, `getattr(self._galaxy, 'get_system_at_location', None)` for null-guarded DI). No instance found where `getattr` serves as a compatibility shim for a deleted/renamed attribute. |

**Additional not-found patterns:**
- No `isinstance(x, OldClass)` fallback paths
- No `try: x.new_api() except AttributeError: x.old_api()` patterns
- No `# FIXME` or `# HACK` markers indicating transitional code

## Findings

### CRIT-001: Rule 3 confirmed — no shims detected across all four error boundaries

All four PROJ-381 error boundaries (B-4 facade, B-5 UI dialog, B-6 adapter, B-11 session init) implement proper error translation without fallback systems, monkey patches, or compatibility shims. Each boundary fails loudly, preserves cause chains, and enriches context. No save-file migration or dual-code-path patterns exist. `SessionInitializationError`, `TurnFailedError`, and `BattleResolutionError` are proper exception classes in `game/core/exceptions.py:201,227,251`. The `save_json` migration in `turn_state_snapshot.py` replaces (not wraps) the old manual write path.

### CRIT-002: Pattern #31 violation — B-5 error dialog bypasses StrategyModalWindow

`game/ui/screens/strategy_game_state_manager.py:312` — `_show_turn_failed_dialog()` constructs a raw `pygame_gui.windows.UIMessageWindow(rect=..., html_message=..., manager=..., window_title=...)` instead of subclassing `StrategyModalWindow`. Per Pattern #31 contract ("Use for every new strategy-screen modal that should block input. Do not add manual slots"), this dialog:

- **Does NOT register** with `StrategyWindowManager.register_modal()`
- **Does NOT block** strategy-screen input — the user can click through the error dialog and interact with the map/fleets while it's open
- **Does NOT deregister** on close — no `StrategyWindowManager.unregister_modal()` call

This is functionally incorrect for an error modal that should demand user attention before continuing. The `StrategyWindowManager.modal_window_count` / `has_modal_open()` / `_is_blocking_ui_element_at()` machinery will not see this dialog. A user could issue fleet orders or advance the turn again while the error dialog is still open, potentially compounding the problem that caused the phase failure.

**Recommendation:** Create a `TurnFailedDialog` class that inherits from `StrategyModalWindow`, accepts `window_manager` as a keyword argument, and registers/deregisters automatically. The existing body formatting logic can move into the new class.

### MAJ-001: Pattern #10 EventBus drift — module-level compatibility shim

`game/core/event_logging.py:57-88` — The module-level `log_event()`, `set_event_handler()`, and `get_event_handler()` functions are explicitly documented as a "compatibility shim" (line 57-59: "maintain backward compatibility while code is migrated"). Pattern #10 contract states: "New code should prefer explicit `EventBus` injection." This is a **pre-existing drift**, not introduced by PROJ-381. PROJ-381 code in `ConflictResolutionEngine` already uses explicit `EventBus` injection correctly. No immediate action required on this finding, but the shim should be removed once all consumers have migrated.

### MAJ-002: Defensive raw EnginePhaseError catch may encourage facade bypass

`game/ui/screens/strategy_game_state_manager.py:149-158` — The `process_full_turn()` method catches both `TurnFailedError` (from the facade) and raw `EnginePhaseError` (defensive fallback). The comment says: "if some path bypasses the facade and raises the raw EnginePhaseError, still surface it rather than crash." While this is well-intentioned defense-in-depth, it creates a code path where:

1. A future developer could call `session.turn_engine.process_turn()` directly (bypassing the facade) and the UI would silently handle it rather than failing with a clear import/type error.
2. The catch silently normalizes a facade-bypass — no warning log differentiates it from the expected `TurnFailedError` path (the log message includes "(raw EnginePhaseError — facade conversion bypassed)" but the user-visible dialog is identical).

The facade (B-4) already wraps `EnginePhaseError` → `TurnFailedError`. If a code path truly bypasses the facade, the correct behavior is to fail loudly so the developer fixes the bypass, not to silently accommodate it.

**Recommendation:** Remove the `except EnginePhaseError` block (lines 149-158) and rely solely on the `TurnFailedError` catch. If a code path bypasses the facade, the unhandled `EnginePhaseError` will propagate to the top-level crash handler, making the problem immediately visible.

### MIN-001: TurnFailedError convenience properties unused by B-5 dialog

`game/core/exceptions.py:227-248` — `TurnFailedError` defines `phase_name` and `recoverable` properties, but `_show_turn_failed_dialog()` at `strategy_game_state_manager.py:283` reads `error.context.get("phase_name", "unknown")` directly from the raw dict instead of using `error.phase_name`. The `recoverable` property is not checked at all — the dialog always shows "Turn has been rolled back" regardless of whether the error is retry-able.

**Recommendation:** Change `_show_turn_failed_dialog` to use `error.phase_name` instead of dict access. Consider surfacing `error.recoverable` to conditionally render different guidance text (e.g., "Turn has been rolled back — you may retry" vs "Turn failed — save and reload recommended").

### MIN-002: `if not self._event_bus:` null-guard is falsy but not None-specific

`game/strategy/engine/conflict_resolution_engine.py:173` — The `_log_combat_result` method uses `if not self._event_bus:` which would treat any falsy `EventBus` (including a valid-but-empty instance) as a signal to skip logging. In practice, `self._event_bus` is always either a real `EventBus` instance or `None`, so this is safe. Prefer `if self._event_bus is None:` for clarity.

### MIN-003: game_session.py exceeds 500 LOC ceiling

`game/strategy/engine/game_session.py` — 549 lines. The file is over the 500 LOC production ceiling. Lines 77-190 (`__init__`) account for ~113 lines of construction logic. Not a new regression (537-line pre-PROJ-381) but PROJ-381 added exception-handling lines (the B-11 boundary at 157-174) that pushed it over. Consider extracting the `GameInitializer.initialize()` + error-handling block to a factory method or extracting `from_dict` to `game_session_serde.py`.

