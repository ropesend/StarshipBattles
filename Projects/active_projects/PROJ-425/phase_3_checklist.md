# Phase 3: Extract the factory path and keep a thin shim

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-425 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Re-read `ShipInstance.create(...)` + `_build_full_hp_components_from_design(...)` in `ship_instance.py`.
- [ ] Grep callers: `rg -n "ShipInstance\.create\(" game tests` — record the call-site count in `findings_ledger.md` (this is the shim-removal gate for a later phase / future project).
- [ ] Decide: extend an existing factory / service path, or add `game/strategy/services/ship_instance_factory.py`. Record in `decisions.md`.

---

## Tasks

### Task 3.1: TDD anchor — factory entry point + shim equivalence [Medium]
**File:** `tests/unit/strategy/services/test_ship_instance_factory.py` (new — if helper file is created) and/or `tests/unit/strategy/ship_instance/test_registries_di.py` (extend)
**Tests:** the chosen file(s)

- [ ] Add tests that call the new factory entry point directly and assert: same full-HP component construction; same missing-registry failure; component count matches design.
- [ ] Add one **shim-equivalence** test: `ShipInstance.create(...)` and the new factory produce structurally-equal `ShipInstance` objects.
- [ ] **Verify:** new-API tests fail today; shim-equivalence test fails today; legacy create-tests from Phase 0 still pass.

**Notes:**

### Task 3.2: Move the factory body into the new helper [Medium]
**File:** `game/strategy/services/ship_instance_factory.py` (or chosen extension target)
**Tests:** Task 3.1

- [ ] Cut the body of `create(...)` and `_build_full_hp_components_from_design(...)` into the factory.
- [ ] Preserve every observable behavior (full-HP construction, layer assembly, registry-DI semantics).
- [ ] **Verify:** new-API tests pass.

**Notes:**

### Task 3.3: Replace `ShipInstance.create(...)` body with a thin shim [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** shim-equivalence test from Task 3.1

- [ ] `ShipInstance.create(...)` now delegates to the factory. Do **not** remove the method.
- [ ] Document at the call site (docstring or `# PROJ-425 Phase 3` comment) that the shim is intentional and stays until a later caller-migration batch empties `rg -n "ShipInstance\.create\(" game tests`.
- [ ] **Verify:** shim-equivalence + all create-related Phase 0 tests pass.

**Notes:**

### Task 3.4: Grep gate before phase close [Simple]

- [ ] `rg -n "ShipInstance\.create\(" game tests` — confirm result set is non-empty (shim must remain).
- [ ] Record call-site count in `findings_ledger.md` for cross-reference at Phase 6 close.

**Notes:**

### Task 3.5: Focused regression + sharded suite [Simple]
**Tests:** as below.

- [ ] `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/services/ -x`
- [ ] `pytest tests/integration/test_fms_b_e2e.py tests/integration/test_fms_c_carrier_ai_launch.py -x`
- [ ] `python Tools/test_sharded/test_sharded.py`
- [ ] Record post-phase `wc -l ship_instance.py` in `findings_ledger.md`.
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-425 phase_3`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `ShipInstance.create(...)` body moved out, shim remains
- [ ] `_build_full_hp_components_from_design(...)` moved with the factory
- [ ] Grep gate confirms shim is still load-bearing
- [ ] Focused + sharded suites green
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after review
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
