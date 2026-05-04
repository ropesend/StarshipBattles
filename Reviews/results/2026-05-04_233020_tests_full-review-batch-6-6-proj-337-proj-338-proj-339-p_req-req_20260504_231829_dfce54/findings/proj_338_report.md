# PROJ-338 — UI Panels Characterization Test Review

**Reviewer:** OpenCode (fresh-eyes, no prior review consulted)
**Date:** 2026-05-04
**Scope:** 6 test files, ~112 tests target
**Production referenced:** 5 panel files (see manifest.md)

---

## 1. Behavior Accuracy (trace 3 tests against production)

### 1.1 `test_mouse_down_on_design_button_starts_drag_with_portrait`
- **File:** `tests/unit/ui/panels/test_build_queue_drag_handler.py:165`
- **Production:** `game/ui/panels/build_queue_drag_handler.py:120-143`
- **Trace:** The test creates a design button at `Rect(40,40,100,30)`, clicks at `(50,50)`, which collides. Production hits the `hasattr(element, 'design_id')` + `abs_rect.collidepoint(event.pos)` branch → sets `selected_design`, calls `on_refresh_design_report`, scans designs, loads portrait, populates `dragged_item`.
- **Assertions:** `result == True`, `selected_design == "DSN-1"`, `dragged_item["design_id"] == "DSN-1"`, `dragged_item["name"] == "Frigate"`, `dragged_item["category"] == "ship"`, `dragged_item["portrait"] is not None`, `on_refresh_design_report.assert_called_once_with("DSN-1")`. All meaningful state checks beyond mock.called.
- **Verdict:** PASS — assertions verify production state.

### 1.2 `test_set_items_multi_planet_creates_planetary_system_root_group_with_largest_name`
- **File:** `tests/unit/ui/panels/test_system_tree_panel_characterization.py:154`
- **Production:** `game/ui/panels/system_tree_panel.py:403-420`
- **Trace:** Two planets → `len(planets) > 1` → non-flat path. `largest = max(planets, key=lambda p: p.mass)` selects "Jovian" (mass=99.0). `group_label = f"Planetary System ({largest.name}) ({len(planets)})"` → "Planetary System (Jovian) (2)". Header with `is_group=True`, `group_key="planets_root"`.
- **Assertions:** `len(panel.root_items) == 1`, `is_group is True`, `group_key == "planets_root"`, `"Jovian" in header.label_text`, `"(2)" in header.label_text`. All meaningful structural checks.
- **Verdict:** PASS — assertions verify production grouping/population logic.

### 1.3 `test_draw_battle_over_team0_alive_renders_team1_wins_text`
- **File:** `tests/unit/ui/test_battle_panels_characterization.py:427`
- **Production:** `game/ui/panels/battle_panels.py:495-498`
- **Trace:** `is_over=True`, `team0_alive > 0` → `winner_text = "TEAM 1 WINS!"` (line 498). Render via `win_font.render(winner_text, ...)`. Test stub-fonts captures `font.render.call_args_list` and checks text.
- **Assertions:** `any("TEAM 1 WINS" in t for t in calls)` — checks font render text content.
- **Verdict:** PASS (MAJOR — assertion is on mock.font.render, but verifies meaningful text content, not just `.called`).

---

## 2. Vacuous Tests

### CRITICAL

#### 2.1 Tautology: constructor sets field, test reads it back
- **File:** `tests/unit/ui/panels/test_build_queue_drag_handler.py:121`
- **Test:** `test_constructor_with_remove_callback_stores_it`
- **Reason:** Fixture `_make_handler(with_remove_callback=True)` passes a `MagicMock()` as the remove callback. The test asserts `h._on_remove_from_queue is not None` and `callable(h._on_remove_from_queue)`. The fixture directly sets this field on the instance — the test is self-referential; it proves only that the fixture works, not that production code does.

#### 2.2 Tautology: constructor without field, test reads None back
- **File:** `tests/unit/ui/panels/test_build_queue_drag_handler.py:126`
- **Test:** `test_constructor_without_remove_callback_defaults_to_none`
- **Reason:** Fixture `_make_handler(with_remove_callback=False)` passes `None` as the remove callback. Test asserts `h._on_remove_from_queue is None`. Same pattern as 2.1 — proves only that the fixture works.

#### 2.3 Pure arithmetic, no production code called
- **File:** `tests/unit/ui/panels/test_planet_report_panel_characterization.py:403`
- **Test:** `test_resource_grid_scrollable_area_dimensions_match_layout_constants`
- **Reason:** This test computes local variables `content_w = 80 + 5 + 3 * 75 + 10` and `content_h = 46 + 8 * 20 + 6`, then asserts the arithmetic. No `PlanetReportPanel` instance is created. No production method is called. It exercises nothing but Python's `+` and `*` operators.

