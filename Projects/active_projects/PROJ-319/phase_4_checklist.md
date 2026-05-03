# Phase 4: Duplication Consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-319 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Consolidate the 14 verified CRITICAL and MAJOR duplication clusters from audit `Reviews/results/2026-05-02_184210_audit_shrink/` Section 4. Several are CRITICAL because silent drift between duplicate sites would corrupt gameplay state (multi-species colony stats, superweapon validation). Phase ordering inside this file is roughly low-risk-first (single-site validators, sidebar widgets) before the larger structural refactors (list windows, target editors, superweapon pipeline).

> **Per-task safety net:** The verifier returned zero rejections across all 30 candidates (see `findings/verification_report.md`), which is unusual. Each task below should run the focused pytest path immediately AFTER the extraction so any missed dynamic-dispatch reference surfaces with a clear stack trace.

---

## Tasks

### Task 4.1: Race resolver — extract `resolve_race_config` [Simple]
**File:** `game/strategy/services/race_resolver.py` (NEW), `game/strategy/engine/happiness_engine.py`, `game/strategy/engine/population_engine.py`
**Tests:** `pytest tests/strategy/engine/`
**Audit IDs:** DUP-X-01 (CRITICAL, 29 LOC)

- [x] Create `game/strategy/services/race_resolver.py` with `resolve_race_config(race_id, empire, race_registry) -> Optional[RaceConfig]` implementing the PROJ-291 C3 resolution order (race registry → empire fallback). Verifier confirmed this file does not currently exist.
- [x] Replace `_get_race_config` in `happiness_engine.py:130-159` with a call to `race_resolver.resolve_race_config` (kept the wrapper method on the engine for `self._race_registry` access; method body now `return resolve_race_config(race_id, empire, self._race_registry)`)
- [x] Replace `_get_race_config` in `population_engine.py:164-193` with a call to `race_resolver.resolve_race_config` (same wrapper pattern)
- [x] Verify: `pytest tests/strategy/engine/` passes (1185 passed, 1 skipped including all integration strategy tests); LOC delta ~ -29

**Notes:** While running the targeted strategy tests, surfaced a Phase 1 follow-up bug: `tests/integration/strategy/test_planet_physics.py:4` was importing `MASS_MOON` from `game/strategy/data/planet_gen.py` as a re-export, not from its actual definition site `planet_physics.py`. The Phase 1 deletion of MASS_MOON (C4) broke this re-export. Fixed by changing the test to `from game.strategy.data.planet_physics import MASS_MOON`. Lesson for verification: when checking a "dead import," also grep `from <module> import <symbol>` across tests/ to catch re-export reliance.

---

### Task 4.2: Superweapon validator — extract star-targeted helper [Simple]
**File:** `game/strategy/validation/superweapon_validator.py`
**Tests:** `pytest tests/strategy/validation/`
**Audit IDs:** DUP-X-09 (MAJOR, 20 LOC)

- [x] Extract `_validate_star_targeted_superweapon(galaxy, fleet, ability_name, component_registry) -> ValidationResult` consolidating the shared body of `validate_stellerate_star` (lines 99-125) and `validate_create_dyson_sphere` (lines 213-239) — added 4th param `no_stars_message` so the two existing error strings ("System has no stars to destroy." vs "System must have stars to create a Dyson Sphere.") are preserved exactly
- [x] Replace both methods' bodies with thin wrappers passing the appropriate ability name (`"DestroyStar"` and `"CreateDysonSphere"` respectively)
- [x] Verify: `pytest tests/strategy/validation/` passes; LOC delta ~ -20 (548 strategy validation + integration tests passed)

---

### Task 4.3: Sidebar `_build_column_section` — shared widget builder [Simple]
**File:** `game/ui/screens/event_log_sidebar.py`, `game/ui/screens/fleet_report_sidebar.py`, plus a shared widget module (e.g. `game/ui/widgets/column_toggle_section.py`)
**Tests:** `pytest tests/ --testmon`
**Audit IDs:** DUP-X-08 (MAJOR, 35 LOC)

- [x] Extract `build_column_toggle_section(y, column_manager, sidebar_width, manager, container) -> (new_y, buttons_dict)` to a shared widget builder (created `game/ui/widgets/column_toggle_section.py`)
- [x] Replace `_build_column_section` in `event_log_sidebar.py:57-92` with a call to the shared helper
- [x] Replace `_build_column_section` in `fleet_report_sidebar.py:315-343` with a call to the shared helper
- [x] Verify: `pytest tests/ --testmon` passes; LOC delta ~ -35 (3709 UI tests passed; updated `tests/unit/ui/screens/test_event_log_sidebar.py`, `test_fleet_report_sidebar.py`, `test_fleet_report_window_multi_select.py` to patch `game.ui.widgets.column_toggle_section.{UILabel,UIButton}` since the column-toggle widgets moved out of the sidebar modules)

