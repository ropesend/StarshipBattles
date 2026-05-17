# Phase 1: Source/destination container browsing against unified API

**Status:** Not Started
**Depends on:** phase_0 + **PROJ-436 Phase 7 verified**
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_1.planned_files

**Objective:** Replace source/destination dropdown enumeration with a query over the selected entity's `Container` list. A planet exposes facility-component containers; a fleet exposes per-ship containers (filtered by accessibility); a docked ship exposes its bay + per-component-storage containers. Browse-only — no transfer logic changes yet. Existing slider/arrow/Max UX preserved.

---

## Tasks

To be authored at phase start, informed by the Phase 0 migration map.

Expected shape:
1. RED — `test_transfer_view_model_container.py`: `available_sources` / `available_targets` populated from `Container` enumeration; dropdown labels include entity + container kind.
2. GREEN — `transfer_view_model.py` enumeration switched to Container queries via `fleet_data_source.py`.
3. `transfer_controller.py` selection wiring updated for `ContainerRef` identity.
4. Existing transfer integration tests stay green (`tests/integration/strategy/test_resource_transfer.py`).
5. Manual smoke: open transfer dialog from planet view, fleet view, ship view; confirm container options listed.

---

## Phase Completion Checklist
- [ ] All sub-phases complete
- [ ] Existing transfer UI tests green
- [ ] `tests/unit/ui/screens/test_transfer_view_model_container.py` green
- [ ] Manual smoke complete
- [ ] Full sharded suite green
- [ ] Update status to Complete; update plan.md + phase_state.json
