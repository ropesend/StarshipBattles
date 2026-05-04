# Review Report: PROJ-337/PROJ-340 Test Quality Audit

**Review Type:** tests
**Request ID:** req_20260504_222600_0f1610
**Scope:** 2 projects, ~105 characterization tests across 9 test files
**Review Mode:** standard (not lightweight — no Coverage block present)
**Limitations:** Production code was read but not exhaustively compared for every test. 5 tests selected for deep behavior verification per request instructions. `battle_ui_service.py` component conversion not deep-verified due to lack of test coverage on that path.

---

## Behavior Accuracy (5 Deep-Verified Tests)

All five selected tests correctly characterize production behavior:

| Test | Production Verified | Pass/Fail |
|---|---|---|
| `test_selected_node_drawn_with_selected_color_width_3` | `research_renderer.py:240-241` — `pygame.draw.rect(screen, self.COLOR_SELECTED, rect, 3, ...)` | PASS |
| `test_rp_allocation_bar_drawn_only_when_allocation_positive` | `research_renderer.py:248` — `if state.rp_allocation > 0:` gates the extra rect | PASS |
| `test_slider_allocation_uses_actual_clamped_value_in_label` | `research_controls.py:283-285` — reads `actual = tracker.get_state(node_id).rp_allocation` after set | PASS |
| `test_convert_projectile_uses_projectile_colors_mapping_for_type` | `battle_ui_service.py:264-265` — `color = PROJECTILE_COLORS.get(proj_type, DEFAULT_PROJECTILE_COLOR)` | PASS |
| `test_load_image_falls_back_to_default_theme_for_unknown_theme` | `ship_theme_manager.py:281-287` — `theme_name = self.default_theme` redirect | PASS |

Assertions in the verified tests check meaningful properties (color values, widths, positions, clamping), not just `mock.called == True`.

---

## Findings

### MAJOR

**MAJ-001: `base_gallery.py` has critically thin coverage (3 tests for 265 LOC)**
- `tests/unit/ui/panels/test_base_gallery.py:101-158` — only 3 test methods
- Untested: `on_asset_selected` full routing (callback firing, highlight toggling at `base_gallery.py:221-243`), `_populate_gallery` with 0 assets or edge-case column calculation, `set_from_config` (`base_gallery.py:245-249`), `_sanitize_object_id` (`base_gallery.py:217-219`)
- The 3 existing tests use `_patched_widgets()` which replaces all `pygame_gui.elements.*` with MagicMock — tests verify construction counts but not behavioral correctness of widget interactions

**MAJ-002: `builder_widgets.py` untested `value_change` action path in `_on_row_change`**
- `tests/unit/ui/panels/test_builder_widgets.py:84-107` — tests only `toggle=True`
- The `value_change` branch at `builder_widgets.py:269-274` (which modifies modifier.value and recalculates) has zero coverage
- `rebuild()` method (`builder_widgets.py:72-79`) and scroll position cache restore (`builder_widgets.py:169-174`) also untested

**MAJ-003: `scrollable_json_panel.py` has no valid-JSON happy-path test**
- `tests/unit/ui/widgets/test_scrollable_json_panel.py` — 7 tests total
- `set_json_with_diff` tested only with `None` (line 55) and invalid JSON (line 65); the primary behavior — valid JSON parse with diff coloring — is untested
- `draw()` method (412 LOC in production), `_handle_scrollbar_drag`, and `_format_json_with_diff` for nested dicts/lists are all untested
- `_path_has_changes` has only 2 assertions (positive match), no edge cases for empty paths or no diff_paths

### MINOR

**MIN-001: `battle_ui_service.py` missing test coverage for 3 public DTO methods**
- `get_winner()` (`battle_ui_service.py:124-133`), `is_battle_over()` (`battle_ui_service.py:113-122`), `get_tick_count()` (`battle_ui_service.py:135-144`) — zero tests
- These are simple pass-through methods but are part of the service's public API surface

**MIN-002: `ship_theme_manager` test fixture hardcodes `"Frigate"` while design.md shows lowercase `"frigate"`**
- `test_ship_theme_manager.py:37` — fixture uses `"assets": {"Frigate": entry}`
- `PROJ-340/design.md:56` — example uses `"frigate"` (lowercase)
- Not a bug (production matches against `SHIP_CLASSES_WITH_VISUAL_THEMES` display form, likely "Frigate"), but inconsistency between design doc example and test fixture may confuse future maintainers

**MIN-003: `ship_theme_manager` test fixture writes `image_sizes` as `{}` skipping size validation path**
- `test_ship_theme_manager.py:47` — `"image_sizes": {}` in every test theme
- `_discover_theme` calls `_validate_image_size` only when `image_sizes` dict is populated (`ship_theme_manager.py:245-251`), so the PIL-based size validation code path is never exercised

### OBSERVATION

**OBS-001: PROJ-337 test naming is strong and assertion quality is high**
- Names like `test_rp_allocation_bar_drawn_only_when_allocation_positive` and `test_dependency_line_color_uses_met_when_prereq_meets_required_level` are behaviorally specific
- Assertions check color tuples, widths, order-of-calls, not just `mock.called`

**OBS-002: Characterization of `update_turn_log` truncation is correctly pinned**
- `test_update_turn_log_truncates_after_five_turns` (`test_event_routing_and_updates.py:464`) correctly characterizes the `parts[:5]` split-then-keep behavior at `research_controls.py:445-446`
- The test documents observed behavior (drops the oldest turn entry) with a D-007 annotation — this is the correct approach per project convention

**OBS-003: `_minimal_theme_json` includes `description` / `image_sizes` as required keys, but production accepts them as optional**
- Production `_discover_theme` (`ship_theme_manager.py:136-154`): `description` defaults to `''`, `image_sizes` defaults to `{}`
- The test fixture always includes both, which means the "missing optional fields" edge cases are untested — but this is low-risk since production handles them gracefully

---

## Mocking Discipline Summary

| File | Pattern | Quality |
|---|---|---|
| `test_research_renderer_drawing.py` | importlib-isolated module + per-test `pygame.draw` monkeypatch | Good — clean isolation, meaningful arg captures |
| `test_event_routing_and_updates.py` | `MagicMock(spec=...)` + lambda method binding | Good — runs real methods, avoids `_create_ui` side effects |
| `test_event_routing_and_draw.py` | contextmanager patches all 6-7 dependencies | Good — necessary for constructor isolation |
| `test_battle_ui_service.py` | plain Mock ships/engine fed to real `BattleUIService` | Good — exercises real conversion logic |
| `test_ship_theme_manager.py` | `monkeypatch` for paths + `pygame.image.load` | Good — synthetic surfaces, no disk I/O needed |
| `test_scrollable_json_panel.py` | `patch` for `get_font` + real `pygame.Surface` / `pygame.event.Event` | Good — real surfaces where drawn |
| `test_hit_effects.py` | plain Mock camera + real `pygame.Surface` | Good — exercises real draw dispatch |
| `test_base_gallery.py` | `patch.multiple` replaces all `pygame_gui.elements` | Over-mocked — only verifies construction counts, not widget behavior |
| `test_builder_widgets.py` | `patch.multiple` replaces `UIButton/UILabel/UIScrollingContainer` | Over-mocked — same concern as base_gallery |

---

## Apparent Bugs

No bugs found in the tests or in the production behaviors they pin. The tests correctly characterize observed production behavior. One area worth noting: `research_controls.py:385` — the allocation slider range floor `max(1, max_allocation)` is pinned by `test_update_allocation_slider_range_uses_max_one_floor`, which correctly characterizes that a zero-remaining-RP slider still allows at least value 1.
