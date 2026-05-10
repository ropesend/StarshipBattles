# PROJ-244 Plan-Code Alignment Review

**Date:** 2026-04-10
**Scope:** Verify all code references (file paths, line numbers, class/function names, variable names) in plan.md, phase_1_checklist.md, and phase_2_checklist.md against actual code.

---

## Executive Summary

The rename from `team1_ships`/`team2_ships` to `team0_ships`/`team1_ships` has **already been completed** in the production code. All production files already use the 0-based naming convention. The plan's line number references are significantly stale -- they appear to have been authored before the rename was applied. The test fixtures and test files have also already been updated.

**Bottom line:** Either this project was already completed and not marked as such, or the plan was written against a prior version of the code and the rename was done outside this project. Every single "before" reference in the checklists points to code that already shows the "after" state.

---

## Finding Details

### F-01: BattleEngine.start() -- Already Renamed (Task 1.2)

**Task:** Task 1.2, Rename BattleEngine.start() signature and body
**Plan Reference:** `game/simulation/systems/battle_engine.py` lines 12-13, 223-224, 234-235, 259-260, 263, 266, 275-277, 304
**Plan says:** Parameters are `team1_ships` and `team2_ships`, need renaming to `team0_ships`/`team1_ships`

**Actual Code:**
- Line 12 (module docstring): Already says `engine.start(team0_ships, team1_ships, seed=42)` -- no change needed
- Line 13: Already says `- Assigns team IDs (0 and 1)` -- no change needed
- Line 45 (example): Uses positional args `engine.start([ship1, ship2], [enemy1], seed=12345)` -- no change needed
- Lines 239-240 (was 223-224): Parameters are already `team0_ships: List['Ship']` and `team1_ships: List['Ship']`
- Lines 250-251 (was 234-235): Docstring already says `team0_ships: List of ships for team 0` / `team1_ships: List of ships for team 1`
- Lines 278-279 (was 259-260): Already uses `team0_ships` / `team1_ships`
- Lines 282, 285 (was 263, 266): Already `for s in team0_ships:` / `for s in team1_ships:`
- Lines 294-296 (was 275-277): Already `team0_controllers` / `team1_controllers`
- Line 313 (was 304): Already `f"Battle started: {len(team0_ships)} vs {len(team1_ships)} ships"`

**Impact:** Task 1.2 is already complete. All line numbers have shifted due to prior edits (offsets of ~16-20 lines).

---

### F-02: BattleService._start_battle() -- Already Renamed (Task 1.3)

**Task:** Task 1.3, Update BattleService._start_battle() call site
**Plan Reference:** `game/simulation/services/battle_service.py` lines 207-209
**Plan says:** `engine.start(team1_ships=self._team0_ships, team2_ships=self._team1_ships)` needs renaming

**Actual Code (lines 207-209):**
```python
self._engine.start(
    team0_ships=self._team0_ships,
    team1_ships=self._team1_ships,
```
Already uses 0-based keyword args. Line numbers happen to still match.

**Impact:** Task 1.3 is already complete. Line numbers still accurate.

---

### F-03: BattleScreen.start() -- Already Renamed (Task 1.4)

**Task:** Task 1.4, Update BattleScreen.start() signature and body
**Plan Reference:** `game/ui/screens/battle_screen.py` lines 226, 234-235, 260, 262
**Plan says:** Parameters `team1_ships`/`team2_ships` need renaming

**Actual Code:**
- Line 227 (was 226): `def start(self, team0_ships, team1_ships, seed=None, ...)` -- already renamed
- Lines 235-236 (was 234-235): Docstring already says `team0_ships` / `team1_ships`
- Line 259 (was 260): `team0_ships,` -- already renamed
- Line 260 (was 262): `team1_ships,` -- already renamed

**Impact:** Task 1.4 is already complete. Line numbers shifted by ~1 line.

---

### F-04: battle_factories.py -- Already Renamed (Task 1.5)

**Task:** Task 1.5, Update create_manual_battle() signature and body
**Plan Reference:** `game/ui/services/battle_factories.py` lines 81-82, 90-91, 105-106
**Plan says:** Parameters named `team1_ships`/`team2_ships`

**Actual Code:**
- The function `create_manual_battle` starts at line 101 (not ~80).
- Lines 102-103: Parameters are already `team0_ships` / `team1_ships`
- Lines 111-112: Docstring already says `team0_ships` / `team1_ships`
- Line 125: Already passes `team0_ships, team1_ships`
- Also, `create_started_battle_controller` (lines 53-71) already uses `team0_ships` / `team1_ships`

