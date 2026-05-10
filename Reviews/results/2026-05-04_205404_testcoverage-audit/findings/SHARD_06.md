# Test Coverage Audit — Shard 06 Findings

**Scope:** 47 production files, ~8495 LOC  
**Audit date:** 2026-05-04  
**Methodology:** Exhaustive read of every production file, cross-referenced against coverage matrix and test files. File-level verification performed on all 47 files.

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 4 | Tier 0 non-UI files with zero unit tests |
| MAJOR    | 9 | Tier 1 files or high-impact untested functions |
| MINOR    | 25+ | Partially tested functions missing branches/error paths |
| ADVISORY | 14 | UI rendering/event code, `__init__.py` re-exports |

**Overall assessment:** Shard 06 has **critical gaps** in strategy-layer command handlers (`movement.py`, `order_queue.py`) and replay serialization (`replay_record.py`). These are high-impact production files handling fleet commands and battle replay persistence — both have zero unit tests. The simulation and UI layers have better coverage but still show significant gaps, especially in telemetry subscriber methods and rendering functions.

---

## Tier 0 — CRITICAL (Non-UI Files with Zero Tests)

### 1. `game/simulation/managers/__init__.py` (12 LOC) — Tier 0, Zero Tests
**Severity:** ADVISORY (re-export module)

Re-exports `RetreatManager`, `RetreatState`, `RetreatMethod`, `BattleStateManager`. No executable logic. While Tier 0, this is a pure re-export `__init__.py` — tested implicitly through the sub-module test files.

- Lines 9-11: Re-exports from `.retreat_manager` and `.battle_state_manager`
- **Gap:** No explicit test validates the `__all__` list completeness.
- **Verdict:** ADVISORY. Low priority.

---

### 2. `game/simulation/replay/replay_record.py` (93 LOC) — Tier 0, Zero Tests
**Severity:** CRITICAL

Frozen dataclass `ReplayRecord` with serialization/deserialization and schema-version checking. This is the persisted-on-disk form of battle replays — PROJ-312 deliverable. Has **zero unit tests** for any of its 4 symbols.

- `ReplayRecord` (line 33): 10-field frozen dataclass with `to_dict()`, `from_dict()`, `is_current_schema()`.
- `to_dict()` (line 47): Converts `sector_coords` tuple→list, `participating_empires` tuple→list. No test validates these transformations.
- `from_dict()` (line 63): Reads all 10 fields from dict, handles `Optional` fields (`sector_name`, `sector_coords`, `turn_number`). No test validates None handling, missing-key handling, or type coercion of `sector_coords` from list.
- `is_current_schema()` (line 84): Tests `REPLAY_SCHEMA_VERSION` equality. No test covers true/false branches.
- **Error paths untested:** `sector_coords` with None vs list of 2 ints; missing `components_registry_hash` key; empty `participating_empires` tuple; edge case where `schema_version` is a different type (int vs str).

**Recommendation:** Add tests in `tests/unit/simulation/replay/test_replay_record.py` covering:
1. `to_dict()` round-trips through `from_dict()` faithfully
2. `is_current_schema()` returns True/False for matching/mismatching schema versions
3. `from_dict()` with all-optional fields (`sector_name=None`, `sector_coords=None`, `turn_number=None`)
4. `from_dict()` with empty `participating_empires` list
5. `to_dict()` validates `sector_coords` conversion from `tuple[int,int]` to `list[int,int]`

---

### 3. `game/strategy/engine/handlers/movement.py` (214 LOC) — Tier 0, Zero Tests
**Severity:** CRITICAL

Five command handlers for fleet navigation: `ColonizeCommandHandler`, `MoveCommandHandler`, `InterceptCommandHandler`, `JoinCommandHandler`, `WarpCommandHandler`. All executed through `GameSession.handle_command()` → `CommandHandlerRegistry.dispatch()`. **Zero unit tests** for any of these 10 symbols.

Each handler follows: resolve fleet → validate → apply (create + add Order). These are core gameplay paths:

- `ColonizeCommandHandler.execute()` (line 37): Fleet resolution, planet resolution, colonize validation, auto-MOVE prefix if not at planet, colonize target construction with population/cargo amounts. **Untested branches:** fleet not found; planet not found; validation failure; already-at-planet skip of move order; colonize target with cmd.population_amount/cargo_resources.
- `MoveCommandHandler.execute()` (line 75): Fleet resolution, path preview, unreachable-target error, path optimization for first order. **Untested branches:** fleet=location no-op; unreachable target; path=[] validation error; single-order path optimization.
- `InterceptCommandHandler.execute()` (line 109): Fleet resolution, self-targeting guard (PROJ-222), pursuer registration. **Untested branches:** self-target returns error; fleet not found; pursuer_tracker.add_pursuer side effect.
- `JoinCommandHandler.execute()` (line 139): Fleet resolution, self-targeting guard, same-empire guard, creates MOVE_TO_FLEET + JOIN_FLEET orders, pursuer registration. **Untested branches:** self-target; cross-empire; missing target fleet.
- `WarpCommandHandler.execute()` (line 177): Fleet resolution, warp capability check with limiting-ship detail, warp point existence, auto-MOVE prefix (PROJ-204 Phase 3). **Untested branches:** no warp capability; warp point not at hex; auto-MOVE failure; ship with warp capability but insufficient tonnage.

