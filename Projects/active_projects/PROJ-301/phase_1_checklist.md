# Phase 1: Planet types data registry

**Status:** Complete (2026-04-27)
**Objective:** Create `data/planet_types.json` with intrinsic ability templates per planet type.

> **2026-04-27 update:** the original Phase 1 also shipped the `roll_intrinsic_abilities` helper. Per PROJ-300 decisions.md D15, that helper now ships in PROJ-300 (alongside the IAbilitySource framework). PROJ-301 imports it; Task 1.2 is removed.

---

## Tasks

### Task 1.1: Create `data/planet_types.json` [Simple]
**File:** `data/planet_types.json` (NEW)

- [ ] Confirm the canonical planet_type set used in current planet generation (grep for `planet_type` in `game/strategy/generation/` and `game/strategy/data/planet.py`).
- [ ] Write the JSON registry per the schema in [design.md](design.md). Cover every planet type used by the generator. Empty `abilities` dict is fine for types with no intrinsic effects.
- [ ] Add `Paths.PLANET_TYPES_FILE` to `game/core/paths.py`.

**Notes:**

### Task 1.2: ~~Implement `roll_intrinsic_abilities` helper~~ — REMOVED 2026-04-27

Helper now lives in PROJ-300 (`game/strategy/services/ability_sources/intrinsic_roll.py`) per PROJ-300 decisions.md D15. PROJ-301 imports it as a pure consumer. No work in this project for the helper.

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
