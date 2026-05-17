# Phase 5: Demolish display / consumable / serializer / bridge forwarders (TD-10-independent sub-batches)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-425 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_4
**Review Mode:** standard
**Files (planned):**
- `game/strategy/data/ship_instance.py` (slim — demolish forwarders in sub-batches)
- `game/strategy/data/ship_display_formatter.py` (target of Batch 5a caller migration)
- `game/strategy/data/ship_consumable_manager.py` (target of Batch 5b)
- `game/strategy/data/ship_instance_serializer.py` (target of Batch 5d)
- `game/strategy/data/ship_instance_bridge.py` (target of Batch 5e)
- Caller files discovered by grep at each sub-batch (`game/`, `tests/`)
- `tests/unit/strategy/ship_instance/` regression suite

**Objective:** Demolish the four TD-10-independent forwarder sub-batches **sequentially with grep gates between them**: 5a Display → 5b Consumable → 5d Serializer → 5e Bridge. Cargo/deployable (Batch 5c) is excluded — that is Phase 6 of this project and is blocked on PROJ-431 Phase 1.

For every sub-batch: **grep → write a focused failing test for the new direct-call path → migrate callers → remove only this sub-batch's forwarders → rerun focused tests → next sub-batch.** Never demolish more than one sub-batch in a single commit.

---

## Pre-flight

- [ ] Re-read TD-06 §"Phase 5 — Remove forwarders in controlled sub-batches".
- [ ] Confirm Phase 4 left the entity in a state where write behavior is centralized on the write service.

---

## Sub-batch 5a: Display forwarders

**Forwarders:** `get_display_id`, `get_status_text`, `get_hp_display`, `get_resource_display`
**Caller migration target:** `ShipDisplayFormatter`

- [ ] **Grep callers:** `rg -n "get_display_id|get_status_text|get_hp_display|get_resource_display" game tests`. Record the call sites.
- [ ] Add one focused failing test asserting the new direct-call path (`ShipDisplayFormatter.<method>(ship_instance)` or equivalent) is the expected surface.
- [ ] Migrate all callers from `ship.<forwarder>()` to `ShipDisplayFormatter.<method>(ship)` (or the canonical accessor).
- [ ] Remove the four display forwarders from `ShipInstance` — and only those four.
- [ ] **Verify:** `pytest tests/unit/strategy/ship_instance/ -x` green; targeted UI / formatter tests green; `rg` for the four forwarder names returns zero matches in `game/`.
- [ ] Commit (sub-batch 5a complete).

---

## Sub-batch 5b: Resource / consumable forwarders

**Forwarders:** resource-capacity queries, resource-consumption helpers, resupply helpers (enumerate at grep time)
**Caller migration target:** `ShipConsumableManager` (or a stable accessor to it)

- [ ] **Grep callers:** identify the exact forwarder names from `ship_instance.py` and grep each across `game tests`. Record in `findings_ledger.md`.
- [ ] Add one focused failing test for the new direct-call path.
- [ ] Migrate callers to the consumable manager (or its canonical accessor).
- [ ] Remove the consumable forwarders from `ShipInstance` — and only those.
- [ ] **Verify:** focused suites green; grep for the demolished names returns zero in `game/`.
- [ ] Commit (sub-batch 5b complete).

---

## Sub-batch 5d: Serializer forwarders

**Forwarders:** `to_dict`, `from_dict`, `to_json`, `from_json`, `clone`
**Caller migration target:** `ShipInstanceSerializer`

- [ ] **Grep callers:** `rg -n "to_dict\(|from_dict\(|to_json\(|from_json\(|clone\(" game tests`. Be careful — these names are generic; filter to `ShipInstance` contexts.
- [ ] Add one focused failing test per direct-call path (or one parametrized test covering all five).
- [ ] Migrate callers.
- [ ] Remove the serializer forwarders from `ShipInstance`. **Per TD-06 Weak-LLM Guardrail #1:** if any remain too widely used to migrate in one batch, leave them as documented thin shims and record the count in `findings_ledger.md`.
- [ ] **Verify:** round-trip suites green (`test_ship_instance_serializer.py`, `test_serialization.py`, `tests/unit/strategy/fleets/test_ship_instance_roundtrip.py`).
- [ ] Commit (sub-batch 5d complete).

---

## Sub-batch 5e: Bridge forwarders

**Forwarders:** `to_ship`, `update_from_ship`
**Caller migration target:** `ShipInstanceBridge`

- [ ] **Grep callers:** `rg -n "to_ship\(|update_from_ship\(" game tests`.
- [ ] Add one focused failing test for the new direct-call path.
- [ ] Migrate callers.
- [ ] Remove the bridge forwarders from `ShipInstance` (or leave documented shims if migration would be too large).
- [ ] **Verify:** `pytest tests/integration/test_fms_b_e2e.py tests/integration/test_fms_c_carrier_ai_launch.py -x` green; bridge round-trip tests green.
- [ ] Commit (sub-batch 5e complete).

---

## Phase close

- [ ] **Skip Batch 5c (cargo / deployable).** That is Phase 6 of this project and is blocked on [PROJ-431 Phase 1](../PROJ-431/plan.md).
- [ ] `python Tools/test_sharded/test_sharded.py` green.
- [ ] Record post-phase `wc -l ship_instance.py` in `findings_ledger.md`.
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-425 phase_5`.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All four sub-batches (5a, 5b, 5d, 5e) demolished or explicitly documented as deferred shims
- [ ] No single commit demolished more than one sub-batch
- [ ] Cargo/deployable (5c) intentionally **not** touched — gated to Phase 6
- [ ] Focused + sharded suites green
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after review
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6 (and surface its PROJ-431 dependency)
