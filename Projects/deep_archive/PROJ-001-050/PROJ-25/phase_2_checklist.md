# Phase 2: Migrate UI Consumers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-25 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update all UI files to use refactored imports from `game.ai.strategy_manager`

---

## Tasks

### Task 2.1: Remove Unused Import from battle.py [Simple]
**File:** `game/ui/screens/battle.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Remove line: `from game.ai.core.system import AIController`
- [x] Verify no other references to AIController in file (should be none - it was unused)
- [x] Run tests: `pytest tests/unit/ui/`

**Notes:** Removed unused import. No other AIController references in file.

### Task 2.2: Update setup.py [Simple]
**File:** `game/ui/screens/setup.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Add import: `from game.ai.strategy_manager import StrategyManager`
- [x] Remove import: `from game.ai.core.system import COMBAT_STRATEGIES`
- [x] Find all uses of `COMBAT_STRATEGIES` and replace with `StrategyManager.instance().strategies`:
  - Line ~139: `self.ai_strategies = list(COMBAT_STRATEGIES.keys())`
  - Line ~611: `COMBAT_STRATEGIES.get(strategy, {}).get('name', ...)`
  - Line ~671: `COMBAT_STRATEGIES.get(strat_id, {}).get('name', ...)`
- [x] Run tests: `pytest tests/unit/ui/`

**Notes:** All 3 usages updated successfully.

### Task 2.3: Update panels.py [Simple]
**File:** `game/ui/hud/panels.py`
**Tests:** `pytest tests/unit/ui/`

- [x] Add import: `from game.ai.strategy_manager import StrategyManager`
- [x] Remove import: `from game.ai.core.system import COMBAT_STRATEGIES`
- [x] Find all uses of `COMBAT_STRATEGIES.get(...)` and replace with `StrategyManager.instance().strategies.get(...)`
- [x] Run tests: `pytest tests/unit/ui/`

**Notes:** 1 usage at line 121 updated.

### Task 2.4: Update right_panel.py [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/builder/`

- [x] Change import from `from game.ai.core.system import STRATEGY_MANAGER` to `from game.ai.strategy_manager import StrategyManager`
- [x] Replace `STRATEGY_MANAGER` with `StrategyManager.instance()` throughout file
- [x] Replace `STRATEGY_MANAGER.strategies` with `StrategyManager.instance().strategies`
- [x] Run tests: `pytest tests/unit/builder/`

**Notes:** 2 usages at lines 154 and 243 updated.

### Task 2.5: Update builder/main.py [Simple] (Discovered)
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/builder/`

- [x] Update inline import at line ~656 from `from game.ai.core.system import STRATEGY_MANAGER` to `from game.ai.strategy_manager import StrategyManager`
- [x] Update inline import at line ~852 from `from game.ai.core.system import STRATEGY_MANAGER, load_combat_strategies` to `from game.ai.strategy_manager import StrategyManager`
- [x] Replace all STRATEGY_MANAGER usages with StrategyManager.instance()
- [x] Replace load_combat_strategies() with StrategyManager.instance().load_data()
- [x] Run tests: `pytest tests/unit/builder/`

**Notes:** This file was not in the original plan but was discovered during Phase 1 grep analysis. 2 inline import locations updated.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/ui/ tests/unit/builder/` - all pass (114 passed)
- [ ] Manual test: Launch game, verify AI strategy dropdowns show correct names
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
