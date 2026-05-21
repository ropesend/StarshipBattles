# Test Coverage Audit — Shard 08 Discovery Report

**Date:** 2026-05-20  
**Shard:** Shard 08 — 44 production files, ~9593 LOC  
**Agent:** OpenCode Discovery Agent (skeptical verification pass)

---

## Summary

| Tier | Count | LOC | Description |
|------|-------|-----|-------------|
| **CRITICAL** (Tier 0) | 11 | ~1832 | Zero unit tests — no dedicated test files |
| **MAJOR** (Tier 1) | 5 | ~662 | Test files reference but no symbols tested |
| **MINOR** (Tier 2) | 17 | ~4595 | Partial coverage with specific untested gaps |
| **ADVISORY** (Tier 3) | 9 | ~1949 | Appears well-covered (heuristic verified) |
| **HEURISTIC CORRECTED** | 2 | ~118 | Heuristic misclassified as Tier 0; both have tests |

**Heuristic corrections:** Two files the heuristic classified as Tier 0 actually have dedicated test files:
- `movement.py` → has `tests/unit/simulation/entities/stat_contributors/test_movement.py` (168 lines, tests all 4 contribute functions)
- `image/defaults.py` → has `tests/unit/ui/services/image/test_defaults.py` (27 lines, tests get/set round-trip)

**Overall assessment:** 36% of shard LOC (Tiers 0+1) has zero or unverified test coverage. Seven Tier 0 files are in the simulation/strategy layers (business logic), making them CRITICAL risks.

---

## Tier 0 — CRITICAL: Zero Unit Tests (11 files, ~1832 LOC)

### 1. `game/simulation/systems/battle_setup.py` (141 LOC)
- **Symbols:** `initialize_start_state`, `start_teams`, `log_initial_status`
- **Layer:** simulation
- **Risk:** CRITICAL — core battle initialization path. `start_teams` orchestrates ship team assignment, AI factory setup, aura manager init, and start-of-battle logging. If this breaks, every battle mode (visual, headless, Combat Lab) fails silently.
- **Key untested paths:**
  - `initialize_start_state`: RNG seeding + DamageCalculator singleton replacement (line 49 — `ShipCombatEngine._damage_calculator = DamageCalculator(rng=engine.rng)`)
  - `start_teams`: N-team AI factory dispatch with `enemy_hint` resolution (lines 97-105)
  - `start_teams`: `ValidationException` raise path when both `ai_controllers` and `_ai_factory` are None (lines 106-111)
  - `log_initial_status`: warning paths for zero-thrust and zero-turn-speed (lines 138-141)
  - Edge case: `team_ships` coercion from single ship to list (line 80)
- **Test file needed:** `tests/unit/simulation/systems/test_battle_setup.py`

### 2. `game/strategy/data/planet_serde.py` (256 LOC)
- **Symbols:** `_normalize_to_typed`, `planet_to_dict`, `planet_from_dict_kwargs`, `_deserialize_planet_orders`
- **Layer:** strategy
- **Risk:** CRITICAL — save/load round-trip integrity. Every Planet in every save game goes through these functions. Corruption here is data-loss.
- **Key untested paths:**
  - `planet_to_dict`: 47-field serialization including `staging_yard` typed-to-dict flattening (lines 86-89)
  - `_normalize_to_typed`: dict/CarriedVehicle/DropPod discrimination (lines 28-53)
  - `planet_from_dict_kwargs`: `PersistenceException` raise paths for missing keys (line 131), invalid `planet_type` enum (line 142), invalid `location` hex (lines 149-161)
  - `_deserialize_planet_orders`: corrupt order at index raising `PersistenceException` (lines 245-255)
  - `planet_from_dict_kwargs`: deserialization of `facilities`, `populations`, `species_configs`, `orders` sub-objects
- **Test file needed:** `tests/unit/strategy/data/test_planet_serde.py`

### 3. `game/strategy/engine/handlers/fms_shared.py` (114 LOC)
- **Symbols:** `check_issuer_invariant`, `count_matching_bay`, `count_matching_yard`, `resolve_requested`
- **Layer:** strategy
- **Risk:** CRITICAL — shared validation for all 5 FMS command handlers (LayMines, LaunchFighters, LaunchSatellites, RecoverFighters, RecoverSatellites). A bug here breaks all FMS operations.
- **Key untested paths:**
  - `check_issuer_invariant`: both-has error (line 34), neither-has error (line 38)
  - `count_matching_bay`: `design_id="auto"` / None matches-any path (line 54), non-matching design_id skip (line 58)
  - `count_matching_yard`: dict-shaped staging yard discrimination via `isinstance(item, dict)` + `VALID_VEHICLE_TYPES` probe (lines 78-83)
  - `resolve_requested`: `count is None` returns `count_available` (line 103), `count <= 0` error (line 105)
- **Test file needed:** `tests/unit/strategy/engine/handlers/test_fms_shared.py`

### 4. `game/strategy/engine/session/graph_restoration.py` (79 LOC)
- **Symbols:** `restore_graph_wiring`
- **Layer:** strategy
- **Risk:** CRITICAL — canonical post-deserialize wiring for BOTH save→load AND snapshot→rollback paths. Called by `SessionPersistenceAdapter.rehydrate_state()` and `TurnStateSnapshot.restore()`. A regression here silently corrupts the entity graph on both paths.
- **Key untested paths:**
  - Step 1: `empire.set_galaxy(galaxy)` back-reference (line 58)
  - Step 2: `galaxy.register_fleet(fleet)` for deserialized fleets (line 63)
  - Step 3: `fleet.resolve_order_references(galaxy, empires)` (line 68)
  - Step 4: pursuer tracker rebuild for `MOVE_TO_FLEET`/`JOIN_FLEET` orders (lines 74-79)
  - Defensive: `hasattr(order.target, "pursuer_tracker")` guard (line 78)
