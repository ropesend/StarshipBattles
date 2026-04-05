# PROJ-244: Team Naming Standardization

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-244` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-244 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Rename BattleEngine.start() parameters + docstrings | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Rename all call sites (service, screen, app, factories) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Rename local variables (panels, adapter, setup screen) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Update test fixtures and verify full suite | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-05
**Active Phase:** Planning
**Last Action:** Plan rewritten with full protocol compliance and swarm findings
**Next Action:** Begin Phase 1 — rename BattleEngine.start() parameters
**Blockers:** None
**Context for Next Agent:** Pure mechanical rename. Every change is `team1_ships` -> `team0_ships` and `team2_ships` -> `team1_ships`. No behavioral changes. Rename must be done in dependency order: engine first, then callers, then local variables, then tests.

## Overview
The battle simulator uses inconsistent 0-based and 1-based team naming. `BattleService` internally stores `_team0_ships` and `_team1_ships` (0-indexed, correct), but passes them to `BattleEngine.start(team1_ships=..., team2_ships=...)` where `team1_ships` receives team 0 and `team2_ships` receives team 1. This naming mismatch propagates through factories, screens, and test fixtures. The project standardizes all parameter names, local variables, and docstrings to use 0-based naming (`team0_ships`, `team1_ships`) throughout.

## Goals
- Eliminate the confusing `team1_ships` / `team2_ships` naming where the numbers don't match `team_id`
- Standardize on 0-based naming (`team0_ships`, `team1_ships`) matching the actual `team_id` values (0 and 1)
- Update all docstrings to remove the "team1 = team 0" clarifications that exist to explain the mismatch
- No runtime behavior changes -- purely a rename refactor

## Scope
**In Scope:**
- `BattleEngine.start()` parameter names, docstring, and internal references
- `BattleScreen.start()` parameter names, docstring, and internal references
- `BattleService._start_battle()` call site keyword arguments
- `create_manual_battle()` factory parameter names and docstring
- `App.start_battle()` parameter names and call to factory
- `SimulationAdapter.simulate_battle()` local variables
- `setup_screen.py` local variables and return tuple
- `battle_panels.py` local variables
- Test fixtures (`tests/fixtures/battle.py`) function signature, docstring, local variables
- Test file docstrings referencing old naming
- Module docstring example in `battle_engine.py`

**Out of Scope:**
- `BattleResult.team0_survivors` / `team1_survivors` -- already uses correct 0-based naming
- `BattleService._team0_ships` / `_team1_ships` -- already uses correct 0-based naming
- `battle_results_screen.py` -- already uses correct 0-based naming
- `battle_orchestrator.py` -- already uses correct 0-based naming
- Display labels ("TEAM 1" / "TEAM 2" in UI panels) -- user-facing 1-based display labels
- Any `team_id` integer values -- these stay as 0 and 1
- All `simulation_tests/` scenarios -- use `add_ships(team_id=)` pattern, no old naming
- `BattleService` test file internal attribute access (`service._team1_ships`) -- already correct 0-based

## Key Files Reference
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| BattleEngine | `game/simulation/systems/battle_engine.py` | `BattleEngine.start()` |
| BattleService | `game/simulation/services/battle_service.py` | `BattleService._start_battle()` |
| BattleScreen | `game/ui/screens/battle_screen.py` | `BattleScreen.start()` |
| Battle factories | `game/ui/services/battle_factories.py` | `create_manual_battle()` |
| App entry point | `game/app.py` | `App.start_battle()` |
| SimulationAdapter | `game/strategy/adapters/simulation_adapter.py` | `SimulationAdapter.simulate_battle()` |
| Setup screen | `game/ui/screens/setup_screen.py` | `SetupScreen.get_ships()` |
| Battle panels | `game/ui/panels/battle_panels.py` | `BattleTeamPanel.draw()` |
| Test fixtures | `tests/fixtures/battle.py` | `create_battle_engine_with_ships()` |
| Battle screen tests | `tests/unit/ui/test_battle_screen_simulation.py` | docstring on line 90 |
| Integration tests | `tests/integration/fleet_combat/test_service_integration.py` | local variables lines 146-147 |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | Standardize on 0-based (`team0_ships`, `team1_ships`) | Matches the actual `team_id` values (0, 1). Eliminates the off-by-one confusion where `team1_ships` has `team_id=0`. |
| 2026-04-05 | Keep UI display labels as "TEAM 1" / "TEAM 2" | Display labels are user-facing and 1-based is natural for users. Only code identifiers change. |
| 2026-04-05 | Phase by dependency layer (engine -> callers -> locals -> tests) | Engine first so callers can be updated against the new API. Tests last since they follow the public API. |
| 2026-04-05 | battle_panels.py local vars stay as `team0_ships`/`team1_ships` | Even though display says "TEAM 1", the variable filtering `team_id == 0` should be `team0_ships` for code clarity. |

## Initial Analysis

### Affected Code (80+ occurrences across 12 files)

**Function signatures (4 functions):**
1. `battle_engine.py:221-224` -- `start(team1_ships, team2_ships)`
2. `battle_screen.py:226` -- `start(team1_ships, team2_ships, ...)`
3. `app.py:511` -- `start_battle(team1_ships, team2_ships, ...)`
4. `battle_factories.py:80-82` -- `create_manual_battle(team1_ships, team2_ships, ...)`

**Call sites (1 keyword call):**
1. `battle_service.py:207-209` -- `engine.start(team1_ships=self._team0_ships, team2_ships=self._team1_ships)`

**Local variables (3 files):**
1. `battle_panels.py:121,134` -- `team1_ships = [s for s in ships if s.team_id == 0]`
2. `simulation_adapter.py:84-85,89-90,94,103,109,112,117,141-142` -- fleet conversion locals
3. `setup_screen.py:100-102` -- `team1_ships, team2_ships` load and return

**Test fixtures (1 file):**
1. `tests/fixtures/battle.py:62-63,74-75,85-86,97,100,112,115` -- function params, docstring, locals

**Tests to verify (docstring/local updates only):**
1. `tests/unit/ui/test_battle_screen_simulation.py:90` -- docstring says "team1" / "team2"
2. `tests/integration/fleet_combat/test_service_integration.py:143,146-147` -- param + local var names

### Already Correct (NO changes needed)
- `BattleService._team0_ships` / `_team1_ships` (internal attributes, already 0-based)
- `battle_orchestrator.py` (already 0-based)
- `battle_results_screen.py` (already 0-based)
- ALL `simulation_tests/` scenarios (use `add_ships(team_id=)` pattern)
- `test_battle_service.py` references to `service._team1_ships` (internal attribute, correct)

### Risk Assessment
- **Low risk:** Pure rename, no behavioral changes
- **Mechanical:** Every change is `team1_ships` -> `team0_ships`, `team2_ships` -> `team1_ships`
- **Test coverage:** Battle service and battle screen have dedicated test files
- **Simulation tests:** `simulation_tests/` does NOT use these parameter names

---

## Phases

### Phase 1: Rename BattleEngine.start() Parameters + Docstrings [Simple]
**Objective:** Rename the core API that everything else calls
**Status:** Not Started

#### Task 1.1: Establish baseline [Simple]
**Tests:** `pytest tests/unit/simulation/systems/ tests/unit/simulation/services/ -v`
- [ ] Run baseline tests to confirm all pass before changes
**Notes:**

#### Task 1.2: Rename BattleEngine.start() signature and body [Simple]
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

---

### Phase 2: Rename All Call Sites [Simple]
**Objective:** Update all code that calls BattleEngine.start(), BattleScreen.start(), create_manual_battle(), or App.start_battle()
**Status:** Not Started

#### Task 2.1: Update BattleService._start_battle() call site [Simple]
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

#### Task 2.2: Update BattleScreen.start() signature and body [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/test_battle_screen_simulation.py -v`
- [ ] Line 226: Rename parameter `team1_ships` -> `team0_ships` and `team2_ships` -> `team1_ships` in signature
- [ ] Line 234: Update docstring `team1_ships: List of ships for team 0` -> `team0_ships: List of ships for team 0`
- [ ] Line 235: Update docstring `team2_ships: List of ships for team 1` -> `team1_ships: List of ships for team 1`
- [ ] Line 260: `for ship in team1_ships:` -> `for ship in team0_ships:`
- [ ] Line 262: `for ship in team2_ships:` -> `for ship in team1_ships:`
- [ ] Run `pytest tests/unit/ui/test_battle_screen_simulation.py -v`
**Notes:** BattleScreen.start() is called with positional args from test, so rename is safe.

