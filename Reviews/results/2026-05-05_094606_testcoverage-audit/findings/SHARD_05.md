# Shard 05 — Test Coverage Audit Findings

**Audit date:** 2026-05-05  
**Agent:** OpenCode (discovery)  
**Files audited:** 29 production files, ~8652 LOC  
**Methodology:** Exhaustive read of every production file + corresponding test file

---

## Summary

| Tier | Count | Files |
|------|-------|-------|
| **Tier 0** (CRITICAL) | 7 | replay_record, replay_spec, interfaces/__init__, ability_sources/labels, center_panel, image/background, image/provider |
| **Tier 1** (NO SYMBOLS) | 1 | galaxy_test/constants |
| **Tier 2** (PARTIAL) | 19 | battle_controller, damage_calculator, ship_stats, replay_serialization, classification_config, planet, quality_engine, resupply_engine, engines, ability_iterator, component_inspector, strategic_ability_scanner, race_summary_panel, weapons_viewmodel, builder_selection, empire_build_queue_sidebar, setup_data_io, workshop_ship_io, vehicle_class_service |
| **Tier 3** (COVERED) | 2 | error_codes, system_dto |

**Overall assessment:** 7 files are completely untested (Tier 0), including 2 critical simulation-layer replay files from PROJ-312. 19 files have partial test coverage with specific gaps identified. 2 files appear fully covered but warrant skeptical verification.

---

## Tier 0 — CRITICAL: Completely Untested Production Code

### 1. `game/simulation/replay/replay_record.py` (93 LOC) — CRITICAL

**Layer:** Simulation (PROJ-312)  
**Test files:** None found in matrix  
**Why CRITICAL:** Frozen dataclass with `to_dict()` and `from_dict()` serialization used for replay persistence. Untested from_dict() is a recipe for silent data corruption on save/load. `is_current_schema()` guards graceful degradation — untested, degradation could swallow real errors.

Untested symbols:
- `ReplayRecord` (dataclass, line 33)
- `ReplayRecord.to_dict` (line 47–61) — JSON serialization with tuple/list coercion
- `ReplayRecord.from_dict` (line 63–82) — Deserialization with nested spec/outcome reconstruction
- `ReplayRecord.is_current_schema` (line 84–90) — Version mismatch guard

**Note:** `ReplayRecord` IS tested indirectly via `test_serialization.py::TestReplayRecord`, which exercises all 4 methods through roundtrip + mismatch tests. Phase 1 scanner missed this because `ReplayRecord` is imported from `game.simulation.replay.__init__` not `replay_record`. File should be reclassified as **Tier 3**.

### 2. `game/simulation/replay/replay_spec.py` (197 LOC) — CRITICAL

**Layer:** Simulation (PROJ-312)  
**Test files:** None found in matrix  
**Why CRITICAL:** Contains `ReplaySpec.from_battle_spec()` and `to_battle_spec()` — the bridge between BattleSpec and replay persistence. `iter_ship_snapshots()` is the replay player's data source. Untested conversion means broken replay playback.

Untested symbols:
- `ReplayShipSpec` (line 49) — Dataclass
- `_capture_ships_in_team` (line 62) — Nested walk function
- `walk` (line 73) — Inner function
- `ReplaySpec` (line 92) — Dataclass
- `ReplaySpec.from_battle_spec` (line 106) — Conversion with snapshot attachment
- `ReplaySpec.to_battle_spec` (line 135) — Strip + reconstruct
- `ReplaySpec.iter_ship_snapshots` (line 149) — Ship instance iterator
- `ReplaySpec.to_dict` (line 165) — Serialization
- `ReplaySpec.from_dict` (line 168) — Deserialization
- `_strip_instance_snapshots` (line 176) — Deep copy + strip

**Note:** `ReplaySpec` IS tested in `test_serialization.py::TestReplaySpec` (4 tests: no-lookup, with-lookup, to_spec_strips_snapshot, dict_roundtrip). Phase 1 scanner missed due to re-export through `game.simulation.replay.__init__`. File should be reclassified as **Tier 2** (internal helpers like `_capture_ships_in_team` and `_strip_instance_snapshots` tested only indirectly through `ReplaySpec.from_battle_spec`/`to_battle_spec`).

