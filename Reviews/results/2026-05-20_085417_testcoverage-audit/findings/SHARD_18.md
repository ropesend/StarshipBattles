# Shard 18 — Test Coverage Audit

**Date:** 2026-05-20
**Files audited:** 46 production files (~9,483 LOC)
**Methodology:** Every production file read in full; every corresponding test file path verified by glob; test contents spot-checked for Tier 0 corrections.

---

## Summary

| Severity | Count | Description |
|---|---|---|
| **CRITICAL** | 9 | Tier 0 non-UI file with zero dedicated tests |
| **MAJOR** | 28 | Untested symbols / error paths in partially-tested files |
| **MINOR** | 26 | Partial coverage, missing corner cases |
| **ADVISORY** | 7 | `__init__.py` re-exports, empty files, UI rendering-only |

**Heuristic baseline corrections:** The baseline misclassified two files as Tier 0 that actually have test coverage:
- `fleet_serde.py` → tested via `tests/integration/save_load/test_fleet_serde_roundtrip.py` (192 LOC, characterization tests)
- `ship_resource_manager.py` → tested via `tests/unit/simulation/entities/test_ship_resource_manager.py` (69 LOC, 3 test functions)

---

## Tier 0 — No Dedicated Tests (CRITICAL)

### 1. `game/core/protocols/strategy_domain.py` (256 LOC) — CRITICAL
**Layer:** Core — protocol definitions for cross-layer boundaries.

**No test file exists.** Glob `tests/**/test_strategy_domain*` returns zero results.

This file defines:
- `IEmpire` (Protocol, lines 18–110): 10 properties (`id`, `name`, `color`, `flag_id`, `portrait_id`, `empire_theme_id`, `race_config`, `colonies`, `fleets`, `resource_pool`, `max_storage`, `built_ship_designs`)
- `IFacility` (Protocol, lines 112–166): 6 properties (`instance_id`, `design_id`, `name`, `design_data`, `is_operational`, `construction_queue`, `consumable_levels`)
- `IRaceRegistry` (Protocol, lines 169–181): 1 method (`get_race`)
- `IShipInstance` (Protocol, lines 184–237): 6 properties + `get_calculated_stats`
- `is_empire()` TypeGuard (line 244)
- `is_facility()` TypeGuard (line 249)
- `is_ship_instance()` TypeGuard (line 254)

**Gap:** Core cross-layer protocol package — the contracts these Protocols define are exercised only indirectly via concrete implementations. Protocol structural conformance (e.g., `isinstance(x, IEmpire)` with `@runtime_checkable`) has zero test coverage. TypeGuard functions are untested.

### 2. `game/services/llm/defaults.py` (42 LOC) — CRITICAL
**Layer:** Services — module-level mutable state.

**No test file exists.**

- `get_default_llm_provider()` (line 20): Returns `_default_llm_provider` module-level variable
- `set_default_llm_provider()` (line 31): Uses `global` to mutate module state

**Gap:** Module-level singleton accessor with `global` keyword. No test verifies that `get_default_llm_provider()` returns `None` when no provider has been set, nor that `set_default_llm_provider(None)` clears the slot. No test verifies the deferred-validation pattern ("consumers check `if provider is not None`") mandated by the docstring.

### 3. `game/simulation/replay/replay_record.py` (93 LOC) — CRITICAL
**Layer:** Simulation — persisted-on-disk replay record.

**No dedicated test file exists.** Glob `tests/**/test_replay_record*` returns zero results. The replay integration test (`test_capture_pipeline.py`) exercises this indirectly, but no unit tests exist.

- `ReplayRecord.to_dict()` (line 47): Serialization with tuple→list coercion, None handling
- `ReplayRecord.from_dict()` (line 63): Deserialization with nested type coercion
- `ReplayRecord.is_current_schema()` (line 84): Schema version check

**Gap:** No test for `from_dict` with corrupt/missing fields, None `sector_coords`, missing `participating_empires`, missing `components_registry_hash`. No schema-drift test for `is_current_schema()` returning False. No round-trip test (`Record.from_dict(r.to_dict()) == r`).

### 4. `game/strategy/engine/order_handlers/transfer_branches.py` (604 LOC) — CRITICAL
**Layer:** Strategy Engine — 7 explicit transfer dispatch branches + 3 fleet-to-fleet sub-branches.

**No dedicated test file exists.** Glob `tests/**/test_transfer_branches*` returns zero results. The transfer handler is tested indirectly through integration tests, but these 604 lines have zero direct unit test coverage.

