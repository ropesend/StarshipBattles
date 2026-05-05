# PROJ-346 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| `tests/unit/ui/panels/test_empire_treasury_panel.py` | Test (rewrite lines 140, 145, 150) | PROJ-339 — 3 dictionary-tests-not-panel |
| `tests/unit/ui/panels/test_race_identity_panel.py` | Test (rewrite line 349) | PROJ-339 — hasattr tautology |
| `tests/unit/ui/panels/test_modifier_impact_grid.py` | Test (rewrite line 189) | PROJ-339 — pygame_gui-only kill |
| `tests/unit/ui/panels/test_race_summary_panel.py` | Test (rewrite lines 219, 236) | PROJ-339 — 2 `assert_called` no-content |
| `tests/unit/ui/panels/test_build_queue_drag_handler.py` | Test (rewrite lines 121, 126) | PROJ-338 — 2 drag_handler constructor tautologies |
| `tests/unit/ui/panels/test_planet_report_panel_characterization.py` | Test (rewrite line 403) | PROJ-338 — arithmetic-only resource-grid test |
| `tests/unit/ui/panels/test_system_tree_panel_hazard.py` | Test (rewrite line 23) | PROJ-338 — duplicate-body hazard test |
| `tests/unit/ui/assets/test_ship_theme_manager*.py` | Test (rewrite + add) | PROJ-340 — 3 untested paths + 3 zero-coverage public methods (~8 new tests total) |
| `tests/unit/strategy/save_load/test_*load_state*` | Test (rewrite) | PROJ-331 — UnboundedRegion tautology |
| `tests/unit/combat/test_hit_effects*.py` | Test (rewrite ≥3 "does not raise") | PROJ-331 — 3 "does not raise" tests + shield early-return guard that doesn't fire |
| `Projects/active_projects/PROJ-346/plan.md` | Project artifact | Updates per phase |
| `Projects/projects_index.md` | Project index | Status update at end of Phase 4 |

## Verification commands

| Phase | Command |
|-------|---------|
| 1 (PROJ-339) | `pytest tests/unit/ui/panels/test_empire_treasury_panel.py tests/unit/ui/panels/test_race_identity_panel.py tests/unit/ui/panels/test_modifier_impact_grid.py tests/unit/ui/panels/test_race_summary_panel.py -x` |
| 2 (PROJ-338) | `pytest tests/unit/ui/panels/test_build_queue_drag_handler.py tests/unit/ui/panels/test_planet_report_panel_characterization.py tests/unit/ui/panels/test_system_tree_panel_hazard.py -x` |
| 3 (PROJ-340) | `pytest tests/unit/ui/assets/ -x` |
| 4 (PROJ-331) | `pytest tests/unit/strategy/save_load/ tests/unit/combat/ -x` |
| Final | `pytest tests/unit/ -q` then `python Tools/lint_test_files.py` |
