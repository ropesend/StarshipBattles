# Cross-Shard Duplication Report

## Summary
- Files Scanned: 749
- Total Findings: 30
- Critical: 2 | Major: 12 | Minor: 13 | Info: 3

## Clone Detector Validation

### Cluster 1: Cargo/Transfer Click Handlers
**Status:** CONFIRMED (MAJOR, consolidated to reference)

`_handle_drop_cargo_mode_click`, `_handle_load_cargo_mode_click`, `_handle_transfer_mode_click` in `strategy_click_dispatcher.py:233-259` are structural clones. The only difference is the dialog call (`open_cargo_quick_dialog` vs `open_transfer_dialog`) and the mode string. The team already recognized this pattern: `_handle_superweapon_click` (line 283) was created with comment `"Shared click handler for all superweapon-target modes (DUP-X-02)"` — the same consolidation approach should be applied here. **Estimated LOC savings: 24** (replace 3 x 12-line methods with 1 x 12-line method + 3 x 1-line callers).

### Cluster 2: Ability `__init__` in planetary.py
**Status:** CONFIRMED (MAJOR)

- `ShieldModifierAbility.__init__` (line 453) and `DamageModifierAbility.__init__` (line 528) are **identical** — same 4 fields with same defaults.
- `SystemShieldingAbility.__init__` (line 728) follows the same pattern with different fields (`max_shielding` instead of `multiplier`).

The `if isinstance(data, dict): ... else: defaults` pattern repeats in many more abilities in the same file (ThrustModifierAbility line 795, etc.). A shared `_parse_ability_data(data, required_fields)` base helper would eliminate the boilerplate. Pattern #9 (Template Method Validation) could be extended here. **Estimated LOC savings: 30** (consolidate 3+ identical constructor bodies into one base helper).

### Cluster 3: Superweapon Designation Handlers
**Status:** CONFIRMED (MAJOR, but limited consolidation value)

`handle_stellerate_star_designation`, `handle_close_warp_designation`, `handle_dyson_sphere_designation`, `handle_open_warp_designation` follow the same skeleton (fleet check → ability check → coordinate convert → target validate → confirmation → queue mission) but each has significantly different "guts" — different ability names, different UI calls (`_show_confirmation` vs `_show_system_picker`), different command DTOs, different post-conditions. Consolidation here would require a generic framework that's more complex than the 4 individual methods combined. **Est. LOC savings: 10** (extract coordinate conversion + ability check into shared helper). Downrate from 44 estimated to 10 feasible.

### Cluster 4: Selection Prompt Methods
**Status:** CONFIRMED (MINOR)

`prompt_planet`, `prompt_fleet`, `open_system` in `selection_prompts.py:29-85` share the same boilerplate: calculate centered rect → construct window → assign to composer slot. Consolidatable into a generic `_prompt_window(cls, widths, height, ...)` helper. **Estimated LOC savings: 15** (replace 3 methods with 1 generic + 3 one-liner callers).

### Cluster 5: Hit Effect Drawing Functions
**Status:** CONFIRMED (MAJOR)

`_draw_armor_hit` and `_draw_component_destroyed` in `hit_effects.py:146-203` are near-identical: create surface → draw expanding circle → draw radiating lines → blit. Differences are purely cosmetic (colors, line count, line width). Consolidate into a single parameterized function `_draw_radial_effect(screen, pos, effect, t, alpha, zoom, config)`. **Estimated LOC savings: 25** (replace 2 x ~28-line functions with 1 x ~25-line function + 2 x config dicts).

### Cluster 6: Squadron Delete/Duplicate Controller Methods
**Status:** CONFIRMED (MINOR)

`duplicate_squadron` and `delete_squadron` in `battle_setup/controller.py:283-301` are structural clones: get active fleet → validate task force → validate squadron → call FleetHierarchyEditor method → on_change. Consolidate into `_squadron_action(tf_index, sq_index, action_method)`. **Estimated LOC savings: 8** (replace 2 methods with 1 generic + 2 callers).

### Cluster 7: `__init_subclass__` Validators
**Status:** CONFIRMED (INFO)

