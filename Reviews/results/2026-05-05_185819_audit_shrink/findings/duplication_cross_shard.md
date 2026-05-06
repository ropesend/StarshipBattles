# Cross-Shard Duplication Report

## Summary
- Files Scanned: 653
- Total Findings: 39
- Critical: 1 | Major: 12 | Minor: 16 | Info: 10

---

## Clone Detector Validation

### CONFIRMED — Genuine Duplication

#### Cluster 1: Planetary ability __init__ methods
**Status:** CONFIRMED, downrated to MINOR.
**Files:** `game/simulation/components/abilities/planetary.py:453,528,728`
**Finding:** `PlanetaryShieldAbility`, `PlanetaryShieldHardeningAbility`, and `PlanetaryRadiationShieldingAbility` have nearly identical `__init__` methods that parse `energy_drain_rate`, `activation_time`, `deactivation_time` from the data dict. The third variant also handles `max_shielding`. Could be extracted to a shared base with a `_parse_energy_fields(data, extra_fields)` helper.
**Estimated LOC Savings:** 8
**Effort:** Simple

#### Cluster 2: Cargo mode click handlers
**Status:** CONFIRMED. Already addressed partially in DUP-X-02 via `_emit_validated_order` pattern in `BaseCommandHandler`, but could still be further consolidated.
**Files:** `game/ui/screens/strategy_click_dispatcher.py:205,233,247`
**Finding:** `_handle_transfer_mode_click`, `_handle_drop_cargo_mode_click`, and `_handle_load_cargo_mode_click` are structurally identical — resolve click target, get fleet, open dialog with a mode string variant, then restore SELECT mode. Only the dialog method name and a single string parameter differ.
**Estimated LOC Savings:** 10
**Effort:** Simple

#### Cluster 3: Superweapon designation handlers
**Status:** CONFIRMED but downrated to MINOR.
**Files:** `game/ui/screens/strategy_superweapons.py:119,221,265`
**Finding:** `handle_stellerate_star_designation`, `handle_close_warp_designation`, and `handle_dyson_sphere_designation` follow a common pattern: validate fleet, check ability, screen-to-world conversion, get target, show confirmation/system-picker, queue command. However, each has unique validation (different ability check, different target resolution — star system vs warp point), unique confirmation UI (different dialogs), and different command types. Consolidation into a generic "superweapon designation handler" would require awkward parameterization and harm readability.
**Estimated LOC Savings:** 0 (not recommended)
**Effort:** N/A

#### Cluster 4: Selection prompt methods
**Status:** CONFIRMED, MINOR.
**Files:** `game/ui/screens/strategy_windows/selection_prompts.py:29,50,69`
**Finding:** `prompt_planet`, `open_system`, and `prompt_fleet` are nearly identical window-creation boilerplate methods (calculate dimensions, create rect, instantiate window class with composer/manager). Could use a single `_open_selection_window(WindowClass, *args, width, height)` helper. Already small at ~15 LOC total.
**Estimated LOC Savings:** 8
**Effort:** Simple

#### Cluster 5: Planet environment target command handlers
**Status:** CONFIRMED, MAJOR.
**Files:** `game/strategy/engine/planet_command_handlers.py:163,184,205`
**Finding:** `SetAtmosphereTargetCommandHandler`, `SetGravityTargetCommandHandler`, and `SetWaterTargetCommandHandler` are near-clones. Each handler: (1) resolves planet via `BaseCommandHandler._resolve_planet`, (2) checks `planet.owner_id != session.active_empire.id`, (3) sets `planet.X_target = cmd.X_target`, (4) logs with the field name. The three are identical except for the attribute name and a log format string. These should be merged into a single `SetPlanetEnvironmentalTargetCommandHandler` parameterized by attribute. Additionally, the `planet.owner_id != session.active_empire.id` check is repeated 7 times across all planet command handlers — a separate anti-pattern documented below (DUP-X-03).
**Estimated LOC Savings:** 30
**Effort:** Medium (requires command-level refactoring)

#### Cluster 6: _rebuild_modifier_icons duplication
**Status:** CONFIRMED, MAJOR.
**Files:** `game/ui/screens/builder/structure_list_items.py:195,472`
**Finding:** `IndividualComponentItem._rebuild_modifier_icons` and `GroupComponentItem._rebuild_modifier_icons` are identical across ~40 lines — clear modifier icons, bail if no modifier_icon_service, collect modified IDs, layout icons from right side with margin `-220`, create `UIImage` widgets with tooltips. The Group variant has a one-line comment difference. Should be extracted to a shared static method or mixin on a common base class.
**Estimated LOC Savings:** 40
**Effort:** Medium

