# Phase 2: `Star.intrinsic_abilities` field + generation

**Status:** Not Started
**Objective:** Add `intrinsic_abilities` to Star; populate during generation; save/load roundtrip.

---

## Tasks

### Task 2.1: Add `intrinsic_abilities` to `Star` dataclass [Simple]
**File:** `game/strategy/data/stars.py`
**Tests:** `pytest tests/unit/strategy/data/test_stars.py` (or appropriate)

- [ ] Failing tests first:
  - [ ] `test_star_has_intrinsic_abilities_field_default_empty`
  - [ ] `test_star_to_dict_carries_intrinsic_abilities`
  - [ ] `test_star_from_dict_reads_intrinsic_abilities`
  - [ ] `test_star_from_dict_defaults_when_missing`
- [ ] Add field; update serialization.

**Notes:**

### Task 2.2: Populate during star generation [Medium]
**File:** Locate the star generator file (`game/strategy/generation/`).
**Tests:** Star generator tests.

- [ ] Failing tests:
  - [ ] `test_neutron_star_has_radiation_intrinsic`
  - [ ] `test_g_class_has_no_intrinsic`
  - [ ] `test_pulsar_has_both_shieldmodifier_and_environmental_damage`
  - [ ] `test_intrinsic_value_within_template_range`
- [ ] Load `data/star_types.json` once at module init. After star type assignment, call `roll_intrinsic_abilities(template['abilities'], rng)`.

**Notes:**

### Task 2.3: Save/load roundtrip [Simple]
**File:** `tests/integration/save_load/test_roundtrip_stars.py` (extend or NEW)

- [ ] Generate a galaxy with at least one neutron star. Save. Load. Assert intrinsic_abilities preserved.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
