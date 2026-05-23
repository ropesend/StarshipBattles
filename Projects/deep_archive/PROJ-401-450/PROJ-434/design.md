# PROJ-434: Complete DesignLibrary deletion — design

## Source

PROJ-427's Phase 6 partial-close on 2026-05-17. Two consecutive Phase-6 subagents (the operator-budget halt at the original phase-0 entry, and the partial-completion entry that landed the dependency inversion + `transfer_controller` migration) independently deferred the remaining UI migration citing the same blockers. Their analysis is preserved verbatim in [`../PROJ-427/decisions.md`](../PROJ-427/decisions.md) — the 2026-05-17 "Project halted at Phase 0 entry; scope-vs-budget blocker" entry and the 2026-05-17 "Phase 6 partial" entry. This project spins their deferred remainder out of PROJ-427 so the linear arc can proceed.

PROJ-427 Phase 6 stopped after:

- `DesignLoadResult` value type relocated from `design_library.py` to `design_repository.py`; `design_library.py` re-exports it for backwards compatibility.
- `design_repository.py` no longer imports from `design_library.py` (dependency inversion landed).
- `game/ui/screens/transfer_controller.py::discover_pod_designs` migrated: now reads through `session.services.design_catalogs_by_empire[empire_id]` and filters in-memory for `vehicle_type == "Drop Pod"`. Its test fixtures repoint the monkeypatch from `DesignLibrary` to the catalog.

What remains:

- 3 UI screens (`workshop_ship_io.py` 254 LOC, `strategy_build_queue_manager.py` 340 LOC, `design_selector_window.py` 705 LOC).
- 4 panel collaborators of the build-queue family (`build_queue_screen.py`, `build_queue_controller.py`, `build_queue_drag_handler.py`, `build_queue_portrait_loader.py`).
- ~30 test files (the ones that monkeypatch `game.strategy.engine.production_spawner.DesignLibrary` at the module boundary, plus UI-screen test fixtures).
- API gaps on `DesignCatalog`/`DesignRepository` that the deferred screens depend on.
- The QA-Obs-3 cache contract on the workshop save flow, currently enforced by `DesignLibrary`'s per-turn cache side effects, must be served by `DesignCatalog` before workshop migration is safe.

`DesignLibrary` cannot be deleted until all of the above migrate; PROJ-427's Phase 6 deletion gate intentionally fails until then.

## Collaborator chain

The `BuildQueueScreen` family is the reason a clean "migrate one screen at a time" approach does not work for Phase 1. Four files participate:

- **`game/ui/screens/build_queue_screen.py`** — top-level screen; constructs `DesignLibrary(save_path, empire.id)` and passes references into its panel collaborators.
- **`game/ui/screens/build_queue_controller.py`** — state mutation (queue reorders, cancellations). Holds a reference to the same `DesignLibrary` instance and calls `load_design_data` / `scan_designs` directly to refresh queue tooltips.
- **`game/ui/screens/build_queue_drag_handler.py`** — drag-and-drop. Reads design metadata from the `DesignLibrary` instance during drag previews.
- **`game/ui/screens/build_queue_portrait_loader.py`** — thumbnail caching. Calls `get_design_path` (filesystem) to load portrait PNGs and pickles the cache keyed on design path.

Migrating only the screen would leave the three collaborators with stale `DesignLibrary` references; migrating only a collaborator would orphan it from the screen's shared state. They must move together in a single phase.

`strategy_build_queue_manager.py` (Phase 2) is a separate manager that lives outside this collaborator chain — it manages cross-screen build queue state (which is why it has 4 independent `DesignLibrary(...)` construction sites) but does not share `DesignLibrary` instances with the `BuildQueueScreen` family.

## API gaps on `DesignCatalog` / `DesignRepository`

PROJ-427 introduced the catalog/repository pair with a minimal surface sufficient for the runtime production migration (Phase 3) and the `transfer_controller.discover_pod_designs` migration. The deferred UI callers need additional methods:

| Method | Owner | Currently on `DesignLibrary` | Used by |
|--------|-------|------------------------------|---------|
| `scan_designs(empire_id)` | `DesignRepository` | yes | `BuildQueueController`, `strategy_build_queue_manager.py`, `design_selector_window.py` initial population |
| `load_design_data(design_id)` | `DesignRepository` | yes | `BuildQueueController`, `BuildQueueDragHandler` tooltip metadata |
| `get_design_path(design_id)` | `DesignRepository` | yes | `BuildQueuePortraitLoader` cache keys |
| `search_designs(query)` | `DesignCatalog` | yes | `design_selector_window.py` search box |
| `filter_designs(predicate)` | `DesignCatalog` | yes | `design_selector_window.py` filter chips; `transfer_controller.discover_pod_designs` (already migrated using an in-memory equivalent) |
| `save_design(ship, name, built_designs)` (rich) | `DesignRepository` | yes | `workshop_ship_io.py` |
| `mark_obsolete(design_id)` | `DesignRepository` | yes | `design_selector_window.py` |

PROJ-427's 2026-05-17 decisions log explicitly recorded that the **low-level** `save_design_data(design_id, data)` lives on `DesignRepository` but the rich `save_design(ship, name, built_designs)` workshop flow does not. The rich variant welds three responsibilities — metadata embedding, overwrite-protection against already-built designs, and per-turn UI cache invalidation — and PROJ-427 deliberately left it on `DesignLibrary` until Phase 6 could move it. Phase 0 here picks it up.

## QA-Obs-3 cache contract

The QA-Obs-3 issue (`docs/_ignore` / archived) was: after the workshop saved a new design, the same-empire viewer's design selector showed stale data until next turn because the per-turn UI cache was not invalidated. The fix on `DesignLibrary` was to make `save_design` clear `_scan_cache` on the same instance so the next `scan_designs` call re-read from disk. `FacadeSessionState.designs_by_empire` held those `DesignLibrary` instances per-empire, so the invalidation followed naturally.

PROJ-427's 2026-05-17 decision narrowed Phase 2 scope ("Phase 2 scope narrowed: cache migration + `FacadeSessionState.designs_by_empire` deferred to Phase 6") explicitly because that cache contract is a caller migration, not an additive change. The catalog already owns its own per-turn cache (PROJ-427 Phase 2 task 2.3 was the deferred slot for wiring it up). Phase 0 here completes that wiring:

- `DesignCatalog.save_design(...)` must invalidate the catalog's per-turn cache so the next read repopulates from `DesignRepository.scan_designs`.
- `FacadeSessionState.designs_by_empire` must resolve through `session.services.design_catalogs_by_empire[empire_id]` rather than through a `DesignLibrary` instance.
- A focused regression test must cover: workshop save → same-empire viewer reads the new design on the next `designs_by_empire[...]` access without a turn advance.

## Deletion gate

PROJ-427's Phase 6 deletion gate:

```
rg -n "DesignLibrary" game tests docs
```

Must return zero live hits — meaning no `import DesignLibrary`, no `DesignLibrary(...)` construction, no `from game.strategy.systems.design_library import ...`. Historical mentions in `Projects/active_projects/PROJ-427/` markdown are fine. Once the gate passes, `game/strategy/systems/design_library.py` is deleted and the `DesignLoadResult` re-export shim is removed (the canonical home is `design_repository.py` per PROJ-427's 2026-05-17 dependency-inversion decision).

## Risk register

- **API parity drift:** the additive methods in Phase 0 must match the existing `DesignLibrary` contract byte-for-byte. Subtle differences (e.g. `scan_designs` ordering, `search_designs` substring vs. prefix match) will surface as UI test failures in Phase 1 / Phase 2. Mitigation: Phase 0 includes characterization tests that pin the `DesignLibrary` behavior, then re-runs the same tests against the new methods.
- **`BuildQueueScreen` shared-state coupling:** the four collaborators must be migrated atomically (see "Collaborator chain"). Mitigation: Phase 1 treats them as a single unit.
- **QA-Obs-3 regression:** if the cache contract is not wired correctly, workshop saves silently fail to appear in the design selector until next turn. Mitigation: the Phase 0 regression test described above.
- **Test fixture monkeypatch sites:** ~30 test files patch `DesignLibrary` at module boundaries (e.g. `game.strategy.engine.production_spawner.DesignLibrary`). Phase 1 and Phase 2 must repoint each monkeypatch onto the catalog/repository at the new import location. Mitigation: enumerate the patch sites in the manifest before starting Phase 1.
- **Docs drift:** any text in `docs/` that still describes the `DesignLibrary` UI flow will become stale at Phase 2 close. Mitigation: Phase 2 includes a `rg -n "DesignLibrary" docs` sweep with text updates.
