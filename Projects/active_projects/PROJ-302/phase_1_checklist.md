# Phase 1: Star types data registry

**Status:** Not Started
**Objective:** Confirm the canonical star_type taxonomy. Create `data/star_types.json` with intrinsic ability templates per star type.

> **2026-04-27 update:** the original Phase 1 had a fallback "ship `roll_intrinsic_abilities` here if PROJ-301 hasn't landed" task. Per PROJ-300 D15 the helper now ships in PROJ-300 alongside the IAbilitySource framework. Task 1.3 is removed; PROJ-302 imports the helper from PROJ-300 unconditionally.

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

### Task 1.3: ~~Ensure `roll_intrinsic_abilities` available~~ — REMOVED 2026-04-27

Helper ships in PROJ-300 per PROJ-300 D15. Phase 2 imports it directly.

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