#### Task 2.3: Update create_manual_battle() signature and body [Simple]
**File:** `game/ui/services/battle_factories.py`
**Tests:** `pytest tests/unit/ui/ -v`
- [ ] Line 81: `team1_ships: List['Ship']` -> `team0_ships: List['Ship']`
- [ ] Line 82: `team2_ships: List['Ship']` -> `team1_ships: List['Ship']`
- [ ] Line 90: Update docstring `team1_ships: Ships for team 0` -> `team0_ships: Ships for team 0`
- [ ] Line 91: Update docstring `team2_ships: Ships for team 1` -> `team1_ships: Ships for team 1`
- [ ] Line 105: `controller.add_ships(team1_ships, 0)` -> `controller.add_ships(team0_ships, 0)`
- [ ] Line 106: `controller.add_ships(team2_ships, 1)` -> `controller.add_ships(team1_ships, 1)`
**Notes:**

#### Task 2.4: Update App.start_battle() signature and call [Simple]
**File:** `game/app.py`
**Tests:** Manual verification (App is top-level entry point)
- [ ] Line 511: `def start_battle(self, team1_ships, team2_ships, headless=False):` -> `def start_battle(self, team0_ships, team1_ships, headless=False):`
- [ ] Line 516: `controller = create_manual_battle(team1_ships, team2_ships, headless=headless)` -> `controller = create_manual_battle(team0_ships, team1_ships, headless=headless)`
**Notes:** Check all callers of `App.start_battle()` -- should be called from setup_screen with positional args.