#### Cluster 7: Hit effect drawing functions
**Status:** CONFIRMED, MINOR.
**Files:** `game/ui/effects/hit_effects.py:146,176`
**Finding:** `_draw_armor_hit` and `_draw_component_destroyed` share identical structure: lookup config by type, compute max radius, create alpha surface, draw circle + radiating lines, blit. The only differences are config keys, color values, line count (6 vs 8), line thickness (1 vs 2), and line length multiplier (1.3 vs 1.4). Could be consolidated into a single parameterized `_draw_radiating_hit(screen, pos, effect, t, alpha, zoom, config)` function.
**Estimated LOC Savings:** 15
**Effort:** Simple

#### Cluster 8: Planet/star list window update methods
**Status:** CONFIRMED, MAJOR.
**Files:** `game/ui/screens/planet_list_window.py:541`, `game/ui/screens/star_list_window.py:389`
**Finding:** Both `update()` methods follow an identical 4-step pattern: (1) scrollbar movement check → update visible rows, (2) slider text sync with type-specific fields, (3) header sort/swap with `column_manager.swap_column`/`set_sort`, (4) preset dropdown change detection → apply state. The only differences are the slider field tuples and filter helper method names. Both files also have identical `_set_all_filters` patterns. A shared `ListWindowBase` class or `TableViewUpdateMixin` would eliminate ~50 lines of duplicated structural logic.
**Estimated LOC Savings:** 50
**Effort:** Medium (requires base class extraction)

#### Cluster 9: Squadron delete/duplicate handlers
**Status:** CONFIRMED but downrated to INFO (too small to matter).
**Files:** `game/ui/screens/battle_setup/controller.py:283,293`
**Finding:** `delete_squadron` and `duplicate_squadron` are ~8-line methods that both do basic index validation, call a method on the controller, and log. MINOR — insufficient LOC to justify consolidation overhead.
**Estimated LOC Savings:** 3
**Effort:** Not worth doing

#### Cluster 10: __init_subclass__ validators
**Status:** CONFIRMED, MINOR.
**Files:** `game/simulation/components/abilities/base.py:450,502`
**Finding:** `StaticValueAbility.__init_subclass__` and `SimpleMultiplierAbility.__init_subclass__` both validate that subclasses set required class attributes, using the same loop pattern. Could use a shared `_validate_required_attrs(cls, attrs, exclude_class)` helper. MINOR — it's a legitimate use of metaclass-like validation, and the benefit is marginal.
**Estimated LOC Savings:** 5
**Effort:** Simple

#### Cluster 11: Superweapon mission command handlers (Stellerate & Dyson vs Open & Close)
**Status:** CONFIRMED, MAJOR.
**Files:** `game/strategy/engine/superweapon_command_handlers.py:225,256,292,328`
**Finding:** Four handlers follow an identical 4-step pattern: (1) `_resolve_player_fleet`, (2) call `SuperweaponValidator.validate_X`, (3) `add_move_order_if_needed`, (4) create `Order(OrderType.X, target=...)` and `fleet.add_order`. `_emit_validated_order` already exists in `BaseCommandHandler` and was designed precisely for steps 3–4, but these handlers still manually create orders. Additionally: StellerateStar (225) and DysonSphere (328) are structurally identical (target=None, same flow); OpenWarpPoint (256) and CloseWarpPoint (292) are structurally identical (target=dict, same flow). The first pair could use `_emit_validated_order`. The second pair could use a parameterized helper.
**Estimated LOC Savings:** 40
**Effort:** Medium (refactor to use `_emit_validated_order` + parameterized target dict builder)

#### Cluster 12: Energy drain / deactivation time extractors
**Status:** CONFIRMED, MINOR.
**Files:** `game/strategy/engine/planet_action_engine.py:312,327`
**Finding:** `_get_energy_drain_rate` and `_get_deactivation_time` have identical logic — iterate `facility.design_data`, find component matching `comp_id`, extract abilities, look up ability data, return a specific field with a default. Only the field name (`energy_drain_rate` vs `deactivation_time`) and return type (`float` vs `int`) differ. Should be consolidated into a single `_get_ability_field(facility, comp_id, ability_name, field_name, default)` method.
**Estimated LOC Savings:** 12
**Effort:** Simple

#### Cluster 13: System/sector effects addition
**Status:** CONFIRMED, MINOR.
**Files:** `game/ui/panels/system_tree_panel.py:467,482`
**Finding:** `_add_system_effects` and `_add_sector_effects` are nearly identical — import a collector function, get empire context, call collector, pass results to `_add_effects_group` with a label prefix and group key. Only the collector function name and label differ. Could be a single method accepting `collector_fn, label_prefix, group_key` parameters. Already partially addressed by shared `_add_effects_group`, but the callers still duplicate the setup.
**Estimated LOC Savings:** 10
**Effort:** Simple

