# Phase 1 Checklist: Rename All Production Code
**Status:** Complete

## Task 1.1: Establish baseline [Simple]
**Tests:** `pytest tests/unit/simulation/systems/ tests/unit/simulation/services/ tests/unit/ui/ -v`
- [x] Run baseline tests to confirm all pass before changes
**Notes:** Completed as part of implementation on 2026-04-05.

## Task 1.2: Rename BattleEngine.start() signature and body [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/ -v`
- [x] Line 12: Update module docstring example
- [x] Line 13: Update comment
- [x] Lines 239-240: Rename parameters `team0_ships` / `team1_ships`
- [x] Lines 250-251: Update docstrings
- [x] Lines 278-279: Update isinstance checks
- [x] Lines 282, 285: Update for-loops
- [x] Lines 294-296: Update controller variable names
- [x] Line 313: Update log message
**Notes:** Completed in commit d85718a2 on 2026-04-05. Line numbers updated to reflect current state.

## Task 1.3: Update BattleService._start_battle() call site [Simple]
**File:** `game/simulation/services/battle_service.py`
**Tests:** `pytest tests/unit/simulation/services/test_battle_service.py -v`
- [x] Lines 207-209: Changed keyword args to `team0_ships=self._team0_ships, team1_ships=self._team1_ships`
- [x] Run tests
**Notes:** Completed in commit d85718a2 on 2026-04-05.

## Task 1.4: Update BattleScreen.start() signature and body [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/test_battle_screen_simulation.py -v`
- [x] Line 227: Renamed parameters
- [x] Lines 235-236: Updated docstrings
- [x] Lines 259-260: Updated body references
- [x] Run tests
**Notes:** Completed in commit d85718a2 on 2026-04-05.

## Task 1.5: Update create_manual_battle() signature and body [Simple]
**File:** `game/ui/services/battle_factories.py`
**Tests:** `pytest tests/unit/ui/ -v`
- [x] Lines 102-103: Renamed parameters
- [x] Lines 111-112: Updated docstrings
- [x] Line 125: Updated variable references
**Notes:** Completed in commit abacb998 on 2026-04-05.

## Task 1.6: Update App.start_battle() signature and call [Simple]
**File:** `game/app.py`
**Tests:** Manual verification
- [x] Line 558: Renamed parameters in signature
- [x] Line 563: Updated call to `create_manual_battle()`
**Notes:** Completed in commit abacb998 on 2026-04-05.

## Task 1.7: Update battle_panels.py local variables [Simple]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** Manual visual verification
- [x] Lines 135-138: Renamed `team0_ships` / `team0_alive`
- [x] Lines 148-151: Renamed `team1_ships` / `team1_alive`
- [x] Keep display labels "TEAM 1" / "TEAM 2" unchanged (user-facing)
**Notes:** Completed in commit abacb998 on 2026-04-05.

## Task 1.8: Update simulation_adapter.py local variables [Simple]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ -v`
- [x] Lines 84-85: Renamed locals
- [x] Lines 89-90: Updated `_apply_shield_interference()` calls
- [x] Lines 94, 103, 109, 112, 117: Updated conditionals and survivor conversion
- [x] Lines 142-143: Updated `controller.add_ships()` calls
**Notes:** Completed in commit abacb998 on 2026-04-05.

## Task 1.9: Update setup_screen.py local variables [Simple]
**File:** `game/ui/screens/setup_screen.py`
**Tests:** Manual verification
- [x] Lines 100-104: Renamed locals and return tuple in `get_ships()`
**Notes:** Completed in commit abacb998 on 2026-04-05. `self.team1` and `self.team2` are UI data lists, not being renamed.

## Task 1.10: Run targeted test suite [Simple]
**Tests:** `pytest tests/unit/simulation/ tests/unit/ui/ tests/integration/ -v`
- [x] All targeted tests pass
- [x] No regressions in production code
**Notes:** Verified on 2026-04-05.
