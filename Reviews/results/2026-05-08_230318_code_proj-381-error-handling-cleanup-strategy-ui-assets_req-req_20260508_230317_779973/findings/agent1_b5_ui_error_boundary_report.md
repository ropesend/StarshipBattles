# B-5 UI Error Boundary — Findings Report

**Reviewer:** Agent1 (OpenCode)
**Scope:** `game/ui/screens/strategy_game_state_manager.py` (B-5), `game/strategy/engine/turn_engine.py`, `game/strategy/engine/turn_state_snapshot.py`, `game/strategy/facade/strategy_session_facade.py` (B-4), `game/strategy/engine/game_session.py` (B-11), `tests/integration/ui/test_strategy_turn_error_boundary.py`
**Date:** 2026-05-08

---

## Finding B5-001: CRITICAL
**File:** `game/ui/screens/strategy_game_state_manager.py:312-317`
**Summary:** `_show_turn_failed_dialog` creates a raw `pygame_gui.windows.UIMessageWindow` instead of a `StrategyModalWindow` subclass, bypassing Pattern #31 modal tracking.
**Detail:** The method constructs `pygame_gui.windows.UIMessageWindow(rect=..., html_message=..., manager=..., window_title=...)` directly. `UIMessageWindow` inherits from `UIWindow`, not `StrategyModalWindow`, so it never calls `window_manager.register_modal(self)`. Pattern #31 (`docs/02_PATTERNS.md` §31) requires strategy modal windows to register via `StrategyWindowManager.register_modal()` so that `has_modal_open()` and `_is_blocking_ui_element_at()` correctly block input. A player can click through the galaxy map, issue fleet commands, or advance the turn again while the error dialog is visible — there is no modal input blocking. Additionally, there is no cleanup path through `StrategyWindowManager.unregister_modal()` if the screen transitions while this dialog is open, leaving an orphaned pygame_gui element.
**Recommendation:** Replace the raw `UIMessageWindow` with a `StrategyModalWindow` subclass (e.g. `TurnFailedDialog`) that accepts `window_manager` and calls `super().__init__(..., window_manager=window_manager)`. The `StrategyScreen.ui` already holds a reference to the `StrategyWindowManager` — thread it through.

---

## Finding B5-002: MAJOR
**File:** `tests/integration/ui/test_strategy_turn_error_boundary.py:84-118`
**Summary:** Regression test mocks the exception class directly (`screen._facade.process_turn.side_effect = EnginePhaseError(...)`) rather than triggering the actual failure path through the TurnEngine.
**Detail:** The test at line 104 sets `screen._facade.process_turn.side_effect = err` with a hand-constructed `EnginePhaseError`. This verifies the UI catch clause works but does not exercise: (a) the sub-engine → `_time_phase` wrapping chain, (b) snapshot capture in `process_turn()`, (c) snapshot rollback via `TurnStateSnapshot.restore()`, or (d) the facade's `EnginePhaseError → TurnFailedError` conversion in production. The test validates the `except` block, not the real failure path. A true regression test would inject a faulty sub-engine into `TurnEngineConfig` (e.g., a mock `harvesting_engine` that raises on execute), call `process_turn()`, and verify the session state is intact afterward.
**Recommendation:** Add an integration test that constructs a real `GameSession` (or uses `build_test_turn_engine` from `tests/fixtures/turn_engine.py`) with a mock sub-engine configured via `dataclasses.replace(cfg, harvesting_engine=mock_raises_engine)`. Assert that `process_full_turn()` catches the error, the dialog appears, and subsequent reads from the session (planet state, fleet positions) match pre-turn values.

---

## Finding B5-003: MAJOR
**File:** `game/core/exceptions.py:227-248`
**Summary:** `TurnFailedError` lacks dedicated properties for `turn_number` and `save_path`, despite `_time_phase` (PROJ-381 B-2) now emitting both in error context.
**Detail:** `_time_phase()` at `turn_engine.py:303-304` populates context with `"turn_number": getattr(self, "_current_turn_number", 0)` and `"save_path": getattr(self, "_current_save_path", None)`. The facade at `strategy_session_facade.py:199` faithfully copies the full context dict via `dict(e.context or {})`. However, `TurnFailedError` only exposes `phase_name` (line 241-243) and `recoverable` (line 245-248) as properties. The `_show_turn_failed_dialog` method at `strategy_game_state_manager.py:283-286` reads `phase_name`, `tick`, and `original_type` from the raw context dict — it ignores `turn_number` and `save_path` entirely. The dialog message at line 306 says "Turn has been rolled back" but never states WHICH turn number failed.
**Recommendation:** Add `turn_number` and `save_path` properties to `TurnFailedError` mirroring the `phase_name` pattern. Update `_show_turn_failed_dialog` to include `turn_number` in the modal body text so the player sees "Turn 42 rolled back" rather than an anonymous rollback message.

