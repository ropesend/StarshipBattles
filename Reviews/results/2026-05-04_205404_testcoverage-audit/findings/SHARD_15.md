# Shard 15 — Test Coverage Audit Report

**Shard:** 15  
**Files in scope:** 41 production files  
**Estimated LOC:** ~8,725  
**Date:** 2026-05-04  
**Auditor:** OpenCode Discovery Agent  
**Methodology:** Every production file exhaustively read; pre-computed coverage matrix consulted; gaps verified by cross-referencing known test files under `tests/`.

---

## Summary

| Category | Count | LOC |
|----------|-------|-----|
| **Tier 0 — No Tests (CRITICAL)** | 7 non-UI, 3 UI | 865 |
| **Tier 1 — Symbols Untested (MAJOR)** | 2 | 563 |
| **Tier 2 — Partial Coverage** | 18 | 6,479 |
| **Tier 3 — Apparently Covered** | 11 | 818 |

**Overall Shard Health:** MODERATE. Significant gaps in strategy-layer engines, UI rendering, and planetary ability coverage. Several Tier 0 files are new infrastructure with zero test coverage.

---

## CRITICAL — Tier 0 Non-UI (No Tests Exist)

### 1. `game/exit_dialog.py` (103 LOC, Tier 0)
**Symbols:** `draw_exit_dialog`, `handle_exit_dialog_click`, `handle_exit_dialog_cancel`

**No test file exists.** Three pygame-dependent functions that draw an exit confirmation dialog and handle Yes/No click detection. Uses module-level mutable globals (`_exit_yes_rect`, `_exit_no_rect`) — a state management anti-pattern (PROJ-258 violation).

**Risk:** CRITICAL. A reordering of code that breaks button hit detection would not be caught by any test.

### 2. `game/simulation/replay/replay_outcome.py` (49 LOC, Tier 0)
**Symbols:** `ReplayOutcome`, `ReplayOutcome.from_battle_outcome`, `ReplayOutcome.to_battle_outcome`, `ReplayOutcome.to_dict`, `ReplayOutcome.from_dict`

**No test file exists.** Frozen dataclass wrapping `BattleOutcome` for JSON-safe persistence with a schema version. Has `to_dict()`/`from_dict()` serialization that should be round-trip tested. `from_dict` casts `schema_version` via `str()` which could mask type errors.

**Risk:** CRITICAL. Serialization round-trip correctness is untested. `from_dict` could silently coerce a non-string version key.

### 3. `game/strategy/services/ability_sources/star.py` (69 LOC, Tier 0)
**Symbols:** `StarAbilitySource` (class + 9 properties/methods)

**No test file exists.** Implements `IAbilitySource` adapter for stars (PROJ-302). Contains coordinate math in `affects_hex()` with `try/except TypeError` fallback, offset math (`sys_loc + star_loc`), and duck-type attribute access throughout. Coordinated frame is system-global, not local — getting this wrong silently produces incorrect scope filtering.

**Risk:** CRITICAL. STAR_ABILITY_SOURCE is a core PROJ-302 infrastructure class with coordinate math. Untested `affects_hex` and `affects_system` could silently filter incorrectly, breaking system-level ability application for entire star systems.

### 4. `game/strategy/generation/density/__init__.py` (27 LOC, Tier 0)
**Symbols:** None (re-export only).

**ADVISORY** — Import-re-export `__init__.py` with `__all__`.

### 5. `game/strategy/generation/density/primitives/__init__.py` (23 LOC, Tier 0)
**Symbols:** None (re-export only).

**ADVISORY** — Import-re-export `__init__.py` with `__all__`.

### 6. `game/ui/screens/builder/components.py` (173 LOC, Tier 0)
**Symbols:** `ComponentListItem` (class + 7 methods/properties)

**No test file exists.** Heavy pygame_gui widget construction (`UIPanel`, `UIButton`, `UILabel`, `UIImage`) plus dynamic mass calculation via `component.clone()`. Contains custom tooltip HTML generation logic and selection/hover state management. Over 500 LOC across callers depend on this widget.

**Risk:** CRITICAL. `_generate_tooltip` contains complex HTML generation with ability-based branching and a hardcoded `shown_abilities` set — a regression here could break all component display in the workshop builder.

### 7. `game/ui/screens/strategy_windows/orders_window_ctrl.py` (111 LOC, Tier 0)
**Symbols:** `OrdersRegistrar`, `OrdersRegistrar.__init__`, `OrdersRegistrar.open`

**No test file exists.** Closure-capture pattern for command dispatch on fleet/planet orders. Branches on `entity_type` ("fleet" vs "planet") to define three different callback closures. Location of `facade.handle_command` in closure scope is critical — if `facade` is rebound after capture, commands silently go to stale instance.

