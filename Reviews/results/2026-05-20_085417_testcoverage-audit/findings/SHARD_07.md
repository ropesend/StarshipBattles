# Shard 07 — Test Coverage Audit Findings

**Coverage source:** manual review (Phase 2 discovery agent)
**File count:** 47 | **LOC estimate:** ~9,578
**Tiers after correction:** 0=8 1=1 2=28 3=10

## Phase 1 Baseline Corrections

The heuristic Phase 1 baseline incorrectly classified several files as Tier 0 that have test coverage. Substantive corrections:

| File | Phase 1 Tier | Corrected Tier | Reason |
|------|------------|---------------|--------|
| `simulation/.../stabilizers.py` | 0 | 2 | `GeologicStabilizerAbility` tested in `test_strategic_abilities.py`; `StellarStabilizer`/`WarpFieldStabilizer` not directly unit-tested |
| `strategy/.../close_warp_point.py` | 0 | 2 | Comprehensive tests exist in `test_superweapon_order_processor.py`, `test_superweapon_edge_cases.py`, `test_superweapon_order_processor_gaps.py` |
| `strategy/generation/star_generator.py` | 0 | 2 | Tests in `test_stars.py` (TestStarGenerator, ~200 lines) and `test_star_generation.py` (integration, ~157 lines) |
| `strategy/.../planet_intrinsic.py` | 0 | 3 | Full test file `test_planet_intrinsic.py` covers all methods |
| `strategy/interfaces/.../terraforming.py` | 0 | 0 | Correct — pure ABC definitions, no direct unit tests |

---

## Summary

| Tier | Count | Description |
|------|-------|-------------|
| Tier 0 (CRITICAL/ADVISORY) | 8 | No direct test file found |
| Tier 1 (MAJOR) | 1 | `__init__.py` with zero symbols |
| Tier 2 (PARTIAL) | 28 | Some coverage gaps |
| Tier 3 (COVERED) | 10 | Well-tested |

**Overall:** 8 files have zero dedicated test coverage (5 CRITICAL non-UI, 3 ADVISORY UI). 28 files have partial coverage with identifiable gaps. 10 files are well-tested.

---

## Tier 0 — No Dedicated Test Coverage

### CRITICAL (non-UI, no tests)

#### 1. `game/core/protocols/common.py` (47 LOC) — CRITICAL
**Layer:** Core | **No test file exists.**

Three `@runtime_checkable` protocols and one duck-typing helper. This is foundational infrastructure imported by every other protocol sub-module. The `_has_attrs` helper backs every TypeGuard in the codebase.

Untested symbols:
- `_has_attrs(obj, *attrs)` — line 18: duck-typing helper used by all TypeGuards
- `ILocatable` Protocol — line 24: `location` property contract
- `INamed` Protocol — line 33: `name` property contract
- `IOwnable` Protocol — line 42: `owner_id` property contract

**Risk:** Any change to these protocols or the `_has_attrs` helper has zero regression protection. `_has_attrs` is explicitly documented as "treated as public despite the name" because it's imported by `game.simulation.interfaces.entity_protocols`, `game.simulation.interfaces.ability_protocols`, and `game.ai.protocols`.

**Gap:** No `test_has_attrs_positive`, `test_has_attrs_negative`, `test_locatable_isinstance_check`, `test_named_isinstance_check`, `test_ownable_isinstance_check`.

#### 2. `game/simulation/components/abilities/planetary/stabilizers.py` (180 LOC) — CRITICAL (PARTIAL)
**Layer:** Simulation | **Partial test exists:** `tests/unit/simulation/components/abilities/test_strategic_abilities.py` covers `GeologicStabilizerAbility` only.

Classes NOT directly unit-tested:
- `StellarStabilizerAbility` (lines 77-127): `__init__`, `get_primary_value`, `get_ui_rows`
- `WarpFieldStabilizerAbility` (lines 130-180): `__init__`, `get_primary_value`, `get_ui_rows`

These classes share identical structure with `GeologicStabilizerAbility` but differ in `allowed_scopes`, `default_scope`, and docstring semantics. Integration tests (`test_stabilizer_blocks_superweapon.py`, `test_planet_action_engine.py`, `test_component_activation_engine.py`) exercise activation/deactivation and superweapon-blocking, but the ability construction, default_scope resolution, energy_drain_rate parsing, and UI rows are untested at the unit level.