**Recommendation:** Add tests in `tests/unit/strategy/engine/handlers/test_movement.py` covering all 5 handlers with happy-path + error-path scenarios. Mock `GameSession` and `Fleet` objects. Each handler has 3-7 distinct branches.

---

### 4. `game/strategy/engine/handlers/order_queue.py` (212 LOC) — Tier 0, Zero Tests
**Severity:** CRITICAL

Five command handlers for order-list manipulation: `ColonizeMissionCommandHandler`, `ClearOrdersCommandHandler`, `SplitFleetCommandHandler`, `DeleteOrderCommandHandler`, `ReorderOrderCommandHandler`. **Zero unit tests** for any of these 10 symbols.

These handlers mutate fleet orders and composition — bugs here can orphan ships or corrupt order queues:

- `ColonizeMissionCommandHandler.execute()` (line 37): Fleet resolution, planet resolution, move-if-needed with chain detection (PROJ-207 Phase 5), colonize target construction. **Untested branches:** None planet (any-planet mode); missing planet; move failure.
- `ClearOrdersCommandHandler.execute()` (line 75): Fleet resolution, `fleet.clear_orders()` side effect. **Untested branches:** fleet not found.
- `SplitFleetCommandHandler.execute()` (line 92): Ship resolution by instance_id, ship-not-found error, at-least-one-remaining validation, empire-based new-fleet-ID generation, ship movement between fleets, empire fleet registration. **CRITICAL:** This handler creates a new `Fleet` object (line 133) with late-import — complex state mutation with 6 distinct error paths. **Untested branches:** empty ship list; ship not found; less than 1 ship remaining; invalid owner_id; overlap between moved and remaining; galaxy/empire registration side effects.
- `DeleteOrderCommandHandler.execute()` (line 156): Order-index validation, `fleet.remove_order_at()` with pursuer cleanup. **Untested branches:** negative index; index beyond orders; active order (index 0) path invalidation.
- `ReorderOrderCommandHandler.execute()` (line 180): Index validation, direction validation (-1 or 1 only), target-index boundary check, order swap, active-order path invalidation. **Untested branches:** invalid direction (not -1 or 1); target out of bounds; index 0 affected (path cleared); index 0 not affected.

**Recommendation:** Add tests in `tests/unit/strategy/engine/handlers/test_order_queue.py`. Pay special attention to `SplitFleetCommandHandler` — the most complex handler with the highest risk of state corruption.

---

## Tier 0-1 — UI/Constants Files (ADVISORY/MINOR)

### 5. `game/ui/renderer/__init__.py` (0 LOC) — Tier 1
**Severity:** ADVISORY
Zero-length file. No content to test. The coverage matrix shows this as Tier 1 due to candidate test file `tests/unit/test_app_bootstrap_invariants.py` but no symbols exist.

### 6. `game/ui/screens/builder/__init__.py` (7 LOC) — Tier 0
**Severity:** ADVISORY
Re-exports 7 symbols from builder sub-modules. Zero tests. Pure re-export `__init__.py` — tested implicitly through module import chains.

### 7. `game/ui/screens/strategy_render/__init__.py` (9 LOC) — Tier 0
**Severity:** ADVISORY
Docstring-only package init (no re-exports). Intentional design choice per PROJ-309 sub-phase 3.2. No testable content.

### 8. `game/ui/services/image/__init__.py` (62 LOC) — Tier 1
**Severity:** ADVISORY
Package `__init__.py` with re-exports + side-effect `register_image_provider("null", ...)`. Has 6 candidate test files exercising the sub-modules. The side-effect on line 42 (factory registration) is tested indirectly through default-provider and factory tests.

---

## Tier 1 — Low-Symbol Files with Candidate Tests

### 9. `game/core/ship_classes.py` (59 LOC) — Tier 1
**Severity:** MINOR

Two module-level constants: `FLEET_ICON_SHIP_CLASS` (`str`) and `SHIP_CLASSES_WITH_VISUAL_THEMES` (`frozenset[str]` of 19 ship-class display names). Has 5 candidate test files (`test_ship_classes.py`, `test_codex_ship_theme_creator_skill.py`, `test_regenerate_ship_portraits.py`, `test_ship_theme_manager.py`, `test_theme_discovery.py`) but the coverage scanner found 0 tested symbols (no functions/classes, only constants).

- `FLEET_ICON_SHIP_CLASS` (line 16): Used by `RaceAssetLoader` for fleet icon skin lookup. Constant; no direct test validates the value `"Battle Cruiser"`.
- `SHIP_CLASSES_WITH_VISUAL_THEMES` (line 26): 19-entry frozenset. Tested indirectly through theme discovery but no test validates:
  - The frozenset contains exactly 19 entries
  - Every entry matches a valid ship class display name
  - The set is immutable (frozenset, not set)

**Verdict:** Low severity. Constants are used correctly by consuming code. Adding a direct validation test would prevent accidental drift.

