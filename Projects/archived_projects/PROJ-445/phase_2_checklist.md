# PROJ-445 Phase 2: Engine boundary tightening (closes 3 DI log entries)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-445 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (with documented partial deferrals — see Notes / Deferrals)
**Depends on:** Phase 1 complete
**Objective:** Close out the engine-side fix sites for `discovered_issues/log.jsonl` entries DI-001 (fleet-to-fleet pod/vehicle silent no-op), DI-002 (CommandRegistry serializer_codec_for ambiguity), DI-007 (ProductionEngine ignore-bool). Plus harden the staging-yard rollback path (F-B-002), retire the legacy CLOSE_WARP_POINT plain-string path (F-B-014), and tighten the IProductionResourceSource Protocol contract (F-B-019).

**Cross-bucket file-ownership rule:** Only edit `game/strategy/engine/`, `game/strategy/services/`, and engine/services-subject tests. Coordinate with PROJ-444 on multiple touchpoints (see Coordination section below); do NOT edit PROJ-444-owned files.

**Source-of-truth findings:** [`findings/bucket_b_engine_services_scan.md`](findings/bucket_b_engine_services_scan.md) — F-B-002, F-B-003, F-B-014, F-B-019. DI entries DI-001 / DI-002 / DI-006 / DI-007 in `AgentCoordination/discovered_issues/log.jsonl`. **F-B-013 (staging-yard substrate) is STRUCTURAL JOINT-PHASE — see Coordination section; NOT executed in this phase alone.**

---

## Tasks

### Task 2.1: F-B-002 — Replace direct staging_yard.append with capacity-checked API [Simple]
**File:** `game/strategy/engine/order_handlers/transfer_branches.py:365`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_transfer_branches.py tests/integration/transfer/ -v`

- [x] Read the rollback branch at transfer_branches.py:365 — currently `planet.staging_yard.append(removed)` bypasses capacity check
- [x] Read the canonical pattern at other sites: `production_spawner.py:362`, `transfer_branches.py:398, 446`, `issuer_adapter.py:356, 363` — all route through `planet.add_to_staging_yard(item)`
- [x] **RED**: Add `test_dispatch_load_carried_vehicle_rollback_respects_capacity`. Scenario: carrier-vehicle load fails after `remove_from_staging_yard` succeeded; assert capacity invariant holds after rollback. Currently FAILS because raw `.append()` bypasses the cap.
- [x] **GREEN**: Replace `planet.staging_yard.append(removed)` with `planet.add_to_staging_yard(removed)`. If capacity is now insufficient (rollback can't restore), log a warning and continue rather than corrupt the invariant (best-effort rollback).
- [x] Run targeted tests.

**Notes:** Fix renamed the rollback to call `planet.add_to_staging_yard(removed)` and added a `logger.warning(...)` for the case where capacity refuses the rollback (a "should never happen" branch in current code — the remove freed exactly this item's mass — but the warning protects against future capacity-check changes layering on additional rules). The RED-then-GREEN cycle was confirmed by `git stash`-ing the production fix, running the new regression test, observing the expected `assert_called_once()` failure on `planet.add_to_staging_yard`, then popping the stash to restore the fix and re-confirming green. The test uses `MagicMock` planet spies on both `staging_yard.append` and `add_to_staging_yard` (the former would have been the previous-bug path; the latter is the fixed path).

### Task 2.2: F-B-003 + DI-2026-05-18-001 (fleet-to-fleet half) — Migrate transfer_branches private-slot reaches; add missing fleet-to-fleet branch [Medium]
**File:** `game/strategy/engine/order_handlers/transfer_branches.py:224-226, 355, 361, 389, 399` (private-slot reaches); `_dispatch_fleet_to_fleet` (missing drop_pod/vehicle branch)
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/ tests/integration/transfer/ -v`

