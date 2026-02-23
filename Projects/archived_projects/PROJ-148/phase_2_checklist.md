# Phase 2: Simulation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-148 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Simulation module (7 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 2.1: DUP-SIM-001 - Ability Pattern Boilerplate Duplication [Medium]
**File:** `game/simulation/components/abilities/`
**Tests:** N/A - No code changes

- [x] Investigate the issue at the specified location
- [x] Document as acceptable pattern
- [x] Verify: no action needed

**Notes:** DOCUMENTED AS ACCEPTABLE - Template Method Pattern. Each ability subclass (ShieldProjection, WeaponAbility, CombatPropulsion, etc.) implements the same interface but with unique STAT_BINDINGS, get_ui_rows(), recalculate() logic. This enables polymorphism - abilities are interchangeable via the base class interface. Not duplication.

### Task 2.2: DUP-SIM-002 - Formula Evaluation Pattern Duplication [Simple]
**File:** `game/simulation/formula_system.py`
**Tests:** N/A - No code changes

- [x] Investigate the issue at the specified location
- [x] Document as acceptable pattern
- [x] Verify: already centralized

**Notes:** ALREADY CENTRALIZED - formula_system.py provides safe_evaluate_math_formula() and evaluate_math_formula() which are correctly imported and used by weapons.py and component.py. This is proper code reuse, not duplication.

### Task 2.3: DUP-SIM-003 - Resource Type Handling Duplication [Medium]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** N/A - No code changes

- [x] Investigate the issue at the specified location
- [x] Document as acceptable pattern
- [x] Verify: minimal switch logic

**Notes:** DOCUMENTED AS ACCEPTABLE - _aggregate_resource_abilities() handles ResourceType.FUEL, AMMO, ENERGY with ~5 lines per type. This is minimal switch-case logic that's clear and easy to extend. Abstracting to a loop-over-mapping would add complexity without proportional benefit.

### Task 2.4: DUP-SIM-004 - Validation Pattern Repetition in Loaders [Medium]
**File:** `game/simulation/components/component.py`
**Tests:** N/A - No code changes

- [x] Investigate the issue at the specified location
- [x] Document as acceptable pattern
- [x] Verify: consistent error handling

**Notes:** DOCUMENTED AS ACCEPTABLE - load_components_data() and load_modifiers_data() share similar try/except patterns. Each loader handles its own schema-specific errors appropriately. Consistency aids maintainability without introducing unnecessary abstraction.

### Task 2.5: DUP-SIM-005 - Target Validation Pattern Duplication [Simple]
**File:** `game/simulation/combat/targeting_system.py`
**Tests:** N/A - No code changes

- [x] Investigate the issue at the specified location
- [x] Document as acceptable pattern
- [x] Verify: context-specific validation

**Notes:** DOCUMENTED AS ACCEPTABLE - select_target() and find_valid_target() share ~4 lines of is_alive/team_id checks but operate in different contexts (simple selection vs. weapon-constrained selection). Extraction would over-complicate for minimal benefit.

### Task 2.6: DUP-SIM-007 - UI Row Generation Pattern [Medium]
**File:** `game/simulation/components/abilities/`
**Tests:** N/A - No code changes

- [x] Investigate the issue at the specified location
- [x] Document as acceptable pattern
- [x] Verify: polymorphic design

**Notes:** DOCUMENTED AS ACCEPTABLE - Each ability's get_ui_rows() returns unique labels, values, and color_hints specific to that ability type. This is required polymorphism - each ability knows how to represent itself in UI. A generic approach would lose semantic meaning.

### Task 2.7: DUP-SIM-008 - Physics Constants Duplication [Simple]
**File:** `game/simulation/physics_constants.py`
**Tests:** N/A - No code changes

- [x] Investigate the issue at the specified location
- [x] Document as already resolved
- [x] Verify: centralized

**Notes:** ALREADY CENTRALIZED - physics_constants.py is the single source of truth with explicit "DO NOT DUPLICATE" comment at the top. K_SPEED, K_THRUST, K_TURN are properly imported throughout the codebase.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
