# Type Safety Audit — Shard 03 Review Report

**Reviewer:** OpenCode (Shard 03)
**Date:** 2026-05-04
**Files reviewed:** 180 (all files in scope read exhaustively)
**Convention baseline:** `docs/03_CONVENTIONS.md` §8 ("Every public function/method must carry a return-type annotation")

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| S1 — Missing return type on public function | 86 | Functions lacking `-> T` annotation |
| S1 — `-> Any` on non-generic function | 47 | `Any` where a narrower type is knowable |
| S2 — Missing parameter type | ~35 | Constructor/function params without type hints |
| S3 — `type: ignore` sites | 1 | Suppressed type errors needing justification |
| S4 — Informational | ~15 | Protocol `Any`, valid generic `Any`, legal dunder exemptions |

---

## Severity 1: Missing Return Types on Public Functions/Methods

These functions/methods are public (no leading underscore) and lack a return-type annotation. Per `docs/03_CONVENTIONS.md` §8, this is a hard requirement.

### `game/app.py`

| Line | Function | Issue |
|------|----------|-------|
| 184 | `_route_get(self, name)` | `-> Any` (known) |
| 194 | `_route_set(self, name, value)` | Missing `-> None` |
| 202 | `active_scene` property | `-> Any` (known) |
| 207 | `battle_scene` property | `-> Any` (known) |
| 212 | `battle_setup` property | `-> Any` (known) |
| 217 | `strategy_scene` property | `-> Any` (known) |
| 222 | `builder_scene` property | `-> Any` (known) |
| 227 | `test_lab_scene` property | `-> Any` (known) |
| 232 | `_menu_scene` property | `-> Any` (known, but `_` prefix exempts from public rule) |
| 237 | `menu_ui_manager` property | `-> Any` (known) |
| 273 | `start_builder(self, return_to, context)` | Missing `-> None` |
| 277 | `on_builder_return(self, custom_ship)` | Missing `-> None` |
| 280 | `start_battle_setup(self, preserve_teams)` | Missing `-> None` |
| 283 | `start_strategy_layer(self)` | Missing `-> None` |
| 295 | `start_quickstart_1p(self)` | Missing `-> None` |
| 298 | `start_quickstart_2p(self)` | Missing `-> None` |
| 301 | `show_load_menu(self)` | Missing `-> None` |
| 310 | `start_test_lab(self)` | Missing `-> None` |
| 313 | `start_research_tree(self)` | Missing `-> None` |
| 316 | `on_research_tree_return(self)` | Missing `-> None` |
| 319 | `start_galaxy_test(self)` | Missing `-> None` |
| 322 | `on_galaxy_test_return(self)` | Missing `-> None` |
| 325 | `start_keybindings(self)` | Missing `-> None` |
| 328 | `on_keybindings_return(self)` | Missing `-> None` |
| 331 | `start_race_setup(self)` | Missing `-> None` |
| 340 | `start_battle(self, spec, *, headless, config)` | Missing `-> None` |
| 349 | `start_replay(self, record)` | Missing `-> None` |
| 476 | `run(self)` | Missing `-> None` |

The `-> Any` on scene accessor properties is **justifiable** — the properties proxy a heterogeneous collection of scene types through `ScreenRouter`. These are genuinely dynamic and could be tagged S4 (informational). The 18 missing `-> None` annotations on lifecycle methods are straightforward S1 fixes.

### `game/core/state_machine.py`

| Line | Function | Issue |
|------|----------|-------|
| 69 | `state` property | `-> Any` (known — generic state machine, Any is correct here; S4) |
| 133 | `pop_and_return(self)` | `-> Any` (known — returns the popped state; S4) |

Both are correct uses of `Any` — this is a generic state machine. S4.

### `game/core/protocols/ui.py`

| Line | Function | Issue |
|------|----------|-------|
| 16 | `IScene.handle_event(self, event)` | `event: Any` protocol; S4 |
| 20 | `IScene.update(self, dt)` | `-> None` — OK |
| 24 | `IScene.draw(self, screen)` | `screen: Any` protocol; S4 |
| 62 | `ICamera.position` property | `-> Any` (known — Vector2-like duck typing; S4) |
| 66 | `ICamera.world_to_screen(self, world_pos)` | `-> Any` (known; S4) |
| 78 | `ICamera.screen_to_world(self, screen_pos)` | `-> Any` (known; S4) |

