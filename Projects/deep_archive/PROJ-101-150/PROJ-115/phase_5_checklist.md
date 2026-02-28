# Phase 5: Other

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-115 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings not mapped to a specific shard
**Priority:** Normal

---

## Tasks

### Task 5.1: UNK-01 - Physics formula duplication between Ship
- [x] Investigated: ALREADY FIXED - Physics formulas centralized in `physics_constants.py`

**Notes:** K_SPEED, K_THRUST, K_TURN constants are the single source of truth. Only 3 files import them.

### Task 5.2: UNK-10 - Two parallel ability aggregation systems
- [x] Investigated: ALREADY FIXED - Single system in `ability_aggregator.py`

**Notes:** `calculate_ability_totals()` is the unified aggregation system.

### Task 5.3: UNK-02 - Hull auto-equip code duplicated between __init__ and change_class
- [x] Investigated: ACCEPTABLE - 8 lines duplicated for distinct contexts (init vs class change)

**Notes:** Minimal duplication with different error handling needs.

### Task 5.4: UNK-03 - Modifier application duplicated between files
- [x] Investigated: FALSE POSITIVE - `apply_modifier_effects` is centralized in `modifiers.py`

**Notes:** Single function handles all modifier effects.

### Task 5.5: UNK-04 - Superweapon ability classes are nearly identical
- [x] Investigated: ACCEPTABLE - Intentional marker class pattern

**Notes:** Each superweapon is a distinct type for type-safe checking.

### Task 5.6: UNK-05 - Turret arc lookup logic duplicated in ModifierLogic and ModifierService
- [x] Investigated: ACCEPTABLE - Layer separation pattern

**Notes:** ModifierLogic (UI static wrapper) and ModifierService (simulation) serve different layers.

### Task 5.7: UNK-06 - BeamWeaponAbility.get_damage() duplicate
- [x] FIXED: Removed duplicate `get_damage()` from `BeamWeaponAbility`

**Notes:** `BeamWeaponAbility` now inherits `get_damage()` from parent `WeaponAbility`.

### Task 5.8: UNK-11 - Two independent formula evaluation systems
- [x] Investigated: ACCEPTABLE - Different purposes

**Notes:** `formula_system.py` (general) vs `modifier_effects.py` (modifier-specific with `param` context).

### Task 5.9: UNK-12 - Duplicate default stats dictionaries
- [x] Investigated: FALSE POSITIVE - Single source in `modifiers.py`

**Notes:** `get_default_stat_multipliers()` is the canonical source.

### Task 5.10: UNK-14 - WeaponAbility.__init__ formula parsing repetition
- [x] Investigated: ACCEPTABLE - Local repetition with field-specific variations

**Notes:** 6 occurrences but with different context handling per field.

### Task 5.11: UNK-15 - Missile type checking uses inconsistent methods
- [x] FIXED: Updated `battle_ui.py` to use `AttackType.MISSILE` enum

**Notes:** Fixed string literal check to use proper enum.

### Task 5.12: UNK-18 - Ship stat recalculation scattered across files
- [x] Investigated: FALSE POSITIVE - Intentional layer separation

**Notes:** Simulation vs Strategy calculators serve different purposes.

### Task 5.13: UNK-19 - Component data loading spread across 4 files
- [x] Investigated: FALSE POSITIVE - Centralized in `component.py`

**Notes:** Other files are consumers, not reimplementations.

### Task 5.14: UNK-07 - Ability constructor data-extraction pattern
- [x] Investigated: DEFERRED - Extraction attempted but caused test failures

**Notes:** Helper method caused edge case issues with formula strings. Reverted.

### Task 5.15: UNK-08 - Propulsion sync_data methods are near-identical
- [x] Investigated: DEFERRED - Part of Task 5.14, same issue

**Notes:** Would require Task 5.14 helper. Deferred.

### Task 5.16: UNK-09 - ShipValidatorHelper calls validate_design multiple places
- [x] Investigated: ACCEPTABLE - Each method returns different aspect of result

**Notes:** `check_validity()`, `get_validation_warnings()`, `get_missing_requirements()` are distinct facades.

### Task 5.17: UNK-13 - get_total_sensor_score and get_total_ecm_score patterns
- [x] Investigated: ACCEPTABLE - Intentional symmetry pattern

**Notes:** Two parallel methods, extracting helper would lose semantic clarity.

### Task 5.18: UNK-16 - Resource endurance calculations in combat
- [x] Investigated: FALSE POSITIVE - No duplicate calculations found

**Notes:** Core calculation unified in ComponentStatsCalculator.

### Task 5.19: UNK-17 - apply_modifier_effects partially duplicated
- [x] Investigated: ACCEPTABLE - Different semantics for targeted vs global effects

**Notes:** Helper vs inline have different key handling needs.

### Task 5.20: UNK-20 - Validation result handling duplicated
- [x] Investigated: ACCEPTABLE - Layer separation pattern

**Notes:** UI and Simulation facades serve different purposes.

### Task 5.21: UNK-21 - Persistence layer uses old Ship.from_dict
- [x] Investigated: ACCEPTABLE - Ship.from_dict is the public API

**Notes:** ShipIO correctly uses the factory method.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to audit

## Summary
- **2 FIXES**: Task 5.7 (BeamWeaponAbility.get_damage), Task 5.11 (missile enum)
- **11 FALSE POSITIVE/ALREADY FIXED**: Tasks 5.1, 5.2, 5.4, 5.9, 5.12, 5.13, 5.18
- **6 ACCEPTABLE**: Tasks 5.3, 5.5, 5.6, 5.8, 5.10, 5.16, 5.17, 5.19, 5.20, 5.21
- **2 DEFERRED**: Tasks 5.14, 5.15 (helper caused test failures)
