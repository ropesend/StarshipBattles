# Phase 6: BattleController Mode Handlers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract battle mode handling using Strategy pattern.

---

## Tasks

### Task 6.1: Create BattleMode Interface [Simple]
**File:** Create `game/simulation/combat/battle_mode_handler.py`
**Issue:** CQ-024 - Open/Closed violation
**Tests:** `pytest tests/unit/simulation/combat/test_battle_mode_handlers.py`

- [x] Create abstract `BattleModeHandler`:
  ```python
  class BattleModeHandler(ABC):
      @abstractmethod
      def configure(self, controller, config) -> None
      @abstractmethod
      def can_retreat(self) -> bool
      @abstractmethod
      def can_reinforce(self) -> bool
      @abstractmethod
      def should_clone_ships(self) -> bool
      @abstractmethod
      def is_headless_default(self) -> bool
      @abstractmethod
      def apply_results(self, controller, results) -> None
  ```
- [x] Verify: Interface defined correctly

**Notes:** Extended interface with should_clone_ships() and is_headless_default() for complete mode encapsulation.

---

### Task 6.2: Implement Mode Handlers [Medium]
**Files:** Create handlers in `game/simulation/combat/`
**Issue:** CQ-006, CQ-024 - 4 modes handled by conditionals
**Tests:** `pytest tests/unit/simulation/combat/test_battle_mode_handlers.py`

- [x] Create `ManualBattleModeHandler` (no retreat, no reinforce, no fleet effects)
- [x] Create `TestBattleModeHandler` (headless, no persist)
- [x] Create `StrategyBattleModeHandler` (retreat, reinforce, fleet effects)
- [x] Create `HypotheticalBattleModeHandler` (isolated, ship cloning)
- [x] Verify: Each handler works independently (45 tests pass)

**Notes:** Also created get_handler_for_mode() factory function.

---

### Task 6.3: Refactor BattleController to Use Handlers [Medium]
**File:** `game/simulation/battle_controller.py`
**Issue:** CQ-006 - 40+ methods, mode-specific logic scattered
**Tests:** `pytest tests/unit/simulation/test_battle_controller.py`

- [x] Add `_mode_handler: BattleModeHandler` field
- [x] Refactor `configure()` to select appropriate handler
- [x] Delegate mode-specific logic to handlers
- [x] Added `_retreat_allowed()` and `_reinforcements_allowed()` helper methods
- [x] Verify: All 4 battle modes work correctly (110 controller tests pass)

**Notes:** Backward compatible - config.allow_retreat/allow_reinforcements still work alongside handlers.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/` - all tests pass (5545 passed, 3 skipped)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
