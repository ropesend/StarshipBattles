# Phase 3: Suppressor opponent-team routing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Risk:** MEDIUM (cross-team routing is a new pattern in the compiler)
**Depends On:** Phases 1 + 2 (friendly-team wiring proven first)
**Objective:** Modifiers that debuff opponents (e.g., a planet that imposes `-20% damage` on enemy ships in that hex — "suppressor" effect) route via `ModifierStack.per_team[opponent_team_id]` rather than `per_team[source_team_id]`. Spec compiler determines "who is the opponent" at compile time and targets the right team.

---

## Tasks

### Task 3.1: Identify suppressor source in planet/environmental data [Medium]
**File:** `game/strategy/combat/combat_modifier_collector.py` (or wherever planet auras are collected)
**Tests:** Read-only audit task

- [ ] Audit `FleetCombatModifiers` fields for any that semantically debuff opponents vs buff friendlies. Current suspect fields: any negative-sign field, or fields with a `target="opponent"` or similar
- [ ] Document findings in this file — list which field(s) are opponent-routed
- [ ] If the data model has no explicit "target=opponent" discriminator, flag it to the user as a data-model gap before implementing
- [ ] Write audit results in Notes below

**Notes:** [Filled during audit]

---

### Task 3.2: Compiler emits opponent-routed entries [Complex]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler.py --tb=short`

- [ ] Extend the spec-compile path: for each suppressor field identified in 3.1, emit a `ModifierEntry` keyed by `ModifierStack.per_team[opponent_team_id]` (not the source planet's owning-team)
- [ ] Decide: is "opponent team_id" always `1 - source_team_id` in a 2-team battle? Or does the compiler need to loop over all non-source teams for 3+ team battles? Answer in decisions.md.
- [ ] Write failing test: a planet-aura suppressor on team 0's planet → `spec.modifier_stack.per_team[1]` contains the entry; `per_team[0]` does not
- [ ] Run — fails
- [ ] Implement
- [ ] Run — passes

**Notes:** [Filled during implementation]

---

### Task 3.3: `FleetAuraManager` per-team application test [Medium]
**File:** `tests/unit/simulation/combat/test_fleet_aura_extended.py` (extend)
**Tests:** Targeted pytest run

- [ ] Write a test: `ModifierStack` with a `damage_mult=0.8` entry under `per_team[1]` → ships on team 1 have damage scaled by 0.8; ships on team 0 are unaffected
- [ ] Verify this already works in `FleetAuraManager` (it should — per-team buckets have been the mechanism since PROJ-269 Phase 5.5). If not, fix the gap.

**Notes:** [Filled during implementation]

---

### Task 3.4: Regression guard [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`

- [ ] Extend `TestNoPlaceholderStatKeyInStrategyCompiler` with suppressor-source assertions
- [ ] Optional: add a "cross-team routing" guard test — if the compiler generates an entry for a suppressor, it must be in `per_team[opponent]`, not `per_team[source]`

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Suppressor effects apply to the correct team
- [ ] Placeholder-stat_key guard extended
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