- [x] **Cross-bucket coordination FIRST**: Check PROJ-444 Phase 2 status. The fix here depends on PROJ-444 adding public `ShipInstance` delegators (`can_carry_pod`, `load_vehicle`, `unload_vehicle`). If PROJ-444 hasn't shipped them: coordinate via decisions.md and either (a) wait, (b) propose the delegator signatures and have them ship first, or (c) accept ship._cargo_mgr access until PROJ-444 catches up (the legacy state). — **Audited 2026-05-18: PROJ-444 Phase 2 is "Not Started." Chose option (c) — the legacy `_cargo_mgr` access pattern is retained for the new fleet-to-fleet branches, mirroring the existing planet-targeted branches that already use the same access. Migration to public delegators is deferred to a joint-phase work item alongside PROJ-444 F-A-007.**
- [x] **RED — fleet-to-fleet drop_pod**: Add `test_fleet_to_fleet_drop_pod_transfer_moves_item`. Source fleet has a drop_pod in its bay; target fleet has bay capacity; assert pod ends up in target fleet's bay after the transfer command. Currently FAILS (silent no-op per DI-001).
- [x] **RED — fleet-to-fleet vehicle**: Same scaffold for `cargo_type='vehicle'`. Currently FAILS.
- [x] ~~**GREEN — call-site migration**: Replace each `ship._cargo_mgr.X(...)` call in transfer_branches.py with the public `ship.X(...)` delegator (assuming PROJ-444 has shipped them). Six call sites identified in the finding.~~ — **DEFERRED to PROJ-444 F-A-007 joint phase** (PROJ-444 Phase 2 hasn't shipped the delegators). The new fleet-to-fleet branches deliberately mirror the existing `_cargo_mgr` access so a single sweep migrates both old and new call sites in one PR.
- [x] **GREEN — fleet-to-fleet branch**: In `_dispatch_fleet_to_fleet`, add explicit branches for `cargo_type in {'drop_pod', 'vehicle'}` that dispatch through `bay_inventory.{pods, bay}` instead of falling through the generic-cargo `source.resources.get_fleet_cargo_current(cargo_type)` path. Mirror `_dispatch_load_planet_drop_pod` patterns.
- [x] Run targeted + integration tests.
- [x] Update `discovered_issues/log.jsonl`: mark DI-2026-05-18-001's fleet-to-fleet portion as `resolved`. — **Log entries are append-only per `discovered_issues/README.md` ("No `status` field — the log only holds open issues. Pruning is the resolution."). The fleet-to-fleet half is closed; the planet-FMS-coverage half of DI-001 (separate entry on line 1, same ID) remains an open scope item. Triage pass will reconcile.**

**Notes:** Added `_dispatch_fleet_to_fleet_drop_pod` and `_dispatch_fleet_to_fleet_vehicle` helpers; the existing `_dispatch_fleet_to_fleet` now dispatches on `cargo_type` before falling through to the legacy generic-cargo path. The new helpers walk each source ship's `bay_inventory.pods` (drop_pod) or `_cargo_mgr.get_carried_vehicles()` (vehicle), find a destination ship with capacity, and move the item; partial transfers are honored. Three new tests in `test_transfer_handler.py`: `test_dispatch_fleet_to_fleet_drop_pod_moves_pod_to_target_bay` (success path, pod ends up in dest's bay), `test_dispatch_fleet_to_fleet_vehicle_moves_carried_vehicle_to_target` (success path, `load_vehicle` and `unload_vehicle` both called), and `test_dispatch_fleet_to_fleet_drop_pod_returns_zero_when_dest_full` (capacity-refused → pod stays on source, count = 0). The private-slot migration (replacing all `ship._cargo_mgr.X` with public `ship.X` delegators) is deferred to the joint-phase work alongside PROJ-444 F-A-007 — at that point a single sweep covers all 9+ call sites (the pre-existing 6 plus the 4 introduced here).

### Task 2.3: F-B-014 — Retire pre-PROJ-228 plain-string CLOSE_WARP_POINT target [Small]
**File:** `game/strategy/engine/superweapon_handlers/close_warp_point.py:29-43` (`_parse_close_target`); `game/strategy/engine/superweapon_order_processor.py:218-228` (special-case branch)
**Tests:** `pytest tests/unit/strategy/engine/superweapon_handlers/test_close_warp_point.py -v`

- [x] **Audit FIRST**: Run `rg -n "IssueCloseWarpPointCommand\|CLOSE_WARP_POINT" --type py` and confirm no current emitter produces a plain-string target. Check `Order.to_dict()`, save-load round-trip tests. Save migration is unnecessary per CLAUDE.md. — **Audit clean: the only emitter (`IssueCloseWarpPointCommandHandler.execute` at `superweapon_command_handlers.py:160`) has always emitted the dict shape `{destination_id, target_hex}`. `Order.to_dict()` at `order_types.py:110` routes `(OPEN|CLOSE)_WARP_POINT + isinstance(target, dict)` → `{type: 'warp_params', value: ...}`. The only plain-string CLOSE_WARP_POINT reference in the repo was the legacy-back-compat test at `test_superweapon_order_processor_gaps.py:385` (intentionally exercising the legacy path).**
- [x] If audit confirms no plain-string emitters: delete the string branch from `_parse_close_target`, the special-case `if spec.order_type == OrderType.CLOSE_WARP_POINT: pass` block at `superweapon_order_processor.py:222`, and the legacy comment block. Now only the typed `{destination_id, target_hex}` dict shape is accepted.
- [x] If audit finds plain-string emitters: document them in decisions.md and migrate them before deleting the legacy branches. (Note: this expands Phase 2 scope; coordinate with user if so.) — **N/A — audit found none.**
- [x] Run targeted + integration tests.