### 10. `game/ui/screens/galaxy_test/constants.py` (32 LOC) — Tier 1
**Severity:** ADVISORY

Module-level constants (`SIDEBAR_WIDTH`, `HEX_SIZE`, `PLANET_TYPE_COLORS` dict). Has test file but 0 direct symbols. Constants are tested indirectly when used in `test_galaxy_test_screen.py`.

---

## Tier 2 — Detailed Gaps (MAJOR/MINOR)

### 11. `game/core/math.py` (280 LOC) — 10 Untested Symbols
**Severity:** MINOR

`Vector2` class (186 lines) plus 5 free functions. Coverage matrix reports 10 untested dunder/helper methods:

- `__add__` (line 49), `__radd__` (line 53), `__sub__` (line 57), `__rsub__` (line 61), `__mul__` (line 65), `__rmul__` (line 69), `__truediv__` (line 73), `__neg__` (line 77), `__iter__` (line 91)
- `normalize_angle()` (line 235)

**Analysis:** The Vector2 dunders are exercised indirectly through higher-level code (Vector2 operations appear in 59+ test files). The gap is that no test file specifically validates each dunder method with edge cases:
- `__add__` with non-Vector2 x.y objects
- `__mul__` / `__truediv__` with zero/negative scalars
- `__iter__` yielding (x, y) correctly for tuple unpacking
- `normalize_angle()` edge cases: 0, 180, -180, 360, -360, very large values, float precision near boundaries

**Verdict:** MINOR. The dunders are exercised in practice. `normalize_angle()` has 0 direct tests in `tests/unit/core/math_utils/test_helpers.py` (which covers `clamp`, `lerp`, `angle_diff`, `angle_from_vector`) — it's the only free function in math.py not directly tested.

---

### 12. `game/simulation/combat/telemetry.py` (372 LOC) — 3 Untested Symbols
**Severity:** MAJOR

Three telemetry subscribers: `WeaponSummaryAggregator`, `ShipStatsAggregator`, `HitLogRecorder`. Coverage matrix reports 3 untested private methods:

- `ShipStatsAggregator._on_damage_event()` (line 148): Subscribes to SHIELD_HIT/ARMOR_ABSORBED/COMPONENT_HIT events. Untested branches: `target_ship=None`, `instance_id=None`, `damage<=0`, cumulative damage accumulation.
- `HitLogRecorder._on_hit_event()` (line 275): Subscribes to hit events, extracts attacker weapon/ability metadata. Untested branches: `target=None`, `instance_id=None`, `context=None`, `attacker=None`, `source_weapon=None`, `WeaponAbility` not found in abilities list, fallback to `damage_type`.
- `HitLogRecorder._trace_modifiers_for_team()` (line 325): Modifier tracing for DETAILED telemetry. Untested branches: `stack=None`, empty `global_`, `attacker_team_id=None`, `per_team` empty dict, placeholder effects filtering (stat_key empty or "placeholder").

**Analysis:** The existing tests (`test_telemetry.py`, `test_ship_stats_aggregator.py`, `test_hit_log_recorder.py`) exercise the public API (`snapshot()`, `sample_tick()`, `get_stats()`) but leave the private subscriber callbacks and modifier-trace logic under-tested.

**Recommendation:** Add unit tests directly invoking `_on_damage_event()`, `_on_hit_event()`, `_trace_modifiers_for_team()` with mock `CombatEvent` and `ModifierStack` objects to cover all None/boundary branches.

---

### 13. `game/simulation/entities/projectile.py` (190 LOC) — 1 Untested Symbol
**Severity:** MAJOR

`Projectile` — physics body for missiles, beams, and ballistic projectiles. Coverage matrix reports `Projectile._update_guidance()` untested.

- `_update_guidance()` (line 121-183): Core missile guidance algorithm — lead computation via `solve_lead()`, desired direction normalisation, turn-rate clamping, turn-commitment threshold logic (lines 174-175), turn-direction state machine. **Complex math with multiple branches:**
  - `owner=None` / `owner.combat_engine=None` → direct pursuit (t=0)
  - `t>0` → predictive lead targeting
  - `desired_vec.length_squared()=0` → no-op
  - Turn rate clamping: `abs(angle_diff) > max_turn_step`
  - Turn commitment: `abs(abs(angle_diff) - 180) < 45` with stored direction
  - `last_turn_direction` state machine (1/-1)
  - `turn_rate=0` → no rotation (straight line)
  - `max_speed=0` edge case

**Analysis:** Tested only indirectly through `test_projectile.py` and `test_guidance_behavior.py`. No direct test validates tracked missile turning past 180°, commitment logic preventing oscillation, or the edge case where `target.is_alive=False` mid-guidance.

**Recommendation:** Add tests in `tests/unit/simulation/entities/test_projectile.py` that directly invoke `_update_guidance()` with controlled positions and validate heading changes at each branch point.

---

### 14. `game/strategy/data/design_metadata.py` (294 LOC) — 1 Untested Symbol
**Severity:** MINOR

