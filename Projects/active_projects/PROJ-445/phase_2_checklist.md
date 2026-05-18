# PROJ-445 Phase 2: Engine boundary tightening (closes 3 DI log entries)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-445 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** Phase 1 complete
**Objective:** Close out the engine-side fix sites for `discovered_issues/log.jsonl` entries DI-001 (fleet-to-fleet pod/vehicle silent no-op), DI-002 (CommandRegistry serializer_codec_for ambiguity), DI-007 (ProductionEngine ignore-bool). Plus harden the staging-yard rollback path (F-B-002), retire the legacy CLOSE_WARP_POINT plain-string path (F-B-014), and tighten the IProductionResourceSource Protocol contract (F-B-019).

**Cross-bucket file-ownership rule:** Only edit `game/strategy/engine/`, `game/strategy/services/`, and engine/services-subject tests. Coordinate with PROJ-444 on multiple touchpoints (see Coordination section below); do NOT edit PROJ-444-owned files.

**Source-of-truth findings:** [`findings/bucket_b_engine_services_scan.md`](findings/bucket_b_engine_services_scan.md) — F-B-002, F-B-003, F-B-014, F-B-019. DI entries DI-001 / DI-002 / DI-006 / DI-007 in `AgentCoordination/discovered_issues/log.jsonl`. **F-B-013 (staging-yard substrate) is STRUCTURAL JOINT-PHASE — see Coordination section; NOT executed in this phase alone.**

---

## Tasks

### Task 2.1: F-B-002 — Replace direct staging_yard.append with capacity-checked API [Simple]
**File:** `game/strategy/engine/order_handlers/transfer_branches.py:365`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_transfer_branches.py tests/integration/transfer/ -v`

- [ ] Read the rollback branch at transfer_branches.py:365 — currently `planet.staging_yard.append(removed)` bypasses capacity check
- [ ] Read the canonical pattern at other sites: `production_spawner.py:362`, `transfer_branches.py:398, 446`, `issuer_adapter.py:356, 363` — all route through `planet.add_to_staging_yard(item)`
- [ ] **RED**: Add `test_dispatch_load_carried_vehicle_rollback_respects_capacity`. Scenario: carrier-vehicle load fails after `remove_from_staging_yard` succeeded; assert capacity invariant holds after rollback. Currently FAILS because raw `.append()` bypasses the cap.
- [ ] **GREEN**: Replace `planet.staging_yard.append(removed)` with `planet.add_to_staging_yard(removed)`. If capacity is now insufficient (rollback can't restore), log a warning and continue rather than corrupt the invariant (best-effort rollback).
- [ ] Run targeted tests.

### Task 2.2: F-B-003 + DI-2026-05-18-001 (fleet-to-fleet half) — Migrate transfer_branches private-slot reaches; add missing fleet-to-fleet branch [Medium]
**File:** `game/strategy/engine/order_handlers/transfer_branches.py:224-226, 355, 361, 389, 399` (private-slot reaches); `_dispatch_fleet_to_fleet` (missing drop_pod/vehicle branch)
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/ tests/integration/transfer/ -v`

- [ ] **Cross-bucket coordination FIRST**: Check PROJ-444 Phase 2 status. The fix here depends on PROJ-444 adding public `ShipInstance` delegators (`can_carry_pod`, `load_vehicle`, `unload_vehicle`). If PROJ-444 hasn't shipped them: coordinate via decisions.md and either (a) wait, (b) propose the delegator signatures and have them ship first, or (c) accept ship._cargo_mgr access until PROJ-444 catches up (the legacy state).
- [ ] **RED — fleet-to-fleet drop_pod**: Add `test_fleet_to_fleet_drop_pod_transfer_moves_item`. Source fleet has a drop_pod in its bay; target fleet has bay capacity; assert pod ends up in target fleet's bay after the transfer command. Currently FAILS (silent no-op per DI-001).
- [ ] **RED — fleet-to-fleet vehicle**: Same scaffold for `cargo_type='vehicle'`. Currently FAILS.
- [ ] **GREEN — call-site migration**: Replace each `ship._cargo_mgr.X(...)` call in transfer_branches.py with the public `ship.X(...)` delegator (assuming PROJ-444 has shipped them). Six call sites identified in the finding.
- [ ] **GREEN — fleet-to-fleet branch**: In `_dispatch_fleet_to_fleet`, add explicit branches for `cargo_type in {'drop_pod', 'vehicle'}` that dispatch through `bay_inventory.{pods, bay}` instead of falling through the generic-cargo `source.resources.get_fleet_cargo_current(cargo_type)` path. Mirror `_dispatch_load_planet_drop_pod` patterns.
- [ ] Run targeted + integration tests.
- [ ] Update `discovered_issues/log.jsonl`: mark DI-2026-05-18-001's fleet-to-fleet portion as `resolved`.

### Task 2.3: F-B-014 — Retire pre-PROJ-228 plain-string CLOSE_WARP_POINT target [Small]
**File:** `game/strategy/engine/superweapon_handlers/close_warp_point.py:29-43` (`_parse_close_target`); `game/strategy/engine/superweapon_order_processor.py:218-228` (special-case branch)
**Tests:** `pytest tests/unit/strategy/engine/superweapon_handlers/test_close_warp_point.py -v`