- **Test file needed:** `tests/unit/strategy/engine/session/test_graph_restoration.py`

### 5. `game/strategy/engine/superweapon_handlers/create_dyson_sphere.py` (124 LOC)
- **Symbols:** `process_create_dyson_sphere`, `_precheck`, `_effect`
- **Layer:** strategy
- **Risk:** CRITICAL — Dyson Sphere construction is a superweapon that deletes stars+planets and creates a new planet. Untested destruction logic could leave dangling references.
- **Key untested paths:**
  - `_precheck`: fleet not at star system (line 42), system has no stars (line 46)
  - `_effect`: planets within dyson_radius=5 removed (line 59-62), colony removal via `IEmpireMutator` (line 63-69), galaxy planet unregistration (line 69)
  - `_effect`: star list cleared (line 71)
  - `_effect`: race-based environmental prefs applied (lines 74-89), fallback defaults (lines 85-89)
  - `_effect`: Dyson Planet construction with 14+ parameters (lines 91-109)
  - `process_create_dyson_sphere`: dispatches via `processor.execute_superweapon(...)` with `precheck_fn` (line 122)
- **Test file needed:** `tests/unit/strategy/engine/superweapon_handlers/test_create_dyson_sphere.py`

### 6. `game/strategy/facade/slices/event_slice.py` (96 LOC)
- **Symbols:** `EventSlice.__init__`, `get_human_player_ids`, `get_turn_number`, `get_save_path`, `get_turn_events`, `get_all_events`, `get_events_by_category`
- **Layer:** strategy
- **Risk:** CRITICAL — event log facade slice. The event log is the primary UI feedback channel for turn processing. Other facade slices (`planet_slice`, `system_slice`, `empire_slice`) all have test files; this one does not.
- **Key untested paths:**
  - All methods trivially delegate to `self._state.session` — but the `empire_id=None` vs scoped paths in `get_turn_events`, `get_all_events`, `get_events_by_category` (BUG-123 scoping) have zero coverage
  - `get_turn_events(turn=None)` resolves to current turn_number (line 57)
  - `get_all_events` with empire_id scoping (line 77)
  - `get_events_by_category` with empire_id scoping (line 95)
- **Test file needed:** `tests/unit/strategy/facade/slices/test_event_slice.py`

### 7. `game/strategy/services/fleet_path_projection.py` (201 LOC)
- **Symbols:** `project_path_inner`, `consume_ticks`, `get_action_time_for_projection`, `project_action_order`, `resolve_path_for_order`
- **Layer:** strategy
- **Risk:** CRITICAL — multi-turn fleet path projection drives the strategy renderer's movement preview. Untested simulation loop with safety limits and edge cases.
- **Key untested paths:**
  - `project_path_inner`: `moves_per_turn <= 0` early-return (line 51), `max_steps` safety limit (line 66-68), `initial_progress` pre-adjustment (line 58)
  - `project_path_inner`: action order tick consumption loop (lines 76-83), warp movement detection via `hex_distance > 1` (line 100)
  - `consume_ticks`: multi-turn tick consumption with wraps (lines 129-138)
  - `project_action_order`: `action_time` capped to >= 0 after subtracting `initial_progress` (line 163), `initial_progress=0` after first action (line 168)
  - `resolve_path_for_order`: WARP order special-casing (line 193-194), empty-path return None (line 198)
- **Test file needed:** `tests/unit/strategy/services/test_fleet_path_projection.py`

### 8. `game/ui/screens/galaxy_test/galaxy_mode.py` (427 LOC)
- **Symbols:** `GalaxyModeHelper.__init__`, `create_ui`, `generate`, `_center_camera`, `update_slider_displays`, `draw`, `_draw_warp_lanes`
- **Layer:** ui
- **Risk:** CRITICAL — dev tooling for galaxy generation testing. Not production-critical but represents 427 LOC of unvalidated galaxy layout testing infrastructure.
- **Key untested paths:**
  - `generate`: seed parsing from text input with `ValueError` fallback to `hash(seed_text) % (2**31)` (lines 230-233)
  - `generate`: density-based vs random placement strategy dispatch (lines 264-271)
  - `generate`: `load_and_scale` + `DensityMap.from_config` flow (lines 268-271)
  - `_center_camera`: bounding box computation + zoom clamping (lines 318-344)
  - `_draw_warp_lanes`: drawn-pairs dedup (lines 394-408), viewport culling with margin (lines 418-422)
- **Test file needed:** `tests/unit/ui/screens/galaxy_test/test_galaxy_mode.py`

### 9. `game/ui/screens/list_filter_utils.py` (43 LOC)
- **Symbols:** `make_attr_sort_key`, `_key`
- **Layer:** ui
- **Risk:** CRITICAL — shared sort-key factory used by `sort_planets` and `sort_stars`. A bug here breaks sort in both planet_list_filters and star_list_filters.
- **Key untested paths:**
  - `"func"` in col path (line 31)
  - `"attr"` in col with dotted-path resolution (lines 33-40)
  - Missing attribute → `""` fallback (line 40)
  - Neither func nor attr → `""` fallback (line 42)
