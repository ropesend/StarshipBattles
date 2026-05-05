# Shard 17 — Test Coverage Audit Report

**Audit date:** 2026-05-04  
**Scope:** 33 production files, ~8431 LOC  
**Methodology:** Full read of every production file; verified test file existence; spot-checked key test file content (test_spatial_behaviors.py, test_hex_math_core.py, test_ship_stats_calculator_phases.py, test_race_description_llm_controller.py).

---

## Summary

| Tier | Count | LOC |
|------|-------|-----|
| TIER_0_NO_TESTS | 9 | 1,253 |
| TIER_1_NO_SYMBOLS (init.py) | 3 | 42 |
| TIER_2_PARTIAL | 16 | 5,421 |
| TIER_3_APPARENTLY_COVERED | 6 | 1,715 |
| **Total** | **34** | **~8,431** |

**Two CRITICAL blind spots:** `ShipCombatManager` (184 LOC simulation core) and `CommandDispatchSlice` (219 LOC strategy facade) have zero unit tests. `ShipStatsCalculator` has severely partial coverage (4/21 symbols tested, 12 test functions covering mostly Phase 1 only).

---

## CRITICAL — Tier 0 Non-UI with Zero Tests

### 1. `game/simulation/entities/ship_combat_manager.py` (184 LOC)
**Test files:** None.  
**Untested symbols (7/7):**
- `ShipCombatManager` — Core combat orchestration class
- `__init__` — Initializes combat state (just_fired_projectiles, total_shots_fired, aim_point)
- `combat_engine` — Lazy initialization of ShipCombatEngine
- `set_event_bus()` — Wires event bus into combat engine
- `die()` — Sets ship to dead, zeros velocity, recalculates stats
- `update(dt, context)` — 5-phase per-tick update (resources → components → stats → physics → firing)
- `update_derelict_status()` — Checks crew capacity and functional capability (weapons/engines)

**Severity:** CRITICAL. This delegate orchestrates the ship's entire combat lifecycle per tick. The `update()` method has explicitly load-bearing phase ordering. A regression in `die()`, `update_derelict_status()`, or the update loop could silently corrupt battle outcomes.

### 2. `game/strategy/facade/slices/command_dispatch_slice.py` (219 LOC)
**Test files:** None.  
**Untested symbols (34/34):**
- `CommandDispatchSlice` class + `__init__` + `handle_command`
- 28 `dispatch_*` methods (issue_colonize, issue_move, issue_intercept, issue_join_fleet, clear_orders, issue_transfer, issue_warp, split_fleet, delete_order, reorder_order, issue_self_destruct, queue_colonize_mission, queue_implode_planet_mission, queue_stellerate_star_mission, queue_open_warp_point_mission, queue_close_warp_point_mission, queue_create_dyson_sphere_mission, issue_implode_planet, issue_stellerate_star, issue_open_warp_point, issue_close_warp_point, issue_create_dyson_sphere, issue_build_order, remove_build_order, add_to_construction_queue, remove_from_construction_queue, reorder_construction_queue, issue_planet_order, clear_planet_orders, delete_planet_order, set_atmosphere_target)

**Severity:** CRITICAL for completeness; MODERATE in practice. Each dispatch method is a thin one-line late-import wrapper around a command constructor plus `_handle_command()`. The actual commands and their handlers (superweapon, planet, etc.) ARE tested elsewhere (`test_superweapon_command_handlers.py`, `test_planet_command_handlers.py`, etc.). However, the absence of any direct test means no regression guard for the dispatch surface itself — if a method name changes or an import path rots, it won't be caught until integration.

---

## MAJOR — Tier 2 Partial Coverage with Significant Gaps