`_calculate_construction_cost_from_ship()` (line 260): Iterates ship layers and components, summing `comp.cost` which can be `dict` (resource→amount) or `int`/`float` (assumed minerals). Untested branches:
- Component with `dict` cost (multi-resource)
- Component with `int` cost (single "minerals")
- Component with `float` cost (fractional minerals)
- Component with `0` cost (no contribution)

Existing tests (`test_design_metadata_validation.py`, `test_design_metadata_mass_valid.py`) focus on `from_design_file()` and `from_dict()` but don't cover cost calculation from Ship objects.

---

### 15. `game/strategy/data/fleet_capability_calculator.py` (264 LOC) — 3 Untested Symbols
**Severity:** MAJOR

- `_get_ship_component_registry()` (line 18): Module-level helper. Untested branches: `ship._registries is None`, `hasattr` false.
- `_get_registry()` (line 118): Instance method with 3-tier fallback (constructor injection → ship registries → ValueError). Untested branches: empty fleet (no combat ships), all ships missing `_registries`.
- `list_abilities()` (line 244): Aggregates unique abilities across all combat ships. Untested branches: empty fleet; ships with overlapping abilities (set dedup); ships with zero abilities.

---

### 16. `game/strategy/data/naming.py` (93 LOC) — 1 Untested Symbol
**Severity:** MINOR

`NameRegistry.__init__()` (line 13): Constructor with optional `data_file_path`. Untested branches: `data_file_path=None` (no load), `data_file_path` provided (loads YAML). The test file `test_naming.py` covers `get_system_name()`, `to_roman()`, and `load_data()` but the constructor's branch is exercised only incidentally.

---

### 17. `game/strategy/data/star_generation_config.py` (194 LOC) — 3 Untested Symbols
**Severity:** MAJOR

`StarGenerationConfig` loads astrophysics.json star generation parameters. The `__init__`, `_load_from_json()`, and `_use_defaults()` are classified as untested:
- `__init__()` (line 90): Branch: `data and "star_generation" in data` → `_load_from_json()` or `_use_defaults()`. No test directly validates this branch.
- `_load_from_json()` (line 102): Reads 5 sub-sections (type_weights, mass_generation, system_probabilities, companion_spacing, stefan_boltzmann_types) each with `.get()` fallback chains. No test validates partial JSON (some sections present, others missing).
- `_use_defaults()` (line 153): Assigns all 5 default blocks. No test validates default values match `DEFAULT_*` dictionaries.

Existing test `test_star_generation_config.py` tests `get_star_generation_config()` (cached factory function) but only covers the factory wrapper, not the config class internals.

---

### 18. `game/strategy/engine/turn_state_snapshot.py` (134 LOC) — 1 Untested Symbol
**Severity:** MAJOR

`dump_crash_snapshot()` (line 102): Crash forensics — writes a JSON crash dump to disk. Untested entirely. This is the error-recovery path for turn engine failures (PROJ-251 Phase 4). Branches:
- `error_info.get('tick', '?')` with missing tick key
- `os.makedirs(save_path, exist_ok=True)` already-exists path
- `json.dump` failure (TypeError)
- `OSError` on file write

**Recommendation:** Test with mock `open`/`os.makedirs` to validate crash snapshot content, filename generation, and error resilience.

---

### 19. `game/strategy/facade/dto/fleet_dto.py` (235 LOC) — 1 Untested Symbol
**Severity:** MINOR

`FleetInfo._aggregate_carried_items()` (line 222): Aggregates `carried_items` across all ships by (name, vehicle_type, mass). Untested branches:
- Ship with empty `carried_items` list
- Multiple ships carrying same item type (count aggregation)
- Item with missing `name`/`vehicle_type`/`mass` keys (`.get()` fallback to "Unknown"/0.0)

Existing tests (`test_fleet_dto_build.py`, `test_fleet_dto_capabilities.py`) cover `from_fleet()` but don't exercise `_aggregate_carried_items()` with diverse carried-item scenarios.

---

### 20. `game/ui/components/filters/tri_state_widget.py` (128 LOC) — 3 Untested Symbols
**Severity:** MINOR (UI widget, but has state logic)

- `__init__()` (line 22): Creates 4 pygame_gui widgets. Covers `_update_visuals()` call on line 68.
- `check_pressed()` (line 85): Two-mode dispatcher — event-based (`element=`) and polling (no args). Untested branches: element is None (polling mode); element matches one of three buttons; element doesn't match any button.
- `_update_visuals()` (line 117): Select/unselect button visual state. Has `FilterState.YES/NO/IGNORE` → button mapping.

The test `test_tri_state_widget.py` covers `set_state()`, `current_state`, `attribute_name`, `kill()`. The constructor and `check_pressed` polling-mode branch are tested implicitly but not explicitly.

---

## Tier 3 — Appears Covered (Verified Claims)

### 21-27: Verified Coverage

The following Tier 3 files were verified through source code reading and test file existence checks:

| File | LOC | Symbols | Test Files | Status |
|------|-----|---------|------------|--------|
| `game/core/patterns/layer_iterator.py` | 162 | 6/6 tested | `test_layer_iterator.py` | Covered |
| `game/simulation/components/modifier_introspection.py` | 311 | 6/6 tested | `test_modifier_introspection.py`, `test_component/test_modifier_introspection.py` | Covered |
| `game/strategy/engine/production_math.py` | 39 | 1/1 tested | `test_production_math.py` | Covered |
| `game/strategy/engine/turn_engine_config.py` | 53 | 1/1 tested | `test_turn_engine_config.py`, `test_turn_engine_init_precedence.py` | Covered |
| `game/strategy/generation/density/primitives/radial.py` | 61 | 2/2 tested | `test_radial.py`, `test_density_map.py` | Covered |
| `game/ui/components/table/selection.py` | 138 | 22/22 tested | `test_selection.py`, `test_virtual_table.py` | Covered |
| `game/ui/screens/race_setup/delegate_factory.py` | 87 | 3/3 tested | `test_race_setup_delegate_factory.py` | Covered |
| `game/ui/widgets/dropdown_helper.py` | 52 | 1/1 tested | `test_dropdown_helper.py` | Covered |

---

## UI Files — Additional Gaps (ADVISORY)

The following UI files have untested methods primarily related to pygame_gui widget construction, event handling, and rendering. These are classified ADVISORY per methodology.

### 22. `game/ui/panels/race_environment_panel.py` (337 LOC) — 4 Untested
- `_create_content()` (line 90): Layout orchestration — creates all child widgets. Untested directly.
- `_create_repro_and_happiness()` (line 149): Slider + label construction.
- `_create_factor_rows()` (line 198): Iterates factor registry to create `PreferenceRow` instances.
- `_on_row_change()` (line 276): Callback writes preference into config.
**Existing tests:** `test_race_environment_panel.py`, `test_race_setup_screen.py` cover `update_config()`, `set_from_config()`, `apply_homeworld_preset()`.

### 23. `game/ui/panels/ship_stats_renderer.py` (440 LOC) — 7 Untested
All 7 untested symbols are pure rendering functions (`draw_weapon_entry`, `draw_component_entry`, `draw_ship_info_header`, `draw_ship_vitals`, `draw_fleet_bonuses`, `draw_ship_weapons`, `draw_ship_components`). These call `pygame.draw.rect`, `font.render`, `surface.blit` — pure rendering code, ADVISORY.
**Existing test:** `test_ship_stats_renderer.py` covers helper functions (`get_component_status_display`, `get_hp_bar_color`, `draw_stat_bar`, `draw_ship_resources`, `draw_ship_combat_stats`).

### 24. `game/ui/panels/system_tree_panel.py` (719 LOC) — 10 Untested
- `SystemTreeItem`: `add_child`, `set_expanded`, `set_position`, `show`, `hide` — widget manipulation methods.
- `SystemTreePanel`: `_get_empire_context`, `layout`, `_hide_recursive`, `process_event`, `set_dimensions` — rendering + event handler.
**Existing tests:** `test_system_tree_panel_characterization.py`, `test_system_tree_panel_hazard.py` cover `set_items()`, `on_click()`, effect formatting. The untested methods are tree-layout plumbing.

### 25. `game/ui/screens/build_queue_list_window.py` (221 LOC) — 5 Untested
- `BuildQueueRow` (line 28): Data-only frozen dataclass. ADVISORY.
- `BuildQueueRowCollector._rows_from_owner()` (line 62): Row construction from queue iterable.
- `BuildQueueListUiBuilder` (line 79): Widget builder — creates `UILabel` per row.
- `BuildQueueListWindow.rebuild_list()` (line 184): Refreshes list via builder.
- `BuildQueueListWindow.process_event()` (line 207): Event dispatch to `_handle_keydown`.
**Existing test:** `test_build_queue_list_window.py` covers `BuildQueueRowCollector.collect()` and the test-fixture pattern (`MockBuildQueueListUiBuilder`).

### 26. `game/ui/screens/build_queue_screen.py` (658 LOC) — 15 Untested
Majority untested: constructor, validation, event handlers, button dispatch, drag operations, keyboard input. This is the full-screen MVVM build queue interface. Has 1 test file (`test_sub_window_hotkeys.py`) which only covers hotkey handling.
**Existing tests:** Thin. The screen's business logic is delegated to `BuildQueueController` and `BuildQueueDragHandler` which have their own tests. But the screen-level orchestration (event routing, command dispatch, queue source refresh) is untested.

### 27. `game/ui/screens/builder/stats_config.py` (245 LOC) — 2 Untested
- `load_stats_config()` (line 45): Loads from `data/stats_layout.json`, builds `StatDefinition` objects.
- `load_sections_config()` (line 123): Loads from `data/stats_sections.json`, builds `SectionDefinition` objects.
**Existing tests:** `test_ui_stats.py`, `test_stats_visibility.py` cover `STATS_CONFIG` globals and `resolve_section_visibility()`. The load functions are implicitly tested through module-level globals but not directly with file-system mocking.

### 28. `game/ui/screens/gravity_target_editor.py` (220 LOC) — 9 Untested, Tier 0
Full pygame_gui modal window for planet gravity editing. All 9 symbols untested: class, constructor, `_build_ui`, `update`, `_button_handlers`, `_on_apply`, `_set_species_ideal`, `_set_match_current`, `_clear_target`.
**Verdict:** ADVISORY. Pure pygame_gui widget construction + simple slider reading. The math (g↔m/s² conversion) is simple.

