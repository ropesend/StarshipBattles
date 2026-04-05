# Phase 2 Checklist: Rename All Call Sites
**Status:** Not Started

## Task 2.1: Update BattleService._start_battle() call site [Simple]
**File:** `game/simulation/services/battle_service.py`
**Tests:** `pytest tests/unit/simulation/services/test_battle_service.py -v`
- [ ] Lines 207-209: Change keyword args in `self._engine.start()` call:
  ```python
  # Old:
  self._engine.start(
      team1_ships=self._team0_ships,
      team2_ships=self._team1_ships,
  # New:
  self._engine.start(
      team0_ships=self._team0_ships,
      team1_ships=self._team1_ships,
  ```
- [ ] Run `pytest tests/unit/simulation/services/test_battle_service.py -v`
**Notes:**

## Task 2.2: Update BattleScreen.start() signature and body [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/test_battle_screen_simulation.py -v`
- [ ] Line 226: Rename parameter `team1_ships` -> `team0_ships` and `team2_ships` -> `team1_ships` in signature
- [ ] Line 234: Update docstring `team1_ships: List of ships for team 0` -> `team0_ships: List of ships for team 0`
- [ ] Line 235: Update docstring `team2_ships: List of ships for team 1` -> `team1_ships: List of ships for team 1`
- [ ] Line 260: `for ship in team1_ships:` -> `for ship in team0_ships:`
- [ ] Line 262: `for ship in team2_ships:` -> `for ship in team1_ships:`
- [ ] Run `pytest tests/unit/ui/test_battle_screen_simulation.py -v`
**Notes:** BattleScreen.start() is called with positional args from test, so rename is safe.

## Task 2.3: Update create_manual_battle() signature and body [Simple]
**File:** `game/ui/services/battle_factories.py`
**Tests:** `pytest tests/unit/ui/ -v`
- [ ] Line 81: `team1_ships: List['Ship']` -> `team0_ships: List['Ship']`
- [ ] Line 82: `team2_ships: List['Ship']` -> `team1_ships: List['Ship']`
- [ ] Line 90: Update docstring `team1_ships: Ships for team 0` -> `team0_ships: Ships for team 0`
- [ ] Line 91: Update docstring `team2_ships: Ships for team 1` -> `team1_ships: Ships for team 1`
- [ ] Line 105: `controller.add_ships(team1_ships, 0)` -> `controller.add_ships(team0_ships, 0)`
- [ ] Line 106: `controller.add_ships(team2_ships, 1)` -> `controller.add_ships(team1_ships, 1)`
**Notes:**

## Task 2.4: Update App.start_battle() signature and call [Simple]
**File:** `game/app.py`
**Tests:** Manual verification (App is top-level entry point)
- [ ] Line 511: `def start_battle(self, team1_ships, team2_ships, headless=False):` -> `def start_battle(self, team0_ships, team1_ships, headless=False):`
- [ ] Line 516: `controller = create_manual_battle(team1_ships, team2_ships, headless=headless)` -> `controller = create_manual_battle(team0_ships, team1_ships, headless=headless)`
**Notes:** Check all callers of `App.start_battle()` -- should be called from setup_screen with positional args.
