# Phase 2 Checklist: Update Test Fixtures, Remaining Files, and Verify Full Suite
**Status:** Complete

## Task 2.1: Update tests/fixtures/battle.py [Simple]
**File:** `tests/fixtures/battle.py`
**Tests:** `pytest tests/unit/simulation/ tests/integration/fleet_combat/ -v`
- [x] Lines 62-63: `team0_count` / `team1_count`
- [x] Lines 74-76: Updated docstrings
- [x] Lines 85-97: Renamed team 0 ship creation block (`team0_ships`, `Team0Ship`)
- [x] Lines 100-112: Renamed team 1 ship creation block (`team1_ships`, `Team1Ship`)
- [x] Line 115: `engine.start(team0_ships, team1_ships)`
- [x] Run `pytest tests/unit/simulation/systems/ -v`
**Notes:** Completed in commit abacb998 on 2026-04-05.

## Task 2.2: Update test callers [Simple]
**File:** `tests/integration/fleet_combat/test_service_integration.py`
**Tests:** `pytest tests/integration/fleet_combat/ -v`
- [x] Line 143: `team0_count=2, team1_count=2`
- [x] Lines 146-147: Already correct (filter by `team_id`)
**Notes:** Completed in commit abacb998 on 2026-04-05.

## Task 2.3: Update test docstrings [Simple]
**File:** `tests/unit/ui/test_battle_screen_simulation.py`
**Tests:** `pytest tests/unit/ui/test_battle_screen_simulation.py -v`
- [x] Line 90: Docstring now says `"team0 and team1"`
**Notes:** Completed in commit abacb998 on 2026-04-05.

## Task 2.4: Rename test_battle_determinism.py [Simple] (Added 2026-04-10)
**File:** `tests/integration/fleet_combat/test_battle_determinism.py`
**Tests:** `pytest tests/integration/fleet_combat/test_battle_determinism.py -v`
- [x] Line 16: Rename `_run_battle(team1_ships, team2_ships, ...)` -> `_run_battle(team0_ships, team1_ships, ...)`
- [x] Line 20: Rename `engine.start(team1_ships, team2_ships, ...)` -> `engine.start(team0_ships, team1_ships, ...)`
- [x] Lines 35-57: Rename `team1`/`team2` locals in `_make_teams()` -> `team0`/`team1`
- [x] Line 57: `return team0, team1`
- [x] Update all unpacking sites that receive `_make_teams()` results (`t1a,t2a`->`t0a,t1a`, `t1b,t2b`->`t0b,t1b`)
**Notes:** All 4 tests pass after rename. Pure variable rename, no behavioral changes.

## Task 2.5: Update setup_screen.py → app.py kwargs chain [Simple] (Added 2026-04-10)
**File:** `game/ui/screens/setup_screen.py`, `game/app.py`
**Tests:** Manual verification (UI callback chain)
- [x] `setup_screen.py:338-340`: Renamed `team0, team1 = self.get_ships()` and kwargs `team0=team0, team1=team1`
- [x] `setup_screen.py:72-73`: Updated docstring kwargs references to `team0, team1`
- [x] `app.py:782-788`: Renamed `kwargs["team0"]`/`kwargs["team1"]` and local vars `team0`/`team1`
- [x] Log messages kept as "Team 1"/"Team 2" (user-facing display labels)
**Notes:** Both sender (setup_screen) and receiver (app) updated together. No tests to run — UI callback chain verified by reading code.

## Task 2.6: Rename battle_factories.py ships1/ships2 and fleet1/fleet2 [Simple] (Added 2026-04-10)
**File:** `game/ui/services/battle_factories.py`
**Tests:** `pytest tests/unit/ui/ -v`
- [x] Lines 155-156: Renamed `fleet0`/`fleet1` in `create_strategy_battle()` signature
- [x] Lines 164-165: Updated docstrings
- [x] Lines 183-184: Renamed `ships0`/`ships1` in `create_hypothetical_battle()` signature
- [x] Lines 193-194: Updated docstrings
- [x] Lines 209-210: Updated body references
- [x] Updated test callers in `test_battle_factories.py` (mock_fleet0/1, mock_ship0/1)
**Notes:** No production callers — only test file. 18/18 tests pass after rename.

## Task 2.7: Update documentation [Simple] (Added 2026-04-10)
**File:** `docs/systems/combat_simulation.md`, `tests/fixtures/README.md`
**Tests:** N/A
- [x] `docs/systems/combat_simulation.md:32-33`: Updated to `controller.add_ships(team0_ships, team_id=0)` / `controller.add_ships(team1_ships, team_id=1)`
- [x] `tests/fixtures/README.md:152`: Updated to `team0_count=3, team1_count=2`
**Notes:** Both doc code examples now use 0-based naming.

## Task 2.8: Search for any remaining occurrences + full test suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`
- [x] `grep -r "team2_ships" game/ tests/` -- zero results
- [x] `grep -rn "team1_ships" game/` -- all occurrences correctly map to `team_id == 1`
- [x] `grep -rn "team1_count" tests/` -- all occurrences correctly map to team 1
- [x] `grep -r "ships2\b" game/ui/services/battle_factories.py` -- zero results
- [x] `grep -r "fleet2\b" game/ui/services/battle_factories.py` -- zero results
- [x] `grep -rn "team1.*team 0\|team2.*team 1" game/ tests/` -- zero results
- [x] Run full test suite: 14181 tests passed, 0 failed
**Notes:** All verification checks pass. Full suite clean.
