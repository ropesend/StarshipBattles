# Phase 4: CAT-11 fragile assertion + CAT-12 logic-heavy (core)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-495 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace exact-value/format assertions and logic-heavy test bodies in core-mechanical tests. Inherited from PROJ-480 Phases 4 + 5.

Line refs advisory — Phase 0 should have refreshed them. Re-grep before editing.

---

## Tasks

### Task 4.1: test_join_fleet_handler.py — exact 7-key dict equality
**File:** `tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py`
**Origin:** PROJ-480 T4.3

- [x] Replace exact dict equality (PROJ-480 cited lines 217-242) on FLEET_JOINED payload with `required_keys <= set(payload)` + targeted value assertions on the load-bearing fields.
- [x] Verify: passes (12 tests); test renamed to `test_process_instant_orders_emits_fleet_joined_event_payload_key_presence`.

### Task 4.2: test_ship_loading.py — logic-heavy ship validation body
**File:** `tests/unit/builder/test_ship_loading.py`
**Tests:** `pytest tests/unit/builder/test_ship_loading.py`
**Origin:** PROJ-480 T5.1

- [~] **DROPPED:** PROJ-478 Task 1.10 already replaced the 42-LOC logic-heavy body with a 5-line `pytest.skip(...)` (the test directory `tests/unit/ships/` doesn't exist and `tests/unit/data/ships/` fixtures rely on the test-only component registry). Original CAT-12 finding no longer applies.

### Task 4.3: test_empire_economy_caching.py — repeated scenario unpack
**File:** `tests/unit/strategy/services/test_empire_economy_caching.py`
**Tests:** `pytest tests/unit/strategy/services/test_empire_economy_caching.py`
**Origin:** PROJ-480 T5.2

- [x] Added `economy_test_env` fixture that yields `(service, session, galaxy, empires)`; the 4 cache-behaviour tests now use a single `service, _session, _galaxy, empires = economy_test_env` line.
- [x] Verify: passes (4 tests); LOC delta ≈ -15.

### Task 4.4: test_order_processor_facade.py — meta-test imports
**File:** `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py`
**Origin:** PROJ-480 T5.15

- [x] Removed `test_phase_4_gates_still_pass` (the meta-test that imports gate modules and asserts `hasattr` on their named tests). Kept a traceability comment naming the gate-test paths so a future maintainer can find them.
- [x] Verify: passes (1 test remains: `test_order_processor_minimal_order_type_references`); LOC delta ≈ -15.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate PROJ-495 complete
