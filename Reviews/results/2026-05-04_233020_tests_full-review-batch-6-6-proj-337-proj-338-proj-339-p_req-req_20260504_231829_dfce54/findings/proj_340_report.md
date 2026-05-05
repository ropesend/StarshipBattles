# PROJ-340 — Test Quality Review

**Reviewed:** 2026-05-04 | **Reviewer:** OpenCode (fresh-eyes, no prior reviews consulted)

---

## 1. Behavior Accuracy — 3 Tests Traced

### 1a. `test_initialize_skips_ship_class_when_skin_file_missing` → `ship_theme_manager.py`

**Verdict:** PASS — accurately characterizes production behavior.

Test constructs a theme where `skin_frigate.png` is NOT written to disk (`write_skin=False`). Production `_discover_theme` (line 176-179) checks `os.path.exists(candidate)` → False → `skin_path` remains `None` → line 207 `if skin_path is None: continue` → the ship-class entry is skipped. Test asserts `mgr.theme_data["NoSkin"] == {}`. Matches production exactly.

### 1b. `test_set_json_with_diff_valid_json_renders_with_diff_coloring` → `scrollable_json_panel.py`

**Verdict:** PASS — accurately characterizes the full render pipeline.

Test parses `'{"hp": 50, "shield": 10}'` with `diff_paths = {"hp": DiffResult.CHANGED}`. Production route: `set_json_with_diff` → `json.loads` → `_format_json_with_diff` → `_add_key_value_line_with_diff` → `_get_diff_colors("hp")` returns `(changed_text, changed_bg)`. Test correctly finds the hp line in `json_lines`, verifies the tuple shape `(indent, (key_str, value_str, key_color, value_color), None, bg_color)`, and asserts `bg_color == panel.changed_bg`.

### 1c. `test_progress_returns_one_when_duration_is_zero` → `hit_effects.py`

**Verdict:** PASS — edge case handled correctly.

Production `progress` property (line 68-70): `min(self.elapsed / self.duration, 1.0) if self.duration > 0 else 1.0`. With `duration=0.0`, `0.0 > 0` is False → returns `1.0`. Avoids ZeroDivisionError.

---

## 2. Ship Theme Manager Schema — Design.md Item #7

### Schema in test fixtures

The `_minimal_theme_json` function builds:
```json
{
    "schema_version": 1,
    "name": "TestTheme",
    "description": "test",
    "image_sizes": {},
    "assets": {"Frigate": {"skin": "skin_frigate.png", "scale": 1.0, "portrait": "portrait_frigate.png"}}
}
```

### Schema in production `_discover_theme` (lines 128-218)

Production processes: `name`, `schema_version`, `assets:`, `image_sizes`, per-entry `skin:`/`portrait:`/`scale:`. The fixture matches the production schema for all required fields. Every field used by the test fixture is consumed by production. **No schema field mismatch found.**

However, the fixture always uses `"Frigate"` which is a member of `SHIP_CLASSES_WITH_VISUAL_THEMES`, meaning `_validate_declared_keys` (line 220-236) is **never exercised** with non-canonical or missing ship classes.

### CRITICAL Gaps — Design.md coverage items #7 and #8 NOT covered

PROJ-340 `design.md` explicitly requires (lines 99-104):

> 7. Extra ship classes not in SHIP_CLASSES_WITH_VISUAL_THEMES — warning logged via _validate_declared_keys but not rejected.
> 8. Missing canonical ship classes — warning logged.

**Neither of these behaviors is tested.** See findings #F-01 and #F-02 below.

Also required by design.md but untested:

> 2. Missing assets: block — early return + error log.

**No test covers a valid-JSON theme.json lacking the `assets:` key** (which triggers `not isinstance(assets, dict)` at production line 139-145).

---

## 3. Scrollable JSON Panel — Design.md Item #8

### Summary

All 20 tests exercise real production behavior — there are **zero construction-only tests**. Every test class calls into non-trivial production methods.

### Method coverage

