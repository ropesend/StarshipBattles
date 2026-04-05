# Phase 1 Checklist: Rename BattleEngine.start() Parameters + Docstrings
**Status:** Not Started

## Task 1.1: Establish baseline [Simple]
**Tests:** `pytest tests/unit/simulation/systems/ tests/unit/simulation/services/ -v`
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
- [ ] Line 275: `team1_controllers = self._ai_factory.create_for_ships(team1_ships, enemy_team_id=1)` -> `team0_controllers = self._ai_factory.create_for_ships(team0_ships, enemy_team_id=1)`
- [ ] Line 276: `team2_controllers = self._ai_factory.create_for_ships(team2_ships, enemy_team_id=0)` -> `team1_controllers = self._ai_factory.create_for_ships(team1_ships, enemy_team_id=0)`
- [ ] Line 277: `self.ai_controllers = team1_controllers + team2_controllers` -> `self.ai_controllers = team0_controllers + team1_controllers`
- [ ] Line 304: `f"Battle started: {len(team1_ships)} vs {len(team2_ships)} ships"` -> `f"Battle started: {len(team0_ships)} vs {len(team1_ships)} ships"`
- [ ] Run `pytest tests/unit/simulation/systems/ -v` -- expect failures from test fixture calling with old positional args (will fix in Phase 4)
**Notes:** After this task, `tests/fixtures/battle.py:115` (`engine.start(team1_ships, team2_ships)`) still uses positional args so will still work, but local var names are misleading until Phase 4.
