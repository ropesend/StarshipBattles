# PROJ-244 Scope Gap Analysis Report
**Date:** 2026-04-10
**Analyst:** Scope Gap Analyst (subagent)
**Scope:** Identify areas within PROJ-244's scope that should be addressed but aren't mentioned in any task

## Executive Summary

The plan covers the core function signatures and most local variables well. However, the codebase search revealed **3 genuine scope gaps** (files/locations with the old naming pattern that are not covered by the plan or the out-of-scope list), **2 documentation gaps**, and **1 borderline naming concern**. The most impactful gap is in `test_battle_determinism.py` which is completely missing from the plan.

**Note on plan freshness:** Several files listed in the plan appear to have already been updated to 0-based naming (e.g., `BattleEngine.start()` already uses `team0_ships`/`team1_ships`, `tests/fixtures/battle.py` already uses `team0_count`/`team1_count`). The plan may have been written before some changes were made, or the changes were made outside this project. The gaps below are items that remain with old naming and are NOT covered.

---

## Findings

### GAP-01: test_battle_determinism.py -- Entire File Missing from Plan
**Location:** `tests/integration/fleet_combat/test_battle_determinism.py:16-20, 35-57`
**Related Goal:** Eliminate confusing `team1_ships` / `team2_ships` naming
**Gap Description:** This file uses the old 1-based naming throughout and is completely absent from both the plan's task list AND the out-of-scope list:
- Line 16: `def _run_battle(team1_ships, team2_ships, seed, max_ticks=500):` -- function signature uses old naming
- Line 20: `engine.start(team1_ships, team2_ships, seed=seed)` -- passes old-named params to engine
- Lines 35-57: `_make_teams()` returns `team1, team2` local variables (1-based naming for ships with `team_id=0` and `team_id=1`)

Since `BattleEngine.start()` now uses `team0_ships`/`team1_ships` parameter names, the positional call still works, but the local naming is inconsistent.

**Impact:** After the project completes, `grep -r "team2_ships" game/ tests/` (from the verification checklist) will FAIL because `test_battle_determinism.py` still has `team2_ships`. This file will block the project's own verification criteria.
**Proposed Resolution:** Add to Phase 2 as a new task (Task 2.2b or expand Task 2.2). Rename:
- `_run_battle(team1_ships, team2_ships, ...)` -> `_run_battle(team0_ships, team1_ships, ...)`
- `engine.start(team1_ships, team2_ships, ...)` -> `engine.start(team0_ships, team1_ships, ...)`
- `team1 = [...]` -> `team0 = [...]` and `team2 = [...]` -> `team1 = [...]` in `_make_teams()`
- `return team1, team2` -> `return team0, team1`
- All unpacking sites: `t1a, t2a` -> `t0a, t1a` etc.
**Effort:** Simple

---

### GAP-02: setup_screen.py `_trigger_start_battle()` -- Kwargs Use Old Naming
**Location:** `game/ui/screens/setup_screen.py:338-340`
**Related Goal:** Eliminate confusing team naming where numbers don't match `team_id`
**Gap Description:** The `_trigger_start_battle` method unpacks `get_ships()` into 1-based local variables and passes them as kwargs with old names:
```python
team1, team2 = self.get_ships()  # get_ships returns (team0_ships, team1_ships)
self.scene_callback(action, team1=team1, team2=team2)  # kwargs use old naming
```
The plan's Task 1.9 only covers `get_ships()` itself (lines 100-102), which is already updated. But lines 338-340 in `_trigger_start_battle` are not mentioned anywhere.

**Impact:** The kwargs `team1` and `team2` propagate to `app.py:_handle_battle_setup_action()` which reads `kwargs["team1"]` and `kwargs["team2"]`. This creates a cross-file naming contract that uses the old pattern. While not technically `team1_ships`/`team2_ships`, it's the same off-by-one confusion: `team1` kwarg carries ships with `team_id=0`.
**Proposed Resolution:** Add to Phase 1 Task 1.9 (setup_screen.py). Rename to:
- `team0, team1 = self.get_ships()`
- `self.scene_callback(action, team0=team0, team1=team1)`
Must be done in coordination with GAP-03 (app.py receiver).
**Effort:** Simple

---

### GAP-03: app.py `_handle_battle_setup_action()` -- Kwargs Use Old Naming
**Location:** `game/app.py:782-788`
**Related Goal:** Eliminate confusing team naming where numbers don't match `team_id`
**Gap Description:** The `_handle_battle_setup_action` method reads kwargs with old 1-based names:
```python
self.start_battle(kwargs["team1"], kwargs["team2"])  # line 782
team1, team2 = kwargs["team1"], kwargs["team2"]       # line 784
logger.info(f"Team 1: {len(team1)} ships ...")         # line 785
logger.info(f"Team 2: {len(team2)} ships ...")         # line 786
self.start_battle(team1, team2, headless=True)         # line 788
```
The plan's Task 1.6 only covers `start_battle()` (line 558) and its call to the factory (line 563), which are already updated. But lines 780-788 are not mentioned.

