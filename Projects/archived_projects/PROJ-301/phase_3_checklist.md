# Phase 3: `PlanetIntrinsicAbilitySource` adapter + iterator registration

**Status:** Complete (2026-04-27)
**Objective:** Implement the adapter and register it with the iterator. After this phase, planet intrinsic abilities flow through the existing collector and appear in the Sector panel automatically.

---

## Tasks

### Task 3.1: Implement `PlanetIntrinsicAbilitySource` [Medium]
**File:** `game/strategy/services/ability_sources/planet_intrinsic.py` (NEW)
**Tests:** `tests/unit/strategy/services/ability_sources/test_planet_intrinsic.py` (NEW)

- [ ] Failing tests first:
  - [ ] `test_source_kind_is_planet`
  - [ ] `test_source_label_format` — `"Tarsis IV (Volcanic)"`.
  - [ ] `test_source_id_format` — `"planet_intrinsic:<planet.id>"`.
  - [ ] `test_owner_id_is_none`
  - [ ] `test_get_abilities_returns_intrinsic_dict`
  - [ ] `test_affects_hex_true_for_planet_global_location`
  - [ ] `test_affects_hex_false_for_other_hex`
  - [ ] `test_affects_system_true_when_planet_in_system`
  - [ ] `test_get_activation_state_returns_none`
- [ ] Implement per [design.md](design.md).
- [ ] Re-export from `game/strategy/services/ability_sources/__init__.py`.
- [ ] Run tests — green.

**Notes:**

### Task 3.2: Register provider with the iterator [Simple]
**File:** `game/strategy/services/ability_iterator.py`
**Tests:** `tests/unit/strategy/services/test_ability_iterator.py`

- [ ] Failing tests:
  - [ ] `test_iter_at_planet_hex_yields_planet_intrinsic_source` — fixture: a volcanic planet at H. Iterator at H yields a `PlanetIntrinsicAbilitySource`.
  - [ ] `test_iter_skips_planet_with_empty_intrinsic_abilities` — oceanic planet (empty `abilities`) does NOT yield.
- [ ] Add `_planet_intrinsic_provider` function and `register_source_provider(_planet_intrinsic_provider)` at module bottom.
- [ ] Run tests — green.

**Notes:**

### Task 3.3: Integration test — planet + facility + storm at same hex [Medium]
**File:** `tests/integration/strategy/test_sector_effects_multi_source.py` (NEW)

- [ ] Build fixture: a hex containing a planet (volcanic, with `EnvironmentalDamage damage_type:plasma`), a facility on the planet (with `ShieldModifier scope:sector`), and an overlapping storm (e.g. plasma_storm with its own `EnvironmentalDamage damage_type:plasma`).
- [ ] Assert `collect_sector_effects` returns:
  - One `ShieldModifier` effect with one provider (the facility).
  - One `EnvironmentalDamage:plasma` effect with TWO providers (planet + storm), `kind='rate'`, aggregate value = sum of the two rates (since they're ungrouped).
- [ ] Run — green.

**Notes:** This is the proof that the framework composes cleanly across source kinds.

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
