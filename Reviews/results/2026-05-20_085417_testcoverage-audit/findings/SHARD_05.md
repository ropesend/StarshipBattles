# Shard 05 — Test Coverage Audit (Discovery Agent)

**Generated:** 2026-05-20  
**Files audited:** 32 production files, ~9500 LOC  
**Methodology:** Read every production file + every corresponding test. Traced all code paths.

---

## Summary

| Tier | Count | Status |
|------|-------|--------|
| Tier 0 (CRITICAL) | 8 | 2 gap, 4 advisory, 2 ok |
| Tier 1 (MAJOR) | 0 | — |
| Tier 2 (PARTIAL) | 17 | 5 major gaps, 6 minor, 6 advisory |
| Tier 3 (COVERED) | 7 | 7 ok |

**Key findings:**
- **3 CRITICAL gaps** in non-UI Tier 0 files lacking any dedicated test coverage.
- **5 MAJOR gaps** in Tier 2 production files with partial coverage of key methods.
- **6 MINOR gaps** in well-tested files missing edge cases or private helper coverage.
- **4 ADVISORY** re-export `__init__.py` files — expected, no action needed.
- **6 ADVISORY** UI rendering/event files — out of scope for hard coverage requirements.

---

## Tier 0 — CRITICAL (non-UI)

### 1. `game/simulation/entities/stat_contributors/launch.py` (118 LOC)
**Severity: CRITICAL** | Layer: Simulation | Has tests: Yes (partial)

**Covered:**
- `contribute_vehicle_launch()` — tested at `tests/unit/simulation/entities/stat_contributors/test_launch.py:58-118` with 5 tests: no-op when no ability, single hangar populates capacity/wave/cycle, multi-component summation, launch_cycle takes max, storage without launch ignored.

**Not covered:**
- `contribute_tactical_satellite_launch()` (lines 69-100) — no test exercises satellite launch aggregation. Mirrors the fighter path but writes to different ship fields (`satellites_per_wave`, `satellite_launch_cycle`, `satellite_capacity`, `satellite_launch_rate_tons_per_sec`). An incorrect saturation or field name typo would go undetected.
- `contribute_vehicle_bay()` (lines 103-118) — no test exercises VehicleBay capacity sum into `ship.bay_capacity_mass`. The early-return path (no VehicleBay ability) and the summation loop are untested.

**Recommendation:** Add tests for the satellite path (`contribute_tactical_satellite_launch`) and vehicle bay path (`contribute_vehicle_bay`). These are pure data-accumulation functions and trivial to unit-test — each needs ~3 tests (no-op, single, multi).

### 2. `game/simulation/interfaces/component_protocols.py` (226 LOC)
**Severity: CRITICAL** | Layer: Simulation | Has tests: No

**What it is:** Defines `@runtime_checkable IComponent` Protocol with 23 property/method signatures and a `TypeGuard` helper `is_component(obj)`.

**Not covered:**
- No dedicated test file exists. The protocol is exercised indirectly through every test that uses `Component` objects, but:
  - The `TypeGuard` function `is_component()` (line 224) is never tested with a non-Component argument — it is never called in any test file.
  - Structural completeness (all 23 protocol members present on the real `Component` class) is not verified by any test.
  - `@runtime_checkable` semantics are not exercised — there's no test that `isinstance(mock_component, IComponent)` returns True/False correctly.

**Recommendation:** Write a focused protocol-conformance test. At minimum: (a) verify `isinstance(Component(...), IComponent)` returns True, (b) verify `is_component()` TypeGuard narrows correctly, (c) verify `is_component(dict())` returns False. This is ~30 LOC of tests.

### 3. `game/strategy/facade/slices/economy_slice.py` (188 LOC)
**Severity: CRITICAL** | Layer: Strategy | Has tests: No

**Not covered:**
- `EconomySlice.get_race_registry()` (line 35) — lazy-constructs `CachedRaceRegistry`. The lazy-init path and the cache-hit path are both untested.
- `EconomySlice.resolve_economy_config()` (line 59) — session fallback to `get_default_economy_config()`. The fallback-warning path (session has no economy_config) is untested.
- `EconomySlice.get_colony_demographic_view()` (line 85) — 103 LOC method with significant business logic: planet lookup, species iteration, habitability calculation, growth projection, surplus bonus cap, per-species DTO construction, resource upkeep summation. **This is the heaviest uncovered business logic in the shard.**