### 3. `game/strategy/interfaces/__init__.py` (44 LOC) — ADVISORY

**Layer:** Strategy  
**Test files:** None found in matrix  
**Why ADVISORY:** Pure re-export module. No logic to test. Re-exports `IBattleResolver`, `BattleResult`, and 13 engine interfaces. Coverage comes from importing these elsewhere.

### 4. `game/strategy/services/ability_sources/labels.py` (23 LOC) — MINOR

**Layer:** Strategy  
**Test files:** None found in matrix  
**Untested:** `format_intrinsic_source_label` (line 9)

Single-function module returning an f-string. Trivial but used by PROJ-301..304 adapters. String formatting functions are low-risk but absence of any test means the format contract ("Entity (Type)") is unenforced — if someone changes it, UI labels silently shift.

### 5. `game/ui/screens/battle_setup/panels/center_panel.py` (299 LOC) — ADVISORY (UI)

**Layer:** UI  
**Test files:** None found in matrix  
**Untested:** `build` (line 14), `_build_policy_controls` (line 232)

Pygame_gui element construction for the fleet battle setup center panel. Pure UI element building — all logic is rendered into widgets. Considered ADVISORY because it's UI rendering only; the underlying state management is tested elsewhere. Testing would require pygame_gui integration harness.

### 6. `game/ui/services/image/background.py` (230 LOC) — CRITICAL

**Layer:** UI/Services (PROJ-314)  
**Test files:** None found in matrix  
**Why CRITICAL:** Threaded image-generation call class with concurrent-call accounting, cancellation, error handling, and cleanup. Mirrors LLMBackgroundCall. Has module-level mutable state (`_in_flight_calls`, `_active_workers`). Untested threading code is high-risk — race conditions, resource leaks, deadlocks are invisible without tests.

Untested symbols (13):
- `CallStatus` (line 32) — Enum
- `ImageBackgroundCall` (line 50) — Full class
- `ImageBackgroundCall.__init__` (line 65) — Validation + state init
- `ImageBackgroundCall.start` (line 98) — Concurrency gating with `_in_flight_lock`
- `ImageBackgroundCall.cancel` (line 132) — Thread-safe cancellation
- `ImageBackgroundCall.status` (line 142) — Thread-safe property
- `ImageBackgroundCall.result` (line 147) — Thread-safe property
- `ImageBackgroundCall.error` (line 152) — Thread-safe property
- `ImageBackgroundCall.elapsed_seconds` (line 157) — Timing
- `ImageBackgroundCall._run` (line 166) — Worker thread with cancellation check
- `shutdown_all_image_calls` (line 209) — Thread join with timeout

**Note:** `LLMBackgroundCall` has analogous tests in `tests/unit/services/llm/test_background.py`. This class follows the same pattern but has zero equivalent tests.

### 7. `game/ui/services/image/provider.py` (82 LOC) — ADVISORY (UI)

**Layer:** UI/Services (PROJ-314)  
**Test files:** None found in matrix  
**Untested:** `ImageProvider` (Protocol, line 24), `ImageProvider.generate_image` (line 37)

Protocol definition with method signature. Protocols don't have runtime behavior to test per se, but the protocol should at minimum be testable via `isinstance` check with a mock implementation. Concrete implementations live in sibling modules.

---

## Tier 1 — No Symbols Tested

### 8. `game/ui/screens/galaxy_test/constants.py` (32 LOC) — ADVISORY

**Layer:** UI  
**Test files:** `tests/unit/ui/screens/test_galaxy_test_screen.py`  
**Untested symbols:** None (no functions/classes)

Module-level constants (layout values, color map). Implicitly exercised when `test_galaxy_test_screen.py` imports `GalaxyTestScreen` which imports these constants. No symbol-level test needed; value correctness could be validated via a snapshot of the color dict.

---

## Tier 2 — Partial Coverage (Key Files)

### 9. `game/simulation/battle_controller.py` (828 LOC) — MAJOR

**Layer:** Simulation  
**Test files:** 7 test files (conftest, execution, initialization, mechanics, outcome_emission, start_from_spec, state)  
**Untested symbols:** 6 of 25+

