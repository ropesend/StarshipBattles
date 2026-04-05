# Phase 1 Checklist: Rename All Production Code
**Status:** Not Started

## Task 1.1: Establish baseline [Simple]
**Tests:** `pytest tests/unit/simulation/systems/ tests/unit/simulation/services/ tests/unit/ui/ -v`
- [ ] Run baseline tests to confirm all pass before changes
**Notes:**

## Task 1.2: Rename BattleEngine.start() signature and body [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/ -v`
- [ ] Line 12: Update module docstring example `engine.start(team1_ships, team2_ships, seed=12345)` -> `engine.start(team0_ships, team1_ships, seed=12345)` (line 12: `engine.start([ship1, ship2], [enemy1], seed=12345)` -- this uses positional args, verify if rename needed in example)
- [ ] Line 13: Update comment `- Assigns team IDs (0 and 1)` -- verify, may already be correct
- [ ] Line 223: Rename parameter `team1_ships: List['Ship']` -> `team0_ships: List['Ship']`
- [ ] Line 224: Rename parameter `team2_ships: List['Ship']` -> `team1_ships: List['Ship']`
- [ ] Line 234: Update docstring `team1_ships: List of ships for team 0` -> `team0_ships: List of ships for team 0`
- [ ] Line 235: Update docstring `team2_ships: List of ships for team 1` -> `team1_ships: List of ships for team 1`
- [ ] Line 259: `if not isinstance(team1_ships, list): team1_ships = [team1_ships]` -> `if not isinstance(team0_ships, list): team0_ships = [team0_ships]`
- [ ] Line 260: `if not isinstance(team2_ships, list): team2_ships = [team2_ships]` -> `if not isinstance(team1_ships, list): team1_ships = [team1_ships]`
- [ ] Line 263: `for s in team1_ships:` -> `for s in team0_ships:`
- [ ] Line 266: `for s in team2_ships:` -> `for s in team1_ships:`
- [ ] Line 275: `team1_controllers = ...` -> `team0_controllers = ...`
- [ ] Line 276: `team2_controllers = ...` -> `team1_controllers = ...`
- [ ] Line 277: `self.ai_controllers = team1_controllers + team2_controllers` -> `self.ai_controllers = team0_controllers + team1_controllers`
- [ ] Line 304: `f"Battle started: {len(team1_ships)} vs {len(team2_ships)} ships"` -> `f"Battle started: {len(team0_ships)} vs {len(team1_ships)} ships"`
**Notes:** After this task, tests still pass because `tests/fixtures/battle.py` uses positional args.

## Task 1.3: Update BattleService._start_battle() call site [Simple]
**File:** `game/simulation/services/battle_service.py`
**Tests:** `pytest tests/unit/simulation/services/test_battle_service.py -v`
- [ ] Lines 207-209: Change keyword args: `team1_ships=self._team0_ships, team2_ships=self._team1_ships` -> `team0_ships=self._team0_ships, team1_ships=self._team1_ships`
- [ ] Run tests
**Notes:**

## Task 1.4: Update BattleScreen.start() signature and body [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/test_battle_screen_simulation.py -v`
- [ ] Line 226: Rename parameter `team1_ships` -> `team0_ships` and `team2_ships` -> `team1_ships`
- [ ] Line 234-235: Update docstrings
- [ ] Line 260: `for ship in team1_ships:` -> `for ship in team0_ships:`
- [ ] Line 262: `for ship in team2_ships:` -> `for ship in team1_ships:`
- [ ] Run tests
**Notes:**

## Task 1.5: Update create_manual_battle() signature and body [Simple]
**File:** `game/ui/services/battle_factories.py`
**Tests:** `pytest tests/unit/ui/ -v`
- [ ] Lines 81-82: Rename parameters
- [ ] Lines 90-91: Update docstrings
- [ ] Lines 105-106: Update variable references
**Notes:**

## Task 1.6: Update App.start_battle() signature and call [Simple]
**File:** `game/app.py`
**Tests:** Manual verification
- [ ] Line 511: Rename parameters in signature
- [ ] Line 516: Update call to `create_manual_battle()`
**Notes:**

## Task 1.7: Update battle_panels.py local variables [Simple]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** Manual visual verification
- [ ] Lines 121-128: Rename `team1_ships` / `team1_alive` -> `team0_ships` / `team0_alive`
- [ ] Lines 134-141: Rename `team2_ships` / `team2_alive` -> `team1_ships` / `team1_alive`
- [ ] Keep display labels "TEAM 1" / "TEAM 2" unchanged (user-facing)
**Notes:**

## Task 1.8: Update simulation_adapter.py local variables [Simple]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ -v`
- [ ] Lines 84-85: `team1_ships` -> `team0_ships`, `team2_ships` -> `team1_ships`
- [ ] Lines 89-90: Update `_apply_shield_interference()` calls
- [ ] Lines 94, 103, 109, 112, 117: Update conditionals and survivor conversion
- [ ] Lines 141-142: Update `controller.add_ships()` calls
- [ ] Verify log messages on lines 81, 95, 104, 113
**Notes:** `team0_survivors` / `team1_survivors` are BattleResult field names (already correct, out of scope). Only the local variable being passed changes.

## Task 1.9: Update setup_screen.py local variables [Simple]
**File:** `game/ui/screens/setup_screen.py`
**Tests:** Manual verification
- [ ] Lines 100-102: Rename locals and return tuple
**Notes:** `self.team1` and `self.team2` are UI data lists, not being renamed.

## Task 1.10: Run targeted test suite [Simple]
**Tests:** `pytest tests/unit/simulation/ tests/unit/ui/ tests/integration/ -v`
- [ ] All targeted tests pass
- [ ] No regressions in production code
**Notes:**
