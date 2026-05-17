# TD-05: Split runtime production design lookup from savegame filesystem and replace static replay-store ownership

**Status:** VERIFIED
**Source report:** `Reviews/results/2026-05-16_strategy-layer-tech-debt-review/report.md` section TD-05
**Primary runtime files:** `game/strategy/engine/production_spawner.py`, `game/strategy/systems/design_library.py`, `game/strategy/systems/save_game_service.py`

---

## Verification Summary

This problem is real and current.

Validated facts:
- `ProductionSpawner` still imports `DesignLibrary` directly and still loads designs from disk during spawn paths.
- `ProductionEngine` still threads `save_path` through production tick processing to support those disk reads.
- `AddToConstructionQueueCommandHandler` also instantiates `DesignLibrary` directly for validation and cost lookup.
- `quickstart_builder.spawn_initial_complexes(...)` still instantiates `DesignLibrary` directly.
- `DesignLibrary` still mixes filesystem policy, JSON I/O, per-turn UI cache behavior, and convenience filtering in one class.
- `SaveGameService` still uses the module-global `_replay_store` with `set_replay_store()` and `get_replay_store()`.

The architectural problem is twofold:
1. runtime production reads mutable save-folder design JSON mid-turn;
2. replay-store lifecycle is owned by a process-wide global instead of an instance/service boundary.

---

## End State

The plan is done when all of the following are true:
- Production and construction-queue validation resolve design data through an in-memory catalog, not through save-folder disk reads.
- `save_path` is no longer part of the runtime production-spawn call chain.
- Filesystem and JSON persistence live in a repository object.
- UI caching lives with the in-memory catalog, not in the disk repository.
- `SaveGameService` owns replay-store lifecycle through an instance field or constructor dependency, not through a module-global variable.
- `DesignLibrary` is either deleted or reduced to a thin temporary migration shim with zero runtime callers.

---

## Weak-LLM Guardrails

- Do not change save schema in the same phase that removes production disk I/O unless a phase explicitly says to do so.
- Do not migrate every caller in one step. Move runtime production first, then UI callers, then delete the old shim.
- Keep `DesignLibrary` available as a compatibility shim until `rg -n "DesignLibrary"` shows no remaining production or UI callers.
- Default built-count policy for this plan is **deferred repository write-back**, not a new `Empire` field. That keeps this plan focused and avoids an unnecessary schema bump.
- Convert `SaveGameService` call sites in one contained phase. Do not leave half the repo using statics and half using instances.

---

## File Touch Map

Core runtime files:
- `game/strategy/engine/production_spawner.py`
- `game/strategy/engine/production_engine.py`
- `game/strategy/engine/handlers/construction_queue.py`
- `game/strategy/quickstart_builder.py`
- `game/strategy/systems/design_library.py`
- new `game/strategy/systems/design_repository.py`
- new `game/strategy/systems/design_catalog.py`
- `game/strategy/systems/save_game_service.py`
- `game/strategy/facade/slices/_facade_state.py`
- `game/strategy/engine/game_session.py`
- `game/app_bootstrap.py`

Likely UI migration files:
- `game/ui/screens/workshop_ship_io.py`
- `game/ui/screens/strategy_build_queue_manager.py`
- `game/ui/screens/transfer_controller.py`
- any other `DesignLibrary(...)` caller found by grep

Existing tests to extend first:
- `tests/unit/strategy/design_library/test_basics.py`
- `tests/unit/strategy/design_library/test_scan_designs_caching.py`
- `tests/unit/strategy/design_library/test_design_load_result.py`
- `tests/unit/strategy/save_game_service/test_save_load_ops.py`
- `tests/unit/strategy/save_game_service/test_error_handling.py`
- `tests/unit/strategy/engine/test_production_spawner.py`
- `tests/unit/strategy/production_engine/test_spawning.py`
- `tests/integration/strategy/production/test_completion.py`
- `tests/integration/strategy/production/test_fleet_production_e2e.py`
- `tests/integration/replay/test_replay_store.py`
- `tests/unit/quickstart/test_quickstart_builder.py`

New test packages are acceptable once the new classes exist:
- `tests/unit/strategy/design_catalog/`
- `tests/unit/strategy/design_repository/`

---

## Phased Remediation Plan