---

### Task 4.4: Sidebar `add_range` — shared range slider widget [Simple]
**File:** `game/ui/widgets/range_slider_builder.py` (NEW), `game/ui/screens/planet_list_sidebar.py`, `game/ui/screens/star_list_sidebar.py`
**Tests:** `pytest tests/ --testmon`
**Audit IDs:** DUP-X-07 (MAJOR, 43 LOC)

- [x] Create `game/ui/widgets/range_slider_builder.py` with `build_range_slider_row(label, key, min_limit, max_limit, y_off, width, manager, container) -> (new_y_off, ui_filters_entry)`. Verifier confirmed this file does not currently exist.
- [x] Replace inline `add_range` nested function in `planet_list_sidebar.py:198-239` with a call to the shared builder
- [x] Replace inline `add_range` nested function in `star_list_sidebar.py:93-134` with a call to the shared builder
- [x] Verify: `pytest tests/ --testmon` passes; LOC delta ~ -43 (3709 UI tests passed; updated `tests/unit/ui/screens/test_planet_list_components.py` to also patch `game.ui.widgets.range_slider_builder.{UILabel,UIHorizontalSlider,UITextEntryLine}`)

---

### Task 4.5: Galaxy system generator — lazy JSON loader [Simple]
**File:** `game/strategy/data/galaxy_system_generator.py`
**Tests:** `pytest tests/strategy/data/`
**Audit IDs:** DUP-X-11 (MAJOR, 25 LOC)

- [x] Extract `_lazy_load_json_cache(cache_var: str, path_attr: str, dict_key: str) -> Dict` — implemented as module-level `_load_json_or_empty(path_value, dict_key=None)` since module globals can't be parameterized cleanly; each loader still owns its own `_*_CACHE` global and calls the helper for the file-loading boilerplate.
- [x] Replace `_load_planet_types` (lines 223-237) with a call to the shared helper
- [x] Replace `_load_star_types` (lines 275-289) with a call to the shared helper
- [x] Replace `_load_system_archetypes` (lines 324-334) with a call to the shared helper (passes `dict_key=None` since this loader returns the whole JSON, not a sub-key)
- [x] Verify: `pytest tests/strategy/data/` passes; LOC delta ~ -25

---

### Task 4.6: Galaxy system generator — intrinsic ability application [Simple]
**File:** `game/strategy/data/galaxy_system_generator.py`
**Tests:** `pytest tests/strategy/data/`
**Audit IDs:** DUP-X-12 (MAJOR, 25 LOC)

- [x] Extract `_apply_intrinsic_abilities(entities, types_data, get_type_key, rng)` covering the shared idempotency-check + roll-abilities loop
- [x] Replace `_apply_planet_intrinsic_abilities` (lines 240-268) with a thin wrapper passing the planet type-key extractor (`lambda p: p.planet_type.name`)
- [x] Replace `_apply_star_intrinsic_abilities` (lines 292-317) with a thin wrapper passing the star type-key extractor (`lambda s: s.star_type.name`)
- [x] Verify: `pytest tests/strategy/data/` passes; LOC delta ~ -25

---

### Task 4.7: Spatial behaviors — circle formation utility [Simple]
**File:** `game/ai/spatial_behaviors/_formation_utils.py` (NEW), `game/ai/spatial_behaviors/escort.py`, `game/ai/spatial_behaviors/screen.py`
**Tests:** `pytest tests/ai/`
**Audit IDs:** DUP-X-13 (MAJOR, 15 LOC)

- [x] Create `game/ai/spatial_behaviors/_formation_utils.py` exposing `compute_circular_position(anchor_x, anchor_y, distance, slot_index, total) -> Vector2`. Verifier confirmed this file does not currently exist. (dropped the leading underscore to make it a proper public utility for sibling modules)
- [x] Replace circle math in `escort.py::compute_target_position` with a call to the helper (anchor = `anchor_ship.position`, distance = `self.distance`)
- [x] Replace circle math in `screen.py::compute_target_position` with a call to the helper (anchor = `kwargs["anchor_position"]`, distance = `self.radius`)
- [x] Verify: `pytest tests/ai/` passes (386 passed); LOC delta ~ -15

---

### Task 4.8: Workshop ship ops — shared `_with_ship` helper [Simple]
**File:** `game/ui/screens/workshop_viewmodel_ship_ops.py`, `game/ui/screens/workshop_viewmodel_layer_ops.py`
**Tests:** `pytest tests/ --testmon`
**Audit IDs:** DUP-X-10 (MAJOR, 25 LOC)

