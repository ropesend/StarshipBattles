# Phase 3: Extract the factory path and keep a thin shim

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-425 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):**
- `game/strategy/services/ship_instance_factory.py` (optional new — if no natural existing home)
- `game/strategy/data/ship_instance.py` (slim — `create(...)` body moves out, shim remains)
- `tests/unit/strategy/services/test_ship_instance_factory.py` (optional new — only if helper file is created)
- `tests/unit/strategy/ship_instance/test_registries_di.py` (extend — assert shim still works)

**Objective:** Move the body of `ShipInstance.create(...)` (and `_build_full_hp_components_from_design(...)`) into a factory / helper. **Leave `ShipInstance.create(...)` as a thin shim** that delegates to the new factory — this phase does **not** migrate every call site yet (TD-06 Weak-LLM Guardrail #1).

---

## Pre-flight (TDD baseline)

- [x] Re-read `ShipInstance.create(...)` + `_build_full_hp_components_from_design(...)` in `ship_instance.py`.
- [x] Grep callers: `rg -n "ShipInstance\.create\(" game tests` — record the call-site count in `findings_ledger.md` (this is the shim-removal gate for a later phase / future project).
- [x] Decide: extend an existing factory / service path, or add `game/strategy/services/ship_instance_factory.py`. Record in `decisions.md`.

---

## Tasks

### Task 3.1: TDD anchor — factory entry point + shim equivalence [Medium]
**File:** `tests/unit/strategy/services/test_ship_instance_factory.py` (new — if helper file is created) and/or `tests/unit/strategy/ship_instance/test_registries_di.py` (extend)
**Tests:** the chosen file(s)

- [x] Add tests that call the new factory entry point directly and assert: same full-HP component construction; same missing-registry failure; component count matches design.
- [x] Add one **shim-equivalence** test: `ShipInstance.create(...)` and the new factory produce structurally-equal `ShipInstance` objects.
- [x] **Verify:** new-API tests fail today; shim-equivalence test fails today; legacy create-tests from Phase 0 still pass.

**Notes:**

### Task 3.2: Move the factory body into the new helper [Medium]
**File:** `game/strategy/services/ship_instance_factory.py` (or chosen extension target)
**Tests:** Task 3.1

- [x] Cut the body of `create(...)` and `_build_full_hp_components_from_design(...)` into the factory.
- [x] Preserve every observable behavior (full-HP construction, layer assembly, registry-DI semantics).
- [x] **Verify:** new-API tests pass.

**Notes:**

### Task 3.3: Replace `ShipInstance.create(...)` body with a thin shim [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** shim-equivalence test from Task 3.1

- [x] `ShipInstance.create(...)` now delegates to the factory. Do **not** remove the method.
- [x] Document at the call site (docstring or `# PROJ-425 Phase 3` comment) that the shim is intentional and stays until a later caller-migration batch empties `rg -n "ShipInstance\.create\(" game tests`.
- [x] **Verify:** shim-equivalence + all create-related Phase 0 tests pass.

**Notes:**

### Task 3.4: Grep gate before phase close [Simple]

- [x] `rg -n "ShipInstance\.create\(" game tests` — confirm result set is non-empty (shim must remain).
- [x] Record call-site count in `findings_ledger.md` for cross-reference at Phase 6 close.

**Notes:**

### Task 3.5: Focused regression + sharded suite [Simple]
**Tests:** as below.

- [x] `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/services/ -x`
- [x] `pytest tests/integration/test_fms_b_e2e.py tests/integration/test_fms_c_carrier_ai_launch.py -x`
- [x] `python Tools/test_sharded/test_sharded.py`
- [x] Record post-phase `wc -l ship_instance.py` in `findings_ledger.md`.
- [x] Run `python Projects/scripts/phase_complete.py PROJ-425 phase_3`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `ShipInstance.create(...)` body moved out, shim remains
- [x] `_build_full_hp_components_from_design(...)` moved with the factory
- [x] Grep gate confirms shim is still load-bearing
- [x] Focused + sharded suites green
- [x] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after review
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
