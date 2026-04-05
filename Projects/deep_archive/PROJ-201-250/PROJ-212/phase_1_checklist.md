# Phase 1: Quick Wins (Simple Fixes)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-212 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Eliminate unnecessary deferred imports and fix DRY violations — all zero/low-risk changes
**Priority:** High
**Effort:** Simple (all tasks)

---

## Tasks

### Task 1.1: RS-002 — Promote FleetOrder/OrderType imports in command_handlers.py [Simple]
**File:** `game/strategy/engine/command_handlers.py`
**Finding:** 11 identical `from game.strategy.data.fleet import FleetOrder, OrderType` deferred imports inside method bodies. Validators confirmed no actual circular dependency exists — these are vestigial deferrals.
**Tests:** `pytest tests/unit/strategy/engine/ -x`

- [x] Read file, confirm the 11 deferred imports of FleetOrder/OrderType
- [x] Add single top-level import: `from game.strategy.data.fleet import FleetOrder, OrderType`
- [x] Remove all 11 inline occurrences
- [x] Also check `create_default_registry()` for deferred superweapon handler imports (intentional - different module)
- [x] Run tests, verify no regressions

**Notes:** [Filled during implementation]

### Task 1.2: CA-002 — Consolidate duplicate imports in strategy_build_queue_manager.py [Simple]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Finding:** Same 3 imports (`BuildQueueScreen`, `DesignLibrary`, `DesignLoaderAdapter`) duplicated in `on_build_yard_click()`, `on_navigate_to_hex_build()`, and `on_fleet_build_click()`.
**Tests:** `pytest tests/unit/ui/ -x`

- [x] Read file, confirm the 3 duplicate import sites
- [x] Promote all 3 imports to top-level (verify no circular dependency)
- [x] Remove duplicate inline occurrences from all 3 methods
- [x] Run tests, verify no regressions

**Notes:** Promoted BuildQueueScreen, DesignLibrary, DesignLoaderAdapter to top-level. Updated test patches to match new import location.

### Task 1.3: IIA-003 — Consolidate formula_system imports in weapons.py [Simple]
**File:** `game/simulation/components/abilities/weapons.py`
**Finding:** `safe_evaluate_math_formula` from `game.simulation.formula_system` imported inline 7 separate times within `WeaponAbility.__init__` and `sync_data` methods. No circular dependency.
**Tests:** `pytest tests/unit/simulation/components/ -x`

- [x] Read file, confirm the 7 inline imports of `safe_evaluate_math_formula`
- [x] Add single top-level import
- [x] Remove all 7 inline occurrences
- [x] Run tests, verify no regressions

**Notes:** Found 7 inline imports. Promoted to top-level. Fixed indentation issues from replace_all.

### Task 1.4: RS-003 — Promote command imports in UI fleet ops files [Simple]
**File:** `game/ui/screens/strategy_fleet_ops.py` (and possibly `strategy_window_manager.py`, `strategy_colonization.py`)
**Finding:** UI files defer command class imports (`IssueMoveCommand`, `IssueInterceptCommand`, `IssueJoinFleetCommand`, `ClearFleetOrdersCommand`, `IssueBuildOrderCommand`) despite no circular dependency with those command classes.
**Tests:** `pytest tests/unit/ui/ -x`

- [x] Read `strategy_fleet_ops.py`, identify all deferred command imports
- [x] Verify no circular dependency by checking the command module's own imports
- [x] Promote to top-level
- [x] Check `strategy_window_manager.py` for similar unnecessary deferrals (not needed)
- [x] Run tests, verify no regressions

**Notes:** Promoted IssueMoveCommand, IssueInterceptCommand, IssueJoinFleetCommand to top-level.

### Task 1.5: RS-004 — Fix facade bypass in strategy_build_queue_manager.py [Simple]
**File:** `game/ui/screens/strategy_build_queue_manager.py`
**Finding:** Uses `self._screen.session.handle_command(cmd)` directly instead of `self.facade.handle_command(cmd)`, bypassing the StrategySessionFacade. All other UI delegates use the facade pattern.
**Tests:** `pytest tests/unit/ui/ -x`

- [x] Read file, find the `self._screen.session.handle_command(cmd)` call
- [x] Verify the facade is available (check constructor or parent class)
- [x] Replace with `self._screen.facade.handle_command(cmd)`
- [x] Run tests, verify no regressions

**Notes:** Fixed 2 occurrences (lines 142 and 146). Updated test mocks to use facade.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Full test suite passes: `pytest tests/ -n 12` (12866 passed, 1 skipped + 4 pre-existing bug_13 failures)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