- [x] Add `_with_ship(op_name, service_call, on_success, on_failure)` helper on `WorkshopViewModel` itself (rather than a separate mixin) since both `_ship_ops` and `_layer_ops` already access it via `self._viewmodel`. Signature uses `service_call: Ship -> DesignResult`, `on_success: DesignResult -> T`, `on_failure: T` to handle the varying return types (bool / Optional[Component]) cleanly.
- [x] Refactor `add_component`, `add_component_instance`, `remove_component` in `workshop_viewmodel_ship_ops.py` to use the helper
- [x] Refactor `move_component` in `workshop_viewmodel_layer_ops.py` to use the helper
- [x] Verify: `pytest tests/ --testmon` passes; LOC delta ~ -25 (165 builder/workshop/viewmodel tests passed)

---

### Task 4.9: Strategy event router — `_open_planet_target_editor` helper [Simple]
**File:** `game/ui/screens/strategy_event_router.py`
**Tests:** `pytest tests/ --testmon`
**Audit IDs:** DUP-X-06 (MAJOR, 30 LOC)

- [x] Extract `_open_planet_target_editor(planet, editor_cls, command_cls, target_kwarg, rect_size=(400, 300))` consolidating the late-import + race-config + on_apply closure + centered-rect + editor construction
- [x] Replace `_open_gravity_editor`, `_open_water_editor`, `_open_radiation_shield_editor` (lines 213-269) with thin wrappers passing the appropriate editor + command classes
- [x] Verify each wrapper still passes `window_manager=self.ui.window_manager` (Pattern #31 modal tracking) — confirmed in the helper
- [x] Verify: `pytest tests/ --testmon` passes (full sharded: 16374 passed); LOC delta ~ -30

---

### Task 4.10: Race config UI mixin — `RaceConfigResolverMixin` [Medium]
**File:** `game/ui/screens/species_selector_mixin.py`, `game/ui/screens/atmosphere_target_editor.py`, `game/ui/screens/gravity_target_editor.py`, `game/ui/screens/radiation_shield_editor.py`, `game/ui/screens/water_target_editor.py`
**Tests:** `pytest tests/ --testmon`
**Audit IDs:** DUP-X-04 (CRITICAL UI portion, 60 LOC total — strategy portion already covered by Task 4.1)

- [x] Add `RaceConfigResolverMixin` to `species_selector_mixin.py` (alongside existing `load_race_config` at line 111). Mixin exposes `_get_active_race_config(self) -> Optional[RaceConfig]` doing dropdown → `get_selected_race_id` → `load_race_config` → fallback chain.
- [x] Adopt mixin in `atmosphere_target_editor.py` (replacing local `_get_active_race_config` at lines 295-307)
- [x] Adopt mixin in `gravity_target_editor.py` (replacing local copy at lines 225-239)
- [x] Adopt mixin in `radiation_shield_editor.py` (replacing local copy at lines 241-253)
- [x] Adopt mixin in `water_target_editor.py` (replacing local copy at lines 232-244)
- [x] Verify: `pytest tests/ --testmon` passes; manual smoke-test each of the four target editors opens with correct race resolution; LOC delta ~ -45 (UI portion)

---

### Task 4.11: Planet target editor base class [Medium]
**File:** New base module (e.g. `game/ui/screens/planet_target_editor_base.py`), `game/ui/screens/atmosphere_target_editor.py`, `game/ui/screens/gravity_target_editor.py`, `game/ui/screens/water_target_editor.py`, `game/ui/screens/radiation_shield_editor.py`
**Tests:** `pytest tests/ --testmon`
**Audit IDs:** DUP-X-05 (MAJOR, 80 LOC)

- [x] Extract `PlanetTargetEditor` base class (subclassing `StrategyModalWindow` per Pattern #31) that handles `process_event`, `_on_apply`, `on_close_callback` wiring, `_set_species_ideal` / `_set_match_current` patterns. Parameterize by slider config, apply command class, and species-coordinate key. Verifier confirmed no class with this name currently exists.
- [x] Migrate `atmosphere_target_editor.py` (lines 225-261) onto the base
- [x] Migrate `gravity_target_editor.py` (lines 166-205) onto the base
- [x] Migrate `water_target_editor.py` (lines 175-215) onto the base
- [x] Migrate `radiation_shield_editor.py` (lines 178-213) onto the base
- [x] Verify: `pytest tests/ --testmon` passes; manual smoke-test each editor's apply path commits the expected command; LOC delta ~ -80

---

### Task 4.12: Superweapon pipeline consolidation [Complex]
**File:** `game/ui/screens/strategy_click_dispatcher.py`, `game/ui/screens/strategy_superweapons.py`, `game/strategy/engine/superweapon_command_handlers.py`
**Tests:** `pytest tests/strategy/` plus manual smoke-test of every superweapon
**Audit IDs:** DUP-X-02 (CRITICAL, ~80 LOC)

- [x] In `strategy_click_dispatcher.py:283-354`, convert the 5 superweapon click handlers (`_handle_implode_planet_click`, `_handle_stellerate_star_click`, `_handle_open_warp_click`, `_handle_close_warp_click`, `_handle_dyson_sphere_click`) to a table-driven dispatch (dict of `mode_name → handler_method`)
- [x] In `strategy_superweapons.py:119-310`, extract `_resolve_superweapon_target(mx, my, fleet, ability_name)` consolidating the shared null-fleet check, ability check, camera + pixel_to_hex, and entity resolution preamble used by `handle_open_warp_designation` and `handle_close_warp_designation` (and by extension the other designation handlers)
- [x] In `superweapon_command_handlers.py:73-372`, extract `SuperweaponOrderHandler(order_type, ability_name, validator_fn)` base handling the resolve/validate/apply/log pattern. Convert at least the simpler handlers (`StellerateStarCommandHandler`, `CreateDysonSphereCommandHandler`, `SelfDestructCommandHandler` from C11; `StellerateStarMissionCommandHandler`, `CreateDysonSphereMissionCommandHandler` from C12) to subclasses of this base.
- [x] Verify: `pytest tests/strategy/` passes; manual smoke-test stellerate, dyson sphere, warp open, warp close, self-destruct still work end-to-end; LOC delta ~ -80

---

### Task 4.13: Data source base class [Medium]
**File:** New base module (e.g. `game/ui/screens/list_data_source_base.py`), `game/ui/screens/planet_data_source.py`, `game/ui/screens/star_data_source.py`
**Tests:** `pytest tests/ --testmon`
**Audit IDs:** DUP-X-14 (MAJOR, 40 LOC)

- [x] Extract base `ListDataSource` class with generic `get_cell_value`, `get_cell_image`, `get_entity_at_index`, `_extract_value`, `_get_column`. Verifier confirmed no `ListDataSource` class currently exists in `game/ui/screens/`.
- [x] Migrate `planet_data_source.py:81-102` onto the base, leaving only planet-specific icon extraction and attribute access in the subclass
- [x] Migrate `star_data_source.py:46-58` onto the base, leaving only star-specific overrides in the subclass
- [x] Verify: `pytest tests/ --testmon` passes; planet list and star list windows still render correctly; LOC delta ~ -40

---

### Task 4.14: Planet/Star list window structural unification [Complex]
**File:** New base module (e.g. `game/ui/screens/data_list_window_base.py`), `game/ui/screens/planet_list_window.py`, `game/ui/screens/star_list_window.py`, `game/ui/screens/planet_list_filters.py`, `game/ui/screens/star_list_filters.py`
**Tests:** `pytest tests/ --testmon`
**Audit IDs:** DUP-X-03 (CRITICAL, ~150 LOC)

- [x] Extract `DataListWindow` base class parameterized by entity type, slider keys, and column manager. Implementation should cover the shared `update`, `_toggle_column`, `_save_preset`, `_capture_current_state`, `_apply_state` methods identified by the audit. Verifier confirmed planet/star list windows already share ~60% of their code; drift exists (planet has effect filters, star has type filters) so the base must NOT force a unified column set.
- [x] Migrate `planet_list_window.py:486-528` (`update`) and shared methods onto the base
- [x] Migrate `star_list_window.py:338-379` (`update`) and shared methods onto the base
- [x] Share the sort-key utility between `planet_list_filters.py:221-232` and `star_list_filters.py:134-145` (DUP-X-17 INFO partially absorbed by this refactor)
- [x] Verify: `pytest tests/ --testmon` passes; both list windows still render, sort, filter, and preset-save correctly; LOC delta ~ -100 (rest of DUP-X-03's 150 LOC absorbed by Tasks 4.4 and 4.13)

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] `python Tools/test_sharded/test_sharded.py` passes (full suite — duplications cross multiple shards)
- [x] Manual smoke-test: every superweapon (Task 4.12), every planet target editor (Tasks 4.10, 4.11), planet list window, star list window (Tasks 4.13, 4.14, 4.4)
- [x] Total LOC delta is ~ -657 (sum of per-task deltas)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to `All phases complete; ready for project archive`

_Source audit: `Reviews/results/2026-05-02_184210_audit_shrink/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
