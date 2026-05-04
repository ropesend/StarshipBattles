# PROJ-339: Manifest

> Files this project owns / creates / modifies. Future agents check this to
> avoid scope overlap with sibling projects in the test_coverage master arc.

## Project metadata

- **ID:** PROJ-339
- **Title:** UI panels mid-risk characterization
- **Master arc:** `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md`
- **Predecessors:** PROJ-329A/B/C, PROJ-330, PROJ-331..338
- **Successors:** TBD per master arc
- **Risk tier:** Mid (existing coverage baseline, well-understood pygame_gui mocks)

## Production files (READ-ONLY for this project)

This project performs **zero** production-code changes. The following files are
read for behavior characterization only:

| File | LOC | Notes |
|------|-----|-------|
| `game/ui/panels/race_summary_panel.py` | 733 | RaceConfig + asset loader + ship preview |
| `game/ui/panels/design_stats_panel.py` | 516 | Biggest test gap; only `StatRow` covered today |
| `game/ui/panels/modifier_impact_grid.py` | 514 | Component modifier visualization |
| `game/ui/panels/race_identity_panel.py` | 493 | Race / faction / government dropdowns |
| `game/ui/panels/race_environment_panel.py` | 337 | 17 preference rows + repro/happiness sliders |
| `game/ui/panels/empire_treasury_panel.py` | 333 | EmpireEconomySnapshot rendering |

## Test files (CREATE / MODIFY)

All work is appending NEW test functions to existing files. No new test
modules are created.

| File | Existing tests | New tests | Final |
|------|---------------:|----------:|------:|
| `tests/unit/ui/test_race_summary_panel.py` | ~14 | 4-6 | ~18-20 |
| `tests/unit/ui/panels/test_design_stats_panel.py` | 6 (StatRow only) | 8-10 | 14-16 |
| `tests/unit/ui/test_modifier_impact_grid.py` | 9 | 4-6 | 13-15 |
| `tests/unit/ui/panels/test_race_identity_panel.py` | ~17 | 2-3 | ~19-20 |
| `tests/unit/ui/test_race_environment_panel.py` | ~18 | 2-3 | ~20-21 |
| `tests/unit/ui/panels/test_empire_treasury_panel.py` | ~19 | 2 | ~21 |
| **Totals** | **~93** | **~22-30** | **~115-123** |

## Documentation files (CREATE)

Project-local artefacts under `Projects/active_projects/PROJ-339/`:

- `plan.md` — overview, scope, success criteria, verification.
- `decisions.md` — D-001..D-008 captured this session.
- `manifest.md` — this file.
- `design.md` — architecture context (panel hosts, data binding) + testability blockers.
- `phase_1_checklist.md` — per-file behavior checklists with concrete test names.

No `docs/` updates planned. The master arc's `test_coverage_master_plan_v1.md`
is updated externally as projects close.

## Cross-project overlap check

| File | Other projects touching it | Resolution |
|------|----------------------------|------------|
| All 6 panel files | None in active sequence | This project owns the test coverage of these panels for the master arc. |
| Existing test files | None | Append-only; no rename / move / delete. |

No file overlap with PROJ-329A/B/C, PROJ-330, or PROJ-331..338.

## Findings (CREATE if needed)

- `findings/` directory will be created lazily if any bug is surfaced during
  characterization. Bug reports go to GitHub Issues per current convention
  (`/claude-gi-*` skills); the local `findings/` file would only capture
  reproduction notes too detailed for an issue body.
