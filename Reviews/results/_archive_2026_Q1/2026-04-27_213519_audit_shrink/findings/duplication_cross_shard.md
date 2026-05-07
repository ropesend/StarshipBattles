# Cross-Shard Duplication Report
## Summary
- Files Scanned: 656 (all .py under game/)
- Total Findings: 52
- Critical: 8 | Major: 19 | Minor: 16 | Info: 9

---

## Clone Detector Validation

### Cluster 1 — 5 superweapon click handlers — CONFIRMED
5 identical 13-line methods in `strategy_click_dispatcher.py:283-356`. Each: left-click dispatches to `_superweapons.handle_*_designation()`, right-click resets `input_mode='SELECT'`. Only the method dispatched to differs. Consolidate into `_dispatch_superweapon_click(mx, my, button, designation_method)` driven by mapping dict.

### Cluster 2 — 4 _get_active_race_config — CONFIRMED
4 identical 13-line methods in 4 target editors. Same logic: dropdown check -> `get_selected_race_id()` -> `load_race_config()` -> `_default_race_id` fallback -> `self.race_config`. Move to shared mixin base class.

### Cluster 3 — 4 component manipulation methods — DOWNRATED
`move_component`, `add_component`, `add_component_instance`, `remove_component` in workshop viewmodel files. Each delegates to a different service method with different signatures. The `_require_ship` + `notify_ship_changed()` pattern is deliberate MVVM convention. No consolidation recommended.

### Cluster 4 — 3 planetary Ability __init__ — CONFIRMED
3 near-identical `__init__` methods in `planetary.py:453,528,728`. Each repeats `isinstance(data, dict)` + `data.get(field, default)` pattern. Extract shared `_init_fields(data, defaults_dict)` helper or use Pydantic-style field extraction.

### Cluster 5 — 3 process_event in target editors — CONFIRMED
3 identical 24-line `process_event` methods (atmosphere, gravity, water). Same 4-button handler pattern + window close. Template Method base class needed. Radiation shield editor has slightly different buttons (3 vs 4) but shares 80% structure.

### Cluster 6 — 3 mode-click handlers — CONFIRMED
3 identical 12-line cargo/transfer mode handlers in `strategy_click_dispatcher.py:205-260`. Same left-dispatch + right-cancel pattern. Consolidate into registry-driven dispatch.

### Cluster 7 — 3 superweapon designation handlers — CONFIRMED
3 very similar 44-line methods in `strategy_superweapons.py`. Each shares: fleet null check -> ability check -> screen_to_world -> pixel_to_hex -> system lookup. Diverge in action (confirmation dialog vs system picker). ~80% shared structure. Extract `_resolve_superweapon_target()` preamble.

### Cluster 8 — 3 simple command execute methods — CONFIRMED
StellerateStar, CreateDysonSphere, SelfDestruct handlers in `superweapon_command_handlers.py:73,157,182`. Identical 3-step pattern: resolve fleet -> validate -> create order. Parameterized base template: `_execute_simple_order(fleet_id, ability_name, validator_fn, order_type)`.

### Cluster 9 — 3 _open_*_editor methods — CONFIRMED
`strategy_event_router.py:234-314`. Each: resolve race_config -> create callback -> create window. Extract `_open_target_editor(editor_class, command_class, planet, window_size)`.

### Cluster 10 — 3 _load_*_types — DOWNRATED
Different JSON files with different data shapes. The cache pattern is identical but data semantics differ. Low priority.

### Cluster 11 — 3 planet target set command handlers — CONFIRMED
`planet_command_handlers.py:163,184,205`. Identical: resolve planet -> ownership check -> set attribute -> log -> success. Extract `_set_planet_target(planet_id, attr_name, value, log_label)`.

### Cluster 12 — 3 selection prompt methods — DOWNRATED
Different domain objects with different prompt structures. Insufficient overlap for clean consolidation.

### Cluster 13 — 2 _rebuild_modifier_icons — CONFIRMED (CRITICAL)
42 LOC of 100% identical code in same file (`structure_list_items.py:195,472`). Copy-paste duplication. Delete the redundant copy.

### Cluster 14 — 2 _get_race_config — CONFIRMED (CRITICAL)
29 LOC identical in `happiness_engine.py:95` and `population_engine.py:164`. Both implement PROJ-291 C3 resolution. Extract shared utility.

### Cluster 15 — 2 _build_column_section — CONFIRMED
35 LOC identical in `event_log_sidebar.py:57` and `fleet_report_sidebar.py:315`. Same column toggle button construction. Extract to shared sidebar base class.

### Cluster 16 — 2 add_range — CONFIRMED
43 LOC identical in `planet_list_sidebar.py:135` and `star_list_sidebar.py:93`. Same range slider factory. Extract `RangeFilterFactory` utility.

### Cluster 17 — 2 superweapon validators — CONFIRMED
`validate_stellerate_star` and `validate_create_dyson_sphere` share identical structure (require ability + require at star system + check stars). Extract `_validate_star_based_superweapon()`.