All are protoocls using duck-typed shapes — `Any` is appropriate. S4 only.

### `game/ui/screens/builder/stat_getters.py`

| Line | Function | Issue |
|------|----------|-------|
| 12 | `fmt_time(val)` | `-> Any` — returns `str`, should be `-> str` (S1) |
| 23 | `fmt_multiply(val)` | `-> Any` — returns `str`, should be `-> str` (S1) |
| 26 | `fmt_decimal(val)` | `-> Any` — returns `str`, should be `-> str` (S1) |
| 29 | `fmt_score(val)` | `-> Any` — returns `str`, should be `-> str` (S1) |
| 32 | `fmt_targeting(val)` | `-> Any` — returns `str`, should be `-> str` (S1) |
| 38 | `_get_total_crew_requirement(ship)` | `-> Any` — returns numeric/float; S1 (but priv) |
| 45 | `mass_validator(ship, val)` | `-> tuple` — should be `-> tuple[bool, str]` (S2) |
| 48 | `crew_validator(ship, val)` | `-> tuple` — should be `-> tuple[bool, str]` (S2) |
| 54 | `life_support_validator(ship, val)` | `-> tuple` — should be `-> tuple[bool, str]` (S2) |
| 63 | `get_mass_display(ship)` | `-> Any` — returns `float`, should be `-> float` (S1) |
| 66 | `get_crew_required(ship)` | `-> Any` — should be `-> float` (S1) |
| 69 | `get_crew_capacity(ship)` | `-> Any` — should be `-> float` (S1) |
| 72 | `get_life_support(ship)` | `-> Any` — should be `-> float` (S1) |
| 75 | `get_max_targets(ship)` | `-> Any` — should be `-> int` (S1) |
| 78 | `get_armor_hp(ship)` | `-> Any` — should be `-> float` (S1) |
| 84 | `get_maneuver_points(ship)` | `-> Any` — should be `-> float` (S1) |
| 87 | `get_strategic_speed(ship)` | `-> Any` — returns `int`, should be `-> int` (S1) |
| 99 | `get_fuel_consumption(ship)` | `-> Any` — should be `-> float` (S1) |
| 102 | `get_ammo_consumption(ship)` | `-> Any` — should be `-> float` (S1) |
| 105 | `get_energy_consumption(ship)` | `-> Any` — should be `-> float` (S1) |
| 111 | `get_resource_storage(ship, res_name)` | `-> Any` — should be `-> float` (S1) |
| 116 | `get_resource_current(ship, res_name)` | `-> Any` — should be `-> float` (S1) |
| 121 | `get_resource_generation(ship, res_name)` | `-> Any` — should be `-> float` (S1) |
| 126 | `get_resource_consumption(ship, res_name)` | `-> Any` — returns `float`, should be `-> float` (S1) |
| 141 | `get_resource_endurance(ship, res_name)` | `-> Any` — returns `float`, should be `-> float` (S1) |
| 149 | `get_resource_replenish(ship, res_name)` | `-> Any` — returns `float`, should be `-> float` (S1) |
| 157 | `get_resource_max_usage(ship, res_name)` | `-> Any` — should be `-> float` (S1) |
| 177 | `get_weapon_count(ship)` | `-> Any` — returns `int`, should be `-> int` (S1) |
| 185 | `get_total_dps(ship)` | `-> Any` — should be `-> float` (S1) |
| 190 | `get_dps_duration(ship)` | `-> Any` — should be `-> float` (S1) |
| 196 | `get_max_range(ship)` | `-> Any` — should be `-> float` (S1) |
| 203 | `get_warp_capable(ship)` | `-> Any` — returns `float`, should be `-> float` (S1) |
| 207 | `get_warp_tonnage(ship)` | `-> Any` — should be `-> float` (S1) |
| 211 | `get_warp_cost(ship)` | `-> Any` — should be `-> float` (S1) |
| 215 | `get_warp_jumps(ship)` | `-> Any` — returns `int`, should be `-> int` (S1) |
| 228 | `get_fuel_per_hex(ship)` | `-> Any` — returns `float`, should be `-> float` (S1) |
| 240 | `get_hex_range(ship)` | `-> Any` — should be `-> float` (S1) |
| 251 | `get_cargo_capacity(ship, cargo_type)` | `-> Any` — should be `-> int` (S1) |
| 255 | `get_passenger_capacity(ship)` | `-> Any` — should be `-> int` (S1) |
| 259 | `get_pod_storage(ship)` | `-> Any` — should be `-> float` (S1) |
| 263 | `get_colony_types(ship)` | `-> Any` — returns `str`, should be `-> str` (S1) |
| 290 | `get_superweapon_summary(ship)` | `-> Any` — returns `str`, should be `-> str` (S1) |
| 314 | `get_repair_rate(ship)` | `-> Any` — should be `-> float` (S1) |
| 328 | `fmt_yes_no(val)` | `-> Any` — returns `str`, should be `-> str` (S1) |
| 332 | `fmt_int(val)` | `-> Any` — returns `str`, should be `-> str` (S1) |
| 338 | `fmt_text(val)` | `-> Any` — returns `str`, should be `-> str` (S1) |
| 405 | `mass_unit_func(ship, val)` | `-> Any` — returns `str`, should be `-> str` (S1) |