### 3. `game/simulation/entities/ship_stats.py` (643 LOC)
**Test files:** `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py` (12 test functions)  
**Coverage:** 4/21 symbols tested. 12 test functions exist but cover mainly Phase 1 (damage_check) and Phase 2 (crew_allocation), with light coverage of Phase 3 (stats_aggregation).  
**Untested symbols (17/21):**
- `_get_planetary_resource_ids` — Helper for catalog lookup (called internally but never directly tested with mock catalog)
- `ShipStatsCalculator.__init__` — Constructor
- `_phase_sensor_defense_scores` (Phase 5) — To-hit, defense scores, ECM, emissive armor, shield regenerating armor, repair rate, ammo generation, resource initialization, combat endurance — **significant untested phase**
- `_phase_physics_and_limits` (Phase 4) — Acceleration, max_speed, turn_speed with inverse mass scaling, radius calculation, mass budget checks
- `_phase_stats_aggregation` (Phase 3) — Aggregates thrust, shields, hangar from active components
- `_aggregate_resource_abilities` — Dynamic resource type discovery, ResourceStorage/Generation/Consumption
- `_aggregate_cargo_and_pod_abilities` — CargoStorage and PodStorage
- `_aggregate_propulsion_abilities` — CombatPropulsion, StrategicMovement, WarpJump, ManeuveringThruster
- `_aggregate_defense_abilities` — Armor HP pool, ShieldProjection, ShieldRegeneration, energy cost
- `_aggregate_hangar_abilities` — VehicleLaunch, VehicleStorage, launch cycle
- `_apply_aggregated_stats` — Atomic application including external_stats shield_bonus_add + shield_capacity_mult
- `_phase_resource_allocation` (Phase 2) — Crew/life support allocation, priority sorting
- `_phase_damage_check_and_supply` (Phase 1) — Damage threshold check, supply gathering
- `_priority_sort_key` — Component priority for crew allocation
- `_check_mass_limits` — Layer mass budget validation
- `_initialize_resources` — First-load fill vs delta updates, shield capacity changes
- `_get_ability_total` — Delegates to get_ability_total from ability_aggregator

**Severity:** MAJOR. While `calculate()` (the main entry point) is exercised indirectly through battle runner tests, the individual phases lack targeted unit tests. Phase 4 (physics) and Phase 5 (defense/sensor scores) have zero direct test coverage. The PROJ-271 shield_bonus_add logic inside `_apply_aggregated_stats` has no test.

**Note:** The pre-computed matrix flags 17 untested symbols, but the `_phase_damage_check_and_supply` and `_phase_resource_allocation` methods in the untested list ARE actually exercised through `test_damage_check_phase_marks_damaged_components` and `test_crew_allocation_phase_*`. The heuristic matcher didn't detect this because the tests create mock ships and call `calculator.calculate()` (which calls these phases internally) without referencing the method names directly. The actual effective untested count is closer to 12-13.

### 4. `game/strategy/services/race_description_llm_controller.py` (317 LOC)
**Test files:** `tests/unit/strategy/services/test_race_description_llm_controller.py` (415 LOC test file)  
**Coverage:** 16/25 tested.  
**Untested symbols (9/25):**
- `re_roll_socio` — Cancel + restart socio generation
- `cancel_socio` — Cancel socio background call
- `_start_bio` — Private method that assembles prompt, fires LLMBackgroundCall
- `_start_socio` — Same for socio
- `_gather_captions` — Assembles caption data from RaceCaptionLoader
- `_poll_field` — Per-frame polling of in-flight calls
- `_apply_bio_transition` — Applies generated text to race_config on DONE
- `_apply_socio_transition` — Same for socio
- `_fire_on_change` — Fires the on_change callback

**Severity:** MAJOR. The public API (generate_bio, generate_socio, re_roll_bio, cancel_bio, cancel_all, set_race_config, update) is well-tested. Missing coverage is on private helpers and the socio re_roll/cancel path. The `_apply_bio_transition` / `_apply_socio_transition` methods are the write-back path to race_config — if broken, generated text silently fails to persist.

### 5. `game/simulation/combat/ability_stat_registry.py` (237 LOC)
**Test files:** `tests/unit/simulation/combat/test_ability_stat_registry.py`, `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`  
**Coverage:** 2/4 symbols tested.  
**Untested symbols (2/4):**
- `_extract_value` — Reads numeric value from ability_data dict or primitive
- `_route_team_ids` — Routes scope to team_ids (handles enemy_* fan-out)

