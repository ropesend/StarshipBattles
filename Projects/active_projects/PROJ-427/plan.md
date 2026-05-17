# PROJ-427: Production/persistence split (TD-05)

**Execution Protocol:** 03c-phase-aware-execution

> **WORKING ON THIS PROJECT:**
> - Read the source plan [`TD-05_production_persistence_split.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-05_production_persistence_split.md) for the full specification.
> - Read [`design.md`](design.md) for the verified architectural split (repository vs catalog) and the replay-store conversion model.
> - Open the phase checklist for your current phase.
> - Check off tasks as you complete them.
> - Update Current State before stopping work.

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-427 [phase]` before stopping.
> - Update Current State with specific handoff context.

## Quick Status

| Phase | Status | Checklist | Depends on |
|-------|--------|-----------|------------|
| 0. Lock current behavior with red tests | Complete | [phase_0_checklist.md](phase_0_checklist.md) | — |
| 1. Introduce `DesignRepository` (additive, no caller migration) | Complete | [phase_1_checklist.md](phase_1_checklist.md) | Phase 0 |
| 2. Introduce `DesignCatalog` and move cache ownership | Complete (scope-narrowed: absorption only; cache migration deferred to Phase 6) | [phase_2_checklist.md](phase_2_checklist.md) | Phase 1 |
| 3. Migrate runtime production to the catalog | Complete (Committed) | [phase_3_checklist.md](phase_3_checklist.md) | Phase 2 |
| 4. Built-count write-back (deferred, no mid-tick disk writes) | Complete (Committed) | [phase_4_checklist.md](phase_4_checklist.md) | Phase 3 |
| 5. Convert `SaveGameService` to instance-owned replay-store wiring | Complete (Committed) | [phase_5_checklist.md](phase_5_checklist.md) | Phase 4 |
| 6. Migrate UI callers and delete the old `DesignLibrary` shim | Partial (dependency inversion + 1 UI migration complete; 3 UI screens + deletion deferred) | [phase_6_checklist.md](phase_6_checklist.md) | Phase 5 |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** Phase 6 partial; deletion deferred.
**Last Action:** Phase 6 (partial) — Dependency inversion completed: `DesignLoadResult` value type relocated from `game/strategy/systems/design_library.py` to `game/strategy/systems/design_repository.py`; `design_library.py` re-exports for backwards compatibility so existing importers keep working. `design_repository.py` no longer imports from `design_library`. First UI caller migrated: `game/ui/screens/transfer_controller.py::discover_pod_designs` now reads through `session.services.design_catalogs_by_empire[empire_id]` and filters in-memory for `vehicle_type == "Drop Pod"`; its tests were rewritten to monkeypatch the catalog instead of `DesignLibrary`. Three substantial UI files (`workshop_ship_io.py` 254 LOC, `strategy_build_queue_manager.py` 340 LOC, `design_selector_window.py` 705 LOC) and their associated test suites remain on `DesignLibrary` and are deferred to a follow-up slot per the decision logged in `decisions.md`. `DesignLibrary` is NOT deleted; the deletion gate intentionally fails until those three screens migrate.
**Next Action:** Schedule follow-up slot to migrate `workshop_ship_io.py`, `strategy_build_queue_manager.py`, and `design_selector_window.py` (with QA-Obs-3 cache-invalidation parity), update remaining ~25 test files, then re-run the Phase 6 deletion gate and delete `design_library.py`.
**Blockers:** Phase 6 UI migration of 3 large UI screens + ~25 test files exceeded the single-slot budget when combined with the strict TDD discipline required for cache-invalidation parity. Specifically deferred: `workshop_ship_io.py` (rich `save_design(ship, name, built_designs)` flow with overwrite-protection and per-turn cache invalidation), `strategy_build_queue_manager.py` (4 `DesignLibrary(...)` construction sites threaded through build-queue subsystems), `design_selector_window.py` (`design_library`-typed constructor parameter; `search_designs`, `filter_designs`, `mark_obsolete` callers). All other Phase 6 partial work is committed and tree-green.

## Overview

`ProductionSpawner`, `AddToConstructionQueueCommandHandler`, and `quickstart_builder.spawn_initial_complexes(...)` all instantiate `DesignLibrary(save_path, empire.id)` directly and read mutable save-folder design JSON mid-turn. `DesignLibrary` itself mixes filesystem policy, JSON I/O, per-turn UI cache behavior, and convenience filtering in one class. `SaveGameService` owns the replay store through the module-global `_replay_store` (with `set_replay_store()` / `get_replay_store()`), and `FacadeSessionState.designs_by_empire` couples UI caching to that same disk-coupled object. PROJ-427 separates these concerns into a `DesignRepository` (filesystem + JSON persistence) and a per-empire `DesignCatalog` (in-memory runtime lookup + per-turn UI cache + pending built-count increments), converts `SaveGameService` to instance-owned replay-store wiring, and removes `save_path` from the runtime production-spawn call chain.

## Goals

- Production and construction-queue validation resolve design data through an in-memory catalog, not save-folder disk reads.
- `save_path` is no longer part of the runtime production-spawn call chain.
- `DesignRepository` owns filesystem and JSON persistence; `DesignCatalog` owns in-memory runtime lookup and per-turn UI cache behavior.
- Built-count updates are not written mid-tick; pending increments flush through `DesignRepository` at save time.
- `SaveGameService` owns the replay-store lifecycle through an instance field or constructor dependency — no module-global `_replay_store`.
- `DesignLibrary` is deleted (or reduced to a zero-logic alias slated for immediate follow-up removal) once `rg -n "DesignLibrary"` shows no remaining production or UI callers.

## Scope

**In:**
- New files `game/strategy/systems/design_repository.py` and `game/strategy/systems/design_catalog.py`.
- Refactor of `game/strategy/engine/production_spawner.py`, `game/strategy/engine/production_engine.py`, `game/strategy/engine/handlers/construction_queue.py`, `game/strategy/quickstart_builder.py` to drop `DesignLibrary` and `save_path`.
- `game/strategy/systems/save_game_service.py` conversion from module-global `_replay_store` to instance-owned wiring; bootstrap update at `game/app_bootstrap.py`.
- `game/strategy/facade/slices/_facade_state.py` migration of `designs_by_empire` UI cache into the new catalog.
- `game/strategy/engine/game_session.py` accessor (`get_design_catalog(empire_id)` or `design_catalogs_by_empire[empire_id]`); see Dependencies for the cross-plan note on absorbing this into `SessionRuntimeServices` if PROJ-423 lands later.
- UI caller migration (`workshop_ship_io.py`, `strategy_build_queue_manager.py`, `transfer_controller.py`, and any other site found by `rg -n "DesignLibrary"`).
- Deletion of `game/strategy/systems/design_library.py` (or reduction to a zero-logic alias) once the grep gate passes.
- Test extensions in the existing design-library / save-game-service / production / replay / quickstart suites plus new `tests/unit/strategy/design_catalog/` and `tests/unit/strategy/design_repository/` packages.

**Out:**
- Save-format / save-schema changes. The TD-05 source plan's "Weak-LLM Guardrails" forbid mixing schema changes into the same phase that removes production disk I/O; default policy is **deferred repository write-back** for built counts, with no new `Empire.designs_built_count` field. Any future save-format bump (e.g., a hypothetical v4.0.0) is its own separately-approved phase outside this project.
- Migration of every `GameSession(...)` / `SaveGameService.` call site beyond what is needed to remove the module-global and the runtime `DesignLibrary` import. Mass call-site sweeps belong to neighbouring projects.
- Any TD-02 (PROJ-423) or TD-06 (PROJ-425) work that is not strictly required by this extraction.

## Dependencies

Hard predecessors: none. Soft predecessors: PROJ-423 (TD-02 GameSession lifecycle) and PROJ-425 (TD-06 ShipInstance) are helpful but not required.

Catalog and repository ownership lives on the current `GameSession` if PROJ-423 has not landed yet — `get_design_catalog(empire_id)` or `design_catalogs_by_empire[empire_id]` is added directly to `GameSession`. If PROJ-423 lands later, that accessor must migrate into `SessionRuntimeServices` (or into `SessionBootstrapState` for the per-empire catalogs, since they are per-empire runtime state); see the TD-02 cross-plan note in [`TD-02_game_session_lifecycle.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-02_game_session_lifecycle.md) ("Cross-plan coupling with TD-05") and the PROJ-423 plan at [`../PROJ-423/plan.md`](../PROJ-423/plan.md) for the absorption migration.

TD-03 is adjacent because `construction_queue.py` is touched in both plans, but neither blocks the other.

## Key Files

| Component | File Path | Action |
|-----------|-----------|--------|
| Production spawner | `game/strategy/engine/production_spawner.py` | Edit (drop `DesignLibrary` import, drop `save_path` plumbing) |
| Production engine | `game/strategy/engine/production_engine.py` | Edit (stop threading `save_path` through tick processing) |
| Construction-queue handler | `game/strategy/engine/handlers/construction_queue.py` | Edit (validation and cost lookup through catalog) |
| Quickstart builder | `game/strategy/quickstart_builder.py` | Edit (initial-complex spawn through catalog) |
| Design library (legacy) | `game/strategy/systems/design_library.py` | Keep as shim through Phase 5; delete or alias in Phase 6 |
| Design repository (new) | `game/strategy/systems/design_repository.py` | Add (filesystem + JSON persistence) |
| Design catalog (new) | `game/strategy/systems/design_catalog.py` | Add (in-memory lookup, per-turn UI cache, pending built-count increments) |
| Save-game service | `game/strategy/systems/save_game_service.py` | Edit (instance-owned replay store; built-count flush) |
| Facade session state | `game/strategy/facade/slices/_facade_state.py` | Edit (move `designs_by_empire` UI cache into catalog) |
| Game session | `game/strategy/engine/game_session.py` | Edit (add `get_design_catalog(empire_id)` accessor; see TD-02 cross-plan note) |
| App bootstrap | `game/app_bootstrap.py` | Edit (construct `SaveGameService` instance instead of registering a global) |
| Workshop ship I/O | `game/ui/screens/workshop_ship_io.py` | Edit (UI caller migration) |
| Strategy build-queue manager | `game/ui/screens/strategy_build_queue_manager.py` | Edit (UI caller migration) |
| Transfer controller | `game/ui/screens/transfer_controller.py` | Edit (UI caller migration) |

See [`manifest.md`](manifest.md) for the full per-phase touch list including the test files extended in Phase 0.

## Related Documents

- Source plan: [`TD-05_production_persistence_split.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-05_production_persistence_split.md)
- Execution order reference: [`EXECUTION_ORDER.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md)
- Soft-predecessor (cross-plan absorption note): [`../PROJ-423/plan.md`](../PROJ-423/plan.md) and [`TD-02_game_session_lifecycle.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-02_game_session_lifecycle.md) section "Cross-plan coupling with TD-05"
- Project design notes: [`design.md`](design.md)
- Decisions log: [`decisions.md`](decisions.md)
- Per-phase file manifest: [`manifest.md`](manifest.md)
- Findings ledger: [`findings_ledger.md`](findings_ledger.md)

## Verification

- [ ] Explicit "no design-disk read during production tick" integration test exists under `tests/integration/strategy/production/` and is green.
- [ ] `rg -n "DesignLibrary|save_path" game/strategy/engine/production_spawner.py game/strategy/engine/production_engine.py game/strategy/engine/handlers/construction_queue.py game/strategy/quickstart_builder.py` returns no matches in the runtime production / construction / quickstart call chain.
- [ ] `rg -n "_replay_store|set_replay_store|get_replay_store"` returns no matches in `game/` (module-global ownership eliminated).
- [ ] `rg -n "SaveGameService\."` shows only instance-method call sites, no static-style usage.
- [ ] Built-count updates do not occur during the production tick (Phase 4 flush test green).
- [ ] `FacadeSessionState.designs_by_empire` UI cache behavior is served by `DesignCatalog`, not by a disk-coupled object.
- [ ] `rg -n "DesignLibrary" game tests docs` returns no remaining production or UI callers (deletion gate before Phase 6 completes).
- [ ] Focused suites green: `tests/unit/strategy/design_library/`, `tests/unit/strategy/design_catalog/`, `tests/unit/strategy/design_repository/`, `tests/unit/strategy/engine/test_production_spawner.py`, `tests/unit/strategy/production_engine/test_spawning.py`, `tests/integration/strategy/production/`, `tests/unit/strategy/save_game_service/`, `tests/integration/replay/test_replay_store.py`, `tests/unit/quickstart/test_quickstart_builder.py`.
- [ ] `python Tools/test_sharded/test_sharded.py` is green after every phase that changes runtime behavior, and again at project close.
- [ ] All phase checklists complete; findings ledger has no `open` or `addressed_pending_review` entries at audit time.