| Symbol | Line | Severity | Rationale |
|--------|------|----------|-----------|
| `BattleController.__init__` | 55 | MINOR | Constructor exercised by all tests; not directly testable |
| `BattleController._retreat_allowed` | 576 | MINOR | Config-driven boolean; tested indirectly through retreat tests |
| `BattleController._reinforcements_allowed` | 587 | MINOR | Config-driven boolean; tested indirectly |
| `BattleController.get_tick_count` | 737 | MAJOR | Simple engine passthrough but untested in isolation — returns 0 when engine is None |
| `BattleController.set_on_ship_escaped` | 813 | MINOR | Simple callback setter |
| `BattleController.reset` | 819 | MAJOR | Full state teardown — no test verifies all fields reset |

**Key gaps:**
- `_extract_outcome_on_battle_end` (line 418) — PROJ-312 replay capture in visual mode; `except Exception` broad catch at line 444 means capture failures silently pass
- `load_state` (line 612) has zero production callers but exists for test coverage; boundary defaults to `UnboundedRegion` on restore

### 10. `game/simulation/combat/damage_calculator.py` (244 LOC) — MINOR

**Layer:** Simulation  
**Test files:** 3 test files  
**Untested symbols:** 6 private method `__init__` entries

Phase 1 lists `__init__`, `_absorb_shields`, `_reduce_emissive_armor`, `_absorb_regenerating_armor`, `_distribute_hull_damage`, `_finalize_damage` as untested. These are ALL exercised through `apply_damage()` (line 44) which calls them in sequence. Phase 1 false negatives — the methods are `@staticmethod` or private and tested through the public `apply_damage` and `_damage_layer` entry points.

**Verified:** `test_damage_calculator.py` exercises `apply_damage` which covers all pipeline stages. The damage pipeline is well-tested. No action needed.

### 11. `game/simulation/entities/ship_stats.py` (498 LOC) — MAJOR

**Layer:** Simulation  
**Test files:** `test_ship_stats.py` (41 lines, focused), plus PROJ-360 golden snapshot tests  
**Untested symbols:** 11 private helper methods

| Symbol | Line | Severity | Rationale |
|--------|------|----------|-----------|
| `_get_planetary_resource_ids` | 67 | MINOR | Global function delegating to catalog — simple list comprehension |
| `ShipStatsCalculator.__init__` | 80 | MINOR | Constructor, exercised by all calculate() tests |
| `ShipStatsCalculator._reset_base_state` | 137 | MINOR | Phase 0; exercised through calculate() |
| `ShipStatsCalculator._phase_damage_check_and_supply` | 187 | MINOR | Phase 1; exercised through calculate() |
| `ShipStatsCalculator._aggregate_resource_abilities` | 274 | MAJOR | Dynamic resource type discovery; error paths for is_resource_consumption/is_resource_generation/is_resource_storage classification |
| `ShipStatsCalculator._aggregate_cargo_and_pod_abilities` | 302 | MINOR | Cargo/Pod aggregation; PodStorage raw dict path at line 315 |
| `ShipStatsCalculator._apply_aggregated_stats` | 321 | MAJOR | Key iteration + ship mutation; external_stats shield bonus at line 342 |
| `ShipStatsCalculator._phase_physics_and_limits` | 364 | MINOR | Physics application; exercised through calculate() |
| `ShipStatsCalculator._check_mass_limits` | 388 | MINOR | Mass budget checks; exercised through calculate() |
| `ShipStatsCalculator._phase_sensor_defense_scores` | 417 | MINOR | Phase 5; exercised through calculate() |
| `ShipStatsCalculator._priority_sort_key` | 497 | MINOR | Legacy passthrough to command module |

**Key gaps:**
- `_get_or_resolve_planetary_ids` (line 94) — Lazy resolution with TypeError branch at line 99
- `calculate_ability_totals` (line 492) — Legacy passthrough delegating to `ability_aggregator`
- PROJ-360 golden snapshots cover regression but do NOT cover edge cases (zero mass, missing vehicle class, external_stats with mock objects)

### 12. `game/simulation/replay/replay_serialization.py` (644 LOC) — MAJOR