- **Test file needed:** `tests/unit/ui/screens/test_list_filter_utils.py`

### 10. `game/ui/screens/strategy_render/systems.py` (307 LOC)
- **Symbols:** `draw_systems`, `load_star_image`, `draw_colony_marker`, `draw_star`, `draw_system_details`
- **Layer:** ui
- **Risk:** CRITICAL — the heart of strategy render layer. Draws stars, planets (with multi-planet hex grouping), colony markers, warp points, and Dyson Spheres. No test file exists.
- **Key untested paths:**
  - `draw_systems`: viewport culling with camera transform (lines 30-41)
  - `load_star_image`: 1024px resolution star image loading with missing-texture guard (line 76)
  - `draw_colony_marker`: low-zoom (< 0.5) colony ownership indicator (lines 93-110), empire color lookup (line 101)
  - `draw_star`: core-metadata-based image scaling (lines 137-149), `radius_boost` progressive scaling (line 145), off-center core offset (lines 155-158)
  - `draw_system_details`: multi-planet hex grouping with expansion animation (lines 184-280), per-count smaller-angle tables (lines 222-234), `_temp_screen_pos`/`_temp_draw_r` code smell (lines 258-259)
  - `draw_system_details`: Dyson Sphere separation from normal planets (line 187)
  - `draw_system_details`: warp point rotation animation + `BLEND_ADD` rendering (lines 281-307)
- **Test file needed:** `tests/unit/ui/screens/strategy_render/test_systems.py`

### 11. `game/ui/screens/workshop_viewmodel_selection.py` (140 LOC)
- **Symbols:** `normalize_selection`, `apply_append_selection`, `sync_modifiers_to_selection`
- **Layer:** ui
- **Risk:** CRITICAL — pure algorithm module for WorkshopViewModel multi-select. These functions implement the core selection logic (normalize, append/toggle, modifier-sync) for the ship design workshop. Bugs here cause silent selection corruption.
- **Key untested paths:**
  - `normalize_selection`: tuple pass-through (line 44), component-in-layer lookup with `ValueError` catch (lines 48-55), template/dragged component fallback `(None, -1, comp)` (line 58)
  - `apply_append_selection`: empty current → incoming (line 88), empty incoming → current (line 91), homogeneity mismatch → replacement (line 98), toggle-off with object-identity-based removal (lines 107-111)
  - `apply_append_selection`: duplicate-in-incoming guard via `toggled_off` set (line 113)
  - `sync_modifiers_to_selection`: skip primary_component (line 138)
- **Test file needed:** `tests/unit/ui/screens/test_workshop_viewmodel_selection.py`

---

## Tier 1 — MAJOR: Test Files Reference But Symbols Untested (5 files, ~662 LOC)