**Severity:** MAJOR. Both are private helpers called by `emit_entries_for_ability`, which IS tested. The untested helpers are indirectly exercised. However, `_extract_value` has three code paths (dict, int/float, other) and `_route_team_ids` has branching for opponent scopes — direct edge-case testing is missing. Adding a new mapping to `ABILITY_STAT_REGISTRY` with unusual value shapes (e.g., dict without the expected field, or the zero-value early-return path) could expose bugs.

### 6. `game/simulation/battle_controller.py` (828 LOC)
**Test files:** 7 test files in `tests/unit/simulation/battle_controller/`  
**Coverage:** 25/31 tested.  
**Untested symbols (6/31):**
- `__init__` — Constructor (indirectly covered via factory/setup, no dedicated test)
- `_retreat_allowed` — Property checking config flags
- `_reinforcements_allowed` — Property checking config flags
- `get_tick_count` — Simple accessor
- `set_on_ship_escaped` — Callback registration setter
- `reset` — Full state reset

**Severity:** MAJOR. The 7 test files provide extensive coverage of spec-based start, execution flow, state management, mechanics, initialization, and outcome emission. The 6 untested symbols are all either simple property accessors or setup methods that are exercised indirectly. The `reset()` method has no direct test — it clears `_is_configured`, `_is_started`, `_ship_id_map`, `_initial_state`, `_outcome`, and calls retreat/state manager reset. A test verifying post-reset behavior would be valuable.

### 7. `game/core/hex_math.py` (394 LOC)
**Test files:** `tests/unit/core/test_hex_math_core.py` (923 LOC) + `test_hex_math_strategy.py`  
**Coverage:** 21/22 tested.  
**Untested (1/22):** `_hex_round` — Private rounding function for cube coordinates.

**Severity:** MINOR (false flag). `_hex_round` is called by `pixel_to_hex` and `hex_lerp`, both of which have extensive tests (923 LOC of hex tests). The function has indirect coverage through these callers. No dedicated test for the rounding tiebreaker logic (q_diff > r_diff > s_diff branch priority) exists, but the indirect path exercises all three branches.

### 8. `game/research/data/tech_tree.py` (265 LOC)
**Test files:** 7 test files in `tests/unit/research/tech_tree/` + `test_research_service*.py`  
**Coverage:** 11/12 tested.  
**Untested (1/12):** `TechTree.__init__` — Simple constructor setting `self.nodes = {}` and `self._depth_cache = {}`.

**Severity:** MINOR. Constructor is trivial; `load_from_json` factory method has full test coverage including edge cases.

### 9. `game/simulation/systems/battle_end_conditions.py` (496 LOC)
**Test files:** 27 test files reference this module.  
**Coverage:** 57/67 tested.  
**Untested (10/67):** All 10 are `__repr__` methods (`TickLimitCondition.__repr__`, `TeamEliminatedCondition.__repr__`, `TeamIncapacitatedCondition.__repr__`, `EscapeCondition.__repr__`, `ShipDestroyedCondition.__repr__`, `NeverCondition.__repr__`, `MassRatioCondition.__repr__`, `AnyCondition.__repr__`, `AllCondition.__repr__`, `TeamIncapacitatedCondition._team_has_capability`).

**Severity:** MINOR. The repr methods are debugging/display helpers. `_team_has_capability` is a private static method called by `is_met()` which IS tested. The core behaviors (is_met, to_dict, from_dict, description) have solid coverage.

---

## MINOR — Tier 2 Partial with Limited Missing Branches

### 10. `game/ui/panels/race_aptitudes_panel.py` (280 LOC)
**Test files:** `tests/unit/ui/panels/test_race_aptitudes_panel.py`, `tests/unit/ui/screens/test_race_setup_screen.py`  
**Coverage:** 6/13 tested. Untested: `_create_content`, `_create_budget_section`, `_create_aptitude_section`, `_create_cost_breakdown_section`, `_get_aptitude_value`, `_set_aptitude_value`, `_format_cost`. All private UI construction methods.

### 11. `game/ui/renderer/game_renderer.py` (171 LOC)
**Test files:** `tests/unit/ui/renderer/test_game_renderer.py`  
**Coverage:** 1/2 tested. Untested: `scale` — a local nested function inside `draw_ship`. This is a closure, not a module-level symbol; functionally a helper variable.

