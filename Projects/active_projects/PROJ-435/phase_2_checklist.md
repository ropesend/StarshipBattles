# Phase 2: Implement migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-435 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Register `GravityModifier` and `RadiationShield` in
`AbilityMetadataRegistry` with `StrategicKind.ENERGY_DRAINING` + an
`EnergyFacet`, then migrate `stat_rows_dynamic.py` to drive ability
iteration from registry tags (keeping UI labels in UI-side dicts).

---

## Tasks

### Task 2.1: Failing test — UI iterates registry [Medium]
**File:** `tests/unit/ui/screens/builder/test_stat_rows_dynamic.py`
**Tests:** Add `test_activatable_abilities_literal_is_gone`,
`test_planetary_defense_rows_pick_up_gravity_modifier_and_radiation_shield`.

- [x] Assert `stat_rows_dynamic._ACTIVATABLE_ABILITIES` is not present
      (regression guard against the literal).
- [x] Assert `get_planetary_defense_rows` emits rows for
      `GravityModifier` and `RadiationShield` when the ship has them.
- [x] Run; confirm RED.

### Task 2.2: Failing test — registry has new entries [Simple]
**File:** `tests/unit/strategy/services/test_ability_metadata_registry.py`
**Tests:** Extend an existing test or add
`test_gravity_modifier_and_radiation_shield_are_energy_draining`.

- [x] Assert both names appear in
      `abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)`.
- [x] Assert `ability_drains_energy(name)` is True for both.
- [x] Run; confirm RED.

### Task 2.3: Register the two abilities [Simple]
**File:** `game/strategy/services/ability_metadata.py`

- [x] Add `AbilityMetadata(name="GravityModifier", energy=_energy_drain(), kind_tags=frozenset({StrategicKind.ENERGY_DRAINING}))`.
- [x] Add `AbilityMetadata(name="RadiationShield", energy=_energy_drain(), kind_tags=frozenset({StrategicKind.ENERGY_DRAINING}))`.
- [x] Run Task 2.2 test; confirm GREEN.

### Task 2.4: Migrate `_ACTIVATABLE_ABILITIES` to iteration [Medium]
**File:** `game/ui/screens/builder/stat_rows_dynamic.py`

- [x] Delete `_ACTIVATABLE_ABILITIES` literal.
- [x] Add a UI-side label dict `_ACTIVATABLE_ABILITY_LABELS` (purely
      display-string mapping, no membership semantics).
- [x] Update `get_planetary_defense_rows` to iterate
      `abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)` in a stable
      sort order; resolve label via the UI-side dict (falling back to
      the ability name if missing).
- [x] Run Task 2.1 test; confirm GREEN.

### Task 2.5: Migrate `modifier_abilities` [Medium]
**File:** `game/ui/screens/builder/stat_rows_dynamic.py`

- [x] Replace the inline `modifier_abilities` literal with a UI-side
      label dict plus iteration over the union
      `COMBAT_MODIFIER ∪ BUILD_RATE_BOOSTER ∪ RESOURCE_BOOSTER`.
- [x] Filter to names present in the UI label dict (preserves current
      behaviour: ThrustModifier and QualityImprovement remain hidden
      from this section).
- [x] Preserve stable display order (use the label dict insertion
      order rather than registry tag iteration order).

### Task 2.6: Run focused tests [Simple]

- [x] `pytest tests/unit/ui/screens/builder/test_stat_rows_dynamic.py -q`
- [x] `pytest tests/unit/strategy/services/test_ability_metadata_registry.py -q`

### Task 2.7: Full sharded suite [Simple]

- [x] `python Tools/test_sharded/test_sharded.py`
- [x] Confirm GREEN.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State
