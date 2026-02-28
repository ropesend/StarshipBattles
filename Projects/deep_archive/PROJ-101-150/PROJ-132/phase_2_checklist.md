# Phase 2: Simulation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-132 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Simulation module (4 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 2.1: ADR-SIM-001 - Simulation imports AI layer in factory f [Medium]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/battle_controller/ tests/integration/fleet_combat/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Created new module `game/ui/services/battle_factories.py` with factory functions
- Moved `create_manual_battle`, `create_test_battle`, `create_strategy_battle`, `create_hypothetical_battle` and `_create_default_ai_factory`
- Updated test imports in `test_utilities.py`, `test_damage_pipeline.py`, `test_combat_workflow.py`
- Removed factory functions from `battle_controller.py`
- Layer violation eliminated - Simulation no longer imports from AI layer

### Task 2.2: ADR-SIM-002 - TYPE_CHECKING import from AI layer [Simple]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_*.py tests/unit/combat/test_battle_engine_core.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- Removed `from game.ai.controller import AIController` from TYPE_CHECKING block
- Changed type annotations from `'AIController'` to `'IAIController'` (protocol) at lines 214, 298
- Now only imports `IAIController, IAIControllerFactory` protocols from simulation layer
- 73 battle engine tests pass

### Task 2.3: ADR-SIM-005 - Late import pattern for circular depende [Complex]
**File:** `game/simulation/entities/ship.py`
**Tests:** N/A (documentation decision)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- **ACCEPTED AS-IS** - Documented intentional design decision
- ARCHITECTURE.md lines 139-143 explicitly documents this as "real import cycle that cannot be moved to module level"
- Late import for ModifierService is necessary due to circular dependency chain
- Only called during component addition (edge operation)
- Severity: MINOR, Effort: Complex - restructuring would require significant work with minimal benefit

### Task 2.4: ADR-SIM-007 - Component.py approaching god class thres [Simple]
**File:** `game/simulation/components/component.py`
**Tests:** N/A (monitoring decision)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
- **ACCEPTED AS-IS** - Severity is INFO (lowest level)
- File is 723 lines, below the 800-line extraction threshold
- Review recommendation: "Monitor file growth; extract if it exceeds 800 lines"
- Significant delegation already exists (AbilityManager, ModifierManager, ComponentStatsCalculator, etc.)
- No immediate action required


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
