# Phase 8: BattleEngine-AIController Decoupling (SIM-008)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove internal AIController creation from BattleEngine

---

## Prerequisites
- [ ] Phase 6 complete (simulation interfaces)

## Background

**Problem (SIM-008):**
- BattleEngine creates AIController internally with hardcoded imports when not provided
- Location: `game/simulation/systems/battle_engine.py:212-236, 272-284, 433-435`
- Creates circular dependency risk
- Engine cannot be tested without AI layer

**Target:** Require AIControllers to be passed at initialization.

---

## Tasks

### Task 8.1: Create IAIController Protocol [Simple]
**File:** `game/simulation/interfaces/ai_controller.py` (NEW)
**Tests:** `pytest tests/unit/simulation/interfaces/`

- [ ] Create `IAIController` protocol:
  - `update(ship, engine_state)` - main update method
  - `reset()` - reset controller state
  - Any other methods used by BattleEngine
- [ ] Add to `game/simulation/interfaces/__init__.py`
- [ ] Create unit tests verifying interface

**Notes:**

---

### Task 8.2: Analyze BattleEngine AIController Usage [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** N/A (analysis)

Document AIController usage:
- [ ] Line 212-236: AIController creation logic
- [ ] Line 272-284: Additional AI setup
- [ ] Line 433-435: AI update calls
- [ ] Document what methods are called on AIController
- [ ] Add to findings/phase_8_analysis.md

**Notes:**

---

### Task 8.3: Refactor BattleEngine Constructor [Medium]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine.py`

**Changes:**
- [ ] Add `ai_controllers` parameter to constructor:
  ```python
  def __init__(self, ..., ai_controllers: Dict[int, IAIController] = None):
  ```
- [ ] Remove internal AIController creation logic
- [ ] Remove internal `from game.ai import AIController` imports
- [ ] Require callers to provide AI controllers or explicitly pass None for no-AI battles
- [ ] Update any internal AI creation to raise error if not provided

**Notes:**

---

### Task 8.4: Create AI Controller Factory [Simple]
**File:** `game/simulation/factories/ai_factory.py` (NEW)
**Tests:** `pytest tests/unit/simulation/factories/`

- [ ] Create `AIControllerFactory` class:
  - `create_for_ships(ships, team_id) -> Dict[int, IAIController]`
- [ ] Factory handles importing from game.ai
- [ ] Isolates AI dependency to factory only
- [ ] Create unit tests

**Notes:**

---

### Task 8.5: Update BattleEngine Instantiation Sites [Medium]
**Files:** All files that create BattleEngine
**Tests:** `pytest tests/unit/simulation/ tests/integration/`

- [ ] Find all BattleEngine instantiation sites:
  ```bash
  grep -rn "BattleEngine(" game/ tests/
  ```
- [ ] Update each to provide ai_controllers parameter
- [ ] Use AIControllerFactory for production code
- [ ] Use mock controllers for tests
- [ ] Verify all sites updated

**Notes:**

---

### Task 8.6: Update BattleService [Medium]
**File:** `game/simulation/services/battle_service.py`
**Tests:** `pytest tests/unit/simulation/services/test_battle_service.py`

- [ ] Update BattleService to use AIControllerFactory
- [ ] Ensure BattleService creates AI controllers when needed
- [ ] Update any direct BattleEngine creation

**Notes:**

---

### Task 8.7: Create Mock AI Controller for Tests [Simple]
**File:** `tests/unit/simulation/mocks/mock_ai_controller.py` (NEW)
**Tests:** N/A (test utility)

- [ ] Create `MockAIController` implementing IAIController:
  - Tracks method calls
  - Returns configurable responses
  - Can be configured to raise errors
- [ ] Document usage for tests

**Notes:**

---

### Task 8.8: Integration Testing [Simple]
**Tests:** `pytest tests/integration/simulation/ tests/integration/test_battle*.py`

- [ ] Run battle integration tests
- [ ] Verify AI-controlled battles work
- [ ] Verify headless battles work
- [ ] Verify battle service works
- [ ] Run full test suite

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] IAIController protocol created
- [ ] BattleEngine requires AI controllers via constructor
- [ ] No internal AIController imports in BattleEngine
- [ ] AIControllerFactory created
- [ ] All tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 9
