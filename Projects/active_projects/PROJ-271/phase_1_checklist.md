# Phase 1: `SHIELD_BONUS_ADD` additive stat_key + `AbilityStatBinding`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Risk:** LOW (follows existing `ACCURACY_ADD` precedent)
**Depends On:** None
**Objective:** Add the infrastructure needed to apply additive shield bonuses to ships via the `FleetAuraManager` modifier pipeline. Ship `max_shields` gets an additive bonus (not multiplicative) when a modifier of `stat_key="shield_bonus_add"` is in the `ModifierStack`.

---

## Tasks

### Task 1.1: Add `SHIELD_BONUS_ADD` to `StatKey` enum [Simple]
**File:** `game/simulation/components/abilities/stat_keys.py`
**Tests:** `pytest tests/unit/modifiers/test_stat_key.py --tb=short`

- [ ] Write failing test asserting `StatKey.SHIELD_BONUS_ADD` exists with `operation=ADD`, `target_attribute="max_shields"`, `base_attribute="base_max_shields"`
- [ ] Run — fails (enum entry missing)
- [ ] Add the enum entry (copy shape of `ACCURACY_ADD` which exists at `stat_keys.py`)
- [ ] Run — passes
- [ ] Audit existing `StatKey` entries for naming consistency — ADD-operation entries use the `_ADD` suffix and the string value `"shield_bonus_add"`

**Notes:** [Filled during implementation]

---

### Task 1.2: Add `AbilityStatBinding` for shield components [Medium]
**File:** `game/modifiers/ability_stat_binding.py` (or wherever bindings live — grep)
**Tests:** `pytest tests/unit/modifiers/test_ability_stat_binding.py --tb=short`

- [ ] Locate existing `ACCURACY_ADD` binding — it maps the stat_key onto weapon abilities. Copy the pattern for `SHIELD_BONUS_ADD` onto shield components (Shield, ShieldProjection, ShieldRegeneration?).
- [ ] Write failing test: a shield component with a `SHIELD_BONUS_ADD` entry in its modifier stack has `max_shields = base_max_shields + bonus_value`
- [ ] Run — fails
- [ ] Implement the binding
- [ ] Run — passes
- [ ] Verify: `FleetAuraManager._append_external_from_entry` picks up the stat_key (no placeholder warning logged)

**Notes:** [Filled during implementation]

---

### Task 1.3: `FleetAuraManager` pipeline end-to-end test [Medium]
**File:** `tests/unit/simulation/combat/test_fleet_aura_extended.py` (extend)
**Tests:** `pytest tests/unit/simulation/combat/test_fleet_aura_extended.py --tb=short`

- [ ] Write a test that builds a `ModifierStack` with a `SHIELD_BONUS_ADD` entry (value=50.0) targeting team 0, materializes a ship with `max_shields=100`, and asserts the ship's effective `max_shields` is `150` after `FleetAuraManager.initialize(ships, modifier_stack=stack)`
- [ ] Run — should pass if Tasks 1.1 + 1.2 are correct
- [ ] Test edge case: multiple entries stack additively (entry A +30 + entry B +20 → total +50)
- [ ] Test edge case: additive + multiplicative compose correctly (base 100 → +50 add then *2 mult = (100+50)*2 = 300, NOT 100*2+50 = 250) — verify pipeline ordering matches docs

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Unit tests for `SHIELD_BONUS_ADD` + binding + pipeline green
- [ ] `FleetAuraManager` no longer logs placeholder warning for `shield_bonus_add` (it logs only for truly unmapped stat_keys)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
