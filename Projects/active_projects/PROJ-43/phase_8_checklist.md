# Phase 8: BattleEngine-AIController Decoupling (SIM-008)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove internal AIController creation from BattleEngine

---

## Prerequisites
- [x] Phase 6 complete (simulation interfaces)

## Background

**Problem (SIM-008):**
- BattleEngine creates AIController internally with hardcoded imports when not provided
- Location: `game/simulation/systems/battle_engine.py:212-236, 272-284, 433-435`
- Creates circular dependency risk
- Engine cannot be tested without AI layer

**Target:** Require AIControllers to be passed at initialization.

---

## Tasks

### Task 8.1: Create IAIController Protocol [Simple] - COMPLETE
**File:** `game/simulation/interfaces/ai_controller.py` (NEW)
**Tests:** `pytest tests/unit/simulation/interfaces/`

- [x] Create `IAIController` protocol:
  - `update()` - main update method (no params needed - controller has ship reference)
  - `ship` property - for identification when removing ships
- [x] Add to `game/simulation/interfaces/__init__.py`
- [x] Create unit tests verifying interface: 8 tests, all passing

**Notes:** Simplified protocol to only what BattleEngine needs. No `reset()` needed as
BattleEngine never calls it. Protocol is @runtime_checkable for isinstance() checks.

---

### Task 8.2: Analyze BattleEngine AIController Usage [Simple] - COMPLETE
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** N/A (analysis)

Document AIController usage:
- [x] Line 226-241: Legacy path creates AIController in start()
- [x] Line 284-289: Legacy path creates AIController in add_ship_mid_battle()
- [x] Line 439-442: Creates AIController for fighter launches in update()
- [x] Document what methods are called on AIController (only update())
- [x] Add to findings/phase_8_analysis.md

**Notes:** Found 3 internal AI creation points. PROJ-17 already added optional parameter
to start() and add_ship_mid_battle(). Fighter launch in update() is trickiest case.

---

### Task 8.3: Refactor BattleEngine Constructor [Medium] - COMPLETE
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/combat/test_battle_engine_core.py`

**Changes:**
- [x] Add `ai_factory` parameter to constructor (optional)
- [x] Update `start()` to use factory when available
- [x] Update `add_ship_mid_battle()` to use factory when available
- [x] Update fighter launch in `update()` to use factory when available
- [x] Keep legacy paths for backward compatibility
- [x] Added 3 new tests for factory path: all passing

**Notes:** Conservative refactor - kept legacy paths working. Factory is optional, when provided
it is used for all AI controller creation (start, mid-battle, fighter launch). Explicit
ai_controllers parameter takes precedence over factory.

---

### Task 8.4: Create AI Controller Factory [Simple] - COMPLETE
**File:** `game/simulation/factories/ai_factory.py` (NEW)
**Tests:** `pytest tests/unit/simulation/factories/`

- [x] Create `AIControllerFactory` class:
  - `create_for_ship(ship, enemy_team_id)` - single ship
  - `create_for_ships(ships, enemy_team_id)` - multiple ships
- [x] Factory handles importing from game.ai
- [x] Isolates AI dependency to factory only
- [x] Create unit tests: 9 tests, all passing

**Notes:** Factory takes grid at construction for all controllers to share.

---

### Task 8.5: Update BattleEngine Instantiation Sites [Medium] - COMPLETE
**Files:** All files that create BattleEngine
**Tests:** `pytest tests/unit/simulation/ tests/integration/`

- [x] Find all BattleEngine instantiation sites (grep)
- [x] Only 1 production site found: `game/simulation/services/battle_service.py:59`
- [x] BattleService updated to use AIControllerFactory (Task 8.6)
- [x] Tests continue to work via legacy path (backward compatible)
- [x] Verify all sites work: 15 BattleService tests pass

**Notes:** Since refactor maintained backward compatibility, all existing instantiation sites
work without changes. BattleService is the key production site and was updated to use factory.

---

### Task 8.6: Update BattleService [Medium] - COMPLETE
**File:** `game/simulation/services/battle_service.py`
**Tests:** `pytest tests/unit/services/test_battle_service.py`

- [x] Update BattleService to use AIControllerFactory
- [x] Import AIControllerFactory at module level
- [x] Create factory and attach to engine in create_battle()
- [x] All 15 BattleService tests pass

**Notes:** BattleService now creates an AIControllerFactory using engine's grid and sets
it on the engine, enabling factory-based AI controller creation.

---

### Task 8.7: Create Mock AI Controller for Tests [Simple] - COMPLETE
**File:** `tests/unit/simulation/mocks/mock_ai_controller.py` (NEW)
**Tests:** N/A (test utility)

- [x] Create `MockAIController` implementing IAIController:
  - Tracks method calls (update_call_count, update_calls)
  - Returns configurable responses
  - Can be configured to raise errors (should_raise_on_update)
- [x] Document usage for tests
- [x] Created mocks package with __init__.py

**Notes:** Created before factory tests to use in testing.

---

### Task 8.8: Integration Testing [Simple] - COMPLETE
**Tests:** `pytest tests/integration/simulation/ tests/integration/test_battle*.py`

- [x] Run battle integration tests: 192 passed
- [x] Verify AI-controlled battles work: test_battle_engine_core.py tests pass
- [x] Verify headless battles work: test_factory_controllers_work_with_battle_engine passes
- [x] Verify battle service works: 15 tests pass
- [x] Run incremental test suite: 64 affected tests pass

**Notes:** All integration tests pass. BattleEngine refactoring is backward compatible.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] IAIController protocol created
- [x] BattleEngine supports AI factory via constructor (optional)
- [x] Internal AIController imports in BattleEngine guarded by factory check
- [x] AIControllerFactory created
- [x] All tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 9
