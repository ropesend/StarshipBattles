# Phase 6: Protocol churn + build-queue/UI `context_type` cleanup

**Status:** Not Started
**Depends on:** phase_5
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_6.planned_files

**Objective:** Redesign the public protocol surface around `Container`. `IEmpire.resource_pool` and `IEmpire.max_storage` at `game/core/protocols/strategy_domain.py:64-72` become container-aware reads (or are removed if no consumer needs them post-Phase-5). `IStockpileHolder` / `IStagingYardHolder` at `game/strategy/data/galaxy_protocols.py:130-180` consolidate around `Container` — the two protocols may collapse into one `IContainerHolder`. Build-queue UI controller `context_type` reads at `game/ui/panels/build_queue_controller.py:483-513` move to typed Container queries.

---

## Tasks

To be authored at phase start. Expected sub-phase shape:
- 6a — design the consolidated protocol(s); document in `decisions.md`.
- 6b — implement new protocol(s) alongside old (both valid temporarily).
- 6c — migrate every implementer of the old protocols to satisfy the new one(s).
- 6d — migrate `build_queue_controller.py:483-513` to typed Container queries.
- 6e — migrate other UI consumers of the deprecated protocol methods.
- 6f — final cutover: delete old protocol methods; AST guard `test_no_legacy_protocol_names.py` pins absence.

---

## Phase Completion Checklist
- [ ] All sub-phases complete
- [ ] `tests/static_guards/test_no_legacy_protocol_names.py` green
- [ ] Build-queue integration tests green
- [ ] UI smoke tests green
- [ ] Full sharded suite green
- [ ] Update status to Complete; update plan.md + phase_state.json