#### Cluster 14: Bio/socio transition handlers
**Status:** CONFIRMED, MAJOR.
**Files:** `game/strategy/services/race_description_llm_controller.py:266,289`
**Finding:** `_apply_bio_transition` and `_apply_socio_transition` are mirror methods — same DONE/ERROR handling, same logging patterns, only the attribute names differ (`_race.bio_description` vs `_race.socio_description`, `_bio_error` vs `_socio_error`, `_bio_status` vs `_socio_status`). Consolidation into a single `_apply_transition(call, new_status, field: str)` method would work cleanly. Same pattern applies to `_start_bio` / `_start_socio` (lines 198, 219 — cluster 26).
**Estimated LOC Savings:** 22
**Effort:** Simple

#### Cluster 15: ModifierManager get_stat_summary / get_stat_summary_static
**Status:** CONFIRMED but INFO — already marked DEPRECATED.
**Files:** `game/simulation/components/modifier_manager.py:166,297`
**Finding:** Instance method `get_stat_summary()` and static method `get_stat_summary_static()` share identical logic. The static version is already documented as "DEPRECATED — will be removed in Task 1.3." No action needed now; the cleanup is already planned.
**Estimated LOC Savings:** 0 (planned removal)
**Effort:** N/A

#### Cluster 16: Race randomizer pick methods
**Status:** CONFIRMED, MINOR.
**Files:** `game/strategy/systems/race_randomizer.py:109,127`
**Finding:** `_pick_name_entry` and `_pick_leader` follow the same "look up from portrait data, fall back to fallback list, return default" pattern with different data keys (`names` vs `leaders`, `fallback_names` vs `fallback_leaders`). Could use a generic `_pick_from_portrait(data, portrait_id, rng, portrait_key, fallback_key, default_value)` helper.
**Estimated LOC Savings:** 8
**Effort:** Simple

#### Cluster 17: Event log replay accessors
**Status:** CONFIRMED but downrated to INFO (different logic, same structure only).
**Files:** `game/ui/screens/event_log_data_source.py:150,172`
**Finding:** `get_cell_replay_id` and `get_cell_replay_unavailable_reason` both: get event at index, check category=="combat", extract from details. But the fields extracted differ (`replay_id` vs `replay_unavailable_reason`) and return types differ. The shared structure is too small to warrant abstraction.
**Estimated LOC Savings:** 0 (not recommended)
**Effort:** N/A

#### Cluster 18: Movement/targeting dropdown handlers
**Status:** CONFIRMED, MINOR.
**Files:** `game/ui/screens/workshop_event_router.py:493,505`
**Finding:** `_handle_movement_dropdown` and `_handle_targeting_dropdown` are identical except for the options list import and the viewmodel setter method name (`set_ship_movement_policy` vs `set_ship_targeting_policy`). A generic `_handle_policy_dropdown(event, options_module, setter_name)` helper would remove the duplication. The same pattern applies to `_handle_role_dropdown` (line 517).
**Estimated LOC Savings:** 12
**Effort:** Simple

#### Cluster 19: Component grouping strategies
**Status:** CONFIRMED, MINOR.
**Files:** `game/ui/screens/builder/grouping_strategies.py:18,53`
**Finding:** `DefaultGroupingStrategy.group_components` and `TypeGroupingStrategy.group_components` implement the same algorithm with different group-key generation. Both build a `defaultdict(list)`, sort groups, compute total mass, return tuples. Could use a shared `_group_by(components, key_fn)` base method. This is a legitimate strategy pattern though; the current design is clean.
**Estimated LOC Savings:** 10
**Effort:** Simple

#### Cluster 20: Panel _create_content methods
**Status:** FALSE POSITIVE, downrated to INFO.
**Files:** `game/ui/panels/race_aptitudes_panel.py:91`, `game/ui/panels/race_identity_panel.py:86`
**Finding:** Both methods are called `_create_content` and follow a `y = 5; y = self._create_X_section(y, panel_width)` structural pattern, but the actual content sections are entirely different. Only the boilerplate is similar — standard pygame_gui panel construction. Not a real duplication.
**Estimated LOC Savings:** 0
**Effort:** N/A