### Cluster 18 — 2 _save_preset — CONFIRMED
16 LOC identical in `planet_list_window.py:444` and `star_list_window.py:403`. Move to shared mixin.

### Cluster 19 — 2 _toggle_column — CONFIRMED
10 LOC identical. Move to shared mixin.

### Cluster 20 — 2 update methods — CONFIRMED
41 LOC ~95% similar. Only filter key names differ. Extract base class.

### Cluster 21 — 2 draw methods in hit_effects — DOWNRATED
Combat visual effects with legitimate variation.

### Cluster 22 — 2 battle setup controller methods — DOWNRATED
8-line similarity, fundamentally different operations.

### Cluster 23 — 2 keydown handlers — DOWNRATED
Different supported keys and actions.

### Cluster 24 — 2 __init_subclass__ — DOWNRATED
Legitimate metaclass registration pattern.

### Cluster 25 — 2 superweapon mission handlers — CONFIRMED
Same pattern as Cluster 8 but with move-order preamble. Consolidated together with Cluster 8.

### Cluster 26 — 2 helper methods in planet_action_engine — DOWNRATED
Different domain property queries.

### Cluster 27 — 2 effects methods in system_tree_panel — DOWNRATED
Sector vs system scope — legitimate difference.

### Cluster 28 — 2 transition methods in race_description_llm_controller — DOWNRATED
Different LLM endpoint schemas.

### Cluster 29 — 2 get_stat_summary — CONFIRMED (CRITICAL)
53 LOC exact duplicate. `get_stat_summary()` (instance) vs `get_stat_summary_static()` (static). Migration artifact from Task 1.3. Static version marked DEPRECATED.

### Cluster 30 — 2 sort_key methods — DOWNRATED
Different filter categories.

### Cluster 31 — 2 pick methods in race_randomizer — DOWNRATED
Different data sources, different semantics.

### Cluster 32 — 2 dropdown handlers in workshop — DOWNRATED
Different dropdown types.

### Cluster 33 — 2 group_components — DOWNRATED
Different grouping strategies — legitimate Strategy pattern.

### Cluster 34 — 2 filter set-all methods — CONFIRMED
`_set_all_filters()` in planet vs `_set_all_type_filters()` in star. Subsumed by DUP-X-002 base class consolidation.

### Cluster 35 — 2 _create_content methods — DOWNRATED
Different panel content.

### Cluster 36 — 2 execute methods in superweapon handlers — CONFIRMED
Part of broader Cluster 8/25 pattern. Consolidated together.

### Cluster 37 — 2 dialog methods in tkinter_utils — DOWNRATED
Load vs save dialogs — legitimate mirror operations.

### Cluster 38 — 2 __init__ test lab panels — DOWNRATED
Different widget configurations.

### Cluster 39 — 2 provider methods in ability_iterator — DOWNRATED
Different ability source types.

### Cluster 40 — 2 _start_* methods in LLM controller — DOWNRATED
Different LLM schemas and prompts.

### Cluster 41 — 2 get_cell_image — DOWNRATED
Planet vs star icon rendering — legitimate domain variation.

### Cluster 42 — 2 cargo methods in fleet_consumable_aggregator — DOWNRATED
Load/unload mirror operations.

### Cluster 43 — 2 execute methods in fleet_ops — DOWNRATED
Intercept vs join are different operations.

### Cluster 44 — 2 compute_target_position — CONFIRMED
Identical circular distribution math in `escort.py:46-52` and `screen.py:51-57`. Extract `compute_circular_position(center, radius, slot, total) -> Vector2`.

### Cluster 45 — 2 superweapon execute methods — CONFIRMED
Two more mission handlers with same structure. Consolidated with Cluster 8/25/36.

### Cluster 46 — 2 add resources methods — DOWNRATED
Empire.add_resources vs Planet.add_to_stockpile — different data models.

### Cluster 47 — 2 registry methods in harvesting_engine — DOWNRATED
Different registry lookups.

### Cluster 48 — 2 info methods in harvesting_engine — DOWNRATED
Storage vs harvester info — different queried data.

### Cluster 49 — 2 ability application methods — DOWNRATED
Planet intrinsic vs star intrinsic — different roll mechanics.

**Validation Summary:** 29 confirmed genuine, 20 downrated (different semantics or legitimate pattern variation).

---

## Cross-Shard Findings

