# Phase 3: SHIELD_CAPACITY_MULT Stat Key

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-189 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `shield_capacity_mult` to the modifier system so environmental effects and future modifiers can reduce shield capacity independently.

---

## Tasks

### Task 3.1: Add SHIELD_CAPACITY_MULT to StatKey enum [Simple]
**File:** `game/simulation/components/abilities/stat_keys.py`
**Tests:** `pytest tests/unit/simulation/components/`

- [x] Add `SHIELD_CAPACITY_MULT = "shield_capacity_mult"` to StatKey enum in the multiplicative stats section (after `CAPACITY_MULT`, ~line 43)
- [x] Verify `StatKey.get_default(StatKey.SHIELD_CAPACITY_MULT)` returns 1.0 (handled by default multiplicative branch automatically)
- [x] Verify `StatKey.create_default_stats_dict()` includes `'shield_capacity_mult': 1.0`
- [x] Run existing stat key tests

**Notes:** Added after CAPACITY_MULT at line 44. Default returns 1.0 as expected.

### Task 3.2: Add shield_capacity_mult to modifier defaults [Simple]
**File:** `game/simulation/components/modifiers.py`
**Tests:** `pytest tests/unit/simulation/components/`

- [x] Locate `get_default_stat_multipliers()` function
- [x] Add `'shield_capacity_mult': 1.0` to the returned dict (in the multiplicative section)
- [x] Run full test suite to verify no regressions: `pytest tests/ --testmon`

**Notes:** Added after capacity_mult at line 142.

### Task 3.3: Wire ShieldProjection to shield_capacity_mult [Medium]
**File:** `game/simulation/components/abilities/defense.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/`

- [x] Read current ShieldProjection implementation to understand STAT_BINDINGS and `recalculate()` pattern
- [x] Add `AbilityStatBinding(StatKey.SHIELD_CAPACITY_MULT, ...)` to ShieldProjection.STAT_BINDINGS (exact attribute name depends on current implementation - may be 'capacity', 'shield_capacity', or 'value')
- [x] If SimpleMultiplierAbility only supports one stat_key, may need to override `recalculate()` to apply both CAPACITY_MULT and SHIELD_CAPACITY_MULT
- [x] Write test: ShieldProjection with `shield_capacity_mult=0.5` in component stats produces half shield capacity
- [x] Write test: Both `capacity_mult=1.5` and `shield_capacity_mult=0.5` multiply together correctly (1.5 * 0.5 = 0.75x base)
- [x] Write test: `shield_capacity_mult=1.0` (default/no storm) has no effect on existing shield values
- [x] Run all existing shield/defense tests to verify no regressions

**Notes:** Added second STAT_BINDING for SHIELD_CAPACITY_MULT. Overrode recalculate() to multiply both capacity_mult and shield_capacity_mult. Added 4 new tests. Updated integration test for consumed stats (now expects 2).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All tests pass: `pytest tests/ --testmon`
- [x] Existing shield behavior unchanged when shield_capacity_mult is at default 1.0
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
