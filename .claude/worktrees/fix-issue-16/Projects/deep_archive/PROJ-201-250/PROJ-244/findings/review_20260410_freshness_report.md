# PROJ-244 Task Freshness Analysis
**Date:** 2026-04-10
**Analyst:** Claude Code (automated review)
**Scope:** All Phase 1 and Phase 2 checklist tasks

---

## Executive Summary

**ALL Phase 1 tasks (1.2-1.9) and most Phase 2 tasks are ALREADY_DONE.** The codebase already uses `team0_ships`/`team1_ships` naming throughout all production code. The rename described in the project plan has already been applied -- either by a prior session, a hotfix, or an unrecorded change. Only minor residual occurrences remain in test files and documentation that fall outside the original checklist scope.

---

## Phase 1 Findings

### F-01: BattleEngine.start() already renamed
**Task:** 1.2
**Status:** ALREADY_DONE
**Evidence:** `game/simulation/systems/battle_engine.py` lines 237-240 already read:
```python
def start(
    self,
    team0_ships: List['Ship'],
    team1_ships: List['Ship'],
```
The module docstring (line 12) already uses `engine.start(team0_ships, team1_ships, seed=42)`. All body references use `team0_ships`/`team1_ships`. Local controller variables are `team0_controllers`/`team1_controllers` (lines 294-296). Log message on line 313 already uses `team0_ships`/`team1_ships`.
**Impact:** High -- this is the foundational change; all downstream tasks depend on it.
**Proposed Resolution:** Mark Task 1.2 as complete.

### F-02: BattleService already uses correct naming
**Task:** 1.3
**Status:** ALREADY_DONE
**Evidence:** `game/simulation/services/battle_service.py` lines 50-51 use `_team0_ships`/`_team1_ships`. Lines 207-209 pass keyword args `team0_ships=self._team0_ships, team1_ships=self._team1_ships` to `engine.start()`. All other internal references are consistent.
**Impact:** High
**Proposed Resolution:** Mark Task 1.3 as complete.

### F-03: BattleScreen.start() already renamed
**Task:** 1.4
**Status:** ALREADY_DONE
**Evidence:** `game/ui/screens/battle_screen.py` line 227 reads:
```python
def start(self, team0_ships, team1_ships, seed=None, headless=False, ...):
```
Docstrings (lines 235-236) correctly say `team0_ships`/`team1_ships`. Body uses `team0_ships`/`team1_ships` (line 260).
**Impact:** High
**Proposed Resolution:** Mark Task 1.4 as complete.

### F-04: battle_factories.py already renamed
**Task:** 1.5
**Status:** ALREADY_DONE
**Evidence:** `game/ui/services/battle_factories.py` lines 54-56 already use `team0_ships`/`team1_ships` in `create_started_battle_controller()`. Lines 102-103 use `team0_ships`/`team1_ships` in `create_manual_battle()`. All docstrings are consistent.
**Impact:** Medium
**Proposed Resolution:** Mark Task 1.5 as complete.

### F-05: App.start_battle() already renamed
**Task:** 1.6
**Status:** ALREADY_DONE
**Evidence:** `game/app.py` line 558 reads:
```python
def start_battle(self, team0_ships, team1_ships, headless=False):
```
Line 563 calls `create_manual_battle(team0_ships, team1_ships, headless=headless)`.
**Impact:** Medium
**Proposed Resolution:** Mark Task 1.6 as complete.

### F-06: battle_panels.py local vars already renamed
**Task:** 1.7
**Status:** ALREADY_DONE
**Evidence:** `game/ui/panels/battle_panels.py` lines 135-138 use `team0_ships`/`team0_alive`. Lines 148-151 use `team1_ships`/`team1_alive`. Display labels remain "TEAM 1"/"TEAM 2" (user-facing, unchanged as specified).
**Impact:** Low
**Proposed Resolution:** Mark Task 1.7 as complete.

### F-07: simulation_adapter.py local vars already renamed
**Task:** 1.8
**Status:** ALREADY_DONE
**Evidence:** `game/strategy/adapters/simulation_adapter.py` lines 84-85 use `team0_ships`/`team1_ships`. All conditional checks, `_apply_shield_interference()` calls, and `controller.add_ships()` calls on lines 89-143 use the correct naming.
**Impact:** Medium
**Proposed Resolution:** Mark Task 1.8 as complete.

### F-08: setup_screen.py local vars already renamed
**Task:** 1.9
**Status:** ALREADY_DONE
**Evidence:** `game/ui/screens/setup_screen.py` lines 102-104 read:
```python
team0_ships = load_ships_from_entries(self.team1, team_id=0, ...)
team1_ships = load_ships_from_entries(self.team2, team_id=1, ...)
return team0_ships, team1_ships
```
**Impact:** Low
**Proposed Resolution:** Mark Task 1.9 as complete.

---

## Phase 2 Findings

### F-09: tests/fixtures/battle.py already renamed
**Task:** 2.1
**Status:** ALREADY_DONE
**Evidence:** `tests/fixtures/battle.py` lines 85-115 already use `team0_ships`/`team1_ships`. Ship names are `Team0Ship{i}` and `Team1Ship{i}`. Line 115 calls `engine.start(team0_ships, team1_ships)`. Function parameters are `team0_count`/`team1_count` (lines 62-63).
**Impact:** Medium
**Proposed Resolution:** Mark Task 2.1 as complete.

