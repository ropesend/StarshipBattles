# PROJ-437: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-17 | Project initialized as sibling subproject of PROJ-436 | Per user "data-model first, UI second" preference. PROJ-436 owns the unified `Container` substrate; PROJ-437 rebuilds the transfer UI on top once the API is stable. Both projects converged via [discussion arc01](../../../AgentCoordination/Scratchpad/Discussion/20260517T230029Z_post-435-project-creation/). |
| 2026-05-17 | **UI is its own project, not absorbed into PROJ-436** | Two reasons. (1) PROJ-436 is already large (12 phases including consult); folding UI in would balloon it and break the substrate-then-sweep checkpointing model. (2) The current transfer UI works adequately against the legacy storage patchwork; rewriting it after the substrate is settled lets us design against the final API shape, not a moving target. |
| 2026-05-17 | **Preserve existing slider/arrow/Max UX shape** | Per user: "we already have a transfer UI that works OK, it is somewhat similar to a slider system." This project re-plumbs the UI to the unified `Container` API but does not redesign the input affordances. `MAX_LOAD` / `MAX_DROP` sentinels preserved; arrow-after-Max behavior preserved. |
| 2026-05-17 | **Phase 0 may start during PROJ-436 Phase 6-8** | Phase 0 is read-the-API + survey-the-current-UI work that produces a findings document. It does not edit production code and does not depend on the final cutover of PROJ-436 Phase 7. Phase 1+ are gated to PROJ-436 Phase 7 completion. This lets the two projects overlap modestly without breaking the checkpoint rule. |
| 2026-05-17 | **No worktrees** | Per user `feedback_no_worktrees.md`. Serial execution in main checkout. |
| 2026-05-17 | **End-of-project Codex consult is Phase 5; verified findings become added phases** | Per user `feedback_consult_at_project_end.md`. Same workflow as PROJ-436 Phase 11. |
| 2026-05-17 | **Mixed-content row model with per-kind specialization** | Resources display as float amounts with per-resource icons; items display as discrete counts with design-name labels and damage indicators; population displays as per-species integer counts. All three render through one unified row contract but with kind-specific formatting hooks. Rejected alternative: separate panels per kind — would proliferate UI surface and contradict the "one transfer screen" goal. |
| 2026-05-17 | **Drop-pod-name handling folds into items-row presentation** | Currently `transfer_view_model.all_pod_names` is a special-cased always-show list for known drop-pod designs. After unification, drop pods are just `ItemContainable` instances; their presentation rule (show even at 0/0) becomes a per-item display flag on the design, not a special view-model field. |
| 2026-05-18 | **OD1 resolved → (a) every container per entity** | Phase 0 audit ([findings/transfer_ui_migration_map.md §5](findings/transfer_ui_migration_map.md#5-open-decisions-od1od2od3--phase-0-resolution)) confirmed the default. The existing `collect_sources_and_targets` already enumerates per-entity; option (a) is the natural extension. Noise concern mitigated by the existing filter-empty toggle. |
| 2026-05-18 | **OD2 resolved → (a) cross-kind transfer in one operation** | Phase 0 confirmed default — preserves existing UX where `pending_transfers` already mixes resources + items + passengers in one confirm pass. |
| 2026-05-18 | **OD3 resolved → (a) per-input mass-remaining preview** | `Container.add()` is O(1) over hash + small slice-map sum; per-arrow-click recompute is well within frame budget for the realistic row counts (≤ 50). Profile only on capacity bump. |
| 2026-05-18 | **Manifest correction: `fleet_data_source.py` is NOT a Phase 1 target** | Phase 0 audit ([findings/transfer_ui_migration_map.md §3.6](findings/transfer_ui_migration_map.md#36-gameuiscreensfleet_data_sourcepy--manifest-entry-is-wrong)) discovered this file is the fleet-report `VirtualTable` data source, unrelated to the transfer dialog. The actual source/target enumeration lives in `transfer_controller.py::collect_sources_and_targets`. The Phase 1 target list will be `transfer_view_model.py` + `transfer_controller.py` + a new DTO/facade `get_containers(id)` accessor (introduced as substrate in Phase 1a). Manifest update deferred to Phase 1 start. |
| 2026-05-18 | **Phase 1 split recommendation: 1a substrate / 1b cutover** | Per the PROJ-431 sub-phase model. Phase 1a introduces `ContainerRef` + `ContainerSnapshotInfo` types and a parallel `facade.fleets.get_containers(id)` / `planets.get_containers(id)` accessor as additive projections; Phase 1b cuts the view model and controller over. Collapse to single commit if Phase 1a turns out to be a ≤30-line patch with no breaking surface. |
| 2026-05-18 | **Pre-existing pytest.ini `norecursedirs` issue is fixed (out of scope note)** | PROJ-443 Phase 4 (commit `e12603992`) flipped `pytest.ini norecursedirs` so 1953 previously hidden tests under `tests/unit/strategy/data/` are now visible. The PROJ-437 prompt's "NOT YOURS TO FIX" caveat about `data` token in `norecursedirs` is moot — the issue has been resolved upstream. PROJ-437 baseline sharded count will reflect the new visible-tests total. |
| 2026-05-18 | **Tangential audit findings flagged (NOT taken in this project)** | `fleet_dto.py:217-226` and `builder/stat_rows_dynamic.py:179,252` still hardcode the eight resource IDs / display names. PROJ-437's UI rework routes around these (Container snapshots are the new SoT) but the leaks should not survive a final grep. Documented in [findings/transfer_ui_migration_map.md §4](findings/transfer_ui_migration_map.md#4-tangential-finding-out-of-scope-for-proj-437-flagging-for-visibility) for a future TD ticket or PROJ-436 Phase 7 cleanup pass. |

## Open decisions (to resolve at phase start)

> **All three were resolved at Phase 0 start (2026-05-18) with their
> documented defaults.** See the 2026-05-18 rows above. The original
> option statements are retained below for traceability.

### OD1: Source/destination enumeration scope (Phase 1)

What counts as a "source" or "destination" container in the dropdown?

Options:
- **(a) Every container on the entity.** A ship with 5 cargo holds shows 5 source options. Most flexible, potentially noisy.
- **(b) One aggregated container per entity.** The ship appears once; UI shows aggregate contents across all its containers. Cleaner, loses some control.
- **(c) Grouped by content kind.** A ship appears as "Ship X — Resources," "Ship X — Items," "Ship X — Population." Mid-ground.

**Default for Phase 1:** (a) most flexible, document if (b) or (c) emerges as cleaner during implementation.

### OD2: Cross-kind transfer in one operation

Can a single staged transfer move resources AND items AND population from one container to another in one confirm?

Options:
- **(a) Yes, all three at once.** Matches existing slider-per-row UX.
- **(b) No, one kind at a time.** Forces clarity, may annoy users.

**Default for Phase 3:** (a) — preserves existing UX. If validation rejection messaging gets confusing across kinds, revisit.

### OD3: Mass-remaining preview granularity (Phase 2)

How often does the preview recompute as the user adjusts sliders?

Options:
- **(a) Per-input (every arrow click).** Most responsive, may be expensive on large containers.
- **(b) On debounce / on confirm.** Cheaper, slightly delayed.

**Default for Phase 2:** (a) — `Container.add()` validation should be cheap. Profile if it isn't.

## Flagged for product-review

None at this time. Open decisions OD1-3 are implementer choices, not user-input dependencies.
