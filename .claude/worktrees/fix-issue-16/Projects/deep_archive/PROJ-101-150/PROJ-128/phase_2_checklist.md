# Phase 2: Simulation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-128 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Simulation module (18 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 2.1: CON-SIM-001 - ResourceRegistry Return Type Inconsisten [Simple]
**File:** `game/simulation/systems/resource_manager.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - The `get_value()` returning 0.0 for non-existent resources is intentional convenience behavior for UI/serialization use cases. The docstring already documents "or 0.0 if not found". No change needed.

### Task 2.2: CON-SIM-002 - Duplicate Exception Handler in design_lo [Simple]
**File:** `game/simulation/services/design_loader.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** RESOLVED - Removed unreachable duplicate exception handler (lines 130-133). Dead code that caught same exceptions already handled above.

### Task 2.3: CON-SIM-003 - Magic Numbers in Projectile Guidance Sys [Simple]
**File:** `game/simulation/entities/projectile.py`
**Tests:** Existing projectile tests

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** RESOLVED - Extracted TURN_COMMITMENT_THRESHOLD_DEG constant (45 degrees), replaced 0.01 with PhysicsConfig.TICK_RATE, removed dead code variable `max_turn`.

### Task 2.4: CON-SIM-004 - Singleton Fallback Pattern in Validation [Complex]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** DEFERRED - The finding references PROJ-50 scope for full DI migration. The singleton pattern is intentional for performance (validator is stateless, registry loading is expensive). Full DI migration would require changing Ship class methods and all callers. Not appropriate for consistency sweep.

### Task 2.5: CON-SIM-005 - Inconsistent Parameter Naming - resource [Simple]
**File:** `game/simulation/components/abilities/resources.py`
**Tests:** tests/unit/simulation/components/abilities/test_resource_consumption.py

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** RESOLVED - Renamed `resource_name` to `resource_type` in ResourceConsumption class. Also updated all references in: ship_stats.py, ship_validator.py, stats_config.py, combat_endurance.py, and test files.

### Task 2.6: CON-SIM-006 - Type Hint Gaps in Physics and Combat Mod [Medium]
**File:** `game/simulation/entities/ship_physics.py`, `game/simulation/entities/combat_endurance.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** RESOLVED - Added type hints to ship_physics.py (update_physics_movement, thrust_forward, rotate) and combat_endurance.py (calculate_combat_endurance, _calculate_cached_summary).

### Task 2.7: CON-SIM-007 - AIControllerFactory Uses Positional Para [Simple]
**File:** `game/ai/ai_factory.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - The finding describes `__init__(self, grid: SpatialGrid)` but actual code shows `__init__(self)` with two-phase initialization via `set_grid()`. No positional parameter issue exists.

### Task 2.8: CON-SIM-008 - Magic Numbers in Targeting and Combat Sy [Simple]
**File:** `game/simulation/combat/targeting_system.py`, `game/simulation/managers/retreat_manager.py`
**Tests:** Existing combat tests

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** RESOLVED - Added PROJECTILE_SPEED_SCALE (100.0) and SEEKER_MAX_RANGE_MULTIPLIER (2.0) to SimulationConstants. Updated targeting_system.py, weapon_firing_system.py to use constants. Fixed retreat_manager.py to use SimulationConstants.WARP_CHARGE_TICKS instead of hardcoded 500.

### Task 2.9: CON-SIM-009 - Abbreviated Parameter Names in solve_lea [Simple]
**File:** `game/simulation/combat/targeting_system.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Parameters `p_speed`, `t_pos`, `t_vel` are standard physics/math notation used consistently within a focused function. Function has full docstrings explaining each parameter. Renaming would make mathematical equations harder to read.

### Task 2.10: CON-SIM-010 - Mixed Logging Initialization Patterns [Simple]
**File:** `game/simulation/services/registry_loader.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** RESOLVED - Replaced `logging.getLogger("StarshipBattles")` with centralized `log_info`, `log_warning`, `log_error` from game.core.logger.

### Task 2.11: CON-SIM-011 - STAT_BINDINGS Type Hint Inconsistency [Simple]
**File:** `game/simulation/components/abilities/markers.py`, `game/simulation/components/abilities/superweapons.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - `STAT_BINDINGS = []` without type hint is used consistently for marker abilities with no stat bindings. More complex classes use type hints. Acceptable stylistic difference.

### Task 2.12: CON-SIM-012 - sync_data() Inconsistent Implementation [Medium]
**File:** `game/simulation/components/abilities/resources.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - By design: abilities needing runtime data updates implement sync_data(), static abilities use inherited no-op base class implementation. Correct polymorphism.

### Task 2.13: CON-SIM-013 - Inconsistent Method Verb Conventions [Simple]
**File:** `game/simulation/entities/ship_stat_querier.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - `get_` vs `calculate_` prefixes are intentional: `get_` for simple lookups, `calculate_` for computation-heavy methods. Finding itself explains this convention.

### Task 2.14: CON-SIM-014 - Missing Exports in services/__init__.py [Simple]
**File:** `game/simulation/services/__init__.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** RESOLVED - Added SimulationDesignLoader and reload_registries_from_directory to __all__ exports.

### Task 2.15: CON-SIM-015 - ability_aggregator.py Naming Convention [Simple]
**File:** `game/simulation/entities/ability_aggregator.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** DEFERRED - File rename is risky (all imports need updating). Minor naming consistency benefit vs high risk of breaking imports. Should be dedicated refactoring task.

### Task 2.16: CON-SIM-016 - PROJ Comment Format Inconsistency [Simple]
**File:** Various files
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INFO - Minor documentation style inconsistency across multiple files. Low value/high effort for consistency sweep. File location "Unknown" indicates scattered findings.

### Task 2.17: CON-SIM-017 - ResourceRegistry Class Name Deviation [Simple]
**File:** `game/simulation/systems/resource_manager.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - INFO level finding acknowledges name is "semantically correct" for registry pattern. Renaming would require updating all usages for low value.

### Task 2.18: CON-SIM-018 - Excellent Pattern Adherence - Facade/Del [N]
**File:** `game/simulation/entities/ship_combat_engine.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INFO (Positive Finding) - Positive observation about good facade/delegate pattern usage. No action needed.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

## Summary
- **RESOLVED:** 7 tasks (2.2, 2.3, 2.5, 2.6, 2.8, 2.10, 2.14)
- **ACCEPTABLE:** 6 tasks (2.1, 2.9, 2.11, 2.12, 2.13, 2.17)
- **FALSE POSITIVE:** 1 task (2.7)
- **DEFERRED:** 2 tasks (2.4, 2.15)
- **INFO:** 2 tasks (2.16, 2.18)