### F-10: test_service_integration.py already correct
**Task:** 2.2
**Status:** ALREADY_DONE
**Evidence:** `tests/integration/fleet_combat/test_service_integration.py` line 143 already uses `team0_count=2, team1_count=2`. Lines 146-149 use `team0_ships`/`team1_ships` as local filter variables (filtering by `team_id`), which is the correct naming.
**Impact:** Low
**Proposed Resolution:** Mark Task 2.2 as complete.

### F-11: test_battle_screen_simulation.py docstring already correct
**Task:** 2.3
**Status:** ALREADY_DONE
**Evidence:** `tests/unit/ui/test_battle_screen_simulation.py` line 90 reads:
```python
"""Test start() assigns team_id 0 to team0 and 1 to team1."""
```
This already uses `team0`/`team1` naming. The local variables on lines 94-95 use `team0_ships`/`team1_ships` (filtering by team_id), which is correct.
**Impact:** Low
**Proposed Resolution:** Mark Task 2.3 as complete.

---

## Residual Occurrences (Outside Original Checklist Scope)

The following files still contain old-style `team1_ships`/`team2_ships` naming but were **not listed in any checklist task**. These should be addressed as part of Task 2.4 (search for remaining occurrences):

### R-01: test_battle_determinism.py uses old naming
**File:** `tests/integration/fleet_combat/test_battle_determinism.py`
**Lines:** 16, 20, 35, 46
**Details:** `_run_battle(team1_ships, team2_ships, ...)` function signature and `_make_teams()` returning `team1`/`team2` local variables. These are local parameter names, not keywords -- they work because `engine.start()` is called positionally. But they violate the naming convention this project establishes.
**Proposed Resolution:** Add a subtask to Task 2.4 to rename these.

### R-02: docs/systems/combat_simulation.md uses old naming
**File:** `docs/systems/combat_simulation.md`
**Line:** 33
**Details:** Example code `controller.add_ships(team2_ships, team_id=1)` still uses old naming.
**Proposed Resolution:** Add a subtask to Task 2.4 to update the documentation example.

### R-03: battle_results_screen.py uses team1_ships local var
**File:** `game/ui/screens/battle_results_screen.py`
**Line:** 137
**Details:** `team1_ships = [s for s in self.results.ships if s.team_id == 1]` -- this is a local variable filtering by `team_id == 1`, so the naming is actually **correct** per the new convention. No change needed.

### R-04: _handle_battle_setup_action uses team1/team2 kwargs
**File:** `game/app.py`
**Lines:** 782-788
**Details:** `kwargs["team1"]` and `kwargs["team2"]` are used as callback parameter names from `setup_screen.py` which passes `team1=team1, team2=team2`. These are UI-layer data list names (`self.team1`/`self.team2`), not the ship list naming being standardized. However, they feed into `self.start_battle(kwargs["team1"], kwargs["team2"])` which expects `team0_ships`/`team1_ships`. This mismatch (UI calling them `team1`/`team2`, function expecting `team0`/`team1`) is confusing but functional since they're positional. The setup_screen callback uses `team1=` and `team2=` as kwargs names.
**Proposed Resolution:** Consider renaming the callback kwargs to `team0`/`team1` for consistency, but this is a separate concern from the core rename (the `self.team1`/`self.team2` UI lists are explicitly out of scope per the phase_1_checklist Task 1.9 notes).

### R-05: test_battle_service.py references _team1_ships
**File:** `tests/unit/simulation/services/test_battle_service.py`
**Lines:** 185, 201, 414, 761, 932, 964
**Details:** These test assertions check `service._team1_ships` which is the **new** correct naming (the internal attribute for team_id=1 ships). These are correct and need no changes.

---

## Summary Table

| Task | Status | Notes |
|------|--------|-------|
| 1.1 (Baseline) | STILL_VALID | Should still run baseline before any remaining work |
| 1.2 (battle_engine.py) | ALREADY_DONE | All params, body, docstrings already renamed |
| 1.3 (battle_service.py) | ALREADY_DONE | Keywords and internals already renamed |
| 1.4 (battle_screen.py) | ALREADY_DONE | Signature and body already renamed |
| 1.5 (battle_factories.py) | ALREADY_DONE | All functions already renamed |
| 1.6 (app.py) | ALREADY_DONE | Signature already renamed |
| 1.7 (battle_panels.py) | ALREADY_DONE | Local vars already renamed |
| 1.8 (simulation_adapter.py) | ALREADY_DONE | Local vars already renamed |
| 1.9 (setup_screen.py) | ALREADY_DONE | Local vars already renamed |
| 1.10 (Run tests) | STILL_VALID | Should verify with test run |
| 2.1 (fixtures/battle.py) | ALREADY_DONE | Params, ships, start call already renamed |
| 2.2 (test_service_integration.py) | ALREADY_DONE | Already uses correct naming |
| 2.3 (test_battle_screen_simulation.py) | ALREADY_DONE | Docstring already correct |
| 2.4 (Search remaining + full suite) | PARTIALLY_DONE | Core rename done; 2 residual files remain (R-01, R-02) |

---

## Recommendation

1. **Mark Tasks 1.2-1.9 and 2.1-2.3 as complete** -- all code changes described in these tasks are already present in the codebase.
2. **For Task 2.4**, the grep verification will find two residual occurrences:
   - `tests/integration/fleet_combat/test_battle_determinism.py` -- rename `team1_ships`/`team2_ships` params to `team0_ships`/`team1_ships` and `team1`/`team2` locals to `team0`/`team1`
   - `docs/systems/combat_simulation.md` line 33 -- update example code
3. **Run the full test suite** (Task 1.10 / Task 2.4) to confirm no regressions.
4. **Consider closing the project** after the two residual fixes and a passing test suite.
