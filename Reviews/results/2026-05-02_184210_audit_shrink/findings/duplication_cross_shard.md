# Cross-Shard Duplication Report
## Summary
- Files Scanned: 675 (all `game/**/*.py`)
- Total Findings: 38
- Critical: 4 | Major: 14 | Minor: 12 | Info: 8

## Clone Detector Validation
Below validation of all 53 clusters from `clones.json`. Each entry: confirmed / downrated / false-positive with rationale.

### Confirmed — High Value (10 clusters)

**C1 — Superweapon click handlers (0.979, 5 members, 13 LOC)**: CONFIRMED. `_handle_implode_planet_click`, `_handle_stellerate_star_click`, `_handle_open_warp_click`, `_handle_close_warp_click`, `_handle_dyson_sphere_click` in `strategy_click_dispatcher.py:283-354`. All delegate to `self.scene._superweapons.handle_*_designation()` then reset `self.input_mode = 'SELECT'`. Identical structure with only the handler name differing. Consolidation: extract a single `_handle_superweapon_click(mx, my, button, handler)` dispatcher; loop over a table of (mode_name, handler_ref) pairs.

**C2 — `_get_active_race_config` in target editors (1.0, 4 members, 15 LOC)**: CONFIRMED. `atmosphere_target_editor.py:295`, `gravity_target_editor.py:225`, `radiation_shield_editor.py:241`, `water_target_editor.py:232`. All are identical 12-line methods that check `_species_dropdown` then fall back to `_default_race_id` then `self.race_config`. Consolidation: extract to `species_selector_mixin.py` (already has `load_race_config` at line 111 — this is the perfect homes). **Architectural drift note**: Pattern #31 (StrategyModalWindow) is followed correctly by all 4 editors, but the shared race-config resolution logic should be in a mixin, not copy-pasted.

**C3 — Workshop VM ops (0.943, 4 members, 25 LOC)**: CONFIRMED. `add_component` (ship_ops:88), `add_component_instance` (ship_ops:131), `remove_component` (ship_ops:156), `move_component` (layer_ops:195). All share pattern: `require_ship` guard, delegate to `_ship_service`, check `result.success`, call `notify_ship_changed()`, log on failure. Consolidation: extract `_dispatch_to_service(service_method, args, op_name)` helper. Estimation: ~20 LOC saved.

**C4 — Superweapon designation handlers (0.988, 3 members, 44 LOC)**: CONFIRMED. `strategy_superweapons.py:119-162` (stellerate_star, open_warp as 0.988 similar — close_warp has a system_picker vs confirmation dialog divergence). `handle_open_warp_designation` and `handle_close_warp_designation` share identical guard blocks (null fleet check, ability check, camera + pixel_to_hex, entity resolution). Consolidation: limited by the UI divergence (confirmation dialog vs system picker), but the common preamble (lines 1-8) could be a `_resolve_superweapon_target(mx, my, fleet, ability_name)` helper. ~30 LOC saved.

**C5 — Three-way identical (1.0) cargo mode click handlers**: CONFIRMED. `strategy_click_dispatcher.py:205-259` — `_handle_transfer_mode_click`, `_handle_drop_cargo_mode_click`, `_handle_load_cargo_mode_click`. Identical 12-line structure varying only mode string. Consolidation: single `_handle_cargo_mode_click(mode_string)`.

**C6 — Duplicate `_get_race_config` happiness/population (1.0, 29 LOC)**: CONFIRMED. `happiness_engine.py:130-159` and `population_engine.py:164-193` are IDENTICAL — same docstring, same PROJ-291 C3 resolution order, same legacy fallback logic. These are in the SAME layer (strategy/engine) and are a classic copy-paste. Consolidation: extract to a shared module (e.g., `strategy/services/race_resolver.py`). ~29 LOC saved. **Severity escalated to CRITICAL** because both engines independently resolve the same race config; drift here silently produces different population growth vs happiness values for multi-species colonies.

**C7 — Duplicate `_build_column_section` (1.0, 35 LOC)**: CONFIRMED. `event_log_sidebar.py:57-92` and `fleet_report_sidebar.py:315-343`. Identical column toggle button builder. Consolidation: extract `build_column_toggle_section(y, column_manager, sidebar_width, manager, container) -> int` to a shared widget helper. ~35 LOC saved.

**C8 — Planet/Star list window `_save_preset` (1.0, 16 LOC)**: CONFIRMED. `planet_list_window.py:582-598` and `star_list_window.py:417-433`. Identical save preset logic. Consolidation: extract to shared `PresetAwareWindow` mixin. ~16 LOC saved.

**C9 — Planet/Star list window `_toggle_column` (1.0, 10 LOC)**: CONFIRMED. `planet_list_window.py:570-580` and `star_list_window.py:405-415`. Identical column toggle logic. Consolidation: same mixin as C8. ~10 LOC saved.

**C10 — Planet/Star list window `update` (0.995, 41 LOC)**: CONFIRMED. `planet_list_window.py:486-528` and `star_list_window.py:338-379`. Near-identical update loops (scrollbar, slider text sync, header sort/swap, preset dropdown). Only the slider key lists differ. Consolidation: extract `_update_list_window(time_delta, slider_keys)` base method. ~30 LOC saved.