### 12. `game/ui/research/research_controls.py` (475 LOC)
**Test files:** `tests/unit/research/research_controls/conftest.py` (no test_*.py found)  
**Coverage:** 1/13 tested. Only the class constructor symbol is matched via conftest import. Untested: `_create_ui`, `handle_event`, `update_selected_node`, `clear_selection`, `update_budget_display`, `_toggle_auto_spread`, `_update_auto_spread_button`, `_update_allocation_slider_range`, `update_turn_log`, `clear_log`, `reset`.

### 13. `game/ui/screens/builder/right_panel.py` (437 LOC)
**Test files:** `tests/unit/builder/test_builder_ui_sync.py`  
**Coverage:** 3/16 tested. Untested: `__init__`, `on_registry_reloaded`, `on_ship_updated`, `setup_controls`, `setup_stats`, `_sync_from_stats_panel`, `rebuild_stats`, `update_class_dropdown`, `update_vehicle_type_dropdown`, `update_role_dropdown`, `_get_role_dropdown_data`, `update_dropdowns_for_data_reload`, `update_stats_display`.

### 14. `game/ui/screens/new_game_setup_screen.py` (738 LOC)
**Test files:** `tests/unit/ui/screens/test_new_game_setup_extended.py`, `tests/unit/ui/test_new_game_setup.py`  
**Coverage:** 21/34 tested. Untested: `system_count_slider_inverse` (module-level helper function), `_init_state`, `_init_widget_refs`, `galaxy_type` (appears twice — getter/setter property), `_create_ui`, `_create_empire_inputs`, `_on_load_race_clicked`.

### 15. `game/ui/screens/race_validator.py` (96 LOC)
**Test files:** `tests/unit/ui/screens/test_race_validator.py`  
**Coverage:** 2/3 tested. Untested: `RaceValidator.__init__` — trivial constructor creating `RacePointBudget()`.

### 16. `game/ui/screens/star_list_filters.py` (204 LOC)
**Test files:** `tests/unit/ui/screens/test_star_list_filters.py`  
**Coverage:** 6/8 tested. Untested: `matches_filter` (module-level function), `padded_range` (module-level function).

### 17. `game/ui/screens/test_lab/panel_manager.py` (233 LOC)
**Test files:** `tests/unit/test_lab/test_panel_manager.py`  
**Coverage:** 2/5 tested. Untested: `__init__`, `create_results_panel`, `create_ui_buttons`.

### 18. `game/ui/services/design_loader_adapter.py` (99 LOC)
**Test files:** `tests/unit/ui/services/test_design_loader_adapter.py`  
**Coverage:** 3/4 tested. Untested: `DesignLoaderAdapter.__init__` — constructor with DI validation.

---

## ADVISORY — UI Rendering + `__init__.py` (Tier 0/1)

### 19. `game/ui/screens/strategy_render/background.py` (58 LOC)
**Test files:** None.  
Untested: `BackgroundLayer`, `__init__`, `_load_background`, `draw`. Background image loading/scaling/blitting for the strategy map.

### 20. `game/ui/screens/strategy_windows/transfer_dialogs.py` (79 LOC)
**Test files:** None.  
Untested: `TransferDialogRegistrar`, `__init__`, `open`, `open_quick`. Thin delegate that opens TransferDialog or CargoQuickDialog windows through StrategyWindowManager.

### 21. `game/ui/screens/test_lab/details/validation.py` (253 LOC)
**Test files:** None.  
Untested: `_phase_color`, `draw_validation_results`, `draw_single_validation`, `draw_numeric_difference`. Validation rendering for Combat Lab test run details.

### 22. `game/ui/services/image/background.py` (230 LOC)
**Test files:** None.  
Untested: `CallStatus`, `ImageBackgroundCall`, `__init__`, `start`, `cancel`, `status`, `result`, `error`, `elapsed_seconds`, `_run`, `shutdown_all_image_calls`. Background-thread image generation helper (PROJ-314). Mirrors LLMBackgroundCall which IS tested.

### 23. `game/ui/services/image/defaults.py` (45 LOC)
**Test files:** None.  
Untested: `get_default_image_provider`, `set_default_image_provider`. Simple module-level accessor pair.

