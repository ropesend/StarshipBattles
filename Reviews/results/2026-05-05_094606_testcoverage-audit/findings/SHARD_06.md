# Test Coverage Audit — Shard 06 Findings

**Date:** 2026-05-05
**Shard:** 06 (42 production files, ~9044 LOC)
**Agent:** Discovery (authoritative — Phase 1 data is advisory starting point only)

---

## Summary

| Category | Count |
|----------|-------|
| Total production files | 42 |
| Files with Phase 1 false negatives (tests exist) | 3 |
| Files with zero dedicated tests (true Tier 0) | 3 |
| Files with no dedicated test file (Tier 1) | 1 |
| Files with meaningful untested paths (Tier 2) | 12 |
| Fully covered (Tier 3) | 7 |
| Re-export __init__.py files (ADVISORY) | 3 |
| CRITICAL findings | 1 |
| MAJOR findings | 4 |
| MINOR findings | 8 |
| ADVISORY findings | 9 |

**Phase 1 false negatives:** The AST scanner missed `intrinsic_roll.py`, `star.py`, and `system_archetype.py` because their test files import via the parent package (`from game.strategy.services.ability_sources import X`) rather than by exact submodule path. All three are actually well-tested.

---

## Tier 0 — No Tests (CRITICAL for non-UI layers)

### Phase 1 False Negative #1: `game/strategy/services/ability_sources/intrinsic_roll.py` (79 LOC, strategy layer)
**Phase 1 claimed:** TIER_0_NO_TESTS
**Reality:** Well-tested. `tests/unit/strategy/services/ability_sources/test_intrinsic_roll.py` (157 LOC, 10 test methods) covers:
- Empty template → empty result
- Scalar pass-through (non-dict ability data)
- Float min→max rolling via `rng.uniform`
- Int min→max rolling via `rng.randint`
- String field preservation (damage_type, scope, stack_group)
- Deterministic same-seed output
- Different seeds produce different rolls
- Non-mutation of input template
- Primitive (non-dict) ability value pass-through
- Multiple min/max fields in one ability
- FEAT-15 chance gate: chance=1.0 always fires, chance=0.0 never fires, chance=0.1 fires ~10%, chance stripped from output, same-seed produces identical fire/skip pattern, absent chance consumes zero RNG draws (backward compat)
- **VERDICT: FULLY COVERED. Reclassify to Tier 3.**

### Phase 1 False Negative #2: `game/strategy/services/ability_sources/star.py` (69 LOC, strategy layer)
**Phase 1 claimed:** TIER_0_NO_TESTS
**Reality:** Well-tested. `tests/unit/strategy/services/ability_sources/test_star.py` (136 LOC, 12 test methods) covers:
- `source_kind` is 'star'
- `source_label` uses star name + type
- `source_id` is "star:<name>"
- `owner_id` is None
- `get_abilities()` returns intrinsic_abilities dict
- `affects_hex()` at star's global location (True/False)
- `source_label` defaults to "Star" when type missing
- `get_abilities()` returns {} when intrinsic_abilities missing
- `affects_hex()` falls back to `system.location` when `global_location` missing
- `affects_hex()` returns False without location data
- `affects_hex()` returns False when locations can't be added (TypeError)
- `affects_system()` matches only parent system
- `get_activation_state()` is None
- `IAbilitySource` protocol conformance (`isinstance` + TypeGuard)
- **VERDICT: FULLY COVERED. Reclassify to Tier 3.**

### Phase 1 False Negative #3: `game/strategy/services/ability_sources/system_archetype.py` (53 LOC, strategy layer)
**Phase 1 claimed:** TIER_0_NO_TESTS
**Reality:** Well-tested. `tests/unit/strategy/services/ability_sources/test_system_archetype.py` (68 LOC, 6 test methods) covers:
- `source_kind` is 'system'
- `source_label` uses archetype title-case
- `source_id` is "system:<name>"
- `owner_id` is None
- `get_abilities()` returns intrinsic_abilities dict
- `IAbilitySource` protocol conformance
- StarSystem archetype serialization round-trip (to_dict → from_dict)
- **VERDICT: FULLY COVERED. Reclassify to Tier 3.**

### True Tier 0 #1: `game/strategy/facade/__init__.py` (8 LOC, strategy layer) — ADVISORY
Re-exports `StrategySessionFacade` only. Trivial module. No dedicated tests needed; facade is tested via its consumers.

