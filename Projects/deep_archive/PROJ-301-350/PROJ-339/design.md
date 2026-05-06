# PROJ-339: Design notes

> Architecture context for the 6 panel files, plus testability blockers and
> the resolved fixture strategy. Read this before opening
> `phase_1_checklist.md`.

## Architecture context

| Panel | Host scene / window | Data it receives |
|-------|---------------------|------------------|
| `race_summary_panel` | `RaceSetupScreen` → `race_setup/panel_factory` | `RaceConfig`, `RaceAssetLoader`, optional callbacks (`on_load_race_callback`) |
| `race_identity_panel` | `RaceSetupScreen` → `race_setup/panel_factory` | `RaceConfig` |
| `race_environment_panel` | `RaceSetupScreen` → `race_setup/panel_factory` | `RaceConfig`, `RacePointBudget` |
| `design_stats_panel` | `DesignWorkshopScreen.builder` right panel + `BuildQueueWindow` | `Ship` (optional at construction) + `show_requirements` flag |
| `modifier_impact_grid` | `DesignWorkshopScreen.workshop_event_router` | `Component` (or `None`) via `update()` |
| `empire_treasury_panel` | `EmpirePanelWindow` (Treasury tab) | `EmpireEconomySnapshot` + module-level `resource_icons` dict |

All six panels are leaf widgets composed into windows / scenes that own their
`UIManager`. None of the six own a `UIManager` directly.

## Per-file public APIs (characterization targets)

### `race_summary_panel.py`
- Public: `__init__`, `refresh`, `handle_button_click`.
- Private formatters / renderers: `_format_*`, `_render_*`, `_refresh_*`,
  `_rebuild_env_scroll_content`, `_refresh_ship_preview`.
- Data binding: `RaceConfig` (race name, government, physical, society,
  faction, theme, preferences, aptitudes, descriptions), `RaceAssetLoader`
  (flag/portrait surfaces), `ShipThemeManager` singleton (ship preview).

### `design_stats_panel.py`
- Public: `__init__`, `_build_layout`, `update_stats`, `needs_rebuild`,
  `rebuild`, `kill`, `handle_event`. `StatRow` helper (already tested).
- Data binding: `Ship` (`vehicle_type`, `layers`, `layer_status`, `mass`,
  `mass_limits_ok`, `max_mass_budget`, `get_missing_requirements`,
  `get_validation_warnings`). Pulls `SECTIONS_CONFIG` + `SECTION_GENERATORS`
  from `stats_config`.
- Mutable state: `collapsed_sections`, `current_logistics_keys`,
  `visible_section_keys`.

### `modifier_impact_grid.py`
- Public: `__init__`, `update`, `draw`, `handle_event`, `kill`, `set_position`.
- Helpers: `_get_affected_stats`, `_format_stat_name`, `_format_value`,
  `_format_sig_digits`, `_get_value_color`.
- Data binding: `Component.get_modifier_stat_summary`, `get_all_modifier_effects`,
  `ability_instances` + each ability's `STAT_BINDINGS`.

### `race_identity_panel.py`
- Public: `__init__`, `update_config`, `set_from_config`, `update_labels`
  (no-op), `handle_event`.
- Helpers: `_auto_generate_faction_name`, `_get_dropdown_value`,
  `_recreate_dropdown`.
- Special invariant: `_faction_name_overridden` flag tracks whether the user
  has manually edited the faction name; subsequent race-name / government
  edits skip auto-regen iff this flag is set.

### `race_environment_panel.py`
- Public: `__init__`, `update_config`, `update_labels`, `set_from_config`,
  `apply_homeworld_preset`, `handle_dropdown_change`.
- Helpers: `_on_row_change`, `_update_points_display`, `_format_reproduction`.
- Construction creates one `PreferenceRow` per `iter_scalar_factors()` (7) +
  per `iter_gas_factors()` (10) entry — 17 rows total.

### `empire_treasury_panel.py`
- Public: `__init__`, `refresh`. Helpers: `_format_value`, row-builders,
  module-level `load_resource_icons`.
- Data binding: `EmpireEconomySnapshot` (colony / ship / trade / tribute /
  mining production, tribute / construction expenses, total_population_upkeep,
  net / current / max storage), `_PLANETARY_IDS` (5 resource IDs).

## Testability blockers (resolved strategy)

### `race_summary_panel._refresh_ship_preview`
- **Blocker:** Depends on `get_default_ship_theme_manager()` singleton and
  `pygame.transform.smoothscale` on real surfaces.
- **Resolution:** Reuse the existing mock pattern in
  `tests/unit/ui/test_race_summary_panel.py` — patch
  `get_default_ship_theme_manager` to return a stub returning known surfaces.

### `design_stats_panel._build_layout`
- **Blocker:** Requires a real `UIScrollingContainer` with a working
  `get_container().get_rect()`.
- **Resolution:** Instantiate against a real `UIManager` as the existing
  `tests/unit/ui/panels/` tests already do. The fixture infrastructure exists.

### `modifier_impact_grid.draw`
- **Blocker:** Writes directly to a pygame Surface; pinning rendered output
  is impractical without a snapshot framework.
- **Resolution:** Per D-004, pin the **data preparation** in `update()` and
  the **formatting helpers** (`_format_value`, `_format_sig_digits`,
  `_get_value_color`); treat `draw()` as glue and accept it stays uncovered.

### `empire_treasury_panel`
- **Blocker:** `ResourceCatalog.from_json()` runs at module import time —
  needs the real catalog file present.
- **Resolution:** The catalog file ships in the repo; existing tests already
  import the module successfully. No mock needed.

## Files needing only minimal new coverage (2-3 each)

- `race_identity_panel.py` — already 17 tests; add 2-3 corner cases (dropdown
  empty starting option, faction-override detection on `set_from_config`).
- `race_environment_panel.py` — already 18 tests; add 2-3 unhappy-path tests
  (preset-not-found, points-display exception swallow).
- `empire_treasury_panel.py` — already 19 tests; add 2 corner cases
  (icon-missing skip, `_format_value` rounding boundary).

## Files needing significant new coverage (the "big lifts")

- `design_stats_panel.py` — **8-10 NEW tests**. Panel-level construction,
  `_build_layout` against a real container, `needs_rebuild` diff (key set
  vs value change), `update_stats` layer population, requirements textbox
  rendering, collapse / expand toggling.
- `modifier_impact_grid.py` — **4-6 NEW tests**. Consumed-stats filter
  (universal vs binding stats), `_format_sig_digits` precision tiers (4
  buckets), `_get_value_color` neutral path, scroll gating by mouse rect.

## Conventions reminders

- Public functions and methods need return-type annotations (`docs/03_CONVENTIONS.md` §key conventions).
- Test files stay under the LOC limits enforced by `Tools/lint_test_files.py`.
- Reuse existing pygame_gui mock fixtures; do not invent new ones.