**Risk:** CRITICAL. Closure-capture lifetime bugs are hard to diagnose. The comment warns "The closures bind the local `facade` and `owner_id` names so the captured values are stable even if the scene's facade attribute is later rebound" — but there's no test verifying this contract.

### 8. `game/ui/screens/test_lab/details/draw_context.py` (62 LOC, Tier 0)
**Symbols:** `DetailsDrawContext`, `OutcomePalette`

**No test file exists.** Two frozen dataclasses that bundle fonts, colors, and geometry for the Combat Lab test-run-details sub-renderers. Pure data carriers — low risk, but a missing field would cause `AttributeError` at render time.

**Risk:** ADVISORY. Data-carrier dataclasses. Should at minimum verify construction + field count.

### 9. `game/ui/screens/test_lab/renderer/metadata_panel.py` (221 LOC, Tier 0)
**Symbols:** `MetadataPanel`, `MetadataPanel.__init__`, `MetadataPanel.draw`, `MetadataPanel._draw_run_buttons`

**No test file exists.** Renders the Combat Lab Test Details panel with Visual Run / Headless Run / Visual Baseline buttons. Complex rendering with hover-state coloring, conditional button display (baseline button only for `is_comparison` scenarios), and dynamic validation result display. Writes button rects onto `viewmodel` for click detection.

**Risk:** CRITICAL. The `_draw_run_buttons` method has hover-state logic for 3 button types plus conditional baseline button display — all untested. Button hover detection depends on `pygame.mouse.get_pos()` which cannot be tested without rendering, but the rect-calculation logic (position computation, branching on `is_comparison`) should be extractable and testable.

### 10. `game/ui/screens/transfer_grid_renderer.py` (366 LOC, Tier 0)
**Symbols:** `TransferGridRenderer` (class + 8 methods), `TransferDialogUiBuilder` (class + 1 method)

**No test file exists.** Builds the entire TransferDialog widget tree — source/target dropdowns, filter button, scrolling grid container with per-row arrow buttons (10 per row: 5 load + 5 drop), max/zero buttons, pending labels, and bottom confirm/clear/cancel buttons. This is the largest untested UI file in the shard at 366 LOC.

**Risk:** CRITICAL. The grid building logic (`_add_row`) constructs 15+ pygame_gui widgets per row with pixel-position math. Arrow button increment lists differ between load/drop directions. A layout regression would silently break the entire transfer UI.

---

## MAJOR — Tier 1 (No Symbols Tested)

### 11. `game/simulation/interfaces/__init__.py` (128 LOC, Tier 1)
**Symbols:** 0 (re-export file). **ADVISORY.** Import-only package init. The underlying modules (`ability_protocols.py`, `component_protocols.py`, `entity_protocols.py`, `ai_controller.py`) have their own test coverage. This file itself needs no direct tests.

### 12. `game/ui/panels/battle_panels.py` (563 LOC, Tier 1)
**Symbols:** 35 total, **ALL UNTESTED**
- `BattlePanel` (class + 5 methods) — main panel, stat bars, ship listing
- `ExpandableIdPanel` (class + 3 methods) — ID expansion toggle
- `ShipStatsPanel` (class + 9 methods) — ship stats display with expandable details
- `SeekerMonitorPanel` (class + 9 methods) — projectile tracking monitor
- `BattleControlPanel` (class + 3 methods) — control buttons

**563 LOC, ZERO SYMBOLS TESTED.** This is the largest completely untested production file in the shard (and is at 563 LOC, exceeding the 500-line ceiling). It is a Tier 1 matrix entry (some test files mention it, but no symbols match). The file renders ship stat panels, seeker monitors, and battle controls — core battle UI.

**Risk:** MAJOR. Battle UI with stat calculation display, expandable panels, scroll-state management, seeker projectile tracking, and control buttons. A regression here silently breaks the battle HUD.

---

## MAJOR — Tier 2 Partial Coverage

### 13. `game/simulation/components/abilities/planetary.py` (913 LOC, Tier 2)
**72 symbols, 50 tested, 22 untested**
All 22 untested are `__init__` methods of ability classes:
- `PlanetaryShieldAbility.__init__`, `StrategicResourceGenerationAbility.__init__`, `GeologicStabilizerAbility.__init__`, `StellarStabilizerAbility.__init__`, `WarpFieldStabilizerAbility.__init__`, `ResourceHarvestBoosterAbility.__init__`, `BuildRateBoosterAbility.__init__`, `AtmosphereModifierAbility.__init__`, `ShieldModifierAbility.__init__`, `DamageModifierAbility.__init__`, `QualityImprovementAbility.__init__`, `GravityModifierAbility.__init__`, `WaterModifierAbility.__init__`, `RadiationShieldAbility.__init__`, `ThrustModifierAbility.__init__`, `StrategicSpeedModifierAbility.__init__`, `EnvironmentalDamageAbility.__init__`, `FuelDrainAbility.__init__`
Plus: `ThrustModifierAbility`, `StrategicSpeedModifierAbility`, `EnvironmentalDamageAbility`, `FuelDrainAbility` (class symbols themselves not directly tested).