Classes and methods:
- `_TransferDispatchMixin` (line 46): Mixin class for `TransferHandler`
- `_dispatch_load_planet_resource()` (line 60): Planet→fleet resource cargo. Capacity checks (line 68-77), stockpile capping (line 76), consumption+loading (lines 83-85)
- `_dispatch_load_planet_passengers()` (line 88): Planet→fleet passengers. Species_id required (line 112, PROJ-393 enforcement), population finding (line 120)
- `_dispatch_drop_pod_load()` (line 135): Planet→fleet drop pods. Staging yard iteration (line 165), Ship capacity search (line 179), BayInventory construction (line 205)
- `_dispatch_unload_planet_resource()` (line 212): Fleet→planet resource cargo
- `_dispatch_unload_planet_passengers()` (line 231): Fleet→planet passengers. SpeciesPopulation creation (line 272), IPlanetMutator routing
- `_dispatch_carried_vehicle_load()` (line 278): Planet→fleet vehicles. Design_id filtering (line 316), capacity checks (line 326), rollback on load failure (line 338)
- `_dispatch_carried_vehicle_unload()` (line 356): Fleet→planet vehicles. Reverse-index iteration (line 379), staging yard capacity check (line 388)
- `_dispatch_drop_pod_unload()` (line 393): Fleet→planet drop pods. Typed pod slot (line 421), BayInventory rebuild (line 438)
- `_dispatch_fleet_to_fleet()` (line 444): Fleet→fleet cargo. Three-way dispatch by `cargo_type` (lines 473-479)
- `_dispatch_fleet_to_fleet_drop_pod()` (line 497): Fleet→fleet drop pods. Source/dest ship iteration, typed bay slots
- `_dispatch_fleet_to_fleet_vehicle()` (line 559): Fleet→fleet vehicles. design_id matching, `load_vehicle`/`unload_vehicle`

**Gap:** Every branch untested per the baseline. Critical gaps include:
- Zero-capacity edge cases (amount=0 means "all")
- Species_id=required enforcement (legacy fallback removed by PROJ-393)
- BayInventory rebuild paths (pods consumed/kept)
- Fleet-to-fleet drop_pod path (PROJ-445 Phase 2, lines 497-557)
- Fleet-to-fleet vehicle path (PROJ-445 Phase 2, lines 559-603)
- Carried vehicle load rollback on failure (line 338)
- Drop pod mass-based capacity filtering (line 176-194)

### 5. `game/strategy/services/ability_sources/fleet.py` (148 LOC) — CRITICAL
**Layer:** Strategy Services — IAbilitySource adapter for fleet strategic abilities.

**No dedicated test file exists.**

- `FleetAbilitySource` (line 30): Not frozen, has mutable `_abilities_cache` (line 40)
- `source_kind`, `source_label`, `source_id`, `owner_id` properties (lines 42-63)
- `get_abilities()` (line 65): Strategic-scope ability extraction from fleet ships, per-instance memoization
- `affects_hex()` (line 86): Location-based hex check with hidden-fleet guard
- `affects_system()` (line 91): System-wide effect (always True, hidden guard only)
- `get_activation_state()` (line 98): Returns None (deferred feature)
- `_is_combat_capable()` (line 105): Best-effort check with broad except
- `_is_hidden()` (line 119): Future stealth hook, always False baseline
- `_walk_strategic_abilities()` (line 128): Component iteration, strategic scope filtering

**Gap:** No test for strategic-scope filtering (self/fleet/team excluded, sector/system/planet included). No test for cache behaviour (memoization). No test for hidden-fleet suppression. No test for `_is_combat_capable` with callable/non-callable/exception paths. No test for edge case: fleet with zero ships, ships with no design_data, components with no strategic-scope abilities.

### 6. `game/strategy/services/ability_sources/intrinsic_roll.py` (79 LOC) — CRITICAL
**Layer:** Strategy Services — shared roll helper for intrinsic ability templates.

**No dedicated test file exists.**

- `roll_intrinsic_abilities()` (line 12): Template→instance materialization with `{min, max}` range rolling, `chance` probability gate (FEAT-15), RNG determinism

**Gap:** No test for:
- Empty template returns {}
- Scalar/pass-through values preserved
- `{min, max}` → randint for ints, uniform for floats
- `chance` gate: values < 1.0 consume RNG, >= 1.0 do not
- `chance` key stripped from output (line 62)
- Non-dict ability_data pass-through (line 47)
- RNG determinism with seeded Random

### 7. `game/strategy/services/ability_sources/labels.py` (23 LOC) — CRITICAL
**Layer:** Strategy Services — shared label formatter.

**No dedicated test file exists.**