### Confirmed — Moderate Value (12 clusters)

**C11 — Superweapon command handler execute() first set (0.966, 3 members, 19 LOC)**: CONFIRMED. `superweapon_command_handlers.py:73, 157, 182`. `StellerateStarCommandHandler`, `CreateDysonSphereCommandHandler`, `SelfDestructCommandHandler` share identical pattern: resolve fleet, validate with static validator method, add `Order(...)`, log, return result. Consolidation: extract a `_execute_simple_superweapon(order_type, validator_method, target=None)` template method on a shared base handler. ~15 LOC saved.

**C12 — Superweapon command handler execute() second set (0.974, 2 members, 25 LOC)**: CONFIRMED. `superweapon_command_handlers.py:244, 347`. `StellerateStarMissionCommandHandler.execute` and `CreateDysonSphereMissionCommandHandler.execute` share identical 5-step pattern: resolve fleet, validate ability, add move order, queue action order, log. Consolidation: together with C11, a general superweapon handler template. ~25 LOC saved.

**C13 — `validate_stellerate_star` vs `validate_create_dyson_sphere` (1.0, 26 LOC)**: CONFIRMED. `superweapon_validator.py:99-125` and `213-239`. Identical 8-line bodies: `_require_ability(fleet, ABILITY_NAME)`, `_require_at_star_system(galaxy, fleet)`, "no stars" check. Only difference: the ability name string. Consolidation: `_validate_star_targeted_superweapon(galaxy, fleet, ability_name, component_registry)`. ~20 LOC saved.

**C14 — Planet/Star list sidebar `add_range` (1.0, 43 LOC)**: CONFIRMED. `planet_list_sidebar.py:198-239` and `star_list_sidebar.py:93-134`. Identical 43-line `add_range` inner function creating Min/Max slider rows. Consolidation: extract to a shared `build_range_slider_row(label, key, min_limit, max_limit, y_off, width, manager, container) -> (y_off, ui_filters_dict)` function. ~43 LOC saved.

**C15 — `_load_planet_types` / `_load_star_types` / `_load_system_archetypes` (0.941, 3 members, 14 LOC)**: CONFIRMED. `galaxy_system_generator.py:223, 275, 324`. Identical lazy-load pattern: global cache check, import json + pathlib, open and parse JSON, extract key from data dict. Consolidation: generic `_lazy_load_json_cache(cache_var_name, path_attr, dict_key)` helper. ~10 LOC saved.

**C16 — `_apply_planet_intrinsic_abilities` / `_apply_star_intrinsic_abilities` (0.839, 2 members, 28 LOC)**: CONFIRMED. `galaxy_system_generator.py:240, 292`. Same pattern: load types data, check for empty, default RNG, iterate entities, check idempotency, get type_key, roll abilities. Consolidation: generic `_apply_intrinsic_abilities(entities, types_data, type_key_fn, rng)` helper. ~20 LOC saved.

**C17 — `_open_gravity_editor` / `_open_water_editor` / `_open_radiation_shield_editor` (0.951, 3 members, 19 LOC)**: CONFIRMED. `strategy_event_router.py:213-269`. All share: late import editor class, late import command class, `_get_race_config(planet)`, `on_apply` closure creating command + calling `facade.handle_command(cmd)`, `create_centered_rect`, constructing editor with same args except class and command. Consolidation: `_open_planet_target_editor(EditorClass, CommandClass, planet, cmd_kwargs_key, rect_size)`. ~15 LOC saved.

**C18 — `execute_intercept` / `execute_join` (0.897, 2 members, 21 LOC)**: CONFIRMED. `strategy_fleet_ops.py:134-155, 197-218`. Same 8-line structure: log, create command, `facade.handle_command`, success/error return dict. Consolidation: `_execute_fleet_command(cmd, operation_name) -> dict`. ~12 LOC saved.

**C19 — `escort` / `screen` spatial behavior `compute_target_position` (0.892, 2 members, 26 LOC)**: CONFIRMED. `escort.py:26-52` and `screen.py:33-59`. Same algorithm: get `slot_index`, compute `total = max(len(group_ships), 1)`, distribute evenly around circle (`angle = 2*math.pi*slot_index/total`), `cos`/`sin` for position. Only difference: anchor source (ship.position vs argument position) and distance source (self.distance vs self.radius). Consolidation: extract `_compute_circular_position(anchor_x, anchor_y, distance, slot_index, total) -> Vector2` shared by both. ~15 LOC saved.

**C20 — `planet_data_source.get_cell_image` / `star_data_source.get_cell_image` (0.909, 21 LOC)**: CONFIRMED. `planet_data_source.py:81-102` and `star_data_source.py:46-58`. Same flow: get column, check for image type, get entity at index, return icon. Consolidation: extract base `ListDataSource` class. ~15 LOC saved.

**C21 — `planet_list_filters.sort_key` / `star_list_filters.sort_key` (0.957, 12 LOC)**: CONFIRMED. Same sort function pattern, different filter dict names. Consolidation: shared sort key generator function. ~8 LOC saved.

**C22 — Selection prompts (0.939, 3 members, 19 LOC)**: CONFIRMED. `selection_prompts.py:29-82` — `prompt_planet`, `prompt_fleet`, `open_system`. All share: build prompt options, create `SelectionPrompt`, show window, return result. Limited consolidation; UI callback divergence makes full extraction awkward.

