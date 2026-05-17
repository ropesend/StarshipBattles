# Phase 5: Migrate `combat_modifier_collector` and `spec_compiler`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-429 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_4
**Review Mode:** standard

**Files (planned):**
- `game/strategy/combat/spec_compiler.py` (modify — line 827 `combat_ability_names`)
- `game/strategy/services/combat_modifier_collector.py` (modify — lines 96, 109, 113, 127)
- `game/strategy/services/ability_metadata.py` (modify — confirm/add `ShieldProjection` entry tagged `COMBAT_FLAT_BONUS`)
- `tests/unit/strategy/services/test_combat_modifier_collector.py` (modify — parity test FIRST)
- `tests/integration/test_combat_modifier_*` (read-only — gate phase exit)

**Objective:** Make "is this ability a combat modifier?" have one answer. Replace duplicated literal sets in `spec_compiler.py` and `combat_modifier_collector.py` with `abilities_with_kind_tag(StrategicKind.COMBAT_MODIFIER)` queries. Model `ShieldProjection` with the distinct `COMBAT_FLAT_BONUS` tag so it stays out of the multiplier aggregation path.

---

## Reading

- [ ] Re-read `design.md` "Per-Consumer Migration Order" Phase 5 row and "Risks" `ShieldProjection` row.
- [ ] Re-read `decisions.md` row 4 (the `COMBAT_FLAT_BONUS` choice).
- [ ] Read `game/strategy/combat/spec_compiler.py` lines 820-840 (the `combat_ability_names` set and the `_entries_from_sector_effects` filter call).
- [ ] Read `game/strategy/services/combat_modifier_collector.py` lines 80-140 (both iterated tuples plus the `ShieldProjection` flat-bonus branch).
- [ ] List any existing `tests/integration/test_combat_modifier_*` files.

---

## Tasks

### Task 5.1: Add the failing parity test (TDD red) [Simple]

**File:** `tests/unit/strategy/services/test_combat_modifier_collector.py`

- [ ] Add `test_collector_iterates_exactly_kind_combat_modifier_set`:
      `assert set(combat_modifier_collector._modifier_names()) == abilities_with_kind_tag(StrategicKind.COMBAT_MODIFIER)`
      (Adjust the function/property name to whatever currently emits the multiplier-ability iteration.)
- [ ] Add `test_spec_compiler_combat_ability_names_matches_registry`:
      `assert spec_compiler._combat_ability_names_for_test() == abilities_with_kind_tag(StrategicKind.COMBAT_MODIFIER)`
      (Expose a test hook if needed; or simply test the resulting filter behavior.)
- [ ] Add `test_shield_projection_is_flat_bonus_not_modifier`:
      `assert ability_has_kind_tag('ShieldProjection', StrategicKind.COMBAT_FLAT_BONUS)`
      `assert not ability_has_kind_tag('ShieldProjection', StrategicKind.COMBAT_MODIFIER)`
- [ ] Confirm failures: literal sets still exist → tests fail.

**Notes:** [Filled during implementation]

### Task 5.2: Replace `combat_ability_names` in `spec_compiler.py` (TDD green) [Simple]

**File:** `game/strategy/combat/spec_compiler.py`

- [ ] Line 827: replace `combat_ability_names = {"ShieldModifier","DamageModifier","ThrustModifier"}` with `combat_ability_names = abilities_with_kind_tag(StrategicKind.COMBAT_MODIFIER)`.
- [ ] Verify: filter behavior unchanged for current three abilities; adding a fourth multiplier ability in the registry would automatically participate.

**Notes:** [Filled during implementation]

### Task 5.3: Replace tuples + `ShieldProjection` literal in `combat_modifier_collector.py` (TDD green) [Medium]

**File:** `game/strategy/services/combat_modifier_collector.py`

- [ ] Lines 96 and 127: replace `("ShieldModifier","DamageModifier")` with iteration over `abilities_with_kind_tag(StrategicKind.COMBAT_MODIFIER)`. (Note: the original tuple may exclude `ThrustModifier` deliberately for this code path — preserve that semantic by either filtering further on facet attributes or keeping a narrower kind tag distinct from the spec_compiler use case.)
- [ ] Lines 109 and 113: replace literal `"ShieldProjection"` with `abilities_with_kind_tag(StrategicKind.COMBAT_FLAT_BONUS)` membership/iteration.
- [ ] If lines 96 and 127 iterate a strict subset of COMBAT_MODIFIER (e.g., excluding `ThrustModifier`), introduce a separate tag (e.g., `MULTIPLIER_DEFENSIVE`) rather than reusing `COMBAT_MODIFIER` and silently changing behavior. Record decision in `decisions.md`.

**Notes:** [Filled during implementation]

### Task 5.4: Confirm `ShieldProjection` registry entry [Simple]

**File:** `game/strategy/services/ability_metadata.py`

- [ ] Confirm `ShieldProjection` was added in Phase 1's registry build with `kind_tags=frozenset({StrategicKind.COMBAT_FLAT_BONUS})`, no `EffectFacet`, no `EnergyFacet`.
- [ ] If somehow absent, add it here.

**Notes:** [Filled during implementation]

### Task 5.5: Integration regression sweep [Medium]

**Tests:**
- `pytest tests/unit/strategy/services/test_combat_modifier_collector.py -q`
- `pytest tests/integration/ -k combat_modifier -q` (or whatever the actual integration test prefix is)

- [ ] All combat-modifier multiplier aggregation tests still produce identical numerical results.
- [ ] `ShieldProjection` flat-bonus accumulation unchanged.
- [ ] No name divergence between `combat_modifier_collector` and `spec_compiler`.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No literal `{"ShieldModifier","DamageModifier","ThrustModifier"}` set in `spec_compiler.py`
- [ ] No literal `("ShieldModifier","DamageModifier")` tuple or `"ShieldProjection"` string in `combat_modifier_collector.py`
- [ ] `ShieldProjection` tagged `COMBAT_FLAT_BONUS`, not `COMBAT_MODIFIER`
- [ ] Focused unit + integration tests green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
