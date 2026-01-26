# Phase 5: Deprecated Functions [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove deprecated load_combat_strategies and _execute_move_step

---

## Tasks

### Task 5.1: Update load_combat_strategies Callers [Medium]
**Files:** `game/ui/screens/workshop_data_loader.py`, `simulation_tests/conftest.py`, `conftest.py`
**Tests:** `pytest tests/unit/builder/test_builder_data_loader.py -v`

- [x] `game/ui/screens/workshop_data_loader.py` - Updated to use StrategyManager.instance().load_data() directly
- [x] Removed import of load_combat_strategies from the file
- [x] `simulation_tests/conftest.py:96` - Updated to use StrategyManager directly
- [x] `conftest.py:60` - Removed the monkeypatch since function no longer exists
- [x] `tests/infrastructure/session_cache.py` - Updated to use StrategyManager directly
- [x] `tests/unit/ai/test_strategy_system.py` - Removed unused import
- [x] Verify: Grep shows no remaining calls

**Notes:** Found more callers than listed - all updated

---

### Task 5.2: Remove load_combat_strategies Function [Simple]
**Files:** `game/ai/strategy_manager.py`, `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [x] `game/ai/strategy_manager.py` - Deleted `load_combat_strategies()` function
- [x] `game/ai/controller.py` - Removed `load_combat_strategies` from re-exports
- [x] Verify: `python -c "from game.ai.strategy_manager import StrategyManager"` works

**Notes:**

---

### Task 5.3: Remove _execute_move_step Method [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/test_advanced_fleet_orders.py -v`

- [x] `game/strategy/engine/turn_engine.py` - Deleted `_execute_move_step()` method (lines 261-286)

**Notes:**

---

### Task 5.4: Update Test Using _execute_move_step [Medium]
**File:** `tests/unit/test_advanced_fleet_orders.py`
**Tests:** `pytest tests/unit/test_advanced_fleet_orders.py -v`

- [x] Line 127: Updated test to use `_calculate_next_hex` and apply movement manually
- [x] Verify: Test passes with new implementation

**Notes:** Test now uses the canonical pattern

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] No remaining load_combat_strategies calls
- [x] No remaining _execute_move_step calls
- [x] Run: `pytest tests/unit/ai/ tests/unit/test_advanced_fleet_orders.py tests/unit/builder/test_builder_data_loader.py -v` - 204 tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