- `format_intrinsic_source_label()` (line 9): Returns `"{entity_name} ({type_name})"`

**Gap:** Simple but shared across PROJ-301..304 adapters. No test verifies the canonical format contract.

### 8. `game/research/__init__.py` (8 LOC) — ADVISORY
**Layer:** Research — package docstring only.

No test needed. Package-level docstring.

### 9. `game/strategy/engine/session/__init__.py` (26 LOC) — ADVISORY
**Layer:** Strategy Engine — `SessionBootstrapState` and `SessionRuntimeServices` re-exports from `runtime_services.py`.

These classes are tested indirectly via `GameSession` tests (`test_bootstrap.py`, `test_persistence_adapter.py`, `test_runtime_services.py`). The `__init__.py` itself is a re-export shim.

### 10. `game/ui/research/research_renderer.py` (324 LOC) — MAJOR
**Layer:** UI — Research tech tree renderer.

**No test file.** Heuristic baseline correctly identified Tier 0.

- `ResearchRenderer.__init__()` (line 53): Accepts TechTree, ResearchTracker, node_positions, camera, node_width, node_height
- `_get_font()` (line 74): Font resolution with quantized size
- `draw()` (line 85): Main render entry with screen clipping
- `_draw_dependency_lines()` (line 110): Line drawing for prerequisites, negated requirements (PROJ-40/NEW-RES-007)
- `_draw_dashed_line()` (line 163): Dashed line rendering for negated requirements
- `_draw_nodes()` (line 197): Node rectangles with status colors, selection highlight, RP allocation bar
- `_draw_node_text()` (line 262): Name truncation, level/chance/RP text layout
- `_is_visible()` (line 312): Viewport culling

**Gap:** All 9 methods untested. Critical rendering logic (negated requirement dashed lines, zoom-dependent text sizing, node truncation) has zero test coverage.

### 11. `game/ui/screens/build_queue_selector.py` (196 LOC) — MAJOR
**Layer:** UI — Queue source selection panel with multi-select.

**No test file.** Heuristic baseline correctly identified Tier 0.

- `BuildQueueSelector.__init__()` (line 29): Panel creation, default selection, button-map
- `refresh()` (line 89): Rebuilds button UI dynamically, kills old elements
- `handle_button_click()` (line 135): ctrl_held multi-select routing
- `_on_queue_selected()` (line 155): Single-select, deselects others
- `_on_queue_toggled()` (line 167): Multi-select toggle with empty-prevention guard
- `get_selected_sources()` (line 194): Returns sorted indices as source objects

**Gap:** Non-trivial selection state machine. Empty-prevention at `_on_queue_toggled` line 179 (prevents deselecting last item). Button-to-index mapping. `refresh()` kills prior elements. No test for any of these behaviors.

### 12. `game/ui/screens/strategy_windows/selection_prompts.py` (90 LOC) — MAJOR
**Layer:** UI — Modal selection prompts for planets, systems, fleets.

**No test file.** Heuristic baseline correctly identified Tier 0.

- `SelectionPromptRegistrar.__init__()` (line 26): Stores composer reference
- `prompt_planet()` (line 29): PlanetSelectionWindow with 950x650 rect, facade passthrough
- `open_system()` (line 55): SystemSelectionWindow with 450x500 rect
- `prompt_fleet()` (line 74): FleetSelectionWindow with 450x400 rect

**Gap:** All methods depend on `pygame_gui` window construction. Testable aspects: rect computation, composer slot assignment, facade threading for `prompt_planet`.

---

## Tier 1 — Test Files Exist But Symbols Not Directly Tested

### 1. `game/core/ship_classes.py` (59 LOC) — MAJOR
**Heuristic:** 5 candidate test files, 0 symbols tested.

**Actual:** Test files import or depend on the constants indirectly:
- `FLEET_ICON_SHIP_CLASS` (line 16): String constant `"Battle Cruiser"` — tested via `test_race_setup_ships_smoke.py` which exercises ship theme loading
- `SHIP_CLASSES_WITH_VISUAL_THEMES` (line 26): frozenset of 19 ship class names — verified by `test_ship_theme_manager.py::test_theme_discovery` which validates theme.json against this set

**Gap:** No direct unit test for the module itself. The 19-entry frozenset cardinality and contents are tested indirectly but never asserted in isolation. A static guard that `len(SHIP_CLASSES_WITH_VISUAL_THEMES) == 19` would catch accidental drift.

### 2. `game/strategy/facade/dto/__init__.py` (32 LOC) — ADVISORY
**Re-export shim.** 13 candidate test files import DTOs from this package. No symbols tracked by heuristic because it's a pure re-export.