| Production method | Tested? | Tests |
|---|---|---|
| `set_json_with_diff` | Yes | `TestSetJsonWithDiff` (2 tests), `TestSetJsonWithDiffValid` (1 test) |
| `_format_json_with_diff` | Yes | `TestSetJsonWithDiffValid`, `TestFormatJsonWithDiffNested` (2 tests) |
| `_get_diff_colors` | Yes | `TestGetDiffColors` (3 tests — all 3 DiffResult values, both panel types) |
| `_path_has_changes` | Yes | `TestPathHasChanges` (3 tests — direct, nested, prefix vs substring) |
| `_format_value` | Yes | `TestFormatValue` (1 test — long string truncation) |
| `_add_key_value_line_with_diff` | Yes | Indirectly via `TestSetJsonWithDiffValid` |
| `handle_event` | Yes | `TestHandleEvent` (3 tests — wheel in/out bounds, scrollbar drag start) |
| `_handle_scrollbar_drag` | Yes | `TestHandleScrollbarDrag` (2 tests — normal drag, noop when no range) |

### `_build_diff_matrix` / `_colorize_json`

Neither method exists in the production code. The equivalent functionality is split across `_get_diff_colors`, `_add_key_value_line_with_diff`, and `_format_json_with_diff`. All are tested.

### JSON parsing edge cases covered

- `None` payload → empty lines, zero content height
- Malformed JSON → error line prepended + raw lines fallback
- Valid flat JSON → proper line count, scroll dimensions, diff coloring
- Nested dict → correct indentation levels
- List of objects → bracket/brace rendering, comma handling

This test file is **the strongest of the 6** — thorough, well-structured, no construction-only padding.

---

## 4. Test Names — Spot-Check

### `tests/unit/ui/panels/test_base_gallery.py`

All 11 test names are descriptive. Examples: `test_init_constructs_expected_widget_tree_for_populated_asset_list`, `test_on_asset_selected_toggles_highlight_select_on_match_unselect_on_others`. **No vague names found.**

### `tests/unit/ui/panels/test_builder_widgets.py`

All 9 test names are descriptive. Some are long (`test_layout_caches_scroll_position_from_existing_container_before_clearing` — 74 chars) but none are vague or misleading. **No issues.**

**Verdict: PASS.** Both files use clear, behavior-describing test names.

---

## 5. Concurrent-Commit Contamination

All 6 PROJ-340 test files exist and are non-trivial:

| File | Size | Accessible |
|---|---|---|
| `tests/unit/ui/services/test_battle_ui_service.py` | 5,998 bytes | Yes |
| `tests/unit/ui/assets/test_ship_theme_manager.py` | 11,427 bytes | Yes |
| `tests/unit/ui/widgets/test_scrollable_json_panel.py` | 13,563 bytes | Yes |
| `tests/unit/ui/effects/test_hit_effects.py` | 8,185 bytes | Yes |
| `tests/unit/ui/panels/test_base_gallery.py` | 12,294 bytes | Yes |
| `tests/unit/ui/panels/test_builder_widgets.py` | 9,127 bytes | Yes |

**No contamination detected.** All files present with expected content.

---

## Findings

### CRITICAL