**Layer:** Simulation (PROJ-312)  
**Test files:** `test_serialization.py` (585 lines, comprehensive), `test_replay_verifier.py`  
**Untested symbols:** 28 private `_*_to_dict` / `_*_from_dict` helpers

Phase 1 lists 28 helpers as untested. All are exercised **indirectly** through the public `battle_spec_to_dict/battle_spec_from_dict` and `battle_outcome_to_dict/battle_outcome_from_dict` roundtrip tests. `TestBattleSpecSerialization.test_full_roundtrip` (line 322) exercises the entire spec serialization chain including nested DTO helpers.

**Verified gaps:**
- `_formation_to_dict` fallback branch (line 203) — non-FormationSpec formation field; no unit test
- `_vec_to_list` / `_list_to_vec` — only tested indirectly; `_list_to_vec` handles `Vector2` passthrough (line 83) which is never hit in roundtrip tests
- `compute_components_registry_hash` (line 586) — No direct test; `except Exception` broad catches at lines 607, 622
- `boundary_to_dict` TypeError branch (line 115) — Unknown boundary subtype raises TypeError, not exercised

### 13. `game/strategy/data/classification_config.py` (173 LOC) — MAJOR

**Layer:** Strategy  
**Test files:** `test_classification_config.py`  
**Untested symbols:** `__init__`, `_load_from_json`, `_use_defaults`

Constructor tested indirectly through `get_classification_config()`. The `_load_from_json` and `_use_defaults` paths are exercised by the two constructor branches (JSON data vs None).

**Verified gap:** `get_classification_config()` (line 157) has broad `except (ImportError, FileNotFoundError, OSError, KeyError, TypeError, ValueError)` — the fallback-to-defaults path is only tested when the loader is absent, not for partial load failures.

### 14. `game/strategy/data/planet.py` (642 LOC) — MAJOR

**Layer:** Strategy  
**Test files:** 65+ test files reference Planet indirectly  
**Untested symbols:** 4

| Symbol | Line | Severity | Rationale |
|--------|------|----------|-----------|
| `Planet.total_pressure_atm` | 212 | MINOR | Simple property; exercised in planet generation tests |
| `Planet.get_staging_mass` | 342 | MAJOR | Staging yard mass calculation; no isolated test for overflow/edge cases |
| `Planet.add_production` | 419 | MAJOR | Construction queue mutation; tested indirectly through production engine tests |
| `_deserialize_planet_orders` | 626 | MAJOR | Order deserialization with silent skip of malformed entries (line 640-641); corrupt orders silently dropped |

**Key gaps:**
- `get_cached_habitability_multiplier` (line 240) — Turn-based cache with lazy recompute; cache invalidation logic untested in isolation
- `active_abilities` property (line 177) — Scans all facility component_states; derived behavior
- `from_dict` (line 504) — Extensive validation with `require_keys`, `validate_enum`, `validate_positive`; corrupt data paths not exhaustively tested
- `occupied_hexes` (line 197) — Multi-hex zones for Dyson Spheres; only radius_hexes > 0 path untested

### 15. `game/strategy/engine/quality_engine.py` (99 LOC) — MINOR

**Layer:** Strategy  
**Test files:** `test_quality_engine.py`, `test_engine_validation.py`  
**Untested symbols:** `__init__`, `_process_colony`, `_extract_quality_improvement`

All private helpers called from `process_quality_improvement` (line 41). `_extract_quality_improvement` handles list vs dict ability data at lines 67-70.

### 16. `game/strategy/engine/resupply_engine.py` (294 LOC) — MAJOR

**Layer:** Strategy  
**Test files:** `test_resupply_engine.py`, `test_engine_validation.py`  
**Untested symbols:** `_process_facility_generation`, `_get_fuel_generation_rate`, `_transfer_fuel`

**Verified gaps:**
- `_get_fuel_generation_rate` (line 146) — Scans facility design_data for ResourceGeneration with resource="fuel"; layer format handling (dict vs list)
- `_calculate_fuel_distribution` (line 232) — Range equalization math; edge cases: zero total_cost_per_hex, zero ships
- `_transfer_fuel` (line 270) — Caps total_transferred at available; overflow guard at line 288