**Analysis:** The `__init__` methods all follow an identical pattern: `super().__init__()` + data-extraction with defaults. These are exercised whenever an ability instance is constructed in any test that exercises `get_primary_value()` or `get_ui_rows()`. The four PROJ-300 storm-style abilities (ThrustModifier, StrategicSpeedModifier, EnvironmentalDamage, FuelDrain) are new additions that may not have dedicated tests yet.

**Risk:** MINOR-MAJOR. The 22 `__init__` gaps are mostly false positives (tested indirectly via construction). However, the 4 PROJ-300 abilities (ThrustModifierAbility, StrategicSpeedModifierAbility, EnvironmentalDamageAbility, FuelDrainAbility, lines 777–913) should have dedicated construction + value tests since they feed into the IAbilitySource framework.

### 14. `game/simulation/components/component_health_manager.py` (102 LOC, Tier 2)
**5 symbols, 4 tested, 1 untested:** `ComponentHealthManager.__init__`

**Risk:** MINOR. `__init__` is exercised whenever the manager is constructed in tests. The core logic (`take_damage`, `reset_hp`, `hp_ratio`) is tested.

### 15. `game/simulation/systems/resource_manager.py` (208 LOC, Tier 2)
**22 symbols, 13 tested, 9 untested:**
- `ResourceState.__init__`, `ResourceState.has_sufficient`, `ResourceState.add`, `ResourceState.set_max` (untested ResourceState methods)
- `ResourceRegistry.__init__`, `ResourceRegistry.set_max_value`, `ResourceRegistry.set_regen_rate`, `ResourceRegistry.get_resource_names`, `ResourceRegistry.get_all_resources` (untested registry methods)

**Analysis:** ResourceRegistry's `set_max_value` creates new ResourceState entries when the resource doesn't exist (fallback to `register_storage`) — a different behavior from `set_regen_rate` which silently does nothing for missing resources. This asymmetric behavior should be tested.

**Risk:** MAJOR. ResourceState has 4 untested methods including `add` (resource addition with clamping) and `set_max` (max reduction + current clamping). ResourceRegistry's `get_resource_names` and `get_all_resources` return the mutable dict's view — external callers could mutate it (returns `list(self._resources.keys())` which is safe, but `get_all_resources` returns `list(self._resources.values())` — ResourceState objects are mutable).

### 16. `game/strategy/combat/post_battle_hook.py` (201 LOC, Tier 2)
**6 symbols, 1 tested, 5 untested:**
- `_find_instance_by_id` — linear scan O(n*m) lookup
- `_apply_single_outcome` — dispatches on `ShipStatus` enum (4 branches: SURVIVED/DERELICT/DESTROYED/RETREATED/unknown)
- `_apply_survivor_outcome` — reconstructs `ComponentState` dict from outcome, updates `is_alive`/`is_derelict`/`battles_survived`
- `_remove_ship` — calls `fleet.remove_ship()` with try/except
- `_prune_empty_fleets` — cleans up empty fleets from empires

Only `apply_outcome_to_fleets` (the public entry) has a test match.

**Risk:** MAJOR. The private helpers implement the actual outcome-to-instance state transfer — component HP round-trip, fleet pruning, and ship removal. Only the public entry is tested. A regression in `_apply_survivor_outcome`'s `ComponentState` reconstruction (e.g., missing `prior_max_hp` key) would corrupt ship state across battles.

### 17. `game/strategy/data/classification_config.py` (173 LOC, Tier 2)
**5 symbols, 2 tested, 3 untested:**
- `ClassificationConfig.__init__` — JSON vs default dispatch
- `ClassificationConfig._load_from_json` — 4 subsections, 21 attribute assignments
- `ClassificationConfig._use_defaults` — 21 attribute assignments

Only `ClassificationConfig` and `get_classification_config` are tested.

**Risk:** MAJOR. `_load_from_json` handles 4 subsections (mass, temperature, pressure, water) + chthonian_stripping with 21 attribute assignments using `.get()` fallbacks to `DEFAULT_*` dicts. A missing key in astrophysics.json could silently use defaults that differ from intent. `_use_defaults` is the fallback path for when JSON loading fails — should be tested to verify that all required attributes are set.