`StaticValueAbility.__init_subclass__` (line 450) and `SimpleMultiplierAbility.__init_subclass__` (line 502) in `abilities/base.py` share the validation loop pattern. Different required attribute sets justify the duplication — each checks a distinct set of class attributes. The pattern itself is intentional (Template Method subclass validation). No consolidation needed.

### Cluster 8: System/Sector Effects Methods
**Status:** CONFIRMED (MINOR, already partially consolidated)

`_add_system_effects` (line 467) and `_add_sector_effects` (line 482) in `system_tree_panel.py` are near-twins. Both already delegate to the shared `_add_effects_group` helper (line 497). The remaining duplication is in the try/except wrapper and the import/call pattern. **Estimated LOC savings: 10** (merge into single parameterized method).

### Cluster 9: Superweapon Mission Execute — StellerateStar / CreateDysonSphere
**Status:** CONFIRMED (MAJOR)

`StellerateStarMissionCommandHandler.execute` (line 296) and `CreateDysonSphereMissionCommandHandler.execute` (line 415) follow the identical 4-step template: 1) resolve fleet, 2) validate ability, 3) add move, 4) emit order. Same as Cluster 19 below. **Estimated LOC savings: 35** (consolidate 4 mission handlers into one template method).

### Cluster 10: `get_stat_summary` vs `get_stat_summary_static`
**Status:** CONFIRMED (MAJOR)

The static method `get_stat_summary_static` (line 297) is a byte-for-byte copy of the instance method `get_stat_summary` (line 166) taking a `modifiers_list` parameter instead of `self._modifiers`. The static method is already marked DEPRECATED with comment "Will be removed in Task 1.3". **Do not consolidate — just delete the static method when ready.** **Estimated LOC savings: 53** (delete deprecated static method entirely, no consolidation needed).

### Cluster 11: Race Randomizer Pick Methods
**Status:** CONFIRMED (MINOR)

`_pick_name_entry` and `_pick_leader` in `race_randomizer.py:109-142` follow identical logic with different data keys. Consolidatable into `_pick_from_portrait(data, portrait_id, rng, key, fallback_key, default_value)`. **Estimated LOC savings: 12** (replace 2 x 15-line methods with 1 x 16-line helper + 2 x 2-line callers).

### Cluster 12: Event Log Replay Methods
**Status:** CONFIRMED (MINOR)

`get_cell_replay_id` (line 150) and `get_cell_replay_unavailable_reason` (line 172) follow identical structure: get event → check None → check category → return details[key]. Consolidate into `_get_cell_detail(key)`. **Estimated LOC savings: 12** (replace 2 methods with 1 generic + 2 one-liner callers).

### Cluster 13: Component Grouping Strategies
**Status:** CONFIRMED (INFO)

`DefaultGroupingStrategy.group_components` and `TypeGroupingStrategy.group_components` share the defaultdict/sort/mass-compute loop. However, these implement the same `GroupingStrategy` protocol (Strategy Pattern), and the similarity is inherent to the protocol contract. Minor opportunity: extract a `_aggregate_groups(groups_dict)` helper. **Estimated LOC savings: 6**.

### Cluster 14: Race Panel `_create_content` Methods
**Status:** CONFIRMED (INFO)

`_create_content` in `race_aptitudes_panel.py:91` and `race_identity_panel.py:86` share the section-layout skeleton (get width, y=5, call sections with y+=15 spacing). Weak consolidation case — the panels serve different purposes and the section calls are completely different. Not worth consolidating.

### Cluster 15: Tkinter Dialog Functions
**Status:** CONFIRMED (MINOR)

`open_save_dialog` and `open_load_dialog` in `tkinter_utils.py:108-177` are structural twins: get root → check None → set default filetypes → call filedialog function → catch errors. Could extract a shared `_tk_dialog(dialog_func, **kwargs)` helper. **Estimated LOC savings: 15**.

### Cluster 16: Test Lab Panel `__init__` Methods
**Status:** CONFIRMED (MINOR)