**Impact:** Task 1.5 is already complete. Line numbers are significantly off (plan says 81-82, actual function starts at line 101).

---

### F-05: App.start_battle() -- Already Renamed (Task 1.6)

**Task:** Task 1.6, Update App.start_battle() signature and call
**Plan Reference:** `game/app.py` lines 511, 516
**Plan says:** Parameters named `team1_ships`/`team2_ships` at line 511

**Actual Code:**
- Line 558: `def start_battle(self, team0_ships, team1_ships, headless=False):` -- already renamed
- Line 563: `controller = create_manual_battle(team0_ships, team1_ships, headless=headless)` -- already renamed

**Impact:** Task 1.6 is already complete. Line numbers shifted significantly (plan says 511/516, actual 558/563 -- ~47 lines off).

---

### F-06: battle_panels.py -- Already Renamed (Task 1.7)

**Task:** Task 1.7, Update battle_panels.py local variables
**Plan Reference:** `game/ui/panels/battle_panels.py` lines 121-128, 134-141
**Plan says:** Local vars `team1_ships`/`team2_ships` need renaming to `team0_ships`/`team1_ships`

**Actual Code:**
- Lines 135-136 (was ~121-128): Already `team0_ships = [s for s in ships if s.team_id == 0]` / `team0_alive = ...`
- Lines 148-149 (was ~134-141): Already `team1_ships = [s for s in ships if s.team_id == 1]` / `team1_alive = ...`

**Impact:** Task 1.7 is already complete. Line numbers shifted by ~14 lines.

---

### F-07: simulation_adapter.py -- Already Renamed (Task 1.8)

**Task:** Task 1.8, Update simulation_adapter.py local variables
**Plan Reference:** `game/strategy/adapters/simulation_adapter.py` lines 81, 84-85, 89-90, 94, 95, 103, 104, 109, 112, 113, 117, 141-142

**Actual Code:**
- Line 84-85: Already `team0_ships = fleet1.battle.to_battle_ships(...)` / `team1_ships = fleet2.battle.to_battle_ships(...)`
- Line 89-90: Already `self._apply_shield_interference(team0_ships, ...)` / `self._apply_shield_interference(team1_ships, ...)`
- Lines 94, 103, 112: Already use `team0_ships` / `team1_ships` in conditionals
- Lines 142-143: Already `controller.add_ships(team0_ships, 0)` / `controller.add_ships(team1_ships, 1)`

**Impact:** Task 1.8 is already complete. Line numbers are approximately correct (within 1-2 lines).

---

### F-08: setup_screen.py -- Already Renamed (Task 1.9)

**Task:** Task 1.9, Update setup_screen.py local variables
**Plan Reference:** `game/ui/screens/setup_screen.py` lines 100-102
**Plan says:** Local vars `team1_ships`/`team2_ships` in get_ships()

**Actual Code (lines 100-104):**
```python
def get_ships(self):
    """Load and return ships for both teams."""
    team0_ships = load_ships_from_entries(self.team1, team_id=0, ...)
    team1_ships = load_ships_from_entries(self.team2, team_id=1, ...)
    return team0_ships, team1_ships
```
Already uses 0-based naming. Line numbers are accurate.

**Impact:** Task 1.9 is already complete.

---

### F-09: tests/fixtures/battle.py -- Already Renamed (Task 2.1)

**Task:** Task 2.1, Update tests/fixtures/battle.py
**Plan Reference:** Lines 62-63, 74-75, 84-97, 99-112, 115
**Plan says:** Parameters `team1_count`/`team2_count`, locals `team1_ships`/`team2_ships`, ship names `Team1Ship`/`Team2Ship`

**Actual Code:**
- Lines 62-63: Already `team0_count: int = 1, team1_count: int = 1`
- Lines 74-76: Docstring already says `team0_count` / `team1_count`
- Lines 85-97: Already `team0_ships = []` with ships named `Team0Ship{i}`
- Lines 100-112: Already `team1_ships = []` with ships named `Team1Ship{i}`
- Line 115: Already `engine.start(team0_ships, team1_ships)`

**Impact:** Task 2.1 is already complete. Line numbers are accurate.

---

### F-10: test_service_integration.py -- Already Renamed (Task 2.2)