**Impact:** This is the kwargs receiver for GAP-02. Together they form a cross-file naming contract using old naming. `kwargs["team1"]` carries `team_id=0` ships. The log messages also say "Team 1" and "Team 2" for the ship counts -- though these could be considered user-facing display labels (like the panel labels).
**Proposed Resolution:** Add to Phase 1 Task 1.6 (app.py). Rename to:
- `kwargs["team0"]` / `kwargs["team1"]` 
- Local variables `team0, team1`
- Update log messages (or keep as "Team 1"/"Team 2" if treating as display labels -- decision needed)
Must coordinate with GAP-02 (setup_screen.py sender).
**Effort:** Simple

---

### GAP-04: docs/systems/combat_simulation.md -- Code Example Uses Old Naming
**Location:** `docs/systems/combat_simulation.md:32-33`
**Related Goal:** Update all docstrings to remove the "team1 = team 0" clarifications
**Gap Description:** The documentation code example shows:
```python
controller.add_ships(team1_ships, team_id=0)
controller.add_ships(team2_ships, team_id=1)
```
This uses the old naming pattern. The plan does not mention any documentation updates (the plan explicitly says "No documentation updates needed" at line 155 of plan.md).

**Impact:** After the project completes, the documentation will show the old naming pattern that the project was created to eliminate. Anyone reading the docs will encounter the same confusion the project aims to fix.
**Proposed Resolution:** Add to Phase 2 Task 2.4 (search for remaining occurrences) or create a new task. Update to:
```python
controller.add_ships(team0_ships, team_id=0)
controller.add_ships(team1_ships, team_id=1)
```
**Effort:** Simple

---

### GAP-05: tests/fixtures/README.md -- Code Example Uses Old Naming
**Location:** `tests/fixtures/README.md:152`
**Related Goal:** Standardize on 0-based naming
**Gap Description:** The README shows the old API:
```python
engine = create_battle_engine_with_ships(team1_count=3, team2_count=2)
```
But `create_battle_engine_with_ships()` already uses `team0_count`/`team1_count` parameters. This documentation is stale.

**Impact:** Misleads developers reading fixture documentation. Could cause confusion about the actual API.
**Proposed Resolution:** Add to Phase 2 (after fixture rename is verified). Update to:
```python
engine = create_battle_engine_with_ships(team0_count=3, team1_count=2)
```
**Effort:** Simple

---

### GAP-06 (Borderline): create_hypothetical_battle() -- ships1/ships2 Naming
**Location:** `game/ui/services/battle_factories.py:183-184`
**Related Goal:** Eliminate off-by-one naming confusion
**Gap Description:** `create_hypothetical_battle(ships1, ships2)` uses 1-based parameter names where `ships1` maps to team 0 and `ships2` maps to team 1. The docstring has to clarify: `ships1: Ships for team 0 (will be cloned)`. This is exactly the kind of "team1 = team 0" clarification the project goals say should be eliminated.

Similarly, `create_strategy_battle(fleet1, fleet2)` uses `fleet1: First fleet (team 0)`.

**Impact:** These don't use the `team1_ships`/`team2_ships` naming pattern, so they technically don't match the grep search targets. However, they perpetuate the same conceptual confusion the project aims to fix. Whether to include these is a scoping decision.
**Proposed Resolution:** Flag for user decision. If in scope: rename to `ships0`/`ships1` and `fleet0`/`fleet1` (or `team0_ships`/`team1_ships` and `team0_fleet`/`team1_fleet`). If out of scope: add to out-of-scope list with rationale.
**Effort:** Simple (if included)

---

## Cross-Reference: Goals vs. Tasks

| Goal | Covered by Tasks? | Notes |
|------|-------------------|-------|
| Eliminate `team1_ships`/`team2_ships` naming | Mostly yes | GAP-01 (test_battle_determinism.py) is missing |
| Standardize on 0-based naming | Mostly yes | GAP-02/03 (kwargs contract) not covered |
| Update docstrings to remove "team1 = team 0" clarifications | Partially | GAP-04/05 (docs, README) not covered |
| No runtime behavior changes | Yes | All gaps are pure rename changes |

## Verification Checklist Gaps

The plan's verification checklist (plan.md lines 151-155) says:
- `grep -r "team2_ships" game/ tests/` returns zero results

This grep will **fail** due to GAP-01 (`test_battle_determinism.py` still has `team2_ships`).

The plan also says:
- "No documentation updates needed (this is an internal naming change, not an architecture change)"

This is incorrect due to GAP-04 and GAP-05 -- documentation code examples use the old naming.

## Summary Table

| ID | Location | Severity | Effort | Currently in Plan? |
|----|----------|----------|--------|--------------------|
| GAP-01 | `tests/integration/fleet_combat/test_battle_determinism.py` | **High** (blocks verification) | Simple | No |
| GAP-02 | `game/ui/screens/setup_screen.py:338-340` | Medium | Simple | No |
| GAP-03 | `game/app.py:782-788` | Medium | Simple | No |
| GAP-04 | `docs/systems/combat_simulation.md:32-33` | Medium | Simple | No (plan says no docs needed) |
| GAP-05 | `tests/fixtures/README.md:152` | Low | Simple | No |
| GAP-06 | `game/ui/services/battle_factories.py:183-184` | Low (borderline) | Simple | No |