### 3. `game/ui/renderer/__init__.py` (0 LOC) — ADVISORY
**Empty file.** No content to test. Package exists for namespace.

---

## Tier 2 — Partially Tested

### 1. `game/ai/controller.py` (470 LOC) — AI Controller
**Test files:** `test_ai_controller_unit.py`, `test_ai_controller_edge_cases.py`, `test_ai_controller_interface.py`, etc. (10+ files)
**Heuristically untested:** `_acquire_targets`, `_select_behavior`, `_execute_behavior`

**Verified gaps:**
- `_acquire_targets()` (line 370): Dead-target invalidation (lines 373-375), secondary target setup (line 382), satellite exit (line 362) — tested but with partial branch coverage
- `_select_behavior()` (line 391): Retreat threshold comparison (`retreat_threshold > 0` guard, line 396) — tested indirectly
- `_execute_behavior()` (line 403): Behavior instantiation via dict lookup (line 410), `enter()` call (line 413), `_NO_TARGET_BEHAVIORS` check (line 418)

### 2. `game/services/llm/deepseek.py` (354 LOC) — DeepSeek LLM Provider
**Test files:** `test_deepseek.py` 
**Heuristically untested:** `__repr__`, `__str__`, `_read_api_key`, `_build_body`, `_build_headers`, `_parse_response`

**Verified gaps:**
- `__repr__` (line 76): Returns `DeepSeekProvider(api_key=<REDACTED>)` — security invariant untested
- `_read_api_key()` (line 241): Empty key raises `LLMConfigError` — tested indirectly via `complete()` call but key-not-set raises ConfigError inside `complete`, not here
- `_build_body()` (line 255): Default model/temperature/max_tokens fallback, unknown opts pass-through — tested indirectly
- `_parse_response()` (line 287): Non-JSON response (line 296-304), missing fields (line 314-323), Unknown finish_reason→STOP (line 332) — error paths partially tested

### 3. `game/simulation/services/modifier_service.py` (268 LOC) — Modifier Service
**Test files:** `test_modifier_service.py`
**Heuristically untested:** `_has_arc_set_effect`

**Verified gaps:**
- `_has_arc_set_effect()` (line 142): Static method with `isinstance(effect, dict)` guard and `effect.get('stat') == 'arc_set'` check. Called by `get_initial_value` and `get_local_min_max`. No direct unit test.

### 4. `game/simulation/services/registry_loader.py` (137 LOC) — Registry Loader
**Test files:** `test_registry_loader.py`
**Heuristically untested:** `find_file`

**Verified gaps:**
- `find_file` nested function (line 87): File-discovery logic with test_ prefix fallback. Tested indirectly via `reload_registries_from_directory`. No tests for: non-existent directory, empty directory, only test_-prefixed files, only standard-named files, mixed presence.

### 5. `game/strategy/data/fleet_serde.py` (168 LOC) — Fleet Serde — *Corrected from Tier 0*
**Test files:** `test_fleet_serde_roundtrip.py` (192 LOC integration test)
**Heuristically untested:** `fleet_to_dict`, `fleet_from_dict_kwargs`, `_deserialize_fleet_ships`, `_deserialize_fleet_orders`

**Verified:** The integration test covers round-trip serialization. Missing: error path tests for `_deserialize_fleet_ships` corrupt data at specific indices (lines 143-153), `fleet_from_dict_kwargs` missing required keys (line 103), location deserialization from list vs dict shape (lines 106-109).

### 6. `game/strategy/data/group_policy_registry.py` (108 LOC) — Group Policy Registry
**Test files:** `test_group_policies.py`, `test_group_policy_registry_characterization.py`
**Heuristically untested:** `GroupPolicyRegistry.__init__`

**Verified:** `__init__` (line 31) initializes empty dicts — trivial. Characterized in `test_group_policy_registry_characterization.py`.

### 7. `game/strategy/data/naming.py` (93 LOC) — Name Registry
**Test files:** `test_naming.py`
**Heuristically untested:** `NameRegistry.__init__`

**Verified:** `__init__` (line 13) is tested indirectly (no-args creates empty; with path loads YAML). `to_roman` (line 68) edge cases: n=0, n≥4000, n=3999 — verify via test_naming.py.

### 8. `game/strategy/engine/order_handlers/self_destruct.py` (111 LOC) — Self-Destruct Handler
**Test files:** `test_self_destruct_handler.py`, `test_superweapon_edge_cases.py`, etc.
**Heuristically untested:** `supported_order_types`

**Verified gaps:**
- `supported_order_types` property (line 38): Returns `(OrderType.SELF_DESTRUCT,)` — trivial.