### 18. `game/strategy/engine/atmosphere_engine.py` (147 LOC, Tier 2)
**6 symbols, 3 tested, 3 untested:**
- `AtmosphereEngine.__init__`
- `AtmosphereEngine._process_colony` — core atmosphere modification logic with multi-gas deltas
- `AtmosphereEngine._extract_atmo_modifier` — ability extraction with registry lookup

Only `process_atmosphere`, `_validate_tick_inputs`, and `AtmosphereEngine` itself are tested.

**Risk:** MAJOR. `_process_colony` contains the core formula: mass/pressure conversion, gas-by-gas delta computation, proportional modification rate distribution, non-overshoot clamping, and surface_pressure recalculation. The `pa_per_kg = gravity / surface_area` formula is inverted from the module docstring's `mass_kg = pressure_Pa * surface_area_m2 / gravity_ms2` — this should be verified with tests. `_extract_atmo_modifier` handles both dict and list return types from `extract_abilities_from_component`.

### 19. `game/strategy/engine/population_engine.py` (176 LOC, Tier 2)
**8 symbols, 6 tested, 2 untested:**
- `PopulationEngine._process_empire`
- `PopulationEngine._process_colony`

Both are simple iteration delegates that call `_grow_species` (which IS tested). However, `_process_colony` iterates `colony.populations` — if the list contains non-SpeciesPopulation objects, `_grow_species` will fail deep inside with an AttributeError on `pop.count`.

**Risk:** MINOR. The delegation methods are thin wrappers iterating collections. `_grow_species` has comprehensive formula coverage including the PROJ-284 logistic growth + starvation-decline terms.

### 20. `game/strategy/generation/placement_strategies.py` (210 LOC, Tier 2)
**7 symbols, 6 tested, 1 untested:** `DensityBasedPlacementStrategy.__init__`

**Risk:** MINOR. `__init__` is trivial (stores density_map reference). The `sample_location` method is tested and contains the complex rejection-sampling logic.

### 21. `game/strategy/services/cargo_transfer_service.py` (300 LOC, Tier 2)
**8 symbols, 7 tested, 1 untested:** `_extract_population_items`

**Risk:** MINOR. `_extract_population_items` is a private helper that extracts population items from `PlanetInfo`. Tested indirectly through `CargoTransferService.get_load_items()` and `CargoTransferService.get_inventory_items()` which call it.

### 22. `game/ui/effects/hit_effects.py` (233 LOC, Tier 2)
**12 symbols, 11 tested, 1 untested:** `HitEffect.update`

**Risk:** MINOR. `update` is a one-liner (`self.elapsed += dt`) exercised whenever `update_effects()` is called in tests.

### 23. `game/ui/panels/race_summary_panel.py` (733 LOC, Tier 2)
**25 symbols, 13 tested, 12 untested:**
- `_create_left_column_content` (197 LOC), `_create_environment_column`, `_create_ship_theme_strip` — UI construction
- `_format_race_summary`, `_format_physical_summary`, `_format_society_summary`, `_format_homeworld_summary` — formatting
- `_render_section_header`, `_render_env_row`, `_render_aptitude_rows` — rendering helpers
- `_refresh_flag_preview`, `_refresh_portrait_preview` — image refresh

**Risk:** MAJOR. At 733 LOC, this file significantly exceeds the 500-line ceiling. The 12 untested methods are all private helpers that compose the panel's content. `_create_left_column_content` at 197 LOC is a large method with precise pixel-position layout that is completely untested. The formatting methods (`_format_race_summary`, `_format_physical_summary`, `_format_society_summary`, `_format_homeworld_summary`) contain simple string formatting but have null/fallback handling that should be tested.

### 24. `game/ui/research/research_scene.py` (401 LOC, Tier 2)
**15 symbols, 14 tested, 1 untested:** `ResearchTreeScene._calculate_layout`

**Risk:** MINOR. Layout calculation with depth-based column positioning. Tested indirectly since the scene is constructed in tests.

### 25. `game/ui/screens/builder/grouping_strategies.py` (79 LOC, Tier 2)
**9 symbols, 1 tested, 8 untested:**
- `GroupingStrategy` (Protocol), `GroupingStrategy.group_components` — protocol
- `DefaultGroupingStrategy`, `DefaultGroupingStrategy.group_components` — ID+modifier grouping
- `TypeGroupingStrategy`, `TypeGroupingStrategy.group_components` — type-only grouping
- `FlatGroupingStrategy`, `FlatGroupingStrategy.group_components` — individual grouping

Only `get_component_group_key` has a test match.

