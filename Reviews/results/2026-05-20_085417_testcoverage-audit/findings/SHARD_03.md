# Shard 03 — Test Coverage Audit (Discovery Agent)

**Date:** 2026-05-20  
**Files audited:** 39 production files  
**LOC audited:** ~9762  

## Summary

| Metric | Count |
|--------|-------|
| CRITICAL gaps (Tier 0 non-UI with zero/minimal tests) | 2 |
| MAJOR gaps (Tier 1, untested error paths) | 3 |
| MINOR gaps (partial coverage) | 18 |
| ADVISORY (UI, `__init__.py` re-exports) | 8 |
| Files verified as fully covered | 8 |

**Overall assessment:** Shard 03 shows moderate coverage with 2 genuine CRITICAL gaps in core strategy logic (BuildOrderCommandHandler family). The Phase 1 heuristic misclassified `terraforming.py` as Tier 0 (no tests) — tests exist but only cover 2/4 ability classes. Several Tier 2 files have meaningful gaps in inner helper functions that exercise error paths. UI files are appropriately classified as ADVISORY.

---

## Tier 0 — CRITICAL

### 1. `game/strategy/engine/handlers/build.py` (97 LOC) — CRITICAL

**Status:** NO DEDICATED TESTS. Confirmed Tier 0.

**Symbols:**
- `BuildOrderCommandHandler.execute` (line 42) — Creates BUILD order, inserts at front via `IFleetMutator`, clears path. No test coverage.
- `RemoveBuildOrderCommandHandler.execute` (line 77) — Removes BUILD orders via `IFleetMutator`. No test coverage.
- `register(registry)` (line 91) — Registers both handlers into CommandRegistry. No test coverage.

**Risk:** These are production command handlers wired into the live command dispatcher via `create_default_registry`. A regression in either handler breaks the entire build-order feature (players cannot toggle construction mode on/off via UI). The handlers call `IFleetMutator.insert_order`, `IFleetMutator.set_path`, and `Fleet.remove_orders_by_type` — all mutation paths that need verification.

**Test reference files checked (none found):**
- No `test_build*.py` under `tests/unit/strategy/engine/handlers/`
- Other handlers have dedicated tests: `test_movement_handlers.py`, `test_order_queue_handlers.py`

**Suggested tests:**
1. `BuildOrderCommandHandler` with valid fleet → BUILD order at position 0, path cleared
2. `BuildOrderCommandHandler` with unresolvable fleet → error ValidationResult
3. `RemoveBuildOrderCommandHandler` with fleet having BUILD orders → all removed
4. `RemoveBuildOrderCommandHandler` with unresolvable fleet → error
5. `register()` produces 2 handler entries in a fresh `CommandRegistry`

---

### 2. `game/simulation/components/abilities/planetary/terraforming.py` (188 LOC) — CRITICAL → downgraded to MAJOR on discovery

**Phase 1 heuristic:** Marked Tier 0 (no tests). **Correction:** Tests exist at `tests/unit/simulation/components/abilities/test_terraforming_abilities.py` (67 LOC).

**Tested:** `AtmosphereModifierAbility` (lines 19-54) and `QualityImprovementAbility` (lines 57-100) — both with dict construction, defaults, `get_primary_value`, and `get_ui_rows`.

**Untested:**
- `GravityModifierAbility` (lines 103-150) — 6 methods: `__init__` (line 123), `get_primary_value` (line 135), `get_ui_rows` (line 138). No test coverage at all.
- `WaterModifierAbility` (lines 153-188) — 4 methods: `__init__` (line 170), `get_primary_value` (line 178), `get_ui_rows` (line 181). No test coverage at all.

**Risk:** These are Tier 0 simulation-layer abilities. `GravityModifierAbility` has activation/deactivation semantics (`energy_drain_rate`, `activation_time`, `deactivation_time`) — the non-default `data` branch in `__init__` is untested. `WaterModifierAbility` is a passive per-turn modifier.

**Suggested tests:**
1. `GravityModifierAbility` construction from dict with all fields
2. `GravityModifierAbility` defaults
3. `GravityModifierAbility.get_primary_value` and `get_ui_rows`
4. `WaterModifierAbility` construction from dict with `modification_rate`
5. `WaterModifierAbility` defaults, `get_primary_value`, `get_ui_rows`
6. Both abilities: non-dict `data` parameter (int, None-equivalent)

