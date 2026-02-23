# PROJ-156: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** `2026-02-16_105410_general_test-suite-cleanup-v3`
- **Validation:** `findings/validation_3_ai_refactor.md`
- **Scope:** AI, Research, Combat, Builder, Systems test directories
- **Date:** 2026-02-16

## Initial Analysis

### Baseline
- **12,788 tests passing**, 145 failed (pre-existing UI failures), 2 skipped, 2 warnings
- Pre-existing failures are ALL in: `test_build_queue_controller.py`, `test_cargo_quick_dialog_issuance.py`, `test_strategy_input_handler_*.py`, `test_column_manager.py`, `test_transfer_dialog.py`, `test_turn_execution.py`
- None of these overlap with files being cleaned up

### Path Corrections from Original Review
The validation review referenced some incorrect paths. Corrected paths:

| Review Said | Actual Path |
|-------------|-------------|
| `tests/unit/ai/formation_prediction/test_ai_behaviors.py` | `tests/unit/ai/test_ai_behaviors.py` |
| `tests/unit/engine/test_spatial_extended.py` | `tests/unit/systems/test_spatial_extended.py` |
| `tests/unit/engine/test_spatial.py` | `tests/unit/systems/test_spatial.py` |
| `tests/unit/engine/test_collision_system.py` | `tests/unit/systems/test_collision_system.py` |
| `tests/unit/engine/test_beam_ramming.py` | `tests/unit/engine/collision_edge_cases/test_beam_ramming.py` |
| `test_target_evaluator_rules.py` (in target_evaluator/) | `tests/unit/ai/test_target_evaluator_rules.py` (in ai/) |
| `test_target_evaluator_edge_cases.py` (in target_evaluator/) | `tests/unit/ai/test_target_evaluator_edge_cases.py` (in ai/) |

### TestLayoutConstants Locations
Two instances found (both confirmed trivial):
1. `tests/unit/research/research_scene/test_initialization.py` lines 264-287 (4 tests: `> 0` checks)
2. `tests/unit/ui/panels/test_empire_treasury_panel.py` lines 322-343 (4 tests: range checks)

## Merge Details

### Pair 1: AI Behaviors
- **Source:** `tests/unit/ai/test_ai_behaviors.py` (~341 lines)
- **Target:** `tests/unit/ai/test_behavior_units.py` (735 lines)
- **Vector2 concern:** Source uses `pygame.math.Vector2`, target uses `game.core.math.Vector2`. Must adapt.
- **Fixture concern:** Formation tests in source need master-ship fixtures not present in target.
- **7 unique tests to merge:**
  - `test_opt_dist_calculation` - exact opt_dist = weapon_range * multiplier + stop_dist
  - `test_opt_dist_min_clamp` - opt_dist clamped to minimum 150
  - `test_branching_kite_maintain` - exact kite-away vector math
  - `test_target_pos_fixed_rotation` - fixed rotation ignores master angle
  - `test_target_pos_relative_rotation` - relative rotation offset rotated by master angle
  - `test_drift_logic_correction` - spring correction drift logic
  - `test_velocity_sync` - throttle sync between ship and master

### Pair 2: Evaluation Rules
- **Source:** `tests/unit/ai/target_evaluator/test_evaluation_rules.py` (598 lines)
- **Target:** `tests/unit/ai/test_target_evaluator_rules.py` (752 lines)
- **CRITICAL:** `TestSpeedRulesFactorBased` class (7 tests) documents a **known bug** where `slowest` with `factor` (weight=0) produces inverted results. Comments must be preserved.
- **~11 unique tests to merge:**
  - Full `TestSpeedRulesFactorBased` class (7 tests documenting speed factor bug)
  - `test_nearest_zero_distance` - zero distance edge case
  - `test_largest_same_as_mass` - mass/largest equivalence
  - `test_missing_mass_uses_default` - missing attribute handling
  - `TestStrengthRules` (2 tests) - strongest/weakest aliases

### Pair 3: Evaluation Integration
- **Source:** `tests/unit/ai/target_evaluator/test_evaluation_integration.py` (285 lines)
- **Target:** `tests/unit/ai/test_target_evaluator_edge_cases.py` (314 lines)
- **New import needed:** `from game.ai.combat_utils import get_hp_percent, is_in_pdc_arc`
- **~11 unique tests to merge:**
  - TestCustomStatHelpers (2 tests) - custom HP percent and PDC arc functions
  - TestDefaultStatHelpers (3 tests) - `get_hp_percent()` and `is_in_pdc_arc()` from combat_utils
  - TestThreatAssessment (2 tests) - realistic multi-rule scenarios
  - Edge case defaults (4 tests) - missing_weight, missing_factor, negative_weight, very_large_distance

