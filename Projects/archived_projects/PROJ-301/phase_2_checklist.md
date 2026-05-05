# Phase 2: `Planet.intrinsic_abilities` field + generation

**Status:** Complete (2026-04-27)
**Objective:** Add the `intrinsic_abilities: Dict[str, Any]` field to `Planet`. Populate it during generation by reading the registry and rolling per-instance values. Save/load roundtrip preserves rolled values.

---

## Tasks

### Task 2.1: Add `intrinsic_abilities` to `Planet` dataclass [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet.py`

- [ ] Failing tests first:
  - [ ] `test_planet_has_intrinsic_abilities_field_default_empty`
  - [ ] `test_planet_to_dict_carries_intrinsic_abilities`
  - [ ] `test_planet_from_dict_reads_intrinsic_abilities`
  - [ ] `test_planet_from_dict_defaults_intrinsic_abilities_when_missing` (defensive default for partial fixtures, not a save-format-compat shim).
- [ ] Add `intrinsic_abilities: Dict[str, Any] = field(default_factory=dict)` to the dataclass.
- [ ] Update `to_dict` / `from_dict`.
- [ ] Run tests — green.

**Notes:**

### Task 2.2: Populate `intrinsic_abilities` during planet generation [Medium]
**File:** `game/strategy/generation/planet_generator.py` (or wherever planets are constructed — confirm via grep)
**Tests:** `pytest tests/unit/strategy/generation/test_planet_generator.py` (or appropriate)

- [ ] Failing tests:
  - [ ] `test_volcanic_planet_has_environmental_damage_intrinsic` — generated volcanic planet has a rolled `EnvironmentalDamage` ability with `damage_type: plasma`.
  - [ ] `test_oceanic_planet_has_no_intrinsic_abilities` — empty dict.
  - [ ] `test_intrinsic_ability_rate_within_range` — rolled value in [0.2, 0.5] for volcanic.
  - [ ] `test_two_volcanic_planets_have_different_rolled_values_with_different_seeds`.
- [ ] In the generator: load `data/planet_types.json` once at module init. After choosing a planet_type, call `roll_intrinsic_abilities(template['abilities'], rng)` and assign to `planet.intrinsic_abilities`.
- [ ] Run tests — green.

**Notes:**

### Task 2.3: Save/load roundtrip with rolled values [Simple]
**File:** `tests/integration/save_load/test_roundtrip_planets.py` (extend or NEW)

- [ ] Generate a galaxy with at least one volcanic planet. Save. Load. Assert:
  - Loaded planet has same `intrinsic_abilities` dict (deep equality).
  - Specifically the rolled scalar values are preserved exactly.
- [ ] Run test — green.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