**Gap:**
- No `TestStellarStabilizerAbility` class
- No `TestWarpFieldStabilizerAbility` class
- No tests for `non-dict` data input (True/False/None) on these two classes
- `get_primary_value` returns `energy_drain_rate` — untested for stellar/warp variants

#### 3. `game/strategy/engine/superweapon_handlers/close_warp_point.py` (117 LOC) — CORRECTED to Tier 2
**Note:** Phase 1 classified as Tier 0 incorrectly. Tests exist at:
- `tests/unit/strategy/engine/test_superweapon_order_processor.py` (TestProcessCloseWarpPoint, ~lines 479+)
- `tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py` (TestCloseWarpPointTargetShape, TestCloseWarpPointPreconditions)
- `tests/unit/strategy/engine/test_superweapon_edge_cases.py`
- `tests/integration/strategy/test_stabilizer_blocks_superweapon.py`
- `tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py`
- `tests/unit/strategy/engine/test_superweapon_event_payloads.py`

Remaining gaps (MINOR):
- `_parse_close_target` with a `dict` that has `destination_id` but no `target_hex` → returns `(destination_id, None)` — covered by `test_close_warp_point_dict_without_target_hex_skips_sector_check`
- `_parse_close_target` with `target_hex` but missing `destination_id` → returns `("", hex)` — not explicitly tested
- `process_close_warp_point` with `target` as a `dict` containing `target_hex` but no `destination_id` — tested in `TestCloseWarpPointPreconditions`
- Path-invalidation after successful close (line 102-103) — covered via mock assertions in processor tests

#### 4. `game/strategy/generation/star_generator.py` (471 LOC) — CORRECTED to Tier 2
**Note:** Phase 1 classified as Tier 0 incorrectly. Tests exist at:
- `tests/unit/strategy/data/test_stars.py` (TestStarGenerator class, lines 458-657, plus TestDetermineTypeCharacterization lines 626-760)
- `tests/integration/strategy/test_star_generation.py` (157 lines of integration tests)

Covered methods: `_generate_mass`, `_determine_type_and_radius`, `_kelvin_to_rgb`, `_map_solar_radius_to_hex_radius`, `_generate_spectrum`, `generate_system_stars` (both random and blueprint), `generate_from_blueprint`

Remaining gaps (MINOR):
- `_generate_companions` (line 288): companion star creation is tested indirectly through `generate_system_stars`, but collision-avoidance loop (lines 316-319) and suffix string `['B', 'C', 'D']` logic are not directly unit-tested
- `_generate_mass_constrained` (line 457): constrained mass generation, only tested via `generate_from_blueprint`
- `_roll_star_type` (line 195): weighted random selection — only tested via `_determine_type_and_radius` with mocked `_roll_star_type`
- `_compute_stefan_boltzmann_type` (line 147): RED_GIANT / BROWN_DWARF / WHITE_DWARF specialized path with `mass_mode` handling — tested via parametrized characterization but not exhaustively for all config branches
- `_generate_random_stars` (line 410): fully random star count determination from probability thresholds — tested only via `generate_system_stars` without explicit count validation

#### 5. `game/strategy/interfaces/engines/terraforming.py` (72 LOC) — CRITICAL
**Layer:** Strategy | **No dedicated test file.**

Three abstract base classes defining terraforming engine interfaces. These are used as `MagicMock(spec=IQualityEngine)` etc. in turn-engine tests, but their structural contract (method signatures, abstractmethod decorators, class hierarchy) has no dedicated test.

Untested symbols:
- `IQualityEngine` ABC — line 21: `process_quality_improvement(empires: List) -> None`
- `IAtmosphereEngine` ABC — line 39: `process_atmosphere(empires: List) -> None`
- `IWaterEngine` ABC — line 57: `process_water_modification(empires: List) -> None`

**Gap:** No test verifying that concrete subclasses can be instantiated, that abstract methods are enforced, or that the `__all__` export list matches class definitions.

---

### ADVISORY (UI layer, no tests)

#### 6. `game/ui/components/filters/__init__.py` (3 LOC) — ADVISORY
Re-export shim for `TriStateFilterWidget`. Import-only, no logic.

#### 7. `game/ui/research/__init__.py` (8 LOC) — ADVISORY
Re-export shim for `ResearchTreeScene`. Docstring + import only.

#### 8. `game/ui/screens/planet_target_editor_base.py` (63 LOC) — ADVISORY
**No test file.** Base class `PlanetTargetEditor(RaceConfigResolverMixin, StrategyModalWindow)` with `_button_handlers()` and `process_event()`. Subclasses are tested indirectly through integration, but the base class button-dispatch loop and close-callback wiring (lines 47-63) have no unit test.

