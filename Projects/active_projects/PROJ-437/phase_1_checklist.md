# Phase 1: Source/destination container browsing against unified API

**Status:** In Progress (1a complete; 1b not started)
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

## Sub-phase 1b — Cutover (not started)

Expected shape:
1. RED — `tests/unit/ui/screens/test_transfer_view_model_container.py`: `available_sources` / `available_targets` entries gain `containers: tuple[ContainerSnapshotInfo, ...]`; new `get_amounts_from_containers(snapshots)` reader emits the same cargo_key → amount mapping the legacy `get_amounts(info_obj)` does (parity check). Lock browse-only behavior — `build_row_data` shape unchanged.
2. GREEN — `transfer_controller.collect_sources_and_targets` calls `facade.fleets.get_containers(id)` / `facade.planets.get_containers(id)` for each emitted entry and attaches the snapshot tuple. Field is additive; existing `{label, type, id}` shape preserved.
3. GREEN — `TransferViewModel.get_amounts_from_containers(snapshots)` mirrors the existing `get_amounts(info_obj)` mapping (resource ids → quantity; population/passengers handling) but reads from container snapshots. Legacy `get_amounts(info_obj)` stays alive through Phase 1b for the row-ordering tests.
4. Existing transfer integration tests stay green (`tests/integration/strategy/test_resource_transfer.py`, `tests/unit/ui/screens/test_transfer_controller.py`, `test_transfer_view_model.py`).
5. Manual smoke deferred to project-end (Phase 5 Codex consult covers UI integration checks).

---

## Phase Completion Checklist
- [x] Sub-phase 1a substrate complete
- [ ] Sub-phase 1b cutover complete
- [ ] Existing transfer UI tests green
- [ ] `tests/unit/ui/screens/test_transfer_view_model_container.py` green
- [ ] Full sharded suite green (post-1b)
- [ ] Update status to Complete; update plan.md + phase_state.json
