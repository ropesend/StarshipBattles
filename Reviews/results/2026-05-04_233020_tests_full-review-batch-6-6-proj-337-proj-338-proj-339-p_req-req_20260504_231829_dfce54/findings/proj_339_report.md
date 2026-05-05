# PROJ-339 Test Quality Review — Findings

**Reviewer:** OpenCode (fresh-eyes, batch 6/6)
**Date:** 2026-05-04
**Scope:** 6 test files, 29 tests + 7 review-4 fixes
**Production:** `game/ui/panels/{race_summary_panel, design_stats_panel, modifier_impact_grid, race_identity_panel, race_environment_panel, empire_treasury_panel}.py`

---

## 1. Behavior Accuracy

### 1a. `test_handle_event_collapse_click_updates_collapsed_sections` → `design_stats_panel.py:handle_event`

**Test:** `tests/unit/ui/panels/test_design_stats_panel.py:415`
**Prod:** `game/ui/panels/design_stats_panel.py:338-355`

**Traced path:** Panel constructed via `_make_panel(ship=_StubShip())` → `section_header_buttons` populated → stubs `get_abs_rect` to `pygame.Rect(50, 50, 100, 25)` → simulates `MOUSEBUTTONDOWN` at `(60, 60)` (inside rect) → verifies `sec_key` added to `collapsed_sections`, returns `True`. Second click removes it.

**Verdict: ACCURATE.** The test exercises the real `handle_event()` method with the real toggle logic. Assertions verify membership in `collapsed_sections` and return values — not just `mock.called == True`.

### 1b. `test_update_with_modifiers_groups_effects_by_source_modifier_id` → `modifier_impact_grid.py:update`

**Test:** `tests/unit/ui/test_modifier_impact_grid.py:85`
**Prod:** `game/ui/panels/modifier_impact_grid.py:102-154` (grouping at 130-148)

**Traced path:** Real `ModifierImpactGrid` + real `ModifierEffect` dataclass instances (from `game.simulation.components.modifier_effects`) → two effects with same `source_modifier_id='size_mount'` → `grid.update(mock_component)` → verifies `len(grid.modifier_rows) == 1`, merged `stats` dict keys `{'mass_mult', 'hp_mult'}`, and `stat_columns` set.

**Verdict: ACCURATE.** Uses real production `ModifierEffect` objects and real `ModifierImpactGrid`. Exercises the grouping logic with concrete assertions on the merged data structure — not just `mock.called`.

### 1c. `test_row_visible_with_single_resource_upkeep` → `empire_treasury_panel.py:_get_expense_rows`

**Test:** `tests/unit/ui/panels/test_empire_treasury_panel.py:346`
**Prod:** `game/ui/panels/empire_treasury_panel.py:256-279`

**Traced path:** Mutates `sample_snapshot.total_population_upkeep = {"organics": 5.0}` → constructs `EmpireTreasuryPanel` → calls `_get_expense_rows()` → finds "Population Upkeep" row → verifies `is_total is False`, value is negated (`-5.0`), unused resources default to `0.0`.

**Verdict: ACCURATE.** Tests the data transformation (negation for "drain" display) and row-filtering logic. Checks concrete numeric values, not just presence.

---

## 2. Vacuous Tests

### CRITICAL — 7 vacuous tests found across 3 files