---

### Phase 3: Rename Local Variables [Simple]
**Objective:** Update local variable names in files that create/filter ships into misleadingly named team variables
**Status:** Not Started

#### Task 3.1: Update battle_panels.py local variables [Simple]
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

#### Task 3.2: Update simulation_adapter.py local variables [Simple]
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

#### Task 3.3: Update setup_screen.py local variables [Simple]
**File:** `game/ui/screens/setup_screen.py`
**Tests:** Manual verification (UI screen)
- [ ] Line 100: `team1_ships = load_ships_from_entries(self.team1, team_id=0, ...)` -> `team0_ships = load_ships_from_entries(self.team1, team_id=0, ...)`
- [ ] Line 101: `team2_ships = load_ships_from_entries(self.team2, team_id=1, ...)` -> `team1_ships = load_ships_from_entries(self.team2, team_id=1, ...)`
- [ ] Line 102: `return team1_ships, team2_ships` -> `return team0_ships, team1_ships`
**Notes:** `self.team1` and `self.team2` are UI data lists (team setup entries), not being renamed (display-facing). Only the local ship list variables change.

---

### Phase 4: Update Test Fixtures and Verify Full Suite [Simple]
**Objective:** Update test helper functions and verify everything passes
**Status:** Not Started

#### Task 4.1: Update tests/fixtures/battle.py [Simple]
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

#### Task 4.2: Update test callers of create_battle_engine_with_ships() [Simple]
**File:** `tests/integration/fleet_combat/test_service_integration.py`
**Tests:** `pytest tests/integration/fleet_combat/ -v`
- [ ] Line 143: `engine = create_battle_engine_with_ships(team1_count=2, team2_count=2, registries=fresh_registries)` -> `engine = create_battle_engine_with_ships(team0_count=2, team1_count=2, registries=fresh_registries)`
- [ ] Lines 146-147: local variable names `team0_ships` / `team1_ships` -- already correct (filtering by `team_id`), verify no changes needed
**Notes:**

#### Task 4.3: Update test docstrings [Simple]
**File:** `tests/unit/ui/test_battle_screen_simulation.py`
**Tests:** `pytest tests/unit/ui/test_battle_screen_simulation.py -v`
- [ ] Line 90: Update docstring `"Test start() assigns team_id 0 to team1 and 1 to team2."` -> `"Test start() assigns team_id 0 to team0 and 1 to team1."`
**Notes:** The test body uses `team0_ships` and `team1_ships` local vars that already filter correctly by `team_id` -- no changes needed there.

#### Task 4.4: Search for any remaining occurrences [Simple]
**Tests:** `python scripts/test_sharded.py`
- [ ] `grep -r "team2_ships" game/ tests/` -- must return zero results
- [ ] `grep -rn "team1_ships" game/` -- verify every remaining occurrence maps to `team_id == 1` (not `team_id == 0`)
- [ ] `grep -rn "team1_count" tests/` -- verify every remaining occurrence maps to team 1 (not team 0)
- [ ] Search for stale docstrings: `grep -rn "team1.*team 0\|team2.*team 1" game/ tests/` -- must return zero results
- [ ] Run full test suite: `python scripts/test_sharded.py` -- all tests pass

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Run full test suite: `python scripts/test_sharded.py` -- establish baseline

### After Each Phase
- [ ] Run targeted tests for affected files
- [ ] No behavioral changes -- only names changed

### Final Verification
- [ ] `python scripts/test_sharded.py` -- all tests pass
- [ ] `grep -r "team2_ships" game/ tests/` returns zero results
- [ ] All `team1_ships` references now correctly map to `team_id == 1` (not `team_id == 0`)
- [ ] Docstrings are clean -- no "team1 means team 0" disclaimers remain
- [ ] No documentation updates needed (this is an internal naming change, not an architecture change)

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified

---

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest for parallel execution