**Recommendation:** Write unit tests for `EconomySlice`. The ViewModel-like shape (pure data transformation, no pygame) makes it highly testable. Key test scenarios: (a) colony with single species returns correct demographics, (b) multi-species colony, (c) surplus bonus clamped at cap, (d) unowned planet returns None, (e) unknown race_id gracefully skipped, (f) race registry lazy-init and cache hit, (g) economy_config fallback path.

### 4. `game/engine/__init__.py` (36 LOC)
**Severity: ADVISORY** | Layer: Engine | Has tests: Indirect only

Re-exports `PhysicsBody`, `CollisionSystem`, `SpatialGrid`. The exported classes are tested individually; the re-export module itself needs no dedicated test. **No action required.**

### 5. `game/simulation/combat/families/__init__.py` (13 LOC)
**Severity: ADVISORY** | Layer: Simulation | Has tests: Indirect only

Imports 4 weapon family modules (beam, projectile, seeker, pdc) for side-effect registration. **No action required.**

### 6. `game/strategy/generation/loaders/__init__.py` (7 LOC)
**Severity: ADVISORY** | Layer: Strategy | Has tests: Indirect only

Re-exports `GalaxyLayoutsLoader`. **No action required.**

### 7. `game/ui/screens/race_setup/ship_preview.py` (163 LOC)
**Severity: ADVISORY** | Layer: UI | Has tests: No

`ShipPreviewBuilder` constructs pygame_gui widgets for the 3x3 ship preview grid. Pure rendering. **No action required.**

### 8. `game/ui/screens/test_lab/renderer/validation_panel.py` (230 LOC)
**Severity: ADVISORY** | Layer: UI | Has tests: No

`ValidationPanel.draw()` renders validation results with pygame surfaces. Pure rendering. **No action required.**

---

## Tier 2 — MAJOR / MINOR

### 9. `game/core/component_state.py` (102 LOC)
**Severity: MINOR** | Layer: Core | Has tests: Good (169 LOC test file)

**Covered:** Dataclass fields, to_dict/from_dict roundtrip, defaults (is_active, max_hp), component_state_key helper, integer-to-float coercion, is_damaged property, from_dict with missing optional fields, ComponentInstanceView frozen/equality/immutability.

**Gap:** `ComponentState.__post_init__` (lines 72-75) is exercised by the coercion tests but never called directly or tested in isolation. The behavior (float coercion) is verified. **Low priority.**

### 10. `game/core/paths.py` (202 LOC)
**Severity: MINOR** | Layer: Core | Has tests: Indirect

**Covered:** Core path constants used across the test suite. The `Path` accessor classmethods are exercised by many tests.

**Gaps:**
- `_find_project_root()` error path (lines 36-40) — the `ResourceException` branch is never triggered in tests. The sentinel-finding loop (10 parent directories) works in production but the failure case (no game/data dirs found) is untested.
- `Paths.get_planets_v3_dir()` (line 188) — returns a `Path` object; usage across codebase exercises it indirectly.
- `Paths.get_stars_dir()` (line 192) — same situation.

### 11. `game/simulation/combat/formation.py` (416 LOC)
**Severity: MINOR** | Layer: Simulation | Has tests: Good (216 LOC test file + multiple other formation tests)

**Covered:** `FormationShape` enum completeness, `FormationSpec` frozen dataclass/serialization, `FormationResolver.resolve()` exercised via default formation tests, `resolve_team_entry_vectors()` thoroughly tested (2-team legacy, 3-8 team ring, facing-inward, ValueError on invalid counts), `resolve_default_for_task_force()` tested via integration/combat lab tests.

**Gaps:**
- `_compute_local_positions()` (line 161) — exercised through `FormationResolver.resolve()`. Edge shapes tested only implicitly: CUSTOM with empty positions (line 174), CUSTOM with shorter-than-n positions (line 176), SCREEN with odd counts (line 212), CARRIER_PROTECTED with 1 ship (line 230), unknown shape fallback (line 244). No test explicitly covers the "unknown shape returns LINE_ASTERN" fallback.
- `_symmetric_y()` (line 248) — exercised through LINE_ABREAST and SCREEN shapes. The `count == 1` early return (line 256) is exercised; even-count half-spacing (lines 258-262) is exercised. No isolated test exists but behavior is implicit via public API.

