# Phase 1: Order-pop / event-payload characterization

**Status:** Complete
**Objective:** Lock down the order-pop matrix (6 superweapons × 3 outcomes) and the event payload shape for the 4 event types lacking payload assertions. Tests pass against the current code; they protect Phase 2-3.

---

## Tasks

### Task 1.1: Order-pop matrix test [Medium]
**File:** `tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py -v`

- [x] Module docstring referencing PROJ-364 Phase 1 + review finding #5.
- [x] Parametrize over the 6 superweapons (5 strategic + SELF_DESTRUCT) × 3 outcomes (success, failure-no-target, failure-no-ship). Total ~18 cases.
- [x] For each case, assert post-call: `fleet.get_current_order() is None` (popped) or matches expectation per superweapon's known semantics.
- [x] Document any exceptions in test docstrings (e.g. STELLERATE_STAR has `consume_ship=True` so the fleet itself is gone).
- [x] All tests pass against current code (this is characterization).

**Notes:** Landed 16 cases (5 strategic weapons × 3 + SELF_DESTRUCT × 2; failure-no-ship N/A for SELF_DESTRUCT — no ability check). STELLERATE_STAR success path explicitly does NOT call `fleet.pop_order()` (system_destroyer wipes the fleet); test docstring records this exception.

### Task 1.2: Event payload characterization for 4 weapons [Medium]
**File:** `tests/unit/strategy/engine/test_superweapon_event_payloads.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_event_payloads.py -v`

- [x] Use a fake `event_bus` with capture-list to record emitted events.
- [x] One test per weapon for the 4 currently uncovered event types:
  - `TestStarDestroyedPayload.test_payload_keys` — assert payload keys: `fleet_id`, `system_name`, `location_name`, `location_hex`.
  - `TestWarpPointOpenedPayload.test_payload_keys` — assert keys: `source_system`, `target_system`.
  - `TestWarpPointClosedPayload.test_payload_keys` — assert keys: `source_system`, `target_system`.
  - `TestDysonSphereCreatedPayload.test_payload_keys` — assert keys: `system_name`, `location_hex`, `message` (DYSON_SPHERE_CREATED only emits `system_name`, no `planet_id`/`planet_name` in current code).
- [x] Existing PLANET_DESTROYED and SHIPS_SELF_DESTRUCTED tests referenced via `test_existing_event_payload_coverage_documented` docstring.
- [x] All tests pass against current code.

**Notes:** Used real `EventBus` with capture-list handler for fidelity. Confirmed DYSON_SPHERE_CREATED currently only emits `system_name` — no planet_id/planet_name despite the dyson sphere being a registered planet.

### Task 1.3: Verify all tests pass green against pre-refactor code [Simple]
- [x] Run `pytest tests/unit/strategy/engine/test_superweapon* -v`. All green (existing + new): 148 passed.
- [x] Sharded suite: 17617 passed, 0 failed.

**Notes:** No test adjustments needed — characterization tests passed first time.

---

## Phase Completion Checklist
- [x] Order-pop matrix landed (16 tests, all green)
- [x] Event-payload tests for 4 weapons landed (5 tests including sanity reference)
- [x] Update plan.md phase table to `Complete`; Current State → Phase 2
