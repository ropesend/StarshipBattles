# Test Quality Review: PROJ-337/338/339/340 (UI Subsystem + Panels + Services)

**Review type:** tests | **Request ID:** req_20260504_231829_dfce54
**Date:** 2026-05-04 | **Review mode:** Fresh-eyes (no prior `Reviews/results/` consulted)
**Scope:** 21 test files across 4 projects (~277+ characterization tests for the UI surface)
**Method:** 4 parallel subagents, one per project. Each read test + production files and verified per the 10 check items.
**Limitations:** Agents traced 2-3 tests per project for behavior accuracy (not all ~277). Test-name spot-check covered 7 of 21 files. Drag handler state machine verified exhaustively.

---

## Overall Verdict

| Project | Verdict | CRITICAL | MAJOR | Strengths |
|---------|---------|----------|-------|-----------|
| PROJ-337 | PASS WITH FINDINGS | 0 | 3 | Excellent importlib isolation, rich property assertions in renderer tests |
| PROJ-338 | CONDITIONAL PASS | 4 | 6 | Complete drag-handler state machine coverage (highest-risk area) |
| PROJ-339 | FAIL | 7 | 0 | D-009 fixture resolved correctly, characterization names well-described |
| PROJ-340 | FAIL | 3 | 3 | Scrollable JSON panel tests are exemplary (20 behavioral tests, 0 construction-only) |

**Aggregate: 14 CRITICAL, 12 MAJOR across 21 test files.**

---

## CRITICAL Findings

### PROJ-338 (4 CRITICAL)

**C-001: Vacuous — constructor tautology: callback stores it**
- `tests/unit/ui/panels/test_build_queue_drag_handler.py:121`
- `test_constructor_with_remove_callback_stores_it`
- Fixture passes a `MagicMock()` as `remove_callback`. Test asserts `h._on_remove_from_queue is not None`. Proves the fixture works, not production. Delete or restructure to verify the callback is invoked during drag.

**C-002: Vacuous — constructor tautology: defaults to None**
- `tests/unit/ui/panels/test_build_queue_drag_handler.py:126`
- `test_constructor_without_remove_callback_defaults_to_none`
- Fixture passes `None` as `remove_callback`. Test asserts `h._on_remove_from_queue is None`. Same issue as C-001.

**C-003: Vacuous — pure arithmetic, zero production code**
- `tests/unit/ui/panels/test_planet_report_panel_characterization.py:403`
- `test_resource_grid_scrollable_area_dimensions_match_layout_constants`
- Computes `content_w = 80 + 5 + 3 * 75 + 10`, asserts the arithmetic. No `PlanetReportPanel` instance is created. No production method is called. Exercises only Python's `+` and `*`.

**C-004: Duplicate test body, different name**
- `tests/unit/ui/panels/test_system_tree_panel_hazard.py:23`
- `test_benign_main_sequence_star_yields_no_hint`
- Body is `assert _format_star_hazard_hints([]) == []` — identical to `test_no_effects_yields_empty_hints` at line 19. Adds no coverage. Delete the duplicate.

### PROJ-339 (7 CRITICAL)

**C-005: Vacuous — hasattr on unconditionally-set attribute**
- `tests/unit/ui/panels/test_race_identity_panel.py:349`
- `test_identity_panel_has_leader_name_input`
- `hasattr(panel, 'leader_name_input')` — `_init_empty_refs()` sets `self.leader_name_input = None` unconditionally. `hasattr` always returns `True`. Tests nothing.

**C-006: Tests imported dictionary, not the panel**
- `tests/unit/ui/panels/test_empire_treasury_panel.py:140`
- `test_all_resources_have_abbreviations`
- Tests `RESOURCE_ABBREVIATIONS` dict from `game.ui.utils.resource_display` — does not exercise `EmpireTreasuryPanel`. Move to a dedicated `test_resource_display.py` or delete.

**C-007: Tests imported dictionary (2nd instance)**
- `tests/unit/ui/panels/test_empire_treasury_panel.py:145`
- `test_abbreviations_are_short`
- Same as C-006.

**C-008: Tests imported dictionary (3rd instance)**
- `tests/unit/ui/panels/test_empire_treasury_panel.py:150`
- `test_expected_abbreviations`
- Same as C-006.