**Risk:** MAJOR. Three grouping strategies with different key-generation logic — all untested. `DefaultGroupingStrategy` uses modifier comparison with readonly-filtering, which is essential for correct component display in the workshop structure panel. The `get_component_group_key` function being tested alone does not verify the strategy classes.

### 26. `game/ui/screens/builder/panel_layout_config.py` (71 LOC, Tier 2)
**4 symbols, 2 tested, 2 untested:**
- `ComponentItemContext.__post_init__`
- `StructurePanelLayoutConfig.__post_init__`

**Risk:** MINOR. `__post_init__` methods set default config objects. Neglecting to set `ANCHOR_TOP_LEFT`/`ANCHOR_TOP_RIGHT` (which are class-level None defaults initialized in `__post_init__`) would cause `None` anchors — reasonable to test.

### 27. `game/ui/screens/empire_panel_window.py` (572 LOC, Tier 2)
**19 symbols, 4 tested, 15 untested:**
- `EmpirePanelUiBuilder.build` — widget builder
- `EmpirePanelWindow._create_ui`, `_create_tab_buttons`, `_create_tab_panels` — UI shell
- `_build_treasury_tab`, `_build_population_tab`, `_build_placeholder_tab` — tab content
- `_render_species_card`, `_render_portrait_flag_row`, `_render_identity_section`, `_render_aptitudes_section`, `_render_environment_section`, `_render_descriptions_section` — render helpers
- `process_event`, `kill` — lifecycle

At 572 LOC, exceeds the 500-line ceiling. Only 4 symbols tested: `EmpirePanelWindow`, `EmpirePanelUiBuilder`, `__init__`, and `_show_tab`.

**Risk:** MAJOR. Core empire UI with 3 tabs (Treasury, Population, More), asset loading (flag/portrait), and scrolling content. `_build_treasury_tab` instantiates `EmpireEconomyService` and `EmpireTreasuryPanel` — untested integration chain. `_render_environment_section` reads `race_config.preferences` dictionary with `.get()` calls that can return None — the formatting f-strings would crash on None attributes.

### 28. `game/ui/screens/strategy_input_handler.py` (207 LOC, Tier 2)
**9 symbols, 8 tested, 1 untested:** `StrategyInputHandler._handle_keydown`

**Risk:** MINOR. `_handle_keydown` is a 2-line dispatcher that calls `_handle_keydown_mapped` if mapper exists. Tested indirectly through the main `handle_event` path.

### 29. `game/ui/screens/workshop_viewmodel.py` (494 LOC, Tier 2)
**49 symbols, 44 tested, 5 originally reported, but only 1 actually untested:** `WorkshopViewModel._with_ship`

**Analysis:** `_with_ship` is tested indirectly — it's called by every delegated ship op method. The gap is a false positive. 44/49 tested is excellent coverage for a ViewModel of this size.

**Risk:** MINOR. False positive.

### 30. `game/ui/widgets/scrollable_json_panel.py` (412 LOC, Tier 2)
**15 symbols, 10 tested, 5 untested:**
- `_add_key_value_line_with_diff` — diff-highlighted key:value line appending
- `_add_value_line_with_diff` — diff-highlighted value line appending
- `_get_scrollbar_thumb_rect` — scrollbar geometry computation
- `draw` — 60+ line rendering method
- `_draw_scrollbar` — scrollbar rendering

**Risk:** MAJOR. `draw` and `_draw_scrollbar` are the main rendering paths — 80+ lines of pygame blitting with clipping, mixed-color text rendering, and scroll offset math. `_add_key_value_line_with_diff` and `_add_value_line_with_diff` contain the diff-highlight logic that determines color overrides. Untested rendering could produce visual regressions.

### 31. `game/ui/widgets/ui_element_registry.py` (62 LOC, Tier 2)
**7 symbols, 4 tested, 3 untested:**
- `UIElementRegistry.__init__`
- `UIElementRegistry.__len__`
- `UIElementRegistry.__iter__`

**Risk:** MINOR. The three untested items are trivial: `__init__` sets `self._elements = []`, `__len__` returns `len()`, and `__iter__` delegates to `iter()`. The core logic (`register`, `kill_all`, `clear`) is tested.

---

## Tier 3 — Apparently Covered

### 32. `game/ai/spatial_behaviors/__init__.py` (66 LOC, Tier 3)
1 symbol, 1 tested. `create_spatial_behavior` factory with registry fallback to FreeManeuverBehavior.

### 33. `game/engine/spatial.py` (61 LOC, Tier 3)
7 symbols, 7 tested. SpatialGrid with cell-based bucketing, broad-phase and exact-distance queries.

