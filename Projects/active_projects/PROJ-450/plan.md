# PROJ-450: Typed staging-yard substrate completion

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-450` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-450 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03a-continue-working (serial on `main`, no worktrees — per standing user preference)

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Re-verify Stage 3 preflight audit; verify PROJ-449 Phase 3 precondition | Not Started | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Path A engine-only API cleanup (typed accept + typed pop) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Substrate widening (`_staging_yard: List[CarriedVehicle \| DropPod]`) + serde normalization | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI reader migration + DTO / validator / write-service tightening | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Integration test migration (9+ `.append`/`.extend` sites in `test_fms_planet_*`) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Static guard updates (type-pin tightening) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-19
**Active Phase:** Planning
**Last Action:** Group A cross-group collision resolution applied: serial position changed to LAST in Group A (`449 → 451 → 459 → 450`); Phase 0 cross-group sync gate added (Task 0.6 — waits for PROJ-454 + PROJ-456 to mark `Status: Complete` before Phase 1 starts). Phase 3 Task 3.2 reader-pattern hardened to handle the tuple return from the typed read-only property (codex r5 caught the `isinstance(staging_yard, list)` silent-skip bug). Group A is ready for execution.
**Next Action:** Run agent picks up PROJ-450 Phase 0 LAST in Group A serial order, AFTER PROJ-449 + PROJ-451 + PROJ-459 close AND the cross-group sync gate clears (PROJ-454 + PROJ-456 from Group B both Complete).
**Blockers:** Sequential prerequisites: PROJ-449 Phase 3 (Planet wrapper + property cluster deletion). Cross-group sync gate: PROJ-454 + PROJ-456 (Group B). Phase 0 verifies both before Phase 1.
**Context for Next Agent:** This is the substrate-typing project that the cancelled PROJ-444..447 Joint A phase tried (and could not complete) in May 2026. The Joint A preflight report documented three hard blockers (UI reader, integration tests, validator probes) that all required cross-bucket coordination. Codex r4 redesign re-bundles all of those owners into PROJ-450 as a single job. **The must-know Path A rationale and BLOCKER #1 reasoning are inlined into `design.md`** (sections "Why partial Path A is justified" + "BLOCKER #1 — the rationale for permanent typed-readonly") — this project is executable from project-local docs alone. The archived preflight at `Projects/archived_projects/PROJ-444to447_coordinator/stage_3_joint_a_preflight_findings.md` is OPTIONAL background reading; nothing in it is required to execute the phases.

## Overview
Convert `Planet._staging_yard: List[Dict[str, Any]]` to a typed `List[CarriedVehicle | DropPod]` substrate. Eliminate the flatten/inflate round-trip at the `transfer_branches.py` boundary (where typed `DropPod` instances are currently dict-flattened before being added to the staging yard, then dict-inflated on the way out). Migrate every reader/writer across data/facade/engine/validation/UI layers and the unowned integration-test root (`tests/integration/test_fms_planet_*`). Save format stays dict-shaped; `planet_serde._normalize_to_typed` converts on load.

## Goals
- Widen `Planet._staging_yard` from `List[Dict[str, Any]]` to `List[CarriedVehicle | DropPod]`.
- Move the dict↔typed conversion helpers (`_pod_from_dict` at `transfer_branches.py:55-73`, `_staging_yard_carried_vehicle` at `:76-87`, `_is_carried_vehicle_dict` at `:41-52`) into `Planet` as private helpers (single source of truth).
- Drop the engine-side flatten/inflate calls in `transfer_branches.py` (`:412` `cv.to_dict()`, `:454-460` pod-dict construction) and `issuer_adapter.py` (`:363` `vehicle.to_dict()`).
- Migrate the UI reader at `game/ui/screens/strategy_detail_fmt.py:285-297` so typed entries render correctly (currently silently skipped via `isinstance(item, dict)` check — **silent UI regression risk** if widened without this fix).
- Tighten `IPlanetMutator.add_staging_item` / `pop_staging_item` signatures and the `transfer_validator.py:228, 363-379` shape probe.
- Migrate 9+ direct `planet.staging_yard.append(...)` / `.extend(...)` mutations in `tests/integration/test_fms_planet_*` (4 files) and `tests/integration/test_fms_a_e2e.py` (the unowned-in-old-partition cluster).
- Maintain save-load round-trip via `planet_serde._normalize_to_typed()` (save fixture stays dict-shaped per CLAUDE.md — canonical on-disk format does not change because "saves are disposable" applies to OLD saves on load, not to the on-disk format).
- Update `tests/static_guards/test_no_legacy_storage_fields.py` to pin the new typed substrate.

## Scope

**In Scope:**
- `game/strategy/data/planet.py` — substrate type widening + helper-method migration (depends on PROJ-449 Phase 3 having freed up this file from the property-cluster + wrapper).
- `game/strategy/data/planet_serde.py` — `_normalize_to_typed()` helper on load + new typed-emit path on save.
- `game/strategy/data/galaxy_protocols.py` — `IStagingYardHolder` protocol annotations widened.
- `game/strategy/engine/order_handlers/transfer_branches.py` — drop 3 helpers + 2 flatten blocks.
- `game/strategy/engine/issuer_adapter.py` — drop `_matches` dict probe; tighten `pop_carried` / `append_carried` signatures.
- `game/strategy/engine/production_spawner.py` — construct typed `DropPod` / `CarriedVehicle` directly instead of dicts.
- `game/strategy/validation/transfer_validator.py` — drop runtime shape probes at `:228, :363-379`.
- `game/strategy/services/planet_write_service.py` — tighten `add_staging_item` / `pop_staging_item` signatures.
- `game/strategy/facade/slices/planet_slice.py` — replace `item.get(...)` with typed attribute access.
- `game/strategy/facade/dto/planet_dto.py` — `staging_yard_summary` typed-builder.
- `game/ui/screens/strategy_detail_fmt.py:285-297` — typed reader.
- `tests/integration/test_fms_planet_recovery.py`, `test_fms_planet_lay_mines.py`, `test_fms_planet_launch.py`, `test_fms_a_e2e.py` — 9+ direct mutations.
- `tests/unit/ui/screens/test_strategy_detail_fmt.py:915-1009` — 5 dict-injection fixture tests.
- All affected unit tests under `tests/unit/strategy/engine/`, `tests/unit/strategy/data/`, `tests/unit/strategy/facade/`, `tests/unit/strategy/validation/`.
- `tests/static_guards/test_no_legacy_storage_fields.py` — tighter type pin.

**Out of Scope:**
- Wrapper / property-cluster deletion (PROJ-449's territory — Phase 3 precondition).
- Save-format change. **Saves stay dict-shaped.** `_normalize_to_typed()` converts on load; `planet_to_dict` serializes via `.to_dict()` on each typed entry.
- Renaming `staging_yard` → some other name (out of scope; the conceptual name stays).
- `Planet.add_to_staging_yard` capacity / mass policy changes (only the SHAPE of the substrate changes; the `max_staging_mass` invariant is preserved).
- Engine-side `_apply_resource_consumption` bool-return handling (PROJ-451's territory).
- F-A-007 (ship_instance.py LOC ceiling) — out of all three Stage-3 projects per Codex r4.

## Findings Summary
Source: `Projects/archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md` (F-B-013) + DI-2026-05-18-001 substrate half. F-A-013 was already complete at PROJ-444 Phase 2 Task 2.4. Per-finding entries with current-state verification land in [findings/PROJ-450_findings.md](findings/PROJ-450_findings.md).

| Finding | Severity | File:line | Status |
|---------|----------|-----------|--------|
| F-B-013 | low-medium | `transfer_branches.py:416-446` + `planet.py:316-322` (substrate) | open |
| DI-2026-05-18-001 (engine half) | medium | `transfer_branches.py:472-632` | resolved at fleet-to-fleet branch; substrate half still open |
| F-A-013 | low | `fleet_slice.py:165-191` | **already complete** at PROJ-444 Phase 2 Task 2.4 — verify in Phase 0 only |

## Key Files
| Component | File Path |
|-----------|-----------|
| Substrate field | `game/strategy/data/planet.py:316-328` (add_to_staging_yard, remove_from_staging_yard, _staging_yard field) |
| Helper functions to move | `game/strategy/engine/order_handlers/transfer_branches.py:41-87` (`_is_carried_vehicle_dict`, `_pod_from_dict`, `_staging_yard_carried_vehicle`) |
| Engine flatten blocks to drop | `transfer_branches.py:412, 454-460` + `issuer_adapter.py:363` |
| UI reader (silent regression risk) | `game/ui/screens/strategy_detail_fmt.py:285-297` |
| UI reader test fixtures (dict-injection) | `tests/unit/ui/screens/test_strategy_detail_fmt.py:915-1009` (5 test cases) |
| Validator shape probes | `game/strategy/validation/transfer_validator.py:228, 363-379` |
| Write service signatures | `game/strategy/services/planet_write_service.py:100-105` |
| Facade slice projector | `game/strategy/facade/slices/planet_slice.py:194-213` |
| DTO summary builder | `game/strategy/facade/dto/planet_dto.py:99-112` |
| Save serde | `game/strategy/data/planet_serde.py` (new `_normalize_to_typed` helper) |
| Integration test cluster | `tests/integration/test_fms_planet_recovery.py:59`, `test_fms_planet_lay_mines.py:82,139,155,171`, `test_fms_planet_launch.py:92,121,157,192`, `test_fms_a_e2e.py:305` |
| Save fixture (round-trip target) | `tests/fixtures/saves/galaxy_proj372_populated.json` (17 staging_yard refs) |
| Static guard | `tests/static_guards/test_no_legacy_storage_fields.py` |

Full enumeration per phase in [manifest.md](manifest.md).

## Phase Breakdown

### Phase 0: Re-verify Stage 3 preflight audit; verify PROJ-449 Phase 3 precondition
Re-run the audit commands from `Projects/archived_projects/PROJ-444to447_coordinator/stage_3_joint_a_preflight_findings.md` §1.2 + §1.3 at current HEAD. Confirm the 310-occurrence / 49-file count from May 2026 still holds (pre-audit at 2026-05-19: 82 in `game/` + 228 in `tests/` = 310 across 49 files — matches exactly). Verify the three blockers from §2 are still present:
- BLOCKER #1: UI reader at `strategy_detail_fmt.py:285-297` still does `isinstance(item, dict): continue`.
- BLOCKER #2: integration tests still do direct `.append/.extend` mutations.
- BLOCKER #3: validator still has shape probes at `:228, :363-379`.

Verify PROJ-449 Phase 3 has landed (Planet wrapper + property cluster deleted). If not, PAUSE — Phase 1 cannot proceed cleanly without the wrapper-free `planet.py` surface. **No code changes in Phase 0.**

### Phase 1: Path A engine-only API cleanup (recommended by Stage 3 preflight)
Per Stage 3 preflight §3.1 (Path A — recommended in May 2026 but never executed). Widens `Planet.add_to_staging_yard()` to accept `Dict | CarriedVehicle | DropPod`; adds `Planet.pop_staging_yard_typed(index) -> CarriedVehicle | DropPod | None`; moves the 3 helpers from `transfer_branches.py:41-87` into `planet.py` as private module-level helpers. Engine handlers drop their flatten/inflate calls. **Save format unchanged; UI reader unchanged; integration tests unchanged.** This is a checkpoint: the substrate is still `List[Dict[str, Any]]`, but the dict↔typed conversion is centralized inside Planet. Closes the call-site bookkeeping half of F-B-013.

### Phase 2: Substrate widening
The literal type change: `_staging_yard: List[CarriedVehicle | DropPod]`. Update `planet_serde` for round-trip via a new `_normalize_to_typed()` helper on load (read dicts, promote to typed) and serialize each typed entry via its `.to_dict()` on save. Save format is unchanged. The internal Planet helpers from Phase 1 now hand out typed objects directly without going through the dict shape. Engine handlers stop their own dict construction. **Phase 2 lands behind a temp-shim**: `Planet.staging_yard` continues to return a `List[Dict[str, Any]]` projection for one phase so the UI reader still works, then Phase 3 migrates the UI reader and drops the projection.

> **NOTE:** Phase 2 deliberately keeps a *dict-projection compatibility layer alive for one phase* so the UI reader migration in Phase 3 is its own RED-then-GREEN cycle without breaking the visible planet detail panel. CLAUDE.md's "no compat shims" rule applies to ENDURING shims, not to single-phase migration bridges that come down with the next commit. Land the projection as Phase 2's deliberate residual; delete it in Phase 3.

### Phase 3: UI reader migration + DTO / validator / write-service tightening
Migrate `game/ui/screens/strategy_detail_fmt.py:285-297` to read typed entries (use `isinstance(item, (CarriedVehicle, DropPod))` and pull `item.design_id` / `item.vehicle_type` / `item.payload.get('name')` directly, replacing the legacy `item.get(...)` dict reads). Migrate the 5 dict-injection fixture tests at `tests/unit/ui/screens/test_strategy_detail_fmt.py:915-1009` to construct typed fixtures instead of dict literals. Tighten `IPlanetMutator.add_staging_item` / `pop_staging_item` signatures to match the new substrate type. Drop the runtime shape probes in `transfer_validator.py:228, 363-379` (replace with direct `isinstance` checks on the typed entries). After Phase 3, **the Phase-2 dict-projection bridge property is replaced by a permanent typed read-only property** `Planet.staging_yard -> Tuple[CarriedVehicle | DropPod, ...]` so external readers (UI / facade / DTO) keep a stable public surface; all mutations route through `add_to_staging_yard` / `pop_staging_yard_typed` / `remove_from_staging_yard`. (See decisions.md row 2026-05-19 "Codex BLOCKER #1 = Option A: permanent typed read-only property.")

### Phase 4: Integration test migration
Migrate the 9+ direct `planet.staging_yard.append(dict_literal)` / `.extend(...)` mutations in `tests/integration/test_fms_planet_recovery.py:59`, `test_fms_planet_lay_mines.py:82,139,155,171`, `test_fms_planet_launch.py:92,121,157,192`, `test_fms_a_e2e.py:305`. Either:
(a) Construct typed `CarriedVehicle(...)` / `DropPod(...)` instances directly, OR
(b) Replace direct mutations with `planet.add_to_staging_yard(typed_instance)` calls (the cleaner option — exercises the public API).

Per the Stage 3 preflight §2.2, these 4 files were "unowned" in the old PROJ-444..447 partition because they sit at the integration-test root, between bucket-A (data/facade), bucket-B (engine), and bucket-C (UI). PROJ-450 explicitly owns them per Codex r4 redesign.

### Phase 5: Static guard updates
Update `tests/static_guards/test_no_legacy_storage_fields.py` to pin the new typed substrate. The current guard pins the absence of legacy field names (`stockpile`, `staging_yard` as dataclass fields). After Phase 2, `_staging_yard` IS a typed list — the guard should additionally pin "every entry is `CarriedVehicle` or `DropPod`, no dict entries" so a future regression that re-introduces dicts via `.append(legacy_dict)` is caught at static-guard time.

## Related Documents
- [design.md](design.md) — design rationale (Path A → substrate widening sequencing).
- [decisions.md](decisions.md) — decisions log.
- [findings/PROJ-450_findings.md](findings/PROJ-450_findings.md) — consolidated findings.
- [manifest.md](manifest.md) — file manifest grouped by phase + production/test/doc type.
- Codex r4 redesign: `AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md` (job 2 row).
- Stage 3 Joint A preflight (OPTIONAL background, NOT a mandatory pre-read; key rationale inlined into design.md): `Projects/archived_projects/PROJ-444to447_coordinator/stage_3_joint_a_preflight_findings.md` — full 310-occurrence audit + 3 hard blockers + Path A / B / C trade-offs.
- Archived bucket scan: `Projects/archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md` (F-B-013).
- DI-2026-05-18-001 in `AgentCoordination/discovered_issues/log.jsonl` — fleet-to-fleet half resolved; substrate half tracked here.

## Dependencies & Sibling Projects

| This project depends on | What | Why |
|-------------------------|------|-----|
| **PROJ-449 Phase 3** | Wrapper + property-cluster deletion in `planet.py` | The PROJ-450 substrate widening needs the post-Phase-3 cleaned `planet.py` surface. Without Phase 3, the @property-driven `staging_yard` accessor still exists and the substrate type change cascades through every property reader. |

| Sibling projects | Their dependency on PROJ-450 | When unblocked |
|------------------|------------------------------|----------------|
| PROJ-449 (wrapper retirement) | depends-on-from-this-side: Phase 3 must land first | n/a |
| PROJ-451 (production resource-consumption) | independent | can run in parallel |
| PROJ-459 (strategy data LOC extractions) | independent at the project level | Runs BEFORE this project in Group A serial order (collision-resolution reorder) |

### Group A serial order (2026-05-19 collision resolution) + cross-group sync gate

Group A executes its 4 projects in this serial order: **PROJ-449 → PROJ-451 → PROJ-459 → PROJ-450**.

This project (PROJ-450) is LAST in the order. PROJ-450 was reordered from third-place to last-place because of hard test-file collisions with Group B:

- `tests/unit/strategy/engine/test_order_processor_transfer.py` — PROJ-450 Phase 4 (substrate assertions) vs PROJ-454 Phase 3 (`process_transfer` facade call-site rewrites)
- `tests/unit/ui/screens/test_transfer_dialog_characterization.py` — PROJ-450 Phase 3 (UI reader migration) vs PROJ-456 Phase 4 (characterization sweep)

**Cross-group sync gate.** Before Phase 1 begins, PROJ-450 Phase 0 explicitly verifies that **PROJ-454** AND **PROJ-456** both show `Status: Complete` in their respective plan.md files. Running PROJ-450 last lets it rebase once cleanly on the merged Group B work rather than fighting two concurrent edits. See `phase_0_checklist.md` Task 0.6 for the gate.

## Verification
- [ ] Phase 0 re-verifies the 310 / 49-file count and the 3 blockers; verifies PROJ-449 Phase 3 landed
- [ ] Phase 1 engine API cleanup: dict↔typed helpers centralized in Planet; engine flatten/inflate calls removed
- [ ] Phase 2 substrate type widened to `List[CarriedVehicle | DropPod]`; save-load round-trip green via `_normalize_to_typed`
- [ ] Phase 3 UI reader migrated; dict-injection fixture tests migrated; validator probes dropped; Phase-2 projection bridge deleted
- [ ] Phase 4 integration tests migrated to typed inputs or public API calls
- [ ] Phase 5 static guard tightened
- [ ] Full sharded suite green at every phase boundary
- [ ] Save-fixture (`galaxy_proj372_populated.json`) loads and round-trips correctly
- [ ] Audit passed (end-of-project Codex consult)
- [ ] User verified