### 29. `game/ui/screens/list_data_source_base.py` (104 LOC) — 11 Untested, Tier 0
Abstract base class `ListDataSource` implementing `ITableDataSource` protocol. Core data plumbing for `PlanetDataSource` and `StarDataSource` (PROJ-319 DUP-X-14 extraction). All 11 symbols untested.
**Verdict:** MAJOR (Tier 0 non-UI logic). This is pure-Python data source logic with no pygame dependency. Methods like `_extract_value()` (line 80) have complex branch logic (func, attr with dot-path, fmt formatting) that should be tested independently of subclasses.

### 30. `game/ui/screens/new_game_setup_ui_builder.py` (41 LOC) — 2 Untested, Tier 0
Thin seam builder — delegates to `screen._create_ui()`. ADVISORY. Tested through `MockNewGameSetupUiBuilder` fixture pattern from PROJ-328.

### 31. `game/ui/screens/race_setup/renderer.py` (234 LOC) — 3 Untested
- `close_save_update_dialog()` (line 131): Widget cleanup.
- `close_llm_dialog()` (line 182): Widget cleanup.
- `close_llm_error_popup()` (line 222): Widget cleanup.
**Existing tests:** `test_race_setup_screen.py` covers `show_save_update_dialog()` and ship preview. Close methods are simple widget.kill() + None-assignment — ADVISORY.

### 32. `game/ui/screens/race_setup/ui_builder.py` (42 LOC) — 2 Untested, Tier 0
Thin seam builder — delegates to `screen._create_ui()`. ADVISORY. Same pattern as `new_game_setup_ui_builder.py`.

### 33. `game/ui/screens/settings_window.py` (109 LOC) — 5 Untested, Tier 0
Settings modal window with brightness slider. All 5 symbols untested. Pure pygame_gui code — ADVISORY.

### 34. `game/ui/screens/strategy_render/fleets.py` (120 LOC) — 2 Untested, Tier 0
`draw_fleets()` (line 16) and `draw_fleet_path()` (line 83) — pure rendering code. Camera transforms, hex-to-pixel, fleet icon scaling, path-segment drawing. ADVISORY.

### 35. `game/ui/screens/strategy_screen_lifecycle.py` (148 LOC) — 8 Untested, Tier 0
Lifecycle/menu helpers extracted from `strategy_screen.py` (PROJ-330). All 8 functions untested:
- `on_design_click()` (line 27): Scene callback dispatch.
- `on_menu_option()` (line 40): Option switch with 6 branches.
- `show_load_game_dialog()` (line 64): Creates `SaveSelectionWindow`.
- `on_load_selected()` (line 80): Scene callback.
- `confirm_quit_to_menu()` (line 86): Creates `UIConfirmationDialog`.
- `handle_quit_confirmed()` (line 100): Scene callback.
- `show_coming_soon()` (line 107): Creates `UIMessageWindow`.
- `on_save_game_click()` (line 121): Calls `SaveGameService.save_game()`, creates message window.

**Verdict:** MAJOR (Tier 0). While these are function-shape wrappers, `on_save_game_click()` has complex logic (save success/failure paths with different UIMessageWindow content) that should be tested. `on_menu_option()` has 6 dispatch branches worthy of test coverage.

### 36. `game/ui/screens/strategy_ui.py` (415 LOC) — 35 Untested
`StrategyUI` — the main strategy screen UI class. 35 of 46 symbols classified as untested. These are almost exclusively delegation methods (to `StrategyWindowManager`, `StrategyDetailFormatter`, `StrategyEventRouter`). The MVVM decomposition means the real logic lives in helper classes; `StrategyUI` is the composition root.
**Verdict:** ADVISORY (delegation methods). EXCEPT: `__getattr__()` (line 110), `hide_ui()`/`show_ui()` (lines 167-181), `handle_resize()` (line 185), and `_update_resource_display()` (line 249) have real logic beyond delegation. `_update_resource_display()` has `hasattr` guard + resource iteration — MINOR.

### 37. `game/ui/screens/strategy_windows/fleet_report_ctrl.py` (63 LOC) — 4 Untested, Tier 0
`FleetReportRegistrar` — creates `FleetReportWindow` with `split_fleet_callback` closure capturing `facade` + `fleet_owner_id`. All 4 symbols untested.
**Verdict:** MINOR (Tier 0 but thin wrapper). The `open()` method creates a closure that dispatches `SplitFleetCommand` — this is a composition concern. Tests for `FleetReportWindow` itself exist; the registrar just wires it.

### 38. `game/ui/screens/test_lab/formatting_utils.py` (67 LOC) — 1 Untested
`_format_float()` (line 33): Internal helper called by `format_value()`. Branches:
- Integer-like float detection (line 44)
- Probability/percentage (0 < value < 1) with compact vs full precision
- Very small numbers (scientific notation) with compact vs full thresholds
- Large numbers (>=100) with compact mode
- Regular float with compact vs full precision
**Existing test:** `test_lab_formatting_utils.py` tests `format_value()` which exercises `_format_float()` indirectly. No direct test of `_format_float()` with edge cases (boundary values at 0, 1, 100, 0.001 vs 0.0001 in compact mode).