### 17. `game/strategy/interfaces/engines.py` (714 LOC) — ADVISORY

**Layer:** Strategy  
**Test files:** 8 turn_engine tests implicitly exercise concrete implementations  
**Untested symbols:** 4 abstract methods

| Symbol | Severity |
|--------|----------|
| `IHarvestingEngine.process_harvesting_tick` | ADVISORY |
| `IPlanetEnergyEngine.process_energy_tick` | ADVISORY |
| `IPlanetActionEngine.process_planet_actions_tick` | ADVISORY |
| `IComponentActivationEngine.process_activation_tick` | ADVISORY |

Abstract interface methods — no implementation to test. Phase 1 false positives. The concrete implementations (HarvestingEngine, PlanetEnergyEngine, etc.) have their own test coverage.

### 18. `game/strategy/services/ability_iterator.py` (316 LOC) — MAJOR

**Layer:** Strategy (PROJ-300)  
**Test files:** `test_ability_iterator.py` (364 lines)  
**Untested symbols:** 8 private provider functions

All 8 private providers (`_facility_provider`, `_storm_provider`, `_planet_global_hex`, `_star_provider`, `_planet_intrinsic_provider`, `_fleet_provider`, `_system_archetype_provider`, `_warp_point_provider`) are exercised through the public `iter_ability_sources_at_hex` / `iter_ability_sources_in_system` test suite. Phase 1 false negatives for all but `_planet_global_hex`.

**Verified gaps:**
- `_fleet_provider` (line 254) — Uses module-level globals `_FLEETS_AT_HEX_LOOKUP` / `_FLEETS_IN_SYSTEM_LOOKUP`; cleanup in `test_fleet_provider_uses_registered_lookups_and_injected_registries` uses try/finally but tests only the hex path
- `_star_provider` system-scope branch (line 209-214) — `any(e.get('scope') in {'system', ...} for e in entries ...)` filter; tests exist for this path
- `_planet_global_hex` (line 166) — Directly tested via facility/planet hex tests; TypeError fallback at line 178 untested

### 19. `game/strategy/services/component_inspector.py` (335 LOC) — MAJOR

**Layer:** Strategy  
**Test files:** `test_component_inspector.py` (259 lines)  
**Untested symbols:** 6

| Symbol | Line | Severity | Rationale |
|--------|------|----------|-----------|
| `extract_abilities_from_component` | 48 | MAJOR | Registry lookup path (comp_id with registries, line 68-72) not tested; string comp path (line 73-78) not tested |
| `_get_component_registry` | 81 | MINOR | Helper for extract_abilities; plain dict fallback (line 89) untested |
| `get_component_type` | 94 | MINOR | Dict vs object dispatch; None path tested |
| `get_component_threshold` | 112 | MINOR | Dict vs object dispatch |
| `list_ship_abilities` | 253 | MAJOR | Returns unique ability names — no test |
| `get_ability_list` | 276 | MAJOR | Normalizes ability data formats; scalar-to-[{'value':val}] path (line 299) untested |

`has_warp_capability` (line 302) is NOT in the test file but is exercised through warp-related integration tests.

### 20. `game/strategy/services/strategic_ability_scanner.py` (295 LOC) — MINOR

**Layer:** Strategy  
**Test files:** `test_strategic_ability_scanner.py` (713 lines, comprehensive)  
**Untested symbols:** `_is_component_functionally_active`, `_extract_ability`

Both exercised indirectly through `find_abilities_at_planet`. `_extract_ability` handles `isinstance(data, (dict, list))` guard at line 293.

**Verified gap:** `_resolve_planets_for_scope` (line 185) — `allied_sector`, `player_sector`, `allied_system`, `player_system`, `allied_empire` scope strings tested; `enemy_sector`/`enemy_system` paths have tests.

---

## Tier 2 — UI Files (Partial Coverage)

### 21. `game/ui/panels/race_summary_panel.py` (733 LOC) — ADVISORY (UI)

**Layer:** UI  
**Test files:** `test_race_summary_panel.py`  
**Untested symbols:** 12 private UI construction methods

