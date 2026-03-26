# PROJ-207: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-27 | Project created from review | Review identified 63 raw findings across 5 agents; 15 Critical/Major selected for remediation after validation |
| 2026-02-27 | Functional-area phasing (not severity) | Grouping by functional area (serialization, validation, execution, pipeline, hygiene) gives better workflow than mixing unrelated fixes in a "Critical" phase |
| 2026-02-27 | Phase 5 depends on Phases 3 | AU-002 (dispatch cleanup) and EP-004 (BUILD auto-pop) are easier after EP-001 (remove JOIN_FLEET branch) and 3.1 cleanup |
| 2026-02-27 | EP-002: Delete dead lifecycle methods (Option A) | Simpler than making them authoritative. If lifecycle hooks needed later, that's a separate project |
| 2026-02-27 | EP-001: Instant path is authoritative for JOIN_FLEET | JOIN_FLEET should fire immediately when co-located (instant semantics), not go through tick-based processing |
| 2026-02-27 | EP-005: pop_order() on movement failure (not clear_orders) | Players expect subsequent orders to survive a failed MOVE. Consistent with action failure behavior |
| 2026-02-28 | EP-005 REVISED: Differentiate stranded vs warp failures | Stranded (no fuel) keeps clear_orders() — fleet can't move at all, preserving orders just delays failure. Warp failures (no capability / insufficient resources) use pop_order() — fleet can still move normally. |
| 2026-02-28 | Task 2.4 added: Enemy colony cleanup in superweapon processors | process_implode_planet() and process_create_dyson_sphere() don't clean up victim empire colonies. Data corruption risk. Pass empires param matching process_stellerate_star() pattern. |
| 2026-02-28 | Task 5.3 scoped to 4 of 6 methods | process_self_destruct diverges significantly (ship ID list, multiple ship removal). process_stellerate_star partially fits. Template covers implode, open_warp, close_warp, dyson_sphere. |
| 2026-02-28 | Task 5.5: add_move_order_if_needed() needs start_hex param | Helper is not chain-aware (only checks fleet.location). Must add optional start_hex parameter before replacing ColonizeMissionCommandHandler inline logic. |
| 2026-02-28 | Registry accessor: session.turn_engine._registries.components | session.registries.components does not exist. Correct accessor matches ColonizeMissionCommandHandler pattern. |
| 2026-02-28 | Task 4.2 API: facade.handle_command() not session.dispatch_command() | GameSession has no dispatch_command(). UI layer uses StrategySessionFacade.handle_command(). |
| 2026-02-28 | Project review (Protocol 09) conducted | 13 unique findings across 5 agents: 3 scope gaps (HIGH), 3 design drift (HIGH), 2 stale refs (MED), 2 scope mismatches (MED), 2 unclear/ambiguous (MED), 1 policy tension (LOW). All approved and applied. |
| 2026-02-27 | ODM-003: Use _planet_ref format for Planet serialization | Consistent with Fleet serialization pattern. Resolution handled by the same resolve_order_references() pass |
| 2026-02-27 | Test baseline: 12,827 passed, 4 pre-existing failures (bug_13_colony_flags) | Pre-existing failures unrelated to fleet orders |