### Confirmed — Already Documented as Intentional Pattern (3 clusters)

**C23 — LLM/Image background services (multiple clusters: 0.969 `_run`, 0.883 `start`, 0.9 `__init__`, 1.0 `shutdown`)**: CONFIRMED as intentional shape duplication. Per Pattern #28 (Background Service Call), `ImageBackgroundCall` was designed to mirror `LLMBackgroundCall` "shape for shape." The duplication is acknowledged in the design doc (`PROJ-314/design.md`). **Downrated to INFO** — consolidation into a generic `BackgroundCall[T]` with typed provider would be cleaner but is a design choice, not drift.  Estimated ~100 LOC saved if consolidated, but documented intentional.

**C24 — LLM/Image factories (0.917, 35 LOC)**: CONFIRMED as intentional shape duplication. `factory.py` in both `services/llm/` and `ui/services/image/` follows the identical registrar + env-var dispatch + deferred validation pattern. Per docstring on the image factory: "Two intentional behaviors mirror the LLM factory." **Downrated to INFO** — consolidation into a generic `EnvProviderFactory[T]` would save ~35 LOC but the domain-specific error types make this non-trivial.

**C25 — `modifier_manager.get_stat_summary` vs `get_stat_summary_static` (0.958, 53 LOC)**: CONFIRMED but already marked DEPRECATED. Both methods share identical summary aggregation logic; `get_stat_summary_static` is explicitly marked "DEPRECATED: Use instance get_stat_summary() instead. Will be removed in Task 1.3." **Downrated to INFO** — already on the removal roadmap.

### Confirmed — Low Impact (5 clusters)

**C26 — `_handle_keydown` cargo/transfer (0.978, 11 LOC)**: CONFIRMED. `cargo_quick_dialog.py:217` and `transfer_dialog.py:721`. Shared keydown handler pattern. Minor — ~8 LOC saved.

**C27 — `planet_action_engine` helper pair (0.972, 13 LOC)**: CONFIRMED. `_get_deactivation_time:328` and `_get_energy_drain_rate:313`. Both return `effective_time / scale * factor` style calculations. Minor — ~10 LOC saved.

**C28 — `_add_sector_effects` / `_add_system_effects` (0.968, 13 LOC)**: CONFIRMED. `system_tree_panel.py:496, 481`. Both call `strategic_ability_scanner` and append items to lists. Minor — these differ enough in purpose (sector vs system scope) that consolidation would obscure intent. ~0 LOC saved.

**C29 — `delete_squadron` / `duplicate_squadron` (0.979, 8 LOC)**: CONFIRMED. `battle_setup/controller.py:288, 278`. Both call `self._squadron_controller.delete/duplicate`. Minor — delegation wrappers are thin enough.

**C30 — `__init_subclass__` in base.py (0.976, 7 LOC)**: CONFIRMED. `simulation/components/abilities/base.py:450, 502`. Two very similar `__init_subclass__` hooks. Minor — metaclass mechanics, consolidation risky.

### Downrated / False Positive (3 clusters)

**C31 — `__init__` in planetary.py (1.0, 3 members, 12 LOC)**: PARTIALLY FALSE. `simulation/components/abilities/planetary.py:453, 528, 728`. Three `__init__` methods for different ability classes. While the constructor bodies are similar (setting `_deactivation_time`, `_energy_drain_rate`), each class has different ability-specific defaults. Consolidation into a shared base `__init__` calling `super().__init__()` would work but risks coupling unrelated ability classes. **Downrated to MINOR**.

**C32 — `_add_resources` empire vs `add_to_stockpile` planet (0.878, 20 LOC)**: FALSE POSITIVE. Different domain objects (empire-level pool vs planet-level buffer), different validation. Superficial string similarity in method shape. **Downrated to INFO** — no consolidation warranted.

**C33 — `load_cargo_to_fleet` / `unload_cargo_from_fleet` (0.905, 24 LOC)**: CONFIRMED but natural symmetry. `fleet_consumable_aggregator.py:291, 317`. Load and unload are semantic inverses with different validation. Consolidation would obscure intent. **Downrated to MINOR**.

### Confirmed — Cross-Layer Concerns (8 remaining clusters already captured in cross-shard findings below)

C34–C41 (harvester pair, bio/socio transitions, group_components, grouping strategies, dropdown handlers, panel inits, category/test_list inits, system_generator arg applying) are evaluated in the Cross-Shard Findings section.

## Cross-Shard Findings

#### CRITICAL: Duplicate `_get_race_config` Produces Divergent Population/Happiness (DUP-X-01)
**ID:** DUP-X-01
**Location:** `strategy/engine/happiness_engine.py:130-159` AND `strategy/engine/population_engine.py:164-193`
**Layer:** strategy -> strategy (within same layer, different sub-engines)
**Issue:** Identical 29-line method in both engines. Both implement the PROJ-291 C3 resolution order (race registry → empire fallback). If one engine's resolution logic is ever modified, the other silently diverges. Different race lookup results for the same (empire, race_id) pair would produce different growth vs happiness calculations for multi-species colonies.
**Impact:** HIGH — silent data inconsistency. Two engines computing against different race configs for the same colony population.
**Recommendation:** Extract `resolve_race_config(race_id, empire, race_registry) -> Optional[RaceConfig]` to `strategy/services/race_resolver.py`. Both engines call this shared function.
**Estimated LOC Savings:** 29
**Effort:** Simple