| # | File | Line | Test Name | Reason |
|---|------|------|-----------|--------|
| 1 | `tests/unit/ui/panels/test_race_identity_panel.py` | 349 | `test_identity_panel_has_leader_name_input` | `hasattr(panel, 'leader_name_input')` — `_init_empty_refs()` unconditionally sets `self.leader_name_input = None` in production (race_identity_panel.py:76). `hasattr` always returns `True`. Tests nothing about production behavior. |
| 2 | `tests/unit/ui/panels/test_empire_treasury_panel.py` | 140 | `test_all_resources_have_abbreviations` | Tests `RESOURCE_ABBREVIATIONS` dict imported from `game.ui.utils.resource_display` — does **not** exercise `EmpireTreasuryPanel` at all. Tests an external constant dictionary. |
| 3 | `tests/unit/ui/panels/test_empire_treasury_panel.py` | 145 | `test_abbreviations_are_short` | Same — tests the `RESOURCE_ABBREVIATIONS` dict, not the panel. |
| 4 | `tests/unit/ui/panels/test_empire_treasury_panel.py` | 150 | `test_expected_abbreviations` | Same — tests hardcoded string values in an imported dict. |
| 5 | `tests/unit/ui/test_modifier_impact_grid.py` | 189 | `test_kill_cleans_up_elements` | Calls `grid.update(MagicMock())` with empty data, then `grid.kill()`, then asserts `not grid.panel.alive()`. The sole assertion tests pygame_gui's `.kill()` contract, not `ModifierImpactGrid`-specific cleanup. `_clear_ui()` is never verified (elements list, header cache). |
| 6 | `tests/unit/ui/test_race_summary_panel.py` | 219 | `test_refresh_updates_faction_label` | Single substantive assertion is `panel.summary_labels['faction_value'].set_text.assert_called()` — exact form of the anti-pattern "assert mock_method.called". Does **not** verify what text was set. |
| 7 | `tests/unit/ui/test_race_summary_panel.py` | 236 | `test_refresh_updates_theme_label` | Same pattern: `panel.summary_labels['theme_value'].set_text.assert_called()` without verifying the text content. |

**Note:** Review-4 previously replaced 10 vacuous tests across PROJ-338/339, but the 7 above were NOT caught. Items #2–4 (TestResourceAbbreviations) are particularly surprising — they test a dictionary from another module (`game.ui.utils.resource_display`), not `EmpireTreasuryPanel` at all. Items #6–7 are in pre-PROJ-339 code but still fall under the "assert mock.called" anti-pattern.

---

## 3. PROJ-339 `_StubShip` + `_patched_pygame_gui_for_rebuild` Fixture (D-009)

### Source: `tests/unit/ui/panels/test_design_stats_panel.py:133-218`

**D-009 concern:** No existing fixture constructed a `DesignStatsPanel` instance. The concern was whether `_build_layout`'s `UIScrollingContainer.get_container().get_rect().width` call would work through the mock chain.

**Resolution (validated):** The shared `make_ui_widget` factory from `tests/fixtures/ui_widget_factory.py` introspects `DesignStatsPanel.__init__`, supplies a `pygame.Rect(0, 0, 600, 400)` as `rect`, and patches all `pygame_gui.elements.UI*` classes (including `UIScrollingContainer`, `UILabel`, `UITextBox`) to `MagicMock` for the duration of `__init__`. When `_make_panel(ship=_StubShip())` is called, `_build_layout` runs inside the factory's patch context — all widget construction is mocked.

**Is it a real fixture or mocked-out production?** It is mocked-out production, by design: `make_ui_widget` patches pygame_gui element classes so that `__init__` and `_build_layout` can run their full logic paths without allocating real GPU surfaces. This is the established pattern per D-005 ("Reuse existing pygame_gui mock fixtures").

The `_StubShip` class is a real helper (not mocked) that exposes every attribute/method the production code reads during `_build_layout`, `_build_sections`, and `update_stats`. It returns concrete typed values (0, 0.0, `""`, `[]`, empty dicts).

### 3 tests exercising production behavior:

1. **`test_construct_with_none_ship_then_rebuild_populates_rows_map`** (line 228): Constructs with `ship=None` (no layout), then `panel.rebuild(_StubShip())` wrapped in `_patched_pygame_gui_for_rebuild()`. Verifies `rows_map` populated, `layer_rows` has 4 slots, `stats_scroll` is non-None. **Exercises `rebuild()` → `_build_layout()` → `_build_sections()`** production path.

2. **`test_show_requirements_false_omits_textboxes`** (line 242): Constructs via `_make_panel(ship=_StubShip(), show_requirements=False)`. Verifies `req_box_left` and `req_box_right` are `None`. **Exercises `__init__` → `_build_layout()` → `_build_sections()`** path with the requirements guard.

3. **`test_kill_calls_super_kill_and_destroys_widgets`** (line 527): Constructs with `_StubShip()` + `show_requirements=True`, then calls `panel.kill()`. Verifies `scroll_mock.kill.assert_called_once()`, and that `rows_map`, `layer_rows`, `req_box_left`, `req_box_right`, `stats_scroll` are all cleared. **Exercises `kill()` production path** at design_stats_panel.py:507-516.

