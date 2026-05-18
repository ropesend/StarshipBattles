# PROJ-443 Phase 0 — Hidden-Test Baseline Ledger

**Captured at:** 2026-05-17
**Repo HEAD:** `42ac82eece7c40b47c02e1fae8d0bf30357cb0b6`
**Runner:** `python -m pytest <dir> -q --no-header -n 4` (direct invocation; bypasses the sharded runner so `pytest.ini`'s `testpaths = tests` constraint still applies, but each hidden directory is reached via explicit path).
**Python / pytest:** Python 3.14.4 / pygame-ce 2.5.7 (pytest version from each run's header — captured in `findings/raw/<dir>.out`).

This document is the authoritative ledger of pass/fail state in every directory currently hidden from the canonical sharded suite (`python Tools/test_sharded/test_sharded.py`) by `pytest.ini`'s `norecursedirs` token collisions. Phases 1–3 of PROJ-443 work against this ledger; Phase 4 flips `pytest.ini` and the regression guard prevents recurrence.

---

## Visible-suite baseline (sharded runner)

`python Tools/test_sharded/test_sharded.py` at HEAD `42ac82eec`:

| Metric | Value |
|---|---|
| Sharded TOTAL collected | **21233** |
| Sharded passed | **21233** |
| Sharded failed | **0** |
| Sharded errors | **0** |
| Sharded skipped | **0** |
| Wall time | **114.5s** (16 shards) |

This matches the plan's "~21233" cite exactly — no drift since PROJ-436 Phase 7 closed. Sharded gate is fully green at the current visible-test set.

---

## Hidden directories — inventory

Six directories under `tests/` are hidden from the canonical sharded suite because `pytest.ini`'s `norecursedirs` glob matches their basenames. `find tests -type d \( -name data -o -name combat_lab -o -iname assets -o -name ShipThemes \)` confirmed the inventory; `tests/unit/research/data/` matched the `data` glob but contains **0** `test_*.py` files so it is listed for completeness only.

| Hidden directory | `test_*.py` count | Hidden by `norecursedirs` token |
|---|---:|---|
| `tests/unit/strategy/data/` | 95 | `data` |
| `tests/unit/combat_lab/` | 24 | `combat_lab` |
| `tests/unit/data/` | 3 | `data` |
| `tests/unit/assets/` | 2 | `Assets` (Windows `fnmatch` is case-insensitive) |
| `tests/unit/ui/assets/` | 1 | `Assets` (Windows `fnmatch` is case-insensitive) |
| `tests/integration/data/` | 1 | `data` |
| `tests/unit/research/data/` | 0 | `data` (no test files; informational) |
| **Total (with tests)** | **126** | — |

`ShipThemes` is also in the `norecursedirs` list but matches no test directory today (`find tests -type d -name ShipThemes` returns nothing). Per `decisions.md` 2026-05-18 row, it is retained.

---

## Per-directory counts

| Hidden directory | Files | Tests collected | Passed | Failed | Wall time |
|---|---:|---:|---:|---:|---:|
| `tests/unit/strategy/data/` | 95 | 1573 | 1506 | **67** | 12.91s |
| `tests/unit/combat_lab/` | 24 | 268 | 268 | 0 | 2.98s |
| `tests/unit/data/` | 3 | 29 | 22 | **7** | 1.78s |
| `tests/unit/assets/` | 2 | 29 | 28 | **1** | 1.50s |
| `tests/unit/ui/assets/` | 1 | 30 | 30 | 0 | 1.44s |
| `tests/integration/data/` | 1 | 23 | 23 | 0 | 1.30s |
| **Total** | **126** | **1952** | **1877** | **75** | **~22s aggregate** |

Important deltas vs. plan/design assumptions:

- **Plan assumed ~65 failures in `tests/unit/strategy/data/`** (the PROJ-436 Phase 2 snapshot of "1510 pass / 65 fail"). Actual on 2026-05-17 HEAD: **67 failures / 1506 passed.** Very close — slight drift from PROJ-436 Phases 3-7 intermediate state.
- **Plan assumed `tests/unit/combat_lab/` would surface its own failure cluster** (24 test files marked as Phase 3 risk #3). Actual: **all 268 tests pass.** Phase 3b is effectively a no-op for combat_lab — direct-invocation confirms zero failures today.
- **Plan did not enumerate failures in `tests/unit/data/` or `tests/unit/assets/`.** Actual: 7 + 1 = **8 small-dir failures** to triage in Phase 3c.
- **`tests/unit/ui/assets/` and `tests/integration/data/`** are clean (Phase 3c effectively no-ops for these too).
- **Plan said "~21359+" as expected post-flip count** (visible baseline + 126). That conflates *file* count with *test* count. Real projection is visible baseline + 1952 tests (see below).

---

## Failing test inventory (clustered by phase)

### Phase 1 cluster — `test_cargo_tracking.py` (30 failures)

All in `tests/unit/strategy/data/test_cargo_tracking.py`. Plan estimated "~30" — confirmed at exactly 30.

```
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceCargoCapacity::test_ship_instance_cargo_capacity
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceCargoCapacity::test_ship_instance_cargo_capacity_generic
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceCargoCapacity::test_ship_instance_cargo_capacity_missing_type
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceCargoCapacity::test_ship_instance_cargo_capacity_no_cargo_ship
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceLoadCargo::test_ship_instance_load_cargo
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceLoadCargo::test_ship_instance_load_cargo_multiple_times
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceLoadCargo::test_ship_instance_load_over_capacity
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceLoadCargo::test_ship_instance_load_partial_over_capacity
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceLoadCargo::test_ship_instance_load_no_capacity
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceLoadCargo::test_ship_instance_load_different_cargo_types
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceUnloadCargo::test_ship_instance_unload_cargo
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceUnloadCargo::test_ship_instance_unload_more_than_current
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceUnloadCargo::test_ship_instance_unload_clears_zero_entry
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceCargoSpaceAvailable::test_cargo_space_available_empty
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceCargoSpaceAvailable::test_cargo_space_available_partial
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceCargoSpaceAvailable::test_cargo_space_available_full
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceCargoSerialization::test_ship_instance_cargo_serialization_roundtrip
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceCargoSerialization::test_zero_cargo_removed_from_dict
tests/unit/strategy/data/test_cargo_tracking.py::TestShipInstanceCargoClone::test_clone_preserves_cargo
tests/unit/strategy/data/test_cargo_tracking.py::TestFleetCargoCapacity::test_fleet_cargo_capacity_sum
tests/unit/strategy/data/test_cargo_tracking.py::TestFleetCargoCapacity::test_fleet_cargo_capacity_generic
tests/unit/strategy/data/test_cargo_tracking.py::TestFleetCargoCapacity::test_fleet_cargo_capacity_missing_type
tests/unit/strategy/data/test_cargo_tracking.py::TestFleetLoadCargo::test_fleet_load_distributes_across_ships
tests/unit/strategy/data/test_cargo_tracking.py::TestFleetLoadCargo::test_fleet_load_caps_at_capacity
tests/unit/strategy/data/test_cargo_tracking.py::TestFleetLoadCargo::test_fleet_load_to_empty_fleet
tests/unit/strategy/data/test_cargo_tracking.py::TestFleetUnloadCargo::test_fleet_unload_from_multiple_ships
tests/unit/strategy/data/test_cargo_tracking.py::TestFleetUnloadCargo::test_fleet_unload_more_than_available
tests/unit/strategy/data/test_cargo_tracking.py::TestFleetUnloadCargo::test_fleet_unload_from_empty
tests/unit/strategy/data/test_cargo_tracking.py::TestFleetCargoCurrent::test_fleet_cargo_current_sum
tests/unit/strategy/data/test_cargo_tracking.py::TestFleetCargoCurrent::test_fleet_cargo_current_empty
```

### Phase 2 cluster — `test_mutator_boundary_ast_guard.py` (4 failures)

Plan estimated "~9" AST guard failures. Actual is **4** — likely because PROJ-436's protocol consolidation already eliminated some of the drift.

```
tests/unit/strategy/data/test_mutator_boundary_ast_guard.py::test_mutator_boundary[ShipInstance]
tests/unit/strategy/data/test_mutator_boundary_ast_guard.py::test_mutator_boundary[Fleet]
tests/unit/strategy/data/test_mutator_boundary_ast_guard.py::test_mutator_boundary[Planet]
tests/unit/strategy/data/test_mutator_boundary_ast_guard.py::test_mutator_boundary[Empire]
```

### Phase 3a cluster — `tests/unit/strategy/data/` long-tail (33 failures across 6 files)

Plan estimated "~26" long-tail. Actual is **33**, with a much larger `test_build_queue_source.py` cluster than anticipated.

| File | Failures | Provisional sub-cluster |
|---|---:|---|
| `test_build_queue_source.py` | 19 | Build-queue collection — likely related to PROJ-436 Phase 6 build-queue/transfer-validator surface changes |
| `test_fleet_consumable_aggregator.py` | 9 | Cargo aggregation — likely cargo-manager API migration parity (companion to Phase 1) |
| `test_galaxy_planet_star_loc_ceilings.py` | 2 | LOC ceiling guards — likely Planet/Star file size delta from PROJ-436 work |
| `test_build_context.py` | 1 | Protocol compliance — `test_fleet_satisfies_build_context_protocol` |
| `test_planet_classification_logic.py` | 1 | `TestClassificationConfigLoader::test_all_planet_types_have_rules` |
| `test_storm.py` | 1 | `TestStarSystemStormIntegration::test_star_system_from_dict_skips_invalid_storm_gracefully` |

Full IDs (33):

```
tests/unit/strategy/data/test_build_context.py::TestBuildContextProtocolCompliance::test_fleet_satisfies_build_context_protocol
tests/unit/strategy/data/test_build_queue_source.py::TestCollectBuildQueuesAtHex::test_planet_no_shipyards_returns_base_only
tests/unit/strategy/data/test_build_queue_source.py::TestCollectBuildQueuesAtHex::test_planet_with_two_shipyards_returns_three_sources
tests/unit/strategy/data/test_build_queue_source.py::TestCollectBuildQueuesAtHex::test_fleet_with_space_yard_included
tests/unit/strategy/data/test_build_queue_source.py::TestCollectBuildQueuesAtHex::test_non_operational_shipyard_excluded
tests/unit/strategy/data/test_build_queue_source.py::TestCollectBuildQueuesAtHex::test_queue_references_are_shared
tests/unit/strategy/data/test_build_queue_source.py::TestCollectBuildQueuesAtHex::test_mixed_facilities_only_shipyards_get_queues
tests/unit/strategy/data/test_build_queue_source.py::TestCollectAllBuildQueuesForEmpire::test_collect_all_build_queues_with_planet_base_queue
tests/unit/strategy/data/test_build_queue_source.py::TestCollectAllBuildQueuesForEmpire::test_collect_all_build_queues_with_shipyard_facility
tests/unit/strategy/data/test_build_queue_source.py::TestCollectAllBuildQueuesForEmpire::test_collect_all_build_queues_with_space_shipyard
tests/unit/strategy/data/test_build_queue_source.py::TestCollectAllBuildQueuesForEmpire::test_collect_all_build_queues_mixed_sources
tests/unit/strategy/data/test_build_queue_source.py::TestCollectAllBuildQueuesForEmpire::test_collect_all_build_queues_non_operational_shipyard_excluded
tests/unit/strategy/data/test_build_queue_source.py::TestBuildQueueSourceNewFields::test_collect_queues_sets_base_build_rate
tests/unit/strategy/data/test_build_queue_source.py::TestBuildQueueSourceNewFields::test_collect_queues_sets_shipyard_build_rate
tests/unit/strategy/data/test_build_queue_source.py::TestBuildQueueSourceNewFields::test_collect_queues_sets_shipyard_build_rate_with_bonus
tests/unit/strategy/data/test_build_queue_source.py::TestBuildQueueSourceNewFields::test_collect_queues_sets_fleet_build_rate
tests/unit/strategy/data/test_build_queue_source.py::TestBuildQueueSourceNewFields::test_collect_queues_sets_planet_id_for_planet_sources
tests/unit/strategy/data/test_build_queue_source.py::TestBuildQueueSourceNewFields::test_collect_queues_sets_planet_id_none_for_fleet
tests/unit/strategy/data/test_build_queue_source.py::TestBuildQueueSourceNewFields::test_collect_queues_uses_explicit_production_rates
tests/unit/strategy/data/test_build_queue_source.py::TestBuildQueueSourceNewFields::test_collect_queues_explicit_rates_with_bonus
tests/unit/strategy/data/test_fleet_consumable_aggregator.py::TestCargoMethods::test_get_fleet_cargo_capacity
tests/unit/strategy/data/test_fleet_consumable_aggregator.py::TestCargoMethods::test_get_fleet_cargo_capacity_multiple_ships
tests/unit/strategy/data/test_fleet_consumable_aggregator.py::TestCargoMethods::test_get_fleet_cargo_current
tests/unit/strategy/data/test_fleet_consumable_aggregator.py::TestCargoMethods::test_load_cargo_distributes_to_ships
tests/unit/strategy/data/test_fleet_consumable_aggregator.py::TestCargoMethods::test_unload_cargo_from_fleet
tests/unit/strategy/data/test_fleet_consumable_aggregator.py::TestCargoDistributionEdgeCases::test_load_cargo_partial_capacity_multiple_ships
tests/unit/strategy/data/test_fleet_consumable_aggregator.py::TestCargoDistributionEdgeCases::test_load_cargo_stops_when_fully_loaded
tests/unit/strategy/data/test_fleet_consumable_aggregator.py::TestCargoDistributionEdgeCases::test_unload_cargo_partial_multiple_ships
tests/unit/strategy/data/test_fleet_consumable_aggregator.py::TestCargoDistributionEdgeCases::test_unload_cargo_stops_when_fully_unloaded
tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py::test_planet_loc_ceiling
tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py::test_per_service_loc_ceilings
tests/unit/strategy/data/test_planet_classification_logic.py::TestClassificationConfigLoader::test_all_planet_types_have_rules
tests/unit/strategy/data/test_storm.py::TestStarSystemStormIntegration::test_star_system_from_dict_skips_invalid_storm_gracefully
```

### Phase 3b cluster — `tests/unit/combat_lab/` (0 failures)

All 268 tests pass via direct invocation. Phase 3b is a no-op.

### Phase 3c cluster — small hidden directories (8 failures total)

#### `tests/unit/data/` — 7 failures

```
tests/unit/data/test_data_validation.py::TestFormationFileNaming::test_formation_files_have_professional_names
tests/unit/data/test_data_validation.py::TestFormationFileNaming::test_formation_files_are_valid_json
tests/unit/data/test_data_validation.py::TestBuilderThemeTypes::test_font_size_is_integer
tests/unit/data/test_data_validation.py::TestPlaceholderFiles::test_ui_presets_has_valid_format
tests/unit/data/test_test_infrastructure.py::TestUtilityScriptNaming::test_verify_builder_imports_renamed
tests/unit/data/test_test_infrastructure.py::TestFormationScriptNaming::test_formation_flight_is_manual_script
tests/unit/data/test_test_infrastructure.py::TestFormationScriptNaming::test_formation_attack_is_manual_script
```

Provisional reading: these are validation/infrastructure tests about formation files, builder themes, and utility script naming. They look like they may have drifted as filenames moved during prior refactors — not related to PROJ-436.

#### `tests/unit/assets/` — 1 failure

```
tests/unit/assets/test_asset_manager_resolutions.py::TestStarAssets::test_load_star_image_returns_missing_texture_after_loader_errors
```

Single failure; the raw output shows `RuntimeError` originating in `unittest/mock.py:1241` (`mock.py` line 1241 is the bound-method assertion path). Probable cause: `MagicMock` configuration drift against an updated AssetManager loader signature.

#### `tests/unit/ui/assets/` — 0 failures
All 30 tests pass.

#### `tests/integration/data/` — 0 failures
All 23 tests pass.

---

## Cluster summary

| Phase | Cluster | Failures | Files involved |
|---|---|---:|---|
| 1 | `test_cargo_tracking.py` | 30 | 1 |
| 2 | `test_mutator_boundary_ast_guard.py` | 4 | 1 |
| 3a | `tests/unit/strategy/data/` long-tail | 33 | 6 |
| 3b | `tests/unit/combat_lab/` | 0 | 0 |
| 3c | small hidden directories (`unit/data`, `unit/assets`, `ui/assets`, `integration/data`) | 8 | 2 |
| **Total** | — | **75** | **10** |

---

## Post-flip projection

Once Phases 1–3 land (failures fixed, marked, or deleted with rationale) and Phase 4 removes the `data`, `combat_lab`, and `Assets` tokens from `pytest.ini`'s `norecursedirs`, the sharded suite collects every file under `tests/`.

**Test-count projection (assuming all 75 failures are resolved by fixing the tests/production — not deletions):**

```
post-flip sharded count = 21233 + 1952 = ~23185
```

If failures are resolved by deleting obsolete tests instead, subtract the deletion count from 23185. A conservative band for Phase 4's verification: **~23110 – ~23185** (allowing for up to 75 deletions in the worst case).

**The plan's stated projection of "~21359+" (= 21233 + 126) confused file count with test count.** The actual delta in collected tests is ~1952, not ~126. Phase 4's verification step should expect ~23185, not ~21359.

Per Codex's pre-execution consult, the regression guard added in Phase 4 is file-level only — it will catch a `norecursedirs`/`--ignore` token that drops any `test_*.py` file from collection, but not function-level drift inside an already-collected file.

---

## Raw outputs

Per-directory raw pytest stdout is captured under `findings/raw/` for reproducibility:

- `findings/raw/strategy_data.out`
- `findings/raw/combat_lab.out`
- `findings/raw/unit_data.out`
- `findings/raw/unit_assets.out`
- `findings/raw/ui_assets.out`
- `findings/raw/integration_data.out`
- `findings/raw/sharded_baseline.out`

These files are not committed (kept ad-hoc under `findings/raw/`); the structured ledger in this file is the authoritative artifact.
