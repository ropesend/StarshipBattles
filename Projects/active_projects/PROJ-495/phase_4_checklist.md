# Phase 4: CAT-11 fragile assertion + CAT-12 logic-heavy (core)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-495 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace exact-value/format assertions and logic-heavy test bodies in core-mechanical tests. Inherited from PROJ-480 Phases 4 + 5.

Line refs advisory — Phase 0 should have refreshed them. Re-grep before editing.

---

## Tasks

### Task 4.1: test_join_fleet_handler.py — exact 7-key dict equality
**File:** `tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py`
**Origin:** PROJ-480 T4.3

- [ ] Replace exact dict equality (PROJ-480 cited lines 217-242) on FLEET_JOINED payload with `assert all(key in payload for key in ["category", "empire_id", ...])`.
- [ ] Verify: passes; LOC delta ≈ +3.

### Task 4.2: test_ship_loading.py — logic-heavy ship validation body
**File:** `tests/unit/builder/test_ship_loading.py`
**Tests:** `pytest tests/unit/builder/test_ship_loading.py`
**Origin:** PROJ-480 T5.1

- [ ] Extract per-ship validation into a helper and parametrize by design file. Current 42-LOC body (PROJ-480 cited lines 88-129) has nested loops + 4 stat-type if/else + broad except.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 4.3: test_empire_economy_caching.py — repeated scenario unpack
**File:** `tests/unit/strategy/services/test_empire_economy_caching.py`
**Tests:** `pytest tests/unit/strategy/services/test_empire_economy_caching.py`
**Origin:** PROJ-480 T5.2

- [ ] Extract `session, galaxy, empires = smoke_turn1_scenario` + `_build_service(fresh_registries)` (repeated 4×, PROJ-480 cited lines 32-83) into a fixture yielding `(service, session, galaxy, empires)`.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 4.4: test_order_processor_facade.py — meta-test imports
**File:** `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py`
**Origin:** PROJ-480 T5.15

- [ ] Remove the meta-test that imports gate_no_legacy / gate_completeness then asserts hasattr (PROJ-480 cited lines 60-75). Pytest discovery already fails naturally if those tests are renamed/deleted.
- [ ] Verify: passes; LOC delta ≈ -15.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate PROJ-495 complete
