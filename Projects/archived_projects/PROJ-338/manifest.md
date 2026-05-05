# PROJ-338 — File Manifest

| File | Type | Notes |
|---|---|---|
| `tests/unit/ui/panels/test_build_queue_drag_handler.py` | Test (NEW) | Characterization test file for `BuildQueueDragHandler`. State-machine transitions + multi-select gating + callback vs legacy-pop + drag preview. ~28 tests. |
| `tests/unit/ui/panels/test_build_queue_controller.py` | Test (EXTEND) | Add `TestCharacterizationCoverageGaps` class: category/role filtering, `_validate_designs` paths, build-turns formula corners, `refresh_design_report` happy/error paths. ~15 tests appended. |
| `tests/unit/ui/panels/test_system_tree_panel_characterization.py` | Test (NEW) | `set_items` grouping branches, expansion state persistence across rebuilds, click→toggle vs click→select, recursive expand-children behavior, `set_dimensions`/layout. ~22 tests. |
| `tests/unit/ui/panels/test_system_tree_panel_hazard.py` | Test (EXTEND) | Add corner-case rows: multiple star providers, ThrustModifier =1 (no hint), missing ability_data keys, non-star providers ignored. ~5 tests appended. |
| `tests/unit/ui/panels/test_planet_report_panel_characterization.py` | Test (NEW) | Panel-object behavior — construction with/without `show_complexes`, `update_planet` view/empire/race_registry rebind asymmetry (PROJ-292 m1), `kill`, complexes-list rendering, resource icon fallback path. ~20 tests. |
| `tests/unit/ui/test_battle_panels_characterization.py` | Test (NEW) | New file using existing mocked-pygame pattern. Banner-rect recording, scroll-offset click translation, `_get_ships()` fallback semantics, derelict/dead branches, ID-based expansion (`_is_id_expanded`/`_toggle_id_expanded`), `BattleControlPanel` win/draw text branches. ~22 tests. |
| `Projects/active_projects/PROJ-338/plan.md` | Docs (NEW) | Plan file. |
| `Projects/active_projects/PROJ-338/decisions.md` | Docs (NEW) | Decision log. |
| `Projects/active_projects/PROJ-338/manifest.md` | Docs (NEW) | This file. |
| `Projects/active_projects/PROJ-338/design.md` | Docs (NEW) | Architecture context per panel. |
| `Projects/active_projects/PROJ-338/phase_1_checklist.md` | Docs (NEW) | Per-file checklist. |

## Production files referenced (read-only)

| File | LOC | Top-level classes / helpers |
|---|---:|---|
| `game/ui/panels/build_queue_drag_handler.py` | 350 | `BuildQueueDragHandler` |
| `game/ui/panels/build_queue_controller.py` | 652 | `BuildQueueController` |
| `game/ui/panels/system_tree_panel.py` | 719 | `SystemTreeItem`, `SystemTreePanel`, `_legacy_provider_label`, `_format_star_hazard_hints` |
| `game/ui/panels/planet_report_panel.py` | 673 | `PlanetReportPanel`, `_projection_grid_rows`, `_qty_cell`, `_qual_cell`, `_flow_cell`, `_stockpile_cell`, `_net_cell_color` |
| `game/ui/panels/battle_panels.py` | 563 | `BattlePanel`, `ExpandableIdPanel`, `ShipStatsPanel`, `SeekerMonitorPanel`, `BattleControlPanel` |

## Existing tests audited (may be touched only by EXTEND rows above)

| File | LOC | Notes |
|---|---:|---|
| `tests/unit/ui/panels/test_build_queue_controller.py` | 1108 | Substantial PROJ-69/79/208 callback coverage. Gap: category/role helpers + design-report path + edge cases. |
| `tests/integration/ui/test_build_queue_drag_drop.py` | 361 | E2E only — no unit coverage of the handler in isolation. |
| `tests/integration/ui/test_system_tree_panel_smoke.py` | 267 | Construction + 3 classification path tests (audit S1.3). Untouched. |
| `tests/unit/ui/panels/test_system_tree_panel_hazard.py` | 109 | Hazard formatter happy paths. Will be EXTENDED. |
| `tests/unit/ui/panels/test_planet_report_panel.py` | 981 | Heavy on pure helpers; gap is panel-object behavior. Untouched (new sibling file added). |
| `tests/unit/ui/test_battle_panels.py` + `_extended.py` | ~975 | Mocked-pygame substitution pattern. Untouched (new sibling file added). |

## Per-file behavior counts

| File | Tests planned |
|---|---:|
| `test_build_queue_drag_handler.py` (NEW) | ~28 |
| `test_build_queue_controller.py` (EXTEND) | ~15 |
| `test_system_tree_panel_characterization.py` (NEW) | ~22 |
| `test_system_tree_panel_hazard.py` (EXTEND) | ~5 |
| `test_planet_report_panel_characterization.py` (NEW) | ~20 |
| `test_battle_panels_characterization.py` (NEW) | ~22 |
| **Total** | **~112** |
