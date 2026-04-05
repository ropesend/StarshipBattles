# Phase 2 Checklist: Update Test Fixtures and Verify Full Suite
**Status:** Not Started

## Task 2.1: Update tests/fixtures/battle.py [Simple]
**File:** `tests/fixtures/battle.py`
**Tests:** `pytest tests/unit/simulation/ tests/integration/fleet_combat/ -v`
- [ ] Lines 62-63: `team1_count` -> `team0_count`, `team2_count` -> `team1_count`
- [ ] Lines 74-75: Update docstrings
- [ ] Lines 84-97: Rename team 0 ship creation block (`team1_ships` -> `team0_ships`, `Team1Ship` -> `Team0Ship`)
- [ ] Lines 99-112: Rename team 1 ship creation block (`team2_ships` -> `team1_ships`, `Team2Ship` -> `Team1Ship`)
- [ ] Line 115: `engine.start(team1_ships, team2_ships)` -> `engine.start(team0_ships, team1_ships)`
- [ ] Run `pytest tests/unit/simulation/systems/ -v`
**Notes:** Ship names change from `Team1Ship0` to `Team0Ship0`. Any tests asserting on ship names will need updating.

## Task 2.2: Update test callers [Simple]
**File:** `tests/integration/fleet_combat/test_service_integration.py`
**Tests:** `pytest tests/integration/fleet_combat/ -v`
- [ ] Line 143: `team1_count=2, team2_count=2` -> `team0_count=2, team1_count=2`
- [ ] Lines 146-147: Verify local vars already correct (filter by `team_id`)
**Notes:**

## Task 2.3: Update test docstrings [Simple]
**File:** `tests/unit/ui/test_battle_screen_simulation.py`
**Tests:** `pytest tests/unit/ui/test_battle_screen_simulation.py -v`
- [ ] Line 90: Update docstring `"team1 and team2"` -> `"team0 and team1"`
**Notes:**

## Task 2.4: Search for any remaining occurrences [Simple]
**Tests:** `python scripts/test_sharded.py`
- [ ] `grep -r "team2_ships" game/ tests/` -- must return zero results
- [ ] `grep -rn "team1_ships" game/` -- verify every remaining occurrence maps to `team_id == 1`
- [ ] `grep -rn "team1_count" tests/` -- verify every remaining occurrence maps to team 1
- [ ] `grep -rn "team1.*team 0\|team2.*team 1" game/ tests/` -- must return zero results
- [ ] Run full test suite: `python scripts/test_sharded.py` -- all tests pass
**Notes:**