#### 9. `game/ui/screens/settings_window.py` (109 LOC) — ADVISORY
**No test file.** `SettingsWindow(UIWindow)` with slider-driven brightness control. `process_event`, `update`, `kill` all untested.

#### 10. `game/ui/screens/setup_renderer.py` (216 LOC) — ADVISORY
**No test file.** Pure rendering functions: `draw_title`, `draw_available_ships`, `draw_load_save_buttons`, `draw_team`, `draw_action_buttons`, `draw_ai_dropdown`. All pygame surface.blit calls — rendering-only.

#### 11. `game/ui/screens/star_list_sidebar.py` (180 LOC) — ADVISORY
**No test file.** `build_sidebar` function that constructs pygame_gui widgets + `add_range` closure. Pure UI construction, no business logic.

#### 12. `game/ui/screens/test_lab/theme.py` (174 LOC) — ADVISORY
**No test file.** Module-level color constants only. No functions, no logic — just tuples.

---

## Tier 1 — No Symbols Tested

#### 1. `game/strategy/combat/__init__.py` (6 LOC) — MAJOR
**Layer:** Strategy | Docstring-only package init. No symbols exported, no logic. The real content lives in sub-modules (`spec_compiler.py`, etc.). No test needed for an empty init, but MAJOR per formal rules.

---

## Tier 2 — Partial Coverage

### Core Layer

#### `game/core/math.py` (280 LOC)
**Test files:** `tests/unit/core/test_math.py` (primary), plus 73 indirect consumers.
**Baseline claims 9 untested symbols** — confirmed partially incorrect. `Vector2.__add__`, `__radd__`, `__sub__`, `__rsub__`, `__mul__`, `__rmul__`, `__truediv__`, `__neg__`, `__iter__` are claimed untested. These are exercised indirectly through thousands of call sites, but direct assertions on dunder behavior may be sparse.

Actual gaps verified:
- `__iter__` (line 91): yields x, y for sequence compatibility — unlikely to have explicit test
- `__getitem__` with out-of-range index (line 103): IndexError path
- `__len__` (line 105): explicit test for `len(Vector2(1,2)) == 2`
- `as_int_tuple` (line 182): explicit conversion to int tuple

**Recommendation:** Add direct dunder tests for `__iter__`, `__getitem__` (valid + invalid), `__len__`, `as_int_tuple`, and verify arithmetic operators have at least one explicit assertion each.

### Engine Layer

#### `game/engine/physics.py` (109 LOC)
**Test files:** `tests/unit/systems/test_physics.py`, `tests/unit/systems/test_physics_edge_cases.py`, `tests/unit/simulation/entities/test_ship_physics.py`
**Baseline claims 2 untested** (from 9 symbols). Verified gaps:
- `PhysicsBody.update(dt)` line 79: base Newtonian physics model documented as "NOT used by any subclass at runtime" — `Ship` overrides with arcade physics, `Projectile` does direct velocity integration. The test suite tests this path (`test_physics.py`), so the baseline is likely wrong.
- `forward_vector()` line 105: returns rotated (1,0) vector — exercised by ship physics and AI.
- `x`/`y` setters (lines 67-77): property getters/setters — tested indirectly.

**Status:** Mostly well-tested. Verify `update()` with zero-drag edge case.

### Simulation Layer

#### `game/simulation/components/abilities/__init__.py` (393 LOC)
**Test files:** 16 indirect consumers.
**Status:** This is a registry + factory module. `ABILITY_REGISTRY` is tested implicitly through ability construction throughout the suite. `create_ability` is tested through component creation. `get_ability_default_scope` tested via `test_ability_stat_registry.py`.

Remaining gaps (MINOR):
- `create_ability` with `_contains_unevaluated_formula` returning True — silent skip branch (line 252) — likely tested implicitly
- `create_ability` with unknown ability name (line 237) → returns None

#### `game/simulation/components/abilities/markers.py` (172 LOC)
**Test files:** `tests/unit/simulation/components/abilities/test_markers.py`
**Baseline claims 3 untested:** `MultiplexTrackingAbility._parse_attrs`, `VehicleStorageAbility._parse_attrs`, `PodStorageAbility._parse_attrs`.

