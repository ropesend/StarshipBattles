# Shard 16 — Test Coverage Audit Report

**Generated:** 2026-05-20
**Methodology:** Full read of every production file + corresponding test files
**Files audited:** 42 | **Heuristic LOC:** ~9608 | **Actual tiers after audit:** 0=6, 1=2, 2=21, 3=13

---

## Summary

| Tier | Count | Description |
|------|-------|-------------|
| CRITICAL (Tier 0) | 6 | Zero tests for non-trivial production code (not __init__.py re-exports) |
| MAJOR (Tier 1) | 2 | Top-level package __init__ re-exports; simulation __init__ has 0 symbol-level tests |
| MINOR (Tier 2) | 21 | Partial coverage — untested error paths, private methods, corner cases |
| ADVISORY (Tier 3) | 13 | Appears well-covered; minor gaps noted where found |

**Heuristic correction:** The heuristic baseline misclassified `app_bootstrap.py` as Tier 0 — two test files exist (invariants + profiling) and exercise 7/7 symbols through integration paths. This file moves to Tier 2. Two `__init__.py` re-exports (`research/data/`, `strategy/adapters/`) were Tier 0 in the heuristic but are ADVISORY by convention (re-exports only, no logic).

**Six true Tier 0 gaps found**, totaling ~892 LOC of completely untested production code.

---

## Tier 0 — CRITICAL (Zero Tests)

### 1. `game/simulation/components/abilities/planetary/environmental.py` (90 LOC)
- **Status:** NO test file exists. ZERO coverage.
- **Symbols:** `EnvironmentalDamageAbility` (class + `__init__`, `get_primary_value`, `get_ui_rows`), `FuelDrainAbility` (class + `__init__`, `get_primary_value`, `get_ui_rows`)
- **Risk:** These abilities drive the environmental hazard engine — fleet hull damage and fuel drain per turn. Bugs here silently corrupt combat balance.
- **Test suggestion:** Create `tests/unit/simulation/components/abilities/test_environmental.py` covering:
  - `EnvironmentalDamageAbility` with dict data (rate, damage_type present), with non-dict data (defaults), with missing rate (defaults to 0.0)
  - `FuelDrainAbility` with dict data, with non-dict
  - `get_primary_value()` returns rate for both
  - `get_ui_rows()` returns properly formatted label/value dicts for both

### 2. `game/ui/screens/build_queue_renderer.py` (247 LOC)
- **Status:** NO test file exists. ZERO coverage.
- **Symbols:** `BuildQueueRenderer` (class + `__init__`, `refresh_items_list`, `refresh_queue_display`, `refresh_roles_list`, `update_queue_header`, `refresh_pause_button`)
- **Risk:** Core rendering pipeline for the build queue screen. All 6 methods have branching logic (empty list, missing panels, active_source None, etc.).
- **Gaps:**
  - L80-137: `refresh_items_list` — empty designs branch (L130-136), cost rendering, portrait loading, invalid-design prefix
  - L140-173: `refresh_queue_display` — data_source/virtual_table interaction, optional `on_queue_selector_refresh` callback
  - L175-213: `refresh_roles_list` — missing `roles_scrollable` guard (L182-183), negative btn_width branch (L196-197), selected role highlight
  - L215-225: `update_queue_header` — active_source None vs present branches
  - L227-246: `refresh_pause_button` — active_source None (disabled), active_source present (enabled + label)