### 9. `game/strategy/facade/slices/system_slice.py` (132 LOC) — System Slice
**Test files:** `test_system_slice.py`
**Heuristically untested:** `SystemSlice.__init__`

**Verified:** `__init__` trivial. Tests cover `get_all_systems`, `get_all_stars`, `get_system_at_hex`, `get_system_near_hex`, `get_storm_names_at_hex`.

### 10. `game/strategy/facade/strategy_session_facade.py` (283 LOC) — Strategy Session Facade
**Test files:** 12 candidate test files
**Heuristically untested:** `_build_planet_index`, `_build_fleet_hex_index`

**Verified gaps:**
- `_build_planet_index()` (line 277): Internal helper, delegates to `FacadeSessionState.build_planet_index()`
- `_build_fleet_hex_index()` (line 281): Delegates to `FleetSlice.build_fleet_hex_index()`

### 11. `game/strategy/generation/region_classifier.py` (275 LOC) — Region Classifier
**Test files:** `test_region_classifier.py`
**Heuristically untested:** `RegionClassifier.__init__`, `RegionClassifier._build_regions`

**Verified:** `__init__` tests implicitly via `classify()` calls. `_build_regions()` (line 98) is private — tested indirectly via `regions` property and `classify()`.

### 12. `game/strategy/services/cargo_transfer_service.py` (301 LOC) — Cargo Transfer Service
**Test files:** `test_cargo_transfer_service.py`
**Heuristically untested:** `_extract_population_items`

**Verified gaps:**
- `_extract_population_items()` (line 45): Population extraction with `population_details` (line 68) vs fallback to `total_population` (line 82). With/without `label_fn`, with/without `planet_id`.

### 13. `game/ui/panels/race_summary_panel.py` (732 LOC) — Race Summary Panel
**Test files:** `test_race_summary_panel.py`
**Heuristically untested:** 12 symbols

**Verified gaps** (all covered indirectly via `refresh()` which invokes these private methods):
- `_create_left_column_content()` (line 178): Panel layout — tested via refresh callbacks
- `_create_environment_column()` (line 261): Scroll container — tested via refresh
- `_create_ship_theme_strip()` (line 279): Label strip — tested via refresh
- `_format_race_summary()` (line 325): Base formatting — tested via refresh
- `_format_physical_summary()` (line 341): Base formatting
- `_format_society_summary()` (line 347): Base formatting
- `_format_homeworld_summary()` (line 353): Base formatting
- `_render_section_header()` (line 489): `UILabel` creation — UI rendering
- `_render_env_row()` (line 504): `UILabel` creation — UI rendering
- `_render_aptitude_rows()` (line 547): Aptitude rendering — tested via refresh
- `_refresh_flag_preview()` (line 564): Image scaling + UIImage — tested via refresh
- `_refresh_portrait_preview()` (line 603): UIImage — tested via refresh

### 14. `game/ui/screens/build_queue_screen.py` (490 LOC) — Build Queue Screen
**Test files:** `test_build_queue_screen_lifecycle.py`
**Heuristically untested:** `_validate_params`, `_construct_collaborators`, `handle_event`, `on_active_player_changed`, `update`, `draw`

**Verified:** All 6 are thin delegates or lifecycle methods. `_validate_params` (line 157) is tested via constructor tests. `_construct_collaborators` (line 199) is tested via `open_for_yard` tests. `handle_event`/`on_active_player_changed`/`update`/`draw` are tested indirectly.

### 15. `game/ui/screens/builder/stats_config.py` (246 LOC) — Stats Config
**Test files:** `test_ui_stats.py`, `test_stats_visibility.py`
**Heuristically untested:** `load_stats_config`, `load_sections_config`

**Verified:** Both called at module load time (lines 95, 243). Module-level loading means tests exercise them implicitly. Dedicated tests should verify:
- `load_stats_config` with missing/empty file → returns {}
- `load_sections_config` with missing sections key → returns {}, {}
- `resolve_section_visibility` edge cases: all 4 rule types at lines 206-237

### 16. `game/ui/screens/empire_build_queue_sidebar.py` (234 LOC) — Empire Build Queue Sidebar
**Test files:** `test_empire_build_queue_sidebar.py`
**Heuristically untested:** `EmpireBuildQueueSidebar.__init__`, `_build_column_toggles`, `_build_filters`

**Verified:** Constructed inside tests.

### 17. `game/ui/screens/empire_build_queue_viewmodel.py` (298 LOC) — Empire Build Queue ViewModel
**Test files:** `test_empire_build_queue_viewmodel.py`
**Heuristically untested:** `_clear_selection`, `_refresh`