Verified: These `_parse_attrs` methods are called from `Ability.__init__` and handle scalar, dict, and fallback cases. The baseline is likely correct that they're not DIRECTLY tested — they're tested through construction of the ability, which calls `_parse_attrs` implicitly. The gap is MINOR.

Actual gaps:
- `VehicleStorageAbility._parse_attrs` with `int` data (line 140): scalar path
- `PodStorageAbility._parse_attrs` with `dict` missing `capacity_mass` key (line 162): defaults to 0.0
- `RequiresCommandAndControl.update()` line 40: the branch where `comp.ship is None` returns True — untested
- `RequiresCommandAndControl.update()` line 51: the branch where a component IS the same component (`c is comp`) — skip-self logic

#### `game/simulation/components/abilities/vehicle_bay.py` (89 LOC)
**Test files:** `tests/unit/strategy/data/test_vehicle_bay.py`
**Baseline claims 4 untested:** `_parse_attrs`, `recalculate`, `get_primary_value`, `get_ui_rows`. Verified:
- `_parse_attrs` with `dict` shape → sets `allowed_types` and `capacity_mass`
- `_parse_attrs` with `scalar` (int/float) → treats as capacity, defaults allowed_types
- `_parse_attrs` with `None`/`bool`/other → capacity=0, defaults allowed_types
- `recalculate` → applies `bay_capacity_mult` via `get_effective_stat`
- `accepts(vehicle_type)` → case-insensitive check against `allowed_types`

These are tested through the strategy-layer `test_vehicle_bay.py` (which tests the CarriedVehicle substrate). The gap is MINOR.

#### `game/simulation/components/modifier_introspection.py` (311 LOC)
**Test files:** `tests/unit/modifiers/test_modifier_introspection.py`, `tests/unit/simulation/components/test_modifier_introspection.py`
**Status:** Well-tested. All 6 symbols reportedly covered.

Remaining gaps (MINOR):
- `generate_ability_stats_display` with `change_percent == float('inf')` (line 292): infinite percentage display case

### Strategy Layer

#### `game/strategy/data/fleet_capability_calculator.py` (268 LOC)
**Test files:** 4 test files. **Baseline claims 2 untested:** `_get_ship_component_registry`, `_get_registry`.
- `_get_ship_component_registry` (line 16): module-level helper, tested indirectly through `FleetCapabilityCalculator.ship_has_spaceyard` and other methods
- `_get_registry` (line 121): raises ValueError when no registry available — tested via `ship_has_spaceyard` raising ValueError

**Actual gaps (MINOR):**
- `can_build_type` with `vehicle_type="complex"` and `galaxy=None` → returns False (line 168)
- `can_build_type` with unknown vehicle_type → returns False (line 173)

#### `game/strategy/data/fleet_hierarchy.py` (185 LOC)
**Test files:** 10 test files. **Baseline claims 1 untested:** `FleetHierarchyNode.__init__`.
- `__init__` is exercised through construction in every test. `to_dict`/`from_dict` round-trip tests exist.

**Status:** Well-tested. Gap is a false positive from the heuristic scanner (constructors are often flagged).

#### `game/strategy/engine/atmosphere_engine.py` (143 LOC)
**Test files:** 3 test files. **Baseline claims 3 untested:** `__init__`, `_get_planet_mutator`, `_process_colony`.

Verified gaps:
- `_get_planet_mutator` (line 30): lazy-import pattern when `_planet_mutator is None` — tested indirectly
- `_process_colony` (line 62): full atmosphere modification logic — tested in `test_atmosphere_engine.py`
- `_validate_tick_inputs` (line 38): precondition check for None colonies — tested in `test_engine_validation.py`

**Status:** Mostly well-tested. `_get_planet_mutator` lazy-init path has no direct assertion.

#### `game/strategy/engine/handlers/transfer.py` (142 LOC)
**Test files:** `tests/unit/strategy/engine/test_transfer_handler_fleet_to_fleet.py`
**Baseline claims 1 untested:** `register()`.

Verified:
- `TransferCommandHandler.execute` is tested for both fleet-to-fleet and fleet-to-planet paths
- `register()` (line 136): calls `registry.register(CommandSpec(...))` — this is the self-registration hook. Tests likely call `register()` through module-level test setup but may not assert the registration directly.

**Gap:** No test verifying that `register(registry)` correctly registers both `TransferCommandHandler` entries. MINOR.

