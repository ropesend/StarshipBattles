# PROJ-339 Phase 1 — UI panels characterization

**Status:** Pending
**Goal:** Add ~22-30 NEW characterization tests across 6 panel test files.
Each item maps to a specific behavior surfaced in the per-file analysis.

> Convention: every checkbox below is a NEW test to write. Pre-existing tests
> are NOT listed; they are verified intact in the tail item.

---

## File 1: `game/ui/panels/race_summary_panel.py`

**Test file:** `tests/unit/ui/test_race_summary_panel.py`
**New tests:** 4-6

### Top 3 (guaranteed)

- [ ] `test_refresh_updates_government_when_org_set` — after mutating
      `RaceConfig.government_type` and `government_organization`, `refresh()`
      renders both values; with org unset, only the type is rendered; with
      neither, the placeholder is rendered.
- [ ] `test_rebuild_env_scroll_content_filters_zero_setpoint_gas_factors` —
      one row per scalar factor always; gas factors with `setpoint <= 0`
      excluded; both derived seeds (`base_happiness`, `base_reproduction_rate`)
      always present.
- [ ] `test_handle_button_click_invokes_load_callback_only_when_btn_load` —
      callback fires only when the clicked element is `btn_load` AND
      `on_load_race_callback` is bound; other elements are no-ops.

### Gap-fillers

- [ ] `test_refresh_ship_preview_skips_when_theme_unset` — falsy `theme_id`
      → no ship preview images attached.
- [ ] `test_refresh_ship_preview_skips_category_when_surface_missing` —
      `ShipThemeManager` returns `None` for a category → that slot is empty,
      others render.
- [ ] `test_rebuild_env_scroll_content_renders_dash_for_missing_preference` —
      preference id absent from `RaceConfig.preferences` → row renders `--`.

---

## File 2: `game/ui/panels/design_stats_panel.py`

**Test file:** `tests/unit/ui/panels/test_design_stats_panel.py`
**New tests:** 8-10 (the biggest lift)

### Top 3 (guaranteed)

- [ ] `test_construct_with_none_ship_then_rebuild_populates_rows_map` —
      construct with `ship=None` (empty `rows_map`); call
      `rebuild(real_ship)`; `rows_map` becomes populated.
- [ ] `test_needs_rebuild_true_on_logistics_key_diff_false_on_value_change` —
      ship logistics key set changes → `needs_rebuild()` True; only values
      change → False.
- [ ] `test_update_stats_populates_layer_rows_and_hides_unused_slots` —
      layer rows visible only for layers in `ship.layers`; remaining slots
      hidden.

### Happy

- [ ] `test_build_layout_filters_sections_by_vehicle_type` —
      `resolve_section_visibility` skips sections whose `vehicle_type` does
      not match the ship's.
- [ ] `test_show_requirements_false_omits_textboxes` —
      `show_requirements=False` at construction → no req/recs textboxes built.

### Unhappy / Corner

- [ ] `test_update_stats_requirements_lists_missing_and_mass_overflow` —
      missing requirements rendered red; over-budget mass appends one entry;
      each over-budget layer appends one entry.
- [ ] `test_update_stats_requirements_clean_renders_all_met` — no missing
      reqs, mass within budget, all layers within → "✓ All met".
- [ ] `test_collapsed_section_hides_stat_rows_and_toggles_arrow` — toggling
      a section in `collapsed_sections` hides its rows; arrow flips
      `▶` ↔ `▼`.
- [ ] `test_needs_rebuild_true_on_visible_section_keys_change` — sections
      appearing / disappearing across updates trigger rebuild.
- [ ] `test_handle_event_collapse_click_updates_collapsed_sections` —
      simulated arrow-click event mutates `collapsed_sections` set.

---

## File 3: `game/ui/panels/modifier_impact_grid.py`

**Test file:** `tests/unit/ui/test_modifier_impact_grid.py`
**New tests:** 4-6

### Top 3 (guaranteed)

- [ ] `test_update_filters_columns_to_consumed_stats` — Bridge component
      (universal + bridge-binding stats) does NOT include weapon-binding
      stats in `stat_columns`.
- [ ] `test_format_value_prefixes_per_operation` — `(1.5, "multiply")` →
      `"x1.500"`; `(50, "add")` → `"+50.00"`; `(-1, "add")` → `"-1.000"`;
      assignment operation uses `"="` prefix.
- [ ] `test_format_sig_digits_precision_tiers` — `≥1000` no decimals;
      `100-999` one dp; `10-99` two dp; `<10` three dp; `0` → `"0"`.

### Gap-fillers

- [ ] `test_update_with_none_clears_columns_and_rows` — `update(None)` →
      `stat_columns == []`, `modifier_rows == []`.