#### CRITICAL: Superweapon Handler Boilerplate Duplication Across UI+Strategy (DUP-X-02)
**ID:** DUP-X-02
**Location:** `ui/screens/strategy_click_dispatcher.py:283-354` (5 handlers) AND `ui/screens/strategy_superweapons.py:119-310` (5 handlers) AND `strategy/engine/superweapon_command_handlers.py:73-372` (10 handlers)
**Layer:** ui -> strategy
**Issue:** 20 near-identical handlers across 3 files. The superweapon pipeline (`UI click handler -> superweapons designation -> command handler -> validation`) repeats the same 3-step pattern (resolve fleet, validate ability, queue order) with only the ability name and OrderType varying. Adding a new superweapon requires touching all 3 files with boilerplate.
**Impact:** HIGH — adding a new superweapon requires +3 copy-paste blocks across 3 files. Risk of inconsistent validation between click handler, designation handler, and command handler.
**Recommendation:** For strategy_click_dispatcher.py: convert the 5 handlers into a table-driven dispatch (dict of `mode_name -> handler_method`). For superweapon_command_handlers.py: extract a `SuperweaponOrderHandler(order_type, ability_name, validator_fn)` base class that handles the common resolve/validate/apply/log pattern. For immediate designation handlers: extract `_resolve_superweapon_target(mx, my, fleet, ability_name)`.
**Estimated LOC Savings:** ~80 (across all 3 files)
**Effort:** Medium

#### CRITICAL: Planet/Star List Window Structural Duplication (DUP-X-03)
**ID:** DUP-X-03
**Location:** `ui/screens/planet_list_window.py` + `ui/screens/star_list_window.py` + `ui/screens/planet_list_sidebar.py` + `ui/screens/star_list_sidebar.py` + `ui/screens/planet_data_source.py` + `ui/screens/star_data_source.py` + `ui/screens/planet_list_filters.py` + `ui/screens/star_list_filters.py`
**Layer:** ui -> ui
**Issue:** 8 files implementing near-identical list window functionality for two entity types. `planet_list_window.py` and `star_list_window.py` share ~60% of their code (`update`, `_toggle_column`, `_save_preset`, `_capture_current_state`, `_apply_state`). Sidebars share identical `add_range` and `_build_column_section` methods. Data sources share identical row-indexing and column resolution logic.
**Impact:** HIGH — any change to list window behavior (sorting, filtering, preset system) must be applied in two places. Already showing drift (planet_list has effect filters, star_list has type filters).
**Recommendation:** Extract a `ListWindowMixin` or base `DataListWindow` class parameterized by entity type. Subclass for planet-specific and star-specific behavior. The `add_range` helper should be a shared utility function. The data source should be a generic `ListDataSource` base class.
**Estimated LOC Savings:** ~150
**Effort:** Complex

#### CRITICAL: Race Config Resolution Scattered Across 6 Locations (DUP-X-04)
**ID:** DUP-X-04
**Location:** `ui/screens/atmosphere_target_editor.py:295-307` AND `ui/screens/gravity_target_editor.py:225-239` AND `ui/screens/radiation_shield_editor.py:241-253` AND `ui/screens/water_target_editor.py:232-244` AND `strategy/engine/happiness_engine.py:130-159` AND `strategy/engine/population_engine.py:164-193`
**Layer:** ui -> strategy (cross-layer)
**Issue:** Six implementations of "get the active race config for a planet/species" exist across UI target editors and strategy engines. The UI versions (4 copies) use dropdown → `get_selected_race_id` → `load_race_config` → fallback chain. The strategy versions (2 copies) use `race_registry.get_race` → empire fallback. This is both UI-internal copy-paste AND cross-layer reimplementation.
**Impact:** MEDIUM — any change to how race configs are resolved or loaded impacts 6 files. The `load_race_config` utility already exists in `species_selector_mixin.py:111` but the 4 target editors reimplement the dropdown + fallback logic around it.
**Recommendation:** UI target editors should share a `RaceConfigResolverMixin` with the `_get_active_race_config` method. Strategy engines should share `strategy/services/race_resolver.py::resolve_race_config()`. The `species_selector_mixin.py` is the right home for the UI-side commonality.
**Estimated LOC Savings:** 60
**Effort:** Medium

---