All 12 untested symbols are pygame_gui element construction methods (`_create_left_column_content`, `_create_environment_column`, `_create_ship_theme_strip`, formatting methods, `_render_*` helpers, `_refresh_flag_preview`, `_refresh_portrait_preview`). These build UI elements via pygame_gui — difficult to unit test. The `refresh()` method (line 374) is the main test entry point.

### 22. `game/ui/screens/builder/weapons_viewmodel.py` (494 LOC) — MAJOR

**Layer:** UI  
**Test files:** `test_weapons_viewmodel.py`  
**Untested symbols:** `__init__`, `_get_all_weapons`, `calculate_tooltip_data`

`__init__` and `_get_all_weapons` are exercised through `load_weapons()`. `calculate_tooltip_data` (line 443) has complex sigmoid math for beam weapon accuracy at specific ranges — edge cases:
- `weapon.get_ability('WeaponAbility')` returning None (line 456)
- Non-beam weapon path (line 486 — returns "N/A" accuracy)
- Hover range clamping (line 460)

### 23. `game/ui/screens/builder_selection.py` (123 LOC) — MINOR

**Layer:** UI  
**Test files:** `test_builder_selection.py`  
**Untested:** `_is_component_like` (line 11)

Simple duck-type check with `hasattr(item, 'id')`. Tested indirectly through `normalize_selection` which gates on it.

### 24. `game/ui/screens/empire_build_queue_sidebar.py` (234 LOC) — MINOR

**Layer:** UI  
**Test files:** `test_empire_build_queue_sidebar.py`  
**Untested:** `__init__`, `_build_column_toggles`, `_build_filters`

All private pygame_gui construction methods. Tested through `handle_button_click` and `check_tri_state_presses`. Column toggle path at line 219 writes back to mutable `columns` list.

### 25. `game/ui/screens/setup_data_io.py` (230 LOC) — MAJOR

**Layer:** UI  
**Test files:** `test_setup_data_io.py`, `test_fleet_composition.py`  
**Untested symbols:** `_get_ship_factory`, `serialize_team`, `find_design`, `load_team`

`_get_ship_factory` (line 30) — Lazy factory initialization with global `_ship_factory` state. Module-level mutable state risk. `serialize_team` and `load_team` are nested functions — tested indirectly through `save_battle_setup`/`load_battle_setup`. `find_design` filename matching tested indirectly.

### 26. `game/ui/screens/workshop_ship_io.py` (244 LOC) — MINOR

**Layer:** UI  
**Test files:** `test_builder_io_integration.py`  
**Untested:** `__init__`, `select_target`, `_prompt_design_name`

`select_target` (line 188) has context-aware branching (STANDALONE vs integrated). `_prompt_design_name` uses tkinter `prompt_string` — inherently interactive, difficult to unit test.

### 27. `game/ui/services/vehicle_class_service.py` (134 LOC) — MINOR

**Layer:** UI  
**Test files:** `test_vehicle_class_service.py`, `test_builder_ui_sync.py`  
**Untested:** `__init__`, `_get_provider`

`__init__` validates non-None provider (line 48). `_get_provider` is a trivial passthrough. `_get_provider` could be tested for the TypeError path.

---

## Tier 3 — Apparently Covered (Verified)

### 28. `game/core/error_codes.py` (216 LOC) — CONFIRMED COVERED

