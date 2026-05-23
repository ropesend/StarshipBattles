# PROJ-427: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to [`decisions.md`](decisions.md).

The authoritative specification is the source plan [`TD-05_production_persistence_split.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-05_production_persistence_split.md). This document distills the architectural intent.

---

## Verified problem

Two distinct couplings sit on top of the same `DesignLibrary` class:

1. **Runtime production reads mutable save-folder JSON mid-turn.** `ProductionSpawner` imports `DesignLibrary` directly and instantiates `DesignLibrary(save_path, empire.id)` per spawn path. `ProductionEngine` threads `save_path` through tick processing solely to support those disk reads. `AddToConstructionQueueCommandHandler` and `quickstart_builder.spawn_initial_complexes(...)` do the same. Every spawn or validation re-reads design JSON from the save folder.
2. **Replay-store lifecycle is owned by a process-wide global.** `save_game_service.py` defines `_replay_store` as a module-level variable, exposed via `set_replay_store()` / `get_replay_store()`. The lifecycle is implicit, untestable in isolation, and silently shared across any future multi-session work.

A third coupling sits between them: `FacadeSessionState.designs_by_empire` caches per-turn UI design views on the same `DesignLibrary` instance that also does the disk I/O, so UI cache invalidation and disk-policy decisions are entangled.

## Architectural split

`DesignLibrary` is two responsibilities welded together. PROJ-427 separates them.

### `DesignRepository` (filesystem + JSON persistence)

Owns:
- Folder location and creation.
- `scan_designs()`, `save_design(...)`, `load_design_data(...)`, `mark_design_obsolete(...)`, `increment_built_count(...)`.
- The current `DesignLoadResult` shape (preserved unchanged — no caller-visible result type change in Phase 1).
- Save-folder and temp-folder policy.

Does NOT own:
- In-memory runtime lookup.
- Per-turn UI cache state.
- Convenience filtering for UI panels.

The repository is the **only** type allowed to touch disk for designs. It is constructed once at session/bootstrap boundaries and is reachable from `SaveGameService` (for built-count flush at save time) and from the catalog populate/repopulate path. It is not reachable from production spawn paths or construction-queue validation.

### `DesignCatalog` (in-memory runtime lookup + UI cache + pending increments)

Owns, per empire:
- `lookup(design_id)` — pure in-memory dict access.
- Per-turn filtered / listed views for UI.
- Pending built-count increments (a dict from design_id to delta, flushed at save time).
- An explicit `refresh()` / `repopulate_from(repository)` entry point.

Does NOT own:
- Any filesystem call.
- Any JSON parsing.

The catalog is populated from `DesignRepository` at session bootstrap and after explicit refresh events (new design saved by the workshop, etc.). It is **never** repopulated during a production tick. Phase 3 adds an integration test that asserts this — see Phase 3 / Phase 6 verification gates in [`plan.md`](plan.md).

### Per-empire catalog model

`GameSession` exposes a per-empire accessor — `get_design_catalog(empire_id)` or `design_catalogs_by_empire[empire_id]`. The catalog instance per empire holds that empire's runtime design lookup and that empire's per-turn UI cache. The runtime production tick and the UI both call into the same catalog; this is what unifies `FacadeSessionState.designs_by_empire` with production-side design lookup and lets PROJ-427 remove `save_path` from the spawn call chain entirely.

If PROJ-423 (TD-02 GameSession lifecycle) has not landed when this project starts, the accessor lives directly on `GameSession`. If PROJ-423 lands later, the accessor moves into `SessionRuntimeServices` (or, for the per-empire catalog map, into `SessionBootstrapState` because the catalogs are per-empire runtime state). See [`TD-02_game_session_lifecycle.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-02_game_session_lifecycle.md) section "Cross-plan coupling with TD-05" for the absorption migration.

## Replay-store conversion: module-global → instance-owned

`SaveGameService` today:

```python
# module level
_replay_store: ReplayStore | None = None

def set_replay_store(store): ...
def get_replay_store(): ...
```

PROJ-427 converts this to instance-owned wiring:

```python
class SaveGameService:
    def __init__(self, *, replay_store: ReplayStore | None = None, ...):
        self._replay_store = replay_store
    # save/load/delete operations notify self._replay_store
```

Bootstrap (`game/app_bootstrap.py`) constructs a `SaveGameService` instance with the replay store passed in by constructor injection. There is no longer a process-wide setter or getter; tests construct `SaveGameService(replay_store=spy)` directly. The conversion lands in a single contained phase (Phase 5) — no half-static / half-instance period.

Grep gate before Phase 5 completes:

```bash
rg -n "_replay_store|set_replay_store|get_replay_store|SaveGameService\." game tests
```

Must show no static / module-global usage in `game/`.

## Built-count write-back: deferred, not mid-tick

`DesignRepository.increment_built_count(...)` exists, but the production tick does not call it. Instead, `DesignCatalog` tracks pending increments in memory; `SaveGameService` at save time flushes those increments through `DesignRepository`.

Why deferred:
- Removes per-spawn disk writes.
- Avoids a save-schema change. Per the source plan's "Weak-LLM Guardrails": **do not change save schema in the same phase that removes production disk I/O.** Built counts therefore stay on the repository file, not on `Empire`. No `Empire.designs_built_count` field is added in PROJ-427.
- Keeps the plan focused on the runtime / persistence separation.

A save-format bump (a hypothetical v4.0.0 that absorbed built counts into `Empire`) would be a separately-approved, single-phase change outside this project. PROJ-427 does not bump the save format.

## Why `DesignLibrary` survives until the deletion gate

The source plan's guardrails require keeping `DesignLibrary` available as a compatibility shim until `rg -n "DesignLibrary"` shows no remaining production or UI callers. Premature deletion in Phase 1 or Phase 2 would break live UI callers (`workshop_ship_io.py`, `strategy_build_queue_manager.py`, `transfer_controller.py`, etc.). Phase 6 is the only phase that may delete or alias `DesignLibrary`, and only after the grep gate passes.

## Test surface (verification anchors)

The minimum special-case coverage required by the source plan:

1. **No design-disk read during a production tick.** New integration test in `tests/integration/strategy/production/` that runs a production tick with a `DesignRepository` whose `load_design_data` / `scan_designs` raise if called.
2. **Built-count increments are not written mid-tick.** Phase 4 test asserts the disk repository is untouched during tick processing and is flushed only at save time.
3. **Replay store switches save roots correctly on save / load / delete.** Phase 5 test constructs `SaveGameService(replay_store=spy)` and asserts spy notifications.
4. **UI sees newly saved designs through the new catalog path.** Phase 2 / Phase 6 test exercises the workshop save → catalog refresh → UI panel flow without going through `DesignLibrary`.

## Design Decisions

See [`decisions.md`](decisions.md) for the full log with rationale.