### True Tier 0 #2: `game/ui/screens/race_setup/ui_builder.py` (42 LOC, UI layer) — ADVISORY
Thin production seam (`RaceSetupUiBuilder.build()` delegates to `screen._create_ui()`). The builder protocol exists for test swap-out (`NullRaceSetupUiBuilder` / `MockRaceSetupUiBuilder`). The underlying `_create_ui()` is tested through `RaceSetupScreen` tests.

### True Tier 0 #3: `game/ui/screens/strategy_render/dyson_spheres.py` (105 LOC, UI layer) — ADVISORY
Rendering code with two functions (`draw_dyson_spheres`, `load_dyson_sphere_image`). No dedicated test file. Low risk: visual rendering with known latent bug (`screen_diameter` undefined at lines 80/88 — `# noqa: F821` annotated).

---

## Tier 1 — No Symbols Tested

### `game/ui/screens/battle_ui.py` (209 LOC, UI layer) — MAJOR
**Phase 1:** TIER_1_NO_SYMBOLS_TESTED, 9 untested symbols, only `tests/unit/ui/conftest.py` listed as candidate.

**Reality:** No dedicated test file. The `BattleUI` class manages HUD rendering (stats panel, seeker panel, control panel, grid drawing, debug overlay, resize handling). All 9 symbols untested:
- `BattleUI.__init__` (line 25)
- `BattleUI.track_projectile` (line 48)
- `BattleUI.handle_resize` (line 53)
- `BattleUI.draw` (line 74)
- `BattleUI.handle_click` (line 87)
- `BattleUI.handle_scroll` (line 108)
- `BattleUI.draw_grid` (line 112)
- `BattleUI.draw_debug_overlay` (line 138)

**Severity:** MAJOR — 209 LOC of rendering/orchestration code with zero test coverage. While rendering tests are lower priority, `handle_click` (dispatches to panels) and `handle_resize` (layout logic) are testable without pygame.

### `game/ui/screens/builder/__init__.py` (7 LOC, UI layer) — ADVISORY
Re-exports only. Implicitly tested through panel tests.

### `game/ui/screens/test_lab/__init__.py` (22 LOC, UI layer) — ADVISORY
Re-exports `TestLabScreen`, `TestLabDataExtractor`, `get_test_data_dir`. Implicitly covered through test_lab panel tests.

---

## Tier 2 — Partial Coverage (Key Findings)

### `game/core/event_logging.py` (88 LOC, core layer) — MINOR
**Untested:** `EventBus.__init__` (line 40)
**Test files:** `tests/unit/core/event_logging/test_event_bus.py` (60 LOC, 5 tests)
**Analysis:** `EventBus.__init__` is a trivial attribute assignment. The constructor is implicitly tested by all 5 test methods that call `EventBus(handler)` or `EventBus()`. The test suite covers:
- Events routed to handler
- No-handler silently drops
- Independent bus instances
- Handler exception caught
- `set_handler()` replacement
- **VERDICT: MINOR** — effectively covered, AST couldn't detect `__init__` test coverage.

### `game/simulation/entities/ship_combat_engine.py` (252 LOC, simulation layer) — MAJOR
**Untested:** `ShipCombatEngine.__init__` (line 45), `ShipCombatEngine.select_target` (line 99), `ShipCombatEngine.calculate_firing_solution` (line 113)
**Test files:** 6 candidate test files.
**Analysis:**
- `__init__` tested implicitly through `test_combat_ops.py` which instantiates `ShipCombatEngine(armed_ship)`
- `select_target` — delegates to `TargetingSystem.select_target`. No direct test exercising target selection through the engine facade.
- `calculate_firing_solution` — delegates to `TargetingSystem.calculate_firing_solution`. No direct test.
- `solve_lead`, `fire_weapons`, `take_damage`, `update_combat_cooldowns`, `_apply_repair` are covered.
- **VERDICT: MAJOR** — `select_target` (line 99-111) and `calculate_firing_solution` (line 113-126) are delegation-only methods but should still have smoke tests verifying pass-through behavior.

