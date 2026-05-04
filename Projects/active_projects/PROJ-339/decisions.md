# PROJ-339: Decisions Log

> Add decisions as they're made. Future agents reference this for "why".

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Mid-risk panel batch from `test_coverage_master_plan_v1.md`. Sequenced after PROJ-338. Planning artefacts produced this session; execution deferred. |
| 2026-05-04 | **D-001:** Characterization-only (no TDD) | Per master-arc philosophy: pin existing observable behavior of code that already ships. TDD would imply behavior changes; this project explicitly forbids them. |
| 2026-05-04 | **D-002:** No production refactors; surface bugs as separate tickets | If a characterization test exposes a bug, file a ticket and pin the buggy behavior in the test (with a `# TODO bug:PROJ-XXX` comment). Mixing fixes into characterization defeats the safety net. |
| 2026-05-04 | **D-003:** `StatRow` already tested — `DesignStatsPanel` direct tests are the gap | The 6 existing tests in `tests/unit/ui/panels/test_design_stats_panel.py` only exercise the inner `StatRow` helper. The 8-10 new tests target `DesignStatsPanel` itself: construction, `_build_layout`, `needs_rebuild`, `update_stats`, requirements rendering, collapse. |
| 2026-05-04 | **D-004:** `modifier_impact_grid.draw` stays uncovered; pin `update()` + formatters | Direct Surface output is impractical to pin without snapshot infrastructure that doesn't exist in this repo. The deterministic data preparation in `update()` and the pure formatter helpers (`_format_value`, `_format_sig_digits`, `_get_value_color`) cover the meaningful logic; `draw()` is glue. |
| 2026-05-04 | **D-005:** Reuse existing pygame_gui mock fixtures from `tests/unit/ui/panels/` | Don't invent new fixture infrastructure. The existing tests demonstrate the working pattern (real `UIManager`, mocked surfaces where needed). New tests should match shape verbatim. |
| 2026-05-04 | **D-006:** No new test files — append to the 6 existing files | New tests go into the same module as the existing coverage so locality is preserved and the sharded-suite run plan doesn't need updating. |
| 2026-05-04 | **D-007:** Single-phase project | The work is one cohesive characterization sweep across 6 sibling files. Multi-phase scaffolding (separate inventory / fixture / verification phases) would add ceremony for no benefit at this size. |
| 2026-05-04 | **D-008:** Top-3-per-file is the floor; gap-fillers are the budget | The 18 "top 3" behaviors per file from the source plan are guaranteed deliverables. The additional ~12 gap-fillers (4-6 each for the two big lifts; 2-3 each for the four light-touch files) are budgeted but may be re-prioritized if `_build_layout` proves harder than expected to fixture. |