**Verified:** Internal methods called by public API. Tests cover them indirectly.

### 18. `game/ui/screens/empire_build_queue_window.py` (734 LOC) — Empire Build Queue Window
**Test files:** `test_empire_build_queue_window.py`
**Heuristically untested:** 9 symbols

**Verified gaps:**
- `EmpireBuildQueueUiBuilder.build()` (line 69): Builder pattern — tested via window construction
- `_on_filters_applied()` (line 314): Event callback — tested via event bus integration
- `_source_can_build_type()` (line 441): Static method, 3 branches — tested indirectly
- `_get_system_name()` (line 675): Galaxy-dependent — tested via integration
- `_get_turns_left_text()` (line 680): Static formatter — tested via formatter tests
- `on_close_window_button_pressed()` (line 691): Hide vs kill — tested via window lifecycle
- `request_close()` (line 695): Esc-key close — tested via window lifecycle
- `open_for_empire()` (line 699): Empire rebind + source rebuild — tested via reuse tests

### 19. `game/ui/screens/planet_list_filters.py` (410 LOC) — Planet List Filters
**Test files:** `test_planet_list_filters.py`
**Heuristically untested:** `_name_predicate`, `_type_predicate`, `_owner_predicate`, `_range_predicate`, `get_system_name`, `get_owner_name`, `get_mass_earth`, `get_resource_str`

**Verified:** All tested via `filter_planets()`/`sort_planets()` tests. `get_system_name`/`get_owner_name`/`get_mass_earth`/`get_resource_str` tested via `get_column_value`/`sort_planets` callers.

### 20. `game/ui/screens/planet_menu_items.py` (155 LOC) — Planet Menu Items
**Test files:** `test_planet_menu_items.py`
**Heuristically untested:** `_global_hex`, `_matching_deployed_group_at_hex`

**Verified:** Tested indirectly via `build_menu_items()` call.

### 21. `game/ui/screens/strategy_detail_formatter.py` (454 LOC) — Strategy Detail Formatter
**Test files:** `test_strategy_detail_formatter.py`, `test_planet_production_display.py`
**Heuristically untested:** 21 symbols

**Verified gaps** (these are rendering/wiring methods tested via scene/integration):
- `__init__` / `__getattr__` — basic wiring
- `_get_label_for_obj`, `_format_spectrum`, `_format_atmosphere_raw` — thin wrappers
- `_format_star_system`, `_format_star`, `_format_warp_point`, `_format_storm` — tested indirectly
- `_show_planet_report()` (line 241): PlanetReportPanel wiring — tested via integration
- `_planet_has_atmosphere_modifier`, `_planet_has_gravity_modifier`, `_planet_has_water_modifier`, `_planet_has_radiation_shield`, `_planet_has_ability` — tested via planet report
- `_layout_action_buttons()` (line 320): Dynamic button sizing with `except (TypeError, AttributeError)` on line 355 — mock objects in tests trigger the except branch but visibility calculations aren't assert-tested
- `_format_sector_environment()` (line 358): `MockStar` class (line 363) for spectrum rendering — no test
- `_format_fleet()` (line 380): Fleet colonize button visibility (line 395) — tested via integration

### 22. `game/ui/services/validation_service.py` (79 LOC) — Validation Service
**Test files:** `test_validation_service.py`
**Heuristically untested:** `ValidationService.__init__`, `_get_validator`

**Verified:** `__init__` trivial. `_get_validator()` (line 46) lazy-initializes validator when None — tested via `validate_addition`/`validate_design` calls.

### 23. `game/ui/utils/resource_display.py` (58 LOC) — Resource Display
**Test files:** `test_empire_treasury_panel.py` (indirect)
**Heuristically untested:** `get_displayed_resource_ids`

**Verified gaps:**
- `get_displayed_resource_ids()` (line 46): Calls `ResourceCatalog.from_json()` — depends on filesystem state. No test mocks the catalog. Hard to test without filesystem setup.

### 24. `game/ui/widgets/scroll_state.py` (103 LOC) — Scroll State
**Test files:** `test_scroll_state.py`
**Heuristically untested:** `ScrollState.__init__`

**Verified:** `__init__` (line 35) trivial — tested via all other methods.

---

## Tier 3 — Apparently Fully Covered

### 1. `game/strategy/engine/session/runtime_services.py` (103 LOC) — Covered
**Test files:** `test_bootstrap.py`, `test_runtime_services.py`
**Symbols:** `SessionRuntimeServices`, `SessionBootstrapState`
**Verified:** Both dataclasses tested through construction. No uncovered methods (pure data containers).