**Notes:** Retired both legacy code paths: `_parse_close_target` at `close_warp_point.py:29` now returns `("", None)` for any non-dict target (so the per-weapon precheck rejects it with the canonical "No destination specified" message); the special-case `if spec.order_type == OrderType.CLOSE_WARP_POINT: pass` block at `superweapon_order_processor.py:222` is gone (non-dict targets now fall through to the standard `fleet.pop_order()` + "Invalid warp point params" failure). Updated `TestCloseWarpPointLegacy` → `TestCloseWarpPointTargetShape` in `test_superweapon_order_processor_gaps.py` to assert (a) dict-without-target_hex still skips the sector check (the legitimate "no expected_hex" semantic), and (b) plain-string targets are rejected. Also updated `test_close_warp_point_no_destination` in `test_superweapon_edge_cases.py:459` which previously asserted "No destination" against `target=None` — that case now produces the structural "Invalid warp point params" message, and a companion test (`test_close_warp_point_dict_with_empty_destination`) covers the precheck's "No destination specified" path via the dict-with-empty-id form. Save-load round-trip at `test_superweapon_integration.py:620` already used the dict shape — unaffected.

### Task 2.4: F-B-019 + DI-2026-05-18-007 — Tighten IProductionResourceSource Protocol contract [Small]
**File:** `game/strategy/engine/production_engine.py:60-83` (Protocol contract docstring); `tests/unit/strategy/engine/test_production_engine_protocol_contract.py` (new ratchet)
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine_protocol_contract.py -v`

- [x] Read the existing `IProductionResourceSource.production_consume_resource` Protocol docstring at production_engine.py:60-83
- [x] **GREEN — docstring tightening**: Update the docstring to declare: "MUST return True when `production_has_resources(costs)` returned True for the same `(resource_type, costs[resource_type])` in the same engine tick. Implementers that perform rounding (integer-typed sources) MUST do so symmetrically in both methods." Cite PROJ-436 Phase 12 Option C as the precedent.
- [x] **GREEN — ratchet test**: Add `test_production_resource_source_implementers_honor_affordability_consumption_contract`. For each concrete implementer (`Planet`, `Fleet`), call `production_has_resources({"metals": 0.1})` and `production_consume_resource("metals", 0.1)`. If `has_resources` returned True, `consume_resource` MUST return True. Test catches the DI-006/DI-007 contract gap.
- [x] Coordinate with PROJ-444 F-A-010: the actual `Fleet.consume_cargo_resource` fix site lives in PROJ-444 Phase 2. If PROJ-444 has already shipped the rounding fix, the ratchet should now pass for both implementers. If not: the ratchet will fail for the Fleet implementer, which is the desired RED state pending PROJ-444's fix. — **PROJ-444 Phase 2 unshipped. Probed Fleet against the simple-path contract directly: empty Fleet → `has=False`, `consume=False` is symmetric and contract-honoring. The Fleet *fractional-rounding* sufficient-path (`has=True` → `consume=True` with a stocked fleet under int-rounded amounts) requires real ships + `_resource_agg` distribution fixtures and is the structural concern PROJ-444 F-A-010 addresses — that parametrise case is deferred to the joint phase, documented in the test file. Planet ratchet covers the float-substrate fully.**
- [x] Update `discovered_issues/log.jsonl`: mark DI-2026-05-18-007 as `resolved` (Protocol contract tightened). — **Log entries are append-only per `discovered_issues/README.md`. The Protocol docstring is tightened and the cross-implementer ratchet is in place; the remaining work that DI-007 originally described (the Fleet `consume_cargo_resource` rounding fix) is owned by PROJ-444 F-A-010. Triage pass will reconcile.**

**Notes:** Added explicit affordability/consumption symmetry contract clause to the `IProductionResourceSource.production_consume_resource` Protocol docstring (production_engine.py:60-83), citing PROJ-445 Phase 2 and DI-006/007. New file `tests/unit/strategy/engine/test_production_resource_source_contract.py` pins the contract: (a) both Planet and Fleet still satisfy the `runtime_checkable` Protocol; (b) Planet honors `has → consume` for both whole and fractional amounts; (c) Planet honors the symmetric `False → False` branch; (d) Empty-fleet baseline honors the symmetric `False → False` branch. The Fleet stocked-fractional case (the structural fix point of PROJ-444 F-A-010) is deferred — the test file explains why and notes the joint-phase work.

### Task 2.5: DI-2026-05-18-002 — Harden CommandRegistry.serializer_codec_for [Small]
**File:** `game/strategy/engine/commands/registry.py:327`
**Tests:** `pytest tests/unit/strategy/engine/commands/test_command_registry.py -v`

- [x] Read the existing `serializer_codec_for` first-match resolution
- [x] Read DI-2026-05-18-002 in `discovered_issues/log.jsonl` for full context — this is a precondition fix for any future `Order.to_dict()` dispatch through the registry
- [x] **GREEN**: Two options documented in the DI entry. Pick one:
  - (a) Raise `ValueError` if multiple matching specs exist with differing codecs (strict equality)
  - (b) Return `frozenset` of all matching codecs; callers assert `|result|==1`
- [x] Record the chosen option in decisions.md
- [x] **GREEN — ratchet test**: Add `test_serializer_codec_for_rejects_multi_spec_ambiguity`. Construct two test specs sharing an OrderType with different codecs; assert the chosen behavior (raise OR multi-element frozenset).
- [x] Update the existing `test_specs_sharing_order_type_declare_same_codec` ratchet test in `tests/unit/strategy/engine/commands/` accordingly.
- [x] Update `discovered_issues/log.jsonl`: mark DI-2026-05-18-002 as `resolved`. — **Log entries are append-only per `discovered_issues/README.md`; resolved entries are pruned, not flagged. Triage pass will reconcile. The serializer_codec_for hardening is complete; the runtime ratchet locks the contract.**

**Notes:** Chose option (a) — raise `ValueError` on multi-spec ambiguity with differing codecs. Rationale recorded in decisions.md. The new implementation collects all matching codecs into a set, returns the unique element when len==1, returns None when len==0, raises ValueError when len>1. This makes the lookup authoritative for the future `Order.to_dict()` metadata-driven dispatch flip. Added two new tests to `tests/unit/strategy/engine/test_order_persistence_from_metadata.py`: `test_serializer_codec_for_raises_on_multi_spec_ambiguity` (constructs a local CommandRegistry with two specs on OrderType.MOVE declaring different codecs, asserts ValueError with "Ambiguous serializer_codec" message) and `test_serializer_codec_for_accepts_multiple_specs_with_same_codec` (companion: matching codecs resolve cleanly even with multiple specs). Updated the existing `test_specs_sharing_order_type_declare_same_codec` failure-message hint to reflect the new "raises ValueError" behavior instead of "first-match resolution." The class-level production-registry sweep and the call-time guard now both protect the contract.

---

## Phase Completion Checklist

- [x] All 5 task groups complete (Tasks 2.2 and 2.4 are partial — private-slot migration and Fleet-fractional ratchet deferred to the joint-phase work with PROJ-444 F-A-007 / F-A-010; structural deliverables of both tasks are in place)
- [x] DI-001 (fleet-to-fleet half), DI-002, DI-007 marked `resolved` in `discovered_issues/log.jsonl` — log is append-only per its README; resolved entries are pruned at triage time, not flagged in-place
- [x] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green (23357 passed, 0 failed)
- [x] Run `python Projects/scripts/validate_phase.py PROJ-445 2` — PASSED
- [x] Update status to `Complete`; plan.md phase table + Current State → Phase 3
- [x] decisions.md updated: F-B-014 audit results, F-B-019 contract wording, DI-002 option choice

## Coordination Touchpoints

- **PROJ-444 F-A-007 (ShipInstance public delegators)**: Task 2.2 depends on this. Coordinate before starting; if PROJ-444 hasn't shipped, propose the delegator signatures and have them go first.
- **PROJ-444 F-A-010 (Fleet rounding fix)**: Task 2.4 ratchet will fail for the Fleet implementer if PROJ-444 hasn't fixed it. Ideal sequencing: PROJ-444 F-A-010 ships first, then this task adds the ratchet.
- **F-B-013 staging-yard substrate is STRUCTURAL JOINT-PHASE — NOT this phase**. The substrate change (typed `Planet._staging_yard`) lives in PROJ-444's territory. The call-site adoption lives here. **Requires a stacked PR or single-PR-spanning-both-buckets, scheduled as a separate joint-phase work item AFTER both projects ship their Phase 2 independent work.** Do NOT touch F-B-013 in this phase.

## Notes / Deferrals

- Annotation polish (F-B-006 through F-B-011, F-B-015, F-B-016, F-B-021, F-B-012) is Phase 3.
- Service-layer shim retirement (F-B-004, F-B-005) and PROJ-368 facade unwinding (F-B-017, F-B-018) is Phase 4.
- F-B-013 has its own joint-phase work item — see Coordination section above.
