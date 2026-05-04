# PROJ-339 Characterization Test Review

## 1. Behavior Accuracy (CRITICAL/MAJOR)

### MAJOR: All sampled tests accurately pin production behavior
**File:** tests/unit/ui/test_modifier_impact_grid.py (line 237)
**Category:** accuracy
**Finding:** `test_format_value_prefixes_per_operation` — all four assertions trace correctly through `_format_value` → `_format_sig_digits`:
- `_format_value(1.5, 'multiply')` → `"x1.500"` ✓
- `_format_value(50, 'add')` → `"+50.00"` ✓
- `_format_value(-1, 'add')` → `"-1.000"` ✓ (negative add produces formatted string already carrying minus sign)
- `_format_value(7, 'set')` → `"=7.000"` ✓

**Recommendation:** No action needed.

---

### MAJOR: Rounding boundary test accurately pins production behavior
**File:** tests/unit/ui/panels/test_empire_treasury_panel.py (line 496)
**Category:** accuracy
**Finding:** `test_format_value_zero_thousands_and_rounding` — all three assertions trace correctly through `_format_value`:
- `_format_value(0)` → `"0"` ✓ (early return)
- `_format_value(1234)` → `"1,234"` ✓ (`int(round(1234))` → `f"{1234:,}"`)
- `_format_value(10000.5)` → `"10,000"` ✓ (Python banker's rounding: `round(10000.5)` → 10000)

**Recommendation:** No action needed.

---

### MAJOR: MIN-004 negative-tier pin is accurate
**File:** tests/unit/ui/test_modifier_impact_grid.py (line 267)
**Category:** accuracy
**Finding:** `test_format_sig_digits_negative_values_use_same_tier_boundaries` — all four assertions match production `_format_sig_digits` using `abs(value)` for tier selection:
- `abs(-1000)` = 1000 ≥ 1000 → `f"{round(-1000)}"` = `"-1000"` ✓
- `abs(-500)` = 500 ≥ 100 → `f"{-500:.1f}"` = `"-500.0"` ✓
- `abs(-5)` = 5 < 10 → `f"{-5:.3f}"` = `"-5.000"` ✓
- `abs(-0.001)` = 0.001 < 10 → `f"{-0.001:.3f}"` = `"-0.001"` ✓

**Recommendation:** No action needed. Pin is accurate.

---

### MAJOR: Faction override behavior accurately pinned
**File:** tests/unit/ui/panels/test_race_identity_panel.py (line 365)
**Category:** accuracy
**Finding:** `test_faction_override_blocks_auto_regen_on_race_name_edit` — accurately pins production `handle_event` logic:
1. `UI_TEXT_ENTRY_CHANGED` on faction input → `_faction_name_overridden = True` ✓
2. Subsequent race-name event → `if not self._faction_name_overridden:` guard skips `_update_faction_if_not_overridden` ✓

**Recommendation:** No action needed.

---

### MAJOR: Government formatting 3-state pin is accurate
**File:** tests/unit/ui/test_race_summary_panel.py (line 548)
**Category:** accuracy
**Finding:** `test_refresh_updates_government_when_org_set` — accurately pins `_format_government_summary` three-state behavior:
- Both type and org set → `"Government: Empire (Centralized)"` ✓
- Type only → `"Government: Empire"` ✓
- Neither set → `"Government: --"` ✓

**Recommendation:** No action needed.

---

## 2. D-009 Fixture Discovery Cost (CRITICAL/MAJOR)

### CRITICAL: _StubShip pins meaningful behavior — tests are substantive
**File:** tests/unit/ui/panels/test_design_stats_panel.py (line 133)
**Category:** d009
**Finding:** `_StubShip` exposes every attribute/method production `DesignStatsPanel` reads (`vehicle_type`, `layers`, `layer_status`, `mass`, `mass_limits_ok`, `max_mass_budget`, `resources`, `get_all_components`, `get_missing_requirements`, `get_validation_warnings`, `get_resource_stat`, `get_total_resource_endurance`, `pod_storage_mass`, `cargo_storage`, `construction_cost`). Tests do verify:
- Vehicle-type section filtering (Drop Pod only shows `main`)
- `needs_rebuild` returning False/True on logistics/section visibility
- Layer row visibility (2 of 4 slots populate for HULL+CORE)
- Requirements HTML rendering ("Need a bridge", "over mass", "CORE over by")
- Requirements clean path ("All met", "No recommendations")
- Collapse/expand toggle per header click
- Click outside headers returns False

**Recommendation:** No action needed — tests are substantive.

---

### MAJOR: No StatRow value-population test after update_stats at panel level
**File:** tests/unit/ui/panels/test_design_stats_panel.py (line 310)
**Category:** d009
**Finding:** `TestDesignStatsPanelUpdateStats` tests deliberately strip `rows_map` to focus on layer_rows and requirements. No test verifies that `update_stats()` actually updates StatRow formatted values, units, and validation status via stat definitions (`stat_def.get_value(ship)`, `stat_def.format_value(val)`, `stat_def.get_display_unit(ship, val)`, `stat_def.get_status(ship, val)`). The `_StubShip` returns 0 from `get_resource_stat()` so even if rows_map were present, the values would be trivial — but the code path should be verified.

**Recommendation:** Add a test that keeps `rows_map` populated and verifies that `row.update(fmt_val, final_unit)` is called with the correct formatted values and units derived from a stub with known resource stats.

---

### MAJOR: needs_rebuild logistics-keys-change path has negative-only coverage
**File:** tests/unit/ui/panels/test_design_stats_panel.py (line 254)
**Category:** d009
**Finding:** `test_needs_rebuild_false_when_logistics_keys_unchanged` only tests that `needs_rebuild` returns False when logistics keys are unchanged. The design.md specifies "needs_rebuild diff (key set vs value change)" as a characterization target. No test covers the True case where logistics keys DO change (e.g., a fuel tank is added, producing a new resource key). The `_StubShip` has `resources.get_resource_names()` returning `[]` which yields no logistics rows, making it impossible to trigger the True case without a subclass.

**Recommendation:** Add a `_ShipWithResource` stub subclass (with `resource_names` that produce logistics rows) and a test verifying `needs_rebuild` returns True after logistics keys change (e.g., stub ship A has keys {X}, stub ship B has keys {X, Y}).

---

### MINOR: rebuild method tested only indirectly
**File:** tests/unit/ui/panels/test_design_stats_panel.py (line 228)
**Category:** d009
**Finding:** `rebuild()` is called indirectly via `_patched_pygame_gui_for_rebuild` in `test_construct_with_none_ship_then_rebuild_populates_rows_map`. No test directly verifies that `rebuild()` replaces an existing layout (kill old scroll container, rebuild sections, etc.).

**Recommendation:** Add a test that constructs with one ship, then calls `rebuild(other_ship)` and verifies the state reflects the second ship's sections.

---

### MAJOR: _patched_pygame_gui_for_rebuild is a reasonable mock
**File:** tests/unit/ui/panels/test_design_stats_panel.py (line 198)
**Category:** d009
**Finding:** The context manager patches `UILabel`, `UIScrollingContainer`, and `UITextBox` with `MagicMock(side_effect=lambda *a, **kw: MagicMock())` for calls after construction. This correctly isolates post-construction widget creation from real pygame_gui initialization while allowing `_build_layout` / `_build_sections` to run their full logic paths.

**Recommendation:** No action needed. Pattern is sound.

---

## 3. MIN-004 Negative-Tier Behavior (MAJOR)

### MAJOR: MIN-004 pin is accurate, but boundary cases are untested
**File:** tests/unit/ui/test_modifier_impact_grid.py (line 267)
**Category:** min004
**Finding:** `test_format_sig_digits_negative_values_use_same_tier_boundaries` accurately pins the observed behavior. However, it only tests one value per tier. The exact tier boundaries — where `abs(value)` changes the precision bucket — are not tested for negative values (e.g., `-10.0` exactly should format as `-10.00` at the ≥10 tier, or `-99.999` rounding behavior). The positive-value precision tier test at line 249 covers these for positives but not negatives.

**Recommendation:** Add negative boundary values to the precision-tier test or extend the negative test: `-10.0` → `"-10.00"`, `-100.0` → `"-100.0"`, `-1000.0` → `"-1000"`, `-9.999` → `"-9.999"` to verify the exact tier transitions.

---

### MINOR: _get_value_color neutral path for set operation is untested
**File:** tests/unit/ui/test_modifier_impact_grid.py (line 300)
**Category:** min004
**Finding:** `test_get_value_color_neutral_for_default_multiply` tests the multiply case at value=1.0. The `_get_value_color` fallback `return self.COLOR_NEUTRAL` (for non-multiply, non-add, e.g., 'set') is never explicitly tested.

**Recommendation:** Add an assertion `grid._get_value_color(1.0, 'set') == grid.COLOR_NEUTRAL` to verify the generic fallback path.

---

## 4. Mocking Discipline (MAJOR/MINOR)

### MAJOR: Multiple vacuous "constructs without error" tests in empire_treasury_panel
**File:** tests/unit/ui/panels/test_empire_treasury_panel.py (line 412)
**Category:** mocking
**Finding:** `test_panel_stores_references` only asserts `panel.panel is mock_panel`, `panel.ui_manager is mock_ui_manager`, etc. — trivially true for any constructor that assigns attributes. `test_scroll_container_created` (line 426) only asserts `mock_container.assert_called_once()` and `panel._scroll_container is not None` — these are pure "didn't crash" tests that verify nothing about business logic.

**Recommendation:** Consider removing these two tests. If retained, mark them as smoke-tests clearly.

---

### MAJOR: Vacuous "didn't raise" tests in race_environment_panel
**File:** tests/unit/ui/test_race_environment_panel.py (line 122)
**Category:** mocking
**Finding:** Four tests in `TestPanelConstruction` verify only that attributes are `not None`:
- `test_panel_has_reproduction_and_happiness_sliders` (line 122)
- `test_panel_has_homeworld_dropdown` (line 129)
- `test_panel_has_points_label` (line 135)
- `test_panel_has_row_for_every_scalar_factor` (line 102) — better, checks IDs ⊆ keys
- `test_panel_has_17_total_rows` (line 116) — better, checks count

However, `test_panel_has_homeworld_dropdown` and `test_panel_has_points_label` are pure "not None" assertions. These would fail identically if the attribute were accidentally deleted from `__init__`, but cannot detect misconfiguration (e.g., wrong text, wrong rect, wrong container).

**Recommendation:** Consolidate into a single `test_construction_attributes_populated` that checks all expected attributes exist, or strengthen individual tests to verify actual values (e.g., `panel.homeworld_dropdown` is an `UIDropDownMenu` mock with correct option list).

---

### MAJOR: update_labels is no-op test is vacuous
**File:** tests/unit/ui/panels/test_race_identity_panel.py (line 309)
**Category:** mocking
**Finding:** `test_update_labels_is_no_op` verifies that calling a method whose body is literally `pass` does not raise. This provides zero behavioral signal.

**Recommendation:** Remove the test. The `hasattr(panel, "update_labels")` contract check (from the race_environment_panel crash fix) could be moved here, but testing `pass` is pointless.

---

### MAJOR: Vacuous has_expected_attributes test in race_summary_panel
**File:** tests/unit/ui/test_race_summary_panel.py (line 159)
**Category:** mocking
**Finding:** `test_race_summary_panel_has_expected_attributes` only checks `hasattr(panel, 'summary_labels')`, `hasattr(panel, 'summary_flag_images')`, `hasattr(panel, 'summary_portrait_image')`, `hasattr(panel, 'summary_ship_images')`. These attributes are unconditionally set in `__init__`. The test provides zero behavioral signal.

**Recommendation:** Remove or replace with a test that verifies post-construction state (e.g., that summary_labels contains expected keys after `_create_content` ran).

---

### MAJOR: Several modifier_impact_grid tests are "doesn't crash" with no behavioral assertions
**File:** tests/unit/ui/test_modifier_impact_grid.py (line 31)
**Category:** mocking
**Finding:** Multiple legacy tests in `TestModifierImpactGrid` are vacuous:
- `test_init_creates_panel` (line 21): asserts `grid.panel is not None` and `grid.rect == rect` — trivial attribute checks.
- `test_update_with_no_component` (line 31): asserts only `grid.current_component is None`.
- `test_update_with_component_no_modifiers` (line 42): asserts only `grid.current_component == mock_component`. The grid also sets `stat_columns=[]`, `modifier_rows=[]`, and renders a "No modifier effects to display" message — none of these are verified.
- `test_kill_cleans_up_elements` (line 164): asserts only `not grid.panel.alive()` after calling `kill()` on a grid with no dynamic UI elements. The `_clear_ui()` path (killing `_ui_elements`) is never exercised because `_build_ui()` spawns one UILabel for the "no effects" message but the assertion doesn't check that path.

**Recommendation:** Strengthen these tests or remove them. For `test_update_with_no_component`, also assert `grid.stat_columns == []` and `grid.modifier_rows == []`. For `test_kill_cleans_up_elements`, seed with UI elements and verify they are killed.

---

### MINOR: Real pygame init mixed with MagicMock in modifier_impact_grid tests
**File:** tests/unit/ui/test_modifier_impact_grid.py (line 194)
**Category:** mocking
**Finding:** `TestPROJ339Characterization` inherits `setup_method` which calls `pygame.init()` and `pygame.display.set_mode((1,1))` — real pygame initialization. But some tests then replace `grid.panel` with a `MagicMock()` (line 330), mixing real and mocked infrastructure. The `test_handle_event_scroll_only_when_mouse_inside_panel_rect` patches `pygame.mouse.get_pos` with MagicMock-style return values alongside the real pygame window.

**Recommendation:** This is acceptable for characterization tests (pinning scroll gating), but fragile. If flakes appear, consider extracting the scroll-gating logic into a pure function that takes mouse position + panel rect as arguments and testing that.

---

### MINOR: race_summary_panel test uses __new__ bypass with manual attribute wiring
**File:** tests/unit/ui/test_race_summary_panel.py (line 338)
**Category:** mocking
**Finding:** `TestFeat14RegistryDrivenSummary._refresh_with_mocked_uilabel` constructs `RaceSummaryPanel` via `__new__` + manual attribute wiring (lines 362-382) rather than using `_make_summary_panel` / `make_ui_widget`. This duplicates the bypass-init pattern instead of reusing the shared factory.

**Recommendation:** Refactor to use `make_ui_widget` or extract a helper that calls `make_ui_widget` and then sets up the env scroll container. The current pattern is fragile against __init__ signature changes.

---

## 5. Test Naming (MINOR)

### MINOR: Vague test name — "has expected attributes"
**File:** tests/unit/ui/test_race_summary_panel.py (line 159)
**Category:** naming
**Finding:** `test_race_summary_panel_has_expected_attributes` does not specify which attributes are expected. A reader must inspect the test body to know.

**Recommendation:** Rename to `test_race_summary_panel_has_summary_collections_initialized` or similar.

---

### MINOR: Vague test name — "stores references"
**File:** tests/unit/ui/panels/test_empire_treasury_panel.py (line 412)
**Category:** naming
**Finding:** `test_panel_stores_references` does not specify what references. This test is vacuous anyway (see mocking finding).

**Recommendation:** Remove the test entirely. If kept, rename to `test_constructor_assigns_all_arguments_to_attributes`.

---

### MINOR: Imprecise test name — "has row for every scalar factor"
**File:** tests/unit/ui/test_race_environment_panel.py (line 102)
**Category:** naming
**Finding:** `test_panel_has_row_for_every_scalar_factor` — slightly imprecise. The test verifies scalar_ids ⊆ preference_rows keys, which is "has at least one row per scalar factor" rather than "a separate row for each."

**Recommendation:** Rename to `test_panel_has_preference_row_for_every_scalar_factor` for clarity.

---

## 6. Missing Edge Cases (MAJOR)

### MAJOR: design_stats_panel — needs_rebuild logistics change True path not covered
**File:** tests/unit/ui/panels/test_design_stats_panel.py (line 251)
**Category:** missing-coverage
**Finding:** The design.md specifies `needs_rebuild` diff as a characterization target. Only the negative case (False) is tested (`test_needs_rebuild_false_when_logistics_keys_unchanged`). The positive case — where `new_log_keys != self.current_logistics_keys` causes `needs_rebuild` to return True — has no coverage.

**Recommendation:** Create a `_ShipWithCargo` stub subclass where `resources.get_resource_names()` returns a non-empty list, then verify that `needs_rebuild` returns True when switching from a ship with no cargo resources to one with cargo resources.

---

### MAJOR: design_stats_panel — StatRow value population through update_stats not tested at panel level
**File:** tests/unit/ui/panels/test_design_stats_panel.py (line 310)
**Category:** missing-coverage
**Finding:** The `TestDesignStatsPanelUpdateStats` tests deliberately drop `rows_map` to isolate layer/requirements paths. No test verifies that `update_stats` correctly populates StatRow formatted values, units, and validation status via the stat-definition pipeline (`stat_def.get_value(ship)` → `stat_def.format_value(val)` → `stat_def.get_display_unit(ship, val)` → `stat_def.get_status(ship, val)`).

**Recommendation:** Add a test that keeps `rows_map` populated (construct with a ship that produces stat rows), calls `update_stats`, and verifies that StatRow `.update(fmt_val, final_unit)` was called with correct formatted values. Use `_StubShip` subclass with known `get_resource_stat` return values.

---

### MAJOR: design_stats_panel — kill method not tested at panel level
**File:** tests/unit/ui/panels/test_design_stats_panel.py
**Category:** missing-coverage
**Finding:** `DesignStatsPanel.kill()` (production line 507) is never tested. It kills the scroll container and resets `rows_map`/`layer_rows`/`req_box_left`/`req_box_right`.

**Recommendation:** Add a test: construct a panel with a ship, call `kill()`, verify `stats_scroll` is None and `rows_map` is empty.

---

### MAJOR: modifier_impact_grid — handle_event non-mousewheel path untested
**File:** tests/unit/ui/test_modifier_impact_grid.py
**Category:** missing-coverage
**Finding:** `handle_event` has a single `if event.type == pygame.MOUSEWHEEL:` branch with no else. The `return False` path for non-mousewheel events (e.g., key events forwarded to the grid) is never tested.

**Recommendation:** Add a test: `grid.handle_event(MagicMock(type=pygame.KEYDOWN))` → `assert False`.

---

### MAJOR: modifier_impact_grid — set_position untested
**File:** tests/unit/ui/test_modifier_impact_grid.py
**Category:** missing-coverage
**Finding:** `set_position()` (production line 511) has no test coverage.

**Recommendation:** Add a test: construct a grid, call `set_position((100, 200))`, verify `grid.rect.topleft == (100, 200)` and `grid.panel.set_position.assert_called_with((100, 200))`.

---

### MAJOR: modifier_impact_grid — _format_sig_digits boundary values not tested
**File:** tests/unit/ui/test_modifier_impact_grid.py (line 249)
**Category:** missing-coverage
**Finding:** `test_format_sig_digits_precision_tiers_for_positive_values` tests mid-tier values (10, 99, 100, 999, 1000, 1500) but not exact tier boundaries and their rounding behavior. Values like `9.999` (should use 3dp tier → `"9.999"`), `9.9995` (rounding to `"10.00"` at 2dp tier), `99.95` (should render as `"100.0"` at 1dp tier), `999.5` (should render as `"1000"` at 0dp tier) are not tested.

**Recommendation:** Add boundary/rounding edge case assertions to the existing tier test.

---

### MAJOR: modifier_impact_grid — _get_rotated_header cache untested
**File:** tests/unit/ui/test_modifier_impact_grid.py
**Category:** missing-coverage
**Finding:** `_get_rotated_header()` has a `self._header_cache` dictionary that caches pygame surfaces. No test verifies the caching behavior.

**Recommendation:** Since `draw()` is accepted as uncovered (D-004), and `_get_rotated_header` is primarily exercised through `draw()`, this gap is acceptable. However, a unit test that first calls `_get_rotated_header("Test")`, verifies the surface, then patches the font render to raise, and calls again to verify the cached surface is returned, would be ideal.

---

### MAJOR: modifier_impact_grid — _format_value unknown operation fallback untested
**File:** tests/unit/ui/test_modifier_impact_grid.py (line 237)
**Category:** missing-coverage
**Finding:** `_format_value` has a `return str(value)` fallback at line 271 for operations other than 'multiply', 'add', or 'set'. This path is never tested.

**Recommendation:** Add: `grid._format_value(5.0, 'unknown') == "5.0"`.

---

### MAJOR: race_summary_panel — _build_sections for Drop Pod coverage
**File:** tests/unit/ui/test_design_stats_panel.py (line 294)
**Category:** missing-coverage
**Finding:** The Drop Pod test only asserts that `crewlogistics` and `logistics` are absent from `visible_section_keys`. It does not verify that the Drop Pod's always-visible section list (`['main']`) correctly resolves, nor that all Ship-only sections are absent (e.g., `weapons`, `maneuvering`, `shields`, `armor`, `targeting`, `fightersupport`).

**Recommendation:** Expand the test with `assert 'weapons' not in panel.visible_section_keys`, `assert 'maneuvering' not in panel.visible_section_keys`, etc., for the full set of Ship-exclusive sections, or verify that only `'main'` is present.

---

### MAJOR: race_environment_panel — handle_dropdown_change untested
**File:** tests/unit/ui/test_race_environment_panel.py
**Category:** missing-coverage
**Finding:** The design.md lists `handle_dropdown_change` as a public method. Production line 300 handles the dropdown change event, resolving the selected preset name and calling `apply_homeworld_preset`. No test exercises this method.

**Recommendation:** Add a test: mock `homeworld_dropdown.selected_option` to return a known preset name, create a `MagicMock` event with `ui_element` pointing to the dropdown mock, call `panel.handle_dropdown_change(event)`, and verify `apply_homeworld_preset` was called with the correct preset ID.

---

### MINOR: race_summary_panel — handle_button_click for Randomize All button untested
**File:** tests/unit/ui/test_race_summary_panel.py (line 709)
**Category:** missing-coverage
**Finding:** `TestPROJ339HandleButtonClick` tests the Load Race callback path but does not test the Randomize All callback (FEAT-12, `on_randomize_all_callback`, `btn_randomize_all`). Production `handle_button_click` only handles Load, so this is a production gap (Randomize All button exists but has no click handler in the panel). However, the test doesn't document this.

**Recommendation:** Add a note in the test class documenting that `btn_randomize_all` is not handled by `handle_button_click` (the parent screen likely subscribes directly).

---

### MINOR: race_environment_panel — apply_homeworld_preset does not test set_from_config call
**File:** tests/unit/ui/test_race_environment_panel.py (line 220)
**Category:** missing-coverage
**Finding:** `test_apply_continental_overrides_relevant_factors` verifies the mutation on `race_config` but does not verify that `set_from_config()` was called to push the preset's values back into the UI widgets. Production line 298 calls `self.set_from_config()` after `apply_preset_to_config`.

**Recommendation:** Since `set_from_config` calls are verified separately in `TestSetFromConfig`, this gap is minor. But ideally, the test should verify that after `apply_homeworld_preset("CONTINENTAL")`, each `PreferenceRow.set_preference()` was called on the matching rows.

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| MAJOR    | 18 |
| MINOR     | 6 |

**CRITICAL findings:** 1
- _StubShip pins meaningful behavior — confirmed substantive (categories: d009)

**MAJOR findings:** 18
- Behavior accuracy: 5 (all confirmed accurate — informational)
- No StatRow value-population test at panel level (d009)
- needs_rebuild logistics change True path exposed but not tested (d009)
- _patched_pygame_gui_for_rebuild is reasonable (d009, informational)
- MIN-004 boundary cases untested for negatives (min004)
- min004 _get_value_color neutral path for set untested (min004)
- 3 vacuous "doesn't crash" tests in empire_treasury_panel (mocking)
- 4 vacuous "not None" tests in race_environment_panel (mocking)
- update_labels no-op test is vacuous (mocking)
- has_expected_attributes test is vacuous (mocking)
- 4 vacuous tests in modifier_impact_grid (mocking)
- needs_rebuild logistics change True (missing-coverage)
- StatRow value population (missing-coverage)
- kill method (missing-coverage)
- handle_event non-mousewheel path (missing-coverage)
- set_position (missing-coverage)
- _format_sig_digits boundaries (missing-coverage)
- _format_value unknown op fallback (missing-coverage)
- Drop Pod full section exclusion (missing-coverage)
- handle_dropdown_change (missing-coverage)

**MINOR findings:** 6
- rebuild tested only indirectly (d009)
- Real pygame init mixed with MagicMock (mocking)
- race_summary_panel __new__ pattern (mocking)
- 3 vague/loose test names (naming)
- Randomize All callback not tested (missing-coverage)
- apply_homeworld_preset set_from_config verification (missing-coverage)
