# PROJ-450: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Architecture analysis

`Planet._staging_yard: List[Dict[str, Any]]` is the only major strategy substrate that still holds untyped dicts. Every other carried-vehicle storage in the codebase (`ShipInstance.bay_inventory.bay: list[CarriedVehicle]`, `ShipInstance.bay_inventory.pods: list[DropPod]`) is typed end-to-end. The staging yard's dict substrate forces a flatten/inflate round-trip at every transfer boundary — every typed pod from a fleet bay is flattened to a dict before landing in the staging yard, then dict-inflated back to typed when it leaves. The 3 helpers in `transfer_branches.py:41-87` are the inflate side; the explicit `.to_dict()` calls in `transfer_branches.py:412, 454-460` and `issuer_adapter.py:363` are the flatten side. This was deferred from PROJ-431 Phase 1d and stayed deferred through PROJ-444..447.

The cancelled PROJ-444..447 Joint A attempt (May 2026) tried to land the substrate widening in one cross-bucket coordination phase. The Stage 3 preflight discovered three hard blockers that all required cross-bucket cooperation, the simplest of which (the UI reader at `strategy_detail_fmt.py:285-297`) would have caused a silent UI regression if the substrate widened without the UI reader migrating in lockstep. The Joint A author recommended Path A (engine-only API cleanup) as a checkpoint, but the four-way joint phase to land the literal substrate widening never opened — Codex r4 cancelled the layer-bucket projects entirely and re-bundled the substrate work into PROJ-450 as a single job-oriented project.

## Sequencing rationale

The 6-phase breakdown:
- **Phase 0 — re-verify audit.** The Stage 3 preflight numbers (310 occurrences, 49 files) are the audit-of-record. Re-verify at HEAD because the preflight is dated 2026-05-18 and PROJ-444..447 closure work may have shifted counts.
- **Phase 1 — Path A engine cleanup.** The preflight's recommended Path A: widen `add_to_staging_yard` to accept typed inputs, add `pop_staging_yard_typed`, move helpers into Planet. Substrate stays dict. Engine handlers drop their flatten/inflate. **This is the literal "Path A" from preflight §3.1.**
- **Phase 2 — substrate widening.** The actual type change. Save format stays dict (via `_normalize_to_typed` on load + per-entry `.to_dict()` on save). A one-phase dict-projection bridge property keeps the UI reader working until Phase 3.
- **Phase 3 — UI reader + validator + write service + facade tightening.** Closes the three hard blockers from preflight §2. **Replaces the Phase-2 dict-projection bridge with a permanent typed read-only property** `Planet.staging_yard -> Tuple[CarriedVehicle | DropPod, ...]` (Option A per codex audit, see decisions.md). Mutations route through `add_to_staging_yard` / `pop_staging_yard_typed` / `remove_from_staging_yard` — no setter, no list-mutation through the public name.
- **Phase 4 — integration test migration.** The unowned-in-old-partition cluster.
- **Phase 5 — static guard tightening.** Defensive.

## Why partial Path A (substrate widening) is justified — inlined for self-containment

(Inlined from `Projects/archived_projects/PROJ-444to447_coordinator/stage_3_joint_a_preflight_findings.md` §3.1; the archive remains as background reading but is not a mandatory pre-read.)

The cancelled PROJ-444..447 Joint A attempt (May 2026) tried to land both the engine-side API cleanup AND the literal substrate widening AND the cross-bucket reader migrations as one transaction. The Stage 3 preflight found this could not be a single atomic phase because of three hard blockers (UI reader silent-skip, integration test in-place mutations, validator shape probes) that all sat at the reader side, not the substrate side. The preflight recommended Path A as a **standalone checkpoint** — engine-side flatten/inflate cleanup with the substrate STILL dict-typed — because Path A removes the engine-side helpers (3 in `transfer_branches.py:41-87` + the flatten calls at `:412, :454-460` + `issuer_adapter.py:363`) without changing the underlying type. Path A by itself reduces engine surface complexity and lets the substrate-widening + reader-migration steps follow in their own phases without rolling back.

PROJ-450 takes Path A first (Phase 1), then substrate widening behind a one-phase bridge (Phase 2), then reader migration + permanent typed-read-only property (Phase 3). This phasing is what makes the four-way joint-phase cycle from PROJ-444..447 tractable as a single project: each phase is independently green; the bridge-then-tightening pattern from Phase 2 → Phase 3 is the same pattern PROJ-436 Phase 5 / Phase 12 used during data layer migration.