### 24. `game/ui/services/tkinter_utils.py` (231 LOC)
**Test files:** None.  
Untested: `get_tk_root`, `is_tkinter_available`, `reset_tk_root`, `open_save_dialog`, `open_load_dialog`, `prompt_string`, `copy_to_clipboard`. Tkinter platform-dependent utilities with extensive error handling. The broad except blocks mean a malformed filetypes arg could produce unexpected behavior.

### 25. `game/strategy/config/__init__.py` (0 LOC)
Empty package init — no testable surface.

### 26. `game/strategy/data/__init__.py` (0 LOC)
Empty package init — no testable surface.

### 27. `game/strategy/services/ability_sources/__init__.py` (42 LOC)
Package init with `__all__` exports. Imports 8 adapters and 2 format helpers. No testable logic — pure re-export. Test files for the individual adapters exist in `tests/unit/strategy/services/ability_sources/`.

---

## TIER 3 — Verified Coverage

These 6 files have all symbols matched to test files. Spot-checked for quality:

### 28. `game/ai/spatial_behaviors/free_maneuver.py` (25 LOC)
**Test:** `tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py`  
`TestFreeManeuverBehavior` class has 2 tests: `test_free_maneuver_returns_none` (verifies `compute_target_position` returns None) and `test_free_maneuver_type` (verifies `behavior_type == "free_maneuver"`). Coverage is adequate for this trivial delegate.

### 29. `game/strategy/config/economy_config.py` (151 LOC)
**Test:** `tests/unit/strategy/config/test_economy_config.py`  
All 5 symbols tested: `EconomyConfig`, `primary_resource` property, `load_economy_config`, `get_default_economy_config`, `set_default_economy_config`. The data-driven JSON loading with graceful fallback is well-tested.

### 30. `game/strategy/engine/planet_command_handlers.py` (220 LOC)
**Test:** `tests/unit/strategy/engine/test_planet_command_handlers.py`  
6 handlers tested (IssuePlanetOrder, ClearPlanetOrders, DeletePlanetOrder, SetAtmosphereTarget, SetGravityTarget, SetWaterTarget, SetRadiationShieldTarget). Each handler's execute method has tests for ownership validation, error paths, and success paths.

### 31. `game/strategy/engine/superweapon_command_handlers.py` (353 LOC)
**Test:** `tests/unit/strategy/engine/test_superweapon_command_handlers.py`, `test_superweapon_edge_cases.py`, `test_superweapon_handler_validation.py`  
All 22 symbols tested. 11 handlers (5 direct + 5 mission + SelfDestruct) with thorough validation tests.

### 32. `game/strategy/facade/dto/empire_dto.py` (116 LOC)
**Test:** `tests/unit/strategy/facade/test_empire_dto.py`  
All 6 symbols tested: `ColonySummary` + `from_planet`, `FleetSummary` + `from_fleet`, `EmpireInfo` + `from_empire`. Frozen dataclass DTOs with factory constructors — well-covered.

### 33. `game/strategy/quickstart_builder.py` (312 LOC)
**Test:** `tests/unit/quickstart/test_quickstart_builder.py`, `tests/unit/strategy/test_quickstart_builder.py`, `tests/unit/strategy/engine/test_population_seeding.py`  
All 8 symbols tested. `QuickstartBuilder.build_1p_config`, `build_2p_config`, `load_test_race`, `get_quickstart_races_dir`, `get_quickstart_designs_dir`, `populate_initial_complexes`, etc. Well-covered.

---

## File Coverage Verification Table