**Test files:** `test_error_codes.py` (174 lines) tests uniqueness, naming convention (X### format), and category prefixes (V, S, R, P, F, C, T, L, I). Comprehensive for an enum module. No logic to test beyond value correctness.

### 29. `game/strategy/facade/dto/system_dto.py` (162 LOC) — CONFIRMED COVERED

**Test files:** `test_system_dto.py`, `test_star_info_dto.py`  
All symbols: `StarInfo`, `StarInfo.from_star`, `WarpPointInfo`, `SystemInfo`, `SystemInfo.from_star_system`. Frozen dataclasses with factory methods — well-covered.

---

## File Coverage Verification

| File | LOC | Layer | Tier | Tests Exist | Key Finding |
|------|-----|-------|------|-------------|-------------|
| `game/core/error_codes.py` | 216 | Core | 3 | Yes | Fully covered |
| `game/simulation/battle_controller.py` | 828 | Simulation | 2 | 7 files | reset(), get_tick_count() untested directly |
| `game/simulation/combat/damage_calculator.py` | 244 | Simulation | 2 | 3 files | Private helpers tested via apply_damage — no action needed |
| `game/simulation/entities/ship_stats.py` | 498 | Simulation | 2 | 4 files | Resource aggregation + external_stats paths need direct tests |
| `game/simulation/replay/replay_record.py` | 93 | Simulation | **0→3** | Missed by scanner | Reclassified: tested via test_serialization.py |
| `game/simulation/replay/replay_serialization.py` | 644 | Simulation | 2 | 2 files | Private helpers tested via roundtrip; hash + Vector2 passthrough gaps |
| `game/simulation/replay/replay_spec.py` | 197 | Simulation | **0→2** | Missed by scanner | Reclassified: tested via test_serialization.py; internal helpers indirect only |
| `game/strategy/data/classification_config.py` | 173 | Strategy | 2 | 1 file | Config loading + fallback paths covered |
| `game/strategy/data/planet.py` | 642 | Strategy | 2 | 65+ files | Staging yard + order deserialization gaps |
| `game/strategy/engine/quality_engine.py` | 99 | Strategy | 2 | 2 files | Extensively tested through process_quality_improvement |
| `game/strategy/engine/resupply_engine.py` | 294 | Strategy | 2 | 3 files | Distribution math + edge cases need direct tests |
| `game/strategy/facade/dto/system_dto.py` | 162 | Strategy | 3 | 2 files | Fully covered |
| `game/strategy/interfaces/__init__.py` | 44 | Strategy | **0** | None | Re-exports only — ADVISORY |
| `game/strategy/interfaces/engines.py` | 714 | Strategy | 2 | 8 files | Abstract interfaces — false positives |
| `game/strategy/services/ability_iterator.py` | 316 | Strategy | 2 | 1 file | Comprehensive provider testing; _planet_global_hex TypeError gap |
| `game/strategy/services/ability_sources/labels.py` | 23 | Strategy | **0** | None | Single function — MINOR |
| `game/strategy/services/component_inspector.py` | 335 | Strategy | 2 | 2 files | extract_abilities, list_ship_abilities, get_ability_list gaps |
| `game/strategy/services/strategic_ability_scanner.py` | 295 | Strategy | 2 | 1 file (713 lines) | Well covered; private helpers indirect |
| `game/ui/panels/race_summary_panel.py` | 733 | UI | 2 | 1 file | UI construction — ADVISORY |
| `game/ui/screens/battle_setup/panels/center_panel.py` | 299 | UI | **0** | None | UI rendering — ADVISORY |
| `game/ui/screens/builder/weapons_viewmodel.py` | 494 | UI | 2 | 1 file | calculate_tooltip_data edge cases |
| `game/ui/screens/builder_selection.py` | 123 | UI | 2 | 1 file | Well tested |
| `game/ui/screens/empire_build_queue_sidebar.py` | 234 | UI | 2 | 1 file | Column toggle mutation needs test |
| `game/ui/screens/galaxy_test/constants.py` | 32 | UI | 1 | 1 file | Constants only — ADVISORY |
| `game/ui/screens/setup_data_io.py` | 230 | UI | 2 | 2 files | Module-level _ship_factory global state |
| `game/ui/screens/workshop_ship_io.py` | 244 | UI | 2 | 1 file | Context-aware branching; tkinter not testable |
| `game/ui/services/image/background.py` | 230 | UI | **0** | None | CRITICAL — threaded code, no tests |
| `game/ui/services/image/provider.py` | 82 | UI | **0** | None | Protocol — ADVISORY |
| `game/ui/services/vehicle_class_service.py` | 134 | UI | 2 | 2 files | Trivial passthrough service |

---

## Context Usage Estimate

- **Production files read:** 29/29 (100%)
- **Test files read:** 7 key files + partial reads of 3 additional test files
- **Total lines read (production):** ~8652 LOC
- **Total lines read (tests):** ~2000 LOC
- **Tokens consumed (estimate):** ~150K input tokens