### 34. `game/simulation/battle_spec.py` (232 LOC, Tier 3)
8 frozen dataclass symbols, 8 tested. The battle spec contract is well-covered.

### 35. `game/simulation/entities/layer_data.py` (112 LOC, Tier 3)
4 symbols, 4 tested. LayerData typed structure with factory methods.

### 36. `game/strategy/engine/construction_forecast.py` (95 LOC, Tier 3)
1 symbol, 1 tested. `forecast_queue_turn_spend` with carry-over capacity.

### 37. `game/strategy/services/fleet_cargo_projector.py` (64 LOC, Tier 3)
2 symbols, 2 tested. Fleet cargo projection through queued order simulation.

### 38. `game/ui/interfaces/battle_ui.py` (244 LOC, Tier 3)
12 symbols (4 frozen dataclasses + 1 Protocol + 7 methods), all tested. Battle UI protocol and DTOs.

### 39. `game/ui/screens/build_queue_helpers.py` (205 LOC, Tier 3)
4 symbols, 4 tested. Build queue formatting and spend calculation.

### 40. `game/ui/screens/__init__.py` (0 LOC, Tier 1)
Empty file. **ADVISORY.**

### 41. `game/ui/utils/__init__.py` (57 LOC, Tier 1)
Re-export file. **ADVISORY.**

---

## File Coverage Verification Table

| # | File | LOC | Tier | Symbols | Tested | Tests Found | Status |
|---|------|-----|------|---------|--------|-------------|--------|
| 1 | `game/ai/spatial_behaviors/__init__.py` | 66 | 3 | 1 | 1 | 1 | COVERED |
| 2 | `game/engine/spatial.py` | 61 | 3 | 7 | 7 | 8 | COVERED |
| 3 | `game/exit_dialog.py` | 103 | 0 | 3 | 0 | 0 | **CRITICAL** |
| 4 | `game/simulation/battle_spec.py` | 232 | 3 | 8 | 8 | 20 | COVERED |
| 5 | `game/simulation/components/abilities/planetary.py` | 913 | 2 | 72 | 50 | 6 | PARTIAL |
| 6 | `game/simulation/components/component_health_manager.py` | 102 | 2 | 5 | 4 | 1 | PARTIAL |
| 7 | `game/simulation/entities/layer_data.py` | 112 | 3 | 4 | 4 | 20 | COVERED |
| 8 | `game/simulation/interfaces/__init__.py` | 128 | 1 | 0 | 0 | 2 | ADVISORY |
| 9 | `game/simulation/replay/replay_outcome.py` | 49 | 0 | 5 | 0 | 0 | **CRITICAL** |
| 10 | `game/simulation/systems/resource_manager.py` | 208 | 2 | 22 | 13 | 5 | PARTIAL |
| 11 | `game/strategy/combat/post_battle_hook.py` | 201 | 2 | 6 | 1 | 1 | **MAJOR** |
| 12 | `game/strategy/data/classification_config.py` | 173 | 2 | 5 | 2 | 1 | **MAJOR** |
| 13 | `game/strategy/engine/atmosphere_engine.py` | 147 | 2 | 6 | 3 | 2 | **MAJOR** |
| 14 | `game/strategy/engine/construction_forecast.py` | 95 | 3 | 1 | 1 | 1 | COVERED |
| 15 | `game/strategy/engine/population_engine.py` | 176 | 2 | 8 | 6 | 4 | PARTIAL |
| 16 | `game/strategy/generation/density/__init__.py` | 27 | 0 | 0 | 0 | 0 | ADVISORY |
| 17 | `game/strategy/generation/density/primitives/__init__.py` | 23 | 0 | 0 | 0 | 0 | ADVISORY |
| 18 | `game/strategy/generation/placement_strategies.py` | 210 | 2 | 7 | 6 | 1 | PARTIAL |
| 19 | `game/strategy/services/ability_sources/star.py` | 69 | 0 | 9 | 0 | 0 | **CRITICAL** |
| 20 | `game/strategy/services/cargo_transfer_service.py` | 300 | 2 | 8 | 7 | 1 | PARTIAL |
| 21 | `game/strategy/services/fleet_cargo_projector.py` | 64 | 3 | 2 | 2 | 1 | COVERED |
| 22 | `game/ui/effects/hit_effects.py` | 233 | 2 | 12 | 11 | 1 | PARTIAL |
| 23 | `game/ui/interfaces/battle_ui.py` | 244 | 3 | 12 | 12 | 5 | COVERED |
| 24 | `game/ui/panels/battle_panels.py` | 563 | 1 | 35 | 0 | 1 | **MAJOR** |
| 25 | `game/ui/panels/race_summary_panel.py` | 733 | 2 | 25 | 13 | 1 | **MAJOR** |
| 26 | `game/ui/research/research_scene.py` | 401 | 2 | 15 | 14 | 8 | PARTIAL |
| 27 | `game/ui/screens/__init__.py` | 0 | 1 | 0 | 0 | 7 | ADVISORY |
| 28 | `game/ui/screens/build_queue_helpers.py` | 205 | 3 | 4 | 4 | 1 | COVERED |
| 29 | `game/ui/screens/builder/components.py` | 173 | 0 | 7 | 0 | 0 | **CRITICAL** |
| 30 | `game/ui/screens/builder/grouping_strategies.py` | 79 | 2 | 9 | 1 | 1 | **MAJOR** |
| 31 | `game/ui/screens/builder/panel_layout_config.py` | 71 | 2 | 4 | 2 | 2 | PARTIAL |
| 32 | `game/ui/screens/empire_panel_window.py` | 572 | 2 | 19 | 4 | 1 | **MAJOR** |
| 33 | `game/ui/screens/strategy_input_handler.py` | 207 | 2 | 9 | 8 | 6 | PARTIAL |
| 34 | `game/ui/screens/strategy_windows/orders_window_ctrl.py` | 111 | 0 | 3 | 0 | 0 | **CRITICAL** |
| 35 | `game/ui/screens/test_lab/details/draw_context.py` | 62 | 0 | 2 | 0 | 0 | **CRITICAL** |
| 36 | `game/ui/screens/test_lab/renderer/metadata_panel.py` | 221 | 0 | 4 | 0 | 0 | **CRITICAL** |
| 37 | `game/ui/screens/transfer_grid_renderer.py` | 366 | 0 | 10 | 0 | 0 | **CRITICAL** |
| 38 | `game/ui/screens/workshop_viewmodel.py` | 494 | 2 | 49 | 44 | 5 | PARTIAL |
| 39 | `game/ui/utils/__init__.py` | 57 | 1 | 0 | 0 | 1 | ADVISORY |
| 40 | `game/ui/widgets/scrollable_json_panel.py` | 412 | 2 | 15 | 10 | 1 | **MAJOR** |
| 41 | `game/ui/widgets/ui_element_registry.py` | 62 | 2 | 7 | 4 | 1 | PARTIAL |