| File | LOC | Tier | Tested/Total | Untested Count | Key Gaps |
|------|-----|------|-------------|----------------|----------|
| `game/ai/spatial_behaviors/free_maneuver.py` | 25 | 3 | 2/2 | 0 | — |
| `game/core/hex_math.py` | 394 | 2 | 21/22 | 1 | `_hex_round` (indirectly covered) |
| `game/research/data/tech_tree.py` | 265 | 2 | 11/12 | 1 | `__init__` (trivial) |
| `game/simulation/battle_controller.py` | 828 | 2 | 25/31 | 6 | `__init__`, `reset`, accessors |
| `game/simulation/combat/ability_stat_registry.py` | 237 | 2 | 2/4 | 2 | `_extract_value`, `_route_team_ids` |
| `game/simulation/entities/ship_combat_manager.py` | 184 | **0** | 0/7 | **7** | **CRITICAL: no tests** |
| `game/simulation/entities/ship_stats.py` | 643 | 2 | 4/21 | 17 | Phases 3-5, all `_aggregate_*` helpers |
| `game/simulation/systems/battle_end_conditions.py` | 496 | 2 | 57/67 | 10 | 10 `__repr__` methods + 1 private helper |
| `game/strategy/config/__init__.py` | 0 | 1 | 0/0 | 0 | Empty file |
| `game/strategy/config/economy_config.py` | 151 | 3 | 5/5 | 0 | — |
| `game/strategy/data/__init__.py` | 0 | 1 | 0/0 | 0 | Empty file |
| `game/strategy/engine/planet_command_handlers.py` | 220 | 3 | 14/14 | 0 | — |
| `game/strategy/engine/superweapon_command_handlers.py` | 353 | 3 | 22/22 | 0 | — |
| `game/strategy/facade/dto/empire_dto.py` | 116 | 3 | 6/6 | 0 | — |
| `game/strategy/facade/slices/command_dispatch_slice.py` | 219 | **0** | 0/34 | **34** | **CRITICAL: no tests** |
| `game/strategy/quickstart_builder.py` | 312 | 3 | 8/8 | 0 | — |
| `game/strategy/services/ability_sources/__init__.py` | 42 | 1 | 0/0 | 0 | Re-export init |
| `game/strategy/services/race_description_llm_controller.py` | 317 | 2 | 16/25 | 9 | Socio cancel/re-roll, private helpers |
| `game/ui/panels/race_aptitudes_panel.py` | 280 | 2 | 6/13 | 7 | UI construction privates |
| `game/ui/renderer/game_renderer.py` | 171 | 2 | 1/2 | 1 | `scale` (nested closure) |
| `game/ui/research/research_controls.py` | 475 | 2 | 1/13 | 12 | Almost entirely untested |
| `game/ui/screens/builder/right_panel.py` | 437 | 2 | 3/16 | 13 | Heavy UI — mostly untested |
| `game/ui/screens/new_game_setup_screen.py` | 738 | 2 | 21/34 | 8 | `_create_ui`, `_create_empire_inputs` |
| `game/ui/screens/race_validator.py` | 96 | 2 | 2/3 | 1 | `__init__` (trivial) |
| `game/ui/screens/star_list_filters.py` | 204 | 2 | 6/8 | 2 | `matches_filter`, `padded_range` |
| `game/ui/screens/strategy_render/background.py` | 58 | **0** | 0/4 | **4** | ADVISORY: rendering |
| `game/ui/screens/strategy_windows/transfer_dialogs.py` | 79 | **0** | 0/4 | **4** | ADVISORY: window registrar |
| `game/ui/screens/test_lab/details/validation.py` | 253 | **0** | 0/4 | **4** | ADVISORY: validation rendering |
| `game/ui/screens/test_lab/panel_manager.py` | 233 | 2 | 2/5 | 3 | `create_results_panel`, `create_ui_buttons` |
| `game/ui/services/design_loader_adapter.py` | 99 | 2 | 3/4 | 1 | `__init__` |
| `game/ui/services/image/background.py` | 230 | **0** | 0/11 | **11** | ADVISORY: image bg calls |
| `game/ui/services/image/defaults.py` | 45 | **0** | 0/2 | **2** | ADVISORY: accessors |
| `game/ui/services/tkinter_utils.py` | 231 | **0** | 0/7 | **7** | ADVISORY: tkinter utils |

---

## Prioritized Remediation Plan

### Immediate (CRITICAL)
1. **`ship_combat_manager.py`** — Write unit tests for `ShipCombatManager`:
   - `test_die_sets_alive_false_and_zeros_velocity`
   - `test_update_skips_dead_ship`
   - `test_update_runs_all_phases_in_order` (verify resource update → component update → stats recalc → physics → firing)
   - `test_update_derelict_status_crew_check`
   - `test_update_derelict_status_functional_capability` (weapons+engines)
   - `test_combat_engine_lazy_init`
   - `test_set_event_bus`
   — Estimated: 10-15 test functions

