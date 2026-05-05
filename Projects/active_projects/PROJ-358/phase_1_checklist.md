# Phase 1: Failing Tests + Validation Error

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-358 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** none
**Review Mode:** standard
**Files (planned):** game/simulation/battle_runner.py, tests/unit/simulation/battle_runner/test_spec_component_validation.py
**Objective:** Replace the silent-ignore in `_apply_spec_components_to_ship` with a `ValidationException` that names the offending ship/component/design. Lock with TDD.

---

## Tasks

### Task 1.1: Audit current test fixtures for spec drift reliance [Simple]
**File:** Read-only audit
**Tests:** `pytest tests/unit/simulation/battle_runner/ -v --collect-only`

- [ ] Grep `ShipSpec.components` and `ComponentStateSpec` usage across `tests/`
- [ ] Identify any test that constructs a `ShipSpec` with components that intentionally don't map (testing the silent-ignore branch)
- [ ] List in [decisions.md](decisions.md). For each: decide whether the test is locking real semantics (rare) or encoding the bug (likely — rewrite to assert the new error)

**Notes:**

---

### Task 1.2: Write failing test — unmapped component raises with context [Medium]
**File:** `tests/unit/simulation/battle_runner/test_spec_component_validation.py` (new)
**Tests:** `pytest tests/unit/simulation/battle_runner/test_spec_component_validation.py -v`

- [ ] Construct a `ShipSpec` whose `components` list includes one entry with a `component_id` not present on the materialized Ship (the design exists; the spec entry is bogus)
- [ ] Call `_apply_spec_components_to_ship(ship_spec, ship)` (or whichever caller surface is being validated; prefer the public entry point)
- [ ] Assert it raises `ValidationException` and that the message contains: ship id, component_id, instance_index, design_id
- [ ] Run on current main — verify the test FAILS (no exception today; the entry is silently dropped)

**Notes:**

---

### Task 1.3: Write passing-on-main test — valid spec unchanged [Simple]
**File:** Same module
**Tests:** Same module

- [ ] Construct a valid `ShipSpec` whose every component entry maps cleanly
- [ ] Call the apply path and assert each component reaches its target HP
- [ ] Snapshot the materialized component state and assert it stays bit-identical post-fix

**Notes:**

---

### Task 1.4: Apply the validation [Medium]
**File:** `game/simulation/battle_runner.py:580-619`
**Tests:** `pytest tests/unit/simulation/battle_runner/test_spec_component_validation.py -v`

- [ ] Replace `if spec_entry is None: continue` with raising `ValidationException(...)` carrying ship id, component_id, instance_index, and `ship_spec.design_id`
- [ ] Remove the "(design drift)" sentence from the docstring; replace with the new contract: "Raises ValidationException if any spec component does not map to a Ship component."
- [ ] Verify Tasks 1.2 and 1.3 tests now PASS

**Notes:**

---

### Task 1.5: Reconcile pre-existing tests [Medium]
**Tests:** `pytest tests/unit/simulation/battle_runner/ -v`

- [ ] Run the existing battle_runner test suite
- [ ] For each failure: triage per the audit in Task 1.1 — rewrite if encoding the bug; surface to user if encoding real production semantics
- [ ] Do NOT weaken the new `ValidationException` to make stale tests pass

**Notes:**

---

### Task 1.6: Sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite passes
- [ ] If a real production drift surfaces (a strategy spec emits a bad entry), STOP and surface to user — that's a real bug worth a follow-up project, not a "make the validation lenient" decision

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to closure / awaiting user verification
- [ ] Update [manifest.md](manifest.md) if files outside the planned set were touched