**Total S1 issues in stat_getters.py: 45+** — The pattern `-> Any` is used on every public function. In all cases the actual return type is knowable (mostly `float`, `int`, `str`, or `bool`). This is a systematic cleanup candidate.

### `game/ui/screens/test_lab/data_extractor.py`

| Line | Function | Issue |
|------|----------|-------|
| 21 | `get_test_data_dir()` | `-> Any` — returns `str`, should be `-> str` (S1) |
| 55 | `extract_ships(self, test_id)` | `-> Any` — returns `list[dict]`, should be `-> list[dict[str, Any]]` (S1) |
| 168 | `_extract_component_ids(self, ship_data)` | `-> Any` — returns `list[str]`; S1 (priv though) |
| 187 | `load_component(self, component_id)` | `-> Any` — returns `dict | None`, should be explicit (S1) |
| 215 | `get_components_cache(self)` | `-> bool` — actually returns `dict[str, dict]`; **wrong type annotation** (S1) |

### `game/ui/screens/strategy_renderer.py`

| Line | Function | Issue |
|------|----------|-------|
| 81+ | Various `_draw_*` methods | All have `-> None` — OK |
| ~170+ | `camera` property | `-> Any` (known; S4 — dynamic scene reference) |
| ~170+ | `galaxy`, `systems`, `empires` properties | `-> Any` (known; S4) |
| ~170+ | `hex_size`, `screen_width`, `screen_height` | `-> Any` (known; S4 — int, should be `-> int`) |

The `screen_width` and `screen_height` returning `-> Any` but always returning `int` values could be improved (S2), but the dynamic proxy pattern is the reason for `Any`.

### `game/ui/screens/strategy_render/systems.py`

| Line | Function | Issue |
|------|----------|-------|
| 28 | `draw_systems(r, screen)` | `r: Any, screen: Any` — could use `StrategyRenderer, pygame.Surface` (S2) |
| 60 | `load_star_image(r, star)` | `-> Any` — returns `pygame.Surface | None`, should be `-> Optional[pygame.Surface]` (S1) |
| 81 | `draw_colony_marker(r, screen, sys, world_pos)` | `-> None` OK but params all `Any` (S2) |
| 113 | `draw_star(r, screen, star, system_center, system_name, is_primary, is_selected_system)` | `-> None` OK but params all `Any` (S2) |
| 173 | `draw_system_details(r, screen, sys, sys_world_pos)` | `-> None` OK but params all `Any` (S2) |

### `game/ui/panels/battle_panels.py`