### CRITICAL: Target Editor Class Family — No Shared Base Class
**ID:** DUP-X-001
**Location:** `atmosphere_target_editor.py`, `gravity_target_editor.py`, `water_target_editor.py`, `radiation_shield_editor.py`
**Layer:** UI
**Issue:** Four target editors share 80%+ methods (`process_event`, `_get_active_race_config`, `_on_apply`, `_set_species_ideal`, `_set_match_current`, `_clear_target`, `update`) with only slider/value-type differences. No shared base class. Violates Template Method pattern (Pattern #9).
**Impact:** Any UI change to button handling, event routing, or species resolution must be made in 4 files.
**Recommendation:** Create `TargetEditorBase` with Template Method. Abstract: `_get_current_value()`, `_apply_target()`, `_format_display()`. Concrete: `process_event()`, `_get_active_race_config()`.
**Estimated LOC Savings:** ~200
**Effort:** Medium

### CRITICAL: PlanetListWindow / StarListWindow — Near-Twin Classes
**ID:** DUP-X-002
**Location:** `planet_list_window.py` (595 lines) AND `star_list_window.py` (462 lines)
**Layer:** UI
**Issue:** Two major UI windows share 90%+ structural similarity across `update()`, `process_event()`, `_toggle_column()`, `_save_preset()`, preset management, column management, header sort/swap, virtual table integration. Only filter keys, data sources, and column IDs differ. Sub-files also duplicated: filter managers, presets, sidebars, data sources.
**Impact:** Every bug fix must be mirrored. Copy-paste drift already visible (different filter key names).
**Recommendation:** Extract `FilterableTableWindow` base class. Planet/star variants become thin subclasses providing data source, filter config, column definitions.
**Estimated LOC Savings:** ~300
**Effort:** Complex

### CRITICAL: Race Config Resolution — 4 Duplicated Implementations
**ID:** DUP-X-003
**Location:** `species_selector_mixin.py:111` (UI), `strategy_event_router.py:349` (UI), `happiness_engine.py:95` (Strategy), `population_engine.py:164` (Strategy)
**Layer:** UI -> Strategy (cross-layer)
**Issue:** Four different implementations with different fallback logic:
- `species_selector_mixin.load_race_config()`: Creates new `RaceLibrary()` with broad-exception catch
- `strategy_event_router._get_race_config()`: Goes through `empire.race_config`, then `RaceLibrary`
- `happiness_engine._get_race_config()`: PROJ-291 C3 resolution via `_race_registry`, then `empire.race_config`
- `population_engine._get_race_config()`: Identical to happiness_engine (Cluster 14)
**Impact:** Multi-species scenarios could produce inconsistent results between UI display and engine calculation. PROJ-291 established C3 order but only strategy engines follow it.
**Recommendation:** Promote C3 resolution to `game/strategy/services/race_config_resolver.py`. Both layers use same function.
**Estimated LOC Savings:** ~80
**Effort:** Medium

### CRITICAL: ModifierManager Static/Instance Duplication — Migration Artifact
**ID:** DUP-X-004
**Location:** `simulation/components/modifier_manager.py:166-330`
**Layer:** Simulation
**Issue:** 6 methods duplicated as static + instance versions: `get_stat_summary`/`_static`, `get_all_effects`/`_static`, `add_modifier`/`_static`, `remove_modifier`/`_static`, `get_modifier`/`_static`, `remove_modifier_inplace` (static only). All static variants marked DEPRECATED "Task 1.3 transition". ~160 LOC of dead weight.
**Impact:** Every developer must understand both code paths. Static methods still callable and could be used inadvertently.
**Recommendation:** Complete migration. Remove all static variants. Verify no callers remain.
**Estimated LOC Savings:** ~160
**Effort:** Simple

### CRITICAL: SuperweaponCommandHandlers — 5-Layer Template Missing
**ID:** DUP-X-005
**Location:** `strategy/engine/superweapon_command_handlers.py` (372 lines)
**Layer:** Strategy
**Issue:** Two families of handlers (3 simple + 5 mission) repeat identical structure. Simple: resolve fleet + validate + create order. Mission: resolve fleet + validate + add move + add action order. Only ability name, validator, and OrderType differ. Violates the CommandHandlerRegistry pattern.
**Impact:** 372-line file could be reduced to ~120 lines. Every new superweapon requires copy-pasting entire handler class.
**Recommendation:** Create `SimpleSuperweaponHandler` and `MissionSuperweaponHandler` parameterized base classes with ability name, validator, OrderType as class attributes.
**Estimated LOC Savings:** ~200
**Effort:** Medium

### CRITICAL: StrategyClickDispatcher — Registry-Driven Dispatch Missing
**ID:** DUP-X-006
**Location:** `strategy_click_dispatcher.py:205-356`
**Layer:** UI
**Issue:** 8 click handler methods (5 superweapon + 3 mode) are identical except for the method they dispatch to and `input_mode` value. Could be driven by a mapping dict keyed on `input_mode`.
**Impact:** 110+ LOC of mechanically identical code. Adding a new click mode requires copy-pasting.
**Recommendation:** Replace with dict-driven single click handler. Use `input_mode` as dict key.
**Estimated LOC Savings:** ~90
**Effort:** Simple

### CRITICAL: Planetary Ability __init__ Template Missing
**ID:** DUP-X-007
**Location:** `simulation/components/abilities/planetary.py:453,528,728`
**Layer:** Simulation
**Issue:** Three Ability `__init__` methods repeat identical `isinstance(data, dict)` + `data.get(...)` pattern. Same pattern exists across weapons, defense, and other ability classes.
**Impact:** Every new ability requires copy-pasting init boilerplate. Error in one propagates.
**Recommendation:** Provide `_init_fields(data, field_defaults: dict) -> dict` base class helper.
**Estimated LOC Savings:** ~60 (planetary.py) + ~200 (across all ability classes)
**Effort:** Medium

### CRITICAL: PlanetDataSource / StarDataSource — Near-Twin Data Sources
**ID:** DUP-X-008
**Location:** `planet_data_source.py` (220 lines) AND `star_data_source.py` (123 lines)
**Layer:** UI
**Issue:** Two data source classes share identical `_get_column()`, `_extract_value()`, `get_cell_value()`, `get_row_count()`, `get_columns()`, `update_data()`. Only domain object (planet vs star) and icon caching logic differ. `_extract_value()` is 30 LOC of EXACT duplicate code in both files.
**Impact:** NEW finding missed by clone detector. Any fix to `_extract_value` must be applied in both files.
**Recommendation:** Extract `AbstractTableDataSource<T>` base class with shared logic. Subclasses provide `_get_icon()` and `update_data()`.
**Estimated LOC Savings:** ~105 (combined)
**Effort:** Medium

---

### MAJOR: PlanetListFilterManager / StarListFilterManager — Near-Twin
**ID:** DUP-X-009
**Location:** `planet_list_filter_manager.py` (127 lines) AND `star_list_filter_manager.py` (85 lines)
**Layer:** UI
**Issue:** Two filter managers with identical structure: types dict, range dict, search text, `toggle_type()`, `set_all_types()`, `get_filter_state()`. Only type constants and range keys differ.
**Impact:** NEW finding missed by clone detector. The file header even says "Mirrors PlanetListFilterManager."
**Recommendation:** Extract `FilterStateManager<T>` generic base with type constants and range keys as class attributes.
**Estimated LOC Savings:** ~70
**Effort:** Medium

### MAJOR: capture/apply *_list_state — Near-Twin Functions
**ID:** DUP-X-010
**Location:** `planet_list_presets.py` AND `star_list_presets.py`
**Layer:** UI
**Issue:** `capture_planet_list_state`/`capture_star_list_state` and `apply_planet_list_state`/`apply_star_list_state` share identical column reordering, filter restoration, and UI toggle update logic. Only slider key names and filter category names differ. `StarPresetManager` already subclasses `PresetManager` — the capture/apply functions should follow the same pattern.
**Impact:** NEW finding. 130+ LOC of structural duplication.
**Recommendation:** Extract `_capture_list_state_base()` and `_apply_list_state_base()` with range keys and filter categories as parameters.
**Estimated LOC Savings:** ~80
**Effort:** Medium

### MAJOR: PlanetCommandHandlers — 3 Identical Set-Target Handlers
**ID:** DUP-X-011
**Location:** `strategy/engine/planet_command_handlers.py:163-220`
**Layer:** Strategy
**Issue:** SetGravityTarget, SetWaterTarget, SetRadiationShieldTarget share identical structure. Only planet attribute name and log format differ.
**Recommendation:** Single `SetPlanetTargetCommandHandler` with config mapping command type to planet attribute.
**Estimated LOC Savings:** ~50
**Effort:** Simple

### MAJOR: Event Log / Fleet Report Sidebar Column Section
**ID:** DUP-X-012
**Location:** `event_log_sidebar.py:57` AND `fleet_report_sidebar.py:315`
**Layer:** UI
**Issue:** 35 LOC identical `_build_column_section()`. Both create COLUMNS label + column toggle buttons.
**Recommendation:** Extract `ColumnToggleSection` sidebar widget.
**Estimated LOC Savings:** ~30
**Effort:** Simple

### MAJOR: Planet List / Star List Sidebar add_range
**ID:** DUP-X-013
**Location:** `planet_list_sidebar.py:135` AND `star_list_sidebar.py:93`
**Layer:** UI
**Issue:** 43 LOC identical `add_range()` nested functions. Create min/max sliders + text boxes.
**Recommendation:** Extract `RangeFilterFactory.create_range_filter()` utility.
**Estimated LOC Savings:** ~40
**Effort:** Simple

### MAJOR: AI Spatial compute_target_position
**ID:** DUP-X-014
**Location:** `ai/spatial_behaviors/escort.py:46-52` AND `ai/spatial_behaviors/screen.py:51-57`
**Layer:** AI
**Issue:** EXACT same circular distribution math: `angle = (2*pi*slot)/total`, `target = center + cos/sin * radius`.
**Recommendation:** Extract `compute_circular_position(center, radius, slot, total) -> Vector2` into `ai/combat_utils.py`.
**Estimated LOC Savings:** ~15
**Effort:** Simple

### MAJOR: SuperweaponValidator — validate_stellerate_star / validate_create_dyson_sphere
**ID:** DUP-X-015
**Location:** `strategy/validation/superweapon_validator.py:99,213`
**Layer:** Strategy
**Issue:** Two validators share identical: `_require_ability()`, `_require_at_star_system()`, check `system.stars`. Only ability name differs.
**Recommendation:** Extract `_validate_star_based_superweapon(fleet, ability_name, galaxy, component_registry)`.
**Estimated LOC Savings:** ~20
**Effort:** Simple

### MAJOR: _rebuild_modifier_icons — Copy-Pasted Within Same File
**ID:** DUP-X-016
**Location:** `ui/screens/builder/structure_list_items.py:195,472`
**Layer:** UI
**Issue:** 42 LOC identical within the same file. Likely copy-paste error.
**Recommendation:** Delete the redundant copy. Verify only one caller.
**Estimated LOC Savings:** ~42
**Effort:** Simple

### MAJOR: Strategy Event Router Editor Openers
**ID:** DUP-X-017
**Location:** `strategy_event_router.py:234-314`
**Layer:** UI
**Issue:** `_open_gravity_editor()`, `_open_water_editor()`, `_open_radiation_shield_editor()` share: resolve race_config -> create `on_apply` callback -> create editor window. Only editor class and target parameter differ. `_open_atmosphere_editor()` above also follows this pattern but was not in cluster 9.
**Recommendation:** Single `_open_target_editor(editor_class, command_class, planet, window_rect)`.
**Estimated LOC Savings:** ~60
**Effort:** Simple

### MAJOR: _load_*_types Cached JSON Loader Pattern
**ID:** DUP-X-018
**Location:** `galaxy_system_generator.py:223,275` AND `galaxy_warp_generator.py:381`
**Layer:** Strategy
**Issue:** Three functions with identical caching pattern: module-level cache, `if cache is None` guard, `Path(path)`, `json.load()`, `.get(section_key, {})`. Only file path and section key differ.
**Recommendation:** Extract `_load_json_cached(file_path: str, section_key: str) -> dict` utility.
**Estimated LOC Savings:** ~30
**Effort:** Simple

### MAJOR: Strategy Superweapons Designation Preamble
**ID:** DUP-X-019
**Location:** `strategy_superweapons.py:119-289`
**Layer:** UI
**Issue:** Three 44-line handlers share preamble: fleet null check -> ability capability check -> `screen_to_world` -> `pixel_to_hex` -> system lookup. Diverge only in specific action.
**Recommendation:** Extract `_resolve_superweapon_target(mx, my, fleet, ability_name)` returning `(system, error_dict)`.
**Estimated LOC Savings:** ~80
**Effort:** Medium

### MAJOR: harvesting_engine — get_harvester vs get_storage Proxy Methods
**ID:** DUP-X-020
**Location:** `harvesting_engine.py:38,67,274,301`
**Layer:** Strategy
**Issue:** `get_harvester_info`/`_get_storage_info` follow same pattern checking component dict/list types, then delegating to registry. `get_harvester_from_registry`/`_get_storage_from_registry` share identical registry lookup + ability extraction pattern.
**Recommendation:** Extract `_get_ability_from_registry(comp_id, registries, ability_name)` utility.
**Estimated LOC Savings:** ~40
**Effort:** Simple

### MAJOR: Planet Action Engine — _get_energy_drain_rate / _get_deactivation_time
**ID:** DUP-X-021
**Location:** `strategy/engine/planet_action_engine.py:313,328`
**Layer:** Strategy
**Issue:** Both methods iterate facility components to find matching comp_id, then extract a specific field from ability data. Identical iteration pattern, different field accessed.
**Recommendation:** Extract `_get_ability_field(facility, comp_id, ability_name, field_name, default)`.
**Estimated LOC Savings:** ~20
**Effort:** Simple

### MAJOR: _recognize_ship_type Hardcoded List Pattern
**ID:** DUP-X-022
**Location:** `ui/screens/strategy_fleet_command_router.py:250-268` AND `ui/screens/strategy_detail_fmt.py:411-425` AND `ui/screens/strategy_detail_formatter.py:305-315`
**Layer:** UI (3 files)
**Issue:** NEW finding. Three UI files import `extract_abilities_from_component` from Strategy layer and iterate ship components checking for specific ability names with near-identical patterns. This is business logic (ability classification) leaking into the UI layer.
**Impact:** Adding a new ability type requires changes in multiple UI files. UI layer shouldn't be doing ability introspection.
**Recommendation:** Add facade-level methods like `fleet.has_ability(ability_name)` and `fleet.get_ability_description(ability_name)`. Remove raw ability extraction from UI.
**Estimated LOC Savings:** ~40
**Effort:** Medium

### MAJOR: Workshop Pattern Duplication — _require_ship + notify_ship_changed
**ID:** DUP-X-023
**Location:** `workshop_viewmodel_layer_ops.py` (15 calls) AND `workshop_viewmodel_ship_ops.py` (11 calls)
**Layer:** UI
**Issue:** NEW finding. Every (non-trivial) method in both files wraps its operation in `_require_ship()` guard + `notify_ship_changed()` on success. These could use a decorator or `@contextmanager` wrapper.
**Recommendation:** Add `@requires_ship` decorator or `with self._ship_mutation() as ship:` context manager that handles the guard + notification.
**Estimated LOC Savings:** ~50
**Effort:** Medium

---

### MINOR: Hit Effects draw methods
**ID:** DUP-X-030
**Location:** `ui/effects/hit_effects.py:146,176`
**Layer:** UI
**Issue:** `_draw_armor_hit` / `_draw_component_destroyed` share visual structure. Legitimate variation.
**Recommendation:** Low priority.
**Estimated LOC Savings:** ~10
**Effort:** Low

### MINOR: Race Description LLM Controller transitions
**ID:** DUP-X-031
**Location:** `strategy/services/race_description_llm_controller.py:198,219,266,289`
**Layer:** Strategy
**Issue:** `_start_bio`/`_start_socio` and `_apply_bio_transition`/`_apply_socio_transition` are parallel paths with different LLM schemas.
**Recommendation:** No consolidation — diverge by design.
**Estimated LOC Savings:** 0
**Effort:** N/A

### MINOR: Workshop Event Router Dropdown Handlers
**ID:** DUP-X-032
**Location:** `ui/screens/workshop_event_router.py:493,505`
**Layer:** UI
**Issue:** `_handle_movement_dropdown` / `_handle_targeting_dropdown` share dropdown selection extraction + command dispatch pattern.
**Recommendation:** Extract `_handle_policy_dropdown(event, command_class)`.
**Estimated LOC Savings:** ~10
**Effort:** Simple

### MINOR: Planet/Star List sort_key
**ID:** DUP-X-033
**Location:** `planet_list_filters.py:134` AND `star_list_filters.py:134`
**Layer:** UI
**Issue:** Two `sort_key` methods with same lambda structure. Subsumed by DUP-X-002.
**Estimated LOC Savings:** Included in DUP-X-002
**Effort:** Included

### MINOR: Cargo/Fleet Consumable load/unload symmetry
**ID:** DUP-X-034
**Location:** `fleet_consumable_aggregator.py:291,317`
**Layer:** Strategy
**Issue:** Mirror operations — expected structural symmetry.
**Estimated LOC Savings:** 0
**Effort:** N/A

### MINOR: Empire/Planet add_resources symmetry
**ID:** DUP-X-035
**Location:** `empire.py:187` AND `planet.py:279`
**Layer:** Strategy
**Issue:** Different data models — legitimate variation.
**Estimated LOC Savings:** 0
**Effort:** N/A

### MINOR: Ability Iterator providers
**ID:** DUP-X-036
**Location:** `strategy/services/ability_iterator.py:213,284`
**Layer:** Strategy
**Issue:** `_planet_intrinsic_provider` / `_warp_point_provider` share ability scanning pattern for different domains.
**Recommendation:** Low priority — IAbilitySource interface may naturally converge.
**Estimated LOC Savings:** ~15
**Effort:** Simple

### MINOR: Race Randomizer pick methods
**ID:** DUP-X-037
**Location:** `strategy/systems/race_randomizer.py:109,127`
**Layer:** Strategy
**Issue:** `_pick_name_entry` / `_pick_leader` share weighted-random-pick-from-dict pattern.
**Recommendation:** Extract `_weighted_pick(data: dict, rng)`.
**Estimated LOC Savings:** ~10
**Effort:** Simple

### MINOR: Test Lab Panel __init__ patterns
**ID:** DUP-X-038
**Location:** `ui/screens/test_lab/renderer/category_panel.py:28` AND `test_list_panel.py:27`
**Layer:** UI
**Issue:** pygame_gui element creation pattern with different widget configurations.
**Estimated LOC Savings:** ~15
**Effort:** Simple

### MINOR: Grouping Strategies
**ID:** DUP-X-039
**Location:** `ui/screens/builder/grouping_strategies.py:18,53`
**Layer:** UI
**Issue:** Two `group_components` implementations — legitimate Strategy pattern variation.
**Estimated LOC Savings:** 0
**Effort:** N/A

### MINOR: Battle Setup Controller — delete/duplicate squadron
**ID:** DUP-X-040
**Location:** `ui/screens/battle_setup/controller.py:278,288`
**Layer:** UI
**Issue:** 8-line similarity with different operations.
**Estimated LOC Savings:** 0
**Effort:** N/A

### MINOR: planet_action_engine — _get_energy_drain_rate / _get_deactivation_time
**ID:** DUP-X-041
**Location:** `strategy/engine/planet_action_engine.py:313,328`
**Layer:** Strategy
**Issue:** Duplicated in Cluster 26, now folded into DUP-X-021 above.
**Estimated LOC Savings:** Included in DUP-X-021
**Effort:** Included

### MINOR: Cargo/Transfer dialog keydown handlers
**ID:** DUP-X-042
**Location:** `cargo_quick_dialog.py:209` AND `transfer_dialog.py:714`
**Layer:** UI
**Issue:** Similar key handling with different supported keys.
**Estimated LOC Savings:** ~5
**Effort:** Simple

### MINOR: _set_all_filters / _set_all_type_filters — Different Method Names
**ID:** DUP-X-043
**Location:** `planet_list_window.py:412` AND `star_list_window.py:371`
**Layer:** UI
**Issue:** Same pattern with different method names and signatures. Subsumed by DUP-X-002.
**Estimated LOC Savings:** Included in DUP-X-002
**Effort:** Included

---

### INFO: Serialization Protocol Conformance (Not Duplication)
**ID:** DUP-X-050
**Location:** 45+ classes across all layers
**Layer:** All
**Issue:** `to_dict()` / `from_dict()` methods on 45+ classes. Expected Protocol conformance (Serializable Protocol, Pattern #17). Each entity has domain-specific serialization logic.
**Recommendation:** No action needed — architectural conformance.

### INFO: to_dict/from_dict Field Extraction Boilerplate
**ID:** DUP-X-051
**Location:** 45+ `from_dict()` methods across strategy/data and simulation
**Layer:** All
**Issue:** Many `from_dict()` methods repeat `data.get(key, default)` pattern for dozens of fields. `ship_serialization.py:129`, `battle_state.py:480,632`, `fleet.py:430`, `planet.py:499`, `galaxy.py:624` among the largest.
**Recommendation:** Lightweight schema helper for common patterns. Low priority.
**Estimated LOC Savings:** ~200 (long-term)
**Effort:** Complex

### INFO: Validation Result Pattern Consistency
**ID:** DUP-X-052
**Location:** `strategy/validation/` package (4 files)
**Layer:** Strategy
**Issue:** Four validator classes use `ValidationResult` with varying method signatures. `SuperweaponValidator` uses static methods; others use instance. `ColonizeValidator` mirrors `SuperweaponValidator`'s `_require_ability` pattern.
**Recommendation:** Standardize validator signatures. Extract common validation primitives.
**Estimated LOC Savings:** ~40
**Effort:** Medium

### INFO: Hex/Coordinate Math — Single Source of Truth Confirmed
**ID:** DUP-X-053
**Location:** `core/hex_math.py`, `core/math.py`
**Layer:** Core
**Issue:** `hex_to_pixel`, `pixel_to_hex`, `hex_distance`, `Vector2.distance_to` are correctly centralized. No cross-shard duplication found. Camera correctly implements ICamera protocol.
**Recommendation:** No consolidation needed — positive finding.

### INFO: Component Ability Extraction — Centralized but Widely Imported
**ID:** DUP-X-054
**Location:** `strategy/services/component_inspector.py` (called from 40+ locations)
**Layer:** Strategy -> UI (cross-layer calls)
**Issue:** NEW finding. `extract_abilities_from_component()` is correctly centralized in Strategy but is called from 40+ places across both Strategy and UI layers. The UI layer (6 files: `strategy_detail_fmt.py`, `strategy_detail_formatter.py`, `strategy_fleet_command_router.py`, `planet_abilities_window.py`, etc.) imports business logic directly. This is architectural drift — UI should use facade-level methods, not Strategy-layer component inspectors.
**Recommendation:** Add facade methods wrapping `extract_abilities_from_component()`. Deprecate direct UI imports of `component_inspector`.
**Estimated LOC Savings:** ~0 (architectural cleanup)
**Effort:** Medium

### INFO: StabilizerRegistry — Single Source of Truth for Superweapon Blocking
**ID:** DUP-X-055
**Location:** `strategy/services/stabilizer_registry.py`
**Layer:** Strategy
**Issue:** PROJ-277 correctly centralized superweapon-blocking logic into a data-driven registry. Previously each handler hand-rolled its own blocking check. GOOD — no consolidation needed. Archetype for how other cross-shard duplication should be resolved.
**Recommendation:** Use as pattern for race config resolution (DUP-X-003) and ability name lookups.

### INFO: SystemDestroyer — Single Entry Point for System Removal
**ID:** DUP-X-056
**Location:** `strategy/services/system_destroyer.py`
**Layer:** Strategy
**Issue:** PROJ-319 correctly centralized system-destroying logic that was previously duplicated across superweapon handlers. GOOD — already consolidated.
**Recommendation:** Document as consolidation benchmark.

### INFO: HabitabilityFactor Registry — Single Source of Truth Confirmed
**ID:** DUP-X-057
**Location:** `strategy/data/habitability_factors.py`
**Layer:** Strategy
**Issue:** `get_factor()` is the single entry point for all habitability axes. Called from `race_point_budget.py`, `race_randomizer.py`, `homeworld_presets.py`. No cross-shard duplication of factor definitions.
**Recommendation:** No consolidation needed — positive finding.

### INFO: 3 Gateway/Category Panels with ~80% Shared init Structure
**ID:** DUP-X-058
**Location:** `strategy_windows/selection_prompts.py:29,49,67`
**Layer:** UI
**Issue:** `prompt_planet`, `prompt_fleet`, `open_system` share UIDropDownMenu construction pattern with different domain objects. Low-impact but similar to target editor pattern.
**Recommendation:** Monitor for divergence. Could extract `PromptWindowBase` if more prompts are added.
**Estimated LOC Savings:** ~30 (future-proofing)
**Effort:** Low

---

## Prioritized Consolidation Plan

Ordered by impact/effort ratio (highest first):

| Priority | ID | Title | LOC Savings | Effort | Severity |
|----------|-----|-------|-------------|--------|----------|
| 1 | DUP-X-004 | ModifierManager static/instance migration completion | 160 | Simple | CRITICAL |
| 2 | DUP-X-006 | StrategyClickDispatcher registry-driven dispatch | 90 | Simple | CRITICAL |
| 3 | DUP-X-016 | Delete duplicated _rebuild_modifier_icons | 42 | Simple | MAJOR |
| 4 | DUP-X-011 | PlanetCommandHandlers — single SetPlanetTarget handler | 50 | Simple | MAJOR |
| 5 | DUP-X-012 | Shared ColumnToggleSection sidebar widget | 30 | Simple | MAJOR |
| 6 | DUP-X-013 | Shared RangeFilterFactory utility | 40 | Simple | MAJOR |
| 7 | DUP-X-014 | AI spatial circular position helper | 15 | Simple | MAJOR |
| 8 | DUP-X-015 | SuperweaponValidator star-based helper | 20 | Simple | MAJOR |
| 9 | DUP-X-018 | Cached JSON loader utility | 30 | Simple | MAJOR |
| 10 | DUP-X-017 | Event router editor opener consolidation | 60 | Simple | MAJOR |
| 11 | DUP-X-020 | Harvesting engine ability extraction helpers | 40 | Simple | MAJOR |
| 12 | DUP-X-021 | Planet action engine ability field helper | 20 | Simple | MAJOR |
| 13 | DUP-X-037 | Race randomizer weighted pick helper | 10 | Simple | MINOR |
| 14 | DUP-X-032 | Workshop dropdown handler helper | 10 | Simple | MINOR |
| 15 | DUP-X-001 | Target editor Template Method base class | 200 | Medium | CRITICAL |
| 16 | DUP-X-003 | Unified race config resolution | 80 | Medium | CRITICAL |
| 17 | DUP-X-005 | Superweapon command handler parameterized base | 200 | Medium | CRITICAL |
| 18 | DUP-X-007 | Planetary ability __init__ template | 260 | Medium | CRITICAL |
| 19 | DUP-X-008 | Planet/Star DataSource base class | 105 | Medium | CRITICAL |
| 20 | DUP-X-019 | Superweapons designation preamble extraction | 80 | Medium | MAJOR |
| 21 | DUP-X-009 | FilterManager base class extraction | 70 | Medium | MAJOR |
| 22 | DUP-X-010 | capture/apply state function consolidation | 80 | Medium | MAJOR |
| 23 | DUP-X-022 | Remove ability introspection from UI layer | 40 | Medium | MAJOR |
| 24 | DUP-X-023 | Workshop _require_ship decorator | 50 | Medium | MAJOR |
| 25 | DUP-X-052 | Validator primitives standardization | 40 | Medium | INFO |
| 26 | DUP-X-002 | PlanetListWindow / StarListWindow base class | 300 | Complex | CRITICAL |
| 27 | DUP-X-051 | Serialization schema helper (long-term) | 200 | Complex | INFO |

### Quick Wins (Simple Effort, ~1-2 hours each, ~605 LOC total savings)

Items 1-14 can be done independently:
1. Complete ModifierManager static removal (~160 LOC)
2. StrategyClickDispatcher dict dispatch (~90 LOC)
3. Delete duplicate _rebuild_modifier_icons (~42 LOC)
4. PlanetCommandHandlers unification (~50 LOC)
5. ColumnToggleSection widget (~30 LOC)
6. RangeFilterFactory utility (~40 LOC)
7. AI circular position helper (~15 LOC)
8. SuperweaponValidator helper (~20 LOC)
9. Cached JSON loader (~30 LOC)
10. Event router opener consolidation (~60 LOC)
11. Harvesting engine helpers (~40 LOC)
12. Planet action engine helper (~20 LOC)
13. Race randomizer weighted pick (~10 LOC)
14. Workshop dropdown helper (~10 LOC)

### Medium-Term (Medium Effort, ~1-3 days each, ~1,165 LOC total savings)

Items 15-25 require architectural changes:
- Target editors need Template Method base class
- Race config resolution unified across UI and Strategy
- Superweapon handlers parameterized
- Ability __init__ shared field extraction
- Planet/Star DataSource base class
- FilterManager base class
- Preset capture/apply consolidation
- Ability introspection removed from UI
- Workshop decorator pattern

### Long-Term (Complex, ~1 week each, ~500 LOC total savings)

Items 26-27 require significant refactoring:
- Planet/Star list windows composable table component
- Serialization schema modernization (incremental)

### Total Estimated Shrinkable LOC: ~2,270