### 12. `game/simulation/components/abilities/base.py` (535 LOC)
**Severity: MINOR** | Layer: Simulation | Has tests: Extensive (via subclasses and combat tests)

**Covered:** `Ability.__init__`, `_parse_scope`, `sync_data`, `applies_to_layer`, `get_effective_stat` (local-only, external-only, combined _mult, combined _add, unknown key fallback), `get_primary_value`, `get_consumed_stats`, `get_stat_bindings_info`, `get_effect_summary`, `StaticValueAbility` (parse/multiplier/UI), `SimpleMultiplierAbility` (parse/recalculate/multiplier).

**Gaps:**
- `Ability._parse_attrs()` (line 98) — default no-op is exercised through every subclass's overridden version. No direct test.
- `StaticValueAbility._parse_attrs()` (line 459) — exercised through subclass behavior (e.g., `ToHitAttackModifier`).
- `SimpleMultiplierAbility._parse_attrs()` (line 511) — exercised through subclass behavior.
- `Ability.get_effective_stat()` with `default=_NO_DEFAULT` sentinel (lines 271-278) — the sentinel-based default resolution is well-exercised. **Low priority.**

### 13. `game/simulation/systems/battle_engine.py` (758 LOC)
**Severity: MAJOR** | Layer: Simulation | Has tests: Good (17 test files reference it)

**Covered:** `start()`, `start_teams()`, `is_battle_over()`, `get_winner()`, `update()` (tick loop), `add_ship_mid_battle()`, `enforce_boundary()`, `launch_fighters_in_battle()`, `launch_satellites_in_battle()`, `_run_mine_resolver_tick()`, N-team accessors (`teams`, `get_ships_by_team`, `get_enemies_of`).

**Gaps (most delegate to helpers — tested through integration):**
- `remove_ship()` (line 399) — aura manager unregistration and AI controller removal are tested through tactical launch/reboard tests but not in isolation.
- `get_ship_by_name()` (line 430) — no dedicated test for match/no-match paths.
- `set_ram_target()` (line 575) / `clear_ram_target()` (line 587) — proxied to `RamTargetResolver`. Tested indirectly via ramming integration but no unit test for the engine's delegation itself.
- `_run_ramming_tick()` (line 591) — tested via battle tick loop integration; the broad-except safety wrapper (line 470) is never triggered in tests.
- `shutdown()` (line 756) — one-line `self.logger.close()`. Trivial, but technically untested in isolation.
- `_initialize_start_state()` (line 305), `_rebuild_grid()` (line 660), `_update_ai_and_ships()` (line 673) — all delegate to helper modules, tested via `update()` tick loop.

**Recommendation:** `remove_ship()` and `get_ship_by_name()` are low-hanging unit-test targets. The remaining methods are thin delegates tested adequately through integration.

### 14. `game/strategy/data/deployed_group.py` (424 LOC)
**Severity: MAJOR** | Layer: Strategy | Has tests: Indirect only

**Covered:** Serialization roundtrip (`to_dict` → `from_dict`) tested through fleet/deployment integration tests (`test_battle_assembly.py`, `test_fighter_group_combat_join.py`, `test_satellite_group_combat_join.py`).

**Gaps (no dedicated test file):**
- `_register_type` / `deco` (lines 48-53) — the decorator-based type registry is not independently verified. A missing `@_register_type` on a new subclass would only surface at deserialization time.
- `DeployedGroup._from_dict_payload()` (line 146) — raises `NotImplementedError`. The raise path is untested.
- `DeployedGroup._decode_location()` (line 152) — covers dict, list/tuple, and HexCoord input. The `ValueError` raise path (line 159) is untested.
- `DeployedGroup.__eq__()` (line 167) — type+id equality. Untested.
- `DeployedGroup.__hash__()` (line 172) — Untested.
- `DeployedGroup.__repr__()` (line 175) — Untested.
- `MineGroup._from_dict_payload()` / `FighterWing._from_dict_payload()` / `SatelliteConstellation._from_dict_payload()` (lines 253, 352, 410) — exercised through integration tests.
- `_ShipBearingDeployedGroup.remove_ship()` (line 300) — Untested in isolation.