### Phase 0 - Lock the current behavior with red tests

Add or extend tests that prove the current coupling points before changing code.

Required assertions:
- production spawning currently depends on design lookup, built-count recording, and save-path plumbing;
- save/load/delete replay-store hooks are currently triggered by `SaveGameService`;
- UI design scans currently reuse per-turn cache state.

Preferred test homes:
- `tests/unit/strategy/engine/test_production_spawner.py`
- `tests/unit/strategy/production_engine/test_spawning.py`
- `tests/unit/strategy/save_game_service/test_save_load_ops.py`
- `tests/unit/strategy/design_library/test_scan_designs_caching.py`

If you add a new "no disk read during tick" test, place it under:
- `tests/integration/strategy/production/`

### Phase 1 - Introduce `DesignRepository` without changing callers

Touch list:
- new `game/strategy/systems/design_repository.py`
- optionally a tiny shared result-type module if needed
- `tests/unit/strategy/design_repository/`

Scope:
- Move disk-bound responsibilities out of `DesignLibrary` into `DesignRepository`.
- Keep `DesignLoadResult` shape unchanged.
- Keep save-folder and temp-folder policy here for now.

Repository responsibilities:
- locate folder
- create folder
- `scan_designs`
- `save_design`
- `load_design_data`
- `mark_design_obsolete`
- `increment_built_count`

Do not migrate runtime or UI callers yet. This phase should be additive.

### Phase 2 - Introduce `DesignCatalog` and move cache ownership there

Touch list:
- new `game/strategy/systems/design_catalog.py`
- `game/strategy/facade/slices/_facade_state.py`
- `game/strategy/engine/game_session.py`
- tests under `tests/unit/strategy/design_catalog/`

Catalog responsibilities:
- in-memory design lookup by `design_id`
- per-turn filtered/list views for UI
- pending built-count increments
- explicit refresh or repopulate from repository

Implementation rules:
- populate catalogs from `DesignRepository` during session/bootstrap boundaries, not during production ticks;
- move `FacadeSessionState.designs_by_empire` behavior here;
- give `GameSession` a concrete accessor such as `get_design_catalog(empire_id)` or `design_catalogs_by_empire[empire_id]`.

Do not remove `DesignLibrary` yet. Existing callers can keep using it while the catalog is introduced.

### Phase 3 - Migrate runtime production to the catalog

Touch list:
- `game/strategy/engine/production_spawner.py`
- `game/strategy/engine/production_engine.py`
- `game/strategy/engine/handlers/construction_queue.py`
- `game/strategy/quickstart_builder.py`
- relevant production tests

Execution order inside this phase:
1. add failing tests proving spawn paths use the catalog and do not read design JSON directly;
2. change `ProductionSpawner` to accept a catalog or catalog-provider dependency;
3. remove `DesignLibrary` import from `production_spawner.py`;
4. stop threading `save_path` through spawn helper methods;
5. migrate `AddToConstructionQueueCommandHandler` validation and cost lookup to the same catalog source;
6. migrate quickstart initial-complex spawn to populate/read through the catalog.

Required grep before and after:

```bash
rg -n "DesignLibrary|save_path" game/strategy/engine/production_spawner.py game/strategy/engine/production_engine.py game/strategy/engine/handlers/construction_queue.py game/strategy/quickstart_builder.py
```

Success condition for this phase:
- runtime production no longer requires a save-folder path to resolve design JSON during a tick.

### Phase 4 - Implement built-count write-back without mid-tick disk writes

Default approach for this plan:
- `DesignCatalog` tracks pending increments in memory;
- save-time code flushes those increments through `DesignRepository`.

Why this is the default:
- it removes per-spawn disk writes;
- it avoids a save-schema change;
- it keeps this plan focused on runtime/persistence separation.

Touch list:
- `game/strategy/systems/design_catalog.py`
- `game/strategy/systems/design_repository.py`
- `game/strategy/systems/save_game_service.py`
- tests for built-count flush behavior

Do not add `Empire.designs_built_count` in this plan unless a separate decision explicitly approves a save-format change.

### Phase 5 - Convert `SaveGameService` to instance-owned replay-store wiring

Touch list:
- `game/strategy/systems/save_game_service.py`
- `game/app_bootstrap.py`
- all `SaveGameService.` call sites found by grep
- replay/save-load tests