#### Cluster 21: Tkinter save/load dialogs
**Status:** CONFIRMED, MINOR.
**Files:** `game/ui/services/tkinter_utils.py:108,147`
**Finding:** `open_save_dialog` and `open_load_dialog` share most of their structure: get Tk root, set default filetypes, call `filedialog.askX` with kwargs, catch platform-dependent exceptions. The functions differ in supported parameters (save has `initialfile` and `defaultextension`; load doesn't) and the tk dialog called. Could consolidate by extracting the `root` + `filetypes` + try/except boilerplate but the actual dialog calls are different enough that a helper may obscure more than it helps.
**Estimated LOC Savings:** 5
**Effort:** Not recommended

#### Cluster 22: Factory provider factories
**Status:** CONFIRMED, MAJOR.
**Files:** `game/services/llm/factory.py:52`, `game/ui/services/image/factory.py:47`
**Finding:** `LLMProviderFactory.create()` and `ImageProviderFactory.create()` are structural clones: read env var, look up in `_PROVIDERS` dict, raise on unknown, try-construct returning None on config error. The only differences are: env var name, default provider, exception types (`LLMConfigError` vs `ImageConfigError`), error codes. A generic `ProviderFactory` base class parameterized on these would eliminate ~30 LOC. However, the existing code is clean and well-documented; consolidation would cross the services↔UI layer boundary and introduce a shared dependency.
**Estimated LOC Savings:** 25
**Effort:** Medium (layer-boundary concern)

#### Cluster 23: Test lab panel constructors
**Status:** CONFIRMED but downrated to INFO.
**Files:** `game/ui/screens/test_lab/renderer/category_panel.py:28`, `game/ui/screens/test_lab/renderer/test_list_panel.py:27`
**Finding:** Both `__init__` methods accept the same parameter set (header_font, body_font, small_font, header_color, text_color, selected_color, panel_bg, border_color, header_height) and assign them identically. Could use a shared `PanelTheme` config object. Minor — the panels serve different purposes and the shared params may diverge.
**Estimated LOC Savings:** 5
**Effort:** Simple

#### Cluster 24: Ability provider functions
**Status:** FALSE POSITIVE, downrated to INFO.
**Files:** `game/strategy/services/ability_iterator.py:217,288`
**Finding:** `_planet_intrinsic_provider` and `_warp_point_provider` share a guard-early-return pattern (`if system is None: return`) but are otherwise different (different domain objects, different iteration logic). The similarity is the provider function signature convention, not actual code duplication.
**Estimated LOC Savings:** 0
**Effort:** N/A

#### Cluster 25: Bio/socio start methods
**Status:** CONFIRMED, see Cluster 14 above (same file pair).
**Files:** `game/strategy/services/race_description_llm_controller.py:198,219`
**Finding:** `_start_bio` and `_start_socio` are mirror methods — both gather captions, log, build a prompt, create an `LLMBackgroundCall`, try-start, handle `LLMConfigError`. Consolidation with the transition handlers (Cluster 14) into a unified field-parameterized controller would eliminate both pairs of duplication.
**Estimated LOC Savings:** Covered under Cluster 14
**Effort:** Combined with Cluster 14

#### Cluster 26: Fleet consumable load/unload
**Status:** CONFIRMED, MINOR.
**Files:** `game/strategy/data/fleet_consumable_aggregator.py:291,317`
**Finding:** `load_cargo_to_fleet` and `unload_cargo_from_fleet` are structurally identical — guard amount≤0, initialize remaining/total, iterate ships calling `ship.load_cargo` or `ship.unload_cargo`, accumulate, return total. Only the ship method name differs. Could use a shared `_distribute_cargo(cargo_type, amount, ship_method)` internal method.
**Estimated LOC Savings:** 18
**Effort:** Simple

#### Cluster 27: Fleet ops execute methods
**Status:** CONFIRMED, MINOR.
**Files:** `game/ui/screens/strategy_fleet_ops.py:134,197`
**Finding:** `execute_intercept` and `execute_join` are structurally identical — create a command with `fleet.id` and `target_fleet.fleet_id`, call `self.facade.handle_command(cmd)`, return success/error dict with fleet or message. Only the command class differs. A shared `_execute_fleet_command(CommandClass, fleet, target_fleet_info)` helper would eliminate the duplication.
**Estimated LOC Savings:** 12
**Effort:** Simple

#### Cluster 28: Empire/planet resource addition
**Status:** CONFIRMED but downrated to INFO (different domain objects, legitimate duplication).
**Files:** `game/strategy/data/empire.py:187`, `game/strategy/data/planet.py:284`
**Finding:** `Empire.add_resources` and `Planet.add_to_stockpile` implement the same resource pool addition algorithm but operate on different storage dictionaries and different caps (`max_storage` vs `max_stockpile`). Similarly, `Empire.consume_resources` and `Planet.consume_from_stockpile` are mirrors. These are separate domain objects with different storage semantics — not a candidate for consolidation. A shared `ResourcePool` mixin would be the correct abstraction but introduces complexity disproportional to the benefit (~20 LOC total).
**Estimated LOC Savings:** 0 (not recommended)
**Effort:** N/A

#### Cluster 29: Harvesting engine registry lookups (harvester)
**Status:** CONFIRMED. Covered under Cluster 30-31 below.
**Files:** `game/strategy/engine/harvesting_engine.py:67,301`
**Finding:** `get_harvester_from_registry` and `_get_storage_from_registry` are identical except for the ability key (`ResourceHarvester` vs `LocalStorage`). A generic `_get_ability_data_from_registry(comp_id, registries, ability_name)` module-level function would serve both callers and eliminate the pattern duplication.

#### Cluster 30: Harvesting engine component-level extraction (harvester/storage info)
**Status:** CONFIRMED. Combined with Cluster 29.
**Files:** `game/strategy/engine/harvesting_engine.py:38,274`
**Finding:** `get_harvester_info` (module-level) and `_get_storage_info` (instance method) share identical structure: check `isinstance(comp, dict)`, try inline abilities, fall back to registry lookup by comp_id; if string, use registry lookup directly. Only the ability key differs. These are the top-level wrappers for Clusters 29's registry methods.
**Estimated LOC Savings:** 25 (combined with Cluster 29)
**Effort:** Simple

---

## Cross-Shard Findings

### CRITICAL

#### CRITICAL: Owner-ID validation repeated 7x in planet_command_handlers
**ID:** DUP-X-01
**Location:** `game/strategy/engine/planet_command_handlers.py:47,110,128,149,170,191,212` AND `game/strategy/engine/superweapon_command_handlers.py` (similar ownership check via `_resolve_player_fleet`)
**Layer:** strategy
**Issue:** The exact line `if planet.owner_id != session.active_empire.id: return ValidationResult.error("Planet does not belong to this empire.")` appears 7 times in `planet_command_handlers.py`. `BaseCommandHandler._resolve_planet` already provides planet resolution but does NOT validate ownership. Meanwhile `BaseCommandHandler._resolve_fleet` supports optional ownership validation via `empire_id` parameter. The planet path has no equivalent `_resolve_player_planet` that bakes in the ownership check.
**Impact:** Every new planet command handler must remember to copy-paste the ownership check. If the validation message changes, 7 sites need updating. Risk of new handlers missing the check entirely.
**Recommendation:** Add `BaseCommandHandler._resolve_player_planet(session, planet_id)` that wraps `_resolve_planet` with the ownership check, mirroring `_resolve_player_fleet`. Refactor all 7 handlers to use it.
**Estimated LOC Savings:** 14
**Effort:** Simple

### MAJOR

#### MAJOR: "Iterate components → extract ability → read field" pattern duplicated across 8+ engines
**ID:** DUP-X-02
**Location:** `game/strategy/engine/planet_action_engine.py:312–340` AND `game/strategy/engine/water_engine.py:53,82` AND `game/strategy/engine/quality_engine.py:62,94` AND `game/strategy/engine/atmosphere_engine.py:68,142` AND `game/strategy/engine/planet_energy_engine.py:206` AND `game/strategy/engine/harvesting_engine.py:218,258,357` AND `game/strategy/data/build_queue_source.py:142,219` AND `game/strategy/engine/empire_economy_calculator.py:229` AND `game/ui/screens/strategy_detail_formatter.py:314`
**Layer:** strategy AND ui (cross-shard)
**Issue:** A pervasive pattern appears across strategy engines and UI code:
```python
for comp in iter_components(facility.design_data):
    abilities = extract_abilities_from_component(comp, self._registries)
    if ability_name in abilities:
        ability_data = abilities.get(ability_name, {})
        value = ability_data.get(field_name, default)
```
This is the core loop of every engine that processes facility component abilities (water, quality, atmosphere, energy, harvesting, planet action). While `extract_abilities_from_component` is already centralized in `component_inspector.py`, the outer loop ("iterate facility, find component with ability X, then get field Y") is reimplemented in 8+ files, often with subtle variations in how `comp_id` matching works or how the field is extracted.
**Impact:** Changes to the component iteration pattern (e.g., new design_data format) require updates in 8+ files. Subtle bugs hide in the per-engine variations (e.g., `planet_action_engine.py` extracts `energy_drain_rate` as float while `deactivation_time` as int — same loop, different cast, duplicated code).
**Recommendation:** Add a `get_ability_field_from_facility(facility, ability_name, field_name, default, registries)` function to `component_inspector.py`. This would be the single hop from "I know the facility, ability, and field I want" to the value, encapsulating the entire pattern. Each engine would replace 8+ lines with a single function call.
**Estimated LOC Savings:** 80
**Effort:** Medium (requires changing 8+ call sites)

#### MAJOR: Workshop dropdown handlers — 5 almost-identical methods
**ID:** DUP-X-03
**Location:** `game/ui/screens/workshop_event_router.py:441,464,493,505,517`
**Layer:** ui
**Issue:** `_handle_class_dropdown`, `_handle_vehicle_type_dropdown`, `_handle_movement_dropdown`, `_handle_targeting_dropdown`, and `_handle_role_dropdown` all follow the same event-handling pattern. The movement/targeting/role trio are pure clones: import options list, match display name to policy ID, call viewmodel setter. The class/vehicle_type pair share a confirmation-dialog pattern with `gui.pending_action` and `gui.confirm_dialog`. A unified dispatcher that reads from a config dict would eliminate all 5 methods.
**Impact:** Adding a new dropdown policy requires copy-pasting a new handler method. Risk of drift in confirmation dialog sizing, error messages, or guard clauses.
**Recommendation:** Define dropdown handler config as a dict mapping dropdown names to `(options_import, viewmodel_setter_name, confirmation_config)` tuples. Dispatch from a single `_handle_policy_dropdown(event)` method.
**Estimated LOC Savings:** 50
**Effort:** Simple

#### MAJOR: Planet and star list windows share ~45 lines of identical update() logic
**ID:** DUP-X-04
**Location:** `game/ui/screens/planet_list_window.py:541–573` AND `game/ui/screens/star_list_window.py:389–421`
**Layer:** ui
**Issue:** Beyond the clone detector finding (Cluster 8), both files also have identical `_set_all_filters` / `_toggle_filter` patterns in their private helpers. The update() method is a templated algorithm: scrollbar → slider sync → header sort/swap → preset dropdown. The only variance is the slider field names.
**Impact:** Any change to the scrollbar update pattern, header sort logic, or preset dropdown handling must be made in two files. Bug risk from divergent implementations.
**Recommendation:** Extract a `ListWindowUpdater` mixin or base class that provides `_update_template(slider_fields, column_manager, preset_manager)` with the common 4-step update loop. Both windows would extend it and provide their own `_sync_slider_text()` and filter methods.
**Estimated LOC Savings:** 60 (combining update + filter helpers)
**Effort:** Medium

#### MAJOR: Race description LLM controller — entire bio/socio axis is mirrored
**ID:** DUP-X-05
**Location:** `game/strategy/services/race_description_llm_controller.py:198–219,266–307`
**Layer:** strategy/services
**Issue:** Clusters 14 and 25 together show that the bio and socio description paths are complete mirrors: `_start_bio` / `_start_socio`, `_apply_bio_transition` / `_apply_socio_transition`, `_bio_call` / `_socio_call`, `_bio_status` / `_socio_status`, `_bio_error` / `_socio_error`. This is a two-dimensional copy-paste — any change to the LLM field lifecycle must be made twice.
**Impact:** Adding a third LLM-generated field (e.g., "history_description") would require adding 4+ mirrored methods and 3+ mirrored attributes. Maintenance risk from one axis drifting (e.g., bio gets error handling improvement but socio doesn't).
**Recommendation:** Replace the mirrored attribute pairs with a `_fields: dict[str, FieldState]` dict mapping field names to their call/status/error tuples. The start/poll/transition methods become generic functions accepting a `field_name` parameter. This is a ~30-line refactor that eliminates 60+ lines of mirrored code.
**Estimated LOC Savings:** 55
**Effort:** Simple

#### MAJOR: Ability data from component extraction — 3 variant patterns in planet_action_engine
**ID:** DUP-X-06
**Location:** `game/strategy/engine/planet_action_engine.py:296–310,312–324,327–339,376–380`
**Layer:** strategy/engine
**Issue:** The planet action engine has 4 methods that iterate `facility.design_data` looking for a component with a specific ability, then extract different fields. `_find_component_with_ability` (line 296) builds the comp_key and comp_id. `_get_energy_drain_rate` and `_get_deactivation_time` (Clusters 12) do the same loop but extract a specific numeric field. `_target_facility_exists` (line 342) does yet another iteration over `planet.facilities` to find by instance_id. These are variants of the same "find thing by identity" pattern.
**Impact:** 4 private methods that are variations on "look up component in facility and extract something". Any change to the facility design_data format requires updating 4 methods.
**Recommendation:** The `_find_component_with_ability` method could return richer data (the found abilities dict), and `_get_energy_drain_rate` / `_get_deactivation_time` would become thin wrappers that call it and then extract their specific field. Or combine with DUP-X-02's centralized `get_ability_field_from_facility`.
**Estimated LOC Savings:** 20 (combined with DUP-X-02 scope)
**Effort:** Medium

#### MAJOR: Superweapon command handlers don't use existing _emit_validated_order pattern
**ID:** DUP-X-07
**Location:** `game/strategy/engine/superweapon_command_handlers.py:222–250,253–286,289–322,325–353`
**Layer:** strategy/engine
**Issue:** All 4 superweapon mission handlers execute the same 4-step pattern. `BaseCommandHandler._emit_validated_order` (added by PROJ-319 specifically to consolidate this pattern) exists at `game/strategy/engine/handlers/base.py:228` but NONE of these 4 handlers use it. Instead they manually: validate, call `add_move_order_if_needed`, create `Order(...)`, `fleet.add_order(...)`, log. The `_emit_validated_order` method does steps 3-4 in a single call with better logging.
**Impact:** The fix for DUP-X-02 from PROJ-319 was not applied to these handlers. Adding a new superweapon mission type requires copy-pasting 30+ lines with slight variations in order type and target format. If the fleet.add_order contract changes, 4 handlers need updating.
**Recommendation:** Refactor all 4 handlers to call `self._emit_validated_order(fleet, order_type, target, result, log_label)` after their resolve+validate steps. The StellerateStar and DysonSphere handlers (identical pattern with `target=None`) could even share a single `_handle_simple_superweapon_mission` helper.
**Estimated LOC Savings:** 45
**Effort:** Simple

#### MAJOR: Factory pattern duplicated across LLM and Image providers
**ID:** DUP-X-08
**Location:** `game/services/llm/factory.py:48–87` AND `game/ui/services/image/factory.py:43–79`
**Layer:** services AND ui (cross-shard)
**Issue:** The two factory files are structural clones: module-level `_PROVIDERS` dict, `register_X` function, `XFactory` class with static `create()` method. The only differences are: exception types, env var names, default provider strings, error codes. Pattern #15 (Factory) describes both but doesn't prescribe a shared base.
**Impact:** Adding a new provider type (e.g., audio provider) means copy-pasting the entire factory.py structure and substituting type names. Cross-layer concern: the LLM factory lives in `services/` and the image factory in `ui/services/`. A shared base would be in `services/` and imported by both.
**Recommendation:** Extract `BaseProviderFactory` to `game/services/provider_factory.py` with class variables for `_env_var`, `_default`, `_error_code`, `_config_error_type`. Both factories become 3-line subclasses. The `_PROVIDERS` dict and `register_provider` function remain in each module for import-time registration.
**Estimated LOC Savings:** 30
**Effort:** Medium (introduces new shared dependency)

### MINOR

#### MINOR: "Reset planet attribute to None" pattern duplicated in 6 unrelated command handlers
**ID:** DUP-X-09
**Location:** `game/strategy/engine/planet_command_handlers.py:36–220` (6 handlers: IssuePlanetOrder, SetAtmosphereTarget, SetGravityTarget, SetWaterTarget, SetRadiationShieldTarget, SetTemperature)
**Layer:** strategy/engine
**Issue:** Each handler follows a resolve→validate ownership→set attribute→log pattern. The ownership check and the "if not None else cleared" logging pattern repeat. These are already using `BaseCommandHandler._resolve_planet` but still duplicate ownership validation (see DUP-X-01).
**Estimated LOC Savings:** Covered under DUP-X-01
**Effort:** Combined

#### MINOR: Hex screen-to-world conversion duplicated across strategy superweapons
**ID:** DUP-X-10
**Location:** `game/ui/screens/strategy_superweapons.py:139,185,241,285`
**Layer:** ui
**Issue:** Every `handle_X_designation` method repeats the 2-line hex conversion: `world_pos = self.camera.screen_to_world((mx, my)); target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.hex_size)`. A shared `_screen_to_hex(mx, my)` helper would remove 8 lines of repetition.
**Estimated LOC Savings:** 6
**Effort:** Simple

#### MINOR: "Has ability check + error message" pattern in superweapons UI
**ID:** DUP-X-11
**Location:** `game/ui/screens/strategy_superweapons.py:134,180,236,280`
**Layer:** ui
**Issue:** Each designation handler checks `fleet.capabilities.has_ability("AbilityName")` with a unique hardcoded log message and user-facing error message. The 4 checks share the same pattern. A small helper would reduce boilerplate.
**Estimated LOC Savings:** 8
**Effort:** Simple

### INFO (Observations)

#### INFO: to_dict/from_dict pattern is intentionally pervasive (ISerializable protocol)
**Location:** 122+ matches across game/ (serialization, persistence, entity, state, config files)
**Layer:** all
**Issue:** Almost every entity class implements `to_dict()` / `from_dict()` following the `ISerializable` protocol from `game/core/protocols/persistence.py`. This is by design — the protocol pattern ensures consistent serialization. Not duplication; it's the documented persistence architecture.
**Recommendation:** No action needed.

#### INFO: "Get by ID" lookup pattern is intentionally duplicated (CQRS-lite + Facade)
**Location:** galaxy.py, facade/slices/*, galaxy_entity_registry.py, game_session.py, battle_controller.py
**Layer:** strategy, simulation (cross-shard)
**Issue:** `get_fleet_by_id`, `get_planet_by_id`, `get_empire_by_id` appear in multiple layers. The galaxy is the domain source; the facade/slices expose these for UI via CQRS-lite; `game_session.py` wraps them for internal engine use; `galaxy_entity_registry.py` provides another cache layer. These are different interfaces for different consumers, following the Facade/Delegate pattern.
**Recommendation:** No action needed. Pattern is intentional per architecture docs.

#### INFO: hex_distance is properly centralized in game/core/hex_math.py
**Finding:** All 33+ call sites import `hex_distance` from `game.core.hex_math`. No competing implementations exist. The centralization is healthy.
**Recommendation:** No action needed.

#### INFO: extract_abilities_from_component is properly centralized in component_inspector.py
**Finding:** All 40+ call sites import from `game/strategy/services/component_inspector`. The function correctly handles both inline abilities and registry lookup. The outer loop duplication (DUP-X-02) is the remaining problem, not the core function.
**Recommendation:** Maintain this. Extend with `get_ability_field_from_facility` per DUP-X-02.

#### INFO: Multiple "iter_components" definitions are intentional layer-specific variants
**Location:** `game/core/patterns/layer_iterator.py:42` (core — generic design_data), `game/simulation/entities/ship_component_manager.py:188` (simulation — Ship), `game/simulation/entities/ship.py:523` (facade)
**Layer:** core, simulation
**Issue:** Three `iter_components` implementations exist at different layers, but they are intentionally different: the core-layer one iterates JSON design_data dicts; the simulation one iterates Ship's live Component objects; the ship.py one delegates to the component manager. Each serves its layer's data model.
**Recommendation:** No action needed. The layer-specific implementations prevent cross-layer coupling.

---

## Prioritized Consolidation Plan

Ordered by impact/effort ratio (highest value, lowest risk first).

| Priority | ID | Title | LOC Savings | Effort | Layer |
|----------|----|-------|-------------|--------|-------|
| 1 | DUP-X-01 | Add _resolve_player_planet to BaseCommandHandler | 14 | Simple | strategy |
| 2 | Cluster 14+25 | Unify race_description bio/socio axis via field dict | 55 | Simple | strategy |
| 3 | DUP-X-03 | Unify workshop dropdown handlers via config dispatch | 50 | Simple | ui |
| 4 | Cluster 5 | Merge 3 environment target handlers into parameterized handler | 30 | Medium | strategy |
| 5 | Cluster 29+30 | Generic _get_ability_data_from_component helper in harvesting_engine | 25 | Simple | strategy |
| 6 | DUP-X-02 | Add get_ability_field_from_facility to component_inspector | 80 | Medium | cross-shard |
| 7 | DUP-X-07 | Refactor superweapon handlers to use _emit_validated_order | 45 | Simple | strategy |
| 8 | Cluster 6 | Extract shared _rebuild_modifier_icons to mixin | 40 | Medium | ui |
| 9 | Cluster 8 + DUP-X-04 | Extract ListWindowBase for planet/star list windows | 60 | Medium | ui |
| 10 | Cluster 11 | Parameterize superweapon mission handlers | 40 | Medium | strategy |
| 11 | DUP-X-08 | Extract BaseProviderFactory for LLM+Image providers | 30 | Medium | cross-shard |
| 12 | Cluster 7 | Parameterize _draw_radiating_hit for armor/component effects | 15 | Simple | ui |
| 13 | Cluster 12 | Merge _get_energy_drain_rate / _get_deactivation_time | 12 | Simple | strategy |
| 14 | Cluster 26 | Generic _distribute_cargo helper in FleetConsumableAggregator | 18 | Simple | strategy |
| 15 | Cluster 27 | Generic _execute_fleet_command helper in fleet_ops | 12 | Simple | ui |
| 16 | Cluster 18 | Unify movement/targeting/role dropdown handlers | 12 | Simple | ui |
| 17 | Cluster 13 | Merge _add_system_effects / _add_sector_effects | 10 | Simple | ui |
| 18 | Cluster 19 | Shared _group_by base for grouping strategies | 10 | Simple | ui |
| 19 | DUP-X-10 | Add _screen_to_hex helper in strategy_superweapons | 6 | Simple | ui |
| 20 | DUP-X-11 | Add _check_ability helper in strategy_superweapons | 8 | Simple | ui |
| 21 | Cluster 2 | Unify cargo mode click handlers | 10 | Simple | ui |
| 22 | Cluster 4 | Generic _open_selection_window in selection_prompts | 8 | Simple | ui |
| 23 | Cluster 1 | Shared _parse_energy_fields for planetary abilities | 8 | Simple | simulation |
| 24 | Cluster 16 | Generic _pick_from_portrait for race_randomizer | 8 | Simple | strategy |
| 25 | Cluster 10 | Shared __init_subclass__ validator helper | 5 | Simple | simulation |
| 26 | Cluster 23 | PanelTheme config object for test_lab panels | 5 | Simple | ui |
| 27 | Cluster 9 | Squadron delete/duplicate — not worth consolidating | 0 | N/A | ui |
| 28 | Cluster 17 | Event log replay accessors — not consolidatable | 0 | N/A | ui |
| 29 | Cluster 28 | Empire/planet resource pools — not consolidatable | 0 | N/A | strategy |
| 30 | Cluster 3 | Superweapon designation handlers — not recommended | 0 | N/A | ui |
| 31 | Cluster 21 | Tkinter dialogs — not recommended | 0 | N/A | ui |

**Total LOC Savings (consolidatable items):** ~530 lines across priority items 1–26
**Total LOC Savings (from clone detector's 685 estimated):** ~335 lines validated as genuinely consolidatable (excluding DEPRECATED, false positives, and INFO items)