2. **`command_dispatch_slice.py`** — Write integration-level tests verifying dispatch methods route commands correctly. Since each dispatch is a thin wrapper, a single parameterized test per dispatch group (fleet orders, missions, superweapons, build, planet orders) is sufficient. Estimated: 5-7 parameterized test functions.

### High Priority (MAJOR)
3. **`ship_stats.py`** — Extend `test_ship_stats_calculator_phases.py` to cover:
   - Phase 3: `_aggregate_resource_abilities` (dynamic resource type discovery)
   - Phase 3: `_aggregate_cargo_and_pod_abilities` (CargoStorage, PodStorage)
   - Phase 4: `_phase_physics_and_limits` (inverse mass scaling, radius calc, mass budget)
   - Phase 5: `_phase_sensor_defense_scores` (defense score, ECM, emissive armor, shield regen armor)
   - `_apply_aggregated_stats` with external_stats shield_bonus_add path
   - `_initialize_resources` (first-load vs delta-update path)
   — Estimated: 15-20 test functions

4. **`race_description_llm_controller.py`** — Add tests for:
   - `cancel_socio` / `re_roll_socio` paths
   - Socio DONE transition (verify `_apply_socio_transition`)
   - Verify `_fire_on_change` is called on transitions
   — Estimated: 5-8 test functions

5. **`ability_stat_registry.py`** — Add direct tests for:
   - `_extract_value` with dict missing value_field, primitive int, primitive float, empty dict
   - `_route_team_ids` with enemy_* scope and num_teams=3, 4
   - `emit_entries_for_ability` with zero-value (early return path)
   — Estimated: 6-8 test functions

6. **`battle_controller.py`** — Add test for `reset()` method verifying full state restoration. Estimated: 1-2 test functions.

### Medium Priority (MINOR)
7. **`battle_end_conditions.py`** — Tests for `_team_has_capability` with edge cases (no operational weapons or engines). Estimated: 2-3 test functions.
8. **`star_list_filters.py`** — Tests for `matches_filter` and `padded_range`. Estimated: 3-5 test functions.
9. **`hex_math.py`** — Direct test for `_hex_round` tiebreaker logic (unlikely to fail given indirect coverage, but adds explicit regression guard). Estimated: 1-2 test functions.

### Low Priority (ADVISORY — UI rendering)
10. UI files marked ADVISORY (`background.py`, `transfer_dialogs.py`, `validation.py`, `image/background.py`, `image/defaults.py`, `tkinter_utils.py`) are rendering/utility code where testing ROI is lower. `tkinter_utils.py` has the most logic of this group and would benefit most from tests.

---

## Context Usage Estimate

| Phase | Activity | Tokens |
|-------|----------|--------|
| Doc reading (docs/01-03) | 3 full architecture docs | ~15,000 |
| Coverage matrix extraction | 1 full JSON + per-entry parsing | ~15,000 |
| Production file reading | 33 files, ~8,431 LOC | ~60,000 |
| Test file verification | 19 test files, spot checks | ~10,000 |
| Report compilation | Structured write | ~5,000 |
| **Total estimate** | | **~105,000 tokens** |

---

## Verification Notes

- All 33 production files read in full.
- Test file existence verified via filesystem check.
- Key test file content spot-checked: `test_spatial_behaviors.py`, `test_hex_math_core.py`, `test_ship_stats_calculator_phases.py`, `test_race_description_llm_controller.py`.
- `test_hex_math_core.py` confirmed at 923 LOC with extensive coverage; `_hex_round` untested in name but exercised through `pixel_to_hex` and `hex_lerp`.
- `test_ship_stats_calculator_phases.py` confirmed at 371 LOC / 12 test functions; coverage is Phase 1-2 heavy, Phase 3-5 light.
- `test_race_description_llm_controller.py` confirmed at 415 LOC with mock providers (_StubProvider, _RaisingProvider, _BlockingProvider). Coverage is public-API focused; private helpers and socio path mostly untested.

---

*Report ends.*