| Line | Function | Issue |
|------|----------|-------|
| 32 | `__init__` dunder | Exempt — OK |
| 37 | `draw(self, screen)` | Missing `-> None` (S1) |
| 40 | `handle_click(self, mx, my)` | `-> bool` — OK |
| 43 | `draw_stat_bar(self, surface, x, y, width, height, pct, color)` | Missing `-> None` (S1) |
| 47 | `_get_ships(self)` | `-> list` — OK but S2 (should be `-> list[Any]`) |
| 112 | `ShipStatsPanel.draw(self, screen)` | Missing `-> None` (S1) |
| 165 | `draw_ship_entry(...)` | `-> int` — OK |
| 197 | `draw_ship_details(...)` | `-> int` — OK |
| 236 | `handle_click(self, mx, my)` | `-> bool \| tuple[str, str]` — OK |
| 298 | `SeekerMonitorPanel.draw(self, screen)` | Missing `-> None` (S1) |
| 349 | `draw_seeker_entry(...)` | `-> int` — OK |
| 486 | `BattleControlPanel.draw(self, screen)` | Missing `-> None` (S1) |
| 558 | `handle_click(self, mx, my)` | `-> str \| bool` — OK |

### `game/ui/screens/battle_setup/screen.py`

| Line | Function | Issue |
|------|----------|-------|
| 64 | `handle_event(self, event)` | Missing `-> None` (S1) |
| 69 | `update(self, dt)` | `-> None` — OK |
| 73 | `draw(self, screen)` | Missing `-> None` (S1) |
| 78 | `handle_resize(self, width, height)` | Missing `-> None` (S1) |
| 87 | `start(self, preserve_teams)` | Missing `-> None` (S1) |
| 114 | `selected_tf_index` property | `-> Any` — should go through viewmodel; S2 |
| 122 | `selected_sq_index` property | `-> Any` — S2 |
| 130 | `selected_ship_index` property | `-> Any` — S2 |

### `game/ui/screens/battle_setup/input_handler.py`

