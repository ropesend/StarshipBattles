# PROJ-494: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-23 | Project initialized | Starting point for Test polish UI-family (PROJ-480 follow-through) |
| 2026-05-23 | Split PROJ-480 backlog by path locality, not by CAT-number | Codex consult 2026-05-23 (`AgentCoordination/Scratchpad/Consult/20260523T125719Z_plan-PROJ-480-followthrough/response.md`) flagged 6 same-file collisions under the category split: fleet_menu_items (1.3+3.14), design_selector_window (2.19+3.19), fleet_report_filters (2.16+3.30), empire_treasury_panel (2.20+3.45), build_queue_panel_factory (2.3+5.3), turn_engine_lazy_properties (3.29+5.14). Locality-first keeps each file's polish work owned by one project. |
| 2026-05-23 | Three projects: PROJ-494 (UI), PROJ-495 (core mechanical), PROJ-496 (risky + non-UI integration) | Matches the dominant clusters in the deferred backlog and gives each project a coherent risk profile. Worktree/merge friction minimized. |
| 2026-05-23 | Task 1.11 (test_strategy_input_handler_transfer.py, 230 LOC) lives inside PROJ-494 Phase 1, not its own project | Codex: "Keep it inside the UI-family project, but make it the first real execution phase after retarget/prune. It is a good first milestone, not a good standalone project." |
| 2026-05-23 | Phase 0 = retarget/prune (no TDD) | Codex recommended a Phase 0 inside each new project to fix stale `**File:**` and line refs before TDD. Adopted. |
| 2026-05-23 | Drop Task 1.3 (test_fleet_menu_items.py helper extraction) | Live file already has module-level `_make_fleet`, `_make_galaxy`, `_mapper` at lines 30-97; Codex spot-check 2026-05-23 + my own read confirmed. Task 3.14 on the same file is still real work (different cluster). |
| 2026-05-23 | Path retargets locked in manifest at scaffold time | Affected: test_race_setup_screen.py (→ screens/), test_build_queue_formatting.py (→ integration/ui/), test_battle_screen_simulation.py (→ tests/unit/ui/, no `screens/`), test_research_renderer.py (→ tests/unit/research/). |
| 2026-05-23 | Skip 1.15 and 1.17 — inherited from PROJ-480 | Plan.md:35-36 documents the deliberate skip rationale (one-liner conversion has no real LOC win; switching real pygame_gui.UIManager to MagicMock is risky). Not in scope. |
