# Phase 1: Scope audit — TD-06 shim caller inventory

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-461 1`
> 2. Caller inventory written to `findings/phase_1_caller_audit.md`
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Build the per-shim caller table that the rest of the project will execute against. Identify which of the 5 TD-06 high-value shim clusters can be retired by migrating callers to the underlying manager APIs (`ship._cargo_mgr.*`, `ship._resource_mgr.*`, `ShipInstanceBridge.*`, `ShipInstanceSerializer.*`), which must keep a thin facade, and what the per-cluster LOC drop will be.

**No code changes in this phase.** Audit + scope-decision only.

---

## Tasks

### Task 1.1: Confirm baseline LOC [Simple]
**File:** `game/strategy/data/ship_instance.py` (read-only)

- [ ] Run: `wc -l game/strategy/data/ship_instance.py`. Record the current LOC.
- [ ] Compare against the PROJ-459 Phase 3 verdict baseline (789 LOC at 2026-05-19, post PROJ-449 + PROJ-454). Note any drift.
- [ ] Record LOC + delta in `findings/phase_1_caller_audit.md`.

### Task 1.2: Enumerate the 5 TD-06 shim clusters [Simple]
**File:** `game/strategy/data/ship_instance.py` (read-only, class docstring at L106-125)

- [ ] Read the class docstring's "Retained-shim entry points" catalog at `ship_instance.py:106-125`.
- [ ] List each shim cluster with its method names and the rough LOC contribution. Initial inventory (verify each):
  - **Serializer cluster** (~70 LOC): `to_dict`, `from_dict`, `to_json`, `from_json`, `clone`
  - **Bridge cluster** (~40 LOC): `to_ship`, `update_from_ship`
  - **Resource-manager facades** (~80 LOC): `consume_resource`, `get_resource_capacity`, `get_current_resource`, `get_all_resource_costs_per_hex`, `get_all_resource_costs_per_turn`, `get_warp_resource_costs`, `resupply`
  - **Write-service facades** (~30 LOC): `set_component_enabled`, `repair`
  - **Cargo-manager facade** (~20 LOC): any `_cargo_mgr` delegators on `ShipInstance` directly (verify; some may already be retired)

### Task 1.3: Per-shim caller count [Medium]
**Tool:** `Grep` / `git grep`

- [ ] For each method name in Task 1.2, count callers across `game/` + `tests/`:
  - `git grep -c "\.to_dict()" game/ tests/ | grep -v "^.*:0$"`
  - Same shape for the other ~15 method names.
- [ ] Tabulate: shim cluster → method → call-site count in `game/` → call-site count in `tests/` → total.
- [ ] Total should be roughly ~910 callers per the PROJ-425 Phase 5d/5e estimate (verify; the actual number may have shrunk after PROJ-454 retirements).

### Task 1.4: Classify caller paths [Medium]
**For each shim cluster**, for each caller:

- [ ] Determine: can this caller move to the underlying manager API directly, OR does the caller need the facade (e.g., the caller is at a layer that should not know about `_cargo_mgr` internals)?
- [ ] Group callers by classification. Record per cluster the breakdown: migrate-to-manager / keep-facade / unclear.

### Task 1.5: Decide which clusters retire vs. keep [Simple]
**File:** `findings/phase_1_caller_audit.md`

- [ ] For each cluster: if >80% of callers can migrate to the manager API, the cluster is a retirement candidate. Record decision per cluster.
- [ ] Order the retirement candidates by LOC payoff (largest first).
- [ ] Sketch a per-cluster migration phase plan (Phase 2 = cluster A, Phase 3 = cluster B, ...).

### Task 1.6: Update plan.md phase table [Simple]
**File:** `Projects/active_projects/PROJ-461/plan.md`

- [ ] Replace the `(TBD — scope phase before any code phases)` row with the actual phase sequence from Task 1.5.
- [ ] Update Current State to reflect Phase 1 complete and next concrete phase.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] `findings/phase_1_caller_audit.md` exists with per-cluster caller counts + classification + retirement decisions
- [ ] plan.md phase table populated with the per-cluster migration sequence
- [ ] plan.md Current State updated; ready for the first migration phase
- [ ] No production code touched in this phase
- [ ] Sharded suite green (baseline confirmed for downstream phases)