- [ ] **Audit FIRST**: Run `rg -n "IssueCloseWarpPointCommand\|CLOSE_WARP_POINT" --type py` and confirm no current emitter produces a plain-string target. Check `Order.to_dict()`, save-load round-trip tests. Save migration is unnecessary per CLAUDE.md.
- [ ] If audit confirms no plain-string emitters: delete the string branch from `_parse_close_target`, the special-case `if spec.order_type == OrderType.CLOSE_WARP_POINT: pass` block at `superweapon_order_processor.py:222`, and the legacy comment block. Now only the typed `{destination_id, target_hex}` dict shape is accepted.
- [ ] If audit finds plain-string emitters: document them in decisions.md and migrate them before deleting the legacy branches. (Note: this expands Phase 2 scope; coordinate with user if so.)
- [ ] Run targeted + integration tests.

### Task 2.4: F-B-019 + DI-2026-05-18-007 — Tighten IProductionResourceSource Protocol contract [Small]
**File:** `game/strategy/engine/production_engine.py:60-83` (Protocol contract docstring); `tests/unit/strategy/engine/test_production_engine_protocol_contract.py` (new ratchet)
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine_protocol_contract.py -v`

- [ ] Read the existing `IProductionResourceSource.production_consume_resource` Protocol docstring at production_engine.py:60-83
- [ ] **GREEN — docstring tightening**: Update the docstring to declare: "MUST return True when `production_has_resources(costs)` returned True for the same `(resource_type, costs[resource_type])` in the same engine tick. Implementers that perform rounding (integer-typed sources) MUST do so symmetrically in both methods." Cite PROJ-436 Phase 12 Option C as the precedent.
- [ ] **GREEN — ratchet test**: Add `test_production_resource_source_implementers_honor_affordability_consumption_contract`. For each concrete implementer (`Planet`, `Fleet`), call `production_has_resources({"metals": 0.1})` and `production_consume_resource("metals", 0.1)`. If `has_resources` returned True, `consume_resource` MUST return True. Test catches the DI-006/DI-007 contract gap.
- [ ] Coordinate with PROJ-444 F-A-010: the actual `Fleet.consume_cargo_resource` fix site lives in PROJ-444 Phase 2. If PROJ-444 has already shipped the rounding fix, the ratchet should now pass for both implementers. If not: the ratchet will fail for the Fleet implementer, which is the desired RED state pending PROJ-444's fix.
- [ ] Update `discovered_issues/log.jsonl`: mark DI-2026-05-18-007 as `resolved` (Protocol contract tightened).

### Task 2.5: DI-2026-05-18-002 — Harden CommandRegistry.serializer_codec_for [Small]
**File:** `game/strategy/engine/commands/registry.py:327`
**Tests:** `pytest tests/unit/strategy/engine/commands/test_command_registry.py -v`

- [ ] Read the existing `serializer_codec_for` first-match resolution
- [ ] Read DI-2026-05-18-002 in `discovered_issues/log.jsonl` for full context — this is a precondition fix for any future `Order.to_dict()` dispatch through the registry
- [ ] **GREEN**: Two options documented in the DI entry. Pick one:
  - (a) Raise `ValueError` if multiple matching specs exist with differing codecs (strict equality)
  - (b) Return `frozenset` of all matching codecs; callers assert `|result|==1`
- [ ] Record the chosen option in decisions.md
- [ ] **GREEN — ratchet test**: Add `test_serializer_codec_for_rejects_multi_spec_ambiguity`. Construct two test specs sharing an OrderType with different codecs; assert the chosen behavior (raise OR multi-element frozenset).
- [ ] Update the existing `test_specs_sharing_order_type_declare_same_codec` ratchet test in `tests/unit/strategy/engine/commands/` accordingly.
- [ ] Update `discovered_issues/log.jsonl`: mark DI-2026-05-18-002 as `resolved`.

---

## Phase Completion Checklist

- [ ] All 5 task groups complete
- [ ] DI-001 (fleet-to-fleet half), DI-002, DI-007 marked `resolved` in `discovered_issues/log.jsonl`
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-445 2` — PASSED
- [ ] Update status to `Complete`; plan.md phase table + Current State → Phase 3
- [ ] decisions.md updated: F-B-014 audit results, F-B-019 contract wording, DI-002 option choice

## Coordination Touchpoints

- **PROJ-444 F-A-007 (ShipInstance public delegators)**: Task 2.2 depends on this. Coordinate before starting; if PROJ-444 hasn't shipped, propose the delegator signatures and have them go first.
- **PROJ-444 F-A-010 (Fleet rounding fix)**: Task 2.4 ratchet will fail for the Fleet implementer if PROJ-444 hasn't fixed it. Ideal sequencing: PROJ-444 F-A-010 ships first, then this task adds the ratchet.
- **F-B-013 staging-yard substrate is STRUCTURAL JOINT-PHASE — NOT this phase**. The substrate change (typed `Planet._staging_yard`) lives in PROJ-444's territory. The call-site adoption lives here. **Requires a stacked PR or single-PR-spanning-both-buckets, scheduled as a separate joint-phase work item AFTER both projects ship their Phase 2 independent work.** Do NOT touch F-B-013 in this phase.

## Notes / Deferrals

- Annotation polish (F-B-006 through F-B-011, F-B-015, F-B-016, F-B-021, F-B-012) is Phase 3.
- Service-layer shim retirement (F-B-004, F-B-005) and PROJ-368 facade unwinding (F-B-017, F-B-018) is Phase 4.
- F-B-013 has its own joint-phase work item — see Coordination section above.