---

## Finding B5-004: MINOR
**File:** `game/strategy/engine/turn_engine.py:282-285`
**Summary:** When `_time_phase` catches an already-wrapped `EnginePhaseError`, it re-raises without adding `turn_number`/`save_path` to the context, unlike the exception-wrapping branch.
**Detail:** The `except EnginePhaseError` branch at line 282 re-raises the existing error as-is. Only the `except Exception` branch at lines 297-308 constructs a new `EnginePhaseError` with `turn_number` and `save_path` in context. If a sub-engine raises its own `EnginePhaseError` directly (e.g., `raise EnginePhaseError("reason", code=..., context={...})`), the B-2 breadcrumb fields are absent. This creates an inconsistency: failures that pass through `_time_phase` wrapping get full context, but failures from sub-engines that construct their own `EnginePhaseError` do not.
**Recommendation:** In the `except EnginePhaseError` branch, defensively merge `turn_number` and `save_path` into the existing error's context (via `.setdefault()` or similar) before re-raising, so every `EnginePhaseError` escaping `_time_phase` carries the canonical fields regardless of origin.

---

## Finding B5-005: INFO
**File:** `game/strategy/engine/game_session.py:165-174`
**Summary:** B-11 null-object recovery correctly re-raises `SessionInitializationError` after setting null defaults — the "fail loudly with degraded state" contract holds.
**Detail:** On any `GameInitializer.initialize()` failure, `self.galaxy = None`, `self.empires = []`, `self.systems = []`, `self.human_player_ids = []`, and `self.active_empire = None` are set before `raise SessionInitializationError(...) from e`. The session is left in a deterministic null-object state rather than partially constructed with `galaxy` unset but `empires` pointing at a half-built list. The re-raise propagates the typed exception to the caller. If a caller ignores the exception and uses the session, it will get `AttributeError` on `None` — noisy, not silent.
**Recommendation:** No change required. Contract is satisfied. The intentional broad catch at line 165 carries the required justification comment.

---

## Finding B5-006: INFO
**File:** `game/strategy/facade/strategy_session_facade.py:195-200`
**Summary:** Facade B-4 mapping `EnginePhaseError → TurnFailedError` correctly preserves the original cause chain via `from e` and shallow-copies context.
**Detail:** The `raise TurnFailedError(..., context=dict(e.context or {})) from e` at line 196-200 chains `TurnFailedError.__cause__ → EnginePhaseError.__cause__ → (original sub-engine exception from _time_phase's own `from e`)`. The `dict(e.context or {})` creates a shallow copy — safe because context values are all strings/ints. The three layers of the error hierarchy (StrategyException → TurnFailedError → EnginePhaseError) are correctly preserved.
**Recommendation:** No change required. The implementation follows `docs/05_ERROR_HANDLING.md` §244-252 (preserve causes pattern) correctly.

---

## Question Answers

### Q1: Modal dialog per Pattern #31 or one-shot bypass?
**One-shot bypass.** `_show_turn_failed_dialog` creates `pygame_gui.windows.UIMessageWindow` directly (line 312), which does not subclass `StrategyModalWindow` and never registers with `StrategyWindowManager`. See **B5-001**.

### Q2: Does UI know post-error state is recoverable?
**Partially.** The modal dialog message includes "Turn has been rolled back — empire state is preserved" (line 306), and `process_full_turn()` correctly skips auto-save and event-log popup on failure (lines 164-170). However, the dialog does not display the rolled-back turn number despite `_time_phase` including it in context. See **B5-003**.

### Q3: Does the regression test exercise the actual failure path?
**No.** The test mocks `screen._facade.process_turn.side_effect` with a hand-constructed exception rather than injecting a faulty sub-engine into the TurnEngine. It verifies the catch clause but not snapshot/rollback or the full production chain. See **B5-002**.

### Q4: Does TurnFailedError carry canonical context fields?
**Partially.** The context dict travels through the chain (`_time_phase → EnginePhaseError → TurnFailedError`), including `turn_number` and `save_path` from B-2. But `TurnFailedError` only exposes `phase_name` as a property — `turn_number`, `save_path`, `tick`, and `original_type` require raw dict access. See **B5-003**.

### Q5: Is B-11 null-object recovery genuinely "fail loudly"?
**Yes.** `GameSession.__init__` sets `galaxy=None, empires=[], systems=[], human_player_ids=[], active_empire=None` and then re-raises `SessionInitializationError`. Callers get a typed exception; ignoring it produces `AttributeError` on `None`, not silent corruption. See **B5-005**.

### Q6: Does B-4 mapping preserve original cause chain?
**Yes.** `raise TurnFailedError(...) from e` at `strategy_session_facade.py:200` chains through `EnginePhaseError.__cause__` to the original sub-engine exception. Context is shallow-copied via `dict(e.context or {})`. See **B5-006**.
