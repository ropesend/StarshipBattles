# Phase 5: Deprecated Functions [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-15 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove deprecated load_combat_strategies and _execute_move_step

---

## Tasks

### Task 5.1: Update load_combat_strategies Callers [Medium]
**Files:** `game/ui/screens/workshop_data_loader.py`, `simulation_tests/conftest.py`, `conftest.py`
**Tests:** `pytest tests/unit/builder/test_builder_data_loader.py -v`

- [ ] `game/ui/screens/workshop_data_loader.py:168` - Update to use StrategyManager directly:
  ```python
  # FROM:
  if strat_path:
      load_combat_strategies(strat_path)
  # TO:
  if strat_path:
      from game.ai.strategy_manager import StrategyManager
      manager = StrategyManager.instance()
      manager.load_data(os.path.dirname(strat_path))
  ```
- [ ] Also update import at top of file (remove load_combat_strategies import if present)
- [ ] `simulation_tests/conftest.py:96` - Update similarly to use StrategyManager.instance().load_data()
- [ ] `conftest.py:60` - Remove or update the monkeypatch (function no longer exists)
- [ ] Verify: Grep shows no remaining calls: `grep -r "load_combat_strategies" game/ tests/ --include="*.py"`

**Notes:**

---

### Task 5.2: Remove load_combat_strategies Function [Simple]
**Files:** `game/ai/strategy_manager.py`, `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] `game/ai/strategy_manager.py` - Delete lines 151-171: `load_combat_strategies()` function
- [ ] `game/ai/controller.py` - Remove `load_combat_strategies` from re-exports (around line 55)
- [ ] Verify: `python -c "from game.ai.strategy_manager import StrategyManager"` works

**Notes:**

---

### Task 5.3: Remove _execute_move_step Method [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/test_advanced_fleet_orders.py -v`

- [ ] `game/strategy/engine/turn_engine.py` - Delete lines 261-286: `_execute_move_step()` method

**Notes:**

---

### Task 5.4: Update Test Using _execute_move_step [Medium]
**File:** `tests/unit/test_advanced_fleet_orders.py`
**Tests:** `pytest tests/unit/test_advanced_fleet_orders.py -v`

- [ ] Line 127: Update test to not use deprecated method:
  ```python
  # FROM:
  engine._execute_move_step(f1, galaxy)

  # TO:
  next_hex = engine._calculate_next_hex(f1, galaxy)
  if next_hex:
      f1.location = next_hex
      if f1.path:
          f1.path.pop(0)
      elif not f1.has_orders():
          pass  # No orders to pop
  ```
- [ ] Verify: Test passes with new implementation

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No remaining load_combat_strategies calls
- [ ] No remaining _execute_move_step calls
- [ ] Run: `pytest tests/unit/ai/ tests/unit/test_advanced_fleet_orders.py tests/unit/builder/test_builder_data_loader.py -v`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