**F-01: `_validate_declared_keys` never tested (design.md item #7)**
- **File:** `tests/unit/ui/assets/test_ship_theme_manager.py` (entire file)
- **Production:** `game/ui/assets/ship_theme_manager.py:220-236`
- **Issue:** The `_validate_declared_keys` static method warns when theme.json declares ship classes not in `SHIP_CLASSES_WITH_VISUAL_THEMES` (extras) and when canonical classes are missing. The test fixtures always use `"Frigate"` which IS in the canonical set. No test supplies a non-canonical ship class (e.g., `"DeathStar"`) to trigger the warning branch at line 226-231. No test checks the "missing" warning branch at line 232-236. This is a direct omission against design.md specification items #7 and #8.

**F-02: Missing `assets:` block not tested (design.md item #2)**
- **File:** `tests/unit/ui/assets/test_ship_theme_manager.py` (entire file)
- **Production:** `game/ui/assets/ship_theme_manager.py:139-145`
- **Issue:** Production `_discover_theme` does `data.get('assets')` — if this returns `None` (key absent) or a non-dict, the theme is rejected with a specific error log mentioning "legacy 'images:' schema is no longer supported". No test constructs a theme.json that lacks the `assets:` key or has `"assets": "bad_type"`. The only "bad" theme tested is unparseable JSON (`test_initialize_skips_theme_with_invalid_theme_json`), which exercises a different code path (`load_json` returns None at line 132-133).

**F-03: Non-dict `assets[ship_class]` entry not tested (design.md item #3)**
- **File:** `tests/unit/ui/assets/test_ship_theme_manager.py` (entire file)
- **Production:** `game/ui/assets/ship_theme_manager.py:166-171`
- **Issue:** When an asset entry is `"Frigate": "not_a_dict"`, production logs an error and `continue`s (skipping the class). No test constructs such a malformed entry. The fixture always provides a proper dict with at least `"skin"` and `"scale"`.

### MAJOR

**F-04: `_draw_shield_hit` early-return guard boundary NOT actually tested**
- **File:** `tests/unit/ui/effects/test_hit_effects.py:127-150`
- **Production:** `game/ui/effects/hit_effects.py:128-129`
- **Issue:** `test_draw_shield_early_returns_when_size_is_below_threshold` claims to test the `if size < 4: return` guard. However, the test uses `ship_radius=0.0` and `zoom=0.0` which produces `size = int(0 * 3.5) + 4 = 4`. Since `4 < 4` is False, the guard is **never entered**. The test comment at line 133-136 acknowledges this limitation: *"To trigger early return we need negative inputs. Production never produces negatives in practice, so we instead pin: with a tiny radius/zoom that keeps size at the threshold, draw still runs."* The test name is misleading — it does NOT verify the early-return behavior; it verifies the boundary survives without crashing. A proper boundary test would verify either `size >= 4` continues (which it does) or use a negative radius to actually test the return.

**F-05: `_on_row_change` toggle-off branch (`value=False`) not tested**
- **File:** `tests/unit/ui/panels/test_builder_widgets.py:84-107`
- **Production:** `game/ui/panels/builder_widgets.py:255-264`
- **Issue:** `test_on_row_change_toggle_true_adds_modifier_and_recalculates` tests the `toggle=True` → `add_modifier` path but no test exercises the `toggle=False` → `remove_modifier` path (production line 264). The full `_on_row_change` toggle logic has two branches; only one is characterized.

**F-06: `get_manual_scale` and `get_skin_path` / `get_portrait_path` untested**
- **File:** `tests/unit/ui/assets/test_ship_theme_manager.py` (entire file)
- **Production:** `game/ui/assets/ship_theme_manager.py:345-353` (get_manual_scale), `428-439` (path accessors)
- **Issue:** Three public API methods on ShipThemeManager have zero test coverage: `get_manual_scale` (returns per-ship scale factor), `get_skin_path` (returns absolute filesystem skin path), `get_portrait_path` (returns absolute filesystem portrait path). These are part of the manager's public interface but never exercised.

### MINOR

- **Test name length:** `test_layout_caches_scroll_position_from_existing_container_before_clearing` (74 chars) and `test_layout_renders_select_component_hint_when_editing_component_is_none` (76 chars) are very long. Not a bug, but consider shorter forms (e.g., `test_layout_cache_scroll_on_clear`, `test_layout_renders_hint_when_no_component`).
- **MagicMock spec missing:** The `panel_factory` fixture in `test_scrollable_json_panel.py:32` uses `MagicMock()` without `spec=pygame.Surface`. `rendered.get_width.return_value = 7` works, but a `spec` would catch attribute errors earlier.

---

## Verdict for PROJ-340

**FAIL.**

Three CRITICAL gaps in `test_ship_theme_manager.py` leave core `_discover_theme` branches untested: `_validate_declared_keys` coverage (#7/#8 from design.md), missing `assets:` block rejection (#2), and non-dict asset entries (#3). Multiple public API methods on `ShipThemeManager` also lack any test. The scrollable JSON panel tests are excellent and hit_effects coverage is good. `test_builder_widgets.py` is missing the `toggle=False` branch. Remediation priority: add the 3 missing `_discover_theme` schema-variant tests, then add `toggle=False` and `_draw_shield_hit` boundary coverage.
