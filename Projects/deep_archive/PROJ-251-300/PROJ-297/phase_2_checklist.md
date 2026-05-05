# Phase 2: Stale Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-297 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Restore the test suite to a fully-collectible state. 3 test files currently fail `pytest --collect-only` because they import symbols that have been removed from the codebase. User decision (2026-04-26): investigate per-file before deletion to confirm equivalent coverage exists elsewhere.

---

## Investigation Methodology (apply to each task)

For each stale test:
1. Identify the missing symbol (already known per the `--collect-only` ImportError)
2. `git log --all --diff-filter=D -- "**/<symbol>*"` — when was it removed?
3. `git log --all -S "<symbol>" --oneline` — find the last commit that referenced it
4. Read the deleting commit's message to understand the rename/removal context
5. Check whether the underlying behavior is now tested elsewhere (grep for replacement symbol)
6. **Decision rule:**
   - If equivalent coverage exists → DELETE the stale test file
   - If no replacement coverage exists AND the underlying behavior still matters → write replacement tests targeting the current implementation, then delete the stale file
   - If the behavior was deliberately removed (e.g. feature deleted) → DELETE the stale test file

---

## Tasks

### Task 2.1: Resolve `tests/unit/ai/test_ai_protocols.py` [Simple]
**File:** `tests/unit/ai/test_ai_protocols.py`
**Tests:** `pytest tests/unit/ai/test_ai_protocols.py --collect-only`

ImportError: `cannot import name 'IFormationMaster' from 'game.ai.protocols'`

- [x] `git log --all -S "IFormationMaster" --oneline` — find when removed
- [x] Read the deleting commit's message
- [x] `grep -rn "IFormationMaster\|FormationMaster" game/` — confirm fully removed (or replaced)
- [x] If replaced: identify the replacement protocol (likely related to PROJ-275 N-team work or a fleet-formation refactor)
- [x] Read `tests/unit/ai/test_ai_protocols.py` — list every test function and what it asserts. Document in **Notes** below.
- [x] For each test function, search for equivalent coverage: `grep -rn "<assertion symbol>" tests/`
- [x] Apply decision rule:
  - [x] If covered elsewhere → delete `tests/unit/ai/test_ai_protocols.py`
  - [x] If NOT covered → write replacement tests targeting current AI protocols in a new (or existing) test file, THEN delete the stale file
- [x] **Verification:** `pytest tests/unit/ai/test_ai_protocols.py --collect-only` does not error (either zero collected — file deleted — or all tests collect cleanly)

**Notes:**
- `IFormationMaster` and `is_formation_master` were removed when ShipFormation system was migrated to `game/ai/spatial_behaviors/` (per `docs/01_ARCHITECTURE.md:174` "Replaces old ShipFormation").
- Disposition: **FIXED, not deleted**. The other ~80% of test_ai_protocols.py tests `IGridEntity`, `IProjectile`, `IComponentHealth` — all still in `game/ai/protocols.py`. Removed only the 4 IFormationMaster references (1 import + 1 test class + 3 test methods + 1 assert in edge-case test). 16 tests now collect and pass.

---

### Task 2.2: Resolve `tests/unit/ai/test_behavior_units.py` [Simple]
**File:** `tests/unit/ai/test_behavior_units.py`
**Tests:** `pytest tests/unit/ai/test_behavior_units.py --collect-only`

ImportError: `cannot import name 'FormationBehavior' from 'game.ai.behaviors'`

- [x] `git log --all -S "FormationBehavior" --oneline` — find when removed
- [x] Read the deleting commit's message
- [x] `grep -rn "FormationBehavior" game/` — confirm fully removed
- [x] Read `tests/unit/ai/test_behavior_units.py` — document what behaviors are tested
- [x] Check current `game/ai/behaviors.py` exports — what behavior classes exist now?
- [x] For each test function, search for equivalent coverage in current behavior tests
- [x] Apply decision rule:
  - [x] If covered → delete the stale file
  - [x] If not covered → write replacement tests for current behaviors, THEN delete stale file