Execution steps:
1. add failing tests that construct `SaveGameService(replay_store=spy)` and assert save/load/delete notify the spy correctly;
2. convert replay-store notifications to instance methods;
3. remove `_replay_store`, `set_replay_store`, and `get_replay_store`;
4. update bootstrap wiring to construct a service instance instead of registering a global;
5. update tests to use explicit service instances.

Required grep before finalizing this phase:

```bash
rg -n "_replay_store|set_replay_store|get_replay_store|SaveGameService\." game tests
```

Do not leave both global and instance ownership paths active.

### Phase 6 - Migrate UI callers and delete the old shim

Touch list:
- all remaining `DesignLibrary(...)` callers
- `game/strategy/systems/design_library.py`
- docs if runtime flow descriptions change

Execution steps:
1. grep for all remaining `DesignLibrary` callers;
2. migrate each caller to `DesignCatalog` or `DesignRepository` based on whether it needs runtime reads or disk writes;
3. confirm no production path still imports `DesignLibrary`;
4. delete `DesignLibrary` or reduce it to a zero-logic alias only if a separate follow-up will remove the alias immediately.

Deletion gate:

```bash
rg -n "DesignLibrary" game tests docs
```

Do not delete the file while live callers still exist.

---

## Test Strategy

Run targeted suites at the end of each phase that changes behavior:

```bash
pytest tests/unit/strategy/design_library/ -x
pytest tests/unit/strategy/design_catalog/ tests/unit/strategy/design_repository/ -x
pytest tests/unit/strategy/engine/test_production_spawner.py tests/unit/strategy/production_engine/test_spawning.py -x
pytest tests/integration/strategy/production/ -x
pytest tests/unit/strategy/save_game_service/ tests/integration/replay/test_replay_store.py -x
pytest tests/unit/quickstart/test_quickstart_builder.py -x
```

Only after focused suites are green:

```bash
python Tools/test_sharded/test_sharded.py
```

Minimum special-case coverage:
- no design-disk read during a production tick;
- built-count increments are not written mid-tick;
- replay store switches save roots correctly on save/load/delete;
- UI sees newly saved designs through the new catalog path.

---

## Risks And Mitigations

| Risk | Mitigation |
|---|---|
| A weak LLM tries to replace runtime I/O and replay-store globals in one uncontrolled sweep. | Separate them into Phases 3 through 5 with independent tests. |
| Built-count handling expands into a save-format redesign. | Default this plan to deferred repository write-back and prohibit schema changes unless separately approved. |
| `DesignLibrary` is deleted too early and live UI callers break. | Keep it until grep proves all callers are migrated. |
| Runtime production accidentally repopulates the catalog from disk during the tick. | Add an explicit no-disk-read test in the production integration suite. |
| The repo ends up with mixed static and instance `SaveGameService` usage. | Convert all `SaveGameService` call sites in one contained phase and grep for leftovers. |

---

## Ordering Constraints

Hard ordering constraints:
- None.

Soft ordering notes:
- TD-02 is helpful, but not required. This plan can introduce catalog/repository ownership on the current `GameSession`.
- TD-06 is helpful, but not required. Production can keep calling `ShipInstance.create` or its shim.
- TD-03 is adjacent because `construction_queue.py` is touched in both plans, but neither blocks the other.

Effect on `EXECUTION_ORDER.md`:
- Remove any hard `TD-02 -> TD-05` or `TD-06 -> TD-05` dependency language.
- Keep those as soft sequencing preferences only.

---

## Acceptance Criteria

- [ ] Runtime production no longer reads design JSON from the save folder during a tick.
- [ ] Runtime production no longer depends on `save_path` for design lookup.
- [ ] `DesignRepository` owns filesystem and JSON persistence responsibilities.
- [ ] `DesignCatalog` owns in-memory runtime lookup and per-turn UI cache behavior.
- [ ] Built-count updates are not written mid-tick.
- [ ] `SaveGameService` owns replay-store lifecycle through an instance dependency, not a module-global variable.
- [ ] No live runtime caller still imports `DesignLibrary`.
- [ ] Focused production, design-library/catalog, save-load, replay, and quickstart suites are green before the sharded run.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.
