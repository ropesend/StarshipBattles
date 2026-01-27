# Phase 2: Migrate UI Consumers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-25 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all UI files to use refactored imports from `game.ai.strategy_manager`

---

## Tasks

### Task 2.1: Remove Unused Import from battle.py [Simple]
**File:** `game/ui/screens/battle.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Remove line: `from game.ai.core.system import AIController`
- [ ] Verify no other references to AIController in file (should be none - it was unused)
- [ ] Run tests: `pytest tests/unit/ui/`

**Notes:**

### Task 2.2: Update setup.py [Simple]
**File:** `game/ui/screens/setup.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Add import: `from game.ai.strategy_manager import StrategyManager`
- [ ] Remove import: `from game.ai.core.system import COMBAT_STRATEGIES`
- [ ] Find all uses of `COMBAT_STRATEGIES` and replace with `StrategyManager.instance().strategies`:
  - Line ~139: `self.ai_strategies = list(COMBAT_STRATEGIES.keys())`
  - Line ~611: `COMBAT_STRATEGIES.get(strategy, {}).get('name', ...)`
  - Line ~671: `COMBAT_STRATEGIES.get(strat_id, {}).get('name', ...)`
- [ ] Run tests: `pytest tests/unit/ui/`

**Notes:**

### Task 2.3: Update panels.py [Simple]
**File:** `game/ui/hud/panels.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Add import: `from game.ai.strategy_manager import StrategyManager`
- [ ] Remove import: `from game.ai.core.system import COMBAT_STRATEGIES`
- [ ] Find all uses of `COMBAT_STRATEGIES.get(...)` and replace with `StrategyManager.instance().strategies.get(...)`
- [ ] Run tests: `pytest tests/unit/ui/`

**Notes:**

### Task 2.4: Update right_panel.py [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/builder/`

- [ ] Change import from `from game.ai.core.system import STRATEGY_MANAGER` to `from game.ai.strategy_manager import StrategyManager`
- [ ] Replace `STRATEGY_MANAGER` with `StrategyManager.instance()` throughout file
- [ ] Replace `STRATEGY_MANAGER.strategies` with `StrategyManager.instance().strategies`
- [ ] Run tests: `pytest tests/unit/builder/`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/ui/ tests/unit/builder/` - all pass
- [ ] Manual test: Launch game, verify AI strategy dropdowns show correct names
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