---

## Priority Remediation Plan

### Immediate (CRITICAL — missing test files for non-UI code):

1. **`game/simulation/replay/replay_outcome.py`** — Write `tests/unit/simulation/replay/test_replay_outcome.py`:
   - Round-trip: `ReplayOutcome.from_battle_outcome(outcome).to_battle_outcome() == outcome`
   - Serialization round-trip: `ReplayOutcome.from_dict(x.to_dict()) == x`
   - `from_dict` with non-string `schema_version`
   - `to_dict` output schema validation

2. **`game/strategy/services/ability_sources/star.py`** — Write `tests/unit/strategy/services/ability_sources/test_star_ability_source.py`:
   - Construction with mock star/system
   - `affects_hex` with coordinate math (verify global offset: `sys_loc + star_loc`)
   - `affects_hex` with None location/system (returns False)
   - `affects_hex` with TypeError path
   - `affects_system` identity check
   - `get_abilities` with None intrinsic_abilities
   - `source_kind`, `source_label`, `source_id`, `owner_id` property tests
   - `get_activation_state` returns None

3. **`game/exit_dialog.py`** — Write `tests/unit/ui/test_exit_dialog.py`:
   - `draw_exit_dialog` with mock screen/fonts → verify button rects set
   - `handle_exit_dialog_click` inside/outside Yes rect
   - `handle_exit_dialog_cancel` inside/outside No rect
   - Verify globals reset between calls (state leak risk)

4. **`game/ui/screens/strategy_windows/orders_window_ctrl.py`** — Write `tests/unit/ui/screens/strategy_windows/test_orders_window_ctrl.py`:
   - `open` with fleet entity → verify fleet closures created
   - `open` with planet entity → verify planet closures created
   - `open` with existing window → verify old killed first
   - Closure-capture: rebind `scene.facade` after capture, verify closures still reference captured instance

### High Priority (MAJOR — partial coverage with untested core logic):

5. **`game/strategy/combat/post_battle_hook.py`** — Full unit tests for private helpers:
   - `_find_instance_by_id` with matching/non-matching/empty fleets
   - `_apply_single_outcome` all 4 ShipStatus branches + unknown status
   - `_apply_survivor_outcome` with/without prior_max_hp
   - `_remove_ship` normal + ValueError fallback
   - `_prune_empty_fleets` with/without empires dict, with/without empire_fleets attribute