**Recommendation:** Write a focused test file. At minimum: (a) verify `_register_type` populates `_TYPE_REGISTRY`, (b) verify `from_dict` with unknown type raises `ValueError`, (c) verify `_decode_location` with invalid input raises, (d) verify `__eq__`/`__hash__` semantics, (e) verify `_from_dict_payload` base raises `NotImplementedError`.

### 15. `game/strategy/engine/population_engine.py` (177 LOC)
**Severity: MINOR** | Layer: Strategy | Has tests: Excellent (692 LOC test file)

**Covered:** Thoroughly. Logistic growth, happiness effects, habitability effects, starvation decline, multi-species via registry, legacy path, edge cases (zero pop, no empires, no colonies, clamped to zero), multi-resource starvation, PROJ-284 formula parity.

**Gaps:** `_process_empire()` and `_process_colony()` are tested through `process_population_growth()` — they're simple iteration helpers. **No significant gaps.**

### 16. `game/strategy/engine/production_spawner.py` (667 LOC)
**Severity: MAJOR** | Layer: Strategy | Has tests: Good (582 LOC test file, + staging yard + normalization)

**Covered:** `spawn_completed_item()` dispatch, `_resolve_planet_location()`, `_load_design()` / `_load_and_create_ship()` (catalog-based), `_spawn_to_staging_yard()`, `_spawn_ship()`, `_spawn_fleet_ship()`, `_spawn_fleet_complex()` (target_planet_id resolution), `_create_and_place_facility()`.

**Gaps:**
- `__init__()` (line 36) — `TypeError` raise on None registries is covered by tests. The `planet_mutator` eager-default path tested via spawn methods.
- `_get_catalog()` (line 99) — one-liner dict access. Tested through all spawn methods.
- `_get_planet_mutator()` (line 103) — tested through facility creation.
- `_spawn_fleet_carried_vehicle()` (line 477) — PROJ-FMS-A Phase 4 method. The bay-capacity-full branch (line 571) and the unknown vehicle type branch (line 529) are **probably not exercised** given the single test file for production spawner. These error paths rely on fleet-bay state that's harder to mock. The drop_pod fallback branch (line 526) is also questionable.

**Recommendation:** Add test coverage for `_spawn_fleet_carried_vehicle()` error paths: no bay capacity, unknown vehicle type, missing registries. These are production-critical error-handling paths.

### 17. `game/ui/panels/modifier_impact_grid.py` (514 LOC)
**Severity: ADVISORY** | Layer: UI | Has tests: Yes

UI grid rendering. The logic methods (`_get_component_consumed_stats`, `_get_affected_stats`, `_format_value`, `_get_value_color`) are testable pure functions. The draw/event methods are pygame-dependent. **No critical action.**

### 18. `game/ui/screens/builder/modifier_row.py` (355 LOC)
**Severity: ADVISORY** | Layer: UI | Has tests: Yes

UI modifier control row. The private helpers `_build_linear_controls` and `_clear_ui` are exercised through `build_ui()`/`kill()`. **No critical action.**

### 19. `game/ui/screens/fleet_menu_items.py` (274 LOC)
**Severity: MINOR** | Layer: UI (non-rendering) | Has tests: Excellent (615 LOC test file)

**Covered:** Pure-logic builder with no pygame. All 8 capability-gate helpers tested through `build_menu_items()` public API. FMS rows (lay mines, launch/recover fighters/satellites) have 15+ tests each, including callback wiring, ordering, backward compat. **No significant gaps.**

All private helpers (`_has`, `_can_warp`, `_can_strategic_move`, `_has_self_destruct_ships`, `_at_colonisable_hex`, `_fleet_has_carried_vehicle`, `_matching_deployed_group_at_fleet_hex`, `_MapperLike`) are exercised through the comprehensive public API tests.

### 20. `game/ui/screens/planet_selection_window.py` (262 LOC)
**Severity: ADVISORY** | Layer: UI | Has tests: Yes