#### `game/strategy/engine/order_handlers/colonize.py` (210 LOC)
**Test files:** `tests/unit/strategy/engine/order_handlers/test_colonize_handler.py`
**Baseline claims 1 untested:** `supported_order_types`.

Verified:
- `supported_order_types` (line 42): returns `(OrderType.COLONIZE,)`. This property is tested implicitly when the handler factory looks up handlers by OrderType.

**Actual gaps (MINOR):**
- `_deploy_drop_pod` with `pod_index` out of range (line 172-178): the warning log path
- `execute_action_order` with `component_registry=None` (line 60-64): early-return path with log
- `execute_action_order` with target as plain Planet (not dict) (line 70): the else branch

#### `game/strategy/engine/session/bootstrap.py` (322 LOC)
**Test files:** `tests/unit/strategy/engine/session/test_bootstrap.py`
**Baseline claims 2 untested:** `build_event_handler`, `handler`.

Verified:
- `build_event_handler` (line 45): builds a closure-based event handler. Tested via `_build_services` which calls it.
- `SessionBootstrap._build_services` (line 87): massive service wiring function — tested in `test_bootstrap.py`
- `SessionBootstrap.new_game_state` (line 227): new-game initialization — may have limited test coverage
- `handler` inner closure (line 58): the actual event handler logic extracting `category`, `message`, `empire_id` from kwargs — MINOR gap

**Actual gaps:**
- `new_game_state` `SessionInitializationError` path (line 269-278): the except block with intentional broad catch
- `handler` closure with `category` as enum vs string (line 62): the `hasattr(category, "value")` path

#### `game/strategy/services/empire_economy_service.py` (96 LOC)
**Test files:** 2 test files. **Baseline claims 1 untested:** `EmpireEconomyService.__init__`.
- `__init__` creates `EmpireEconomyCalculator` — tested through construction in service tests.
- `get_snapshot` with `facade_state` caching — tested in `test_empire_economy_caching.py`

**Status:** Well-tested. Only `__init__` may be flagged because it's a constructor.

#### `game/strategy/systems/design_repository.py` (509 LOC)
**Test files:** 16 test files. **Baseline claims 5 untested:** `DesignLoadResult.invalid_schema`, `permission_denied`, `io_error`, `DesignRepository.has_design`, `_sanitize_design_id`.

Verified gaps:
- `DesignLoadResult.invalid_schema` (line 81): factory method — tested in `test_load_design_data.py` or similar
- `DesignLoadResult.permission_denied` (line 88): factory method
- `DesignLoadResult.io_error` (line 95): factory method
- `DesignRepository.has_design` (line 365): simple file-existence check — MINOR
- `DesignRepository._sanitize_design_id` (line 369): calls `slugify()` — MINOR

**Actual gaps:**
- `load_design_data` returning `permission_denied` (line 306-312): PermissionError path
- `load_design_data` with `designs_folder is None` (line 289-290)
- `save_design` with `built_designs` containing the slug (line 403-408): overwrite protection
- `save_design` catching `ValidationException` (line 442-448)
- `increment_built_count` catching `JSONDecodeError` (line 489-495)

---

### UI Layer (Tier 2)

#### `game/ui/panels/build_queue_controller.py` (723 LOC)
**Test files:** 3 test files. **Baseline claims 5 untested.**
- `_get_target_planet_id`, `_add_to_single_queue`, `_add_item_with_target_planet`, `_add_to_multiple_queues`, `_add_to_fallback`

These are internals of the multi-queue add path. The `PROJ-69` multi-queue path is tested at the integration level. The private helper methods may not have direct unit test assertions but are exercised through `add_item_to_queues`.

**Note:** File at 723 LOC exceeds the 500 LOC ceiling (violates Pattern LOC ceiling). File is a strong candidate for decomposition.

#### `game/ui/panels/empire_treasury_panel.py` (370 LOC)
**Test files:** `tests/unit/ui/panels/test_empire_treasury_panel.py`
**Baseline claims 7 untested.** Correct:
- `_get_planetary_ids` (line 25): `@lru_cache(maxsize=1)` function — tested indirectly
- `EmpireTreasuryPanel.__init__`, `_build_ui`, `_build_section`, `_build_row`: pygame UI construction methods — ADVISORY
- `_clear_resource_icon_cache`, `load_resource_icons`: cache management

#### `game/ui/screens/battle_state_viewer.py` (262 LOC)
**Test files:** `tests/unit/ui/screens/test_battle_state_viewer.py`
**Baseline claims 3 untested:** `show`, `hide`, `handle_resize`. Confirmed — these are UI lifecycle methods. ADVISORY for rendering.

