# PROJ-495: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-23 | Project initialized | Starting point for Test polish core mechanical (PROJ-480 follow-through) |
| 2026-05-23 | Split PROJ-480 backlog by path locality, not by CAT-number | Codex consult 2026-05-23 (`AgentCoordination/Scratchpad/Consult/20260523T125719Z_plan-PROJ-480-followthrough/response.md`) — see PROJ-494/decisions.md for full rationale. |
| 2026-05-23 | Risky files routed OUT of PROJ-495 into PROJ-496 | The 6 files Codex flagged as high-risk (`test_turn_engine_lazy_properties.py`, `test_persistence_adapter.py`, `test_bug_regressions_2026_01.py`, `test_battle_engine_tick.py`, `test_generation.py` atmosphere, `test_colony_output.py`) plus `test_generator_crew_requirement_design.py` regression-defensive-branch live in PROJ-496 to keep PROJ-495 mechanical. |
| 2026-05-23 | Phase 0 = retarget/prune (no TDD) | Codex recommended a Phase 0 inside each new project to fix stale `**File:**` and line refs before TDD. Adopted. |
| 2026-05-23 | Path retargets locked in manifest at scaffold time | Affected: test_container.py (→ `tests/unit/strategy/data/`), test_tech_preset_loader.py (→ `tests/unit/simulation/systems/`), test_fleet_pursuer_tracker.py (→ `tests/unit/strategy/fleet/`). |
| 2026-05-23 | CAT-11 + CAT-12 combined into one Phase 4 | This project has only ~4 fragile + ~4 logic-heavy tasks total — too small to justify two separate phases. Same in PROJ-494. PROJ-496 also combines them. |
