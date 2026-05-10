# Phase 2: Simulation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-134 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Simulation module (8 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 2.1: LEG-SIM-001 - Empty Factory Module (Dead Package) [Simple]
**File:** `game/simulation/factories/__init__.py`
**Tests:** N/A (removal)

- [x] Investigate the issue at the specified location
- [x] Verified no code imports from this package
- [x] Delete the entire `game/simulation/factories/` directory
- [x] Verify: tests pass, no regressions

**Notes:** Package was empty with "kept for future use" comment. Violates project policy against dead code. Deleted.

### Task 2.2: LEG-SIM-002 - Incomplete Migration - StrategyBattleModeHandler [Medium]
**File:** `game/simulation/combat/battle_mode_handler.py:212-226`
**Tests:** N/A (documentation fix)

- [x] Investigate the issue at the specified location
- [x] Analysis: apply_results() built dicts but never used them; referenced non-existent PROJ-41
- [x] Strategy layer (ConflictResolutionEngine) handles fleet updates directly
- [x] Updated apply_results() to be explicit no-op with clear documentation
- [x] Updated BattleController._apply_results_to_fleet() similarly
- [x] Verify: tests pass (updated test expectations)

**Notes:** Fleet updates are handled by ConflictResolutionEngine calling Fleet.update_from_battle_results(). The mode handler's apply_results() is a no-op for interface compliance.

### Task 2.3: LEG-SIM-004 - Hasattr Checks for ability_instances on [Simple]
**Files:**
- `game/simulation/entities/ability_aggregator.py:101,206`
- `game/simulation/entities/ship_stats.py:281`
- `game/simulation/entities/combat_endurance.py:42`
**Tests:** Existing tests

- [x] Investigate the issue at the specified location
- [x] Verified ability_instances is always initialized in Component.__init__
- [x] Changed hasattr to getattr with guard comment for test mocks
- [x] Verify: tests pass, no regressions

**Notes:** Kept getattr guards because test mocks may not have ability_instances. Added clear comment explaining the guard is for non-Component objects.

### Task 2.4: LEG-SIM-003 - Defensive getattr/hasattr Usage on Core [Medium]
**Files:**
- `game/simulation/battle_state.py:212-225`
- `game/simulation/combat/weapon_firing_system.py:63,177,250,277`
- `game/simulation/combat/damage_calculator.py:47,54`
- `game/simulation/combat/targeting_system.py` (various)
**Tests:** Existing tests

- [x] Investigate the issue at the specified location
- [x] battle_state.py: Removed unnecessary getattr (all attrs exist on Ship)
- [x] weapon_firing_system.py: Removed getattr for is_derelict, max_targets; fixed bug using projectile_hp instead of missile_hp
- [x] damage_calculator.py: Removed getattr for emissive_armor, crystalline_armor
- [x] targeting_system.py: KEPT getattr - handles polymorphic targets (Ship/Projectile)
- [x] Verify: tests pass, no regressions (updated MockShip with missing attrs)

**Notes:** Most getattr patterns were unnecessary for Ship attributes that always exist. targeting_system.py patterns are intentional for polymorphic target handling. Fixed a bug: missile_hp -> projectile_hp.

### Task 2.5: LEG-SIM-005 - V1 Modifier Format Check Still Present [Simple]
**File:** `game/simulation/components/modifier_schema.py:36,50`
**Tests:** `tests/unit/simulation/components/test_modifier_schema.py`

- [x] Investigate the issue at the specified location
- [x] Verified no V1 modifiers exist in data/modifiers.json
- [x] Removed V1 format detection and ValueError raise
- [x] Simplified is_v2_format() to just check if effects is a list
- [x] Updated tests to expect False return instead of ValueError
- [x] Verify: tests pass, no regressions

**Notes:** All modifiers are V2 format. Dead validation code removed.

### Task 2.6: LEG-SIM-006 - Projectile Type String Conversion Pattern [Simple]
**File:** `game/simulation/entities/projectile.py:47-53`
**Tests:** `tests/unit/simulation/entities/test_projectile.py`

- [x] Investigate the issue at the specified location
- [x] String-to-AttackType conversion needed for deserialization (battle state)
- [x] Removed fallback "keep as string with warning" - invalid types now raise ValueError
- [x] Removed unused log_warning import
- [x] Updated test to expect ValueError for unknown types
- [x] Verify: tests pass, no regressions

**Notes:** Tightened validation - invalid projectile types now fail fast.

### Task 2.7: LEG-SIM-007 - Legacy Comment References (PROJ-106 Legacy) [Simple]
**File:** `game/simulation/systems/battle_engine.py:270,322,470`
**Tests:** N/A (comment cleanup)

- [x] Investigate the issue at the specified location
- [x] Removed "PROJ-106: Legacy path removed" comments
- [x] Error messages still explain requirements without referencing legacy behavior
- [x] Verify: tests pass, no regressions

**Notes:** Comments referencing removed legacy behavior cleaned up.

### Task 2.8: LEG-SIM-008 - Stale Docstring Reference to Legacy Behavior [Simple]
**File:** `game/simulation/systems/battle_engine.py:177-178`
**Tests:** N/A (docstring fix)

- [x] Investigate the issue at the specified location
- [x] Updated docstring for ai_factory parameter
- [x] Removed "If None, imports from game.ai directly (legacy behavior)" text
- [x] Now accurately states ai_factory is required unless ai_controllers provided
- [x] Verify: tests pass, no regressions

**Notes:** Docstring now reflects current behavior.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
