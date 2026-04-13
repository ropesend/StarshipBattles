# Phase 2: Both spec compilers emit real stat_keys for all remaining placeholder entries

> **SCOPE EXTENDED 2026-04-12:** Originally just `flat_shield_bonus` on the
> strategy compiler. PROJ-270 Phase 9 audit surfaced that the Battle Setup
> compiler (`game/ui/screens/battle_setup/spec_compiler.py::_complex_entries`)
> also emits `stat_key="placeholder"` for EVERY complex toggle (shield booster,
> damage booster, suppressors, etc.). Phase 2 now covers both compilers.


> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Risk:** LOW (follows Track A Phase 6.2 pattern from PROJ-270)
**Depends On:** Phase 1 (needs `SHIELD_BONUS_ADD` stat_key registered)
**Objective:** Strategy compiler emits `ModifierEntry(stat_key="shield_bonus_add", value=planet.modifiers.flat_shield_bonus, operation="add")` instead of the current `stat_key="placeholder"` stub. Visible effect: planets with a flat-shield-bonus aura actually buff the friendly fleet's ship `max_shields` in combat.

---

## Tasks

### Task 2.1: Replace placeholder entry with real stat_key [Simple]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/ --tb=short`

- [ ] Locate the current `flat_shield_bonus` emission in `_entries_from_fleet_combat_modifiers` (or wherever the placeholder comment from PROJ-270 Phase 6.2 cites PROJ-271)
- [ ] Write failing test in `tests/unit/strategy/combat/test_spec_compiler.py` asserting the compiler emits a `ModifierEntry` with `stat_key="shield_bonus_add"` when a fleet modifier source has `flat_shield_bonus=50`
- [ ] Run — fails (still placeholder)
- [ ] Replace the placeholder with `_real_entry(stat_key="shield_bonus_add", value=modifiers.flat_shield_bonus, operation="add")` using the helper added in PROJ-270 Phase 6.1
- [ ] Remove the "PROJ-271 deferred" comment
- [ ] Run — passes

**Notes:** [Filled during implementation]

---

### Task 2.2: End-to-end compiler → pipeline test [Medium]
**File:** `tests/unit/strategy/adapters/test_simulation_adapter.py` (extend) or a new fixture test
**Tests:** Targeted pytest run

- [ ] Build a strategy scenario with a planet carrying `flat_shield_bonus=75` on its combat modifiers aura
- [ ] Resolve via `build_strategy_battle_spec` and confirm the resulting `spec.modifier_stack` has a `ModifierEntry` with `stat_key="shield_bonus_add"` and `value=75`
- [ ] Separately assert the `FleetAuraManager` pipeline correctly lifts a base-100 shield to an effective-175 shield when this modifier is applied to a ship

**Notes:** [Filled during implementation]

---

### Task 2.3: Regression guard in `test_unified_entry_guard.py` [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`

- [ ] Add a `test_flat_shield_bonus_emits_real_stat_key` test to the existing `TestNoPlaceholderStatKeyInStrategyCompiler` class — same shape as the storm + fleet_mult guards from PROJ-270 Phase 6.1/6.2
- [ ] Assertion: `stat_key != "placeholder"` for any compiler entry whose source references `flat_shield_bonus`

**Notes:** [Filled during implementation]

---

### Task 2.4: Battle Setup complex toggles mapping [Medium] — from PROJ-270 Task 6.3/9.6
**File:** `game/ui/screens/battle_setup/spec_compiler.py:260-296`
**Tests:** `pytest tests/unit/ui/battle_setup/test_spec_compiler.py --tb=short`

- [ ] Audit [data/modifiers.json](../../../data/modifiers.json) — extract the effect mapping per complex design_id
- [ ] Replace `_complex_entries` placeholder emission with a lookup: `design_id → (stat_key, value, operation)` from `data/modifiers.json`
- [ ] Known candidate mappings:
  - Shield booster complex → `stat_key="shield_capacity_mult"`, `operation="multiply"`
  - Damage booster complex → `stat_key="damage_mult"`, `operation="multiply"`
  - Flat shield bonus complex → `stat_key="shield_bonus_add"` (Phase 1's new stat_key), `operation="add"`
  - Suppressor complex → opponent-team routing (see Phase 3)
- [ ] Extend `TestNoPlaceholderStatKeyInStrategyCompiler` guard to also scan the Battle Setup compiler

**Notes:** Phase 9 of PROJ-270 unblocked this work by making the pipeline actually consume stat_keys. Before Phase 9, mapping would have been wasted effort because the values never reached ship stats.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Strategy tests green
- [ ] Placeholder-stat_key regression guard extended to include `flat_shield_bonus`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