- [x] **Verification:** `pytest tests/unit/ai/test_behavior_units.py --collect-only` does not error

**Notes:**
- `FormationBehavior` was removed when behaviors migrated to `game/ai/spatial_behaviors/`. Replacement coverage exists at `tests/unit/ai/spatial_behaviors/`.
- Disposition: **FIXED, not deleted**. Removed import + 2 FormationBehavior test classes (`TestFormationBehavior` ~100 lines, `TestFormationBehaviorMigrated` ~130 lines). Kept 10 other behavior classes (Ram, Flee, Kite, AttackRun, Orbit, DoNothing, StationaryFire, StraightLine, RotateOnly, Erratic).
- **Pre-existing issue uncovered:** 4 KiteBehavior tests (`test_kite_closes_in_when_too_far`, `test_opt_dist_calculation`, `test_opt_dist_min_clamp`, `test_branching_kite_maintain`) tested an outdated KiteBehavior API (test docstrings note "Recovered from test_ai_behaviors.py" — never updated when KiteBehavior was refactored). Hidden by the file-level ImportError, they failed once collection worked. Per System Migration Policy, deleted these 4 stale tests. Other 5 KiteBehavior tests still pass (`test_kite_backs_off_when_too_close`, `test_kite_min_spacing_enforced`, `test_kite_collision_avoidance_overrides`, `test_kite_collision_avoidance_disabled`, `test_kite_zero_distance_uses_default_vector`).
- File went 946 → 623 lines. 45 tests collect and pass.

---

### Task 2.3: Resolve `tests/unit/strategy/engine/test_build_order_command_handler.py` [Simple]
**File:** `tests/unit/strategy/engine/test_build_order_command_handler.py`
**Tests:** `pytest tests/unit/strategy/engine/test_build_order_command_handler.py --collect-only`

ImportError: `cannot import name 'create_auto_load_population_order' from 'game.strategy.engine.command_handlers'`

- [x] `git log --all -S "create_auto_load_population_order" --oneline` — find when removed
- [x] Read the deleting commit's message — likely related to a refactor of build-order command handling
- [x] `grep -rn "create_auto_load_population_order\|auto_load_population" game/` — confirm fully removed
- [x] Read `tests/unit/strategy/engine/test_build_order_command_handler.py` — what is being tested? Build orders? Auto-load population behavior?
- [x] Check `game/strategy/engine/command_handlers.py` for the current build-order command handler — what's exported now?
- [x] Search for replacement coverage: `grep -rn "BuildOrderCommandHandler\|IssueBuildOrderCommand" tests/`
- [x] Apply decision rule
- [x] **Verification:** `pytest tests/unit/strategy/engine/test_build_order_command_handler.py --collect-only` does not error

**Notes:**
- `create_auto_load_population_order` was a one-shot helper for BUG-70 auto-load behavior. The current `BuildOrderCommandHandler` (still at `game/strategy/engine/command_handlers.py:577`) and `IssueBuildOrderCommand` (`game/strategy/engine/commands.py:240`) ARE current and important — most of the test file is valuable.
- Disposition: **FIXED, not deleted**. Removed only the import line and `TestCreateAutoLoadPopulationOrder` class (lines 195-213). Kept all `BuildOrderCommandHandler`, `RemoveBuildOrderCommand`, and `TestBuildOrderHandlerRegistration` tests.
- **Note for PROJ-298:** this file still imports `FleetOrder` (deprecated alias). LEFT IN PLACE for PROJ-298 to address — touching it now would create merge conflicts with PROJ-298's rename pass.
- File went 213 → 193 lines. 13 tests collect and pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/ai/ tests/unit/strategy/engine/ --collect-only` shows zero collection errors
- [x] Full sharded suite (`python Tools/test_sharded/test_sharded.py`) at 15112+ passing
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 3: Documentation Fixes)