**C-009: Tests pygame_gui's .kill(), not panel-specific cleanup**
- `tests/unit/ui/test_modifier_impact_grid.py:189`
- `test_kill_cleans_up_elements`
- Sole assertion: `not grid.panel.alive()`. Asserts pygame_gui's `.kill()` contract, not `ModifierImpactGrid._clear_ui()` cleanup (elements list, header cache). Add panel-specific cleanup verification.

**C-010: assert_called without content verification**
- `tests/unit/ui/test_race_summary_panel.py:219`
- `test_refresh_updates_faction_label`
- Only `panel.summary_labels['faction_value'].set_text.assert_called()` — never verifies what text was set.

**C-011: assert_called without content verification (2nd instance)**
- `tests/unit/ui/test_race_summary_panel.py:236`
- `test_refresh_updates_theme_label`
- Same pattern as C-010.

### PROJ-340 (3 CRITICAL)

**C-012: `_validate_declared_keys` never tested (design.md items #7, #8)**
- `tests/unit/ui/assets/test_ship_theme_manager.py` (entire file)
- Production: `game/ui/assets/ship_theme_manager.py:220-236`
- Fixtures always use `"Frigate"` (canonical). No test with non-canonical ship class triggers warning branches. No test checks missing-class warning. Direct gap against design.md specification.

**C-013: Missing `assets:` block not tested (design.md item #2)**
- `tests/unit/ui/assets/test_ship_theme_manager.py` (entire file)
- Production: `game/ui/assets/ship_theme_manager.py:139-145`
- No test constructs theme.json lacking `"assets"` key or with `"assets": "bad_type"`. The rejection code path (error log + early return) is untested.

**C-014: Non-dict `assets[ship_class]` entry not tested (design.md item #3)**
- `tests/unit/ui/assets/test_ship_theme_manager.py` (entire file)
- Production: `game/ui/assets/ship_theme_manager.py:166-171`
- No test constructs `"Frigate": "not_a_dict"`. The error-log + skip path is untested.

---

## MAJOR Findings

### PROJ-337 (3 MAJOR)

**M-001: Draw order test checks call counts, not order**
- `tests/unit/research/research_scene/test_event_routing_and_draw.py:191`
- `test_draw_fills_background_then_canvas_then_renderer_then_sidebar_then_ui`
- Test name claims order verification. Only checks: `screen.fill.assert_called_once()`, `call_count == 2`, `renderer.draw.assert_called_once()`, `draw_ui.assert_called_once_with(screen)`. Any permutation of 5 draw operations passes. Should use `call_args_list` sequence assertions on a shared mock.

**M-002: "Lightened border" test doesn't verify lightened color**
- `tests/unit/research/test_research_renderer_drawing.py:433`
- `test_unselected_node_uses_lightened_border_width_1`
- Captures color in `rect_calls` lambda but never asserts it. Only checks `border_call[1][0] == 1` (width). If production stops lightening the color, test still passes.

**M-003: Missing side-effect assertion on budget label set_text**
- `tests/unit/research/research_controls/test_event_routing_and_updates.py:160`
- `test_slider_budget_updates_tracker_label_and_allocation_range`
- Asserts `set_rp_budget(250)`, `update_budget_display()`, `_update_allocation_slider_range()` — but not `lbl_budget_value.set_text('250')` which happens between these calls in production. Wouldn't catch regression that removes just the label update.

### PROJ-338 (6 MAJOR)

**M-004: Single assertion: mock.assert_not_called**
- `tests/unit/ui/panels/test_build_queue_drag_handler.py:493`
- `test_draw_preview_no_drag_no_blits`
- Only `screen.blit.assert_not_called()`. Would pass regardless of what `draw_drag_preview` actually does, as long as it doesn't call `screen.blit`.

**M-005: Weak assertion: isinstance(s, str)**
- `tests/unit/ui/panels/test_system_tree_panel_characterization.py:452`
- `test_format_effect_value_shield_modifier_delegates_to_intrinsic_formatter`
- Only `assert isinstance(s, str)`. Would pass for `""`, `"any string"`, or any string. Add a more specific constraint (non-empty for non-trivial input, regex match).

**M-006/007/008: refresh_design_report error-path tests — mock-only assertions**
- `tests/unit/ui/panels/test_build_queue_controller.py:1312,1338`
- `test_refresh_design_report_load_failure_shows_placeholder` (1312)
- `test_refresh_design_report_ship_load_returns_none_shows_placeholder` (1321)
- `test_refresh_design_report_exception_shows_placeholder` (1338)
- Each only asserts `show_placeholder.assert_called_once()` and/or `update_design.assert_not_called()`. These pin branch coverage but are mock.called-only. Add state assertions (e.g., verify `design_report` content after placeholder is shown).

**M-009: draw_preview tests are blit-count-only (borderline)**
- `tests/unit/ui/panels/test_build_queue_drag_handler.py:493-530`
- Several `draw_drag_preview` tests in `TestDrawDragPreview` class only verify `screen.blit.call_count`. No verification of blit arguments (position, surface identity).

### PROJ-340 (3 MAJOR)

**M-010: `_draw_shield_hit` early-return boundary not actually tested**
- `tests/unit/ui/effects/test_hit_effects.py:127`
- `test_draw_shield_early_returns_when_size_is_below_threshold`
- Test name says "early returns when size below threshold" but test uses `size = int(0 * 3.5) + 4 = 4`, so `4 < 4` is False — guard never entered. Test admits this in a comment. Rename or restructure.

**M-011: `_on_row_change` toggle-off branch untested**
- `tests/unit/ui/panels/test_builder_widgets.py:84`
- Only `toggle=True` → `add_modifier` path tested. `toggle=False` → `remove_modifier` (production line `builder_widgets.py:264`) untested.

**M-012: `get_manual_scale`, `get_skin_path`, `get_portrait_path` untested**
- `tests/unit/ui/assets/test_ship_theme_manager.py` (entire file)
- Three public API methods on `ShipThemeManager` have zero coverage. These are part of the manager's public interface.

---

## Positive Findings (No Issues Found)

- **PROJ-337:** Importlib isolation is correct — `spec_from_file_location` + `module_from_spec` creates a fresh module per test, no `sys.modules` pollution. 22 renderer tests all check properties beyond `.called`. Test names are descriptive throughout.
- **PROJ-338:** Drag handler state machine has **complete coverage** — all 9 requested transition categories are pinned with real state assertions. No missing transition pins.
- **PROJ-339:** D-009 fixture-discovery was correctly resolved via shared `make_ui_widget` factory. `_StubShip` provides clean minimum surface. Behavior accuracy traces all pass.
- **PROJ-340:** Scrollable JSON panel test file (20 tests) is exemplary — exercises `_format_json_with_diff`, `_get_diff_colors`, `_path_has_changes`, `_format_value`, scrollbar drag, and JSON edge cases. Zero construction-only padding.
- **Concurrent-commit contamination:** All 21 test files present and accessible. No missing or duplicated files detected.
- **Test names:** Generally well-named. Vague names (e.g., `test_refresh_updates_*_label`) are in pre-PROJ-339 code, not in characterization additions.

---

## Per-Project Verdict

### PROJ-337 — PASS WITH FINDINGS
3 MAJOR issues (draw order assertion, lightened border color, missing label assertion). No CRITICAL issues. 58 characterization tests are solid with property-rich assertions and proper module isolation.

### PROJ-338 — CONDITIONAL PASS
4 CRITICAL (2 constructor tautologies, 1 arithmetic-only test, 1 duplicate). 6 MAJOR (weak assertions, mock-only blit checks). Drag handler state machine is the strongest area — all transitions pinned. Fix the 4 CRITICAL items before merge.

### PROJ-339 — FAIL
7 CRITICAL — all vacuous tests (3 dictionary tests, 2 mock.called-only, 1 hasattr, 1 pygame_gui-only kill test). The characterization additions (D-009 fixture, `_StubShip`, test names) are solid. Remove or rewrite the 7 vacuous tests.

### PROJ-340 — FAIL
3 CRITICAL — `_validate_declared_keys`, missing `assets:` block rejection, and non-dict asset entries all untested. 3 MAJOR — boundary test not exercising its guard, missing toggle-off branch, missing public API coverage. `test_ship_theme_manager.py` needs the most work. The scrollable JSON panel tests are a model of thorough characterization.