### 12. `game/strategy/services/ability_sources/__init__.py` (42 LOC)
- **Layer:** strategy
- **Coverage:** Re-export shim module (Pattern #36). 10 candidate test files reference ability source adapters but none test the `__init__.py` re-exports directly.
- **Risk:** minor — pure re-exports. The underlying adapter modules (`facility.py`, `storm.py`, etc.) have their own tests.

### 13. `game/ui/panels/__init__.py` (0 LOC)
- **Layer:** ui
- **Coverage:** Empty file. 12 candidate test files but nothing to test here.
- **Risk:** none — empty package marker.

### 14. `game/ui/panels/battle_panels.py` (564 LOC)
- **Symbols (35 total):** `BattlePanel`, `ExpandableIdPanel`, `ShipStatsPanel`, `SeekerMonitorPanel`, `BattleControlPanel` — all classes and methods
- **Layer:** ui
- **Coverage:** The heuristic found zero tested symbols. Verified: no dedicated test file exists. The only reference is `tests/unit/ui/conftest.py` which may import the module for fixtures but exercises no functionality.
- **Key untested paths:**
  - `ShipStatsPanel.draw`: surface caching (lines 115-118), team-alive counting (lines 139-140, 151-152), banner-rect recording for click detection (line 189)
  - `ShipStatsPanel.handle_click`: shift+click→focus_ship return (line 257), banner-rect collision with scroll offset (lines 250-261)
  - `SeekerMonitorPanel.draw`: seeker active count + clear-inactive button (lines 319-348)
  - `SeekerMonitorPanel.handle_click`: clear-inactive collision (line 449), X-button removal (lines 463-466)
  - `BattleControlPanel.draw`: battle-over overlay with winner display (lines 496-528), ongoing end-battle button (lines 535-556)
  - `BattleControlPanel.handle_click`: button rect collision returns `"end_battle"` string (lines 559-563)
  - `_get_ships`: MagicMock guard with `isinstance(ships, list)` check (line 62)
- **Risk:** MAJOR — 564 LOC of battle UI with zero test coverage.
- **Test file needed:** `tests/unit/ui/panels/test_battle_panels.py`

### 15. `game/ui/screens/race_setup/__init__.py` (27 LOC)
- **Layer:** ui
- **Coverage:** Single re-export of `RaceSetupScreen`. 2 candidate test files reference race_setup modules but neither tests this shim.
- **Risk:** low — pure re-export shim.

### 16. `game/ui/services/__init__.py` (29 LOC)
- **Layer:** ui
- **Coverage:** Re-exports 8 service classes. 2 candidate test files reference ui/services but neither tests the re-export surface.
- **Risk:** low — pure re-export shim.

---

## Tier 2 — MINOR: Partial Coverage With Specific Gaps (17 files, ~4595 LOC)

### 17. `game/simulation/battle_controller.py` (831 LOC)
- **Layer:** simulation
- **Coverage:** 6 dedicated test files exist with good coverage. Heuristically 25/31 symbols tested.
- **Verified untested symbols (verified as actual gaps):**
  - `BattleController.__init__` (lines 55-99) — partially tested via `configure`/`start_from_spec` flows but never directly instantiated in tests with all optional params
  - `BattleController._retreat_allowed` (lines 576-585) — config-driven boolean; tested indirectly through `update()` flow but never in isolation with `config=None`
  - `BattleController._reinforcements_allowed` (lines 587-589) — same as retreat_allowed
  - `BattleController.get_tick_count` (lines 740-743) — no test with `engine is None` (returns 0)
  - `BattleController.set_on_ship_escaped` (lines 816-818) — trivial setter, not tested
  - `BattleController.reset` (lines 822-831) — calls `_retreat_manager.reset()` which is None-safe via the `if` guard; tested indirectly through full lifecycle tests
  - `BattleController.get_results` (lines 761-807) — `escaped_ids` lookup (line 788), no test with escaped ships
  - `BattleController._update_retreats` (lines 557-574) — `get_ship_by_id` inner function not exercised directly
- **Additional gap:** `load_state` (lines 612-697) has zero production callers (docstring admits this) but appears in test files. Covered but dead code.

### 18. `game/simulation/components/abilities/container.py` (216 LOC)
- **Layer:** simulation
- **Coverage:** 1 test file. Heuristically 5/8 symbols tested.
- **Verified untested:**
  - `ContainerAbility._parse_attrs` (lines 77-108) — dict validation, kind-name parsing, `allowed_type_ids` → frozenset conversion. Core construction path.
  - `ContainerAbility.recalculate` (lines 110-113) — `bay_capacity_mult` application via `get_effective_stat`
  - `ContainerAbility.get_ui_rows` (lines 118-128) — UI formatting with `kinds_str` join and type filter string
- **Coverage note:** The three parity helpers (`container_view_from_*`) at lines 137-208 are tested.

### 19. `game/simulation/entities/stat_contributors/registry.py` (570 LOC)
- **Layer:** simulation
- **Coverage:** 3 dedicated test files. Heuristically 15/28 symbols tested.
- **Verified as actually tested (heuristic misclassified):**
  - `CrewPriorityEntry` — tested indirectly via registry fixtures
  - `_StatContributorRegistry.__init__` — tested via module-level instance
  - `_StatContributorRegistry.add_default`, `add_replacement`, `add_appended`, `remove_handle` — tested in `test_registry.py` and `test_registry_pipeline.py`
  - `_StatContributorRegistry.get`, `__contains__`, `__len__` — tested
  - `_next_entry_id` — internal counter, tested via registration flow
  - `_seed_builtin_contributors` — exercised at import time and reset in conftest
- **Actual gaps:**
  - `_StatContributorRegistry.get_active_entry` (line 269) — no direct test
  - `_StatContributorRegistry.clear` (line 263) — no direct test
  - `_StatContributorRegistry.iter_for` (line 298+) — tested indirectly via ship stat calculation
  - `RegistrationConflictError`, `CannotUnregisterDefaultError` — tested via REPLACE/APPEND test paths
- **Verdict:** Registry is well-tested. Heuristic undercount was due to indirect module-level access patterns.

### 20. `game/strategy/engine/harvesting_engine.py` (585 LOC)
- **Layer:** strategy
- **Coverage:** 8 dedicated test files. Heuristically 10/27 symbols tested.
- **Verified untested:**
  - `_get_ability_info` (lines 46-76) — generic ability extractor with dict/list/str discrimination. Tested indirectly through `get_harvester_info`/`_get_storage_info` wrappers.
  - `_get_ability_data_from_registry` (lines 79-99) — registry lookup with `isinstance(data, (dict, list))` guard
  - `get_harvester_from_registry` (lines 110-115) — thin wrapper, no direct test
  - `HarvestingEngine._get_planet_mutator` (lines 196-203) — lazy-default path
  - `HarvestingEngine._get_empire_mutator` (lines 205-212) — lazy-default path
  - `HarvestingEngine._refresh_storage_if_needed` (lines 270-299) — cache hit/miss logic, defensive `id(empire)` fallback for MagicMock empires (line 287)
  - `HarvestingEngine._aggregate_empire_storage` (lines 317-337) — PROJ-370 mutator routing
  - `HarvestingEngine._collect_staging_capacity` (lines 339-350)
  - `HarvestingEngine._get_staging_info` (lines 352-357)
  - `HarvestingEngine._collect_storage_from_facility` (lines 359-379)
  - `HarvestingEngine._get_storage_info` (lines 381-386)
  - `HarvestingEngine._get_storage_from_registry` (lines 388-393)
  - `HarvestingEngine._process_empire` (lines 395-403)
  - `HarvestingEngine._process_colony` (lines 405-416)
  - `HarvestingEngine._process_facility` (lines 418-446)
- **Note:** Many of these are tested indirectly through `process_harvesting_tick` and `recalculate_storage` integration tests. The cache-related methods (`_refresh_storage_if_needed`, `_invalidate_booster_cache_for_empire`) have dedicated test files (`test_harvesting_engine_caches.py`).

### 21. `game/strategy/engine/order_handlers/base.py` (220 LOC)
- **Layer:** strategy
- **Coverage:** 2 test files. Heuristically 10/16 symbols tested.
- **Verified untested:**
  - `IOrderHandler.execute_action_order` (line 73) — Protocol signature, tested via concrete implementations
  - `BaseOrderHandler.__init__` (lines 132-141) — tested indirectly through subclass construction
  - `BaseOrderHandler._get_planet_mutator` (lines 143-150) — lazy-default path
  - `BaseOrderHandler._get_ship_mutator` (lines 152-159) — lazy-default path
  - `OrderHandlerRegistry.__init__` (line 196) — verified: tested in `test_base.py` `test_register_and_lookup`
  - `OrderHandlerRegistry.__contains__` (line 215) — not directly tested; `in` operator usage not verified
- **Note:** These are minor gaps. The registry and handler infrastructure are well-tested through concrete subclass tests.

### 22. `game/strategy/engine/quality_engine.py` (83 LOC)
- **Layer:** strategy
- **Coverage:** 3 test files. Heuristically 3/5 symbols tested.
- **Verified untested:**
  - `QualityEngine.__init__` (line 27) — trivial, tested via construction in test files
  - `QualityEngine._process_colony` (lines 54-83) — main processing loop; tested indirectly through `process_quality_improvement`
- **Note:** These are covered through integration. The heuristic classified `__init__` as untested but it's exercised in every test that constructs the engine.

### 23. `game/strategy/services/replay_ship_builder.py` (87 LOC)
- **Layer:** strategy
- **Coverage:** 1 test file. Heuristically 1/2 symbols tested.
- **Verified:**
  - `build_replay_ship_builder` (lines 36-84) — tested in `test_replay_ship_builder_registry_contract.py`
  - `_builder` (inner closure, lines 71-82) — closure returned by `build_replay_ship_builder`, tested indirectly
- **Verdict:** Adequately covered. The inner closure isn't a public symbol.

### 24. `game/ui/components/table/header.py` (146 LOC)
- **Layer:** ui
- **Coverage:** 1 test file. Heuristically 4/5 symbols tested.
- **Verified untested:**
  - `TableHeader.__init__` (lines 30-51) — tested via `test_header.py` construction
- **Verdict:** `__init__` is tested through test construction. Heuristic false positive.

### 25. `game/ui/filters/filter_state_manager.py` (54 LOC)
- **Layer:** ui
- **Coverage:** 2 test files. Heuristically 7/8 symbols tested.
- **Verified untested:**
  - `FilterStateManager.__init__` (line 16) — tested through test construction
- **Verdict:** Heuristic false positive. Well-covered module.

### 26. `game/ui/screens/battle_results_data.py` (181 LOC)
- **Layer:** ui
- **Coverage:** 2 test files. Heuristically 5/7 symbols tested.
- **Verified untested:**
  - `_build_team_summary` (lines 148-165) — pure function, tested indirectly through `extract_battle_results`
  - `_derive_winner` (lines 168-181) — tested indirectly; winner derivation with multiple survivors returning -1 (line 181)
- **Additional gap:** `ShipStatus.DERELICT` branch in `is_alive` check (line 109-110) — verify if any test includes derelict ships
- **Verdict:** `_build_team_summary` and `_derive_winner` are tested as private helpers through the public `extract_battle_results`. Heuristic false positive.

### 27. `game/ui/screens/builder/schematic_view.py` (189 LOC)
- **Layer:** ui
- **Coverage:** 2 test files. Heuristically 4/10 symbols tested.
- **Verified untested:**
  - `SchematicView.__init__` (lines 28-38) — requires `sprite_manager`, `theme_manager`, `vehicle_class_service`; tested via construction in test files
  - `SchematicView.update_rect` (lines 40-47) — cache invalidation + center update
  - `SchematicView.draw` (lines 60-119) — complex rendering with `calculate_ship_image_scale`, layer ring drawing, arc dispatch
  - `SchematicView.draw_all_firing_arcs` (lines 121-125) — weapon component iteration
  - `SchematicView.draw_component_firing_arc` (lines 127-129) — single component arc
  - `SchematicView.draw_weapon_arc` (lines 186-189) — cached arc surface blit
- **Key rendering paths untested:**
  - `draw`: theme image with `calculate_ship_image_scale` (lines 83-94), layer ring drawing with sorted layers (lines 98-109)
  - `_get_cached_arc`: beam vs projectile color dispatch (lines 154-157), label rendering (line 177)
- **Verdict:** `__init__` and `update_rect` are tested. The draw methods are untested (graphics-heavy but the arc cache logic is algorithmic).

### 28. `game/ui/screens/builder/stat_getters.py` (461 LOC)
- **Layer:** ui
- **Coverage:** 1 test file (`test_stat_getters.py`, 167 lines). Heuristically 17/49 symbols tested.
- **Verified untested:**
  - `fmt_time`, `fmt_multiply`, `fmt_decimal`, `fmt_score`, `fmt_targeting` (lines 12-33) — all formatters, no direct unit tests
  - `get_total_crew_requirement` (lines 38-47) — tested via ship stat flow
  - `mass_validator`, `crew_validator`, `life_support_validator` (lines 52-65) — validators, tested indirectly
  - `get_mass_display`, `get_crew_capacity`, `get_life_support`, `get_max_targets`, `get_armor_hp`, `get_maneuver_points` (lines 70-89) — basic getters, some tested
  - `get_strategic_speed` (lines 91-101) — algorithmic: `MIN_HEXES`/`MAX_HEXES` clamping, mass <= 0 guard
  - `get_fuel_per_hex` (lines 244-254) — `ResourceConsumption` instance check + `strategic_per_hex` trigger filter
  - `get_hex_range` (lines 256-262) — `float('inf')` return for zero cost with fuel capacity
  - `get_warp_jumps` (lines 231-242) — multi-resource min-jump calculation
  - `get_colony_types` (lines 279-287) — `ColonizePlanet` ability scan
  - `get_superweapon_summary`, `has_superweapons` (lines 340-360) — tested in test_stat_getters
- **Note:** The 167-line test file covers weapon, strategic movement, cargo, and superweapon getters. Many formatters and validators remain untested. `GETTERS`, `FORMATTERS`, `VALIDATORS`, `UNITS` registry dicts (lines 396-461) are tested implicitly through lookup.

### 29. `game/ui/screens/fleet_report_window.py` (565 LOC)
- **Layer:** ui
- **Coverage:** 2 dedicated test files. Heuristically 8/23 symbols tested.
- **Verified untested:**
  - `FleetReportLayoutBuilder` (lines 38-115) — production layout builder, tested via `MockFleetReportUiBuilder` in test fixtures
  - `FleetReportLayoutBuilder.build` (line 49) — same
  - `FleetReportWindow.__init__` (lines 141-224) — two-stage construction, tested via bypass
  - `FleetReportWindow._swap_columns` (lines 226-233) — column reordering, not directly tested
  - `FleetReportWindow.process_event` (lines 248-267) — event routing, tested indirectly
  - `FleetReportWindow._handle_row_click` (lines 269-289) — Ctrl+click multi-select, tested
  - `FleetReportWindow.select_ship` (lines 292-308) — API, not directly tested
  - `FleetReportWindow._on_remove_ship` (lines 314-327) — split fleet callback
  - `FleetReportWindow._post_removal_refresh` (lines 356-363) — UI refresh after removal
  - `FleetReportWindow._toggle_filter` (lines 394-409) — tested
  - `FleetReportWindow._apply_tri_state_filter` (lines 411-421) — tested
  - `FleetReportWindow._toggle_column` (lines 423-434) — tested
  - `FleetReportWindow.on_close_window_button_pressed` (line 440) — hide-on-close, Issue #28 reuse
  - `FleetReportWindow.request_close` (line 444) — hide-on-close
  - `FleetReportWindow.open_for_fleet` (lines 448-463) — fleet rebind flow with per-player state preservation
- **Issue #28 path:** `capture_view_state` (lines 465-488) and `apply_view_state` (lines 490-551) — per-player view-state snapshot/restore. These are algorithmic and should be unit-testable with mock `column_manager` and `view_model`.

### 30. `game/ui/screens/new_game_setup_controller.py` (360 LOC)
- **Layer:** ui
- **Coverage:** 3 test files. Heuristically 12/15 symbols tested.
- **Verified untested:**
  - `_collect_empire_names` (lines 199-208) — tested indirectly through `on_start_clicked`
  - `_centered_modal_rect` (lines 210-215) — tested indirectly through race modal callbacks
  - `_screen_centered_rect` (lines 217-227) — same
- **Verdict:** Heuristic false positives. All symbols are tested through public API (`on_start_clicked`, `on_load_race_clicked`, etc.).

### 31. `game/ui/screens/race_setup/llm_dialog_service.py` (154 LOC)
- **Layer:** ui
- **Coverage:** 2 test files. Heuristically 3/5 symbols tested.
- **Verified untested:**
  - `LLMDialogService.check_dialog_thresholds` (lines 49-94) — 30s/90s threshold logic, per-field state tracking, bio-first tie-breaking. Not directly tested.
  - `LLMDialogService.check_error_popups` (lines 100-134) — per-error-type popup dispatching with seen-flag guard, bio-first ordering. Not directly tested.
  - `LLMDialogService.error_message` (lines 136-154) — static method mapping exception types to user messages. Testable without pygame.
- **Risk:** These are pure-policy (no pygame dependency). `error_message` is trivially testable. The threshold methods require mock view_model/renderer.

### 32. `game/ui/screens/test_lab/data_extractor.py` (227 LOC)
- **Layer:** ui
- **Coverage:** 1 test file. Heuristically 3/7 symbols tested.
- **Verified untested:**
  - `TestLabDataExtractor.extract_ships` (lines 55-166) — complex condition-parsing with .json filename extraction, multi-ship test handling (PROP-002), scenario class attribute fallback. Partially covered.
  - `TestLabDataExtractor._extract_component_ids` (lines 168-185) — layer-based component ID extraction
  - `TestLabDataExtractor.load_component` (lines 187-213) — lazy cache loading with `load_json` default fallback
  - `TestLabDataExtractor.get_components_cache` (lines 215-227) — cache population trigger
- **Note:** `get_test_data_dir` (lines 21-35) is tested via `test_data_paths.py`.

### 33. `game/ui/widgets/scrollable_json_panel.py` (412 LOC)
- **Layer:** ui
- **Coverage:** 1 test file. Heuristically 10/15 symbols tested.
- **Verified untested:**
  - `ScrollableJsonPanel._add_key_value_line_with_diff` (lines 218-230) — mixed-color tuple line construction
  - `ScrollableJsonPanel._add_value_line_with_diff` (lines 232-241) — value-only line with diff
  - `ScrollableJsonPanel._get_scrollbar_thumb_rect` (lines 306-321) — scrollbar geometry with `scroll_ratio`
  - `ScrollableJsonPanel.draw` (lines 336-396) — complete rendering with clipping, mixed-color line rendering, diff highlighting
  - `ScrollableJsonPanel._draw_scrollbar` (lines 398-412) — scrollbar track+thumb rendering
- **Key algorithmic methods tested:** `set_json_with_diff`, `_format_json_with_diff`, `_get_diff_colors`, `_path_has_changes`, `handle_event`
- **Verdict:** The core algorithmic methods are well-tested. The draw methods are pure rendering.

---

## Tier 3 — ADVISORY: Appears Well-Covered (9 files, ~1949 LOC)

All Tier 3 files were skeletally verified against their heuristic data. No corrections needed — the heuristic correctly identified them as covered.

| # | File | LOC | Test File(s) | Verification |
|---|------|-----|-------------|--------------|
| 34 | `game/ai/interfaces/controllable.py` | 393 | 9 test files | Confirmed: IControllable ABC tested via mock and real Ship implementations |
| 35 | `game/ai/spatial_behaviors/base.py` | 95 | 2 test files | Confirmed: SpatialBehavior ABC tested via `test_spatial_behaviors.py` |
| 36 | `game/ai/spatial_behaviors/free_maneuver.py` | 25 | 1 test file | Confirmed: trivial `return None` behavior tested |
| 37 | `game/strategy/facade/dto/empire_dto.py` | 120 | `test_empire_dto.py` | Confirmed: DTO construction and field access tested |
| 38 | `game/strategy/services/fleet_speed_calculator.py` | 188 | `test_fleet_speed_calculator.py` | Confirmed |
| 39 | `game/strategy/systems/race_randomizer.py` | 446 | 2 test files | Confirmed |
| 40 | `game/ui/components/table/selection.py` | 138 | 2 test files | Confirmed: MultiSelect tested via `test_selection.py`, `test_virtual_table.py` |
| 41 | `game/ui/screens/strategy_render/context.py` | 34 | `test_context.py` | Confirmed: single dataclass tested |
| 42 | `game/ui/utils/portraits.py` | 105 | `test_portraits.py` | Confirmed |

---

## File Coverage Verification Table

| # | File | LOC | Tier | Heuristic Testable | Verified Coverage | Severity |
|---|------|-----|------|---------------------|-------------------|----------|
| 1 | `ai/interfaces/controllable.py` | 393 | 3 | 66/66 | Well-covered | ADVISORY |
| 2 | `ai/spatial_behaviors/base.py` | 95 | 3 | 3/3 | Well-covered | ADVISORY |
| 3 | `ai/spatial_behaviors/free_maneuver.py` | 25 | 3 | 2/2 | Well-covered | ADVISORY |
| 4 | `simulation/battle_controller.py` | 831 | 2 | 25/31 | Gap: retreat_allowed, reinforcements_allowed, get_tick_count, set_on_ship_escaped, reset | MINOR |
| 5 | `simulation/components/abilities/container.py` | 216 | 2 | 5/8 | Gap: _parse_attrs, recalculate, get_ui_rows | MINOR |
| 6 | `simulation/entities/stat_contributors/movement.py` | 73 | **2** | 0/4→**4/4** | **CORRECTED** — has test file, all functions tested | MINOR |
| 7 | `simulation/entities/stat_contributors/registry.py` | 570 | 2 | 15/28 | Mostly covered; get_active_entry, clear untested | MINOR |
| 8 | `simulation/systems/battle_setup.py` | 141 | 0 | 0/3 | ZERO TESTS | **CRITICAL** |
| 9 | `strategy/data/planet_serde.py` | 256 | 0 | 0/4 | ZERO TESTS | **CRITICAL** |
| 10 | `strategy/engine/handlers/fms_shared.py` | 114 | 0 | 0/4 | ZERO TESTS | **CRITICAL** |
| 11 | `strategy/engine/harvesting_engine.py` | 585 | 2 | 10/27 | Partial: cache methods tested; many wrappers untested directly | MINOR |
| 12 | `strategy/engine/order_handlers/base.py` | 220 | 2 | 10/16 | Mostly covered; lazy-default mutators untested directly | MINOR |
| 13 | `strategy/engine/quality_engine.py` | 83 | 2 | 3/5 | Covered through integration | MINOR |
| 14 | `strategy/engine/session/graph_restoration.py` | 79 | 0 | 0/1 | ZERO TESTS | **CRITICAL** |
| 15 | `strategy/engine/superweapon_handlers/create_dyson_sphere.py` | 124 | 0 | 0/3 | ZERO TESTS | **CRITICAL** |
| 16 | `strategy/facade/dto/empire_dto.py` | 120 | 3 | 6/6 | Well-covered | ADVISORY |
| 17 | `strategy/facade/slices/event_slice.py` | 96 | 0 | 0/8 | ZERO TESTS | **CRITICAL** |
| 18 | `strategy/services/ability_sources/__init__.py` | 42 | 1 | 0/0 | Re-export shim | MAJOR |
| 19 | `strategy/services/fleet_path_projection.py` | 201 | 0 | 0/5 | ZERO TESTS | **CRITICAL** |
| 20 | `strategy/services/fleet_speed_calculator.py` | 188 | 3 | 6/6 | Well-covered | ADVISORY |
| 21 | `strategy/services/replay_ship_builder.py` | 87 | 2 | 1/2 | Covered (inner closure not public) | MINOR |
| 22 | `strategy/systems/race_randomizer.py` | 446 | 3 | 12/12 | Well-covered | ADVISORY |
| 23 | `ui/components/table/header.py` | 146 | 2 | 4/5 | Covered | MINOR |
| 24 | `ui/components/table/selection.py` | 138 | 3 | 22/22 | Well-covered | ADVISORY |
| 25 | `ui/filters/filter_state_manager.py` | 54 | 2 | 7/8 | Covered | MINOR |
| 26 | `ui/panels/__init__.py` | 0 | 1 | 0/0 | Empty file | MAJOR |
| 27 | `ui/panels/battle_panels.py` | 564 | 1 | 0/35 | ZERO TESTS | **MAJOR** |
| 28 | `ui/screens/battle_results_data.py` | 181 | 2 | 5/7 | Covered through public API | MINOR |
| 29 | `ui/screens/builder/schematic_view.py` | 189 | 2 | 4/10 | Gap: draw methods; arc cache logic partially covered | MINOR |
| 30 | `ui/screens/builder/stat_getters.py` | 461 | 2 | 17/49 | Core getters tested; many formatters/validators untested | MINOR |
| 31 | `ui/screens/fleet_report_window.py` | 565 | 2 | 8/23 | Core path tested; Issue #28 restore path untested directly | MINOR |
| 32 | `ui/screens/galaxy_test/galaxy_mode.py` | 427 | 0 | 0/8 | ZERO TESTS | **CRITICAL** |
| 33 | `ui/screens/list_filter_utils.py` | 43 | 0 | 0/2 | ZERO TESTS | **CRITICAL** |
| 34 | `ui/screens/new_game_setup_controller.py` | 360 | 2 | 12/15 | Covered | MINOR |
| 35 | `ui/screens/race_setup/__init__.py` | 27 | 1 | 0/0 | Re-export shim | MAJOR |
| 36 | `ui/screens/race_setup/llm_dialog_service.py` | 154 | 2 | 3/5 | Gap: threshold checks + error popup orchestration | MINOR |
| 37 | `ui/screens/strategy_render/context.py` | 34 | 3 | 1/1 | Well-covered | ADVISORY |
| 38 | `ui/screens/strategy_render/systems.py` | 307 | 0 | 0/5 | ZERO TESTS | **CRITICAL** |
| 39 | `ui/screens/test_lab/data_extractor.py` | 227 | 2 | 3/7 | Partial: extract_ships complex condition parsing | MINOR |
| 40 | `ui/screens/workshop_viewmodel_selection.py` | 140 | 0 | 0/3 | ZERO TESTS | **CRITICAL** |
| 41 | `ui/services/__init__.py` | 29 | 1 | 0/0 | Re-export shim | MAJOR |
| 42 | `ui/services/image/defaults.py` | 45 | **2** | 0/2→**2/2** | **CORRECTED** — has test file | MINOR |
| 43 | `ui/utils/portraits.py` | 105 | 3 | 2/2 | Well-covered | ADVISORY |
| 44 | `ui/widgets/scrollable_json_panel.py` | 412 | 2 | 10/15 | Core tested; draw methods untested | MINOR |

---

## Heuristic Corrections

Two files the Phase 1 deterministic scanner misclassified as Tier 0:

| File | Heuristic | Corrected | Evidence |
|------|-----------|-----------|----------|
| `simulation/entities/stat_contributors/movement.py` | Tier 0 (0/4) | **Tier 2** (covered) | `tests/unit/simulation/entities/stat_contributors/test_movement.py` — 168 lines, tests all 4 `contribute_*` functions through `_aggregate_propulsion` test helper |
| `ui/services/image/defaults.py` | Tier 0 (0/2) | **Tier 2** (covered) | `tests/unit/ui/services/image/test_defaults.py` — 27 lines, tests `get_default_image_provider`/`set_default_image_provider` round-trip |

---

## Prioritized Action Plan

### Immediate (CRITICAL — 7 non-UI Tier 0 files):
1. `game/strategy/engine/session/graph_restoration.py` — save/load + rollback correctness
2. `game/strategy/data/planet_serde.py` — save file data integrity
3. `game/strategy/engine/handlers/fms_shared.py` — all FMS operations depend on this
4. `game/simulation/systems/battle_setup.py` — every battle starts through this
5. `game/strategy/services/fleet_path_projection.py` — strategy renderer movement preview
6. `game/strategy/facade/slices/event_slice.py` — event log UI read path
7. `game/strategy/engine/superweapon_handlers/create_dyson_sphere.py` — superweapon correctness

### Short-term (CRITICAL — 4 UI Tier 0 files):
8. `game/ui/screens/strategy_render/systems.py` — core strategy rendering
9. `game/ui/screens/workshop_viewmodel_selection.py` — ship designer multi-select
10. `game/ui/screens/list_filter_utils.py` — planet/star sort correctness
11. `game/ui/screens/galaxy_test/galaxy_mode.py` — dev tooling

### Medium-term (MAJOR):
12. `game/ui/panels/battle_panels.py` — 564 LOC battle UI with zero coverage

### Lower Priority (MINOR gaps in already-tested files):
- HarvestingEngine private wrappers, SchematicView draw methods, stat_getters formatters, scrollable_json_panel draw methods, LLMDialogService threshold logic