**All 3 tests pass** (verified via `pytest` run). D-009 fixture-discovery cost was resolved without introducing a separate decision entry.

---

## 4. Test Names — Spot Check

### `tests/unit/ui/test_race_summary_panel.py`

| Line | Name | Issue |
|------|------|-------|
| 219 | `test_refresh_updates_faction_label` | **VAGUE** — "updates" doesn't specify *what* behavior (sets text? shows? changes color?). Missing condition/scenario. |
| 236 | `test_refresh_updates_theme_label` | **VAGUE** — same issue. |
| 193 | `test_format_description_status_with_content` | **VAGUE** — "status" is ambiguous. What aspect of the format? |
| 203 | `test_format_description_status_empty` | **VAGUE** — same. |
| 398 | `test_refresh_renders_every_scalar_factor_display_name` | **GOOD** — specific about what is rendered. |
| 581 | `test_refresh_ship_preview_skips_when_theme_unset` | **GOOD** — describes behavior + condition. |
| 719 | `test_handle_button_click_invokes_load_callback_only_when_btn_load` | **GOOD** — specific about gating logic. |

### `tests/unit/ui/panels/test_race_identity_panel.py`

| Line | Name | Issue |
|------|------|-------|
| 88 | `test_update_config_reads_race_name` | **GOOD** — action + target. |
| 132 | `test_update_config_handles_empty_dropdown` | **GOOD** — edge case identified. |
| 203 | `test_set_from_config_passes_correct_starting_option` | **GOOD** — specific about *which* constructor arg. |
| 318 | `test_update_labels_is_no_op_returns_none_without_mutating_inputs` | **GOOD** — describes 3 contract obligations. |
| 349 | `test_identity_panel_has_leader_name_input` | **VAGUE** — tests attribute existence, name reflects the vacuity. |
| 390 | `test_faction_override_blocks_auto_regen_on_race_name_edit` | **GOOD** — specific behavior + trigger. |

**Overall:** PROJ-339 characterization test names (suffixed `TestPROJ339*`) are well-named. The vagueness is concentrated in pre-PROJ-339 tests in `TestRefreshSummary` and `TestSummaryDataFormatting`.

---

## 5. Concurrent-Commit Contamination

All 6 PROJ-339 test files exist and are accessible:

| # | File | Status | Lines |
|---|------|--------|-------|
| 1 | `tests/unit/ui/panels/test_empire_treasury_panel.py` | ✅ Present | 560 |
| 2 | `tests/unit/ui/test_race_environment_panel.py` | ✅ Present | 510 |
| 3 | `tests/unit/ui/panels/test_race_identity_panel.py` | ✅ Present | 463 |
| 4 | `tests/unit/ui/test_modifier_impact_grid.py` | ✅ Present | 412 |
| 5 | `tests/unit/ui/test_race_summary_panel.py` | ✅ Present | 750 |
| 6 | `tests/unit/ui/panels/test_design_stats_panel.py` | ✅ Present | 550 |

**No missing files.** All 6 match the scope listed in `Reviews/results/.../scope.md`.

---

## Verdict

PROJ-339 tests are **adequate as characterization tests** for mid-risk panels with the following concerns:

**PASS:** Behavior accuracy is solid across the 3 traced tests. D-009 fixture-discovery was successfully resolved via the shared `make_ui_widget` factory. The `_StubShip` provides a clean minimum surface. Test names for the characterization additions are well-described.

**FAIL (7 vacuous tests):** 
- `test_identity_panel_has_leader_name_input` (hasattr on unconditionally-set attribute)
- 3 `TestResourceAbbreviations` tests (test an imported dictionary, not the panel)
- `test_kill_cleans_up_elements` (only asserts pygame_gui behavior)
- 2 `test_refresh_updates_*_label` tests (only assert mock.called, never check text content)

**RECOMMENDATION:** Fix the 7 vacuous tests or move `TestResourceAbbreviations` out of the empire_treasury_panel test file into a dedicated resource_display test. For the two refresh-label tests, add content verification on `set_text` call args.