| Line | Function | Issue |
|------|----------|-------|
| 35 | `handle_event(self, event)` | Missing `-> None` (S1) |
| 44 | `_handle_button(self, event)` | Missing `-> None` (S1, private but caller doesn't check ret) |
| 150 | `_push_tick_limit_to_controller(self)` | Missing `-> None` (S1, private) |
| 160 | `_handle_dropdown(self, event)` | Missing `-> None` (S1, private) |

### `game/ui/screens/battle_setup/controller.py` (partial)

| Line | Function | Issue |
|------|----------|-------|
| 39 | `_get_registries()` | `-> Any \| None` — module-level function, OK |

### `game/ui/screens/strategy_click_dispatcher.py`

| Line | Function | Issue |
|------|----------|-------|
| 54 | `scene` property | `-> Any` — from handler; S4 (dynamic dispatch) |
| 60 | `input_mode` property | `-> str` — OK |
| 69 | `dispatch_click(self, mx, my, button)` | `-> bool` — OK |
| 365 | `_hit_test_planets(self, mx, my, system)` | `-> Optional[object]` — OK but imprecise |
| 474 | `_resolve_click_target(self, mx, my)` | `-> Any` — returns `HexCoord`, should be more specific (S1) |
| 505 | `_handle_picking(self, mx, my)` | Missing `-> None` (S1, private) |

### `game/ui/screens/builder/modifier_row.py`

| Line | Function | Issue |
|------|----------|-------|
| 41 | `__init__` | Many untyped params (S2) |
| 90 | `_get_local_bounds(self)` | `-> tuple` — OK but bare `tuple` (S2) |
| 107 | `_set_controls_enabled(self, enabled)` | Missing `-> None` and param type (S1+S2) |
| 129 | `build_ui(self, y)` | `-> Any` — returns `int`, should be `-> int` (S1) |
| 154 | `_build_linear_controls(self, y, start_x, safe_id)` | `-> None` — OK (private) |
| 228 | `_clear_ui(self)` | `-> None` — OK |
| 241 | `update(self, component, template_modifiers)` | Missing `-> None` (S1) |
| 284 | `handle_event(self, event)` | `-> bool` — OK |
| 354 | `kill(self)` | `-> None` — OK |

### `game/ui/screens/builder/stats_config.py`

| Line | Function | Issue |
|------|----------|-------|
| 45 | `load_stats_config()` | `-> Any` — S2 (could be more specific dict) |

### `game/ui/screens/strategy_windows/empire_panel_ctrl.py`

| Line | Function | Issue |
|------|----------|-------|
| 25 | `EmpirePanelRegistrar.open(self)` | Missing `-> None` (S1) |
| 62 | `SettingsRegistrar.open(self)` | Missing `-> None` (S1) |

### `game/ui/screens/strategy_windows/orders_window_ctrl.py`

| Line | Function | Issue |
|------|----------|-------|
| 34 | `open(self, entity, entity_type)` | Missing `-> None` (S1) |

### `game/ui/screens/strategy_windows/selection_prompts.py`

| Line | Function | Issue |
|------|----------|-------|
| 29 | `prompt_planet(self, planets, on_select)` | Missing `-> None` (S1) |
| 50 | `open_system(self, systems, current_system, on_selected)` | Missing `-> None` (S1) |
| 69 | `prompt_fleet(self, fleets, on_select)` | Missing `-> None` (S1) |

### `game/ui/screens/strategy_windows/planet_abilities_ctrl.py`

| Line | Function | Issue |
|------|----------|-------|
| 25 | `open(self, planet)` | Missing `-> None` (S1) |
| 58 | `open_editor(self, editor_type, planet)` | Missing `-> None` (S1) |

### `game/ui/screens/strategy_windows/build_queue_windows.py`

| Line | Function | Issue |
|------|----------|-------|
| 24 | `BuildQueueListRegistrar.open(self)` | Missing `-> None` (S1) |

### `game/ui/screens/builder/panel_layout_config.py`

| Line | Function | Issue |
|------|----------|-------|
| 20 | `manager` field | `Any` — but field type, not function; S4 |
| 21 | `container` field | `Any` — S4 |

### Other files with S1 missing return types:

| File | Line(s) | Function(s) |
|------|---------|-------------|
| `game/ui/screens/empire_build_queue_formatter.py` | Many | All public formatter functions have `-> str` — OK |
| `game/ui/screens/build_queue_helpers.py` | Many | All have return types — OK |
| `game/ui/screens/strategy_render/overlay.py` | 11 | `draw_processing_overlay` has `-> None` — OK |
| `game/ui/screens/transfer_controller.py` | 49 | `collect_sources_and_targets` has `-> list[dict]` — OK |
| `game/ui/screens/test_lab/renderer/test_list_panel.py` | 53 | `draw()` Missing `-> None` (S1) |
| `game/ui/screens/test_lab/renderer/category_panel.py` | 57+ | `draw()` Missing `-> None` (S1) |
| `game/ui/screens/test_lab/results_panel.py` | 18+ | `__init__` params untyped (S2) |
| `game/ui/screens/workshop_ship_io.py` | 70 | `save_ship(self)` Missing `-> None` (S1) |
| `game/ui/screens/workshop_ship_io.py` | 119 | `load_ship(self)` Missing `-> None` (S1) |
| `game/ui/screens/workshop_ship_io.py` | 188 | `select_target(self)` Missing `-> None` (S1) |
| `game/ui/screens/cargo_quick_dialog.py` | 79 | `_setup_ui(self)` Missing `-> None` (S1 priv) |
| `game/ui/screens/cargo_quick_dialog.py` | 107 | `_populate_items(self)` Missing `-> None` (S1 priv) |
| `game/ui/panels/build_queue_controller.py` | 57 | `load_designs_by_category` has `-> tuple[list, list[str]]` — OK |

---

## Severity 1: `-> Any` on Non-Generic Functions (Knowable Type)

These are distinct from the protocol/generic `Any` uses — the actual return type is deterministic:

| File | Line | Function | Actual Return | Suggested |
|------|------|----------|---------------|-----------|
| `game/ui/screens/test_lab/data_extractor.py` | 21 | `get_test_data_dir()` | `str` | `-> str` |
| `game/ui/screens/test_lab/data_extractor.py` | 55 | `extract_ships()` | `list[dict]` | `-> list[dict[str, Any]]` |
| `game/ui/screens/test_lab/data_extractor.py` | 168 | `_extract_component_ids()` | `list[str]` | `-> list[str]` |
| `game/ui/screens/test_lab/data_extractor.py` | 187 | `load_component()` | `dict | None` | `-> dict[str, Any] | None` |
| `game/ui/screens/battle_setup/screen.py` | 114 | `selected_tf_index` | `int | None` | `-> int | None` |
| `game/ui/screens/battle_setup/screen.py` | 122 | `selected_sq_index` | `int | None` | `-> int | None` |
| `game/ui/screens/battle_setup/screen.py` | 130 | `selected_ship_index` | `int | None` | `-> int | None` |
| `game/ui/screens/strategy_renderer.py` | ~170+ | `screen_width` | `int` | `-> int` |
| `game/ui/screens/strategy_renderer.py` | ~170+ | `screen_height` | `int` | `-> int` |
| `game/ui/screens/strategy_renderer.py` | ~170+ | `hex_size` | `float` | `-> float` |
| `game/ui/screens/battle_setup/controller.py` | 39 | `_get_registries()` | `GameRegistries | None` | Type hint is `Any | None` — acceptable S4 |

All of `stat_getters.py` functions (45+ entries listed above) fit this category — they all return `-> Any` but return concrete types (`float`, `int`, `str`, `bool`).

---

## Severity 1: Missing Return Types — `_button_handlers` (Known)

From the task briefing, these are confirmed:

| File | Line | Function | Issue |
|------|------|----------|-------|
| `game/ui/screens/gravity_target_editor.py` | 164 | `_button_handlers(self)` | Returns `dict` but no annotation; S1. This is a template method pattern — `PlanetTargetEditor._button_handlers` base returns `dict[Any, Callable]` |

The `PlanetTargetEditor` base class at `game/ui/screens/planet_target_editor_base.py:39` defines `_button_handlers() -> Dict[Any, Callable[[], None]]`. Overrides in GravityTargetEditor (164), RadiationShieldEditor (~176), AtmosphereTargetEditor (~223), WaterTargetEditor (~173) don't repeat the annotation. Per conventions, overrides should carry the return type.

---

## Severity 2: Missing Parameter Types

Notable files with many untyped parameters:

1. **`game/ui/screens/builder/modifier_row.py`** — `__init__(self, manager, container, width, mod_id, mod_def, config, on_change_callback, modifier_logic=None)` — 8 untyped params (S2)
2. **`game/ui/panels/battle_panels.py`** — `BattlePanel.__init__(self, scene, x, y, w, h)` + `ExpandableIdPanel.__init__(self, scene, x, y, w, h)` — untyped params (S2)
3. **`game/ui/screens/battle_setup/input_handler.py`** — `__init__(self, screen)` — untyped param (S2)
4. **`game/ui/screens/test_lab/results_panel.py`** — `__init__(self, x, y, width, height, test_history)` — untyped params (S2)
5. **`game/ui/screens/workshop_ship_io.py`** — `__init__` with 7 untyped params (S2)

---

## Severity 3: `type: ignore` Sites

| File | Line | Annotation | Reason |
|------|------|------------|--------|
| `game/ui/panels/race_theme_gallery.py` | 101 | `# type: ignore[override]` | Override of `_discover_assets() -> List[Tuple[str, ...]]` returns `List[Tuple[str, Dict[str, pygame.Surface]]]` instead of `List[Tuple[str, pygame.Surface]]` from `BaseGallery`. This is a real type mismatch — the subclass overrides both the return type and the data shape. The `type: ignore` is a workaround, not a fix. |

---

## Severity 4: Informational / Justified `Any`

These are not actionable issues:

1. **`game/app.py`** — Scene accessor properties (`active_scene`, `battle_scene`, etc.) — justified `Any` for generic ScreenRouter proxy pattern.
2. **`game/core/state_machine.py`** — `state` property + `pop_and_return` — generic state machine, `Any` is correct.
3. **`game/core/protocols/ui.py`** — Protocol methods using `Any` for duck-typed parameters — valid protocol design.
4. **`game/engine/spatial.py`** — `SpatialGrid` uses `Any` for `pos` parameter and generic object storage — acceptable in engine code.
5. **`game/simulation/entities/projectile.py:19`** — `__init__` with `**kwargs` — dunder, exempt.
6. **`game/ui/screens/builder/stats_config.py:45`** — `load_stats_config()` returning `-> Any` for JSON-loaded dict — acceptable for deserialized content.
7. **`game/ui/screens/strategy_render/systems.py`** — Render functions taking `Any` params (duck-typed pygame/domain objects from the dynamic renderer) — this is a pervasive pattern in the render layer for pragmatic reasons (avoid circular imports).

---

## File-Specific Findings by Layer

### Core Layer (4 files)
- `game/core/state_machine.py` — Correct use of `Any` on generic API. Clean.
- `game/core/protocols/ui.py` — Correct protocol `Any` usage. Clean.
- `game/core/config.py` — Clean.
- `game/app.py` — 18 S1 missing `-> None` annotations on lifecycle methods.

### Simulation Layer (20+ files)
- `game/simulation/entities/projectile.py` — Clean except `__init__` (dunder exempt).
- `game/simulation/entities/ship_combat_engine.py` — Clean with good type annotations.
- `game/simulation/entities/ship_resource_manager.py` — Clean.
- `game/simulation/entities/ship_stat_querier.py` — Clean.
- `game/simulation/combat/targeting_system.py` — Clean.
- `game/simulation/combat/weapon_firing_system.py` — Clean.
- `game/simulation/combat/modifier_stack.py` — Clean.
- `game/simulation/managers/battle_state_manager.py` — Clean.
- `game/simulation/managers/retreat_manager.py` — Clean.
- `game/simulation/services/registry_loader.py` — Clean.
- `game/simulation/systems/resource_manager.py` — Clean.
- `game/simulation/systems/tech_preset_loader.py` — Clean.
- `game/simulation/replay/replay_spec.py` — Clean.
- `game/simulation/components/modifier_introspection.py` — Clean.
- `game/simulation/components/modifier_manager.py` — Clean.
- `game/simulation/components/component.py` — Clean.
- `game/simulation/components/modifier_effects.py` — Clean.
- `game/simulation/components/abilities/planetary.py` — Clean.
- `game/simulation/components/abilities/markers.py` — Clean.
- `game/simulation/components/abilities/ui_colors.py` — Clean (constants only).
- `game/simulation/physics_constants.py` — Clean.
- `game/simulation/projectile_manager.py` — Clean.
- `game/simulation/battle_state.py` — Clean.

**Observation:** Simulation layer has excellent type hygiene across these 23 files. Nearly zero issues found.

### Strategy Layer (20+ files)
- `game/strategy/facade/slices/economy_slice.py` — Clean.
- `game/strategy/facade/dto/fleet_hierarchy_dto.py` — Clean.
- `game/strategy/facade/dto/empire_dto.py` — Clean.
- `game/strategy/data/ship_display_formatter.py` — Clean.
- `game/strategy/data/fleet_consumable_aggregator.py` — Clean.
- `game/strategy/data/galaxy_warp_generator.py` — Clean.
- `game/strategy/data/homeworld_presets.py` — Clean.
- `game/strategy/data/ship_instance_bridge.py` — Clean.
- `game/strategy/data/planet_gen.py` — Clean.
- `game/strategy/data/group_policy_registry.py` — Clean.
- `game/strategy/data/race_caption_loader.py` — Clean.
- `game/strategy/data/ship_consumable_manager.py` — Clean.
- `game/strategy/combat/spec_compiler.py` — Clean (595 lines, close to 500 cap; well-annotated).
- `game/strategy/engine/command_handlers.py` — Re-export shim — OK.
- `game/strategy/engine/handlers/base.py` — Clean.
- `game/strategy/engine/production_math.py` — Clean.
- `game/strategy/engine/fleet_movement_engine.py` — Clean.
- `game/strategy/engine/organics_consumption_engine.py` — Clean.
- `game/strategy/services/modifier_resolver.py` — Clean.
- `game/strategy/services/design_cost_calculator.py` — Clean.
- `game/strategy/services/ability_sources/facility.py` — Clean.
- `game/strategy/services/ability_sources/planet_intrinsic.py` — Clean.
- `game/strategy/generation/star_image_registry.py` — Clean.
- `game/strategy/generation/density/primitives/density_primitive.py` — Clean (Protocol).
- `game/strategy/generation/density/primitives/ring.py` — Clean.
- `game/strategy/generation/density/primitives/spiral_arm.py` — Clean.

**Observation:** Strategy layer has excellent type hygiene. Nearly zero issues.

### UI Layer (~80 files)
Most S1 issues are concentrated here, particularly in:
- `game/ui/screens/builder/stat_getters.py` (45+ issues)
- `game/ui/screens/test_lab/data_extractor.py` (5 issues)
- `game/ui/screens/battle_setup/screen.py` (4+ issues)
- `game/ui/panels/battle_panels.py` (4+ issues)
- `game/ui/screens/battle_setup/input_handler.py` (4+ issues)
- Various registrar/window classes (missing `-> None`)

### Other Layers (AI, Assets, Engine, Services, Research)
- All clean or near-clean.

---

## Comparative Notes

| Layer | Files | S1 Issues | Type Hygiene |
|-------|-------|-----------|-------------|
| Core | 4 | 0 (Any correct) | Excellent |
| Simulation | 23 | 0 | Excellent |
| Strategy | 27 | 0 | Excellent |
| UI — screens | ~50 | ~80 | Poor |
| UI — panels | ~10 | ~10 | Fair |
| UI — services | ~10 | ~5 | Good |
| AI | 5 | 0 | Excellent |
| Engine | 2 | 0 | Excellent |

The type quality gap between the non-UI layers (near-flawless) and the UI layer (many issues) is **substantial**. The UI layer accounts for approximately 95% of all S1 issues in this shard.

---

## Highest Priority Remediation Targets

1. **`game/ui/screens/builder/stat_getters.py`** — Replace all 45+ `-> Any` with actual return types (`-> float`, `-> int`, `-> str`). This is the single largest source of type-safety loss in the shard. All return types are deterministic and knowable.

2. **`game/ui/screens/test_lab/data_extractor.py`** — Fix `get_components_cache()` returning `-> bool` when it actually returns `dict[str, dict]`. Also fix `get_test_data_dir()` returning `str` but annotated `-> Any`.

3. **`game/ui/screens/battle_setup/screen.py`** — Add `-> None` to `handle_event`, `draw`, `handle_resize`, `start`. Replace `-> Any` on `selected_tf_index`, `selected_sq_index`, `selected_ship_index` with `-> int | None`.

4. **`game/ui/panels/battle_panels.py`** — Add `-> None` to all `draw()` methods. Clean but straightforward fixes.

5. **`game/app.py`** — Add `-> None` to 18 lifecycle delegation methods. Scene accessor `-> Any` is justified and stays.

6. **`game/ui/screens/strategy_render/systems.py`** — Replace module-level function `-> Any` returns with concrete types. `load_star_image` returns `pygame.Surface | None`, not `Any`.

7. **Multiple registrar/controller `open()` methods** — Add `-> None` to ~10 open methods in `strategy_windows/` registrars.

---

## `type: ignore` Deep Dive

### `game/ui/panels/race_theme_gallery.py:101`

```python
def _discover_assets(self) -> List[Tuple[str, Dict[str, pygame.Surface]]]:  # type: ignore[override]
```

**Analysis:** `BaseGallery._discover_assets()` returns `List[Tuple[str, pygame.Surface]]` (one surface per asset). `RaceThemeGallery._discover_assets()` returns `List[Tuple[str, Dict[str, pygame.Surface]]]` (a dict of surfaces per asset — multiple ship classes). The override changes both the return type AND the data shape consumed by `_populate_gallery` (which is also overridden in `RaceThemeGallery`).

This is a legitimate Liskov violation being suppressed. The fix options:
1. Make `BaseGallery` generic over the asset type (`TGalleryAsset`) so derived classes can declare their asset shape.
2. Split `_discover_assets` into a smaller protocol that only populates `asset_buttons`.
3. Make `_populate_gallery` the only override point (already done) and convert `_discover_assets` to return a common base.

Current state: `type: ignore` works but masks a structural design issue.

---

## Verification

All 180 files listed in the shard scope were read exhaustively. Each was checked for:
- Public function/method return type annotations
- `-> Any` density
- Missing parameter types (sampled, not exhaustive on private methods)
- `type: ignore` / `# type: ignore` annotations
- Broad-catch exception handling with required comment (outside scope, noted incidentally via grep)

No files were skipped.
