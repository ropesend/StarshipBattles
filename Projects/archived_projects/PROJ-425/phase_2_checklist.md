# Phase 2: Move component/layer inspection out of `ShipInstance`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-425 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):**
- `game/strategy/services/component_inspector.py` (extend)
- `game/strategy/data/ship_instance.py` (slim — inspector methods removed / become forwarders)
- `tests/unit/strategy/fleets/test_ship_instance_components.py` (update assertions to the new direct-call path)

**Objective:** Extend `component_inspector.py` with the ship-instance-specific helpers `iter_all_components_by_layer`, `get_damaged_components_by_layer`, `get_damaged_component_count`, and the helper logic that joins design layers with `ComponentState`. Move those behaviors **out of `ShipInstance`** and into the inspector. Per TD-06 Weak-LLM Guardrail #4, do not create a second inspector module unless extending `component_inspector.py` would breach the 500-LOC ceiling.

---

## Pre-flight (TDD baseline)

- [x] Re-read `component_inspector.py` end-to-end. Capture current LOC + the API surface that already exists.
- [x] If extending `component_inspector.py` would push it past 500 LOC, record in `decisions.md` and only then consider a new module.
- [x] Re-read the component-by-layer methods on `ShipInstance` and grep for callers: `rg -n "iter_all_components_by_layer|get_damaged_components_by_layer|get_damaged_component_count" game tests`.

---

## Tasks

### Task 2.1: TDD anchor — assert the new inspector API [Medium]
**File:** `tests/unit/strategy/fleets/test_ship_instance_components.py` (update)
**Tests:** `pytest tests/unit/strategy/fleets/test_ship_instance_components.py -v`

- [x] Add or pivot tests to call the new inspector entry points directly (e.g. `ComponentInspector(ship_instance).iter_all_components_by_layer()` or whatever the chosen surface is).
- [x] Keep one parallel test against `ShipInstance.iter_all_components_by_layer(...)` (if it survives as a thin shim) to prove call-site equivalence.
- [x] **Verify:** new-API tests fail today; legacy-API tests still pass.

**Notes:**

### Task 2.2: Extend `component_inspector.py` with the three helpers [Medium]
**File:** `game/strategy/services/component_inspector.py`
**Tests:** Task 2.1

- [x] Add `iter_all_components_by_layer`, `get_damaged_components_by_layer`, `get_damaged_component_count` to the inspector. Cut the helper logic that joins design layers with `ComponentState` out of `ShipInstance` and into the inspector.
- [x] Do **not** move this logic into UI code (TD-06 §"Phase 2" is explicit).
- [x] **Verify:** new-API tests now pass.

**Notes:**

### Task 2.3: Slim `ShipInstance` and (optionally) leave thin forwarders [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** Task 2.1

- [x] Remove the inspector implementations from `ShipInstance`. Either delete the methods entirely or leave them as thin forwarders to the inspector (forwarder removal is Phase 5-style work; defer if caller migration is large).
- [x] If forwarders remain, document in `findings_ledger.md` which ones survive into Phase 5/6.
- [x] **Verify:** legacy-API tests in 2.1 still pass (if forwarders remain) — or were migrated to the new API (if forwarders were removed).

**Notes:**

### Task 2.4: Focused regression + sharded suite [Simple]
**Tests:** as below.

- [x] `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/fleets/ -x`
- [x] `pytest tests/integration/test_fms_b_e2e.py tests/integration/test_fms_c_carrier_ai_launch.py -x`
- [x] `python Tools/test_sharded/test_sharded.py`
- [x] Record post-phase `wc -l ship_instance.py` and `wc -l component_inspector.py` in `findings_ledger.md`.
- [x] Run `python Projects/scripts/phase_complete.py PROJ-425 phase_2`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Component/layer inspection no longer lives inline in `ShipInstance`
- [x] `component_inspector.py` still under 500 LOC (or the split is justified in `decisions.md`)
- [x] No inspector logic landed in UI code
- [x] Focused + sharded suites green
- [x] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after review
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
