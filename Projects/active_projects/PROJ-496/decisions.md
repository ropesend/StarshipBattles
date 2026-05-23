# PROJ-496: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-23 | Project initialized | Starting point for Test polish risky + non-UI integration (PROJ-480 follow-through) |
| 2026-05-23 | Split PROJ-480 backlog by path locality, not by CAT-number | Codex consult 2026-05-23 (`AgentCoordination/Scratchpad/Consult/20260523T125719Z_plan-PROJ-480-followthrough/response.md`) — see PROJ-494/decisions.md for full rationale. |
| 2026-05-23 | Phase 1 = risky unit files; Phase 2 = non-UI integration | Two distinct risk profiles. Phase 1 needs assertion-semantics judgment per task; Phase 2 needs deterministic-setup design per test. Sequencing Phase 1 first because the risky files are more likely to surface conftest helper needs we should know before integration rewrites. |
| 2026-05-23 | Inherit T5.14 re-pending from PROJ-480 Phase 6 | PROJ-480 `findings/audit_verification.md` F1: Codex audit confirmed `test_turn_engine_lazy_properties.py:219-251` (inspect.getsource guard) and `:262-288` (AST-parsing guard) both still present. PROJ-479 Task 3.21 (the proposed subsume) is itself NEEDS_REWORK and was never done. |
| 2026-05-23 | Pair T3.29 with T5.14 on the same file | Both target `test_turn_engine_lazy_properties.py`; Codex flagged this as a collision pair. Execute T3.29 (parametrize 18 isinstance) first; then T5.14 (guard split into `tests/static_guards/` per the original PROJ-479 intent). |
| 2026-05-23 | Path retargets locked in manifest at scaffold time | Affected: test_persistence_adapter.py (→ `tests/unit/strategy/engine/session/`), test_bug_regressions_2026_01.py (→ `tests/unit/regressions/`). |
| 2026-05-23 | Phase 0 = retarget/prune (no TDD) | Codex recommended a Phase 0 inside each new project. Adopted. |
| 2026-05-23 | Sequence PROJ-496 AFTER PROJ-494 and PROJ-495 | Failure cost is highest here; let mechanical projects land first to free up overlapping conftest helpers (e.g. ship mock factories from PROJ-494 T2.10 / PROJ-495 T1.1 may be reusable in T5.4 battle_engine_tick if it needs ship instances). |
