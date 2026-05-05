# Phase 1: Order-pop / event-payload characterization

**Status:** Not Started
**Objective:** Lock down the order-pop matrix (6 superweapons × 3 outcomes) and the event payload shape for the 4 event types lacking payload assertions. Tests pass against the current code; they protect Phase 2-3.

---

## Tasks

### Task 1.1: Order-pop matrix test [Medium]
**File:** `tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py -v`

- [ ] Module docstring referencing PROJ-364 Phase 1 + review finding #5.
- [ ] Parametrize over the 6 superweapons (5 strategic + SELF_DESTRUCT) × 3 outcomes (success, failure-no-target, failure-no-ship). Total ~18 cases.
- [ ] For each case, assert post-call: `fleet.get_current_order() is None` (popped) or matches expectation per superweapon's known semantics.
- [ ] Document any exceptions in test docstrings (e.g. STELLERATE_STAR has `consume_ship=True` so the fleet itself is gone).
- [ ] All tests pass against current code (this is characterization).

**Notes:** _(filled during implementation)_

### Task 1.2: Event payload characterization for 4 weapons [Medium]
**File:** `tests/unit/strategy/engine/test_superweapon_event_payloads.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_event_payloads.py -v`

- [ ] Use a fake `event_bus` with capture-list to record emitted events.
- [ ] One test per weapon for the 4 currently uncovered event types:
  - `test_stellerate_star_emits_star_destroyed_payload` — assert payload keys: `fleet_id`, `system_name`, `location_name`, `location_hex`.
  - `test_open_warp_point_emits_warp_point_opened_payload` — assert keys: `source_system`, `target_system`.
  - `test_close_warp_point_emits_warp_point_closed_payload` — assert keys: `source_system`, `target_system`.
  - `test_create_dyson_sphere_emits_dyson_sphere_created_payload` — assert keys per current code (likely `system_name`, `planet_id`, `planet_name`).
- [ ] Existing PLANET_DESTROYED and SHIPS_SELF_DESTRUCTED tests are already covered; add a sanity assertion at the top of this file referencing them (no duplication).
- [ ] All tests pass against current code.

**Notes:** _(filled during implementation)_

### Task 1.3: Verify all tests pass green against pre-refactor code [Simple]
- [ ] Run `pytest tests/unit/strategy/engine/test_superweapon* -v`. All green (existing + new).
- [ ] If a new test fails, current behavior IS the spec — adjust the test to characterize actual behavior and document in the test docstring.

**Notes:** _(filled during implementation)_

---

## Phase Completion Checklist
- [ ] Order-pop matrix landed (~18 tests, all green)
- [ ] Event-payload tests for 4 weapons landed
- [ ] Update plan.md phase table to `Complete`; Current State → Phase 2
