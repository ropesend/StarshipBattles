# Phase 1: Planet types data registry + roll helper

**Status:** Not Started
**Objective:** Create `data/planet_types.json` with intrinsic ability templates per planet type. Add the shared `roll_intrinsic_abilities` helper that converts `{"min": x, "max": y}` template values to rolled scalars.

---

## Tasks

### Task 1.1: Create `data/planet_types.json` [Simple]
**File:** `data/planet_types.json` (NEW)

- [ ] Confirm the canonical planet_type set used in current planet generation (grep for `planet_type` in `game/strategy/generation/` and `game/strategy/data/planet.py`).
- [ ] Write the JSON registry per the schema in [design.md](design.md). Cover every planet type used by the generator. Empty `abilities` dict is fine for types with no intrinsic effects.
- [ ] Add `Paths.PLANET_TYPES_FILE` to `game/core/paths.py`.

**Notes:**

### Task 1.2: Implement `roll_intrinsic_abilities` helper [Medium]
**File:** `game/strategy/services/ability_sources/intrinsic_roll.py` (NEW)
**Tests:** `tests/unit/strategy/services/ability_sources/test_intrinsic_roll.py` (NEW)

- [ ] Failing tests first:
  - [ ] `test_passes_through_scalar_values` — `{"multiplier": 0.5, "scope": "sector"}` returns unchanged.
  - [ ] `test_rolls_range_to_scalar` — `{"multiplier": {"min": 0.5, "max": 0.9}, ...}` returns dict with `multiplier` between 0.5 and 0.9.
  - [ ] `test_rng_determinism` — same `random.Random(seed)` produces same rolls.
  - [ ] `test_rolls_rate_field`
  - [ ] `test_rolls_multiple_fields_in_one_ability_data`
  - [ ] `test_rolls_across_multiple_abilities`
  - [ ] `test_empty_template_returns_empty`
- [ ] Implement:
  ```python
  def roll_intrinsic_abilities(template: Dict[str, Any], rng: random.Random) -> Dict[str, Any]:
      result = {}
      for ability_name, ability_data in template.items():
          rolled = {}
          for key, value in ability_data.items():
              if isinstance(value, dict) and 'min' in value and 'max' in value:
                  rolled[key] = rng.uniform(value['min'], value['max'])
              else:
                  rolled[key] = value
          result[ability_name] = rolled
      return result
  ```
- [ ] Run tests — green.

**Notes:** Promote to a shared module in PROJ-302 if both projects use it as expected.

### Task 1.3: Validation test — every planet_type has an entry [Simple]
**File:** `tests/integration/data/test_planet_types_registry.py` (NEW)

- [ ] For every planet_type the generator can produce, assert `planet_types.json` has an entry (even if `abilities` is empty).

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