### 39. `game/ui/screens/test_lab/test_executor.py` (393 LOC) — 5 Untested
- `run_visual()` (line 76): Visual test execution — loads scenario, ensures engine, switches to battle scene.
- `run_visual_baseline()` (line 129): Baseline comparison test visual execution.
- `_run_scenario_via_run_battle()` (line 239): Core headless execution through the unified `run_battle()` entry point. Complex: `BattleStateCapture` manual enter/exit, pre_tick_loop_hook closure, outcome extraction, validation, result logging.
- `run_all()` (line 306): Batch test execution initiator.
- `continue_batch()` (line 390): Batch continuation from event loop.
**Existing tests:** `test_visual_run.py`, `test_batch_skip.py`. The core `_run_scenario_via_run_battle()` is exercised through `run_headless()` which is tested. The untested methods are either visual (pygame-dependent) or thin batch orchestration.

---

## File Coverage Verification Table

| # | File | Tier | LOC | Symbols | Tested | Untested | Severity |
|---|------|------|-----|---------|--------|----------|----------|
| 1 | `game/core/math.py` | 3→2 | 280 | 33 | 23 | 10 | MINOR |
| 2 | `game/core/patterns/layer_iterator.py` | 3 | 162 | 6 | 6 | 0 | COVERED |
| 3 | `game/core/ship_classes.py` | 1 | 59 | 0 | 0 | 0 | MINOR |
| 4 | `game/simulation/combat/telemetry.py` | 2 | 372 | 15 | 12 | 3 | MAJOR |
| 5 | `game/simulation/components/modifier_introspection.py` | 3 | 311 | 6 | 6 | 0 | COVERED |
| 6 | `game/simulation/entities/projectile.py` | 2 | 190 | 5 | 4 | 1 | MAJOR |
| 7 | `game/simulation/managers/__init__.py` | 0 | 12 | 0 | 0 | 0 | ADVISORY |
| 8 | `game/simulation/replay/replay_record.py` | 0 | 93 | 4 | 0 | 4 | **CRITICAL** |
| 9 | `game/strategy/data/design_metadata.py` | 2 | 294 | 10 | 9 | 1 | MINOR |
| 10 | `game/strategy/data/fleet_capability_calculator.py` | 2 | 264 | 13 | 10 | 3 | MAJOR |
| 11 | `game/strategy/data/naming.py` | 2 | 93 | 5 | 4 | 1 | MINOR |
| 12 | `game/strategy/data/star_generation_config.py` | 2 | 194 | 5 | 2 | 3 | MAJOR |
| 13 | `game/strategy/engine/handlers/movement.py` | 0 | 214 | 10 | 0 | 10 | **CRITICAL** |
| 14 | `game/strategy/engine/handlers/order_queue.py` | 0 | 212 | 10 | 0 | 10 | **CRITICAL** |
| 15 | `game/strategy/engine/production_math.py` | 3 | 39 | 1 | 1 | 0 | COVERED |
| 16 | `game/strategy/engine/turn_engine_config.py` | 3 | 53 | 1 | 1 | 0 | COVERED |
| 17 | `game/strategy/engine/turn_state_snapshot.py` | 2 | 134 | 4 | 3 | 1 | MAJOR |
| 18 | `game/strategy/facade/dto/fleet_dto.py` | 2 | 235 | 5 | 4 | 1 | MINOR |
| 19 | `game/strategy/generation/density/primitives/radial.py` | 3 | 61 | 2 | 2 | 0 | COVERED |
| 20 | `game/ui/components/filters/tri_state_widget.py` | 2 | 128 | 8 | 5 | 3 | MINOR |
| 21 | `game/ui/components/table/selection.py` | 3 | 138 | 22 | 22 | 0 | COVERED |
| 22 | `game/ui/panels/race_environment_panel.py` | 2 | 337 | 15 | 11 | 4 | ADVISORY |
| 23 | `game/ui/panels/ship_stats_renderer.py` | 2 | 440 | 12 | 5 | 7 | ADVISORY |
| 24 | `game/ui/panels/system_tree_panel.py` | 2 | 719 | 26 | 16 | 10 | ADVISORY |
| 25 | `game/ui/renderer/__init__.py` | 1 | 0 | 0 | 0 | 0 | ADVISORY |
| 26 | `game/ui/screens/build_queue_list_window.py` | 2 | 221 | 12 | 7 | 5 | MINOR |
| 27 | `game/ui/screens/build_queue_screen.py` | 2 | 658 | 23 | 8 | 15 | ADVISORY |
| 28 | `game/ui/screens/builder/__init__.py` | 0 | 7 | 0 | 0 | 0 | ADVISORY |
| 29 | `game/ui/screens/builder/stats_config.py` | 2 | 245 | 3 | 1 | 2 | MINOR |
| 30 | `game/ui/screens/galaxy_test/constants.py` | 1 | 32 | 0 | 0 | 0 | ADVISORY |
| 31 | `game/ui/screens/gravity_target_editor.py` | 0 | 220 | 9 | 0 | 9 | ADVISORY |
| 32 | `game/ui/screens/list_data_source_base.py` | 0 | 104 | 11 | 0 | 11 | MAJOR |
| 33 | `game/ui/screens/new_game_setup_ui_builder.py` | 0 | 41 | 2 | 0 | 2 | ADVISORY |
| 34 | `game/ui/screens/race_setup/delegate_factory.py` | 3 | 87 | 3 | 3 | 0 | COVERED |
| 35 | `game/ui/screens/race_setup/renderer.py` | 2 | 234 | 9 | 6 | 3 | ADVISORY |
| 36 | `game/ui/screens/race_setup/ui_builder.py` | 0 | 42 | 2 | 0 | 2 | ADVISORY |
| 37 | `game/ui/screens/settings_window.py` | 0 | 109 | 5 | 0 | 5 | ADVISORY |
| 38 | `game/ui/screens/strategy_render/__init__.py` | 0 | 9 | 0 | 0 | 0 | ADVISORY |
| 39 | `game/ui/screens/strategy_render/fleets.py` | 0 | 120 | 2 | 0 | 2 | ADVISORY |
| 40 | `game/ui/screens/strategy_screen_lifecycle.py` | 0 | 148 | 8 | 0 | 8 | MAJOR |
| 41 | `game/ui/screens/strategy_ui.py` | 2 | 415 | 46 | 11 | 35 | ADVISORY |
| 42 | `game/ui/screens/strategy_windows/fleet_report_ctrl.py` | 0 | 63 | 4 | 0 | 4 | MINOR |
| 43 | `game/ui/screens/test_lab/formatting_utils.py` | 2 | 67 | 2 | 1 | 1 | MINOR |
| 44 | `game/ui/screens/test_lab/test_executor.py` | 2 | 393 | 9 | 4 | 5 | MINOR |
| 45 | `game/ui/services/component_service.py` | 2 | 132 | 7 | 5 | 2 | MINOR |
| 46 | `game/ui/services/image/__init__.py` | 1 | 62 | 0 | 0 | 0 | ADVISORY |
| 47 | `game/ui/widgets/dropdown_helper.py` | 3 | 52 | 1 | 1 | 0 | COVERED |