`CategoryPanel.__init__` and `TestListPanel.__init__` share the font/color/dimension storage pattern. Both are simple constructor property assignments — the similarity is cosmetic rather than structural logic duplication. Low consolidation value.

### Cluster 17: LLM and Image Factory `create` Methods
**Status:** CONFIRMED (MAJOR — also ARCHITECTURAL DRIFT)

`LLMProviderFactory.create` (line 52) and `ImageProviderFactory.create` (line 47) are near-identical static factory methods. Pattern #15 (Factory) is documented, but these two classes reimplement the same lookup-and-construct logic with different env-var and exception-class names. A `ProviderFactory` base class or generic function would eliminate the duplication. **This is both duplication AND lacks the documented Factory pattern reuse.** **Estimated LOC savings: 25**.

### Cluster 18: Ability Iterator Providers
**Status:** CONFIRMED (MINOR)

`_planet_intrinsic_provider` (line 217) and `_warp_point_provider` (line 288) share the same logic: check container → iterate items → skip no abilities → create adapter → yield if in hex. Differences: container attribute name and adapter class. **Estimated LOC savings: 10** (extract `_iter_ability_source(container, adapter_cls, hex_coord)` helper).

### Cluster 19: Superweapon Mission Execute — OpenWarp / CloseWarp
**Status:** CONFIRMED (MAJOR, superset of Cluster 9)

`OpenWarpPointMissionCommandHandler.execute` (line 332) and `CloseWarpPointMissionCommandHandler.execute` (line 373) also follow the 4-step template, but include additional target dict construction. Together with Cluster 9, there are **4 mission handlers** sharing the same skeleton. All 5 superweapon mission handlers (including the 5th not in any cluster) should use a `MissionCommandHandler.execute(session, cmd, validator_fn, order_type, target_dict_fn)` template method. **Estimated LOC savings: 60** (consolidate 5 handlers into one template).

### Cluster 20: Cargo Load/Unload Methods
**Status:** CONFIRMED (MAJOR)

`load_cargo_to_fleet` (line 291) and `unload_cargo_from_fleet` (line 317) in `fleet_consumable_aggregator.py` are identical except for the ship operation call (`load_cargo` vs `unload_cargo`) and variable naming. Consolidate into `_distribute_cargo_to_fleet(cargo_type, amount, ship_method)`. **Estimated LOC savings: 18**.

### Cluster 21: Fleet Ops Execute Methods
**Status:** CONFIRMED (MINOR)

`execute_intercept` (line 134) and `execute_join` (line 197) in `strategy_fleet_ops.py` share identical structure: create command DTO → facade.handle_command → check result → log. Consolidate into `_execute_fleet_command(fleet, command, operation_name)`. **Estimated LOC savings: 10**.

### Cluster 22: Resource Addition Methods
**Status:** CONFIRMED (MINOR, but valid protocol conformance)

`empire.add_resources` (line 201) and `planet.add_to_stockpile` (line 200) share the same overflow calculation: `current + amount → if > max: set max, return overflow; else: set sum, return 0`. However, these operate on different storage attributes (`_fleet_resource_pool` vs `stockpile`) and implement different protocols. The Empire is an infrastructure resource pool; the Planet is a stockpile holder. Consolidation would require protocol-level changes. **Estimated LOC savings: 0** (protocol conformance — not duplication).

---

## Cross-Shard Findings