### 3. `game/ui/screens/strategy_render/warp_lanes.py` (69 LOC)
- **Status:** NO test file exists. ZERO coverage.
- **Symbols:** `draw_warp_lanes`, `is_on_screen` (nested closure)
- **Risk:** Warp lane rendering on the strategy map. All viewport culling and reciprocal-warp paired-or-unpaired branching is untested. A regression here would make warp lanes disappear or render incorrectly.
- **Gaps:** L19-69 — two rendering branches (reciprocal warp exists vs doesn't), draw-pair dedup (L49-52), viewport culling (L46-47, L66-67)

### 4. `game/ui/screens/strategy_windows/fleet_report_ctrl.py` (73 LOC)
- **Status:** NO test file exists. ZERO coverage.
- **Symbols:** `FleetReportRegistrar` (class + `__init__`, `open`, `_on_closed`)
- **Risk:** Fleet Report window lifecycle management. The `open` method has two branches (existing alive window vs new construction) and builds a closure that captures `facade` and `fleet_owner_id`.
- **Gaps:** L27-70 — window reuse branch (L39-41), new construction branch (L44-70), split_fleet_callback closure (L53-60), _on_closed lifecycle (L72-73)

### 5. `game/ui/screens/test_lab/renderer/orchestrator.py` (211 LOC)
- **Status:** NO test file exists. ZERO coverage. Note: there IS a `tests/unit/ui/screens/test_lab/test_renderer_pure_functions.py` that tests `_is_condition_verified` and `_format_check_pair` — but those are now delegated to `_condition_logic.py` / `_draw_helpers.py`, not tested via this orchestrator.
- **Symbols:** `TestLabRenderer` (class + `__init__`, `draw`)
- **Risk:** Central draw method of the Combat Lab renderer. Delegates to 6 sub-panels, the ViewModel's ship/component/results panels, output log, pygame_gui, and dialogs. Failure here breaks the entire Test Lab UI.
- **Gaps:** L67-140 (`__init__` — panel construction with font/layout wiring), L142-211 (`draw` — 9 rendering sub-steps with conditional checks for ViewModel panels and dialogs)

### 6. `game/ui/screens/test_lab/renderer/test_list_panel.py` (202 LOC)
- **Status:** NO test file exists. ZERO coverage.
- **Symbols:** `TestListPanel` (class + `__init__`, `draw`, `_draw_scrollbar`)
- **Risk:** Scrollable test list rendering panel. Complex scrolling logic, test selection/hover states, validation flags, batch execution progress, and scrollbar thumb computation are all untested.
- **Gaps:**
  - L53-173: `draw` — test selection color (L143-150), hover color, batch-running progress text (L88-105), scroll offset clipping (L124-167), no-tests fallback (L107-110)
  - L175-202: `_draw_scrollbar` — thumb height/position calculation (L195-198)

---

## Tier 1 — MAJOR

### 7. `game/simulation/__init__.py` (130 LOC)
- **Status:** Heuristic Tier 1. Four candidate test files exist but none test the __init__ re-exports directly — they test the re-exported classes via other imports.
- **Risk:** Any typo in the `__all__` list or import path creates a silent ImportError for consumers. 27 re-exports with no import verification test.
- **Note:** Test files listed by heuristic (test_battle_outcome.py, test_battle_spec.py, test_outcome_emission.py, test_physics.py) test the underlying classes, not the __init__.py exports.

### 8. `game/app_bootstrap.py` (343 LOC) — Heuristic correction
- **Status:** The heuristic classified this as Tier 0, but two test files exist: `test_app_bootstrap_invariants.py` (329 LOC, 8 tests) and `test_app_bootstrap_profiling.py` (140 LOC, 6 tests). These exercise `bootstrap()` end-to-end via patching. However, individual functions are not unit-tested in isolation.
- **Existing tests cover:** Init ordering (6 invariants + 2 PROJ-366 invariants), BootstrapResult completeness, profiling phase recording, log emission
- **Untested (MAJOR gaps):**
  - L56-67: `configure_logging()` — never called in isolation; error paths (os.makedirs failure) untested
  - L70-76: `parse_args()` — never called in isolation; `parse_known_args` edge cases untested
  - L104-117: `_detect_resolution()` — only exercised via bootstrap with mocked display.Info; edge cases (monitor_w < 2560, monitor_h < 1600) untested
  - L310-311: `_replay_combat_lab_fallback()` — never called in tests
  - L328-341: `BootstrapResult` construction — reply_store/replay_verification_coordinator fields only tested for existence, not correctness

---

## Tier 2 — MINOR (Partial coverage, specific gaps)

### 9. `game/ai/fighter_controller.py` (140 LOC)

- **Test file:** `tests/unit/ai/test_fighter_controller.py` (181 LOC, 5 tests)
- **Covered:** no enemies idle, nearest-enemy targeting, kamikaze ram deferral, dead fighter no-op, factory dispatch
- **Untested:**
  - L115-136: `_find_nearest_enemy()` — only exercised indirectly via `update()`; the helper itself has error-handling branch (L129-132: `except (AttributeError, TypeError): continue`) that is never triggered
  - Enemy with no `.position` attribute path (L130-132) untested
  - Spatial grid returning non-ship entities that pass `is_combatant` but have no `.position` — untested

### 10. `game/core/event_logging.py` (61 LOC)

- **Test file:** `tests/unit/core/event_logging/test_event_bus.py`
- **Covered:** EventBus construction, handler setting, event logging, handler-less silent drop
- **Untested:**
  - L60: Handler exception branch (`except Exception` on L60) — the intentional broad catch that prevents simulation crashes is untested

### 11. `game/simulation/combat/targeting_system.py` (325 LOC)

- **Test files:** `test_targeting_system.py`, `test_weapon_dispatch_golden.py`, `test_weapon_firing_system.py`
- **Heuristic says untested:** `_get_pdc_valid_targets`, `_get_pdc_target_type`
- **Verified gaps:**
  - L209-239: `_get_pdc_valid_targets()` — 3 fallback branches (beam_ab present with pdc_valid_targets, beam_ab present without, weapon_ab fallback, default). The `weapon_ab` fallback path (L235-237) is likely dead code (PROJ-359 MAJ-001 removed the redundant `has_ability` lookup).
  - L241-267: `_get_pdc_target_type()` — `is_missile` branch, vehicle_type branch, UNKNOWN fallback. The `UNKNOWN` fallback (L267) is untested.
  - L125-207: `find_valid_target()` — SEEKER family branch (L196-201) has its own range check; the non-SEEKER beam/PDC flow (L202-205) uses `weapon_ab.check_firing_solution`. The failure path where check_firing_solution returns False (L204) is likely untested in isolation.
  - L88-123: `select_target()` — inline Lambda distance sort (L120-121) has no direct test for ties or near-equivalent distances.

### 12. `game/simulation/validation/ship_validator.py` (450 LOC)

- **Test files:** 12 candidate test files, heaviest coverage in the codebase for this category
- **Heuristic says untested (12 symbols):** All `_do_validate` and `_should_validate` internal methods. These are exercised through the public `validate_addition()` / `validate_design()` entry points but never tested in isolation.
- **Specific gaps verified:**
  - L145-167: `LayerRestrictionDefinitionRule._do_validate()` — HullOnly branch (L156-159) is not tested directly
  - L169-194: `_check_block_rules()` — `deny_ability` path (L192-194) has no direct test
  - L196-233: `_check_allow_rules()` — the `allow_rules` empty guard (L207-208), `allow_ability` branch (L227-230), and "not allowed" error (L232-233) have limited coverage
  - L236-264: `MassBudgetRule._do_validate()` — layer mass path (L255-262) with `layer_type in ship.layers` guard and max_mass_pct calculation
  - L267-348: `ClassRequirementsRule._do_validate()` — maintenance rule (L339-346: `RequiresMaintenance` vs `ProvidesMaintenance`) and life-support rule (L325-334) are likely covered indirectly but hard to verify from file reads alone
  - L351-390: `ResourceDependencyRule._do_validate()` — the ResourceConsumption/ResourceStorage TypeGuard branches (L367-380)

### 13. `game/strategy/data/build_queue_source.py` (463 LOC)

- **Test file:** `tests/unit/strategy/data/test_build_queue_source.py`
- **Heuristic says untested:** `_load_production_rates`, `_get_facility_production_rates`, `_get_planetary_yard_size_multiplier`
- **Verified gaps:**
  - L32-44: `_load_production_rates()` — caching branch (L39) vs JSON-load branch (L41); `except (FileNotFoundError, ValueError)` error path (L42-43) untested
  - L175-207: `_get_facility_production_rates()` — explicit_rates branch (L199-202), default rates branch (L204-205), no-SpaceShipyard fallback (L207)
  - L210-242: `_get_planetary_yard_size_multiplier()` — registry lookup path (L235-241), non-operational facility guard (L227-228)
  - L93-129: `get_build_rate_booster_mult()` — `galaxy is None or empire is None` short-circuit (L108-109), booster iteration over scopes
  - L132-172: `colony_has_planetary_yard()` — `isinstance(comp, str)` path (L166-171)

### 14. `game/strategy/data/classification_config.py` (173 LOC)

- **Test file:** `tests/unit/strategy/data/test_classification_config.py`
- **Heuristic says untested:** `__init__`, `_load_from_json`, `_use_defaults`
- **Verified gaps:**
  - L64-74: `__init__` — data-with-classification vs data-without-classification vs None branches
  - L76-124: `_load_from_json()` — 25+ attribute assignments; partial JSON (missing sub-sections) default-fallback behavior untested
  - L126-154: `_use_defaults()` — 25+ attribute assignments, all copy-paste from class-level dicts
  - L157-173: `get_classification_config()` — `except (ImportError, FileNotFoundError, ...)` fallback branch (L170-173)
  - The `lru_cache(maxsize=1)` on `get_classification_config()` is not tested for cache behavior

### 15. `game/strategy/data/planet.py` (504 LOC)

- **Test files:** 73 candidate test files (most-referenced file in the shard)
- **Heuristic says untested:** `_is_carried_vehicle_dict`, `_staging_yard_carried_vehicle`, `total_pressure_atm`, `get_staging_mass`, `add_production`
- **Verified gaps:**
  - L33-44: `_is_carried_vehicle_dict()` — CarriedVehicle instance branch (L40-41), dict-with-valid-vehicle_type branch (L42-44), non-dict/non-CV fallback (L42-44)
  - L47-73: `_pod_from_dict()` — DropPod instance identity branch (L59-60), non-dict fallback (L62), legacy flat shape path (L65-73)
  - L76-87: `_staging_yard_carried_vehicle()` — same 3 branches
  - L249-251: `total_pressure_atm` — division by zero if atmosphere is empty dict
  - L390-402: `get_staging_mass()` — dict-shape fallback (L399) vs typed entry (L400)
  - L485-491: `add_production()` — simple list append; low priority
  - L199-216: `__post_init__` — staging yard normalization with 3 branches per entry

### 16. `game/strategy/data/ship_instance_bridge.py` (173 LOC)

- **Test file:** `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py`
- **Heuristic says untested:** `__init__`
- **Verified gaps:**
  - L34-35: `__init__` — trivial one-liner (low priority)
  - L46-117: `to_ship()` — damage application branch (L77-83: damage > 0 check), per-component HP branch (L92-103: per_id_index tracking), resource levels branch (L108-112)
  - L119-173: `update_from_ship()` — is_alive branches (L128-136: alive-with-damage vs alive-full-hp vs dead), per-component state rebuild (L143-158)

### 17. `game/strategy/engine/action_execution_engine.py` (329 LOC)

- **Test files:** `test_action_execution_engine.py`, `test_action_execution_engine_gaps.py`
- **Heuristic says untested:** `__init__`, `_process_fleet_action_tick`, `_process_planet_action_tick`, `_execute_planet_action`
- **Verified gaps:**
  - L55-68: `__init__` — trivial wiring
  - L134-218: `_process_fleet_action_tick()` — speed<=0 guard (L149-150), tick%interval check (L156-157), BUILD order auto-pop branch (L169-174), action_time_resolver vs static fallback (L185-192)
  - L245-297: `_process_planet_action_tick()` — get_current_order None guard (L258-260), action_time_resolver vs static fallback (L269-276)
  - L299-329: `_execute_planet_action()` — handler None guard (L319-321), handler without execute_for_issuer guard (L319), issuer adapter construction

### 18. `game/strategy/services/effect_ability_display.py` (182 LOC)

- **Test file:** `tests/unit/strategy/services/test_effect_ability_display.py`
- **Heuristic says untested:** `_effect_facet`, `_ability_kind`, `_format_status`, `_is_activatable`
- **Verified gaps:**
  - L26-34: `_effect_facet()` — meta is None branch (L34)
  - L37-44: `_ability_kind()` — facet is None fallback (L44)
  - L53-65: `_format_status()` — state is None (L55), ACTIVATING with remaining (L60-61), DEACTIVATING with remaining (L63-64), Inactive fallback (L65)
  - L68-70: `_is_activatable()` — non-dict input (L70), dict without activation_time (L70)

### 19. `game/strategy/services/replay_store.py` (495 LOC)

- **Test files:** `test_replay_store_eviction.py`, `test_replay_verification_coordinator.py`, `test_replay_store_instance.py`, `test_replay_store.py` (integration)
- **Heuristic says untested:** 17 symbols — most internal helpers
- **Verified gaps:**
  - L80-109: `load_replay_settings()` — corrupt-JSON branch (L88-90), missing-file branch (L83-85), type-conversion-error branches (L96-97, L103-104)
  - L143-167: `ReplayStore.__init__` — trivial
  - L187-208: `add/remove_on_record_persisted_listener` — duplicate-add guard (L198), unknown-remove tolerance (L207-208)
  - L224-228: `_replay_dir` — private alias (L224-228)
  - L230-235: `_ensure_replay_dir` — mkdir path
  - L239-272: `on_battle_started/ended` — save_root=None branch (L250-251), pending-miss branch (L265-270)
  - L276-310: `persist()` — json_writer failure branch (L291-293), listener error branch (L304-307)
  - L334-369: `load()/load_or_error()` — missing/corrupt/version_drift branches
  - L371-386: `delete()` — unlink failure, sidecar unlink
  - L390-402: `_safe_load()` — corrupt JSON, non-dict, schema mismatch branches
  - L404-456: eviction, iteration, path extraction, sidecar unlink — all internal

### 20. `game/ui/panels/planet_report_panel.py` (674 LOC)

- **Test files:** `test_planet_report_panel.py`, `test_planet_report_panel_characterization.py`
- **Heuristic says untested:** `_qty_cell`, `_qual_cell`, `_flow_cell`, `_stockpile_cell`
- **Verified gaps:**
  - L97-100+: `_qty_cell()` — non-dict deposit branch (L98), missing quantity branch
  - `_qual_cell()` — same pattern
  - `_flow_cell()` — missing projection, missing attribute
  - `_stockpile_cell()` — missing key in stockpile dict

### 21. `game/ui/screens/battle_setup/controller.py` (559 LOC)

- **Test file:** `tests/unit/ui/screens/battle_setup/test_controller.py`
- **Heuristic says untested:** `__init__`, `_get_active_fleet`, `duplicate_task_force`, `duplicate_squadron`, `set_fleet_battle_role`, `set_ship_policy`, `set_selected_policy`, `_toggle_dict_for`, `save_setup`, `_save_to_path`, `load_setup`, `_load_from_path`
- **Verified**: The test file exercises mutation methods. The heuristic's 12 "untested" symbols include `__init__` (low priority) and complex CRUD/save-load methods.
- **Gaps confirmed:**
  - `_toggle_dict_for` — private helper, exercised indirectly
  - `save_setup` / `load_setup` — tkinter file dialog path likely mocked; error paths (file-not-found, corrupt JSON) need verification
  - `_save_to_path` / `_load_from_path` — os.makedirs branch, JSON write failure branch

### 22. `game/ui/screens/battle_setup/screen.py` (98 LOC)

- **Test files:** `test_renderer.py`, `test_battle_setup_state.py`
- **Heuristic says untested:** `handle_event`, `update`, `draw`, `handle_resize`, `start`, `_get_toggle`
- **Verified:** Screen is a thin IScene shell delegating to controller/renderer/input_handler. The `handle_event`, `update`, `draw` methods are pygame-dependent delegates. `start` delegates to controller. `_get_toggle` delegates to controller. These are tested implicitly through controller/renderer tests but not directly.
- **Low risk** — screen is 98 lines of delegation.

### 23. `game/ui/screens/build_queue_helpers.py` (214 LOC)

- **Test file:** `tests/unit/ui/screens/test_build_queue_helpers.py`
- **Heuristic says untested:** `_get_planetary_ids`
- **Verified:** `_get_planetary_ids` is an lru_cache-wrapped helper called by exported functions; tested indirectly.
- **Additional gaps:** `calculate_per_turn_spend` and `calculate_queue_turn_spend` have complex math for limiting-resource and carry-over. The zero-rate blocking branch (L99-101), `turn_capacity <= 0` skip (L147), and blocked-item saturation (L175-178) need verification.

### 24. `game/ui/screens/build_queue_viewmodel.py` (268 LOC)

- **Test file:** `tests/unit/ui/screens/test_build_queue_viewmodel.py`
- **Heuristic says untested:** `__init__`, `queue_sources`
- **Verified:** `__init__` tests the two branches (queue_sources=None vs list). `queue_sources` is a property getter. Both likely tested through constructor scenarios.

### 25. `game/ui/screens/builder/components.py` (173 LOC)

- **Test file:** `tests/unit/ui/screens/builder/test_components.py`
- **Heuristic says untested:** `set_selected`, `set_hovered`
- **Verified:** These are simple setter methods. `_generate_tooltip` has 40+ lines of conditional ability-checking with many branches needing verification.

### 26. `game/ui/screens/fleet_report_sidebar.py` (512 LOC)

- **Test file:** `tests/unit/ui/screens/test_fleet_report_sidebar.py`
- **Heuristic says untested:** `__init__`, `_build_widgets`, `_build_filter_section`, `_create_status_filter_button`, `_build_column_section`, `_build_actions_section`, `update_column_button`
- **Verified gaps:**
  - L113-259: `_build_widgets` — 80+ lines constructing 14+ UILabel/UIButton elements; mostly UI boilerplate
  - L261-300: `_build_filter_section` — 4 status filter buttons + 2 tri-state sections, all exercised implicitly via `update_summary`
  - L345-421: `update_summary()` — multiple conditional branches for fuel pct > 0 (L372-375), energy pct > 0 (L379-382), warp capability states (L394-421: 10+ branches)
  - L454-468: `update_column_button()` — visible vs hidden button text formatting

### 27. `game/ui/screens/strategy_fleet_context_menu.py` (218 LOC)

- **Test files:** `test_fleet_context_menu_dispatch.py`, `test_fleet_context_menu_position.py`
- **Heuristic says untested:** `FleetContextMenu.__init__`, `_create_buttons`, `_format_row`, `required_height`, `PlanetContextMenu.__init__`, `PlanetContextMenu._create_buttons`, `PlanetContextMenu.required_height`
- **Verified:**
  - Test files cover `clamp_menu_position` (5 directions) and `dispatch_action`
  - Menu class constructors and button-creation are pygame_gui-dependent and likely untested directly
  - `_format_row` (L124-138) — shortcut-empty branch (L131-132), padding math
  - `FleetContextMenu.required_height` and `PlanetContextMenu.required_height` — zero-items guard (num_items <= 0)
  - `PlanetContextMenu.process_event` (L202-208) — no callback guard (L205)

### 28. `game/ui/screens/transfer_controller.py` (369 LOC)

- **Test files:** `test_transfer_controller.py`, `test_transfer_view_model_container.py`
- **Heuristic says untested:** `__init__`, `_resolve_endpoints`, `_direction`
- **Verified gaps:**
  - `_resolve_endpoints` — complex facade query logic with multiple branches
  - `_direction` — enum/default resolution
  - `ConfirmResult` dataclass — reuse confirmed, but individual branch testing unclear

### 29. `game/ui/screens/workshop_viewmodel.py` (494 LOC)

- **Test files:** 5 test files, heavy coverage
- **Heuristic says untested:** `_with_ship`
- **Verified:** `_with_ship` is likely a context manager used internally. Need to verify its error-path (exception in body). Low severity — heavily-tested file.

---

## Tier 3 — ADVISORY (Appears well-covered)

### 30. `game/core/event_logging.py` (61 LOC)
Single untested branch: handler-exception catch (L60).

### 31. `game/services/llm/types.py` (95 LOC)
5 dataclasses/enums — all pure data with no logic. Tested via `test_types.py`. TokenUsage.cached_prompt_tokens default (L60) verified.

### 32. `game/simulation/combat/families/pdc.py` (45 LOC)
Single method delegates to `build_beam_resolution`. Covered by weapon family handler tests.

### 33. `game/simulation/components/component_constants.py` (69 LOC)
3 classes: enum + 2 data classes. `Modifier.evaluate_effects()` has late import — verify it's exercised.

### 34. `game/strategy/data/ship_instance_serializer.py` (211 LOC)
All 6 static methods covered by `test_ship_instance_serializer.py` and `test_fms_a_audit_fixes.py`. `clone()` deep-copy path verified.

### 35. `game/strategy/engine/turn_phase_registry.py` (340 LOC)
5 dedicated test files. Purity test verifies no game-engine imports. Golden test pins DEFAULT_TICK_PHASE_LIST order. Well-covered.

### 36. `game/strategy/generation/storm_generator.py` (223 LOC)
`test_storm_generator.py` covers generation. Verify: `_find_valid_center` max_attempts exhaustion (L208-217, returns None), `_collect_occupied_hexes` with existing_storms.

### 37. `game/strategy/services/planet_query_service.py` (83 LOC)
5 static methods, all covered. `can_build_type` unknown vehicle_type (L82-83 returns False) verified.

### 38. `game/strategy/services/race_resolver.py` (43 LOC)
Single function, 3 resolution-order branches. Covered by `test_race_resolver.py`.

### 39. `game/ui/screens/builder/weapons_input_handler.py` (102 LOC)
`detect_tooltip_hover` covered by `test_weapons_input_handler.py`. All 3 return-None branches + tooltip data path.

### 40. `game/ui/utils/formatters.py` (90 LOC)
3 functions: `format_compact_number` (5 branches: >=1M, >=1K, <=-1K, 0+, negatives), `format_signed_float` (positive/zero, negative, -0.0 edge), `get_damage_color` (inactive, 0%, <25%, <50%, >=50%). Covered by `test_formatters.py`.

### 41. `game/ui/widgets/dropdown_helper.py` (52 LOC)
Single function with 3 branches (None input, empty options, selected-not-in-options). Covered by `test_dropdown_helper.py`.

### 42. `game/research/data/__init__.py` (6 LOC) + `game/strategy/adapters/__init__.py` (10 LOC)
Re-export __init__.py files. No logic to test. ADVISORY by convention.

---

## File Coverage Verification Table

| # | File | LOC | Tier | Has Tests | Test Files | Key Gaps |
|---|------|-----|------|-----------|------------|----------|
| 1 | fighter_controller.py | 140 | 2 | Yes | 1 | `_find_nearest_enemy` error-path (L130) |
| 2 | app_bootstrap.py | 343 | 2 | Yes | 2 | `configure_logging`, `parse_args`, `_detect_resolution` edges, `_replay_combat_lab_fallback` |
| 3 | event_logging.py | 61 | 3 | Yes | 10 | Handler exception branch (L60) |
| 4 | research/data/__init__.py | 6 | 3 | No | 0 | Re-export only — ADVISORY |
| 5 | llm/types.py | 95 | 3 | Yes | 7 | Pure data — OK |
| 6 | simulation/__init__.py | 130 | 1 | No | 4* | No direct re-export verification; *tests test underlying classes |
| 7 | families/pdc.py | 45 | 3 | Yes | 1 | OK |
| 8 | targeting_system.py | 325 | 2 | Yes | 3 | `_get_pdc_valid_targets` weapon_ab fallback, `_get_pdc_target_type` UNKNOWN fallback |
| 9 | environmental.py | 90 | **0** | No | 0 | **CRITICAL — ZERO tests** |
| 10 | component_constants.py | 69 | 3 | Yes | 18 | OK |
| 11 | ship_validator.py | 450 | 2 | Yes | 12 | HullOnly, deny_ability, allow_ability, maintenance, mass layer path |
| 12 | adapters/__init__.py | 10 | 3 | No | 0 | Re-export only — ADVISORY |
| 13 | build_queue_source.py | 463 | 2 | Yes | 9 | `_load_production_rates` error path, `_get_facility_production_rates` branches, `_get_planetary_yard_size_multiplier` |
| 14 | classification_config.py | 173 | 2 | Yes | 1 | `__init__` branches, `_load_from_json` partial-JSON, `get_classification_config` except path |
| 15 | planet.py | 504 | 2 | Yes | 73 | `_is_carried_vehicle_dict`, `_pod_from_dict`, `_staging_yard_carried_vehicle`, `total_pressure_atm`, `get_staging_mass` |
| 16 | ship_instance_bridge.py | 173 | 2 | Yes | 1 | `to_ship` damage/resource branches, `update_from_ship` alive/dead/component branches |
| 17 | ship_instance_serializer.py | 211 | 3 | Yes | 2 | OK |
| 18 | action_execution_engine.py | 329 | 2 | Yes | 7 | `_process_fleet_action_tick` all branches, `_process_planet_action_tick`, `_execute_planet_action` |
| 19 | turn_phase_registry.py | 340 | 3 | Yes | 5 | OK — golden test + purity test |
| 20 | storm_generator.py | 223 | 3 | Yes | 1 | `_find_valid_center` exhaustion (None return) |
| 21 | effect_ability_display.py | 182 | 2 | Yes | 1 | `_effect_facet`, `_ability_kind`, `_format_status`, `_is_activatable` (4 private helpers) |
| 22 | planet_query_service.py | 83 | 3 | Yes | 1 | OK |
| 23 | race_resolver.py | 43 | 3 | Yes | 1 | OK |
| 24 | replay_store.py | 495 | 2 | Yes | 4 | 17 private helpers — listener API, persist error paths, load/delete/safe_load all branches |
| 25 | planet_report_panel.py | 674 | 2 | Yes | 3 | `_qty_cell`, `_qual_cell`, `_flow_cell`, `_stockpile_cell` (4 cell formatters) |
| 26 | battle_setup/controller.py | 559 | 2 | Yes | 1 | save/load error paths, `_toggle_dict_for` |
| 27 | battle_setup/screen.py | 98 | 2 | Yes | 2 | Thin IScene shell — low risk |
| 28 | build_queue_helpers.py | 214 | 2 | Yes | 1 | `_get_planetary_ids` (indirect), zero-rate blocking in spend math |
| 29 | build_queue_renderer.py | 247 | **0** | No | 0 | **CRITICAL — ZERO tests** |
| 30 | build_queue_viewmodel.py | 268 | 2 | Yes | 1 | `__init__`, `queue_sources` — likely covered anyway |
| 31 | builder/components.py | 173 | 2 | Yes | 1 | `set_selected`, `set_hovered`, `_generate_tooltip` conditional branches |
| 32 | weapons_input_handler.py | 102 | 3 | Yes | 1 | OK |
| 33 | fleet_report_sidebar.py | 512 | 2 | Yes | 2 | `update_summary` 10+ conditional branches, widget builder methods |
| 34 | strategy_fleet_context_menu.py | 218 | 2 | Yes | 2 | Menu class constructors (pygame_gui), `_format_row`, `required_height` guards |
| 35 | warp_lanes.py | 69 | **0** | No | 0 | **CRITICAL — ZERO tests** |
| 36 | fleet_report_ctrl.py | 73 | **0** | No | 0 | **CRITICAL — ZERO tests** |
| 37 | test_lab/orchestrator.py | 211 | **0** | No | 0 | **CRITICAL — ZERO tests** |
| 38 | test_lab/test_list_panel.py | 202 | **0** | No | 0 | **CRITICAL — ZERO tests** |
| 39 | transfer_controller.py | 369 | 2 | Yes | 2 | `_resolve_endpoints`, `_direction` |
| 40 | workshop_viewmodel.py | 494 | 2 | Yes | 5 | `_with_ship` error path |
| 41 | formatters.py | 90 | 3 | Yes | 2 | OK |
| 42 | dropdown_helper.py | 52 | 3 | Yes | 1 | OK |

---

## Remediation Priority

1. **IMMEDIATE:** Write tests for the 6 Tier 0 files (~892 LOC total):
   - `environmental.py` — core simulation damage/fuel mechanics
   - `build_queue_renderer.py` — UI rendering with 6 methods, many branches
   - `warp_lanes.py` — strategy map rendering, viewport culling
   - `fleet_report_ctrl.py` — fleet report window lifecycle
   - `test_lab/orchestrator.py` — Combat Lab renderer orchestration
   - `test_lab/test_list_panel.py` — scrollable test list with complex scrolling

2. **HIGH:** Fill gaps in `replay_store.py` (17 untested internal methods, error paths critical for crash resilience), `action_execution_engine.py` (planet FMS tick path), `ship_validator.py` (HullOnly, deny_ability, maintenance/life-support rules).

3. **MEDIUM:** Add isolation tests for `app_bootstrap.py` helper functions (`configure_logging`, `parse_args`, `_detect_resolution`, `_replay_combat_lab_fallback`), `build_queue_source.py` private helpers, `classification_config.py` JSON-load branches.

4. **LOW:** Verify `simulation/__init__.py` re-exports via import test. Add corner-case tests for `targeting_system.py` family-metadata edge paths. Test `planet_report_panel.py` cell formatters in isolation.