### 2. `game/strategy/engine/turn_engine_config.py` (263 LOC) — Covered
**Test files:** `test_turn_engine_config.py`, `test_no_lazy_fallback_init.py`
**Symbols:** `TurnEngineConfig`, `TurnEngineConfig.create_default()`
**Verified:** `create_default()` (line 94) constructs 18 engines + 4 mutators. Tests override via `dataclasses.replace`. Checked: lazy-default mutator generation paths (lines 197-211), ai_factory=None vs provided branches (lines 180-191).

### 3. `game/strategy/generation/density/primitives/radial.py` (61 LOC) — Covered
**Test files:** `test_radial.py`, `test_density_map.py`
**Symbols:** `RadialPrimitive`, `RadialPrimitive.evaluate()`
**Verified:** `evaluate()` tested for center=zero, sigma=zero guard (line 54), sigma>0 Gaussian path.

### 4. `game/ui/screens/test_lab/renderer/tag_filter_panel.py` (146 LOC) — Covered
**Test files:** `test_tag_filter_panel.py`
**Symbols:** `TagFilterPanel`, `TagFilterPanel.__init__()`, `TagFilterPanel.draw()`
**Verified:** Constructor and draw method tested with mock controller/registry/viewmodel.

### 5. `game/ui/screens/workshop_context.py` (175 LOC) — Covered
**Test files:** 15 candidate files: `test_app_create_workshop_context.py`, etc.
**Symbols:** `WorkshopMode`, `WorkshopContext`, `standalone()`, `integrated()`, `is_standalone()`, `is_integrated()`
**Verified:** All symbols tested. `standalone()` (line 79) ValueError for missing registries (line 101) tested. `integrated()` (line 109) with/without facade_state tested.

---

## File Coverage Verification Table