6. **`game/strategy/data/classification_config.py`** — Test both init paths:
   - `_load_from_json` with full/partial/empty classification section
   - `_use_defaults` → verify all 21 attributes set to correct DEFAULT values

7. **`game/strategy/engine/atmosphere_engine.py`** — Test core formula:
   - `_process_colony` with no target → early return
   - `_process_colony` with single gas modification
   - `_process_colony` with multi-gas proportional distribution
   - `_process_colony` with zero surface_area/gravity → early return
   - `_extract_atmo_modifier` with dict/list/None returns
   - Verify `pa_per_kg` formula matches `mass_kg = pressure * area / gravity`

8. **`game/ui/panels/battle_panels.py`** — Critical: this entire 563 LOC file has ZERO tested symbols. Needs a comprehensive test suite covering at minimum:
   - `BattlePanel.draw_stat_bar` with various HP ratios
   - `ShipStatsPanel.draw` with expand/collapse states
   - `SeekerMonitorPanel.add_seeker` and `clear_inactive`
   - `BattleControlPanel` button state rendering
   - Consider extracting stat-bar drawing into pure functions for testability

9. **`game/ui/screens/empire_panel_window.py`** — Test rendering helpers:
   - `_render_environment_section` with None preferences entry (crash risk)
   - `_render_aptitudes_section` with 3-column layout
   - `_render_identity_section` with various missing fields
   - `_build_treasury_tab` service integration chain

### Medium Priority (MINOR — missing branch/error-path coverage):

10. `game/simulation/systems/resource_manager.py` — Test `ResourceState.add` clamping, `set_max` reduction behavior, `get_resource_names`/`get_all_resources` return values
11. `game/simulation/components/abilities/planetary.py` — Dedicated tests for 4 PROJ-300 storm abilities (ThrustModifierAbility, StrategicSpeedModifierAbility, EnvironmentalDamageAbility, FuelDrainAbility)
12. `game/ui/screens/builder/grouping_strategies.py` — Tests for DefaultGroupingStrategy, TypeGroupingStrategy, FlatGroupingStrategy
13. `game/ui/widgets/scrollable_json_panel.py` — Test `_add_key_value_line_with_diff`, `_add_value_line_with_diff` with all diff statuses
14. `game/ui/panels/race_summary_panel.py` — Test formatting methods with edge cases (None race_config fields)
15. `game/ui/screens/transfer_grid_renderer.py` — Extract `_add_row` logic for testability

### Low Priority (ADVISORY):

16. `__init__.py` files (items #4, #5, #8, #27, #39) — re-export modules; accept zero coverage
17. `game/ui/screens/test_lab/details/draw_context.py` — data-carrier dataclasses; verify field count
18. `game/ui/screens/test_lab/renderer/metadata_panel.py` — extract button rect calculation for unit testing

---

## Structural Observations

### LOC Ceiling Violations (>500 lines):
- `game/simulation/components/abilities/planetary.py` — 913 LOC (ceiling: 500)
- `game/ui/panels/race_summary_panel.py` — 733 LOC (ceiling: 500)
- `game/ui/panels/battle_panels.py` — 563 LOC (ceiling: 500)
- `game/ui/screens/empire_panel_window.py` — 572 LOC (ceiling: 500)

### Files With Zero Test Coverage (Tier 0 — needs test file created):
10 files total, ~865 LOC untested:
- `game/exit_dialog.py`, `game/simulation/replay/replay_outcome.py`, `game/strategy/services/ability_sources/star.py`
- `game/ui/screens/builder/components.py`, `game/ui/screens/strategy_windows/orders_window_ctrl.py`, `game/ui/screens/test_lab/details/draw_context.py`
- `game/ui/screens/test_lab/renderer/metadata_panel.py`, `game/ui/screens/transfer_grid_renderer.py`
- Plus 2 `__init__.py` density files

### State-Management Anti-Patterns:
- `game/exit_dialog.py` uses module-level mutable globals (`_exit_yes_rect`, `_exit_no_rect`) — PROJ-258 violation
- `game/ui/screens/orders_window_ctrl.py` uses closure-capture of `facade` and `scene` references with no test to verify capture semantics

---

## Context Usage Estimate

**Files read:** 41 (all production files in shard) + 1 (coverage matrix) + 3 (docs) = 45 total  
**Total LOC ingested:** ~8,725 (production) + ~3,000 (coverage matrix excerpt) + ~2,700 (docs) ≈ **14,425 LOC**  
**Test file checks:** 8 glob searches for test file existence  
**Estimated tokens:** ~120K input, ~15K output  
**Verification depth:** Full file reads of every production file. Coverage matrix cross-referenced. Test file existence verified but test contents not read (pre-computed matrix used for symbol-level coverage).