---

## Tier 1 — MAJOR

### 3. `game/simulation/validation/__init__.py` (36 LOC) — ADVISORY (not MAJOR)

**Status:** Pure re-export `__init__.py`. Re-exports 13 symbols from `base.py` and `ship_validator.py`.

**Risk:** None. The re-exports are verified transitively by tests that import from this package. Tests at `tests/unit/strategy/services/test_design_validator.py` exercise `ShipDesignValidator`.

**Verdict:** Downgrade to ADVISORY. No new testing warranted.

---

### 4. `game/strategy/engine/handlers/__init__.py` (72 LOC) — ADVISORY (not MAJOR)

**Status:** Pure re-export `__init__.py`. Imports from 6 sub-modules, re-exports 17 symbols. Factory function `create_default_registry` is imported from `registry_factory.py`.

**Risk:** None. All re-exported symbols are tested in their dedicated test files.

**Verdict:** Downgrade to ADVISORY. No new testing warranted.

---

## Tier 2 — PARTIAL COVERAGE (verified gaps)

### 5. `game/ai/spatial_behaviors/screen.py` (57 LOC) — MINOR

**Phase 1 claim:** `ScreenBehavior.__init__` untested. **Verified:** Tests at `tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py` exercise `compute_target_position` but do NOT directly test `__init__` with non-default `radius` and `reactivity` values.

- Line 30: `self.radius = radius` — only default 2000 tested via `compute_target_position`
- Line 31: `self.reactivity = reactivity` — not exercised in tests (affects AI decision-making, not position calculation)
- Line 49: `anchor_position is None` → returns `None` — exercised when `anchor_position` kwarg absent
- Line 52-56: `compute_circular_position` call with slot_index — exercised

**Gap:** Reactivity values ("active", "aggressive") have no behavioral test.

---

### 6. `game/research/data/tech_tree.py` (264 LOC) — MINOR

**Phase 1 claim:** `TechTree.__init__` untested. **Verified:** The constructor (line 25-27) initializes `self.nodes = {}` and `self._depth_cache = {}`. This is exercised by `TechTree.load_from_json()` (line 43: `tree = cls()`) and test files like `test_loading.py`.

**Actual gaps:**
- `get_all_node_ids` (line 183) — trivial list-key retrieval; indirectly exercised
- `calculate_depth` with nonexistent `node_id` (line 127-130) — returns 0 but code path not directly asserted
- `get_max_depth` with empty tree (line 167-168) — returns 0
- Comment-only entries in JSON (line 51-53) — `load_from_json` skips entries with `comment` but no `id`; test coverage unclear

**Test verification:** 7 test files including `test_cycle_detection.py` (~70 LOC), `test_queries.py`, `test_loading.py`, `test_validation.py`.

---

### 7. `game/simulation/combat/weapon_firing_system.py` (248 LOC) — MINOR

**Phase 1 claims untested:** `set_event_bus` (line 67), `_process_weapon_fire` (line 121), `_create_attack` (line 211)

**Verified coverage:** `tests/unit/simulation/combat/test_weapon_firing_system.py` (1273 LOC) is comprehensive.

- **`set_event_bus` (line 67):** NOT tested directly — no test calls `set_event_bus()` then verifies the bus is forwarded on `AttackRequest`. Tests construct `WeaponFiringSystem(targeting)` without a bus and `self._event_bus` remains `None`.
- **`_process_weapon_fire` (line 121):** HEAVILY exercised indirectly through `fire_weapons` tests. All code paths tested: cannot afford activation (line 142), cannot fire/cooldown (line 145), no valid target (line 149), fire fails (line 154), shot tracking (lines 158-159), attack creation (line 162).
- **`_create_attack` (line 211):** Exercised indirectly through family dispatch tests (BeamResolution, ProjectileResolution, NoAttack). Untested: `detect_family` returns `None` → returns `[]` (line 227).

**Gap:** Missing direct test of `set_event_bus` propagation into `AttackRequest.event_bus`.

---

### 8. `game/simulation/entities/ship_design_stats.py` (113 LOC) — COVERED (verify)

