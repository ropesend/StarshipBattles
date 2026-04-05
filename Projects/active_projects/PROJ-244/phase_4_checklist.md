# Phase 4 Checklist: Update Test Fixtures and Verify Full Suite
**Status:** Not Started

## Task 4.1: Update tests/fixtures/battle.py [Simple]
**File:** `tests/fixtures/battle.py`
**Tests:** `pytest tests/unit/simulation/ tests/integration/fleet_combat/ -v`
- [ ] Line 62: `team1_count: int = 1,` -> `team0_count: int = 1,`
- [ ] Line 63: `team2_count: int = 1,` -> `team1_count: int = 1,`
- [ ] Line 74: Docstring `team1_count: Number of ships for team 0` -> `team0_count: Number of ships for team 0`
- [ ] Line 75: Docstring `team2_count: Number of ships for team 0` -> `team1_count: Number of ships for team 1`
- [ ] Line 84: Comment `# Create team 1 ships (left side)` -> `# Create team 0 ships (left side)`
- [ ] Line 85: `team1_ships = []` -> `team0_ships = []`
- [ ] Line 86: `for i in range(team1_count):` -> `for i in range(team0_count):`
- [ ] Line 88: `name=f"Team1Ship{i}",` -> `name=f"Team0Ship{i}",`
- [ ] Line 97: `team1_ships.append(ship)` -> `team0_ships.append(ship)`
- [ ] Line 99: Comment `# Create team 2 ships (right side)` -> `# Create team 1 ships (right side)`
- [ ] Line 100: `team2_ships = []` -> `team1_ships = []`
- [ ] Line 101: `for i in range(team2_count):` -> `for i in range(team1_count):`
- [ ] Line 103: `name=f"Team2Ship{i}",` -> `name=f"Team1Ship{i}",`
- [ ] Line 112: `team2_ships.append(ship)` -> `team1_ships.append(ship)`
- [ ] Line 115: `engine.start(team1_ships, team2_ships)` -> `engine.start(team0_ships, team1_ships)`
- [ ] Run `pytest tests/unit/simulation/systems/ -v`
**Notes:** Ship names change from `Team1Ship0` to `Team0Ship0` etc. Any tests asserting on ship names will need updating.

## Task 4.2: Update test callers of create_battle_engine_with_ships() [Simple]
**File:** `tests/integration/fleet_combat/test_service_integration.py`
**Tests:** `pytest tests/integration/fleet_combat/ -v`
- [ ] Line 143: `engine = create_battle_engine_with_ships(team1_count=2, team2_count=2, registries=fresh_registries)` -> `engine = create_battle_engine_with_ships(team0_count=2, team1_count=2, registries=fresh_registries)`
- [ ] Lines 146-147: local variable names `team0_ships` / `team1_ships` -- already correct (filtering by `team_id`), verify no changes needed
**Notes:**

## Task 4.3: Update test docstrings [Simple]
**File:** `tests/unit/ui/test_battle_screen_simulation.py`
**Tests:** `pytest tests/unit/ui/test_battle_screen_simulation.py -v`
- [ ] Line 90: Update docstring `"Test start() assigns team_id 0 to team1 and 1 to team2."` -> `"Test start() assigns team_id 0 to team0 and 1 to team1."`
**Notes:** The test body uses `team0_ships` and `team1_ships` local vars that already filter correctly by `team_id` -- no changes needed there.

## Task 4.4: Search for any remaining occurrences [Simple]
**Tests:** `python scripts/test_sharded.py`
- [ ] `grep -r "team2_ships" game/ tests/` -- must return zero results
- [ ] `grep -rn "team1_ships" game/` -- verify every remaining occurrence maps to `team_id == 1` (not `team_id == 0`)
- [ ] `grep -rn "team1_count" tests/` -- verify every remaining occurrence maps to team 1 (not team 0)
- [ ] Search for stale docstrings: `grep -rn "team1.*team 0\|team2.*team 1" game/ tests/` -- must return zero results
- [ ] Run full test suite: `python scripts/test_sharded.py` -- all tests pass
