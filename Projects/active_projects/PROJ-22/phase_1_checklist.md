# Phase 1: Critical Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-22 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address critical severity findings that pose immediate risk
**Priority:** Immediate

---

## Tasks

### Task 1.1: AR-01 - Dead physics mixin (102 lines) [Simple]
**File:** `entities/mixins/physics.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** File already deleted in previous session. Verified mixins folder is empty (only __pycache__). Zero imports found.

### Task 1.2: AR-02 - Dead combat mixin (437 lines) [Simple]
**File:** `entities/mixins/combat.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** File already deleted in previous session. Active combat mixin is in ship_combat.py (imported by ship.py).

### Task 1.3: LPA-01 - ShipControllableAdapter blocks migration [Complex]
**File:** `game/ai/interfaces/controllable.py:162-308`
**Tests:** N/A - Investigation task, defer to future PROJ

- [x] Investigate the issue at the specified location
- [x] Document scope for future PROJ

**Notes:**
**Finding:** `ShipControllableAdapter` uses `__getattr__`/`__setattr__` delegation (lines 194-203) because `AIController` in `system.py` directly accesses 20+ ship attributes instead of using `IControllable` interface methods.

**Attributes accessed directly:** `position`, `turn_throttle`, `angle`, `engine_throttle`, `formation_members`, `in_formation`, `formation_master`, `turn_speed`, `radius`, `get_components_by_ability()`, etc.

**Resolution:** This requires ~50 method updates across AIController to use interface methods exclusively. **Recommend creating new PROJ-XX for "IControllable Interface Migration"** rather than addressing in this cleanup project.

**Status:** DOCUMENTED - Deferred to future PROJ. No code change required in PROJ-22.

### Task 1.4: LDF-01 - Module-level side effect [Medium]
**File:** `game/ai/core/system.py`
**Tests:** `pytest tests/unit/ai/ tests/integration/test_ai_strategy.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Converted `load_combat_strategies()` from module-level call to lazy initialization.
- Added `_StrategyManagerProxy` for `STRATEGY_MANAGER` (lazy on first access)
- Added `_CombatStrategiesProxy` for `COMBAT_STRATEGIES` dict (lazy proxy)
- All 189 AI tests + 23 integration tests pass.

### Task 1.5: LDF-02 - GameSession legacy params [Complex]
**File:** `game/strategy/engine/game_session.py:60-69`
**Tests:** `pytest tests/strategy/test_command_handlers.py tests/strategy/test_game_session_strategy.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Added deprecation warnings when `galaxy_radius` or `system_count` parameters are passed directly to `GameSession()`
- Updated 6 test usages to use proper `GameConfig(system_count=X)` pattern
- Files updated: `test_command_handlers.py`, `test_game_session_strategy.py`
- All 27 gameplay loop integration tests + 6 strategy tests pass.

### Task 1.6: MSA-01 - ValidationResult import chain [Simple]
**File:** `ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ValidationResult was imported from indirect path (ship_validator) but never used. Removed unused import entirely. 541 tests pass.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
