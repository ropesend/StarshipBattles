# Phase 4: Move write behavior onto `ShipInstanceWriteService` + standardize manager names

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-425 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):**
- `game/strategy/services/ship_instance_write_service.py` (extend — toggles + repair)
- `game/strategy/data/ship_instance.py` (slim — write methods become forwarders or move entirely)
- `tests/unit/strategy/services/test_ship_instance_write_service.py` (extend)
- `tests/unit/strategy/ship_instance/test_component_toggles.py` (update assertions)

**Objective:** **Prep:** verify canonical manager/accessor names on `ShipInstance` and reconcile any divergence with the write service **before** any caller migration. **Move:** cache-invalidating component toggles, repair / full-repair logic, and any remaining direct-write helpers that are not identity-level behavior onto `ShipInstanceWriteService`. Cache invalidation must end up centralized in the write service — not split across old entity methods and new service methods.

---

## Pre-flight (TDD baseline)

- [ ] Re-read the Phase 0 manager-name findings in `findings_ledger.md`.
- [ ] Re-grep `rg -n "self\._cargo_manager|self\._consumable_manager|self\.cargo_manager|self\.consumable_manager" game/strategy/data/ship_instance.py game/strategy/services/ship_instance_write_service.py` and record any divergence.
- [ ] Identify the canonical name(s) and capture the decision in `decisions.md`.

---

## Tasks

### Task 4.1: Standardize manager / accessor names [Medium]
**File:** `game/strategy/data/ship_instance.py` + `game/strategy/services/ship_instance_write_service.py`
**Tests:** existing entity + write-service tests must remain green throughout.

- [ ] Rename on whichever side does not match the chosen canonical name. Pick one direction; do not introduce parallel accessors.
- [ ] Update tests and any internal references mechanically.
- [ ] **Verify:** `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/services/test_ship_instance_write_service.py -x` — all green before any logic moves.

**Notes:**

### Task 4.2: TDD anchor — write service owns toggles + repair [Medium]
**File:** `tests/unit/strategy/services/test_ship_instance_write_service.py` (extend)
**Tests:** as above.

- [ ] Add tests that call the write service for: `toggle_component(...)` (or equivalent) + assert cache invalidation; `repair(...)` / full-repair + assert hp restore + cache invalidation.
- [ ] **Verify:** tests fail today (the write service does not yet own these behaviors).

**Notes:**

### Task 4.3: Move toggle + repair behavior to `ShipInstanceWriteService` [Medium]
**File:** `game/strategy/services/ship_instance_write_service.py`
**Tests:** Task 4.2 + Phase 0 toggle/repair characterization (`test_component_toggles.py`).

- [ ] Cut the toggle + repair logic out of `ShipInstance` and into the write service. Centralize cache invalidation in the write service — do not leave it half on the entity and half in the service.
- [ ] If the entity keeps thin forwarders for back-compat, document them as Phase-5-style demolition candidates.
- [ ] **Verify:** Task 4.2 tests pass; Phase 0 toggle/repair tests still pass.

**Notes:**

### Task 4.4: Focused regression + sharded suite [Simple]
**Tests:** as below.

- [ ] `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/services/ tests/unit/strategy/fleets/ -x`
- [ ] `pytest tests/integration/test_fms_b_e2e.py tests/integration/test_fms_c_carrier_ai_launch.py -x`
- [ ] `python Tools/test_sharded/test_sharded.py`
- [ ] Record post-phase `wc -l ship_instance.py` and `wc -l ship_instance_write_service.py` in `findings_ledger.md`.
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-425 phase_4`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Manager/accessor names are consistent between entity and write service
- [ ] Toggle + repair logic centralized on `ShipInstanceWriteService`
- [ ] Cache invalidation is centralized in the write service (not split)
- [ ] Focused + sharded suites green
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after review
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
