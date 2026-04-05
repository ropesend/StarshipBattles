# Phase 3 Checklist: Rename Local Variables
**Status:** Not Started

## Task 3.1: Update battle_panels.py local variables [Simple]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** Manual visual verification (UI rendering)
- [ ] Line 121: `team1_ships = [s for s in ships if s.team_id == 0]` -> `team0_ships = [s for s in ships if s.team_id == 0]`
- [ ] Line 122: `team1_alive = sum(1 for s in team1_ships if s.is_alive and not s.is_derelict)` -> `team0_alive = sum(1 for s in team0_ships if s.is_alive and not s.is_derelict)`
- [ ] Line 124: `f"TEAM 1 ({team1_alive}/{len(team1_ships)})"` -> `f"TEAM 1 ({team0_alive}/{len(team0_ships)})"` (keep "TEAM 1" display label)
- [ ] Line 128: `for ship in team1_ships:` -> `for ship in team0_ships:`
- [ ] Line 134: `team2_ships = [s for s in ships if s.team_id == 1]` -> `team1_ships = [s for s in ships if s.team_id == 1]`
- [ ] Line 135: `team2_alive = sum(1 for s in team2_ships if s.is_alive and not s.is_derelict)` -> `team1_alive = sum(1 for s in team1_ships if s.is_alive and not s.is_derelict)`
- [ ] Line 137: `f"TEAM 2 ({team2_alive}/{len(team2_ships)})"` -> `f"TEAM 2 ({team1_alive}/{len(team1_ships)})"` (keep "TEAM 2" display label)
- [ ] Line 141: `for ship in team2_ships:` -> `for ship in team1_ships:`
**Notes:** Display labels "TEAM 1" and "TEAM 2" stay as-is (user-facing, 1-based).

## Task 3.2: Update simulation_adapter.py local variables [Simple]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ -v`
- [ ] Line 84: `team1_ships = fleet1.battle.to_battle_ships(team_id=0, registries=registries)` -> `team0_ships = fleet1.battle.to_battle_ships(team_id=0, registries=registries)`
- [ ] Line 85: `team2_ships = fleet2.battle.to_battle_ships(team_id=1, registries=registries)` -> `team1_ships = fleet2.battle.to_battle_ships(team_id=1, registries=registries)`
- [ ] Line 89: `self._apply_shield_interference(team1_ships, ...)` -> `self._apply_shield_interference(team0_ships, ...)`
- [ ] Line 90: `self._apply_shield_interference(team2_ships, ...)` -> `self._apply_shield_interference(team1_ships, ...)`
- [ ] Line 94: `if not team1_ships and not team2_ships:` -> `if not team0_ships and not team1_ships:`
- [ ] Line 103: `if not team1_ships:` -> `if not team0_ships:`
- [ ] Line 109: `team1_survivors=self._convert_ships_to_survivors(team2_ships)` -> `team1_survivors=self._convert_ships_to_survivors(team1_ships)`
- [ ] Line 112: `if not team2_ships:` -> `if not team1_ships:`
- [ ] Line 117: `team0_survivors=self._convert_ships_to_survivors(team1_ships),` -> `team0_survivors=self._convert_ships_to_survivors(team0_ships),`
- [ ] Line 141: `controller.add_ships(team1_ships, 0)` -> `controller.add_ships(team0_ships, 0)`
- [ ] Line 142: `controller.add_ships(team2_ships, 1)` -> `controller.add_ships(team1_ships, 1)`
- [ ] Update log messages on lines 81, 95, 104, 113 if they reference "Fleet 1"/"Fleet 2" (verify -- these may use fleet IDs, not team vars)
**Notes:** Be careful with line 109 and 117 -- the `team1_survivors` and `team0_survivors` are BattleResult field names (already 0-based, out of scope). Only the variable being passed changes.

## Task 3.3: Update setup_screen.py local variables [Simple]
**File:** `game/ui/screens/setup_screen.py`
**Tests:** Manual verification (UI screen)
- [ ] Line 100: `team1_ships = load_ships_from_entries(self.team1, team_id=0, ...)` -> `team0_ships = load_ships_from_entries(self.team1, team_id=0, ...)`
- [ ] Line 101: `team2_ships = load_ships_from_entries(self.team2, team_id=1, ...)` -> `team1_ships = load_ships_from_entries(self.team2, team_id=1, ...)`
- [ ] Line 102: `return team1_ships, team2_ships` -> `return team0_ships, team1_ships`
**Notes:** `self.team1` and `self.team2` are UI data lists (team setup entries), not being renamed (display-facing). Only the local ship list variables change.