UI modal window. `PlanetSelectionUiBuilder.build()` is exercised through the window constructor. The `update()` loop (line 176) with planet detail panel creation/rotation is pygame-dependent. **No critical action.**

### 21. `game/ui/screens/star_list_window.py` (554 LOC)
**Severity: ADVISORY** | Layer: UI | Has tests: Yes (6 test files)

UI modal window with filtering/sorting/presets. Covered by reuse tests, filter snapshot tests, row pool visibility tests. **No critical action.**

### 22. `game/ui/screens/strategy_renderer.py` (288 LOC)
**Severity: ADVISORY** | Layer: UI | Has tests: Yes (4 test files)

UI rendering composer. All `_draw_*` methods delegate to layer modules. The public `draw()` and `draw_processing_overlay()` methods are tested for orchestration correctness. **No critical action.**

### 23. `game/ui/screens/strategy_superweapons.py` (416 LOC)
**Severity: ADVISORY** | Layer: UI | Has tests: Yes

UI superweapon orchestration. The private helpers `_show_confirmation`, `_show_system_picker`, `_show_ship_picker` delegate to `scene.ui` methods. `_check_fleet_ability` (line 32) is a simple shared validator tested through all 6 handler methods.

### 24. `game/ui/screens/transfer_view_model.py` (325 LOC)
**Severity: MINOR** | Layer: UI (non-rendering) | Has tests: Good (89+ LOC test file + 6 supporting test files)

**Covered:** `TransferViewModel` pending-transfer math (`apply_arrow`, `apply_max`, `set_pending_zero`, `clear_all_pending`, `reset_pending`), `format_pending`, source/target selection, `toggle_filter_empty`.

**Gaps:**
- `_get_resource_catalog()` (line 39) — module-level lazy loader. Tested indirectly through `_iter_resource_definitions()` and `build_row_data_from_containers()`.
- `_iter_resource_definitions()` (line 46) — tested through row builder integration.
- `TransferViewModel.get_pending()` (line 148) — one-liner dict `.get()`. Trivial but no dedicated test (tested through `apply_arrow`/`apply_max` which read pending values).

### 25. `game/ui/services/image/openai_provider.py` (426 LOC)
**Severity: MAJOR** | Layer: UI Services | Has tests: Partial

**Covered:** The public API `generate_image()` is tested via `test_openai_provider.py`. The retry logic, status-code routing, timeout handling, and SSL error handling are all behind `generate_image()`.

**Gaps (tested only through generate_image):**
- `_read_api_key()` — raise path (no env var) tested through generate_image.
- `_build_headers()` — one-liner dict construction. Tested implicitly.
- `_post_generation()` / `_post_edit()` — HTTP calls, tested through generate_image.
- `_read_edit_file()` — file read + OSError handling. The OSError branch may not be exercised.
- `_read_actual_size()` — PIL-based PNG header decode with fallback. The PIL `Exception` branch (line 413) is likely untested.
- `__repr__` / `__str__` — key redaction. Untested.
- `__init__` — intentionally empty. Trivial.

**Recommendation:** The provider is HTTP-dependent and best tested through integration. Private helpers are thin. The key redaction in `__repr__`/`__str__` is worth a 2-line test.

---

## Tier 3 — APPARENTLY COVERED

### 26. `game/core/config.py` (207 LOC)
**Severity: ADVISORY** | Layer: Core | Has tests: Yes (16 test files reference)

Plain config classes (`DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleTuning`, `LLMConfig`, `ImageConfig`). Class-level attributes only. Resolution classmethods tested. **No action required.**

### 27. `game/core/string_utils.py` (48 LOC)
**Severity: ADVISORY** | Layer: Core | Has tests: Yes

`display_name()` and `slugify()`. Simple pure functions. **No action required.**

### 28. `game/simulation/battle_outcome.py` (203 LOC)
**Severity: ADVISORY** | Layer: Simulation | Has tests: Excellent (280 LOC test file + 18 test files reference)

DTO-only module. `ShipStatus`/`EndReason` enums, frozen dataclass shapes, field completeness. All DTOs verified as frozen. **No action required.**

### 29. `game/simulation/components/abilities/weapons.py` (386 LOC)
**Severity: MAJOR** | Layer: Simulation | Has tests: Excellent (10+ test files)

