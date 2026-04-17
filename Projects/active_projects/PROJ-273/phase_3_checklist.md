# Phase 3: Migrate Strategy Compiler

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-273 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace the hand-rolled `stat_key=...` calls in `game/strategy/combat/spec_compiler.py` with registry-driven emission. Preserve exact behavior.

---

## Tasks

### Task 3.1: Inventory existing hardcoded emissions [Simple]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** N/A (read-only)

- [ ] Read lines 336-450 of `game/strategy/combat/spec_compiler.py`
- [ ] Document each `stat_key=...` emission site and the input DTO it maps from:
  - L353: storm hex → `shield_capacity_mult` (ShieldModifier equivalent)
  - L385: `FleetCombatModifiers.shield_mult` → `shield_capacity_mult`
  - L400: `FleetCombatModifiers.damage_mult` → `damage_mult`
  - L412: `FleetCombatModifiers.flat_shield_bonus` → `shield_bonus_add`
  - L444: generic case
- [ ] Confirm the list is complete (no other `stat_key=` literals in the file)

**Notes:**

### Task 3.2: Add import, write helper wrapper for FleetCombatModifiers [Medium]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/ -v`

- [ ] Add import: `from game.simulation.combat.ability_stat_registry import emit_entries_for_ability`
- [ ] Consider adding a small private helper `_emit_from_fleet_modifier_field(ability_class_name, value, *, owner_team, num_teams, source, stack_group)` that wraps `emit_entries_for_ability` for numeric inputs (since strategy's `FleetCombatModifiers` stores raw floats, not dict-shaped ability data)
- [ ] Write a unit test first that exercises the wrapper with each of the 3 field types

**Notes:**

### Task 3.3: Migrate `_entries_from_environmental_effects` [Medium]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler.py -v`

- [ ] Replace the hardcoded `stat_key="shield_capacity_mult"` construction at L353 with `emit_entries_for_ability("ShieldModifier", value, scope="enemy_sector", owner_team=..., num_teams=2, source=..., stack_group="storm_shield_interference")`
- [ ] Verify the emitted entries are identical to the current output (stat_key, operation, value, stack_group, source, applies_to_team_id)
- [ ] Run environmental-effects tests

**Notes:**

### Task 3.4: Migrate `_entries_from_fleet_combat_modifiers` [Complex]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler.py -v`

- [ ] Replace hardcoded emissions at L385 (`shield_mult`), L400 (`damage_mult`), L412 (`flat_shield_bonus`)
- [ ] Each becomes a call through the wrapper helper (Task 3.2) with the correct `stack_group` — `"team{N}_shield_mult"`, `"team{N}_damage_mult"`, `"team{N}_flat_shield"` as documented in `docs/systems/combat_simulation.md` line 434
- [ ] L444 (generic case): verify what ability this corresponds to, migrate accordingly
- [ ] Ensure `_NUM_TEAMS` value is passed correctly (strategy also has implicit 2-team assumption today — passed as literal `2`, documented in comment for PROJ-275 handoff)

**Notes:**

### Task 3.5: Strategy compiler full test suite [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/combat/ -n 12`

- [ ] All strategy combat tests pass
- [ ] No hardcoded `stat_key=...` literals remain in `game/strategy/combat/spec_compiler.py` (grep check: `grep -n 'stat_key=' game/strategy/combat/spec_compiler.py` should return zero lines)

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-273 3`
