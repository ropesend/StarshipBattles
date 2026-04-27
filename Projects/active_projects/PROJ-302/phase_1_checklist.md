# Phase 1: Star types data registry

**Status:** Not Started
**Objective:** Confirm the canonical star_type taxonomy. Create `data/star_types.json` with intrinsic ability templates per star type. Ensure `roll_intrinsic_abilities` is available (from PROJ-301 or shipped here).

---

## Tasks

### Task 1.1: Confirm star_type taxonomy [Simple]
**File:** N/A (investigation)

- [ ] Read `game/strategy/data/star_generation_config.py` and `game/strategy/data/stars.py`. List every star_type the generator produces.
- [ ] Cross-reference with any UI rendering code that switches on star_type — make sure the JSON registry covers all of them.

**Notes:**

### Task 1.2: Create `data/star_types.json` [Simple]
**File:** `data/star_types.json` (NEW)

- [ ] Write the registry per the schema in [design.md](design.md). Use the confirmed taxonomy from 1.1.
- [ ] Empty `abilities` is fine for star types with no intrinsic effects.
- [ ] Add `Paths.STAR_TYPES_FILE` to `game/core/paths.py`.

**Notes:**

### Task 1.3: Ensure `roll_intrinsic_abilities` available [Simple]
**File:** `game/strategy/services/ability_sources/intrinsic_roll.py`

- [ ] If PROJ-301 has merged, this file already exists. Confirm.
- [ ] If PROJ-301 has NOT merged, create it here per PROJ-301's Phase 1 spec. Note in decisions.md and coordinate with PROJ-301 to avoid duplicate creation.

**Notes:**

### Task 1.4: Validation test — every star_type has an entry [Simple]
**File:** `tests/integration/data/test_star_types_registry.py` (NEW)

- [ ] For every star_type the generator can produce, assert `star_types.json` has an entry.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