**Task:** Task 2.2, Update test_service_integration.py
**Plan Reference:** Lines 143, 146-147
**Plan says:** `team1_count=2, team2_count=2` at line 143; local vars at 146-147

**Actual Code:**
- Line 143: `engine = create_battle_engine_with_ships(team0_count=2, team1_count=2, registries=fresh_registries)` -- already uses 0-based naming
- Lines 146-147: `team0_ships = [s for s in engine.ships if s.team_id == 0]` / `team1_ships = [...]` -- already uses 0-based naming

**Impact:** Task 2.2 is already complete. Line numbers are accurate.

---

### F-11: test_battle_screen_simulation.py -- Already Correct (Task 2.3)

**Task:** Task 2.3, Update test docstring
**Plan Reference:** Line 90, docstring says `"team1 and team2"`

**Actual Code (line 89-90):**
```python
def test_start_assigns_correct_team_ids(self):
    """Test start() assigns team_id 0 to team0 and 1 to team1."""
```
Already uses 0-based naming (`team0` and `team1`). No old "team1 and team2" wording present.

**Impact:** Task 2.3 is already complete.

---

### F-12: Plan Key Files Table -- Class/Function Name Issue

**Plan Reference:** Key Files table row for `battle_panels.py` says `BattleTeamPanel.draw()`
**Actual Code:** There is no class named `BattleTeamPanel` in `battle_panels.py`. The relevant class is `ShipStatsPanel` (line 81), which has a `draw()` method (line 110). The team variable filtering happens inside `ShipStatsPanel.draw()`.

**Impact:** Minor naming error in plan. Would not block implementation since the file path is correct and the developer would find the right location.

---

### F-13: App.start_battle() Caller -- setup_screen Callback Uses Positional Args

**Plan Reference:** `game/app.py` line 782
**Observation:** `_handle_battle_setup_action` calls `self.start_battle(kwargs["team1"], kwargs["team2"])`. The callback from setup_screen passes `team1=team1, team2=team2` kwargs (line 340 of setup_screen.py). These are UI data list references (`self.team1`/`self.team2`), not the renamed ship variables. The plan correctly identifies these as out of scope, but this is a potential confusion point -- the setup_screen still uses `team1`/`team2` as kwargs in the callback, and app.py reads them with `kwargs["team1"]`/`kwargs["team2"]`.

**Impact:** None for this project (correctly out of scope), but worth noting that the callback kwargs `team1`/`team2` represent the raw UI team lists, not the loaded ship objects. The 0-based ship variables are created inside `get_ships()` and passed to the callback.

---

## Summary Table

| Finding | Task | Status | Severity |
|---------|------|--------|----------|
| F-01 | 1.2 BattleEngine.start() | Already complete | Critical (whole task done) |
| F-02 | 1.3 BattleService call site | Already complete | Critical (whole task done) |
| F-03 | 1.4 BattleScreen.start() | Already complete | Critical (whole task done) |
| F-04 | 1.5 create_manual_battle() | Already complete | Critical (whole task done) |
| F-05 | 1.6 App.start_battle() | Already complete | Critical (whole task done) |
| F-06 | 1.7 battle_panels.py | Already complete | Critical (whole task done) |
| F-07 | 1.8 simulation_adapter.py | Already complete | Critical (whole task done) |
| F-08 | 1.9 setup_screen.py | Already complete | Critical (whole task done) |
| F-09 | 2.1 fixtures/battle.py | Already complete | Critical (whole task done) |
| F-10 | 2.2 test_service_integration.py | Already complete | Critical (whole task done) |
| F-11 | 2.3 test docstring | Already complete | Critical (whole task done) |
| F-12 | Plan Key Files table | Wrong class name | Low (file path correct) |
| F-13 | App callback kwargs | Out-of-scope observation | Informational |

---

## Conclusion

**All tasks in PROJ-244 (both Phase 1 and Phase 2) have already been implemented.** Every production file and test file already uses the 0-based `team0_ships`/`team1_ships` naming convention. The project plan references the old code state and should be marked as complete.

### Recommended Actions

1. **Mark PROJ-244 as COMPLETE** -- all rename work is done.
2. **Run verification step from Task 2.4:** `grep -r "team2_ships" game/ tests/` to confirm zero remaining occurrences. This is the only unchecked task.
3. **Run full test suite** to confirm no regressions: `python Tools/test_sharded/test_sharded.py`
4. **Archive the project** once verification passes.
