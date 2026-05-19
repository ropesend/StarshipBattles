# PROJ-450 File Manifest

> Files that this project touches, grouped by phase and by Production / Test / Doc type.
> Numbers are confirmed by the 2026-05-18 Stage 3 preflight (`Projects/archived_projects/PROJ-444to447_coordinator/stage_3_joint_a_preflight_findings.md`); Phase 0 re-verifies at HEAD before any code change.

## Phase 0 — Re-verify Stage 3 preflight audit (read-only)

| File | Type | Notes |
|------|------|-------|
| `findings/phase_0_audit.md` (new) | Doc | Re-verified counts; precondition confirmation for PROJ-449 Phase 3 |
| `Projects/archived_projects/PROJ-444to447_coordinator/stage_3_joint_a_preflight_findings.md` | Doc (read) | Mandatory pre-read; §1.2 / §1.3 / §2 are the audit + blocker source-of-truth |

## Phase 1 — Path A engine-only API cleanup

### Production
| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/planet.py` | Production | Widen `add_to_staging_yard()` to accept `Dict \| CarriedVehicle \| DropPod`; add `pop_staging_yard_typed(index) -> CarriedVehicle \| DropPod \| None`; move 3 helpers from transfer_branches.py:41-87 |
| `game/strategy/engine/order_handlers/transfer_branches.py` | Production | Drop 3 helper definitions (`_is_carried_vehicle_dict` at 41-52, `_pod_from_dict` at 55-73, `_staging_yard_carried_vehicle` at 76-87); drop flatten at line 412 (`cv.to_dict()`); drop pod-dict construction at lines 454-460; replace with `planet.add_to_staging_yard(cv)` / `planet.add_to_staging_yard(pod)` direct typed passes |
| `game/strategy/engine/issuer_adapter.py` | Production | Drop `vehicle.to_dict()` flatten at line 363; change to `add_to_staging_yard(vehicle)` |
| `game/strategy/engine/production_spawner.py` | Production | Keep dict construction for now (Phase 2 migrates this); document as Phase-2 todo |

### Test
| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/data/test_planet_staging_yard_typed_api.py` (new) | Test | Unit tests for the new typed accept + typed pop API |
| `tests/integration/strategy/facade/test_fleet_to_fleet_drop_pod.py` (new) | Test | Verifies PROJ-445 Phase 2's fleet-to-fleet pod fix continues to work after Phase 1 |

## Phase 2 — Substrate widening + serde normalization

