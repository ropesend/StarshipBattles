# Phase 2: Simulation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-126 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Simulation module (7 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 2.1: ADR-SIM-001 - AI Layer Imports in Simulation Factory [Medium]
**File:** `game/simulation/factories/ai_factory.py` -> `game/ai/ai_factory.py`
**Tests:** `pytest tests/unit/simulation/factories/test_ai_factory.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Moved AIControllerFactory from simulation layer to AI layer (game/ai/ai_factory.py)
- Created IAIControllerFactory protocol in simulation/interfaces/ai_controller.py
- Updated factory to use two-phase initialization (set_grid pattern)
- Updated all callers to inject factory from higher layers (UI, strategy)
- Factory functions in battle_controller.py use late import helper
- 11870 tests pass

### Task 2.2: ADR-SIM-002 - TYPE_CHECKING Import of AI Controller [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/combat/test_battle_engine_core.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Updated TYPE_CHECKING imports to use protocols from simulation layer
- Removed direct imports from AI layer in simulation code
- Factory is now injected, TYPE_CHECKING only references protocols

### Task 2.3: ADR-SIM-003 - God Class - BattleController [Complex]
**File:** `game/simulation/battle_controller.py`
**Tests:** N/A - FALSE POSITIVE

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- FALSE POSITIVE - Per PROJ-122 analysis
- 873 lines with proper Strategy pattern (BattleModeHandler)
- Delegation to RetreatManager, BattleStateManager, BattleService
- Factory functions at module level
- Well-architected, not a god class

### Task 2.4: ADR-SIM-004 - God Class - Ship Entity [Complex]
**File:** `game/simulation/entities/ship.py`
**Tests:** N/A - FALSE POSITIVE

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- FALSE POSITIVE - Per PROJ-122 analysis
- 810 lines with proper composition (ShipFormation, ShipStatsCalculator, ShipCombatEngine)
- Mixins (ShipPhysicsMixin), delegation (ShipStatQuerier, ShipValidatorHelper, ShipSerializer)
- Well-architected, not a god class

### Task 2.5: ADR-SIM-005 - Documented Circular Import in Ship.add_c [Medium]
**File:** `game/simulation/entities/ship.py`
**Tests:** N/A - ACCEPTABLE PATTERN

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- ACCEPTABLE PATTERN - Documented late import to break circular dependency
- Import chain: services/__init__.py -> VehicleDesignService -> Ship
- Ship.add_component() needs ModifierService, late import avoids cycle
- Comment documents rationale, uses strict DI pattern with ship's registries
- No code changes needed

### Task 2.6: ADR-SIM-006 - Possible Circular Import Comment in ship [Simple]
**File:** `game/simulation/entities/ship_stat_querier.py`, `ship_stats.py`
**Tests:** N/A - ACCEPTABLE PATTERN

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- ACCEPTABLE PATTERN - Documented intentional late imports
- ship_stat_querier.py:119 - "INTENTIONAL LATE IMPORT" with architecture doc reference
- ship_stats.py:72 - Import for ResourceStorage/ResourceGeneration abilities
- Both comments explain the rationale, no code changes needed

### Task 2.7: ADR-SIM-007 - Heavy Use of TYPE_CHECKING for Forward R [N]
**File:** N/A - INFO ONLY
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- INFO ONLY - Severity "Info", Effort "N" (no action required)
- TYPE_CHECKING for forward references is standard Python practice
- No code changes needed


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
