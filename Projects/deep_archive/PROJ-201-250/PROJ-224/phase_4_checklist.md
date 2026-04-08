# PROJ-224 Phase 4: Minor Cleanup

## DUP-SYS-007: State Capture Duplication
- [x] Read `game/simulation/battle_controller.py` and `game/simulation/managers/battle_state_manager.py`
- [x] Identify where BattleController bypasses BattleStateManager for state capture
- [x] Route all state capture through BattleStateManager
- [x] Run tests

**Notes:** Line 206 of battle_controller.py called `BattleState.capture_from_engine()` directly, duplicating logic in `BattleStateManager.capture_state()`. Replaced with delegation to state manager.

## DUP-SYS-008: "No Active Battle" Guard Pattern
- [x] Read `game/simulation/services/battle_service.py`
- [x] Identify repeated null-check guard pattern (10 occurrences)
- [x] Extract `_require_engine()` helper — used for 6 occurrences returning BattleServiceResult
- [x] Run tests

**Notes:** 4 remaining guards return non-BattleServiceResult types (True, None, [], dict) — left as-is since they can't use the shared helper.

## DUP-UIS-004: ShipIO Path Construction
- [x] Read `game/ui/services/ship_io.py`
- [x] Find duplicated ships folder path construction (save vs load paths)
- [x] Extract shared `_ensure_ships_folder()` class method
- [x] Run tests

## DUP-SCR-006: Facade-or-Session Dispatch
- [x] Read the 3 UI screens with duplicated facade-or-session command dispatch
- [x] Evaluate if a shared helper is warranted or if this is acceptable
- [x] Acceptable as-is: only 3 occurrences across 2 files (build_queue_screen x2, empire_build_queue_window x1). Pattern is simple (3 lines) and most code already uses facade directly.
- [x] Run tests

## Completion
- [x] All items above checked off
- [x] Run full suite: `pytest tests/ -n 12` — all pass (13470 passed, 2 skipped)
- [x] Review all changes for consistency with docs (updated docs/03_CONVENTIONS.md for BattleTuning rename)