### Production
| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/planet.py` | Production | Change `_staging_yard: List[Dict[str, Any]]` to `List[CarriedVehicle \| DropPod]`; internal helpers stop going through the dict shape; add a **temp** `staging_yard` projection property returning `List[Dict[str, Any]]` (Phase 3 will delete this) |
| `game/strategy/data/planet_serde.py` | Production | New `_normalize_to_typed(items: list) -> List[CarriedVehicle \| DropPod]` helper invoked by `planet_from_dict_kwargs`; `planet_to_dict` calls `.to_dict()` on each typed entry |
| `game/strategy/data/galaxy_protocols.py` | Production | `IStagingYardHolder` annotation widened from `List[Dict[str, Any]]` to `List[CarriedVehicle \| DropPod]` (or equivalent) |
| `game/strategy/engine/production_spawner.py` | Production | Construct typed `DropPod(...)` / `CarriedVehicle(...)` directly instead of dicts at lines 347-360 |

### Test
| File | Type | Notes |
|------|------|-------|
| `tests/integration/save_load/test_roundtrip_planet.py` | Test | Verify the fixture `galaxy_proj372_populated.json` round-trips: load → typed substrate → save → identical dict shape on disk |
| `tests/unit/strategy/data/test_planet_staging_yard_typed_api.py` | Test | Expand to cover substrate-widening invariants: every entry IS typed; mass invariant preserved |
| `tests/integration/test_fms_a_e2e.py` | Test | Phase 2 Task 2.0 pre-migration: replace `planet.staging_yard.clear()` at line 305 with explicit `remove_from_staging_yard(0)` loop or fixture-side seed cleanup (silent-mutation prevention before the read-only projection lands) |

## Phase 3 — UI reader migration + DTO / validator / write-service tightening

### Production
| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/strategy_detail_fmt.py` | Production | Lines 285-297: replace `isinstance(item, dict): continue` + `item.get(...)` reads with `isinstance(item, (CarriedVehicle, DropPod))` + direct attribute reads (`item.payload.get('name')` / `item.vehicle_type` / etc.) |
| `game/strategy/validation/transfer_validator.py` | Production | Lines 228, 363-379: drop the dict-shape probes; replace with direct isinstance checks on the typed entries |
| `game/strategy/services/planet_write_service.py` | Production | Lines 100-105: tighten `add_staging_item` / `pop_staging_item` signatures from `Any` to `CarriedVehicle \| DropPod` |
| `game/core/protocols/strategy_mutators.py` | Production | Tighten `IPlanetMutator.add_staging_item` / `pop_staging_item` Protocol signatures (currently `item: Any` at line 105) to match the typed substrate. Matches the write-service tightening above. |
| `game/strategy/facade/slices/planet_slice.py` | Production | Lines 194-213: replace `item.get(...)` with typed attribute access for staging-yard snapshot projection |
| `game/strategy/facade/dto/planet_dto.py` | Production | Lines 99-112: `staging_yard_summary` builder reads typed attrs instead of dict keys |
| `game/strategy/data/planet.py` | Production | Replace the temp `staging_yard` dict-projection property from Phase 2 with a permanent typed read-only property `Planet.staging_yard -> Tuple[CarriedVehicle \| DropPod, ...]` (Option A per 2026-05-19 codex audit BLOCKER #1) |

### Test
| File | Type | Notes |
|------|------|-------|
| `tests/unit/ui/screens/test_strategy_detail_fmt.py` | Test | Lines 915-1009: 5 dict-injection fixtures migrated to typed `CarriedVehicle` / `DropPod` instances |
| `tests/unit/strategy/validation/test_transfer_drop_pod.py` | Test | Update to construct typed fixtures rather than dict literals |
| `tests/unit/strategy/facade/test_container_snapshots.py` | Test | Verify the snapshot projection still works against the typed substrate |
| `tests/unit/strategy/facade/slices/test_planet_slice.py` | Test | Verify the projection path |
| `tests/unit/ui/screens/test_transfer_view_model_container.py` | Test | Verify post-migration |
| `tests/unit/ui/screens/test_transfer_dialog_characterization.py` | Test | Verify post-migration |
| `tests/unit/ui/panels/test_planet_report_panel.py` | Test | Verify post-migration |

## Phase 4 — Integration test migration

### Test
| File | Type | Notes |
|------|------|-------|
| `tests/integration/test_fms_planet_recovery.py` | Test | Line 59: typed `.append(typed_instance)` or `planet.add_to_staging_yard(typed_instance)` |
| `tests/integration/test_fms_planet_lay_mines.py` | Test | Lines 82, 139, 155, 171: 4 mutation sites |
| `tests/integration/test_fms_planet_launch.py` | Test | Lines 92, 121, 157, 192: 4 mutation sites |
| `tests/integration/test_fms_a_e2e.py` | Test | Line 305: 1 mutation site (`.clear()` — straightforward; clears either dict or typed list) |
| `tests/unit/strategy/engine/test_staging_yard_operations.py` | Test | 17 occurrences — verify each is compatible with typed substrate |
| `tests/unit/strategy/engine/test_production_spawner_staging_yard.py` | Test | 20 occurrences |
| `tests/unit/strategy/engine/test_production_spawner.py` | Test | 17 occurrences |
| `tests/unit/strategy/engine/test_pod_transfer.py` | Test | 21 occurrences |
| `tests/unit/strategy/engine/test_issuer_adapter.py` | Test | 12 occurrences |
| `tests/unit/strategy/engine/test_order_processor_transfer.py` | Test | 10 occurrences |
| `tests/unit/strategy/engine/order_handlers/test_transfer_handler.py` | Test | 17 occurrences |
| `tests/unit/strategy/engine/test_production_normalisation.py` | Test | 6 occurrences |
| `tests/unit/strategy/engine/test_order_processor_no_legacy_helpers.py` | Test | 2 occurrences |
| `tests/unit/strategy/data/test_vehicle_bay.py` | Test | 5 occurrences |
| `tests/unit/strategy/data/test_galaxy_protocols.py` | Test | 1 occurrence |
| `tests/unit/strategy/data/test_planet_fleet_empire_post_436_contract.py` | Test | 4 occurrences |
| `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` | Test | 3 occurrences |
| `tests/unit/strategy/data/test_mutator_boundary_ast_guard_self_test.py` | Test | 2 occurrences (`.clear()`) |
| `tests/integration/strategy/test_save_round_trip_phase2.py` | Test | 1 occurrence |
| `tests/unit/strategy/engine/order_handlers/test_colonize_transfer_no_legacy_substrate.py` | Test | 1 occurrence |

## Phase 5 — Static guard updates

| File | Type | Notes |
|------|------|-------|
| `tests/static_guards/test_no_legacy_storage_fields.py` | Test | Tighten type pin: add assertion "every entry in `_staging_yard` is `CarriedVehicle \| DropPod`, no dicts permitted" |
| `tests/static_guards/test_no_legacy_protocol_names.py` | Test | Verify still pinning IStagingYardHolder shape correctly |

## Fixtures (round-trip target — no edit required if serde works)

| File | Type | Notes |
|------|------|-------|
| `tests/fixtures/saves/galaxy_proj372_populated.json` | Save fixture | 17 staging_yard refs in dict form — stays unchanged; `_normalize_to_typed` converts on load |
| `tests/fixtures/saves/_build_galaxy_fixture.py` | Test | Verify if any staging items are constructed here; if so, ensure they round-trip through the new normalize path |