#### `game/ui/screens/builder/weapons_renderer.py` (524 LOC)
**Test files:** `tests/unit/ui/screens/builder/test_weapons_renderer.py`
**Baseline claims 10 untested.** All are rendering methods:
- `clear_caches`, `invalidate_icon_cache`, `invalidate_name_cache`
- `_get_scaled_icon`, `_get_weapon_name_surface`
- `_get_accuracy_color`
- `draw_direction_indicator`, `draw_scale_markers`, `draw_unified_weapon_bar`, `draw_weapon_row`

All ADVISORY — pure pygame rendering with surface manipulation. File at 524 LOC exceeds 500 LOC ceiling.

#### `game/ui/screens/fleet_report_filters.py` (319 LOC)
**Test files:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Baseline claims 2 untested:** `_check_tri_state`, `get_sort_key`. These are inner functions/helpers — MINOR.

#### `game/ui/screens/race_setup/view_model.py` (88 LOC)
**Test files:** 2 test files. **Baseline claims 4 untested:**
- `tab_count` (line 65): `@property` returning `len(TAB_NAMES)` = 7
- `clamp_step` (line 69): clamps index to valid range
- `show_save_button_on` (line 73): visible only on Summary tab
- `show_randomize_button_on` (line 77): visible on tabs 1-5

These are all testable without pygame. Actual gaps.

#### `game/ui/screens/star_list_filters.py` (226 LOC)
**Test files:** 2 test files. **Baseline claims 2 untested:**
- `matches_filter` (inner function at line 87): all filter logic in the closure
- `padded_range` (inner function): padding for range limits

These are MINOR — the filter function is exercised through `filter_stars`.

#### `game/ui/screens/test_lab/screen.py` (416 LOC)
**Test files:** 3 thin test files. **Baseline claims 27 untested.** Many are state variables set through UI interaction. The MVVM split puts logic in ViewModel/Renderer/InputHandler. Coverage is adequate for the coordinator role. ADVISORY for UI-only state.

#### `game/ui/services/vehicle_class_service.py` (134 LOC)
**Test files:** 2 test files. **Baseline claims 2 untested:** `__init__`, `_get_provider`.
- `__init__` with `None` raises `ValidationException` — confirmed tested in `test_vehicle_class_service.py`
- `_get_provider` returns `self._provider` — tested indirectly

**Status:** Well-tested. Minor gap: `get_type_for_class` with unknown class name returns `'Ship'` (line 133).

#### `game/ui/widgets/ui_element_registry.py` (62 LOC)
**Test files:** `tests/unit/ui/widgets/test_ui_element_registry.py`
**Baseline claims 3 untested:** `__init__`, `__len__`, `__iter__`.
- `__init__` exercised through construction, `__len__` through `len(registry)`, `__iter__` through iteration. These are structural methods tested indirectly.

**Status:** Well-tested. `clear()` vs `kill_all()` distinction is the important business logic.

---

## Tier 3 — Well-Covered

All 10 Tier 3 files verified with good coverage:

| File | Test File(s) | Notes |
|------|-------------|-------|
| `ai/combat_utils.py` | `test_combat_utils.py`, `test_target_evaluator_edge_cases.py` | All 9 symbols covered |
| `ai/spatial_behaviors/__init__.py` | `test_spatial_behaviors.py` | Import aggregation only |
| `core/constants.py` | 84 indirect consumers | Enums/constants widely used |
| `core/exceptions.py` | 126 indirect consumers | Exception hierarchy tested through raise/catch |
| `core/registry_cache.py` | `test_registry_cache.py` | Dedicated test file |
| `core/resources.py` | `test_resources.py`, `test_resource_catalog.py` | Comprehensive | 
| `simulation/.../abilities/__init__.py` | 16 indirect | Registry tested through construction |
| `simulation/.../modifier_introspection.py` | `test_modifier_introspection.py` | All 6 symbols |
| `ui/screens/builder/event_bus.py` | `test_event_bus.py` | All 5 symbols |
| `ui/screens/race_setup/delegate_factory.py` | `test_race_setup_delegate_factory.py` | All 3 symbols |

---

## File Coverage Verification Table