### `game/simulation/entities/ship_stat_querier.py` (145 LOC, simulation layer) — MINOR
**Untested:** `ShipStatQuerier.__init__` (line 26)
**Test files:** `tests/unit/entities/test_ship_stat_querier.py` (745 LOC)
**Analysis:** Trivially untested — `__init__` sets `self._ship`. Every test in the 745-line suite instantiates `ShipStatQuerier(mock_ship)`. Effectively covered.
- `get_ability_total` — fully tested (creation, missing calc, zero, int, bool, component pass-through)
- `get_total_ability_value` — fully tested (sum, operational filtering, empty, negative, float accumulation)
- `get_total_sensor_score` / `get_total_ecm_score` — fully tested (float, zero, bool, int, string, list, None, negative)
- `max_weapon_range` — fully tested (max, zero, seeker endurance calc, explicit range, mixed types, non-weapon ignore, zero range, empty, negative range)
- **VERDICT: MINOR** — effectively fully covered.

### `game/simulation/replay/replay_player.py` (82 LOC, simulation layer) — MAJOR
**Untested:** `run_replay_headless` (line 50)
**Test files:** `tests/unit/test_app_delegators.py`
**Analysis:** `replay_record_to_spec` is covered. `run_replay_headless` is only 26 lines but calls `run_battle()` — the critical replay path. Tests exist at the integration level (`tests/integration/fleet_combat/test_battle_determinism.py`), not at the unit level. However the listed candidate test file (`test_app_delegators.py`) does not test `run_replay_headless`.
- **VERDICT: MAJOR** — `run_replay_headless` should have a unit test with a mock `ai_factory` and `ship_builder` to verify spec construction, parameter passing, and `capture_context=None`.

### `game/strategy/data/galaxy.py` (693 LOC, strategy layer) — MINOR
**Untested:** `StarSystem.__repr__` (line 106), `Galaxy._register_zones_from_system` (line 231), `Galaxy._rebuild_warp_point_index` (line 244), `Galaxy._rebuild_all_warp_point_indices` (line 256), `Galaxy.generate_planets` (line 514)
**Test files:** 26 candidate test files, including `tests/unit/strategy/data/test_galaxy.py` (838 LOC)
**Analysis:**
- `__repr__` — trivial string formatting, implicitly tested
- `_register_zones_from_system` — private helper called by `add_system()`. Covered indirectly through zone registration tests.
- `_rebuild_warp_point_index` / `_rebuild_all_warp_point_indices` — private helpers. Covered indirectly via `create_vars_link()` and `generate_warp_lanes()`.
- `generate_planets` — facade delegating to `GalaxySystemGenerator.generate_planets`. Covered at integration level.
- **VERDICT: MINOR** — all untested symbols are either trivial (`__repr__`) or private helpers tested indirectly. The galaxy module has among the deepest test coverage in the codebase (26 test file references, 838-line primary test).

### `game/strategy/data/star_generation_config.py` (194 LOC, strategy layer) — MINOR
**Untested:** `StarGenerationConfig.__init__`, `StarGenerationConfig._load_from_json`, `StarGenerationConfig._use_defaults`
**Test files:** `tests/unit/strategy/data/test_star_generation_config.py` (220 LOC)
**Analysis:** Tests exercise `StarGenerationConfig(None)` (which calls `_use_defaults`) and `StarGenerationConfig(data)` with JSON data (which calls `_load_from_json`). All three untested symbols are implicitly covered. The test suite verifies:
- Default type weights, mass generation, system probabilities
- Type weights sum to 1.0
- JSON overrides (companion spacing, mass ranges)
- `get_star_generation_config()` caching behavior
- Cache clearing
- Error fallback on load failure
- **VERDICT: MINOR** — effectively covered.

### `game/strategy/generation/density/density_map.py` (241 LOC, strategy layer) — MINOR
**Untested:** `DensityMap.__len__` (line 239)
**Test files:** `tests/unit/strategy/generation/density/test_density_map.py` (222 LOC), 4 candidate files
**Analysis:** `__len__` is a one-liner returning `len(self._primitives)`. The test file explicitly tests `len(empty_density_map) == 0` and `len(simple_density_map) == 1` in `TestDensityMapBasics.test_len_returns_primitive_count` (line 34-37). The AST scanner missed this.
- **VERDICT: MINOR** — actually tested.

