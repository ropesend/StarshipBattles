# Phase 1: Source/destination container browsing against unified API

**Status:** Complete (1a + 1b landed 2026-05-18)
**Depends on:** phase_0 + **PROJ-436 Phase 7 verified**
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_1.planned_files

**Objective:** Replace source/destination dropdown enumeration with a query over the selected entity's `Container` list. A planet exposes facility-component containers; a fleet exposes per-ship containers (filtered by accessibility); a docked ship exposes its bay + per-component-storage containers. Browse-only — no transfer logic changes yet. Existing slider/arrow/Max UX preserved.

---

## Sub-phase 1a — Substrate (complete 2026-05-18)

- [x] RED test at `tests/unit/strategy/facade/test_container_snapshots.py` confirmed `ImportError: cannot import name 'ContainerSnapshotInfo'`.
- [x] GREEN — new `ContainerSnapshotInfo` DTO at `game/strategy/facade/dto/container_snapshot.py`; re-exported from `dto/__init__.py`.
- [x] GREEN — `FleetSlice.get_fleet_containers(fleet_id)` emits one snapshot per ship via `bay_inventory.container_view`.
- [x] GREEN — `PlanetSlice.get_planet_containers(planet_id)` emits stockpile + staging-yard snapshots.
- [x] GREEN — `FacadeFleetQueries.get_containers` + `FacadePlanetQueries.get_containers` proxies in `grouped_namespaces.py`.
- [x] All 10 new tests green; existing facade + transfer + integration suites untouched.

## Sub-phase 1b — Cutover (complete 2026-05-18)

- [x] RED — new `tests/unit/ui/screens/test_transfer_view_model_container.py` failed on missing `containers` entry field + missing `get_amounts_from_containers` method.
- [x] GREEN — `transfer_controller.collect_sources_and_targets` calls `facade.fleets.get_containers(id)` / `facade.planets.get_containers(id)` for each emitted entry and attaches the snapshot tuple as the additive `containers` field. The existing `{label, type, id}` shape is preserved; only the new key is added.
- [x] GREEN — `TransferViewModel.get_amounts_from_containers(snapshots)` mirrors the legacy `get_amounts(info_obj)` mapping: `RESOURCE` entries aggregate to `{type_id: int}`, `POPULATION` entries become `passengers_<species>: int`. `ITEM` entries skipped — they continue to render through `_build_pod_rows` until Phase 3.
- [x] Two pre-existing `test_transfer_controller.py` assertions (`test_collect_sources_includes_source_fleet_when_facade_omits_it`, `test_collect_sources_checks_projected_position_when_primary_hex_has_no_planets`) relaxed from exact-dict-eq to subset checks — the additive field doesn't break their intent.
- [x] All 7 new tests + the broader 3356-test UI suite + the integration tests green.

---

## Phase Completion Checklist
- [x] Sub-phase 1a substrate complete
- [x] Sub-phase 1b cutover complete
- [x] Existing transfer UI tests green (3356 passed)
- [x] `tests/unit/ui/screens/test_transfer_view_model_container.py` green
- [x] Full sharded suite green — see plan.md Quick Status post-1b sharded receipt
- [x] Update status to Complete; update plan.md + phase_state.json