#### 2.4 Duplicate test (identical body, different name)
- **File:** `tests/unit/ui/panels/test_system_tree_panel_hazard.py:23`
- **Test:** `test_benign_main_sequence_star_yields_no_hint`
- **Reason:** Body is `assert _format_star_hazard_hints([]) == []` — identical to `test_no_effects_yields_empty_hints` at line 19. The test name implies a distinct scenario ("benign main sequence star") but exercises the exact same input/output. Adds no coverage.

### MAJOR

#### 2.5 Single assertion: mock_method.assert_not_called
- **File:** `tests/unit/ui/panels/test_build_queue_drag_handler.py:493`
- **Test:** `test_draw_preview_no_drag_no_blits`
- **Reason:** When `dragged_item` is None (default constructor state), the only substantive assertion is `screen.blit.assert_not_called()`. This is a pure mock-not-called check — the test would pass regardless of what `draw_drag_preview` actually does, as long as it doesn't call `screen.blit`.

#### 2.6 Weak assertion: isinstance(s, str) on delegated formatter
- **File:** `tests/unit/ui/panels/test_system_tree_panel_characterization.py:452`
- **Test:** `test_format_effect_value_shield_modifier_delegates_to_intrinsic_formatter`
- **Reason:** Only assertion is `assert isinstance(s, str)`. This would pass for `""`, `"any string"`, or any non-None string. The comment says "we don't pin the exact formatting" but a test that only checks the return is a string provides almost no behavioral guarantee.

#### 2.7 Mock-only assertions for refresh_design_report error paths (×3)
- **File:** `tests/unit/ui/panels/test_build_queue_controller.py:1312-1343`
- **Tests:** `test_refresh_design_report_load_failure_shows_placeholder` (line 1312), `test_refresh_design_report_ship_load_returns_none_shows_placeholder` (line 1321), `test_refresh_design_report_exception_shows_placeholder` (line 1338)
- **Reason:** Each test's only assertions are `show_placeholder.assert_called_once()` and/or `update_design.assert_not_called()`. The production method's contract IS to call one or the other, so these do pin branch coverage — but `assert mock.called` is the definition of vacuous per the audit criteria. The success-path test (line 1328) at least checks `assert_called_once_with(ship)` with a real argument object.

---

## 3. Drag Handler State Machine Coverage (CRITICAL)

### Production state machine (`build_queue_drag_handler.py`)

**`handle_mouse_down` (lines 88-153):**
| Guard / Transition | Line | Covered By |
|---|---|---|
| Right button → return False | 112 | `test_mouse_down_right_button_returns_false` |
| multi_select_active → return False | 116 | `test_mouse_down_multi_select_active_returns_false_no_state_change` |
| Design button hit → set selected_design, load portrait, set dragged_item | 120-143 | `test_mouse_down_on_design_button_starts_drag_with_portrait` |
| Design button hit but design not found → skip dragged_item | 132 | `test_mouse_down_on_design_button_with_no_matching_design_skips_dragged_item` |
| Queue row hit → set drag_start_pos, _pending_queue_index | 146-151 | `test_mouse_down_on_queue_row_sets_pending_index_no_drag_yet` |
| No hit → return False | 153 | `test_mouse_down_no_collision_returns_false_no_state_change` |

**`handle_mouse_motion` (lines 155-218):**
| Guard / Transition | Line | Covered By |
|---|---|---|
| multi_select_active → return False | 173 | `test_motion_multi_select_active_returns_false_no_drag_started` |
| guard: no buttons[0] or no drag_start_pos → return False | 176 | `test_motion_button_not_pressed_returns_false` |
| Design-button drag suppressed (drag_start_pos is None) → return False | 176 | `test_handle_mouse_motion_returns_false_during_design_button_drag_due_to_drag_start_pos_none` |
| Motion below threshold → return False | 183/218 | `test_motion_below_threshold_no_drag_started` |
| Motion past threshold → pop (callback path) | 193-194 | `test_motion_above_threshold_starts_drag_pops_via_callback_when_present` |
| Motion past threshold → pop (legacy pop) | 197 | `test_motion_above_threshold_legacy_pops_directly_when_no_callback` |
| Motion past threshold, invalid index → skip pop | 186 | `test_motion_above_threshold_with_invalid_index_skips_pop` |
| Drag starts → clear pending state | 214-215 | `test_motion_clears_pending_state_after_drag_starts` |
| dragged_item carries source="queue" marker | 202-208 | `test_motion_dragged_item_carries_source_queue_marker` |