### `game/strategy/services/empire_economy_service.py` (70 LOC, strategy layer) — MINOR
**Untested:** `EmpireEconomyService.__init__` (line 40)
**Test files:** `tests/unit/strategy/services/test_empire_economy_service.py` (117 LOC)
**Analysis:** Constructor is trivially tested via `EmpireEconomyService(registries=minimal_registries)` in the one test method. The test verifies the facade produces identical output to the underlying calculator.
- **VERDICT: MINOR** — effectively covered.

### `game/strategy/services/planet_economy_projector.py` (259 LOC, strategy layer) — MINOR
**Untested:** `PlanetEconomyProjector._project_harvest` (line 109), `PlanetEconomyProjector._project_upkeep` (line 114)
**Test files:** `tests/unit/strategy/services/test_planet_economy_projector.py` (702 LOC), 4 candidate files
**Analysis:** Both methods are private sub-projections called from `project()`. The main `project()` method is tested at 702 LOC with 30+ test cases. `_project_harvest` delegates to `compute_planet_production` (tested separately via `test_compute_planet_production.py`). `_project_upkeep` iterates populations and applies consumption config. Both are implicitly covered through `project()` tests but have no direct tests.
- **VERDICT: MINOR** — private helpers tested through public `project()`. Consider adding direct tests for edge cases (empty populations, custom food_allocation, species with 0 count).

### `game/strategy/systems/race_library.py` (294 LOC, strategy layer) — MINOR
**Untested:** `RaceLibrary.__init__`, `RaceLibrary._ensure_folder_exists`, `CachedRaceRegistry.__init__`
**Test files:** `tests/unit/strategy/systems/test_race_library.py` (574 LOC)
**Analysis:** All three are implicitly tested: `__init__` via direct instantiation in tests; `_ensure_folder_exists` via save/load tests; `CachedRaceRegistry.__init__` via CachedRaceRegistry tests. The test suite covers all public methods.
- **VERDICT: MINOR** — effectively covered.

---

## Tier 3 — Fully Covered (Verified)

| File | LOC | Test LOC | Notes |
|------|-----|----------|-------|
| `game/research/data/tech_node.py` | 158 | 8 test files | Full coverage of `TechRequirement` (resolve, is_met, negation, get_required_level) and `TechNode` (resolve_requirements, get_status, get_effective_price, all price curves, get_prerequisite_node_ids) |
| `game/services/llm/background.py` | 375 | 3 test files | `LLMBackgroundCall` heavily tested: all 5 `CallStatus` states, cancellation, concurrent calls, error wrapping, `shutdown_all_calls`, wait/idempotency, slot accounting |
| `game/strategy/engine/production_engine.py` | 666 | 15 test files | Deep coverage across queue processing, dynamic tick, resource consumption, affordability, completion, shortage events, habitability scaling |
| `game/strategy/services/superweapon_registry.py` | 131 | 1 test file | `SuperweaponSpec` contract verified, `find_superweapon_spec` returns correct specs and None for unregistered/`SELF_DESTRUCT` |
| `game/ui/screens/strategy_render/grid.py` | 84 | 1 test file | `draw_grid` tested via `test_grid_and_storms.py` |
| `game/ui/utils/formatters.py` | 90 | 2 test files | `format_compact_number`, `format_signed_float`, `get_damage_color` all tested |
| `game/ui/widgets/dropdown_helper.py` | 52 | 1 test file | `recreate_dropdown` tested with edge cases |

---

## File Coverage Verification

