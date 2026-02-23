# Phase 1: Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-118 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Foundation module (24 findings, 3 critical)
**Priority:** High

---

## Tasks

### Task 1.1: TCG-FND-001 - PhysicsBody.apply_force() and forward_ve [Simple]
**File:** `game/engine/physics.py`
**Tests:** `pytest tests/unit/systems/test_physics.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestApplyForceIntegration class with 4 tests for force->acceleration->velocity->position pipeline

### Task 1.2: TCG-FND-002 - AIController.update() Integration Path N [Medium]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestBehaviorContextMerging, TestFormationTargetSync, TestSecondaryTargetAcquisition classes

### Task 1.3: TCG-FND-003 - CollisionSystem.process_beam_attack() Hi [Medium]
**File:** `game/engine/collision.py`
**Tests:** `pytest tests/unit/engine/collision_edge_cases/test_beam_ramming.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestBeamRaycastingGeometry class with 5 tests for ray-sphere intersection math

### Task 1.4: TCG-FND-004 - SpatialGrid.query_radius() Boundary and [Simple]
**File:** `game/engine/spatial.py`
**Tests:** `pytest tests/unit/systems/test_spatial_edge_cases.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestSpatialGridBoundaryEdgeCases with 14 tests for cell boundaries, negative coords, zero radius

### Task 1.5: TCG-FND-005 - AIController._handle_formation_master() [Medium]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestHandleFormationMaster with 5 tests for turn limit and throttle calculation

### Task 1.6: TCG-FND-006 - AIController._check_formation_integrity( [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestCheckFormationIntegrity with 5 tests for propulsion damage and dropout logic

### Task 1.7: TCG-FND-007 - AIController.check_avoidance() Collision [Medium]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestCheckAvoidance with 8 tests for threat filtering and avoidance direction

### Task 1.8: TCG-FND-008 - AIController.navigate_to() Core Navigati [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/test_ai_controller_unit.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestNavigateTo with 10 tests for rotation, thrust, angle wrapping

### Task 1.9: TCG-FND-009 - ResearchService.process_turn() Leaky Buc [Simple]
**File:** `game/research/systems/research`
**Tests:** `pytest tests/unit/research/test_research_service.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestProcessTurnTechLevelsMutation, TestProcessTurnRNGFreshness, TestProcessTurnNodeOrdering with 6 tests

### Task 1.10: TCG-FND-010 - TechNode.get_effective_price() Only Part [Simple]
**File:** `game/research/data/tech_node.p`
**Tests:** `pytest tests/unit/research/test_tech_node.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestGetEffectivePriceParametrized with 65 parametrized tests for all 6 price curves

### Task 1.11: TCG-FND-011 - ResearchRenderer Test Coverage is Minima [Simple]
**File:** `game/research/ui/research_rend`
**Tests:** `pytest tests/unit/research/test_research_renderer.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestRendererIsVisible with 19 tests for viewport bounds and margin parameter

### Task 1.12: TCG-FND-012 - ResearchControlPanel.handle_event() Lack [Medium]
**File:** `game/research/ui/research_cont`
**Tests:** `pytest tests/unit/research/research_controls/test_handle_event.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Created new test file with 23 tests for slider events, auto-spread toggle, button routing

### Task 1.13: TCG-FND-024 - No Integration Test for AI Controller + [Medium]
**File:** `tests/integration/ai_strategy/`
**Tests:** `pytest tests/integration/ai_strategy/test_evaluation.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestAIControllerWithProductionData with 5 tests for real JSON strategy data

### Task 1.14: TCG-FND-013 - StrategyManager.resolve_strategy() Defau [Simple]
**File:** `game/ai/strategy_manager.py`
**Tests:** `pytest tests/unit/ai/test_strategy_system.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestResolveStrategyFallbackChain with 6 tests for policy fallback behavior

### Task 1.15: TCG-FND-014 - HexCoord Arithmetic with Non-HexCoord Ty [Simple]
**File:** `game/core/hex_math.py`
**Tests:** `pytest tests/unit/core/test_hex_math_core.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestHexCoordArithmeticTypeError with 10 tests for TypeError behavior

### Task 1.16: TCG-FND-015 - pixel_to_hex() Rounding Edge Cases at Ce [Simple]
**File:** `game/core/hex_math.py`
**Tests:** `pytest tests/unit/core/test_hex_math_core.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestPixelToHexRoundingEdgeCases with 8 tests including 10K+ coordinate stress test

### Task 1.17: TCG-FND-016 - RegistryManager.hydrate() Partial Resour [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/unit/core/registry/test_registry_operations.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestHydratePartialResources with 6 tests for None vs empty dict handling

### Task 1.18: TCG-FND-017 - combat_utils.is_in_pdc_arc() Missing Tes [Simple]
**File:** `game/ai/combat_utils.py`
**Tests:** `pytest tests/unit/ai/test_combat_utils.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestIsInPdcArcEdgeCases with 11 tests for arc boundaries, rotations, range

### Task 1.19: TCG-FND-018 - TargetEvaluator._eval_speed_rule() Slowe [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/test_evaluation_rules.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestSpeedRulesFactorBased with 6 tests documenting current (buggy) factor behavior

### Task 1.20: TCG-FND-019 - ResearchTracker.spread_rp_evenly() Does [Simple]
**File:** `game/research/data/research_tr`
**Tests:** `pytest tests/unit/research/test_research_tracker.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestSpreadRPEvenlyPrecomputedTechLevels with 7 tests for pre-computed path

### Task 1.21: TCG-FND-020 - Collision Edge Case Tests Use Heavy Mock [Complex]
**File:** `tests/unit/engine/collision_ed`
**Tests:** `pytest tests/unit/engine/collision_edge_cases/test_beam_ramming.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestCollisionIntegrationWithRealShip with 2 tests using real Ship objects

### Task 1.22: TCG-FND-021 - ScreenshotManager Tests Are Fragile Due [Simple]
**File:** `tests/unit/core/test_screensho`
**Tests:** `pytest tests/unit/ui/services/test_screenshot_manager.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added TestCaptureStep (3 tests), TestCaptureStrategyLayer (5 tests) for better coverage

### Task 1.23: TCG-FND-022 - StrategyMetadataService Uses Legacy Sing [Simple]
**File:** `game/core/strategy_metadata.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Already uses SingletonMeta - no changes needed

### Task 1.24: TCG-FND-023 - ErraticBehavior Uses `import random` Ins [Simple]
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/test_behavior_units.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Moved import random to module level (line 64), added TestErraticBehavior with 8 tests


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
