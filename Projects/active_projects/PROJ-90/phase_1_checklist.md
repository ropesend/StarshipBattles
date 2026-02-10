# Phase 1: Quick Wins — Dead Code & Config Extraction

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-90 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove dead code from ship.py and extract BattleConfig/BattleMode to its own module to eliminate a circular import workaround.

---

## Tasks

### Task 1.1: Remove no-op TYPE_CHECKING block [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/entities/ -v`

- [ ] Delete lines 14-15 (`if TYPE_CHECKING: pass  # GameRegistries imported above`)
- [ ] Verify: `pytest tests/unit/simulation/entities/ -v` passes

**Notes:**

---

### Task 1.2: Create battle_config.py [Medium]
**New File:** `game/simulation/battle_config.py`
**Source:** `game/simulation/battle_controller.py` lines 43-78
**Tests:** `pytest tests/unit/simulation/battle_controller/ tests/unit/simulation/combat/test_battle_mode_handlers.py -v`

- [ ] Create `game/simulation/battle_config.py` with:
  - `BattleMode` enum (currently `battle_controller.py` lines 43-48)
  - `BattleConfig` dataclass (currently `battle_controller.py` lines 51-78)
  - Required imports: `dataclass`, `field`, `Enum`, `Optional`, `Tuple`, `Any`, `TYPE_CHECKING`, `BattleEndMode`, `SimulationConstants`, and TYPE_CHECKING import of `CombatScenario`
- [ ] In `game/simulation/battle_controller.py`: Remove `BattleMode` and `BattleConfig` definitions. Add `from game.simulation.battle_config import BattleConfig, BattleMode`
- [ ] Verify: `python -c "from game.simulation.battle_controller import BattleController, BattleConfig, BattleMode; print('OK')"`

**Notes:**

---

### Task 1.3: Update battle_state_manager.py — Eliminate late import [Medium]
**File:** `game/simulation/managers/battle_state_manager.py`
**Tests:** `pytest tests/unit/simulation/ -v`

- [ ] Change TYPE_CHECKING import (line 17): `from game.simulation.battle_controller import BattleConfig` → `from game.simulation.battle_config import BattleConfig`
- [ ] Move to real top-level import: `from game.simulation.battle_config import BattleConfig, BattleMode` (no longer needs TYPE_CHECKING or late import)
- [ ] **Remove late import** at line 77: `from game.simulation.battle_controller import BattleConfig, BattleMode`
- [ ] Verify: `pytest tests/unit/simulation/battle_controller/ -v`

**Notes:**

---

### Task 1.4: Update battle_mode_handler.py — Eliminate late import [Medium]
**File:** `game/simulation/combat/battle_mode_handler.py`
**Tests:** `pytest tests/unit/simulation/combat/test_battle_mode_handlers.py -v`

- [ ] Split TYPE_CHECKING import (line 17): `BattleConfig, BattleMode` from `battle_config`; keep `BattleController` from `battle_controller`
- [ ] Move `BattleConfig, BattleMode` to real top-level import from `battle_config`
- [ ] **Remove late import** at line 290: `from game.simulation.battle_controller import BattleMode`
- [ ] Verify: `pytest tests/unit/simulation/combat/test_battle_mode_handlers.py -v`

**Notes:**

---

### Task 1.5: Update remaining importers [Simple]
**Files:** `simulation_adapter.py`, `battle_screen.py`, 5 test files
**Tests:** `pytest tests/ -n 12`

- [ ] `game/strategy/adapters/simulation_adapter.py` (lines 25-27): Split import — `BattleController` from `battle_controller`, `BattleConfig, BattleMode` from `battle_config`
- [ ] `game/ui/screens/battle_screen.py` (line 27): Split TYPE_CHECKING import — `BattleController` from `battle_controller`, `BattleConfig` from `battle_config`
- [ ] `tests/unit/simulation/battle_controller/conftest.py` (line 5): Import `BattleConfig, BattleMode` from `battle_config`
- [ ] `tests/unit/simulation/battle_controller/test_initialization.py` (line 5): Split import
- [ ] `tests/unit/simulation/battle_controller/test_execution.py` (line 5): Split import
- [ ] `tests/integration/fleet_combat/conftest.py` (line 9): Split import
- [ ] `tests/unit/simulation/combat/test_battle_mode_handlers.py` (lines 267, 276, 285, 294): Update 4 late imports from `battle_controller` → `battle_config`
- [ ] Verify: `pytest tests/ -n 12` — all 7353+ tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