`WeaponAbility`, `ProjectileWeaponAbility`, `BeamWeaponAbility`, `SeekerWeaponAbility`. All covered by extensive modifier binding tests, weapon stats collection tests, targeting rule tests, combat lab tests. `_parse_formula_field()` extracted helper. **No action required.**

### 30. `game/simulation/services/vehicle_design_service.py` (516 LOC)
**Severity: MAJOR** | Layer: Simulation | Has tests: Yes (4 test files)

`VehicleDesignService` for ship creation, component management, validation, class changes. Covered by workshop tests, move-component tests, service injection tests. The `move_component()` BUG-116 fix (selective MassBudgetRule skip) is tested via move-component tests. **No action required.**

### 31. `game/strategy/quickstart_builder.py` (333 LOC)
**Severity: MAJOR** | Layer: Strategy | Has tests: Yes (3 test files)

`QuickstartBuilder` for 1P/2P config, design copying, complex spawning. Covered by quickstart builder tests and population seeding tests. **No action required.**

### 32. `game/strategy/services/superweapon_registry.py` (131 LOC)
**Severity: MAJOR** | Layer: Strategy | Has tests: Yes (4 test files)

`SuperweaponSpec` frozen dataclass + `SUPERWEAPONS` tuple + `find_superweapon_spec()`. Covered by superweapon dispatch, ability metadata registry, and contract tests. **No action required.**

---

## File Coverage Verification Table

| # | File | Tier | LOC | Test Files | Status | Key Gaps |
|---|------|------|-----|-----------|--------|----------|
| 1 | `game/core/component_state.py` | 2 | 102 | 14 (169 LOC dedicated) | **MINOR** | `__post_init__` not directly called |
| 2 | `game/core/config.py` | 3 | 207 | 16 | **OK** | — |
| 3 | `game/core/paths.py` | 2 | 202 | 26 | **MINOR** | `_find_project_root` error path; `get_planets_v3_dir`/`get_stars_dir` not directly tested |
| 4 | `game/core/string_utils.py` | 3 | 48 | 2 | **OK** | — |
| 5 | `game/engine/__init__.py` | 0 | 36 | 0 | **ADVISORY** | Re-exports only |
| 6 | `game/simulation/battle_outcome.py` | 3 | 203 | 18 (280 LOC dedicated) | **OK** | — |
| 7 | `game/simulation/combat/families/__init__.py` | 0 | 13 | 0 | **ADVISORY** | Re-exports only |
| 8 | `game/simulation/combat/formation.py` | 2 | 416 | 11 (216 LOC dedicated + more) | **MINOR** | Unknown-shape fallback untested; `_symmetric_y` count=1 not isolated |
| 9 | `game/simulation/components/abilities/base.py` | 2 | 535 | 26 | **MINOR** | `_parse_attrs` no-op not directly tested |
| 10 | `game/simulation/components/abilities/weapons.py` | 3 | 386 | 10 | **OK** | — |
| 11 | `game/simulation/entities/stat_contributors/launch.py` | 0 | 118 | 1 (119 LOC dedicated) | **CRITICAL** | `contribute_tactical_satellite_launch` and `contribute_vehicle_bay` untested |
| 12 | `game/simulation/interfaces/component_protocols.py` | 0 | 226 | 0 | **CRITICAL** | No dedicated test; TypeGuard and Protocol conformance unverified |
| 13 | `game/simulation/services/vehicle_design_service.py` | 3 | 516 | 4 | **OK** | — |
| 14 | `game/simulation/systems/battle_engine.py` | 2 | 758 | 17 | **MAJOR** | `remove_ship`, `get_ship_by_name`, `shutdown` not individually tested |
| 15 | `game/strategy/data/deployed_group.py` | 2 | 424 | 22 (indirect) | **MAJOR** | No dedicated test file; `_register_type`, `__eq__`, `__hash__`, `_decode_location` error path untested |
| 16 | `game/strategy/engine/population_engine.py` | 2 | 177 | 4 (692 LOC dedicated) | **MINOR** | `_process_empire`/`_process_colony` tested through public API |
| 17 | `game/strategy/engine/production_spawner.py` | 2 | 667 | 3 (582 LOC dedicated) | **MAJOR** | `_spawn_fleet_carried_vehicle` error paths untested |
| 18 | `game/strategy/facade/slices/economy_slice.py` | 0 | 188 | 0 | **CRITICAL** | No test file; 103 LOC `get_colony_demographic_view` completely untested |
| 19 | `game/strategy/generation/loaders/__init__.py` | 0 | 7 | 0 | **ADVISORY** | Re-exports only |
| 20 | `game/strategy/quickstart_builder.py` | 3 | 333 | 3 | **OK** | — |
| 21 | `game/strategy/services/superweapon_registry.py` | 3 | 131 | 4 | **OK** | — |
| 22 | `game/ui/panels/modifier_impact_grid.py` | 2 | 514 | 1 | **ADVISORY** | UI rendering |
| 23 | `game/ui/screens/builder/modifier_row.py` | 2 | 355 | 3 | **ADVISORY** | UI rendering |
| 24 | `game/ui/screens/fleet_menu_items.py` | 2 | 274 | 2 (615 LOC dedicated) | **MINOR** | All helpers tested through public API |
| 25 | `game/ui/screens/planet_selection_window.py` | 2 | 262 | 1 | **ADVISORY** | UI rendering |
| 26 | `game/ui/screens/race_setup/ship_preview.py` | 0 | 163 | 0 | **ADVISORY** | UI rendering |
| 27 | `game/ui/screens/star_list_window.py` | 2 | 554 | 6 | **ADVISORY** | UI rendering |
| 28 | `game/ui/screens/strategy_renderer.py` | 2 | 288 | 4 | **ADVISORY** | UI rendering |
| 29 | `game/ui/screens/strategy_superweapons.py` | 2 | 416 | 2 | **ADVISORY** | UI orchestration |
| 30 | `game/ui/screens/test_lab/renderer/validation_panel.py` | 0 | 230 | 0 | **ADVISORY** | UI rendering |
| 31 | `game/ui/screens/transfer_view_model.py` | 2 | 325 | 6 (89 LOC dedicated) | **MINOR** | Module-level helpers tested indirectly |
| 32 | `game/ui/services/image/openai_provider.py` | 2 | 426 | 1 | **MAJOR** | HTTP-dependent; `__repr__`/`__str__` key redaction untested |