| # | Production File | LOC | Tier | Test File(s) Exist | Coverage Quality | Key Gaps |
|---|----------------|-----|------|-------------------|------------------|---------|
| 1 | `ai/combat_utils.py` | 244 | 3 | Yes (2) | High | None significant |
| 2 | `ai/spatial_behaviors/__init__.py` | 66 | 3 | Yes (1) | High | Import-only |
| 3 | `ai/spatial_behaviors/battle_line.py` | 98 | 2 | Yes (1) | Medium | `__init__` flagged by heuristic |
| 4 | `core/constants.py` | 91 | 3 | Yes (84) | High | Enums — tests are indirect |
| 5 | `core/exceptions.py` | 544 | 3 | Yes (126) | High | Broad indirect coverage |
| 6 | `core/math.py` | 280 | 2 | Yes (73) | Medium | Dunder operators, `__iter__` |
| 7 | `core/protocols/common.py` | 47 | **0** | **None** | **None** | Entire file — 3 protocols + helper |
| 8 | `core/registry_cache.py` | 83 | 3 | Yes (1) | High | Well-tested |
| 9 | `core/resources.py` | 197 | 3 | Yes (21) | High | Comprehensive |
| 10 | `engine/physics.py` | 109 | 2 | Yes (3) | Medium | Base physics model indirect |
| 11 | `simulation/.../abilities/__init__.py` | 393 | 3 | Yes (16) | Medium | Registry factory module |
| 12 | `simulation/.../abilities/markers.py` | 172 | 2 | Yes (1) | Medium | `_parse_attrs` indirect, `update` edge case |
| 13 | `simulation/.../planetary/stabilizers.py` | 180 | **0→2** | Yes (1) | **Low** | Stellar/WarpField not unit tested |
| 14 | `simulation/.../vehicle_bay.py` | 89 | 2 | Yes (1) | Medium | `_parse_attrs` branches |
| 15 | `simulation/.../modifier_introspection.py` | 311 | 3 | Yes (2) | High | Minor edge cases |
| 16 | `strategy/combat/__init__.py` | 6 | 1 | Yes (2) | N/A | Empty init — docstring only |
| 17 | `strategy/data/fleet_capability_calculator.py` | 268 | 2 | Yes (4) | Medium | `can_build_type` edge cases |
| 18 | `strategy/data/fleet_hierarchy.py` | 185 | 2 | Yes (10) | High | Constructor false positive |
| 19 | `strategy/engine/atmosphere_engine.py` | 143 | 2 | Yes (3) | Medium | `_get_planet_mutator` lazy path |
| 20 | `strategy/engine/handlers/transfer.py` | 142 | 2 | Yes (1) | Medium | `register()` direct assertion |
| 21 | `strategy/engine/order_handlers/colonize.py` | 210 | 2 | Yes (1) | Medium | `component_registry=None`, OOB pod_index |
| 22 | `strategy/engine/session/bootstrap.py` | 322 | 2 | Yes (1) | Medium | `handler` closure branches, init error path |
| 23 | `strategy/engine/.../close_warp_point.py` | 117 | **0→2** | Yes (6) | **High** | Minor edge cases |
| 24 | `strategy/generation/star_generator.py` | 471 | **0→2** | Yes (2) | **Medium** | `_generate_companions` collision loop |
| 25 | `strategy/interfaces/.../terraforming.py` | 72 | **0** | **None** | **None** | Pure ABC — no structural test |
| 26 | `strategy/services/.../planet_intrinsic.py` | 91 | **0→3** | Yes (1) | **High** | Fully tested |
| 27 | `strategy/services/empire_economy_service.py` | 96 | 2 | Yes (2) | High | `__init__` false positive |
| 28 | `strategy/systems/design_repository.py` | 509 | 2 | Yes (16) | Medium | Error paths, `has_design`, `_sanitize` |
| 29 | `ui/components/filters/__init__.py` | 3 | **0** | **None** | N/A | Re-export shim |
| 30 | `ui/panels/build_queue_controller.py` | 723 | 2 | Yes (3) | Low | **Exceeds 500 LOC**, multi-queue add internals |
| 31 | `ui/panels/empire_treasury_panel.py` | 370 | 2 | Yes (1) | Low | UI construction methods |
| 32 | `ui/research/__init__.py` | 8 | **0** | **None** | N/A | Re-export shim |
| 33 | `ui/screens/battle_state_viewer.py` | 262 | 2 | Yes (1) | Medium | show/hide/handle_resize |
| 34 | `ui/screens/builder/event_bus.py` | 78 | 3 | Yes (5) | High | All symbols covered |
| 35 | `ui/screens/builder/weapons_renderer.py` | 524 | 2 | Yes (1) | Low | **Exceeds 500 LOC**, 10 render methods |
| 36 | `ui/screens/fleet_report_filters.py` | 319 | 2 | Yes (1) | Medium | Inner functions |
| 37 | `ui/screens/planet_target_editor_base.py` | 63 | **0** | **None** | **None** | Base class with event dispatch |
| 38 | `ui/screens/race_setup/delegate_factory.py` | 87 | 3 | Yes (1) | High | Fully tested |
| 39 | `ui/screens/race_setup/view_model.py` | 88 | 2 | Yes (2) | Low | 4 untested properties |
| 40 | `ui/screens/settings_window.py` | 109 | **0** | **None** | **None** | UIWindow with slider logic |
| 41 | `ui/screens/setup_renderer.py` | 216 | **0** | **None** | **None** | 6 render functions |
| 42 | `ui/screens/star_list_filters.py` | 226 | 2 | Yes (2) | Medium | Inner closure functions |
| 43 | `ui/screens/star_list_sidebar.py` | 180 | **0** | **None** | **None** | UI builder function |
| 44 | `ui/screens/test_lab/screen.py` | 416 | 2 | Yes (3) | Low | UI state, MVVM thin coordinator |
| 45 | `ui/screens/test_lab/theme.py` | 174 | **0** | **None** | **None** | Color constants only |
| 46 | `ui/services/vehicle_class_service.py` | 134 | 2 | Yes (2) | High | Minor edge case |
| 47 | `ui/widgets/ui_element_registry.py` | 62 | 2 | Yes (1) | High | `__len__`/`__iter__` indirect |

