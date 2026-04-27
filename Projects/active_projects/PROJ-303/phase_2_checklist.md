# Phase 2: `WarpPoint.intrinsic_abilities` field + generation

**Status:** Complete (2026-04-27)
**Objective:** Add the field, populate during generation, save/load roundtrip.

---

## Tasks

### Task 2.1: Add `intrinsic_abilities` to `WarpPoint` dataclass [Simple]
**File:** `game/strategy/data/` (warp_point file)
**Tests:** `pytest tests/unit/strategy/data/test_warp_point.py` (or similar)

- [ ] Failing tests for field default + roundtrip.
- [ ] Add `intrinsic_abilities: Dict[str, Any] = field(default_factory=dict)`. Update serialization.

**Notes:**

### Task 2.2: Populate during generation [Medium]
**File:** Locate the warp point generator file.
**Tests:** Generator tests.

- [ ] Failing tests:
  - [ ] `test_unstable_warp_point_has_environmental_damage_intrinsic`
  - [ ] `test_stable_warp_point_has_no_intrinsic`
  - [ ] `test_intrinsic_value_within_range`
- [ ] Load `data/warp_point_types.json`. After type assignment, call `roll_intrinsic_abilities`.

**Notes:**

### Task 2.3: Save/load roundtrip [Simple]
**File:** `tests/integration/save_load/test_roundtrip_warp_points.py` (extend or NEW)

- [ ] Generate a galaxy with at least one unstable warp point. Save. Load. Assert intrinsic_abilities preserved.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
