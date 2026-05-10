# Review Scope: Full review batch 6/6: PROJ-337 + PROJ-338 + PROJ-339 + PROJ-340 (UI subsystem + UI panels + UI services)

**Type:** tests (delegated by Claude Code)
**Request ID:** req_20260504_231829_dfce54
**Scope:** PROJ-337, PROJ-338, PROJ-339, PROJ-340 — characterization tests for the UI surface (21 test files, ~277+ tests)
**Instructions:** Fresh-eyes review, CRITICAL/MAJOR issues only. 10 specific check items (see request file).
**Context:** 6 of 6 OpenCode batches. Codex + Claude subagents reviewing in parallel.
**Review mode:** Fresh-eyes (no prior `Reviews/results/` consulted). Normal depth.

## Scope Details

### PROJ-337 (UI research subsystem — 3 test files, 60 tests)
- `tests/unit/research/research_scene/test_event_routing_and_draw.py` (12)
- `tests/unit/research/test_research_renderer_drawing.py` (22)
- `tests/unit/research/research_controls/test_event_routing_and_updates.py` (26)
- Production: `game/ui/research/{research_scene.py, research_renderer.py, research_controls.py}`

### PROJ-338 (UI panels high-risk — 6 test files, 143 tests + 4 review-4 fixes)
- `tests/unit/ui/panels/test_build_queue_drag_handler.py` (NEW, 31; +1 review-4)
- `tests/unit/ui/panels/test_build_queue_controller.py` (extended, +19)
- `tests/unit/ui/panels/test_system_tree_panel_characterization.py` (NEW, 30)
- `tests/unit/ui/panels/test_system_tree_panel_hazard.py` (extended, +5)
- `tests/unit/ui/panels/test_planet_report_panel_characterization.py` (NEW, 23; +3 review-4)
- `tests/unit/ui/test_battle_panels_characterization.py` (NEW, 26)
- Production: `game/ui/panels/{build_queue_drag_handler.py, build_queue_controller.py, system_tree_panel.py, planet_report_panel.py, battle_panels.py}`

### PROJ-339 (UI panels mid-risk — 6 test files, 29 tests + 7 review-4)
- `tests/unit/ui/panels/test_empire_treasury_panel.py` (extended, +2 + 2 vacuous fixes)
- `tests/unit/ui/test_race_environment_panel.py` (extended, +3 + 2 vacuous fixes)
- `tests/unit/ui/panels/test_race_identity_panel.py` (extended, +3 + 1 vacuous fix)
- `tests/unit/ui/test_modifier_impact_grid.py` (extended, +7 + 4 vacuous fixes + 3 missing-coverage)
- `tests/unit/ui/test_race_summary_panel.py` (extended, +4 + 1 vacuous fix)
- `tests/unit/ui/panels/test_design_stats_panel.py` (extended, +10 + 3 missing-coverage)
- Production: `game/ui/panels/{race_summary_panel.py, design_stats_panel.py, modifier_impact_grid.py, race_identity_panel.py, race_environment_panel.py, empire_treasury_panel.py}`

### PROJ-340 (UI services + utility — 6 test files, 45 tests)
- `tests/unit/ui/services/test_battle_ui_service.py` (NEW, 8)
- `tests/unit/ui/assets/test_ship_theme_manager.py` (NEW, 12)
- `tests/unit/ui/widgets/test_scrollable_json_panel.py` (NEW, 10 + 10 review-3a)
- `tests/unit/ui/effects/test_hit_effects.py` (NEW, 9)
- `tests/unit/ui/panels/test_base_gallery.py` (NEW, 3 + 8 review-3a)
- `tests/unit/ui/panels/test_builder_widgets.py` (NEW, 3 + 6 review-3a)
- Production: `game/ui/services/battle_ui_service.py`, `game/ui/assets/ship_theme_manager.py`, `game/ui/widgets/scrollable_json_panel.py`, `game/ui/effects/hit_effects.py`, `game/ui/panels/{base_gallery.py, builder_widgets.py}`
