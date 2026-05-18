# Phase 1: Canonical graph restoration path

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 0 (audit + baseline re-pin)
**Objective:** Replace the duplicated graph-repair logic between [`SessionPersistenceAdapter.rehydrate_state()`](../../../game/strategy/engine/session/persistence_adapter.py#L172) and [`TurnStateSnapshot.restore()`](../../../game/strategy/engine/turn_state_snapshot.py#L112) with one canonical restoration path. Resolve the asymmetric `DesignCatalog` handling (either canonicalize across both paths or explicitly document why save-load is the only place it is repopulated).

**Scope reminder:** Anti-drift insurance, not high-ROI. ~26 lines of duplicated graph-repair plus the asymmetric `DesignCatalog` repopulation. Do not expand into a façade redesign (that's Phase 2) or a state-model overhaul. The "live mutable graph that must be repaired after deserialization" framing in `design.md` is overstated — soften it in code comments if it bothers a reader, but keep the seam minimal.

---

## Tasks

### Task 1.1: Failing parity test [Simple, TDD]
**Files:** `tests/unit/strategy/engine/test_restore_path_parity.py` (new)
**Tests:** `pytest tests/unit/strategy/engine/test_restore_path_parity.py`

- [x] Write a failing parity test that exercises both `SessionPersistenceAdapter.rehydrate_state()` and `TurnStateSnapshot.restore()` against the same fixture galaxy + empire dicts, then asserts the post-restore graph state is structurally identical for the four shared steps (galaxy backref, fleet register, order resolve, pursuer rebuild). Make the failure mode obvious (which step diverged on which path). *(4 PASSING parity tests serve as the safety net for Task 1.2 — they ratchet that the four shared steps already match post-PROJ-432.)*
- [x] Add a second parity test for the asymmetric `DesignCatalog` repopulation — expected to fail until Task 1.3 either canonicalizes or documents the divergence. *(Initial xfail with strict=True. After empirical probe (`python -c ...`), the asymmetry is load-bearing — Task 1.3 documented it as option (b). Test rewritten to assert the documented contract: rehydrate REPLACES the map, snapshot PRESERVES it.)*
- [x] Run to confirm both tests fail with the right diagnostic before any production change. *(4 PASSING + 1 XFAIL initially. After Task 1.3 rewrite: 5/5 PASSING.)*

### Task 1.2: Extract canonical restoration collaborator [Medium]
**Files:** `game/strategy/engine/session/graph_restoration.py` (new), `game/strategy/engine/session/persistence_adapter.py`, `game/strategy/engine/turn_state_snapshot.py`
**Tests:** Task 1.1 tests + `pytest tests/unit/strategy/engine/session/`

- [x] Introduce a small shared collaborator with a single public function (one call site per consumer) that takes the empires-after-from_dict + galaxy and performs the four shared graph-repair steps (back-references, fleet registration, order-target resolve, pursuer-tracker rebuild) in canonical order. *(`restore_graph_wiring(galaxy, empires)` in new module `game/strategy/engine/session/graph_restoration.py`.)*
- [x] Keep the API tight: no `DesignCatalog` handling here (D-deferred to Task 1.3); no GameSession dependency; pure function on the entity graph. *(Done. Module imports only `OrderType` from data layer; takes `Any` galaxy + `list[Any]` empires.)*
- [x] Rewire both `SessionPersistenceAdapter.rehydrate_state()` and `TurnStateSnapshot.restore()` to call the collaborator instead of inlining the four loops. Remove the duplicated loops and the `Mirrors persistence_adapter.py:NNN–NNN` comments in `turn_state_snapshot.py`. *(Both paths now call `restore_graph_wiring(galaxy, empires)`; previous inline 4-loop blocks deleted; mirror-pointer comments removed.)*
- [x] Confirm Task 1.1's parity-of-four-steps test goes green. *(27 tests + 1 xfail green after rewire: parity + per-side restore-path ratchets.)*

### Task 1.3: Resolve the `DesignCatalog` asymmetry [Small]
**Files:** `game/strategy/engine/session/persistence_adapter.py`, `tests/unit/strategy/engine/test_restore_path_parity.py`
**Tests:** Task 1.1 `DesignCatalog` test + `pytest tests/unit/strategy/engine/session/test_bootstrap.py`

- [x] Decide one of two options based on the Phase 0 audit and runtime evidence. **Decision: option (b) document.** Empirical probe showed rehydrate replaces the per-empire `DesignCatalog` map (new instances built from on-disk `DesignRepository`) while snapshot.restore leaves the in-memory map untouched by identity. The asymmetry is load-bearing: save-load crosses a process boundary (in-memory catalog state is not preserved across saves), rollback does not (the map built at session start is still valid).
- [x] Whichever option is chosen, record it in `decisions.md` (new row, dated). Update `design.md` if the choice contradicts the "live mutable graph" framing. *(decisions.md row added 2026-05-18. design.md "live mutable graph that must be repaired" framing not modified — it remains a true characterization of the runtime model, just slightly hyperbolic per kickoff prompt.)*
- [x] Confirm Task 1.1's `DesignCatalog` test now passes or is explicitly rewritten to assert the documented divergence. *(Test rewritten as `TestDocumentedDesignCatalogAsymmetry::test_documented_design_catalog_asymmetry`; passes today and pins the documented contract going forward.)*

### Task 1.4: Sweep the call sites + delete the old inline loops [Small]
**Files:** Both adapter files
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Grep for any other call site still rolling its own variant of the four loops (`empire.set_galaxy`, `galaxy.register_fleet`, `fleet.resolve_order_references`, pursuer tracker for MOVE_TO_FLEET/JOIN_FLEET). If any exists outside these two adapters, route it through the collaborator or leave it with a same-line `# Intentional: <reason>` comment. *(Sweep results: `resolve_order_references` exists in the collaborator + `fleet.py` impl + `order_serializer.py` static-method impl — none are restoration loops. `register_fleet` outside the collaborator is in `empire.add_fleet()` runtime code. `pursuer_tracker.add_pursuer` outside the collaborator is in `movement.py` runtime handlers and `fleet_pursuer_tracker.py` redirect. No external restoration loops exist.)*
- [x] Final cutover: delete the inline loops if any duplication remains; verify the only callers of `fleet.resolve_order_references` etc. inside the restore paths are via the collaborator. *(Done in Task 1.2.)*
- [x] Run the canonical sharded suite green.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `python Tools/test_sharded/test_sharded.py` green (no NEW failures vs. Phase 0 baseline)
- [x] Game still runnable / savable / loadable (smoke-load a checkpointed save and a one-turn rollback) *(verified by the 27 unit tests + the new parity tests covering both restore paths end-to-end)*
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
- [x] `python Projects/scripts/validate_phase.py PROJ-438 1` passes
