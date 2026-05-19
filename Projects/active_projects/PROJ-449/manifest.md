# PROJ-449 File Manifest

> Files that this project touches, grouped by phase and by Production / Test / Doc type.
> Counts are pinned by Phase 0 audit; numbers below are pre-audit estimates from Codex r4 + PROJ-443 Phase 5b's audit-of-record (18 files for the ShipInstance side).

## Phase 0 — Pre-flight audit (read-only)

| File | Type | Notes |
|------|------|-------|
| `findings/phase_0_audit.md` (new) | Doc | Captures `rg` counts for every legacy-kwarg spelling |
| `Projects/active_projects/PROJ-443/decisions.md` | Doc (read) | Verify Phase 5b "18 files" audit-of-record |
| `Projects/active_projects/PROJ-443/phase_5_checklist.md` | Doc (read) | Carry-over context |

## Phase 1 — Migrate `tests/fixtures/strategy_entities.py`

| File | Type | Notes |
|------|------|-------|
| `tests/fixtures/strategy_entities.py` | Test | 4 sites: `:140` facility, `:318` ship consumable, `:320` ship cargo, `:425` planet stockpile |

## Phase 2 — Sweep direct call sites in tests + rewrite `planet_from_dict_kwargs`

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/planet_serde.py` | Production | Rewrite `planet_from_dict_kwargs` (lines 130-162) to emit `_stockpile=`/`_max_stockpile=`/`_staging_yard=`; drop F-A-025 `data.get("resources", {})` legacy alias at line 156 |
| `tests/fixtures/saves/_build_galaxy_fixture.py` | Test | Per PROJ-436 Phase 4f comment: "planet_serde itself, `_build_galaxy_fixture` and ~15 other test files" |
| (Phase 0 audit output) — typical files | Test | `tests/integration/save_load/test_resupply_persistence.py`, `test_roundtrip_planet.py`, `test_roundtrip_ships.py`, `tests/integration/strategy/test_resource_transfer.py`, `tests/integration/strategy/turn_engine/conftest.py`, `test_resources.py`, `tests/unit/strategy/data/test_facility_resource_tracking.py`, `test_fleet_cargo_resources.py`, `test_planetary_facility_characterization.py`, `test_ship_instance_container_views.py`, `tests/unit/strategy/engine/test_resupply_engine.py`, `tests/unit/strategy/ship_instance/test_capacity_levels.py`, `test_convenience_methods.py`, `test_serialization.py`, `test_ship_instance_bridge.py`, `test_ship_instance_serializer.py`, `tests/fixtures/cargo_mock_ship.py` |
| (Phase 0 audit output) — Planet kwarg sites | Test | Currently 2 known: `tests/unit/strategy/facade/test_container_snapshots.py`, `tests/integration/strategy/test_save_round_trip_phase2.py` (verified via `staging_yard=`) |
| Tests passing `stockpile=` / `max_stockpile=` | Test | ~26 files surfaced by `rg "stockpile=|max_stockpile=|staging_yard="` — re-confirm in Phase 0 |

## Phase 3 — Delete Planet wrapper + 3 property/setter pairs

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/planet.py` | Production | Delete `_planet_init_with_legacy_kwargs` (lines 398-420) and 3 @property/@setter blocks (lines 224-262) |
| `game/strategy/data/planet_serde.py` | Production | Update `planet_to_dict` (lines 49-55) to read directly from `_stockpile` / `_max_stockpile` / `_staging_yard` instead of the now-deleted properties |
| `tests/static_guards/test_no_legacy_storage_fields.py` | Test (verify) | Confirm AST guard remains green; the field rename is unchanged |

## Phase 4 — Delete ShipInstance wrapper + 2 property/setter pairs

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production | Delete `_ship_instance_init_with_legacy_kwargs` (lines 786-833) and 2 @property/@setter blocks (lines 237-262); update `to_dict` / `from_dict` if they route through the public names |

## Phase 5 — Protocol docstring cleanups

| File | Type | Notes |
|------|------|-------|
| `game/core/protocols/strategy_domain.py` | Production | Drop F-C-014 "not read-only in absolute terms" caveat on `IShipInstance.cargo_contents` (lines 208-233); rewrite `IFacility.consumable_levels` docstring (lines 146-166) — keep the deliberate-inconsistency framing but remove any "until PROJ-444 lands" references |

## Phase 6 — Profile `Empire.resource_pool`; cache only if hot

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/empire.py` | Production (conditional) | Add cached aggregation pattern only if profiling shows hotspot; otherwise no code change |
| `Projects/active_projects/PROJ-449/decisions.md` | Doc | Profiling result row (either "cached added with invalidation hooks at X / Y" or "no perf signal observed; deferred indefinitely") |

## Verification / static guards (no edit, just confirm green)

| File | Type | Notes |
|------|------|-------|
| `tests/static_guards/test_no_legacy_storage_fields.py` | Test | Pins absence of legacy field names — unchanged by this project |
| `tests/static_guards/test_no_legacy_protocol_names.py` | Test | Should be updated if it pins the cargo_contents caveat; verify in Phase 5 |
| `tests/static_guards/test_mutator_boundary_ast_guard.py` | Test | Verify Planet / ShipInstance mutation invariants still pass after property deletion |