---

## Prioritized Remediation Plan

### Immediate (CRITICAL — Tier 0 non-UI, no tests)

1. **`economy_slice.py` (P0)** — 188 LOC with no tests. `get_colony_demographic_view()` is the heaviest untested business logic in the shard. Write `tests/unit/strategy/facade/slices/test_economy_slice.py` with ~8 test cases covering species iteration, surplus capping, unknown race_id skip, unowned planet None-return, race_registry lazy-init, and economy_config fallback.

2. **`launch.py` (P1)** — 2 of 3 functions untested. Add `test_contribute_tactical_satellite_launch` and `test_contribute_vehicle_bay` cases to `tests/unit/simulation/entities/stat_contributors/test_launch.py`. ~6 tests, ~60 LOC.

3. **`component_protocols.py` (P1)** — Protocol conformance untested. Write `tests/unit/simulation/interfaces/test_component_protocols.py` with `isinstance(Component(...), IComponent)`, `is_component` TypeGuard narrowing, and negative test.

### Short-term (MAJOR — Tier 2, partial coverage)

4. **`deployed_group.py` (P2)** — No dedicated test file. Write `tests/unit/strategy/data/test_deployed_group.py` covering `_register_type` registry, `from_dict` with unknown type, `_decode_location` error path, `__eq__`/`__hash__` semantics, and `_from_dict_payload` base raise.

5. **`battle_engine.py` (P2)** — `remove_ship()` and `get_ship_by_name()` are low-hanging unit test targets (~4 tests).

6. **`production_spawner.py` (P2)** — `_spawn_fleet_carried_vehicle()` error paths (no bay capacity, unknown type, missing registries) need explicit coverage.

### Low-priority (MINOR / ADVISORY)

7. **`openai_provider.py` (P3)** — Test `__repr__`/`__str__` key redaction (2 lines).
8. **`paths.py` (P3)** — Test `_find_project_root` error path.
9. **`formation.py` (P3)** — Test unknown shape fallback to LINE_ASTERN.