**`handle_mouse_up` (lines 220-297):**
| Guard / Transition | Line | Covered By |
|---|---|---|
| Right button → return None | 242 | `test_mouse_up_right_button_returns_none_no_state_change` |
| multi_select_active → clear all state, return None | 246-251 | `test_mouse_up_multi_select_clears_all_pending_state_returns_none` |
| Click without drag → select index, refresh | 256-260 | `test_mouse_up_click_without_drag_returns_pending_index` |
| Drop inside → calculate index, call add_to_queue | 271-286 | `test_mouse_up_drop_inside_panel_calls_add_to_queue_with_calculated_index` |
| Drop inside → index clamping at len(queue) | 278 | `test_mouse_up_drop_inside_clamps_index_at_queue_length` |
| Drop inside → index clamping at 0 | 278 | `test_mouse_up_drop_inside_clamps_index_at_zero` |
| Drop outside, from queue → refresh | 291-292 | `test_mouse_up_drop_outside_panel_drops_item_silently_when_from_queue` |
| Drop outside, from design list → no refresh | 291 (else) | `test_mouse_up_drop_outside_panel_no_refresh_when_from_design_list` |
| Drop complete → clear dragged_item | 295 | `test_mouse_up_clears_dragged_item_state_after_drop` |

### Coverage assessment

**ALL requested transitions are pinned:**
- design-button mousedown ✓
- queue-row mousedown ✓
- threshold gating (10px) ✓ (both below + above)
- motion past threshold ✓
- motion below threshold ✓
- multi-select disabled ✓ (mousedown, motion, mouseup — all three event types)
- drop-inside ✓ (including index clamping at both bounds + calculated index)
- drop-outside ✓ (both from-queue and from-design-list paths)
- callback-vs-legacy pop ✓

**No MISSING state-transition pins identified.** The coverage is thorough.

**Assertion quality:**
- The A.2-A.5 state-transition tests verify real state: `dragged_item` dict contents, `selected_design` identity, `_pending_queue_index` values, queue mutation (len changes), callback arguments.
- The A.6 `draw_drag_preview` tests are blit-count-based — some are borderline vacuous (see 2.5).

---

## 4. Test Name Quality (spot-check 2 files)

### `test_system_tree_panel_characterization.py`
All test names are descriptive and specific:
- `test_set_items_multi_planet_creates_planetary_system_root_group_with_largest_name` — clear what's tested
- `test_on_click_group_expand_recursively_expands_child_groups` — precise behavior
- `test_add_effects_group_uses_legacy_provider_label_when_source_label_missing` — exact condition
- `test_on_click_leaf_without_callback_silent_no_crash` — edge case clearly named

**No vague names found in this file.**

### `test_planet_report_panel_characterization.py`
Names are generally good. Minor concerns:
- `test_resource_grid_text_colour_setter_attribute_error_swallowed_silently` — long but precise
- `test_resource_grid_scrollable_area_dimensions_match_layout_constants` — describes what the test does but the test itself is vacuous (see 2.3)
- `test_construction_atmosphere_graph_height_floor_50px_when_rect_too_short` — name describes a production branch, but the test body is pure arithmetic with no production instance

**No vague names found.** Names are adequate. The issue with the two tests above is content, not naming.

---

## 5. Concurrent-Commit Contamination

All 6 PROJ-338 test files are present and accessible:

| File | Status |
|---|---|
| `tests/unit/ui/panels/test_build_queue_drag_handler.py` | Present (578 lines) |
| `tests/unit/ui/panels/test_build_queue_controller.py` | Present (1343 lines, EXTEND) |
| `tests/unit/ui/panels/test_system_tree_panel_characterization.py` | Present (489 lines) |
| `tests/unit/ui/panels/test_system_tree_panel_hazard.py` | Present (166 lines, EXTEND) |
| `tests/unit/ui/panels/test_planet_report_panel_characterization.py` | Present (440 lines) |
| `tests/unit/ui/test_battle_panels_characterization.py` | Present (495 lines) |

**No contamination detected.** All files readable, no missing test files.

---

## Verdict

**PROJ-338: CONDITIONAL PASS with 4 CRITICAL and 6 MAJOR findings.**

### Strengths
- The drag handler state machine has **complete coverage** of all requested transitions (Task 3). No missing transition pins. This was the highest-risk area.
- Behavior accuracy traces (Task 1) all pass — sampled tests verify real production state, not just mock counts.
- Test names are generally clear and descriptive (Task 4).
- All 6 files exist and are accessible (Task 5).

### Required fixes (CRITICAL)
1. **Remove or rewrite** the vacuous arithmetic test (`test_resource_grid_scrollable_area_dimensions_match_layout_constants`) — it exercises no production code.
2. **Fix** the two constructor tautology tests (2.1, 2.2) — either delete them or restructure to verify meaningful behavior (e.g., assert that the stored callback is actually invoked during a drag operation).
3. **Delete or rename** `test_benign_main_sequence_star_yields_no_hint` — it is an exact duplicate of `test_no_effects_yields_empty_hints`.

### Recommended fixes (MAJOR)
4. **Strengthen** `test_draw_preview_no_drag_no_blits` — add an assertion about state after the no-op call.
5. **Strengthen** `test_format_effect_value_shield_modifier_delegates_to_intrinsic_formatter` — assert a more specific return constraint (e.g., string is non-empty for non-trivial input, or matches a regex).
6. **Consider adding** a real state assertion to the 3 `refresh_design_report` error-path tests — even verifying `design_report.last_call` or similar would improve them.