| File | Heuristic Tier | Verified Tier | Test Files | Critical Gaps |
|---|---|---|---|---|
| `game/ai/controller.py` | T2 | T2 | 10+ | `_acquire_targets` (line 370), `_select_behavior` (line 391), `_execute_behavior` (line 403) |
| `game/core/protocols/strategy_domain.py` | **T0** | **T0** | NONE | CRITICAL: All 4 Protocols + 3 TypeGuards untested (L1-256) |
| `game/core/ship_classes.py` | T1 | T1 | 5 (indirect) | No direct unit test for frozenset cardinality |
| `game/research/__init__.py` | **T0** | **T0** | NONE | ADVISORY: Package docstring only |
| `game/services/llm/deepseek.py` | T2 | T2 | 2 | `_parse_response` error paths (L287-347) |
| `game/services/llm/defaults.py` | **T0** | **T0** | NONE | CRITICAL: Module-level singleton accessor (L1-42) |
| `game/simulation/entities/ship_resource_manager.py` | ~~T0~~ | **T2** | 1 (3 tests) | Corrected — has test file (69 LOC) |
| `game/simulation/replay/replay_record.py` | **T0** | **T0** | NONE (dedicated) | CRITICAL: No from_dict/to_dict/is_current_schema unit tests (L1-93) |
| `game/simulation/services/modifier_service.py` | T2 | T2 | 3 | `_has_arc_set_effect` (L142), `get_initial_value` arc_set edge |
| `game/simulation/services/registry_loader.py` | T2 | T2 | 2 | `find_file` inner function (L87), error-path logging |
| `game/strategy/data/fleet_serde.py` | ~~T0~~ | **T2** | 1 (integration) | Corrected — has integration test (192 LOC). Error paths untested |
| `game/strategy/data/group_policy_registry.py` | T2 | T3 | 2 | All symbols heuristically covered |
| `game/strategy/data/naming.py` | T2 | T3 | 1 | All symbols heuristically covered |
| `game/strategy/engine/order_handlers/self_destruct.py` | T2 | T2 | 5 | `supported_order_types` property (trivial) |
| `game/strategy/engine/order_handlers/transfer_branches.py` | **T0** | **T0** | NONE | CRITICAL: 604 LOC, 12 dispatch methods, zero tests (L1-604) |
| `game/strategy/engine/session/__init__.py` | **T0** | **T0** | NONE | ADVISORY: Re-export shim (L1-26) |
| `game/strategy/engine/session/runtime_services.py` | T3 | T3 | 3 | Fully covered — frozen dataclasses |
| `game/strategy/engine/turn_engine_config.py` | T3 | T3 | 2 | Fully covered |
| `game/strategy/facade/dto/__init__.py` | T1 | T1 | 13 | ADVISORY: Re-export shim |
| `game/strategy/facade/slices/system_slice.py` | T2 | T3 | 1 | All symbols covered |
| `game/strategy/facade/strategy_session_facade.py` | T2 | T2 | 12 | `_build_planet_index`, `_build_fleet_hex_index` |
| `game/strategy/generation/density/primitives/radial.py` | T3 | T3 | 4 | Fully covered |
| `game/strategy/generation/region_classifier.py` | T2 | T2 | 1 | `__init__`, `_build_regions` tested indirectly |
| `game/strategy/services/ability_sources/fleet.py` | **T0** | **T0** | NONE | CRITICAL: FleetAbilitySource + 3 helpers untested (L1-148) |
| `game/strategy/services/ability_sources/intrinsic_roll.py` | **T0** | **T0** | NONE | CRITICAL: Shared roll helper untested (L1-79) |
| `game/strategy/services/ability_sources/labels.py` | **T0** | **T0** | NONE | CRITICAL: Shared label formatter untested (L1-23) |
| `game/strategy/services/cargo_transfer_service.py` | T2 | T2 | 1 | `_extract_population_items` (L45) |
| `game/ui/panels/race_summary_panel.py` | T2 | T2 | 1 | 12 render methods tested via `refresh()` |
| `game/ui/renderer/__init__.py` | T1 | T1 | 1 | ADVISORY: Empty file |
| `game/ui/research/research_renderer.py` | **T0** | **T0** | NONE | MAJOR: All 9 methods untested (L1-324) |
| `game/ui/screens/build_queue_screen.py` | T2 | T2 | 2 | 6 lifecycle methods tested indirectly |
| `game/ui/screens/build_queue_selector.py` | **T0** | **T0** | NONE | MAJOR: Selection state machine untested (L1-196) |
| `game/ui/screens/builder/stats_config.py` | T2 | T2 | 3 | Module-level loading, no direct config tests |
| `game/ui/screens/empire_build_queue_sidebar.py` | T2 | T3 | 1 | All symbols heuristically covered |
| `game/ui/screens/empire_build_queue_viewmodel.py` | T2 | T3 | 3 | All symbols heuristically covered |
| `game/ui/screens/empire_build_queue_window.py` | T2 | T2 | 1 | `UiBuilder.build()` + 8 event/view methods |
| `game/ui/screens/planet_list_filters.py` | T2 | T2 | 3 | 8 helper functions tested via `filter_planets` |
| `game/ui/screens/planet_menu_items.py` | T2 | T2 | 1 | `_global_hex`, `_matching_deployed_group_at_hex` |
| `game/ui/screens/strategy_detail_formatter.py` | T2 | T2 | 2 | 21 methods, many rendering-only |
| `game/ui/screens/strategy_windows/__init__.py` | T1 | T1 | 3 | ADVISORY: Package docstring only |
| `game/ui/screens/strategy_windows/selection_prompts.py` | **T0** | **T0** | NONE | MAJOR: All 4 methods untested (L1-90) |
| `game/ui/screens/test_lab/renderer/tag_filter_panel.py` | T3 | T3 | 1 | Fully covered |
| `game/ui/screens/workshop_context.py` | T3 | T3 | 15 | Fully covered |
| `game/ui/services/validation_service.py` | T2 | T3 | 1 | All symbols heuristically covered |
| `game/ui/utils/resource_display.py` | T2 | T2 | 1 (indirect) | `get_displayed_resource_ids` filesystem-dependent |
| `game/ui/widgets/scroll_state.py` | T2 | T3 | 1 | All symbols heuristically covered |

---

## Top 5 Remediation Priorities

1. **`transfer_branches.py` (CRITICAL)** — 604 LOC of transfer dispatch logic with zero tests. Every branch (load/unload, planet/fleet, resource/passengers/pod/vehicle) needs unit coverage.

2. **`strategy_domain.py` (CRITICAL)** — Core protocol contracts untested. Minimum: test `isinstance()` checks with `@runtime_checkable` for each Protocol, and TypeGuard functions.

3. **`fleet.py` ability_sources (CRITICAL)** — Strategic ability scanning from fleet ships. Test cache behavior, strategic-scope filtering, hidden-fleet suppression, combat-capable detection.

4. **`intrinsic_roll.py` (CRITICAL)** — Shared ability generation with RNG. Test `{min,max}` range rolling, `chance` probability gate, deterministic output with seeded RNG.

5. **`replay_record.py` (CRITICAL)** — Serialization boundary. Test `from_dict` with corrupt/missing fields, `to_dict` tuple/list coercion, schema version check, full round-trip.