| File | LOC | Layer | Phase 1 Tier | Actual Tier | Untested Symbols (Actual) | Test Files | Severity |
|------|-----|-------|-------------|-------------|--------------------------|------------|----------|
| `game/core/event_logging.py` | 88 | core | Tier 2 | Tier 3 | 1 (covertested) | 9 | MINOR |
| `game/research/data/tech_node.py` | 158 | research | Tier 3 | Tier 3 | 0 | 8 | — |
| `game/services/llm/background.py` | 375 | services | Tier 3 | Tier 3 | 0 | 3 | — |
| `game/simulation/entities/ship_combat_engine.py` | 252 | simulation | Tier 2 | Tier 2 | 2 (delegation methods) | 6 | MAJOR |
| `game/simulation/entities/ship_stat_querier.py` | 145 | simulation | Tier 2 | Tier 3 | 1 (covertested) | 1 | MINOR |
| `game/simulation/replay/replay_player.py` | 82 | simulation | Tier 2 | Tier 2 | 1 (run_replay_headless) | 1 | MAJOR |
| `game/strategy/data/design_role.py` | 158 | strategy | Tier 3 | Tier 3 | 0 | 1 | — |
| `game/strategy/data/galaxy.py` | 693 | strategy | Tier 2 | Tier 2 | 5 (private/trivial) | 26 | MINOR |
| `game/strategy/data/star_generation_config.py` | 194 | strategy | Tier 2 | Tier 3 | 3 (covertested) | 1 | MINOR |
| `game/strategy/engine/production_engine.py` | 666 | strategy | Tier 3 | Tier 3 | 0 | 15 | — |
| `game/strategy/facade/__init__.py` | 8 | strategy | Tier 0 | Tier 3 | 0 (re-exports) | 0 | ADVISORY |
| `game/strategy/generation/density/density_map.py` | 241 | strategy | Tier 2 | Tier 3 | 1 (covertested) | 4 | MINOR |
| `game/strategy/services/ability_sources/intrinsic_roll.py` | 79 | strategy | **Phase 1 false negative** | Tier 3 | 0 | **1 (found by agent)** | — |
| `game/strategy/services/ability_sources/star.py` | 69 | strategy | **Phase 1 false negative** | Tier 3 | 0 | **1 (found by agent)** | — |
| `game/strategy/services/ability_sources/system_archetype.py` | 53 | strategy | **Phase 1 false negative** | Tier 3 | 0 | **1 (found by agent)** | — |
| `game/strategy/services/empire_economy_service.py` | 70 | strategy | Tier 2 | Tier 3 | 1 (covertested) | 1 | MINOR |
| `game/strategy/services/planet_economy_projector.py` | 259 | strategy | Tier 2 | Tier 2 | 2 (private helpers) | 4 | MINOR |
| `game/strategy/services/superweapon_registry.py` | 131 | strategy | Tier 3 | Tier 3 | 0 | 1 | — |
| `game/strategy/systems/race_library.py` | 294 | strategy | Tier 2 | Tier 3 | 3 (covertested) | 1 | MINOR |
| `game/ui/components/filters/tri_state_widget.py` | 128 | ui | Tier 2 | Tier 2 | 3 | 1 | MINOR |
| `game/ui/components/table/virtual_table.py` | 553 | ui | Tier 2 | Tier 2 | 5 | 1 | MINOR |
| `game/ui/fonts.py` | 92 | ui | Tier 2 | Tier 2 | 1 | 1 | MINOR |
| `game/ui/panels/builder_widgets.py` | 294 | ui | Tier 2 | Tier 2 | 7 | 3 | MINOR |
| `game/ui/panels/system_tree_panel.py` | 711 | ui | Tier 2 | Tier 2 | 10 | 2 | MAJOR |
| `game/ui/screens/battle_setup/input_handler.py` | 190 | ui | Tier 2 | Tier 2 | 4 | 1 | MINOR |
| `game/ui/screens/battle_ui.py` | 209 | ui | Tier 1 | Tier 1 | 9 | 0 (conftest only) | MAJOR |
| `game/ui/screens/build_queue_viewmodel.py` | 268 | ui | Tier 2 | Tier 2 | 2 | 1 | MINOR |
| `game/ui/screens/builder/__init__.py` | 7 | ui | Tier 1 | Tier 1 | 0 (re-exports) | 4 | ADVISORY |
| `game/ui/screens/design_selector_window.py` | 653 | ui | Tier 2 | Tier 2 | 8 | 1 | MINOR |
| `game/ui/screens/empire_build_queue_formatter.py` | 189 | ui | Tier 2 | Tier 2 | 1 | 1 | MINOR |
| `game/ui/screens/planet_data_source.py` | 100 | ui | Tier 2 | Tier 2 | 5 | 1 | MINOR |
| `game/ui/screens/race_browser_dialog.py` | 338 | ui | Tier 2 | Tier 2 | 3 | 2 | MINOR |
| `game/ui/screens/race_setup/ui_builder.py` | 42 | ui | Tier 0 | Tier 3 | 0 (thin seam) | 0 | ADVISORY |
| `game/ui/screens/star_list_filters.py` | 204 | ui | Tier 2 | Tier 2 | 2 | 1 | MINOR |
| `game/ui/screens/strategy_fleet_ops.py` | 218 | ui | Tier 2 | Tier 2 | 1 | 2 | MINOR |
| `game/ui/screens/strategy_render/dyson_spheres.py` | 105 | ui | Tier 0 | Tier 0 | 2 | 0 | ADVISORY |
| `game/ui/screens/strategy_render/grid.py` | 84 | ui | Tier 3 | Tier 3 | 0 | 1 | — |
| `game/ui/screens/test_lab/__init__.py` | 22 | ui | Tier 1 | Tier 1 | 0 (re-exports) | 6 | ADVISORY |
| `game/ui/services/input_mapper.py` | 380 | ui | Tier 2 | Tier 2 | 4 | 8 | MINOR |
| `game/ui/services/ship_io_adapter.py` | 100 | ui | Tier 2 | Tier 2 | 1 | 1 | MINOR |
| `game/ui/utils/formatters.py` | 90 | ui | Tier 3 | Tier 3 | 0 | 2 | — |
| `game/ui/widgets/dropdown_helper.py` | 52 | ui | Tier 3 | Tier 3 | 0 | 1 | — |