## BLOCKER #1 (UI reader silent-skip) — the rationale for permanent typed-readonly

(Inlined from Stage 3 preflight §2.1 + 2026-05-19 codex audit BLOCKER #1 finding.)

The UI reader at `game/ui/screens/strategy_detail_fmt.py:285-297` uses `getattr(planet, "staging_yard", None)` and then `for item in staging_yard: if not isinstance(item, dict): continue`. The same `getattr` pattern is used by `game/strategy/facade/slices/planet_slice.py:194-216` and `game/strategy/facade/dto/planet_dto.py:99-148`. Three problems if the Phase-2 bridge were deleted in Phase 3 without a replacement:
1. PROJ-449 Phase 3 already deleted the original `@property staging_yard` accessor on Planet — Phase 2's bridge was a temporary re-addition.
2. After PROJ-449 Phase 3, plain `_staging_yard` is the underlying field; there is no public attribute alias.
3. `getattr(planet, "staging_yard", None)` returns `None` when the attribute is absent, NOT AttributeError. The UI / facade / DTO readers all guard with `isinstance(staging_yard, list)` and silently render zero items — a silent UI regression for live planets with staging contents.

Option A (chosen): replace the Phase-2 dict-projection bridge with a permanent typed read-only `Planet.staging_yard -> Tuple[CarriedVehicle | DropPod, ...]` property. External readers keep their stable public surface; mutations route through the write API only. No setter. Option B (rejected): rewrite every reader to use `_staging_yard` directly before deleting the bridge — would have required a new Phase 2.5 expanding the reader-migration into a third phase. Option A is cheaper, preserves encapsulation, and matches the PROJ-436 read-protocol typed-narrowing pattern.

## Key patterns reused

- **PROJ-431 Phase 1d typed substrates** (`bay_inventory.bay: list[CarriedVehicle]`, `bay_inventory.pods: list[DropPod]`) — Phase 2's substrate change mirrors this exact pattern.
- **PROJ-436 Phase 5 / Phase 12 dict-projection bridge during multi-phase migrations** — Phase 2's temporary projection property is a single-phase migration bridge, not an enduring shim.
- **PROJ-372 planet_serde extraction** — Phase 2's `_normalize_to_typed` helper lives alongside `planet_from_dict_kwargs` per this pattern.
- **PROJ-446 Phase 2 typed-protocol migration** — Phase 3's `IPlanetMutator` signature tightening mirrors the `IShipInstance.cargo_contents` typed-narrowing pattern PROJ-446 used.

## Dependencies & Risks

1. **PROJ-449 Phase 3 hard dependency.** Phase 0 verifies. The Planet @property cluster from PROJ-436 Phase 4f must be deleted first; otherwise the substrate type change cascades through every property reader.
2. **Silent UI regression risk (preflight BLOCKER #1).** If Phase 2 widened the substrate without Phase 3 migrating the UI reader in the same project, the planet detail panel would silently render empty staging yards. Mitigation: Phase 2 deliberately keeps a dict-projection bridge property alive; Phase 3 migrates the UI reader BEFORE deleting the bridge.
3. **Integration test cluster ownership (preflight BLOCKER #2).** `tests/integration/test_fms_*` was unowned in PROJ-444..447. Codex r4 explicitly assigns these to PROJ-450 Phase 4.
4. **Save-format change risk.** Save format MUST stay dict. `_normalize_to_typed` converts on load; `.to_dict()` serializes on save. Verify in Phase 2 Task 2.1's RED test (`test_save_format_remains_dict_shape`).
5. **Rollback semantics in `transfer_branches.py:373`.** The `add_to_staging_yard(removed)` rollback path needs `removed` to be acceptable to the typed `add_to_staging_yard`. Phase 2 widened acceptance, so this works — but verify with a focused rollback test.

## Opportunities discovered

- **`_dispatch_drop_pod_load` and `_dispatch_carried_vehicle_load` simplification.** After Phase 1, the loops can pop via `pop_staging_yard_typed(i)` directly instead of `remove_from_staging_yard(i)` followed by `_pod_from_dict(removed)` / `_staging_yard_carried_vehicle(item)`. Cleaner.
- **`production_spawner.py` typed construction.** Phase 2 Task 2.5 takes this — currently `production_spawner.py:347-360` builds dicts and calls `add_to_staging_yard(dict)`; after Phase 2 it builds typed `CarriedVehicle(...)` / `DropPod(...)` and passes them.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
