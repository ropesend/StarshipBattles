# Phase 3: SHIELD_CAPACITY_MULT Stat Key

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-189 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add `shield_capacity_mult` to the modifier system so environmental effects and future modifiers can reduce shield capacity independently.

---

## Tasks

### Task 3.1: Add SHIELD_CAPACITY_MULT to StatKey enum [Simple]
**File:** `game/simulation/components/abilities/stat_keys.py`
**Tests:** `pytest tests/unit/simulation/components/`

- [ ] Add `SHIELD_CAPACITY_MULT = "shield_capacity_mult"` to StatKey enum in the multiplicative stats section (after `CAPACITY_MULT`, ~line 43)
- [ ] Verify `StatKey.get_default(StatKey.SHIELD_CAPACITY_MULT)` returns 1.0 (handled by default multiplicative branch automatically)
- [ ] Verify `StatKey.create_default_stats_dict()` includes `'shield_capacity_mult': 1.0`
- [ ] Run existing stat key tests

**Notes:**

### Task 3.2: Add shield_capacity_mult to modifier defaults [Simple]
**File:** `game/simulation/components/modifiers.py`
**Tests:** `pytest tests/unit/simulation/components/`

- [ ] Locate `get_default_stat_multipliers()` function
- [ ] Add `'shield_capacity_mult': 1.0` to the returned dict (in the multiplicative section)
- [ ] Run full test suite to verify no regressions: `pytest tests/ --testmon`

**Notes:**

### Task 3.3: Wire ShieldProjection to shield_capacity_mult [Medium]
**File:** `game/simulation/components/abilities/defense.py`
**Tests:** `pytest tests/unit/simulation/components/abilities/`

- [ ] Read current ShieldProjection implementation to understand STAT_BINDINGS and `recalculate()` pattern
- [ ] Add `AbilityStatBinding(StatKey.SHIELD_CAPACITY_MULT, ...)` to ShieldProjection.STAT_BINDINGS (exact attribute name depends on current implementation - may be 'capacity', 'shield_capacity', or 'value')
- [ ] If SimpleMultiplierAbility only supports one stat_key, may need to override `recalculate()` to apply both CAPACITY_MULT and SHIELD_CAPACITY_MULT
- [ ] Write test: ShieldProjection with `shield_capacity_mult=0.5` in component stats produces half shield capacity
- [ ] Write test: Both `capacity_mult=1.5` and `shield_capacity_mult=0.5` multiply together correctly (1.5 * 0.5 = 0.75x base)
- [ ] Write test: `shield_capacity_mult=1.0` (default/no storm) has no effect on existing shield values
- [ ] Run all existing shield/defense tests to verify no regressions

**Notes:** The exact integration depends on ShieldProjection's current implementation. Read the file first. The key is that setting `component.stats['shield_capacity_mult'] = 0.5` should result in halved shield capacity.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/ --testmon`
- [ ] Existing shield behavior unchanged when shield_capacity_mult is at default 1.0
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
