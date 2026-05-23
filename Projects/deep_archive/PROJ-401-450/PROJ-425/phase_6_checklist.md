# Phase 6: Cargo + deployable forwarder demolition (TD-06 Batch 5c) — gated by PROJ-431 Phase 1

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-425 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Blocked
**Depends on:** phase_5, **PROJ-431/phase_1** (cross-project — see body)
**Review Mode:** standard
**Files (planned):**
- `game/strategy/data/ship_instance.py` (slim — demolish cargo/deployable forwarders)
- `game/strategy/data/ship_cargo_manager.py` (target of caller migration)
- Caller files in `game/` and `tests/` discovered by grep
- `tests/unit/strategy/ship_instance/test_capacity_levels.py` (regression gate)
- `tests/integration/test_fms_c_carrier_ai_launch.py` (deployable-heavy regression gate)

**Objective:** Demolish the cargo / carried-vehicle / pod-storage forwarders from `ShipInstance` and migrate their callers to `ShipCargoManager` (or its canonical accessor after PROJ-431). This is **TD-06 Batch 5c** — the sub-batch that TD-06 §"Ordering Constraints" explicitly calls out as the only TD-10-sensitive piece of the entire TD-06 plan.

---

## CROSS-PROJECT GATE — DO NOT START UNTIL THIS IS TRUE

This phase is **blocked** until [PROJ-431 (TD-10) Phase 1](../PROJ-431/plan.md) has landed the typed `bay_inventory` substrate on `main`. The cross-project dependency is not first-class in `phase_state.json`'s `depends_on` field (which only records intra-project predecessors), so the gate is enforced here in the checklist + in `plan.md`'s Quick Status row (`Blocked` until PROJ-431 Phase 1 merges).

**Gate verification before starting any task below:**

- [ ] Confirm [`Projects/active_projects/PROJ-431/plan.md`](../PROJ-431/plan.md) shows Phase 1 as Complete (or has been moved to `Projects/completed/` with Phase 1+ done).
- [ ] Confirm the typed `bay_inventory` substrate exists on `main` and is the canonical cargo accessor: read `game/strategy/data/ship_cargo_manager.py` and verify the typed substrate API is present.
- [ ] If either check fails, **stop** and update plan.md Current State to reflect the continued block.

---

## Pre-flight (TDD baseline, after gate is cleared)

- [ ] Re-read TD-06 §"Batch 5c - Cargo and capacity forwarders" and §"Ordering Constraints".
- [ ] Re-read the cargo / carried-vehicle / pod-storage forwarders still remaining on `ShipInstance` (Phase 5 left them in place).
- [ ] Enumerate the forwarder names that still need demolition; grep each across `game tests` and record call sites in `findings_ledger.md`.

---

## Tasks

### Task 6.1: Sub-batch sequencing for cargo + deployable [Medium]

Treat the cargo forwarder demolition as a series of micro-batches (cargo queries → cargo mutators → carried-vehicle queries → pod-storage helpers). Same discipline as Phase 5: grep → failing test for the new direct-call path → migrate callers → remove this slice's forwarders only → focused tests → next slice.

- [ ] **Cargo queries** — grep, failing test, migrate, demolish, verify.
- [ ] **Cargo mutators** — grep, failing test, migrate, demolish, verify.
- [ ] **Carried-vehicle queries** — grep, failing test, migrate, demolish, verify.
- [ ] **Pod-storage helpers** — grep, failing test, migrate, demolish, verify.

**Notes:** the exact forwarder names depend on the current state of `ship_instance.py` after Phase 5; enumerate at sub-batch time.

### Task 6.2: Final grep gate (TD-06 §"Phase 6 - Final trim and cleanup") [Simple]

- [ ] `rg -n "ShipInstance\.create\(|\.to_ship\(|\.update_from_ship\(|\.to_dict\(|\.clone\(" game tests`
- [ ] For each entry point that still has live callers: leave it as a documented thin shim and record in `decisions.md` + `findings_ledger.md`. **Do not force a risky all-callers migration.**
- [ ] Confirm `ShipInstance` is now materially under 500 LOC. Record post-phase `wc -l ship_instance.py` in `findings_ledger.md`.

### Task 6.3: Full regression sweep [Simple]

- [ ] `pytest tests/unit/strategy/ship_instance/ tests/unit/strategy/services/ tests/unit/strategy/fleets/ -x`
- [ ] `pytest tests/integration/test_fms_b_e2e.py tests/integration/test_fms_c_carrier_ai_launch.py -x` — the carrier AI launch test is the deployable-heavy regression gate.
- [ ] `python Tools/test_sharded/test_sharded.py`
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-425 phase_6`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All cargo / carried-vehicle / pod-storage forwarders demolished (or explicitly documented as deferred shims)
- [ ] `ShipInstance` is materially smaller than the 845-LOC baseline (record final LOC)
- [ ] All TD-06 acceptance criteria from `plan.md` §"Verification" hold
- [ ] Focused + sharded suites green
- [ ] Deployable-heavy integration flows (`test_fms_c_carrier_ai_launch.py`) green
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after review
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to mark the project ready for final audit