- [ ] `test_get_value_color_neutral_for_default_multiply` — multiply value
      exactly `1.0` (within 0.001 tolerance) classifies as neutral and is
      excluded by `_get_affected_stats`.
- [ ] `test_handle_event_scroll_only_when_mouse_inside_panel_rect` —
      mousewheel event with cursor outside `rect` → no scroll; inside →
      scroll applied.

---

## File 4: `game/ui/panels/race_identity_panel.py`

**Test file:** `tests/unit/ui/panels/test_race_identity_panel.py`
**New tests:** 2-3

### Top 3 (guaranteed)

- [ ] `test_auto_generate_faction_name_quadrants` — `("Rossarian", "Empire")`
      → `"Rossarian Empire"`; race-only → race form; gov-only → gov form;
      neither → empty.
- [ ] `test_faction_override_blocks_auto_regen_on_race_name_edit` —
      after a faction text-changed event, `_faction_name_overridden` is
      True; subsequent race-name edits do NOT mutate the faction input.
- [ ] `test_set_from_config_recreates_dropdowns_with_new_starting_option` —
      `set_from_config(new_config)` produces 5 fresh dropdown instances
      (pygame_gui has no in-place starting-option setter).

### Gap-fillers

- [ ] `test_get_dropdown_value_treats_empty_option_as_blank` —
      `EMPTY_OPTION` selection → returned as `""`.
- [ ] `test_set_from_config_does_not_set_override_when_loaded_matches_auto` —
      loading a config whose faction_name equals the auto-generated value
      does NOT flip `_faction_name_overridden` to True.

---

## File 5: `game/ui/panels/race_environment_panel.py`

**Test file:** `tests/unit/ui/test_race_environment_panel.py`
**New tests:** 2-3

### Top 3 (guaranteed)

- [ ] `test_init_constructs_one_row_per_factor` — total `PreferenceRow`
      count equals `len(iter_scalar_factors()) + len(iter_gas_factors())`
      (17).
- [ ] `test_update_config_writes_every_row_back_to_preferences` —
      mutating each row's current value and calling `update_config` writes
      every value into `race_config.preferences`, plus repro + happiness
      slider values.
- [ ] `test_handle_dropdown_change_homeworld_applies_preset_and_refreshes` —
      selecting a homeworld preset triggers `apply_homeworld_preset`
      followed by `set_from_config` (rows refreshed).

### Gap-fillers

- [ ] `test_apply_homeworld_preset_unknown_id_is_silent_noop` — passing
      an id not in the preset registry returns without raising.
- [ ] `test_apply_homeworld_preset_custom_is_noop` — passing `"(Custom)"`
      makes no mutations to `race_config`.
- [ ] `test_update_points_display_swallows_exceptions` — patch
      `RacePointBudget` to raise; method logs warning and sets text to `""`.

---

## File 6: `game/ui/panels/empire_treasury_panel.py`

**Test file:** `tests/unit/ui/panels/test_empire_treasury_panel.py`
**New tests:** 2

### Top 3 (guaranteed — note: 2 of the 3 align with new tests; one is
already covered by existing suite)

- [ ] `test_format_value_zero_thousands_and_rounding` — `0` → `"0"`;
      `1234` → `"1,234"`; `10000.5` → `"10,000"` (rounded).
- [ ] `test_upkeep_row_only_when_any_positive_value` — empty / all-zero
      upkeep → no row; ≥1 positive → row inserted (negated values)
      immediately before the "Total" expenses row.

### Gap-fillers (covered by existing tests for top-3 #3 — refresh rebuild)

- [ ] `test_build_resource_header_skips_missing_icon` — resource id absent
      from `resource_icons` dict → header rendered without icon, no error.

---

## Tail items

- [ ] **Verify pre-existing ~93 tests still green:**
      `pytest tests/unit/ui/panels/ tests/unit/ui/test_race_summary_panel.py tests/unit/ui/test_modifier_impact_grid.py tests/unit/ui/test_race_environment_panel.py -x -q`.
- [ ] **Full sharded suite green:**
      `python Tools/test_sharded/test_sharded.py`.
- [ ] **Lint clean:** `python Tools/lint_test_files.py` reports 0 violations.
- [ ] **Zero production diff:** `git diff --stat game/` is empty.

## Phase Completion

- [ ] All file-1..file-6 boxes ticked (or explicitly deferred with rationale
      added to `decisions.md`).
- [ ] Tail items all green.
- [ ] Commit per-file as `test(339): characterize <panel_name>` so bisect
      can isolate any future regression to its panel.
- [ ] Update `Projects/projects_index.md` PROJ-339 → Awaiting Verification.
