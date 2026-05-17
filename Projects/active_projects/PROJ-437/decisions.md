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

## Open decisions (to resolve at phase start)

These are not user-blocking. They're decisions PROJ-437 will make at phase start with current evidence.

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