---

## Prioritized Remediation Plan

### Priority 1 (CRITICAL — Must Fix)
1. **`game/strategy/engine/handlers/movement.py`** — 5 command handlers, zero tests. Core gameplay logic (colonize, move, intercept, join, warp). Tests needed for all error paths.
2. **`game/strategy/engine/handlers/order_queue.py`** — 5 command handlers, zero tests. `SplitFleetCommandHandler` is especially risky (fleet mutation, ship transfer, ID generation).
3. **`game/simulation/replay/replay_record.py`** — 4 symbols, zero tests. Battle replay persistence DTO. Tests needed for serialization round-trips, schema versioning, optional field handling.

### Priority 2 (MAJOR — High Impact)
4. **`game/simulation/combat/telemetry.py`** — Event subscriber callback paths (`_on_damage_event`, `_on_hit_event`, `_trace_modifiers_for_team`) need direct unit tests with mock events.
5. **`game/simulation/entities/projectile.py`** — `_update_guidance()` has complex bearing-leading algorithm with 8 branches. Needs direct tests.
6. **`game/strategy/data/star_generation_config.py`** — Config loading with JSON→defaults fallback. Needs direct constructor/loader tests.
7. **`game/strategy/engine/turn_state_snapshot.py`** — `dump_crash_snapshot()` error path untested. Crash forensics path should not silently fail.
8. **`game/strategy/data/fleet_capability_calculator.py`** — Registry resolution fallback (`_get_registry`) and `list_abilities()` need tests.
9. **`game/ui/screens/strategy_screen_lifecycle.py`** — `on_save_game_click()` has save success/failure branches. Menu dispatch has 6 branches. Worth testing despite UI-layer classification.
10. **`game/ui/screens/list_data_source_base.py`** — `_extract_value()` has complex branch logic (func, attr with dot-path, fmt). Pure Python, testable without pygame.

### Priority 3 (MINOR — Fill Gaps)
11. **`game/core/math.py`** — `normalize_angle()` and Vector2 dunders need direct edge-case tests.
12. **`game/strategy/data/design_metadata.py`** — `_calculate_construction_cost_from_ship()` dict/int/float cost handling.
13. **`game/strategy/facade/dto/fleet_dto.py`** — `_aggregate_carried_items()` missing-key handling.
14. **`game/ui/services/component_service.py`** — `__init__` None guard, `_get_provider()` wrapper.
15. **`game/ui/screens/builder/stats_config.py`** — `load_stats_config()` / `load_sections_config()` JSON loading with partial/missing data.
16. **`game/ui/screens/test_lab/formatting_utils.py`** — `_format_float()` edge cases at precision boundaries.

---

## Context Usage Estimate

**Total tokens used:** ~180,000
- Production files read: 47/47 (100%)
- Test files cross-referenced via coverage matrix: 47/47
- Key test files existence-verified: 15
- Source lines of code audited: ~8,495