**Phase 1 claim:** fully covered (1 symbol, `calculate_design_stats`). **Verified:**
- 3 test files confirm coverage: `test_design_stats_no_fallback.py`, `test_ship_design_stats.py`, `test_ship_stats_cargo_storage.py`
- Edge cases that should be tested:
  - `component_toggles` path (line 50-58): `copy.deepcopy` + filtering
  - `components` dict with `current_hp < max_hp` (line 72-73): per-instance damage application
  - `is_active=False` components skipped in consumption collection (line 89)
  - Missing `"layers"` key or empty layers dict

**Verdict:** Well-covered. Potential minor gaps in error-path handling (malformed design_data).

---

### 9. `game/strategy/adapters/simulation_adapter.py` (549 LOC) — MAJOR

**Phase 1 claims untested:** `_run_simulated_battle`, `_build_assembly`, `_build_capture_context`

**Verified coverage from `tests/unit/strategy/adapters/test_simulation_adapter.py`:**
- `resolve_battle` with <2 fleets → `ValueError` (line 142)
- Shortcut paths: `sole_survivor` (line 168), `shortcut_no_ships` (line 193)
- `_resolve_seed` with and without seed (line 378-384)

**Verified gaps:**
- **`_run_simulated_battle` (line 245):** Tested indirectly through `resolve_battle` via integration tests. The `max_ticks` parameter path (line 254, issue #8 truncated no-capable) may not be exercised.
- **`_build_assembly` (line 386):** Tested indirectly. `modifiers` filter (line 411-414) — `None` values filtered out — may not be explicitly tested.
- **`_build_capture_context` (line 426):** The `_lookup` closure (line 488-495) has a `try/except Exception` path that is hard to hit. `ship_instance_lookup` returns `None` when instance absent or serialization fails. Fallback empire name "Unknown" (line 467) untested.
- **`_determine_winner` with multiple alive teams → `None`** (draw, line 525) — may not be tested
- **`BattleResolutionError` wrapping** (line 316-341): tested at `test_simulation_adapter_registry_threading.py`

---

### 10. `game/strategy/combat/post_battle_hook.py` (251 LOC) — MAJOR

**Phase 1 claims untested:** `_find_instance_by_id`, `_apply_single_outcome`, `_remove_ship`

**Verified coverage from `tests/unit/strategy/combat/test_post_battle_hook.py`:**
- `apply_outcome_to_fleets` main loop exercises `_find_instance_by_id` and `_apply_single_outcome` indirectly

**Actual untested paths:**
- **`_find_instance_by_id` with instance_id not found in any fleet** (line 133) → returns `(None, None)`. The warning log at line 99-105 is reached but not verified.
- **`_apply_single_outcome` with unknown ShipStatus** (line 171-174) — falls to warning log. Not tested.
- **`_remove_ship` with ValueError/AttributeError** from `fleet.remove_ship` (line 244-248) — catch logged via `logger.warning`. Not tested.
- **`_apply_survivor_outcome` with `outcome_max_hp <= 0`** (line 211-216) — falls back to `prior_max_hp`. Not explicitly tested.
- **`RETREATED` status path** (line 166-168) — removes ship, no HP update. May not be covered.

---

### 11. `game/strategy/combat/post_battle_hook_builder.py` (152 LOC) — MINOR

**Phase 1 claim untested:** `_mine_group_has_inventory` (line 150)

**Verified coverage from `test_post_battle_hook_builder.py`:**
- Tests exercise `build()` with mine_groups, engine_ref, owner_to_team_id

**Gap:** `_mine_group_has_inventory` is tested indirectly via the post-battle hook closure's mine-group prune loop (lines 135-145). However, direct assertion that `_mine_group_has_inventory` returns `True`/`False` for mine_groups with/without mines is missing.

**Untested edge cases:**
- `_hook` closure's reboard `try/except Exception` block (line 106) — intentionally broad catch, hard to trigger
- `_hook` closure's `TacticalMineResolver.writeback_to_mine_group` exception (line 124)
- `delattr(mg, "_tactical_resolver")` AttributeError catch (line 132)
- Empire without `deployed_groups` attribute (line 141-142)

---

### 12. `game/strategy/combat/strategy_modifier_stack_builder.py` (220 LOC) — MINOR

**Phase 1 claim untested:** `StrategyModifierStackBuilder._emit_team_scoped` (line 198)

**Verified:** `test_strategy_modifier_stack_builder.py` and `test_spec_compiler.py` test `entries_from_fleet_combat_modifiers` which calls `_emit_team_scoped` for `shield_mult`, `damage_mult`, and `flat_shield_bonus`. It IS tested indirectly.

**Actual gaps:**
- `entries_from_sector_effects` with `owner_id` not in `empire_to_team_id` (line 110-111) — `continue`, skips provider
- `entries_from_sector_effects` with multiple providers for same ability (line 93)
- `build` with empty environmental_effects/team_modifiers → returns `ModifierStack(per_team={}, global_=())`

---

### 13. `game/strategy/data/physics.py` (76 LOC) — MINOR

**Phase 1 claim untested:** `SectorEnvironment.__init__` (line 27)

**Verified:** `SectorEnvironment.calculate_radiation` delegates to `calculate_incident_radiation`. Tests at `test_radiation_physics.py` likely test `calculate_incident_radiation` directly. The `__init__` is trivial (assigns `self.local_hex` and `self.system`).

**Untested edge cases:**
- `calculate_incident_radiation` with empty stars list → returns zero-spectrum `Spectrum(0,0,0,0,0,0,0,0,0)`
- `calculate_incident_radiation` with `r < 1.0` → clamped to 1.0 (line 59)
- `hex_distance` returning 0 → clamped path exercised

---

### 14. `game/strategy/data/planet_gen_surface.py` (236 LOC) — MINOR

**Phase 1 claim untested:** `_get_planetary_ids` (line 38)

**Verified:** `_get_planetary_ids` is `@lru_cache(maxsize=1)` lazy loader consumed by `generate_resources`. Tests exercise it indirectly via planet generation test coverage at `test_planet_gen.py`.

**Actual untested paths:**
- `determine_planet_type` Chthonian probability branch (line 96-101): `random.random()` comparison
- `determine_planet_type` catch-all continental path (line 151-152)
- `generate_resources` with `earth_qty_norm <= 0` (line 205-206) — defensive guard
- `generate_resources` with `log_mass < cfg.min_log_mass` → sf_linear clamped to 0.001 (line 186)
- `generate_surface_flags` with `temp <= cfg.water_temp_min` (line 64-65) — frozen water
- `generate_surface_flags` with `mass <= MASS_MARS` (line 57-59) — small body

---

### 15. `game/strategy/engine/production_engine.py` (830 LOC) — MINOR

**Phase 1 claim untested:** `ProductionEngine._log_zero_consume_shortage` (line 726)

**Verified:** 16 test files cover this engine thoroughly.

**Gap:** `_log_zero_consume_shortage` is only called at line 720 when `zero_consume_resources` is non-empty during `_apply_resource_consumption`. This path is triggered when a fractional per-step cost rounds to 0 against an integer-typed cargo store. The `DI-2026-05-18-006` assertion at line 696 also guards the consumption contract — this assertion should have a test that exercises the `rounded_to_zero` event emission.

**Other potential gaps:**
- `_check_affordability` with `empire` parameter unused (line 571) — legacy ABI
- `_validate_tick_inputs` with `empire.resource_pool is None` (line 256-260)

---

### 16. `game/strategy/engine/order_handlers/recover_fighters.py` (296 LOC) — MAJOR

**Phase 1 claims untested:** `_run_with_issuer`, `_find_ship`, `_find_fighter_wing`, `_fighter_ship_to_carried_vehicle`

**Verified coverage from `test_recover_fighters_handler.py`:** These are all private helpers of the handler, tested indirectly through `execute_action_order` and `execute_for_issuer`.

**Actual untested code paths:**
- `_find_ship` with ship not in fleet → `None` (line 238-239)
- `_find_fighter_wing` with `fighter_group_id` not matching → continues loop → returns `None` (line 255)
- `_find_fighter_wing` with `g.location != hex_` → continues (line 256)
- `_run_with_issuer`: order `pop_order()` + event emission with `EventCategory.FLEET_OPERATIONS` (line 201-212)
- `_run_with_issuer`: `recovered == 0` → error message about bay capacity (line 214-221)
- `_fighter_ship_to_carried_vehicle`: `carriedVehicle` constructor raises `ValueError` → `None` (line 292-293)
- `_fighter_ship_to_carried_vehicle`: `ship.current_hp is None` (line 277)
- `_fighter_ship_to_carried_vehicle`: `ship.current_hp < 0` clamped to 0 (line 278-279)

---

### 17. `game/strategy/systems/race_library.py` (300 LOC) — MINOR

**Phase 1 claims untested:** `RaceLibrary.__init__`, `_ensure_folder_exists`, `CachedRaceRegistry.__init__`

**Verified:** `tests/unit/strategy/systems/test_race_library.py` tests `get_race`, `save_race`, `delete_race`. The init and internal helpers are exercised indirectly.

**Actual untested paths:**
- `RaceLibrary.__init__` with custom `races_folder` (non-None)
- `_ensure_folder_exists` PermissionError path (line 70-72)
- `_ensure_folder_exists` OSError path (line 73-75)
- `get_all_races` with missing folder (line 84-86)
- `get_all_races` glob empty (no .json files)
- `CachedRaceRegistry.invalidate(None)` — clear all (line 297)
- `CachedRaceRegistry.invalidate(race_id)` — clear specific (line 299)

---

### 18. `game/ui/panels/build_queue_portraits.py` (220 LOC) — ADVISORY (UI)

**Phase 1 claims untested:** `BuildQueuePortraitLoader.__init__`, `load_queue_item_portrait`, `_create_placeholder`, `_create_type_placeholder`

**Verified:** UI panel. The `__init__` stores callable `theme_id_supplier`. Tests at `test_build_queue_portraits.py` cover `load_design_portrait` path.

**Gap:** Missing test for `load_queue_item_portrait` with no matching design (fallback to `_create_type_placeholder`).

---

### 19. `game/ui/panels/builder_widgets.py` (292 LOC) — ADVISORY (UI)

**Phase 1 claims untested:** `ModifierEditorPanel.__init__`, `_get_modifiers`, `set_panel_height`, `_clear_scroll_container`, `_clear_all_rows`, `_ensure_row`, `_clear_extra_ui`

**Verified:** Tests at `test_builder_widgets.py` test `rebuild`, `layout`, `handle_event` paths. The untested methods are mostly cleanup/construction helpers exercised indirectly.

---

### 20. `game/ui/panels/design_stats_panel.py` (516 LOC) — ADVISORY (UI)

**Phase 1 claims untested:** `DesignStatsPanel._build_section`, `_update_requirements`

**Verified:** Tests at `test_design_stats_panel.py` exercise the panel. `_build_section` is called from `_build_sections` (line 249). `_update_requirements` likely renders requirement boxes.

**NOTE:** This file exceeds the 500 LOC ceiling (516 lines). This is a pattern violation (#31 in the pattern catalog).

---

### 21. `game/ui/panels/ship_detail_panel.py` (685 LOC) — ADVISORY (UI)

**Phase 1 claims untested:** `InstanceDamage`, `ComponentGroup`, `_compute_initial_expand_state`, `_add_section_header`, `_build_component_section`, `_build_layer_block`, `_build_group_block`, `_build_instance_row`, `_apply_strikethrough`

**Verified:** Tests at `test_ship_detail_panel.py` test the panel. `InstanceDamage` and `ComponentGroup` are dataclasses — tested via `group_components_by_id` pure function tests. The `_build_*` methods are UI construction helpers, tested via `update_ship` and manual inspection.

**NOTE:** This file FAR exceeds the 500 LOC ceiling (685 lines). Pattern violation.

---

### 22. `game/ui/panels/ship_stats_renderer.py` (440 LOC) — ADVISORY (UI)

**Phase 1 claims untested:** `draw_weapon_entry`, `draw_component_entry`, `draw_ship_info_header`, `draw_ship_vitals`, `draw_fleet_bonuses`, `draw_ship_weapons`, `draw_ship_components`

**Verified:** Pure rendering functions (Pygame `Surface.blit`). Tests at `test_ship_stats_renderer.py` test `draw_stat_bar`, `get_component_status_display`, `get_hp_bar_color`, `draw_ship_resources`. The untested functions are rendering-only.

---

### 23. `game/ui/screens/builder_utils.py` (94 LOC) — ADVISORY (UI)

**Phase 1 claims untested:** `PanelWidths`, `PanelHeights`, `calculate_center_width`, `calculate_dynamic_layer_width`, `calculate_bottom_panel_height`

**Verified:** `PanelWidths` and `PanelHeights` are frozen dataclass singletons with hardcoded values. The calculation functions are pure math. Simple utility module.

---

### 24. `game/ui/screens/cargo_quick_dialog.py` (330 LOC) — ADVISORY (UI)

**Phase 1 claims untested:** `CargoQuickDialogUiBuilder.build`, `_setup_ui`, `_apply_tooltips`, `_add_cargo_row`, `CargoQuickDialog._handle_keydown`

**Verified:** Tests at `test_cargo_quick_dialog.py` and sister files cover the dialog with mock UI builders. The production builder's methods may be tested indirectly or through integration.

---

### 25. `game/ui/screens/planet_list_controller.py` (48 LOC) — ADVISORY (UI)

**Phase 1 claims untested:** `PlanetListController.resolve_demographic_view`, `navigate_to`

**Verified:** Tests at `test_planet_list_window.py` cover the controller. `resolve_demographic_view` has two return paths: `None` when uncolonized/no facade, and `ColonyDemographicView` when colonized.

---

### 26. `game/ui/screens/save_selection_window.py` (473 LOC) — ADVISORY (UI)

**Phase 1 claims untested:** `SaveSelectionUiBuilder.build`, `SaveSelectionWindow._on_expand_clicked`, `_on_delete_clicked`, `_on_cancel_clicked`

**Verified:** Tests at `test_save_selection_window.py` cover window with mock builder. Event handlers are tested via `process_event`.

---

### 27. `game/ui/screens/strategy_screen.py` (539 LOC) — ADVISORY (UI)

**Phase 1 claims untested:** `_on_colonize_planet_selected`, `request_colonize_order`, `on_edit_order`, `_start_edit_move`, `complete_edit_move`, `_start_edit_transfer`, `calculate_hybrid_path`, `_get_system_at_hex`, `_find_nearest_system`

**Verified:** Tests at `test_strategy_screen.py` cover core lifecycle. These are UI orchestration methods. `calculate_hybrid_path` is a pure function possibly tested indirectly.

**NOTE:** Exceeds 300 LOC IScene budget at 539 lines.

---

### 28. `game/ui/screens/strategy_windows/planet_abilities_ctrl.py` (83 LOC) — ADVISORY (UI)

**Phase 1 claims untested:** `PlanetAbilitiesRegistrar._on_closed`, `open_editor`

**Verified:** Tests at `test_planet_abilities_window_lifecycle.py` exercise `open` and `_on_closed`.

---

## Tier 3 — APPARENTLY COVERED (verified)

### 29. `game/services/llm/background.py` (375 LOC) — CONFIRMED COVERED

Tests at `tests/unit/services/llm/test_background.py` comprehensively cover `LLMBackgroundCall` lifecycle (PENDING→RUNNING→DONE/ERROR/CANCELLED), `start()` idempotency, `cancel()`, `wait()`, `elapsed_seconds`, `MAX_CONCURRENT_CALLS` enforcement, and `shutdown_all_calls()`.

Edge case gaps (MINOR):
- `wait()` with `timeout=None` (blocks indefinitely, line 235) — testable with `threading.Event`
- `elapsed_seconds` before `start()` (line 241-242) → 0.0

---

### 30. `game/simulation/combat/families/seeker.py` (83 LOC) — CONFIRMED COVERED

Tests at `test_weapon_family_handlers.py` and `test_weapon_firing_system.py::TestSeekerWeaponFiring` cover SeekerHandler. The arc-check branch (line 45-50) and `event_bus` threading (line 61-62) tested via WeaponFiringSystem tests.

---

### 31. `game/simulation/entities/ship_design_stats.py` — CONFIRMED (see #8 above)

---

### 32. `game/ui/interfaces/battle_ui.py` (244 LOC) — CONFIRMED COVERED

Protocol + frozen DTOs. Tests at 5 files confirm IBattleUI conformance.

---

### 33. `game/ui/screens/race_asset_loader.py` (269 LOC) — CONFIRMED COVERED

Tests at `test_race_asset_loader.py` cover all public methods.

---

### 34. `game/ui/screens/workshop_viewmodel_ship_ops.py` (330 LOC) — CONFIRMED COVERED

Tests at `test_workshop_viewmodel_ship_ops.py` cover all CRUD + attribute-setter methods.

---

### 35. `game/strategy/generation/density/primitives/spiral_arm.py` (103 LOC) — CONFIRMED COVERED

Tests at `test_spiral_arm.py` cover `evaluate` with various center/distance/angle combinations.

---

### 36. `game/strategy/data/storm.py` (144 LOC) — CONFIRMED COVERED

Tests at `test_storm.py` cover `to_dict`, `from_dict`, `occupied_hexes`, and error paths in `from_dict` (missing keys, invalid location/hex_offsets, non-dict abilities). Well-covered.

---

### 37. `game/strategy/engine/order_handlers/registry_factory.py` (105 LOC) — CONFIRMED COVERED

Tests at `test_handler_registry_completeness.py` verify all `OrderType` values have registered handlers. The factory is tested via integration through `TurnEngineConfig.create_default()`.

---

---

## File Coverage Verification Table

| # | File | Tier | LOC | Status | Gaps |
|---|------|------|-----|--------|------|
| 1 | `game/ai/spatial_behaviors/screen.py` | 2 | 57 | MINOR | reactivity param untested |
| 2 | `game/research/data/tech_tree.py` | 2 | 264 | MINOR | edge: empty tree get_max_depth |
| 3 | `game/services/llm/background.py` | 3 | 375 | COVERED | minor edge: wait(None) |
| 4 | `game/simulation/combat/families/seeker.py` | 3 | 83 | COVERED | — |
| 5 | `game/simulation/combat/weapon_firing_system.py` | 2 | 248 | MINOR | set_event_bus not directly tested |
| 6 | `game/simulation/components/abilities/planetary/terraforming.py` | 0 | 188 | **MAJOR** | Gravity+Water abilities untested |
| 7 | `game/simulation/entities/ship_design_stats.py` | 3 | 113 | COVERED | — |
| 8 | `game/simulation/validation/__init__.py` | 1 | 36 | ADVISORY | re-export init |
| 9 | `game/strategy/adapters/simulation_adapter.py` | 2 | 549 | MAJOR | _run_simulated_battle max_ticks; _build_capture_context fallbacks |
| 10 | `game/strategy/combat/post_battle_hook.py` | 2 | 251 | MAJOR | unknown ShipStatus, RETREATED path, remove_ship catch |
| 11 | `game/strategy/combat/post_battle_hook_builder.py` | 2 | 152 | MINOR | reboard exception catch; writeback exception |
| 12 | `game/strategy/combat/strategy_modifier_stack_builder.py` | 2 | 220 | MINOR | _emit_team_scoped IS tested; sector effects ownerless path |
| 13 | `game/strategy/data/physics.py` | 2 | 76 | MINOR | empty stars list in calculate_incident_radiation |
| 14 | `game/strategy/data/planet_gen_surface.py` | 2 | 236 | MINOR | Chthonian RNG branch; frozen water branch |
| 15 | `game/strategy/data/storm.py` | 3 | 144 | COVERED | — |
| 16 | `game/strategy/engine/handlers/__init__.py` | 1 | 72 | ADVISORY | re-export init |
| 17 | `game/strategy/engine/handlers/build.py` | 0 | 97 | **CRITICAL** | NO tests — 2 handlers + register |
| 18 | `game/strategy/engine/order_handlers/recover_fighters.py` | 2 | 296 | MAJOR | error paths: no bay capacity; fighter_ship→cv ValueError |
| 19 | `game/strategy/engine/order_handlers/registry_factory.py` | 3 | 105 | COVERED | — |
| 20 | `game/strategy/engine/production_engine.py` | 2 | 830 | MINOR | _log_zero_consume_shortage directly; resource_pool None |
| 21 | `game/strategy/formulas/__init__.py` | 0 | 11 | ADVISORY | re-export init |
| 22 | `game/strategy/generation/density/primitives/spiral_arm.py` | 3 | 103 | COVERED | — |
| 23 | `game/strategy/systems/race_library.py` | 2 | 300 | MINOR | _ensure_folder_exists error paths; RaceLibrary custom path |
| 24 | `game/ui/interfaces/battle_ui.py` | 3 | 244 | COVERED | — |
| 25 | `game/ui/panels/build_queue_portraits.py` | 2 | 220 | ADVISORY | UI; fallback placeholder path |
| 26 | `game/ui/panels/builder_widgets.py` | 2 | 292 | ADVISORY | UI; cleanup helpers |
| 27 | `game/ui/panels/design_stats_panel.py` | 2 | 516 | ADVISORY | UI; exceeds 500 LOC ceiling |
| 28 | `game/ui/panels/ship_detail_panel.py` | 2 | 685 | ADVISORY | UI; exceeds 500 LOC ceiling |
| 29 | `game/ui/panels/ship_stats_renderer.py` | 2 | 440 | ADVISORY | UI; draw_* rendering fns |
| 30 | `game/ui/screens/atmosphere_target_editor.py` | 0 | 273 | ADVISORY | UI; NO tests — full pygme_gui window |
| 31 | `game/ui/screens/builder_utils.py` | 2 | 94 | ADVISORY | UI; layout singletons |
| 32 | `game/ui/screens/cargo_quick_dialog.py` | 2 | 330 | ADVISORY | UI; UiBuilder production methods |
| 33 | `game/ui/screens/planet_list_controller.py` | 2 | 48 | ADVISORY | UI; controller paths |
| 34 | `game/ui/screens/race_asset_loader.py` | 3 | 269 | COVERED | — |
| 35 | `game/ui/screens/save_selection_window.py` | 2 | 473 | ADVISORY | UI; event handlers via mock builder |
| 36 | `game/ui/screens/strategy_render/fleets.py` | 0 | 120 | ADVISORY | UI; NO tests - pure rendering |
| 37 | `game/ui/screens/strategy_screen.py` | 2 | 539 | ADVISORY | UI; exceeds 300 LOC IScene budget |
| 38 | `game/ui/screens/strategy_windows/planet_abilities_ctrl.py` | 2 | 83 | ADVISORY | UI; registrar lifecycle |
| 39 | `game/ui/screens/workshop_viewmodel_ship_ops.py` | 3 | 330 | COVERED | — |

---

## Phase 1 Data Corrections

| Phase 1 Claim | Correction |
|---------------|------------|
| `terraforming.py` — Tier 0, NO TESTS | **Wrong.** Tests exist covering Atmosphere + Quality. Missing Gravity + Water. Reclassify as MAJOR (partial). |
| `build.py` — Tier 0, NO TESTS | **Confirmed.** No test file exists. |
| `formulas/__init__.py` — Tier 0 | Re-export init. Downgrade to ADVISORY. |
| `simulation/validation/__init__.py` — Tier 1 | Re-export init. Downgrade to ADVISORY. |
| `engine/handlers/__init__.py` — Tier 1 | Re-export init. Downgrade to ADVISORY. |
| `StrModStackBuilder._emit_team_scoped` — untested | **Wrong.** Tested indirectly via `entries_from_fleet_combat_modifiers`. |

---

## Priority Remediation Plan

### CRITICAL (should be addressed this sprint)
1. **`game/strategy/engine/handlers/build.py`** — Write dedicated test file with 5 test cases covering both handlers + register function.

### MAJOR (address next sprint)
2. **`game/simulation/components/abilities/planetary/terraforming.py`** — Add tests for GravityModifierAbility and WaterModifierAbility (missing 2/4 ability classes).
3. **`game/strategy/adapters/simulation_adapter.py`** — Test `_run_simulated_battle` with `max_ticks` parameter; test `_build_capture_context` with orphan fleets.
4. **`game/strategy/combat/post_battle_hook.py`** — Test unknown ShipStatus path; test `_remove_ship` ValueError catch.
5. **`game/strategy/engine/order_handlers/recover_fighters.py`** — Test `_run_with_issuer` with full bay (recovered==0), `_fighter_ship_to_carried_vehicle` ValueError.

### MINOR (address when touching these files)
6. **`game/strategy/combat/post_battle_hook_builder.py`** — Test `_mine_group_has_inventory` directly; test empire without `deployed_groups`.
7. **`game/strategy/data/planet_gen_surface.py`** — Test Chthonian probability branch with seeded RNG.
8. **`game/simulation/combat/weapon_firing_system.py`** — Test `set_event_bus` propagation.
9. **`game/strategy/engine/production_engine.py`** — Test `_log_zero_consume_shortage` event emission path.
10. **`game/ui/panels/design_stats_panel.py`** — Split to drop below 500 LOC ceiling (currently 516).
11. **`game/ui/panels/ship_detail_panel.py`** — Split to drop below 500 LOC ceiling (currently 685).
12. **`game/ui/screens/strategy_screen.py`** — Split to drop below 300 LOC IScene budget (currently 539).