### Pair 4: Controllable Adapter
- **Source 1:** `tests/unit/ai/controllable_interface/test_adapter_basics.py` (232 lines)
- **Source 2:** `tests/unit/ai/controllable_interface/test_adapter_methods.py` (262 lines)
- **Target:** `tests/unit/ai/test_controllable_adapter_edge_cases.py` (475 lines)
- **Keep untouched:** `tests/unit/ai/test_controllable_adapter.py` (ABC contract)
- **~7 unique tests to merge:**
  - `test_direct_attribute_access_raises_error` - validates no __getattr__ delegation
  - `test_direct_attribute_assignment_does_not_delegate` - assignment goes to adapter's __dict__
  - `test_adapter_get_turn_speed_returns_ship_turn_speed`
  - `test_adapter_get_acceleration_rate_returns_ship_acceleration_rate`
  - `test_adapter_get_is_thrusting_returns_ship_is_thrusting`
  - `test_adapter_get_turn_throttle_returns_ship_turn_throttle`
  - `test_adapter_set_formation_master_to_none`

### Pair 5: Spatial
- **Source:** `tests/unit/systems/test_spatial_extended.py` (157 lines)
- **Target:** `tests/unit/systems/test_spatial.py` (153 lines)
- Both import `game.engine.spatial.SpatialGrid`, similar MockObject patterns
- **5 unique tests:** empty_grid, same_cell, different_cells, negative_coords, cross-cell

### Pair 6: Collision System
- **Source:** `tests/unit/systems/test_collision_system.py` (393 lines)
- **Target:** `tests/unit/engine/collision_edge_cases/test_beam_ramming.py` (691 lines)
- **Fixture adaptation:** Source creates `CollisionSystem()` inline; target uses `collision_system` fixture from conftest.py
- **6 unique tests:** near_miss geometry, tangent_hit, target_behind_origin, origin_inside_target, ramming_logic (HP asymmetry), ramming_no_logger

## Dependencies & Risks

1. **Vector2 import mismatch** (Pairs 1, 2, 3) - Source files use `pygame.math.Vector2`, targets use `game.core.math.Vector2`. All migrated tests must use target's Vector2. **Mitigation:** Adapt during merge.

2. **Fixture incompatibility** (All pairs) - Source files often have their own conftest.py fixtures. Migrated tests must be adapted to target's fixture patterns. **Mitigation:** Read both source and target fixtures before each merge.

3. **Bug-documenting tests** (Pair 2) - `TestSpeedRulesFactorBased` documents a known bug. Loss would remove institutional knowledge. **Mitigation:** Merge LAST among Phase 3 tasks to ensure highest care.

4. **Directory cleanup** (Phase 4) - Deleting `controllable_interface/` after all its files are removed. Must confirm no other test files remain. **Mitigation:** Verify with `ls` before deletion.

5. **Lost tests from PROJ-157** (Pair 1/AI Behaviors) - PROJ-157 deleted `test_ai_behaviors.py` but only merged 4 of 7 unique tests. 3 KiteBehavior tests must be recovered from git history. **Mitigation:** Recover from `git show b1edd82b^:tests/unit/ai/test_ai_behaviors.py`. See recovery section below.

## PROJ-157 Overlap Assessment (added 2026-02-19)

PROJ-157 completed independently and overlapped significantly with PROJ-156:

### What PROJ-157 completed (verified against codebase):
- **Phase 1 (all):** All 9 dead test file deletions
- **Phase 2 (4 of 6):** Tasks 2.1–2.4 (stubs, empty classes, duplicate classes)
- **Phase 2 (missed):** Task 2.5 — both `TestLayoutConstants` classes still exist with trivial checks

### What PROJ-157 did NOT do:
- **Phase 3 merges:** None of the 6 merge-then-delete operations were performed (except partial Pair 3)
- **Phase 4 cleanup:** No directory cleanup performed

### Pair 3 Incomplete Merge (PROJ-157 commit b1edd82b):
PROJ-157 deleted `test_ai_behaviors.py` and merged 4 formation/drift tests into `TestFormationBehaviorMigrated` class in `test_behavior_units.py`. However, 3 KiteBehavior optimization tests were **not merged**:

**Lost tests (recover from git):**
```
git show b1edd82b^:tests/unit/ai/test_ai_behaviors.py
```

1. `test_opt_dist_calculation` (line 43) — Tests `opt_dist = weapon_range * multiplier + stop_dist`
2. `test_opt_dist_min_clamp` (line 61) — Tests `opt_dist` clamped to minimum 150
3. `test_branching_kite_maintain` (line 86) — Tests exact kite-away vector math when in maintain range

These belong in or near the existing `TestKiteBehavior` class in `test_behavior_units.py`. They test KiteBehavior's optimal distance calculation and kite-maintain branching — functionality not covered by any other test.

### Updated Unique Test Counts (from code review):
| Pair | Source Tests | Target Tests | Truly Unique in Source |
|------|-------------|--------------|----------------------|
| 1: Spatial | 13 | 11 | ~2 (rest are renamed duplicates) |
| 2: Collision | 12 | 21 | ~2 (target much more comprehensive) |
| 3: AI Behaviors | N/A (deleted) | 70+ | 3 LOST (recovery needed) |
| 4: Adapter | 39 | 51 | ~5 |
| 5: Eval Integration | 16 | 20 | ~12 |
| 6: Eval Rules | 44 | 58 | ~12 (incl. TestSpeedRulesFactorBased) |

### Unused Fixture Found:
`target_with_hp` fixture in `tests/unit/ai/target_evaluator/conftest.py` (lines 40-53) is defined but never used by any test file. Clean up in Phase 4 Task 4.2.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