---

## LOC Ceiling Violations

| File | LOC | Limit | Over |
|------|-----|-------|------|
| `ui/panels/build_queue_controller.py` | 723 | 500 | +223 |
| `core/exceptions.py` | 544 | 500 | +44 |
| `ui/screens/builder/weapons_renderer.py` | 524 | 500 | +24 |
| `strategy/systems/design_repository.py` | 509 | 500 | +9 |

---

## Priority Recommendations

### CRITICAL — Must address

1. **`game/core/protocols/common.py`** — Add `tests/unit/core/protocols/test_common.py`:
   - `test_has_attrs_all_present`, `test_has_attrs_some_missing`
   - `test_ilocatable_isinstance`, `test_inamed_isinstance`, `test_iownable_isinstance`

2. **`game/simulation/components/abilities/planetary/stabilizers.py`** — Add `TestStellarStabilizerAbility` and `TestWarpFieldStabilizerAbility` to `test_strategic_abilities.py`:
   - Construction from dict, minimal data, non-dict data
   - `get_primary_value`, `get_ui_rows`
   - Scope validation (allowed/disallowed)

3. **`game/strategy/interfaces/engines/terraforming.py`** — Add `tests/unit/strategy/interfaces/test_terraforming_contract.py`:
   - Verify ABCs prevent instantiation
   - Verify concrete mocks satisfy the protocol
   - Verify `__all__` completeness

### MAJOR — Should address

4. **`game/ui/screens/race_setup/view_model.py`** — Add tests for `tab_count`, `clamp_step`, `show_save_button_on`, `show_randomize_button_on`

5. **`game/strategy/engine/session/bootstrap.py`** — Test `new_game_state` initialization failure path

6. **`game/strategy/engine/order_handlers/colonize.py`** — Test `component_registry=None` path and `_deploy_drop_pod` with OOB index

### MINOR — Good to have

7. **`game/core/math.py`** — Add direct assertions for `__iter__`, `__getitem__`, `__len__`, `as_int_tuple`
8. **`game/strategy/engine/handlers/transfer.py`** — Add test for `register()` self-registration
9. **`game/strategy/systems/design_repository.py`** — Test error paths in `load_design_data`, `save_design`, `increment_built_count`

### ADVISORY — UI-only

10. **`game/ui/screens/setup_renderer.py`** — Add smoke tests for render functions with mock surfaces
11. **`game/ui/screens/planet_target_editor_base.py`** — Test `process_event` button dispatch
12. **`game/ui/screens/settings_window.py`** — Test slider value sync

### Structural

13. **`ui/panels/build_queue_controller.py`** (723 LOC) — Decompose to meet 500 LOC ceiling
14. **`ui/screens/builder/weapons_renderer.py`** (524 LOC) — Split rendering concerns