### CRITICAL: Superweapon Command Handler Template (Architectural Drift)
**ID:** DUP-X-01
**Location:** `game/strategy/engine/superweapon_command_handlers.py:296-438` (5 execute methods) AND `game/strategy/engine/handlers/` (24+ `_resolve_player_fleet` call sites)
**Layer:** strategy (command handler registry)
**Issue:** Five mission command handlers (`StellerateStar`, `OpenWarpPoint`, `CloseWarpPoint`, `CreateDysonSphere`, `ImplodePlanet`) all implement the same 4-step execute skeleton: resolve fleet → validate ability → add move if needed → emit validated order. Each handler duplicates ~23 lines of identical control flow. The clone detector found clusters within this set (Clusters 9, 19) but missed the full set. This contradicts the `CommandHandlerRegistry` pattern (#7) which expects self-registering handlers via metadata, not duplicated boilerplate. The `BaseCommandHandler` already provides `_resolve_player_fleet` and `_emit_validated_order`; a single `MissionCommandHandler` template with injected validator function would eliminate all 5.
**Impact:** Adding a new superweapon requires copy-pasting ~23 lines and updating 4 places (ability check string, validator call, order type, mission name). Bug risk: if the move-step logic changes, 5 places must be updated identically.
**Recommendation:** Create a `MissionCommandHandler` template class that accepts `validator_fn`, `order_type`, and optional `target_dict_fn`. All 5 handlers reduce to one-line subclasses with class-level configuration.
**Estimated LOC Savings:** 60
**Effort:** Medium

### CRITICAL: LLM/Image Provider Factory Duplication (Pattern #15 Violation)
**ID:** DUP-X-02
**Location:** `game/services/llm/factory.py:52-87` AND `game/ui/services/image/factory.py:47-79`
**Layer:** services (cross-cutting, different sub-packages)
**Issue:** `LLMProviderFactory.create` and `ImageProviderFactory.create` implement identical logic: read env var for provider name, look up in `_PROVIDERS` dict, raise config error if missing, construct with config-error-return-None. Only the env var, default value, and exception class differ. This reimplements the Factory pattern (#15) as two near-identical singletons instead of a shared `ProviderFactory` base. Architecture docs state "Factories pair well with tests when construction depends on registries, environment variables, display state, providers, or mode-specific policy" — yet these two are not testable via a shared interface.
**Impact:** Changes to factory behavior (e.g., adding logging on construction, retry logic, metrics) must be made in two places. Test coverage must duplicate factory tests.
**Recommendation:** Extract a `ProviderFactory` base class (or generic function) taking `provider_dict`, `env_var`, `default`, `error_class`, and `config_error_class` as parameters. Both existing factories become thin subclasses or direct call sites.
**Estimated LOC Savings:** 25
**Effort:** Simple

---

### MAJOR: Ability `__init__` Boilerplate Extends Beyond 3 Found
**ID:** DUP-X-03
**Location:** `game/simulation/components/abilities/planetary.py:453-800` (6+ ability classes)
**Layer:** simulation (ability definitions)
**Issue:** The clone detector found 3 near-identical `__init__` methods, but the broader scan reveals that virtually every ability class in planetary.py implements the same `if isinstance(data, dict): self.X = data.get("X", default)` pattern. Classes found: `ShieldModifierAbility`, `DamageModifierAbility`, `QualityImprovementAbility`, `SystemShieldingAbility`, `ThrustModifierAbility`, and more. The same pattern extends to `get_ui_rows` — many abilities build the same row structure with different labels/values.
**Impact:** Adding a new field to ability data requires updating every `__init__` with that field. The `get_ui_rows` methods are nearly identical boilerplate.
**Recommendation:** Introduce a `_parse_data_fields(data, field_specs: dict)` base helper and a declarative `ui_row_spec` class attribute that `get_ui_rows` iterates. This aligns with Pattern #14 (Two-Phase Ability Aggregation) and the existing `SimpleMultiplierAbility`/`StaticValueAbility` base class approach (lines 440-535 in base.py).
**Estimated LOC Savings:** 30 (for the 3 found + additional classes)
**Effort:** Medium

### MAJOR: Hit Effect Rendering Functions
**ID:** DUP-X-04
**Location:** `game/ui/effects/hit_effects.py:146-219`
**Layer:** ui (effects)
**Issue:** `_draw_armor_hit`, `_draw_component_destroyed`, and `_draw_ship_destroyed` all implement the same rendering algorithm: create transparent surface → draw expanding circle at time t → draw radiating lines → blit. The differences are only in color, line count, line length factor, and circle width formula. This is pure visual parameterization — no business logic difference.
**Impact:** Changing the effect rendering algorithm (e.g., supporting different blending modes) requires editing 3 functions identically.
**Recommendation:** Extract `_draw_hit_effect(screen, pos, effect, t, alpha, zoom, *, circle_color, line_color, num_lines, line_len_factor, circle_width_fn)` and define 3 config dicts indexed by `HitEffectType`.
**Estimated LOC Savings:** 25
**Effort:** Simple

### MAJOR: Deprecated Static Duplicate — `ModifierManager` 
**ID:** DUP-X-05
**Location:** `game/simulation/components/modifier_manager.py:166-330`
**Layer:** simulation
**Issue:** Five static methods (`add_modifier_static`, `remove_modifier_static`, `remove_modifier_inplace`, `get_modifier_static`, `get_all_effects_static`, `get_stat_summary_static`) are complete copies of the instance methods, each marked "DEPRECATED...Will be removed in Task 1.3." The static duplicates account for ~165 lines at 50% of the file. The instance methods already exist and are functionally identical.
**Impact:** Dead code with near-zero test coverage for the static variants. Maintainers may accidentally fix a bug in one but not the other. File is at 330 LOC; removing the deprecated section would bring it well under 200.
**Recommendation:** Execute the Task 1.3 removal. Grep for all callers of `*_static` methods — if none exist in production, delete immediately. If callers exist, migrate them to instance methods first.
**Estimated LOC Savings:** 100 (entire deprecated block)
**Effort:** Simple (if no callers)

### MAJOR: Cargo Load/Unload Mirror Methods
**ID:** DUP-X-06
**Location:** `game/strategy/data/fleet_consumable_aggregator.py:291-341`
**Layer:** strategy (data)
**Issue:** `load_cargo_to_fleet` and `unload_cargo_from_fleet` are mirror images: iterate ships, call ship method, accumulate total, track remaining. The only difference is `ship.load_cargo` vs `ship.unload_cargo`. This is textbook copy-paste with opposite operands.
**Impact:** Any change to cargo distribution logic (e.g., priority-based distribution, partial loading) must be made identically in both methods. Risk of asymmetry bugs.
**Recommendation:** Extract `_distribute_cargo_to_fleet(cargo_type, amount, ship_method)` where `ship_method` is a callable. The two public methods become one-liner wrappers.
**Estimated LOC Savings:** 18
**Effort:** Simple

### MAJOR: Right-Click Cancel Pattern (9 occurrences)
**ID:** DUP-X-07
**Location:** `game/ui/screens/strategy_click_dispatcher.py:125-297` (9 separate methods)
**Layer:** ui (input handling)
**Issue:** Nine click handler methods (`_handle_move_mode_click`, `_handle_join_mode_click`, `_handle_colonize_mode_click`, `_handle_transfer_mode_click`, `_handle_edit_move_click`, `_handle_drop_cargo_mode_click`, `_handle_load_cargo_mode_click`, `_handle_warp_target_click`, and via `_handle_superweapon_click`) each contain an identical right-click cancel block: `elif button == 3: self.input_mode = 'SELECT'; logger.debug("Input Mode: SELECT"); return True`. The team already consolidated the superweapon handlers (line 283) but left the fully identical cargo/transfer handlers unconsolidated (Cluster 1).
**Impact:** Adding a new click mode requires copy-pasting the right-click cancel boilerplate.
**Recommendation:** Create a `_handle_input_mode_click(mx, my, button, mode_name, left_click_action)` base handler. All mode handlers become dispatchers to this base. Already partially done for superweapons.
**Estimated LOC Savings:** 24 (from the 3 cargo/transfer handlers) + ongoing savings for future modes
**Effort:** Medium

### MAJOR: Superweapon UI Duplication (Ability Check + Coordinate Conversion)
**ID:** DUP-X-08
**Location:** `game/ui/screens/strategy_superweapons.py:78-309` (5 designation handlers)
**Layer:** ui (superweapons)
**Issue:** Five designation handlers replicate the same `fleet.capabilities.has_ability("X")` check and the same `world_pos = self.camera.screen_to_world((mx, my)); target_hex = pixel_to_hex(world_pos.x, world_pos.y, self.hex_size)` coordinate conversion. Additionally, `pixel_to_hex(world_pos.x, world_pos.y, ...)` is copy-pasted 11 times across 4 files (superweapons, fleet_ops, colonization, click_dispatcher, input_handler).
**Impact:** If the coordinate conversion API changes, 11 call sites must be updated. Ability check strings are scattered and prone to typos.
**Recommendation:** Extract a `self.camera.hex_at_screen(mx, my)` convenience method. Extract the ability-check pattern into a `_check_fleet_ability(fleet, ability_name, error_msg)` validator.
**Estimated LOC Savings:** 15
**Effort:** Simple

### MAJOR: Event Log Cell Detail Methods
**ID:** DUP-X-09
**Location:** `game/ui/screens/event_log_data_source.py:150-194`
**Layer:** ui (event log)
**Issue:** `get_cell_replay_id` and `get_cell_replay_unavailable_reason` are structural clones sharing the identical `get_event → check None → check category → return details[key]` pattern. The larger `get_cell_replay_id`/`get_cell_replay_unavailable_reason` pair also mirrors a broader pattern used by other cell-getter methods.
**Impact:** Adding a new event-detail accessor requires copy-pasting the 3-step guard pattern.
**Recommendation:** Extract `_get_cell_detail(row_index, detail_key)` returning `Optional[Any]`. The two methods become one-liner wrappers.
**Estimated LOC Savings:** 12
**Effort:** Simple

### MAJOR: Strategy Fleet Ops Result Handling
**ID:** DUP-X-10
**Location:** `game/ui/screens/strategy_fleet_ops.py:127,153,216`
**Layer:** ui (fleet operations)
**Issue:** Three methods (`execute_move`, `execute_intercept`, `execute_join`) contain identical error handling: `msg = result.message if result else 'Unknown'; logger.warning(...)`. This pattern also appears in `strategy_click_dispatcher.py:274` and `strategy_superweapons.py`. The fragmentation means error messages format inconsistently.
**Impact:** Changing logging format or error field requires updating 4+ sites.
**Recommendation:** Extract a `_format_result_error(result, operation)` helper. Standardize across all strategy UI modules.
**Estimated LOC Savings:** 8
**Effort:** Simple

### MAJOR: Serialization `to_dict`/`from_dict` Duplication Across Layers
**ID:** DUP-X-11
**Location:** 55 `to_dict` + 57 `from_dict` methods across `game/strategy/data/`, `game/simulation/`, `game/core/`
**Layer:** All layers (strategy, simulation, core)
**Issue:** 112 serialization methods exist across the codebase. Pattern #17 (Serializable Protocol) is well-documented, but the actual implementations are inconsistent — some manually enumerate fields, some use `__dict__`, some handle nested objects recursively. The `BattleEndCondition` hierarchy alone has 8 near-identical `to_dict`/`from_dict` pairs in `battle_end_conditions.py`.
**Impact:** Adding a new field to a serialized class often requires manual updates in both `to_dict` and `from_dict`. Inconsistent implementations mean some fields are silently lost on round-trip.
**Recommendation:** For dataclass-based entities, investigate a `@serializable` decorator or metaclass that auto-generates `to_dict`/`from_dict` from type annotations. For the `BattleEndCondition` hierarchy, add a base `to_dict` that calls a `_serialize_fields()` abstract method.
**Estimated LOC Savings:** 40 (for battle end conditions specifically) 
**Effort:** Complex

### MAJOR: Ability Source Provider Pattern Duplication
**ID:** DUP-X-12
**Location:** `game/strategy/services/ability_iterator.py:217-298` AND `game/strategy/services/ability_sources/`
**Layer:** strategy (services)
**Issue:** `_planet_intrinsic_provider`, `_warp_point_provider`, `_star_provider`, `_system_archetype_provider`, and `_fleet_provider` all follow the same logic skeleton: check container existence → iterate items → skip items without abilities → create adapter → conditionally yield. The `_facility_provider` and `_storm_provider` (in the same file) also follow this pattern with minor variations. This is the Universal Ability Source pattern (#29), but each provider reimplements the container-iteration boilerplate rather than using a shared base.
**Impact:** Adding a new ability source provider requires copy-pasting the iteration skeleton.
**Recommendation:** A `_iter_ability_sources(container, adapter_cls, filter_fn=bool, hex_coord=None)` generic function would condense these 6-7 providers.
**Estimated LOC Savings:** 25
**Effort:** Medium

---

### MINOR: Selection Prompt Window Creation
**ID:** DUP-X-13
**Location:** `game/ui/screens/strategy_windows/selection_prompts.py:29-85`
**Layer:** ui (strategy windows)
**Issue:** `prompt_planet`, `prompt_fleet`, `open_system` all duplicate the centered-rect calculation + window construction + slot assignment. Differ only in width, height, window class, and data args.
**Recommendation:** Generic `_create_prompt_window(cls, width, height, *args)` helper.
**Estimated LOC Savings:** 15
**Effort:** Simple

### MINOR: Squadron Action Methods
**ID:** DUP-X-14
**Location:** `game/ui/screens/battle_setup/controller.py:283-301`
**Layer:** ui (battle setup)
**Issue:** `duplicate_squadron` and `delete_squadron` differ only in the `FleetHierarchyEditor` method call. A generic `_squadron_action(tf_index, sq_index, action)` helper would eliminate 2 methods.
**Estimated LOC Savings:** 8
**Effort:** Simple

### MINOR: Race Randomizer Pick Functions
**ID:** DUP-X-15
**Location:** `game/strategy/systems/race_randomizer.py:109-142`
**Layer:** strategy
**Issue:** `_pick_name_entry` and `_pick_leader` share the portrait-data lookup → fallback → default pattern. Extract `_pick_from_portrait(data, portrait_id, rng, data_key, fallback_key, default_value)`.
**Estimated LOC Savings:** 12
**Effort:** Simple

### MINOR: Tkinter File Dialog Functions
**ID:** DUP-X-16
**Location:** `game/ui/services/tkinter_utils.py:108-177`
**Layer:** ui (services)
**Issue:** `open_save_dialog` and `open_load_dialog` are structural twins. Shared `_tk_file_dialog(dialog_callable, **kwargs)` would eliminate the root-check and error-handling duplication.
**Estimated LOC Savings:** 15
**Effort:** Simple

### MINOR: System/Sector Effects Wrappers
**ID:** DUP-X-17
**Location:** `game/ui/panels/system_tree_panel.py:467-495`
**Layer:** ui (panels)
**Issue:** `_add_system_effects` and `_add_sector_effects` already delegate to shared `_add_effects_group`. The remaining boilerplate (import + context check + collector call + effects_group call) could merge into `_add_scoped_effects(collector_fn, scope_label, **extra_args)`.
**Estimated LOC Savings:** 10
**Effort:** Simple

### MINOR: Component Grouping Aggregate Logic
**ID:** DUP-X-18
**Location:** `game/ui/screens/builder/grouping_strategies.py:18-69`
**Layer:** ui (builder)
**Issue:** `DefaultGroupingStrategy.group_components` and `TypeGroupingStrategy.group_components` share the defaultdict → sort → mass-sum → result-builder loop. Extract `_build_grouped_result(groups_dict)`.
**Estimated LOC Savings:** 6
**Effort:** Simple

### MINOR: Fleet Ops Execute Methods
**ID:** DUP-X-19
**Location:** `game/ui/screens/strategy_fleet_ops.py:134-218`
**Layer:** ui (fleet operations)
**Issue:** `execute_intercept` and `execute_join` are structural twins. Extract `_execute_fleet_command(cmd, op_name)`.
**Estimated LOC Savings:** 10
**Effort:** Simple

### MINOR: Test Lab Panel Constructors
**ID:** DUP-X-20
**Location:** `game/ui/screens/test_lab/renderer/category_panel.py:28-52` AND `test_list_panel.py:27-51`
**Layer:** ui (test lab)
**Issue:** Both panels accept and store the same font/color/dimension parameters. A shared `_PanelStyleConfig` dataclass would reduce constructor argument count and eliminate the 7-field duplication.
**Estimated LOC Savings:** 5
**Effort:** Simple

### MINOR: Ability Iterator Providers (Planet/WarpPoint)
**ID:** DUP-X-21
**Location:** `game/strategy/services/ability_iterator.py:217-298`
**Layer:** strategy (services)
**Issue:** `_planet_intrinsic_provider` and `_warp_point_provider` share the container iteration → ability check → adapter creation → hex filter pattern. The broader issue (DUP-X-12) covers this, but these two are the most similar pair.
**Estimated LOC Savings:** 10 (of the 25 from DUP-X-12)
**Effort:** Simple

### MINOR: Coordinate Conversion Fragmentation
**ID:** DUP-X-22
**Location:** `game/ui/screens/strategy_superweapons.py` (5 sites), `strategy_fleet_ops.py` (2 sites), `strategy_colonization.py` (1 site), `strategy_click_dispatcher.py` (2 sites), `strategy_input_handler.py` (1 site)
**Layer:** ui (multiple screens)
**Issue:** `pixel_to_hex(world_pos.x, world_pos.y, self.hex_size)` appears 11 times across 5 files. A `Camera.hex_at_screen(mx, my)` convenience method would eliminate the repetitive `screen_to_world` + `pixel_to_hex` two-step.
**Impact:** 11 dup sites, moderate risk of inconsistency if pixel_to_hex signature changes.
**Recommendation:** Add `Camera.hex_at_screen(screen_x: int, screen_y: int) -> HexCoord`.
**Estimated LOC Savings:** 5 (syntactic cleanup, not LOC reduction per se)
**Effort:** Simple

---

## Prioritized Consolidation Plan

Ordered by impact/effort ratio (safest, highest ROI first):

| Rank | ID | Finding | Savings | Effort | Impact/Effort |
|------|-----|---------|---------|--------|---------------|
| 1 | DUP-X-05 | Deprecated `ModifierManager` static methods (delete) | 100 | Simple | Very High |
| 2 | DUP-X-07+C1 | Right-click cancel + cargo/transfer handler consolidation | 48 | Medium | High |
| 3 | DUP-X-01 | Superweapon mission handler template (5 handlers) | 60 | Medium | High |
| 4 | DUP-X-04 | Hit effect rendering parameterization | 25 | Simple | High |
| 5 | DUP-X-02 | Provider factory base (LLM + Image) | 25 | Simple | High |
| 6 | DUP-X-06 | Cargo load/unload mirror | 18 | Simple | High |
| 7 | DUP-X-03 | Ability __init__ boilerplate (planetary.py) | 30 | Medium | Medium |
| 8 | DUP-X-12 | Ability source provider boilerplate | 25 | Medium | Medium |
| 9 | DUP-X-15 | Race randomizer pick functions | 12 | Simple | Medium |
| 10 | DUP-X-16 | Tkinter file dialog consolidation | 15 | Simple | Medium |
| 11 | DUP-X-13 | Selection prompt window creation | 15 | Simple | Medium |
| 12 | DUP-X-09 | Event log cell detail methods | 12 | Simple | Medium |
| 13 | DUP-X-08 | Superweapon ability check + coordinate conversion | 15 | Simple | Medium |
| 14 | DUP-X-10 | Fleet ops result handling | 8 | Simple | Medium |
| 15 | DUP-X-17 | System/sector effects wrappers | 10 | Simple | Medium |
| 16 | DUP-X-11 | Serialization to_dict/from_dict (battle end conditions) | 40 | Complex | Low |
| 17 | DUP-X-19 | Fleet ops execute methods | 10 | Simple | Low |
| 18 | DUP-X-14 | Squadron action methods | 8 | Simple | Low |
| 19 | DUP-X-21 | Ability iterator providers (planet/warp) | 10 | Simple | Low |
| 20 | DUP-X-18 | Component grouping aggregate logic | 6 | Simple | Low |
| 21 | DUP-X-22 | Coordinate conversion fragmentation | 5 | Simple | Low |
| 22 | DUP-X-20 | Test lab panel constructors | 5 | Simple | Low |

**Total estimated LOC savings (achievable): 475**
**Total estimated LOC savings (safe, Simple effort items): 190**
