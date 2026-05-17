# Phase 5: `Empire._fleet_resource_pool` deletion + `resource_pool` semantics

**Status:** Not Started
**Depends on:** phase_4
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_5.planned_files

**Objective:** Delete `Empire._fleet_resource_pool: Dict[str, float]` durable state (self-flagged TODO in current code per `empire.py:58-60`). Fleet construction resources move into per-fleet/per-ship `Container`s on operational components. `Empire.resource_pool` property becomes a pure aggregation query that walks every container in the empire's planets + fleets + ships and sums by `resource_id`. Per Phase 0 D2 default: ship pure-query, defer caching to post-Phase-5 profiling. Migrate all read sites (build-queue projector, empire economy calculator, treasury panel).

---

## Tasks

To be authored at phase start. Expected sub-phase shape:
- 5a — substrate: `Empire.resource_pool` pure-query implementation walking all containers.
- 5b — migrate `EmpireEconomyCalculator` to use the new aggregation API.
- 5c — migrate build-queue projector to read fleet construction resources from per-fleet containers, not `_fleet_resource_pool`.
- 5d — migrate `EmpireWriteService` writes from `_fleet_resource_pool` to the relevant container.
- 5e — migrate empire serializer; drop `_fleet_resource_pool` key from save shape.
- 5f — final cutover: delete `_fleet_resource_pool` field + setter on `resource_pool` property; AST guard.
- 5g — profile `Empire.resource_pool` aggregation on a large-empire fixture; decide D2 caching question; if needed add caching with explicit invalidation (PROJ-293 pattern).

---

## Phase Completion Checklist
- [ ] All sub-phases complete
- [ ] `tests/integration/test_empire_resource_aggregation.py` green
- [ ] Build-queue + treasury panel UI smoke tests green
- [ ] D2 profiling result logged in `decisions.md`
- [ ] Full sharded suite green
- [ ] Update status to Complete; update plan.md + phase_state.json