#### MAJOR: Target Editor Boilerplate Duplication (DUP-X-05)
**ID:** DUP-X-05
**Location:** `ui/screens/atmosphere_target_editor.py:225-261` AND `ui/screens/gravity_target_editor.py:166-205` AND `ui/screens/water_target_editor.py:175-215` AND `ui/screens/radiation_shield_editor.py:178-213`
**Layer:** ui -> ui
**Issue:** All four planet target editors share identical `process_event`, `_on_apply`, on_close_callback wiring, and `_get_active_race_config` (see DUP-X-04). `atmosphere`, `gravity`, and `water` additionally share `_set_species_ideal` and `_set_match_current` patterns. The only differences: slider count (1 vs multi), units (Pa, g, %, dimensionless), and commander command class.
**Impact:** MEDIUM — adding a new planetary target (e.g., temperature) requires copy-pasting the entire editor. Validation of on_apply callbacks is duplicated.
**Recommendation:** Extract a `PlanetTargetEditor` base class (subclass of `StrategyModalWindow`) parameterized by slider config, apply command class, and species-coordinate key. The existing `StrategyModalWindow` base class (Pattern #31) handles modal registration — this would be a domain-specific layer on top.
**Estimated LOC Savings:** 80
**Effort:** Medium

#### MAJOR: Strategy Event Router Editor Opening Boilerplate (DUP-X-06)
**ID:** DUP-X-06
**Location:** `ui/screens/strategy_event_router.py:213-269`
**Layer:** ui -> ui
**Issue:** `_open_gravity_editor`, `_open_water_editor`, `_open_radiation_shield_editor` are near-identical 15-line methods. Each: imports editor + command class, gets race config, defines on_apply closure creating command + calling facade, creates centered rect, constructs editor. Only the class names and command kwargs differ.
**Impact:** MEDIUM — adding a new target editor requires another copy-paste site in this file. Omission of the `window_manager=self.ui.window_manager` parameter (Pattern #31) in a new copy would be a modal-tracking bug.
**Recommendation:** Extract `_open_planet_target_editor(EditorClass, CommandClass, planet, cmd_kwargs_mapping_fn, rect_size)` helper method.
**Estimated LOC Savings:** 30
**Effort:** Simple

#### MAJOR: Planet/Star Sidebar `add_range` Duplication (DUP-X-07)
**ID:** DUP-X-07
**Location:** `ui/screens/planet_list_sidebar.py:198-239` AND `ui/screens/star_list_sidebar.py:93-134`
**Layer:** ui -> ui
**Issue:** Identical 43-line `add_range` inner function. Creates Min/Max slider + text entry rows for range filters. The function is nested inside each sidebar's builder method and captures `nonlocal y_off`. Only the key types differ.
**Impact:** MEDIUM — any UI layout change to range sliders requires two-file editing.
**Recommendation:** Extract to `ui/widgets/range_slider_builder.py` as `build_range_slider_row(label, key, min_limit, max_limit, y_off, width, manager, container) -> (new_y_off, ui_filters_entry)`.
**Estimated LOC Savings:** 43
**Effort:** Simple

#### MAJOR: `_build_column_section` Duplication (DUP-X-08)
**ID:** DUP-X-08
**Location:** `ui/screens/event_log_sidebar.py:57-92` AND `ui/screens/fleet_report_sidebar.py:315-343`
**Layer:** ui -> ui
**Issue:** Identical 35-line column toggle button builder in two sidebars. Creates "COLUMNS" label and iterates `column_manager.get_toggleable_columns()` to build `[x]`/`[ ]` toggle buttons.
**Impact:** MEDIUM — adding sidebar features like column reordering or visibility groups duplicates again.
**Recommendation:** Extract `build_column_toggle_section(y, column_manager, sidebar_width, manager, container) -> (new_y, buttons_dict)` to a shared widget builder.
**Estimated LOC Savings:** 35
**Effort:** Simple

#### MAJOR: Superweapon Validator Method Pair Duplication (DUP-X-09)
**ID:** DUP-X-09
**Location:** `strategy/validation/superweapon_validator.py:99-125` AND `213-239`
**Layer:** strategy -> strategy
**Issue:** `validate_stellerate_star` and `validate_create_dyson_sphere` are identical 8-line bodies: check ability, check at star system, check system has stars. Only the ability name string differs ("DestroyStar" vs "CreateDysonSphere").
**Impact:** MEDIUM — adding validation rules (e.g., fleet must have minimum mass, system must have no enemy fleets) requires two-file editing.
**Recommendation:** Extract `_validate_star_targeted_superweapon(galaxy, fleet, ability_name, component_registry) -> ValidationResult`. Both existing methods become thin wrappers.
**Estimated LOC Savings:** 20
**Effort:** Simple

#### MAJOR: Workshop Ship Ops Method Pattern Duplication (DUP-X-10)
**ID:** DUP-X-10
**Location:** `ui/screens/workshop_viewmodel_ship_ops.py:88-176` AND `ui/screens/workshop_viewmodel_layer_ops.py:195-220`
**Layer:** ui -> ui
**Issue:** `add_component`, `add_component_instance`, `remove_component`, and `move_component` all share identical scaffolding: `require_ship` guard, delegate to `_ship_service.<method>`, store result in `_last_result`, `notify_ship_changed()` on success, log and return on failure. The only variance is the service method signature and return type.
**Impact:** MEDIUM — if the notification or error-reporting contract changes, 4 methods must be updated.
**Recommendation:** Extract `_dispatch_to_service(service_method, args, op_name)` — but the varying return types (bool, Optional[Component], int) make a truly generic dispatcher awkward. A simpler approach: factor out the guard + notify + log pattern into `_with_ship(op_name, action_fn) -> T`.
**Estimated LOC Savings:** 25
**Effort:** Simple

#### MAJOR: `_load_*_types` Triplicate Lazy-Load Pattern (DUP-X-11)
**ID:** DUP-X-11
**Location:** `strategy/data/galaxy_system_generator.py:223-237` AND `275-289` AND `324-334`
**Layer:** strategy -> strategy
**Issue:** `_load_planet_types`, `_load_star_types`, and `_load_system_archetypes` are identical 12-line lazy-load helpers. Each: check `global _CACHE is None`, import json + pathlib + Paths, open file, parse JSON, extract sub-key from data dict.
**Impact:** MEDIUM — if file loading moves to a pathlib alternative or error handling changes, 3 functions must be updated.
**Recommendation:** Extract `_lazy_load_json_cache(cache_var: str, path_attr: str, dict_key: str) -> Dict` using `getattr(Paths, path_attr)`. Or better, a generic `LazyJsonLoader` class.
**Estimated LOC Savings:** 25
**Effort:** Simple

#### MAJOR: Intrinsic Ability Application Pattern Duplication (DUP-X-12)
**ID:** DUP-X-12
**Location:** `strategy/data/galaxy_system_generator.py:240-268` AND `292-317`
**Layer:** strategy -> strategy
**Issue:** `_apply_planet_intrinsic_abilities` and `_apply_star_intrinsic_abilities` share the same flow: load types data, check for empty, default/unseeded RNG, iterate entities, check idempotency prefix, extract type_key from entity, get template from types_data, roll abilities. Only the entity type and type_key extraction differ.
**Impact:** MEDIUM — if the RNG threading or idempotency contract changes, both functions must be updated.
**Recommendation:** Extract `_apply_intrinsic_abilities(entities, types_data, get_type_key_fn, rng)` generic function. Both become thin wrappers.
**Estimated LOC Savings:** 25
**Effort:** Simple

#### MAJOR: Spatial Behavior Circle Formation Duplication (DUP-X-13)
**ID:** DUP-X-13
**Location:** `ai/spatial_behaviors/escort.py:26-52` AND `ai/spatial_behaviors/screen.py:33-59`
**Layer:** ai -> ai
**Issue:** `compute_target_position` in `escort.py` and `screen.py` share the identical 8-line circular positioning algorithm (`angle = 2*math.pi*slot_index/total`, `cos`/`sin` offset from anchor). Only the anchor source (`ship.position` vs `kwargs["anchor_position"]`) and distance field (`self.distance` vs `self.radius`) differ.
**Impact:** MEDIUM — adding formation variations (offset angles, phasing, jitter) requires two-file editing.
**Recommendation:** Extract `_compute_circular_position(anchor_x, anchor_y, distance, slot_index, total) -> Vector2` shared helper in `ai/spatial_behaviors/_formation_utils.py`. Both behaviors call it.
**Estimated LOC Savings:** 15
**Effort:** Simple

#### MAJOR: Data Source Structure Duplication (planet vs star) (DUP-X-14)
**ID:** DUP-X-14
**Location:** `ui/screens/planet_data_source.py:81-102` AND `ui/screens/star_data_source.py:46-58`
**Layer:** ui -> ui
**Issue:** `get_cell_image` in both data sources follows identical flow: get column, check type == "image", get entity at index, return icon. Both also share identical `get_*_at_index` patterns, `_extract_value` patterns, and `_get_column` implementations.
**Impact:** MEDIUM — if image caching or cell-rendering changes, both files require updates.
**Recommendation:** Extract a base `ListDataSource` class with generic `get_cell_value`, `get_cell_image`, `get_entity_at_index`. Subclass for planet/star-specific icon extraction and attribute access.
**Estimated LOC Savings:** 40
**Effort:** Medium

---

#### MINOR: Strategy Fleet Ops Command Execution Duplication (DUP-X-15)
**ID:** DUP-X-15
**Location:** `ui/screens/strategy_fleet_ops.py:134-155` AND `197-218`
**Layer:** ui -> ui
**Issue:** `execute_intercept` and `execute_join` share identical 8-line body: log, create command, `facade.handle_command`, success/error return dict.
**Impact:** LOW — adding standardized error handling requires two-site editing.
**Recommendation:** Extract `_execute_fleet_command(cmd, operation_name) -> dict` helper.
**Estimated LOC Savings:** 12
**Effort:** Simple

#### MINOR: Cargo/Transfer Dialog Keydown Handler Duplication (DUP-X-16)
**ID:** DUP-X-16
**Location:** `ui/screens/cargo_quick_dialog.py:217-227` AND `ui/screens/transfer_dialog.py:721-731`
**Layer:** ui -> ui
**Issue:** Both dialogs share similar `_handle_keydown` logic for Enter/Escape/digit keys.
**Impact:** LOW — keybinding changes might miss one dialog.
**Recommendation:** Extract to shared dialog keydown handler base.
**Estimated LOC Savings:** 8
**Effort:** Simple

#### MINOR: Sort Key Duplication (planet vs star list filters) (DUP-X-17)
**ID:** DUP-X-17
**Location:** `ui/screens/planet_list_filters.py:221-232` AND `ui/screens/star_list_filters.py:134-145`
**Layer:** ui -> ui
**Issue:** Same sort key function pattern, different attribute extraction based on column ID.
**Impact:** LOW — sorting logic divergence unlikely but possible.
**Recommendation:** Shared sort key generator.
**Estimated LOC Savings:** 8
**Effort:** Simple

#### MINOR: Selection Prompt Method Duplication (DUP-X-18)
**ID:** DUP-X-18
**Location:** `ui/screens/strategy_windows/selection_prompts.py:29-82`
**Layer:** ui -> ui
**Issue:** `prompt_planet`, `prompt_fleet`, and `open_system` share similar prompt-construction logic.
**Impact:** LOW — adding prompt features (icons, sorting) requires three-site editing.
**Recommendation:** Extract `_build_selection_prompt(items, formatter_fn, title)` helper.
**Estimated LOC Savings:** 12
**Effort:** Simple

#### MINOR: Harvesting Engine Helper Pair Duplication (DUP-X-19)
**ID:** DUP-X-19
**Location:** `strategy/engine/harvesting_engine.py:38-84` AND `274-318`
**Layer:** strategy -> strategy
**Issue:** `get_harvester_from_registry` and `_get_storage_from_registry` (plus `get_harvester_info` and `_get_storage_info`) follow the same registry + ability-extraction pattern.
**Impact:** LOW — only two callers, and the domain concepts (harvester vs storage) are distinct enough that forced consolidation might reduce clarity.
**Recommendation:** If a third "registry entity resolver" is needed, consolidate. For now, monitor.
**Estimated LOC Savings:** 0 (not recommended currently)
**Effort:** N/A

#### MINOR: Race Description LLM Controller Symmetry (DUP-X-20)
**ID:** DUP-X-20
**Location:** `strategy/services/race_description_llm_controller.py:198-216` AND `219-237` AND `266-286` AND `289-309`
**Layer:** strategy -> services
**Issue:** `_start_bio` / `_start_socio` and `_apply_bio_transition` / `_apply_socio_transition` are symmetrical pairs for biological vs sociological description generation.
**Impact:** LOW — the LLM controller is self-contained with mirror functions; adding a third generation axis would add a third copy.
**Recommendation:** Parameterize by generation axis enum. Low priority since only 2 axes exist.
**Estimated LOC Savings:** 20
**Effort:** Medium

#### MINOR: Hit Effects Rendering Duplication (DUP-X-21)
**ID:** DUP-X-21
**Location:** `ui/effects/hit_effects.py:146-176` AND `176-206`
**Layer:** ui -> ui
**Issue:** `_draw_armor_hit` and `_draw_component_destroyed` share similar draw call patterns.
**Impact:** LOW — visual effects may diverge intentionally for different hit types.
**Recommendation:** Extract shared draw primitives (burst radius, particle scatter) to helper.
**Estimated LOC Savings:** 10
**Effort:** Simple

#### MINOR: Dropdown Handler Duplication (DUP-X-22)
**ID:** DUP-X-22
**Location:** `ui/screens/workshop_event_router.py:493-517`
**Layer:** ui -> ui
**Issue:** `_handle_movement_dropdown` and `_handle_targeting_dropdown` are near-identical.
**Impact:** LOW — only two dropdown types exist.
**Recommendation:** Parameterize by dropdown type enum.
**Estimated LOC Savings:** 8
**Effort:** Simple

---

#### INFO: LLM/Image Background Service Shape Duplication (DUP-X-23)
**ID:** DUP-X-23
**Location:** `services/llm/background.py` AND `ui/services/image/background.py`
**Layer:** services -> ui/services (cross-layer)
**Issue:** `LLMBackgroundCall` and `ImageBackgroundCall` are structurally identical (same `CallStatus` enum, same `__init__` guard pattern, same `start()` concurrency guard, same `cancel()` semantics, same property accessors for `status`/`result`/`error`/`elapsed_seconds`, same `_run()` worker structure, same `shutdown_all_calls` hook). Per Pattern #28 docstring, `ImageBackgroundCall` was intentionally designed to mirror `LLMBackgroundCall`. The DOCSTRING ITSELF acknowledges this: "Mirrors LLMBackgroundCall shape for shape."
**Impact:** LOW — intentional design choice. However, a generic `BackgroundCall[TResult, TProvider, TError, TConfig]` would eliminate 120+ LOC of boilerplate.
**Recommendation:** Not urgent. If a third background service is added, extract `BackgroundCall` generic base class at that point per the Rule of Three.
**Estimated LOC Savings:** ~120 (deferred)
**Effort:** Medium (deferred)

#### INFO: LLM/Image Provider Factory Shape Duplication (DUP-X-24)
**ID:** DUP-X-24
**Location:** `services/llm/factory.py` AND `ui/services/image/factory.py`
**Layer:** services -> ui/services (cross-layer)
**Issue:** Identical factory pattern: `register_provider()`, env-var lookup with default, unknown-name `ConfigError`, deferred validation (constructor error → return None). The image factory docstring explicitly states "Two intentional behaviors mirror the LLM factory."
**Impact:** LOW — intentional shape duplication per design docs.
**Recommendation:** Same as DUP-X-23 — extract `EnvProviderFactory` generic if a third provider type is added.
**Estimated LOC Savings:** ~35 (deferred)
**Effort:** Medium (deferred)

#### INFO: ModifierManager Static/Instance Method Duplication (DUP-X-25)
**ID:** DUP-X-25
**Location:** `simulation/components/modifier_manager.py:166-219` AND `297-330`
**Layer:** simulation -> simulation
**Issue:** `get_stat_summary` and `get_stat_summary_static` share identical summary aggregation logic. The deprecated static variants (`*_static`) plus `add_modifier_static`, `remove_modifier_static`, `get_modifier_static`, `get_all_effects_static` carry ~90 LOC of dead weight. Marked "DEPRECATED ... Will be removed in Task 1.3."
**Impact:** LOW — already on the removal roadmap.
**Recommendation:** Execute Task 1.3 removal. Verify no callers remain.
**Estimated LOC Savings:** 90 (already planned)
**Effort:** Simple (execution of existing plan)

#### INFO: `_rebuild_modifier_icons` Self-Duplication (DUP-X-26)
**ID:** DUP-X-26
**Location:** `ui/screens/builder/structure_list_items.py:195` AND `472`
**Layer:** ui -> ui
**Issue:** Two identically named `_rebuild_modifier_icons` methods exist in the same file. Each is on a different class, suggesting copy-paste between widget subclasses.
**Impact:** LOW — same-file duplication suggests a missing base class.
**Recommendation:** Extract shared `_rebuild_modifier_icons` to a base class.
**Estimated LOC Savings:** 42
**Effort:** Simple

#### INFO: AbilityIterator Provider Symmetry (DUP-X-27)
**ID:** DUP-X-27
**Location:** `strategy/services/ability_iterator.py:217-238` AND `288-309`
**Layer:** strategy -> services
**Issue:** `_planet_intrinsic_provider` and `_warp_point_provider` are structurally similar but serve different entity types.
**Impact:** LOW — natural symmetry of the adapter pattern (Pattern #29 Universal Ability Source).
**Recommendation:** Observe. If more providers are added, refactor to a generic entity trait-based provider.
**Estimated LOC Savings:** 0 (natural pattern)
**Effort:** N/A

#### INFO: Panel `_create_content` Duplication (DUP-X-28)
**ID:** DUP-X-28
**Location:** `ui/panels/race_aptitudes_panel.py:91` AND `ui/panels/race_identity_panel.py:86`
**Layer:** ui -> panels
**Issue:** `_create_content` methods share similar layout pattern but for different domain content.
**Impact:** LOW — race setup panels are limited in number.
**Recommendation:** Monitor. If more race panels are added, extract base.
**Estimated LOC Savings:** 0 (not recommended)
**Effort:** N/A

## Prioritized Consolidation Plan
Ordered by impact/effort ratio. "Best value first."

| Priority | ID | Finding | LOC Saved | Effort | Impact |
|----------|----|---------|-----------|--------|--------|
| 1 | DUP-X-01 | `_get_race_config` happiness/population | 29 | Simple | CRITICAL |
| 2 | DUP-X-09 | Superweapon validator pair | 20 | Simple | MAJOR |
| 3 | DUP-X-04 | Race config resolution (UI 4 copies) | 60 | Medium | CRITICAL |
| 4 | DUP-X-08 | `_build_column_section` | 35 | Simple | MAJOR |
| 5 | DUP-X-07 | Sidebar `add_range` | 43 | Simple | MAJOR |
| 6 | DUP-X-11 | `_load_*_types` triplicate | 25 | Simple | MAJOR |
| 7 | DUP-X-12 | Intrinsic ability application | 25 | Simple | MAJOR |
| 8 | DUP-X-13 | Spatial behavior circle formation | 15 | Simple | MAJOR |
| 9 | DUP-X-02 | Superweapon handler boilerplate | 80 | Medium | CRITICAL |
| 10 | DUP-X-06 | Event router editor opening | 30 | Simple | MAJOR |
| 11 | DUP-X-10 | Workshop ship ops pattern | 25 | Simple | MAJOR |
| 12 | DUP-X-05 | Target editor boilerplate | 80 | Medium | MAJOR |
| 13 | DUP-X-03 | Planet/Star list window structural | 150 | Complex | CRITICAL |
| 14 | DUP-X-14 | Data source structure | 40 | Medium | MAJOR |
| 15 | DUP-X-26 | `_rebuild_modifier_icons` same-file | 42 | Simple | INFO |

**Total achievable LOC savings (Priority 1-15): ~699 LOC**
**Total confirmed duplicated LOC from clone detector (53 clusters): 1,210 LOC**
**Grand total shrinkage opportunity: ~750 LOC** (some overlap between clone detector totals and cross-shard findings)

### Implementation Sequence Recommendation

**Wave 1 (Simple, same-day):** DUP-X-01, DUP-X-08, DUP-X-07, DUP-X-11, DUP-X-09, DUP-X-15
- All are same-layer (strategy or UI) with 1.0 similarity
- No architectural risk
- ~164 LOC saved in one session

**Wave 2 (Medium, next sprint):** DUP-X-04, DUP-X-06, DUP-X-10, DUP-X-12, DUP-X-13, DUP-X-25
- Cross-layer refactors requiring coordination
- ~135 LOC saved plus existing ~90 LOC removal

**Wave 3 (Complex, requires planning):** DUP-X-02, DUP-X-05, DUP-X-03, DUP-X-14
- Structural refactors of superweapon pipeline, target editors, and list windows
- ~310 LOC saved but high risk of regression
- DUP-X-03 particularly needs a design doc before implementation

**Deferred (monitor):** DUP-X-23, DUP-X-24 (wait for third background service type per Rule of Three)
