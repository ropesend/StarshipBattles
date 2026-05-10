# Verification Report

## Critical Finding Verification

| Finding ID | File | Verdict | Reason |
|------------|------|---------|--------|
| Path 1 — No UI error boundary | `game/ui/screens/strategy_game_state_manager.py:122-128` | CONFIRMED | `try/finally` with no `except` clause. `EnginePhaseError` propagates through `StrategySessionFacade.process_turn()` (pass-through at line 181) and `GameSession.process_turn()` (re-raise at line 235), reaching `app.py:494-503` top-level crash handler — game exits. |
| Path 5 — Snapshot failure silences rollback | `game/strategy/engine/turn_engine.py:516-524, 583-588` | CONFIRMED | Lines 516-524: snapshot capture failure is caught, logged at `logger.error`, and execution continues with `snapshot = None` (comment: "better to process the turn than abort"). Lines 583-588: rollback is gated on `if snapshot and session: snapshot.restore(session)` — when `snapshot is None`, no rollback occurs. If a subsequent phase crashes after a failed snapshot capture, state is left in an inconsistent state, violating PROJ-251's documented contract of mandatory rollback. |
| Path 1 — Per-combat error isolation missing | `game/strategy/engine/conflict_resolution_engine.py:358, 450` | CONFIRMED | `_resolve_conflicts()` at line 358 calls `_resolve_combat_at_hex(occupants)` without `try/except`. `_resolve_combat_at_hex()` at line 450 calls `resolve_battle()` without `try/except`. Any single combat crash propagates through `resolve_all_conflicts` → `_time_phase('combat', ...)` (wraps in `EnginePhaseError`) → `process_turn()` catches → re-raises → game crashes. All remaining combats in the tick are abandoned. Combined with CRITICAL #2 (rollback may be unavailable), state corruption risk is elevated. |

## Downgraded Findings

None. All 3 CRITICAL findings are correctly classified. The 12 MAJOR findings across the shard reports (ERR-02-001, ERR-02-002, ERR-03-001, ERR-03-005, ERR-04-001 through ERR-04-007) are convention/comment issues, not data-loss or crash bugs, and the MAJOR rating is appropriate.

## Confirmed Critical

1. **No UI error boundary for turn processing failures** — `strategy_game_state_manager.py:122-128`. `try/finally` without `except` means any `EnginePhaseError` crashes the game at `app.py:494-503`. The facade pass-through (line 181) and session re-raise (line 235) are intentional per their docstrings, but the UI layer has no consumer. Fix: add `except EnginePhaseError` handler with error dialog and graceful cleanup. Effort: Low.

2. **Snapshot-capture failure disables rollback** — `turn_engine.py:516-524`. When `TurnStateSnapshot.capture()` fails, `snapshot` remains `None`, and the `if snapshot and session` guard at line 586 skips restoration. If the turn subsequently crashes, game state is left mutated. This is a gap between PROJ-251's documented guarantee ("state integrity via mandatory rollback") and the implementation. Fix: abort the turn immediately when snapshot capture fails (raise `EnginePhaseError` with `SNAPSHOT_FAILED`), rather than continuing without safety net. Effort: Low.

3. **No per-combat error isolation in conflict resolution** — `conflict_resolution_engine.py:358, 450`. A single combat crash aborts all remaining combats in the tick and crashes the game. No individual combat is wrapped in try/except. Combined with #2, there is re-entrant crash risk: if a buggy fleet pairing survives rollback (or rollback is unavailable), the same combat re-engages on the next turn and crashes again. Fix: wrap `_resolve_combat_at_hex()` call in try/except; log the crash, record a failure event, skip the bad combat, and continue to remaining combats. Effort: Medium.
