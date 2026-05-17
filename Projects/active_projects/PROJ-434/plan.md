# PROJ-434: Complete DesignLibrary deletion (PROJ-427 phase 6 follow-up)

**Execution Protocol:** 03c-phase-aware-execution

> **WORKING ON THIS PROJECT:**
> - Read [PROJ-427's `plan.md`](../PROJ-427/plan.md) and its [`decisions.md`](../PROJ-427/decisions.md) (2026-05-17 entries) for the spinoff rationale and the state of `DesignRepository` / `DesignCatalog`.
> - Read [`design.md`](design.md) for the collaborator chain and the API gaps that gate Phase 1.
> - Open the phase checklist for your current phase.
> - Check off tasks as you complete them.
> - Update Current State before stopping work.

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-434 [phase]` before stopping.
> - Update Current State with specific handoff context.

## Quick Status

| Phase | Status | Checklist | Depends on |
|-------|--------|-----------|------------|
| 0. Extend `DesignRepository` + `DesignCatalog` API to cover the remaining UI surface | Complete | [phase_0_checklist.md](phase_0_checklist.md) | — |
| 1. Migrate `BuildQueueScreen` + its 3 panel collaborators (controller / drag handler / portrait loader) | Complete | [phase_1_checklist.md](phase_1_checklist.md) | Phase 0 |
| 2. Migrate the remaining 3 UI screen entry points + ~25 test files + delete `design_library.py` (deletion gate) | Complete | [phase_2_checklist.md](phase_2_checklist.md) | Phase 1 |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** Complete
**Last Action:** All three phases shipped on `proj/PROJ-434/main`. Phase 0 added the API surface (`scan_designs`, `search_designs`, `filter_designs`, `load_design_data`, `get_design_path`, rich `save_design`, `mark_obsolete`, `invalidate`, `attach_repository`) on `DesignRepository`/`DesignCatalog` and wired `FacadeSessionState.get_designs_for_empire` through the catalog. Phase 1 renamed `design_library` → `design_catalog` across `BuildQueueScreen` + its 3 panel collaborators and their tests. Phase 2 migrated `workshop_ship_io.py`, `strategy_build_queue_manager.py`, and `design_selector_window.py` onto the catalog lookup, repointed all remaining test fixtures, and deleted `game/strategy/systems/design_library.py` along with the `DesignLoadResult` re-export shim. Sharded suite 21125/21125 green at Phase 2 close.
**Next Action:** None — project complete.
**Blockers:** None.

## Overview

PROJ-427 (TD-05) completed Phases 0-5 cleanly and partially completed Phase 6 — it introduced `DesignRepository` + `DesignCatalog`, migrated runtime production off disk, converted the replay store to instance ownership, performed the `DesignLoadResult` dependency inversion, and migrated the lightest UI caller (`transfer_controller.discover_pod_designs`). What remains is the mechanical-but-broad UI migration: 7 production files (`workshop_ship_io.py`, `strategy_build_queue_manager.py`, `design_selector_window.py`, plus `BuildQueueScreen` and its 3 panel collaborators `BuildQueueController` / `BuildQueueDragHandler` / `BuildQueuePortraitLoader`) and ~30 test files still construct `DesignLibrary(save_path, empire_id)` directly. The Phase 6 deletion gate (`rg -n "DesignLibrary"` returns no production / UI / test hits) intentionally fails until that work lands.

The gating prerequisite is API parity: `DesignCatalog` and `DesignRepository` between them must expose every method the old `DesignLibrary` surface offered to UI callers — currently missing are `scan_designs`, `search_designs`, `filter_designs`, `load_design_data`, `get_design_path`, and the rich `save_design(ship, name, built_designs)` flow (which welds metadata embedding, overwrite-protection against built designs, and per-turn UI cache invalidation). The QA-Obs-3 cache-invalidation contract (workshop save → catalog refresh visible to the same-empire viewer through `FacadeSessionState.designs_by_empire`) must also be wired through the catalog rather than through `DesignLibrary`'s side effects.

## Goals

- Complete the deletion of `game/strategy/systems/design_library.py` and remove the `DesignLoadResult` re-export shim.
- Pass the PROJ-427 Phase 6 deletion gate: `rg -n "DesignLibrary" game tests docs` returns zero live hits (only string mentions in historical decisions / changelogs, if any, remain).
- Leave the sharded suite (`python Tools/test_sharded/test_sharded.py`) green at every commit.
- Preserve the QA-Obs-3 cache contract: workshop save invalidates the per-turn UI cache so the same-empire viewer sees the new design on the next read.

## Scope

**In:**
- Additive API on `game/strategy/systems/design_catalog.py` and `game/strategy/systems/design_repository.py`: `scan_designs`, `search_designs`, `filter_designs`, `load_design_data`, `get_design_path`, rich `save_design(ship, name, built_designs)` (overwrite-protection + cache invalidation).
- Wire-through of the QA-Obs-3 cache contract via `game/strategy/facade/slices/_facade_state.py` so the catalog (not `DesignLibrary`) is the source of truth for `designs_by_empire`.
- UI migration of 7 production files: `game/ui/screens/workshop_ship_io.py`, `game/ui/screens/strategy_build_queue_manager.py`, `game/ui/screens/design_selector_window.py`, `game/ui/screens/build_queue_screen.py` and its 3 panel collaborators (`build_queue_controller.py`, `build_queue_drag_handler.py`, `build_queue_portrait_loader.py`).
- Test fixture migration in ~30 test files that currently monkeypatch `DesignLibrary` at module boundaries.
- Deletion of `game/strategy/systems/design_library.py` and removal of the `DesignLoadResult` re-export shim once the deletion gate passes.
- Docs touch-ups for any text under `docs/` that still describes the `DesignLibrary` UI flow.

**Out:**
- Any behavior change beyond moving call sites and matching the existing `DesignLibrary` API surface on the new classes. This is a mechanical migration, not a redesign.
- Save-format / save-schema changes (already forbidden by PROJ-427 guardrails; restated here).
- Touching the runtime production / construction-queue / quickstart-builder call chain — that migrated in PROJ-427 Phase 3 and is out of scope here.
- Replay-store / `SaveGameService` work — that migrated in PROJ-427 Phase 5.
- Reworking `DesignCatalog`/`DesignRepository`'s internal shape (e.g. splitting `DesignRepository` into a folder-rooted root + per-empire view). PROJ-427's 2026-05-17 "session-level `DesignRepository` keyed at empire_id=0" decision stays.

## Dependencies

Hard predecessors: PROJ-427 Phases 0-5 (complete and committed on `proj/PROJ-427/main`). PROJ-427 Phase 6 partial work is also on that branch (dependency inversion + 1 UI migration); this project picks up where it stopped.

Soft predecessors: none. PROJ-428..PROJ-431 do not block and can proceed in parallel.

The project branch is `proj/PROJ-434/main`. Phase branches follow the standard `proj/PROJ-434/phase_<N>` namespace.

## Key Files

Full list in [`manifest.md`](manifest.md). Summary:

| Component | File Path | Action |
|-----------|-----------|--------|
| Design repository (existing) | `game/strategy/systems/design_repository.py` | Edit (Phase 0: add `scan_designs`, `load_design_data`, `get_design_path`, rich `save_design`) |
| Design catalog (existing) | `game/strategy/systems/design_catalog.py` | Edit (Phase 0: add `search_designs`, `filter_designs`, plus the QA-Obs-3 cache invalidation hook on save) |
| Facade session state | `game/strategy/facade/slices/_facade_state.py` | Edit (Phase 0: wire `designs_by_empire` through the catalog, not `DesignLibrary`) |
| Design library (legacy) | `game/strategy/systems/design_library.py` | Delete (Phase 2 deletion gate) |
| Workshop ship I/O | `game/ui/screens/workshop_ship_io.py` | Edit (Phase 2 — rich save flow) |
| Strategy build-queue manager | `game/ui/screens/strategy_build_queue_manager.py` | Edit (Phase 2 — 4 `DesignLibrary(...)` construction sites) |
| Design selector window | `game/ui/screens/design_selector_window.py` | Edit (Phase 2 — `search_designs` / `filter_designs` callers; `mark_obsolete`; `design_library`-typed constructor parameter) |
| Build queue screen | `game/ui/screens/build_queue_screen.py` | Edit (Phase 1 — UI entry point for the build-queue collaborator chain) |
| Build queue controller | `game/ui/screens/build_queue_controller.py` | Edit (Phase 1 — panel collaborator) |
| Build queue drag handler | `game/ui/screens/build_queue_drag_handler.py` | Edit (Phase 1 — panel collaborator) |
| Build queue portrait loader | `game/ui/screens/build_queue_portrait_loader.py` | Edit (Phase 1 — panel collaborator) |
| Test fixtures | ~30 files under `tests/` | Edit (Phase 1 + Phase 2 — repoint monkeypatches off `DesignLibrary` onto the catalog/repository) |

## Phases

### Phase 0: API extension on `DesignRepository` + `DesignCatalog`

Additive-only work on the two new collaborators introduced in PROJ-427. Add the missing methods that the deferred UI callers depend on: `DesignRepository.scan_designs(empire_id)`, `DesignRepository.load_design_data(design_id)`, `DesignRepository.get_design_path(design_id)`, the rich `DesignRepository.save_design(ship, name, built_designs)` that welds metadata embedding + overwrite-protection + on-disk write, and `DesignCatalog.search_designs(query)` / `DesignCatalog.filter_designs(predicate)`. Wire the QA-Obs-3 cache parity through `FacadeSessionState.designs_by_empire` so that on workshop save the catalog invalidates the per-turn cache and the same-empire viewer sees the new design on next read — matching the contract `DesignLibrary` enforced through its side effects. No caller migration in this phase; the existing `DesignLibrary` UI flow stays live alongside the new methods so the tree remains green.

### Phase 1: Migrate `BuildQueueScreen` + 3 panel collaborators

Tackle the tightly-coupled `BuildQueueScreen` family first as a proof of the migration pattern. `BuildQueueScreen` and its three siblings (`BuildQueueController` for state mutation, `BuildQueueDragHandler` for drag-and-drop, `BuildQueuePortraitLoader` for thumbnail caching) all reach into `DesignLibrary` independently and must migrate together — leaving any one on `DesignLibrary` would re-couple the others through shared state. Repoint each one's `DesignLibrary(save_path, empire_id)` construction site onto `session.services.design_catalogs_by_empire[empire_id]` (read path) or the session's repository handle (write path). Update each file's test fixtures in the same commit.

### Phase 2: Migrate remaining UI screens + delete `design_library.py`

Migrate the three remaining UI screen entry points: `workshop_ship_io.py` (rich `save_design(ship, name, built_designs)` flow with overwrite-protection and per-turn cache invalidation — the QA-Obs-3-hardened code path), `strategy_build_queue_manager.py` (4 `DesignLibrary(...)` construction sites threaded through build-queue subsystems), and `design_selector_window.py` (`design_library`-typed constructor parameter; `search_designs`, `filter_designs`, `mark_obsolete` callers). Update the remaining ~25 test files. Once `rg -n "DesignLibrary" game tests` shows zero hits outside `design_library.py` itself, delete `game/strategy/systems/design_library.py` and remove the `DesignLoadResult` re-export shim. Refresh docs that reference the old `DesignLibrary` flow.

## Related Documents

- Predecessor scaffold: [PROJ-427 plan](../PROJ-427/plan.md), [decisions](../PROJ-427/decisions.md) (esp. 2026-05-17 spinoff entries), [Phase 6 checklist](../PROJ-427/phase_6_checklist.md).
- TD-05 source plan: [`TD-05_production_persistence_split.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-05_production_persistence_split.md).
- This project's design notes: [`design.md`](design.md).
- Decisions log: [`decisions.md`](decisions.md).
- Per-phase file manifest: [`manifest.md`](manifest.md).
- Findings ledger: [`findings_ledger.md`](findings_ledger.md).

## Verification

- [ ] `DesignRepository` and `DesignCatalog` between them expose every method `DesignLibrary` exposed to UI callers (`scan_designs`, `search_designs`, `filter_designs`, `load_design_data`, `get_design_path`, rich `save_design`).
- [ ] `FacadeSessionState.designs_by_empire` is served by `DesignCatalog`, not by a `DesignLibrary` instance.
- [ ] QA-Obs-3 parity: workshop save invalidates the per-turn cache; same-empire viewer sees the new design on next read; covered by a focused regression test.
- [ ] `rg -n "DesignLibrary" game tests` returns zero live hits (deletion gate).
- [ ] `game/strategy/systems/design_library.py` is deleted; the `DesignLoadResult` re-export shim is removed.
- [ ] Focused UI suites green for every migrated screen.
- [ ] `python Tools/test_sharded/test_sharded.py` is green at every phase close.
- [ ] All phase checklists complete; findings ledger has no `open` or `addressed_pending_review` entries at audit time.