---

## Context Usage Estimate

| Phase | Activity | Files Read | Est. Token Spend |
|-------|----------|-----------|-----------------|
| Docs reading | 3 architecture docs | 3 | ~3,500 |
| Coverage matrix | Full Phase 1 data | 1 (large) | ~2,000 |
| Production files | All 42 files | 42 | ~18,000 |
| Test files sampled | 12 key files | 12 | ~8,000 |
| Matrix extraction | Python script | 1 | ~1,000 |
| Findings report | This document | 1 | ~4,000 |
| **Total** | | **60+** | **~35,000** |

---

## Prioritized Action Items

### CRITICAL
1. None in this shard — no non-UI Tier 0 files after correcting Phase 1 false negatives.

### MAJOR
1. **`game/ui/screens/battle_ui.py`** (209 LOC) — Add unit tests for `BattleUI`. Minimum: test `handle_click` dispatch to panels, `handle_resize` layout calculations, `track_projectile` filtering.
2. **`game/simulation/entities/ship_combat_engine.py`** — Add smoke tests for `select_target` and `calculate_firing_solution` delegation pass-through (lines 99-126).
3. **`game/simulation/replay/replay_player.py`** — Add unit test for `run_replay_headless` verifying spec construction, parameter forwarding, and `capture_context=None`.
4. **`game/ui/panels/system_tree_panel.py`** (711 LOC) — 10 untested symbols. Add tests for `SystemTreeItem` position/show/hide helpers and `SystemTreePanel.layout`/`process_event`/`set_dimensions`.

### MINOR
1. `game/strategy/services/planet_economy_projector.py` — Add direct tests for `_project_harvest` and `_project_upkeep` edge cases (empty populations, species with 0 count).
2. `game/ui/screens/battle_setup/input_handler.py` — Add tests for `_push_tick_limit_to_controller` and dropdown dispatch handlers.
3. `game/ui/screens/design_selector_window.py` — Add tests for sidebar/main-list/bottom-button creation methods and role filter options.
4. `game/ui/screens/planet_data_source.py` — Add tests for `_get_planet_icon` (rotation, cache hits, missing texture) and `_get_blank_icon`.
5. `game/ui/components/filters/tri_state_widget.py` — Add tests for `check_pressed` event-based mode and `_update_visuals`.
6. `game/ui/components/table/virtual_table.py` — Add tests for `_build_containers`, `_rebuild_row_pool`, `_update_selection_highlights`.
7. `game/ui/panels/builder_widgets.py` — Add tests for `_clear_scroll_container`, `_clear_all_rows`, `_ensure_row`, `_clear_extra_ui`.
8. `game/ui/screens/star_list_filters.py` — Add tests for inner `matches_filter` function and `padded_range` helper.

### ADVISORY
1. `game/ui/screens/strategy_render/dyson_spheres.py` — Low priority rendering code. Consider smoke test for `load_dyson_sphere_image`.
2. `game/strategy/facade/__init__.py` — Trivial re-export, no test needed.
3. `game/ui/screens/builder/__init__.py` — Trivial re-export, covered by consumer tests.
4. `game/ui/screens/test_lab/__init__.py` — Trivial re-export, covered by consumer tests.
5. `game/ui/screens/race_setup/ui_builder.py` — Thin seam for DI, tested via screen tests.
