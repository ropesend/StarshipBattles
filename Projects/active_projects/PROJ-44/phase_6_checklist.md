# Phase 6: BattleController Mode Handlers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract battle mode handling using Strategy pattern.

---

## Tasks

### Task 6.1: Create BattleMode Interface [Simple]
**File:** Create `game/simulation/battle/battle_mode_handler.py`
**Issue:** CQ-024 - Open/Closed violation
**Tests:** `pytest tests/unit/simulation/test_battle_controller.py`

- [ ] Create abstract `BattleModeHandler`:
  ```python
  class BattleModeHandler(ABC):
      @abstractmethod
      def configure(self, controller, config) -> None
      @abstractmethod
      def can_retreat(self) -> bool
      @abstractmethod
      def can_reinforce(self) -> bool
      @abstractmethod
      def apply_results(self, controller, results) -> None
  ```
- [ ] Verify: Interface defined correctly

**Notes:**

---

### Task 6.2: Implement Mode Handlers [Medium]
**Files:** Create handlers in `game/simulation/battle/`
**Issue:** CQ-006, CQ-024 - 4 modes handled by conditionals
**Tests:** `pytest tests/unit/simulation/test_battle_controller.py`

- [ ] Create `ManualBattleModeHandler` (no retreat, no reinforce, no fleet effects)
- [ ] Create `TestBattleModeHandler` (headless, no persist)
- [ ] Create `StrategyBattleModeHandler` (retreat, reinforce, fleet effects)
- [ ] Create `HypotheticalBattleModeHandler` (isolated, ship cloning)
- [ ] Verify: Each handler works independently

**Notes:**

---

### Task 6.3: Refactor BattleController to Use Handlers [Medium]
**File:** `game/simulation/battle_controller.py`
**Issue:** CQ-006 - 40+ methods, mode-specific logic scattered
**Tests:** `pytest tests/unit/simulation/test_battle_controller.py`

- [ ] Add `_mode_handler: BattleModeHandler` field
- [ ] Refactor `configure()` to select appropriate handler
- [ ] Delegate mode-specific logic to handlers
- [ ] Remove mode conditionals from core methods
- [ ] Verify: All 4 battle modes work correctly

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
