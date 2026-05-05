# Shard 11 — Test Coverage Audit Findings

**Shard**: 11
**Files in scope**: 40 production files, ~8,674 LOC
**Audit date**: 2026-05-04
**Agent**: OpenCode (discovery)

---

## Summary

| Tier | Count | Description |
|------|-------|-------------|
| **CRITICAL** (Tier 0 non-UI) | 5 files | No unit tests exist; core business logic untested |
| **ADVISORY** (Tier 0 UI / init) | 8 files | UI rendering, `__init__.py` — low risk, out of scope |
| **MAJOR** (Tier 1-2 gaps) | 5 files | Significant untested logic/error paths |
| **MINOR** (Tier 1-2 gaps) | 9 files | Partial missing branches, private methods |
| **Tier 3 Verified** | 12 files | Matrix claims covered; 1 corrected from Tier 0→3 |
| **Matrix correction** | 1 file | `superweapons.py` matrix error — tests exist |

**Overall**: 5 CRITICAL gaps, 5 MAJOR gaps, 9 MINOR gaps. Shard 11 has significant coverage gaps in the strategy `services/ability_sources/` package, `system_slice.py`, `ability_iterator.py`, `weapon_firing_system.py`, and `galaxy_warp_generator.py`.

---

## CRITICAL — Tier 0 Non-UI Files (No Tests Exist)

### 1. `game/strategy/facade/slices/system_slice.py` (132 LOC, 8 symbols)

**Layer**: Strategy | **Status**: No test file found

The `SystemSlice` is a CQRS-lite read-slice that exposes the strategy facade's system/star query API. It owns a per-turn cache for `get_all_stars()` and performs proximity-based hex→system resolution. Zero tests.

**Untested symbols**:
- `SystemSlice.__init__` (line 19) — stores facade session state
- `SystemSlice.get_all_systems` (line 26) — iterates galaxy systems → DTOs
- `SystemSlice.get_all_stars` (line 33) — turn-keyed cache, star iteration, DTO enrichment
- `SystemSlice.get_system_at_hex` (line 63) — coordinate→system resolution
- `SystemSlice.get_system_containing_fleet` (line 73) — fleet lookup + proximity fallback
- `SystemSlice.get_system_near_hex` (line 85) — strict + proximity fallback with `max_dist`
- `SystemSlice.get_storm_names_at_hex` (line 119) — storm zone spatial index query

**Risk**: High. This is the primary query API used by the UI to find what system is under a click, what stars exist, and what storms are active. Bugs here silently break the strategy UI.

**Recommended tests**: Mock `FacadeSessionState` with a `Galaxy` containing known systems + storms. Verify `get_system_at_hex` returns correct SystemInfo; `get_system_near_hex` fallback path; `get_all_stars` cache invalidation on turn change; `get_storm_names_at_hex` with empty zones.

---

### 2. `game/strategy/facade/dto/build_queue_dto.py` (41 LOC, 2 symbols)

**Layer**: Strategy | **Status**: No test file found

`BuildQueueSourceDTO` is an immutable DTO with a `from_domain` factory that copies construction queue data to prevent UI mutation of domain objects. Simple but the cloning logic (`[dict(item) for item in list(...)]`) could silently fail with malformed queue entries.

**Untested symbols**:
- `BuildQueueSourceDTO` (line 6) — frozen dataclass with 11 fields
- `BuildQueueSourceDTO.from_domain` (line 23) — copies construction_queue, build_rate, resolves entity_id/empire_id via `getattr`

**Risk**: Medium. A shallow copy bug could allow the UI to mutate domain queue data.

**Recommended tests**: Verify `from_domain` produces a DTO with detached copies (modifying the returned `construction_queue` should not affect the source). Test with missing `owner_entity` attributes (fallbacks to `entity_id=0`, `empire_id=None`).

---

### 3. `game/strategy/services/ability_sources/facility.py` (87 LOC, 9 symbols)

**Layer**: Strategy | **Status**: No dedicated test file

`FacilityAbilitySource` bridges planetary facilities to the unified `IAbilitySource` interface. Walks `design_data` layers via `iter_keyed_components`, aggregates abilities per source, and surfaces per-component activation state. Core integration seam for PROJ-300.

**Untested symbols**:
- `FacilityAbilitySource` (line 18) — frozen dataclass
- `FacilityAbilitySource.source_kind` / `source_label` / `source_id` / `owner_id` (lines 24-44)
- `FacilityAbilitySource.get_abilities` (line 46) — walks `design_data` components, aggregates abilities
- `FacilityAbilitySource.affects_hex` / `affects_system` (lines 64-72)
- `FacilityAbilitySource.get_activation_state` (line 74) — per-component activation state lookup

**Risk**: High. Facility abilities are the core mechanism for planetary defenses, stabilizers, and environment editors. Untested `get_abilities` means ability aggregation bugs go undetected.

**Recommended tests**: Mock a facility with `design_data` containing components with known abilities. Verify `get_abilities` returns correct shape; `get_activation_state` returns None for components without state; `source_label` formatting.

---

### 4. `game/strategy/services/ability_sources/system_archetype.py` (53 LOC, 9 symbols)

**Layer**: Strategy | **Status**: No dedicated test file

`SystemAbilitySource` wraps a StarSystem's archetype-based intrinsic abilities. All system archetype abilities use `scope: system`. The simplicity of the adapter doesn't excuse zero test coverage.

**Untested symbols**:
- `SystemAbilitySource` (line 14) — frozen dataclass
- `SystemAbilitySource.source_kind` / `source_label` / `source_id` / `owner_id` (lines 18-36)
- `SystemAbilitySource.get_abilities` (line 38) — returns `system.intrinsic_abilities`
- `SystemAbilitySource.affects_hex` / `affects_system` (lines 41-50)
- `SystemAbilitySource.get_activation_state` (line 52) — always returns None

**Risk**: Medium. Simple adapter but a bug in source_label formatting (archetype name) causes confusing UI display.

**Recommended tests**: Verify `get_abilities` returns the system's `intrinsic_abilities` dict; `affects_system` identity check; `owner_id` is always None; `get_activation_state` always None.

---

### 5. `game/strategy/generation/__init__.py` (23 LOC, 0 symbols)

**Layer**: Strategy | **Status**: Init-only re-export module

Re-exports `DensityMap`, placement strategies, and image registries. No testable logic. ADVISORY only — included here for completeness.

---

## CORRECTION: Matrix Error — `superweapons.py` has tests

### `game/simulation/components/abilities/superweapons.py` (116 LOC, 10 symbols)

The coverage matrix reported Tier 0 (no tests), but exhaustive verified tests exist at:
`tests/unit/simulation/components/abilities/test_superweapons.py` (162 lines, 6 test classes, 18 test methods).

Tests verify:
- All 6 abilities instantiate via registry and factory
- Layer is STRATEGIC for all
- Scope is SELF for all
- STAT_BINDINGS is empty
- `get_primary_value()` returns 0.0
- `get_ui_rows()` returns correct labels + HINT_SUPERWEAPON
- `action_time` parsing (boolean marker, dict with key, dict without key)

**Verdict**: **Tier 3 — Verified**. The matrix heuristic failed because tests access abilities via `ABILITY_REGISTRY` + `create_ability()` rather than directly importing class names from the module.

---

## MAJOR — Tier 1-2 Files with Significant Untested Logic

### 6. `game/engine/collision.py` (193 LOC, 4 symbols, 2 tested)

**Untested**: `CollisionSystem.__init__`, `CollisionSystem.process_ramming` (lines 65-67, 153-193)

`process_ramming` contains the full ramming damage resolution with three branches (rammer weaker, target weaker, mutual destruction) and is completely untested. Contains `BattleTuning` calls and `DamageContext` construction.

**Risk**: High. Ramming is an unconditional damage path — bugs cause incorrect damage or crashes.

**Recommended tests**: Test all three HP-comparison branches. Test ramming-skip conditions (dead ships, non-ramming movement policy, no target). Verify correct `DamageContext` and `take_damage` calls.

---

### 7. `game/simulation/combat/weapon_firing_system.py` (313 LOC, 9 symbols, 2 tested)

**Untested**: 7 of 9 methods — `__init__`, `_process_hangar_launch`, `_process_weapon_fire`, `_find_valid_target`, `_create_attack`, `_create_seeker_projectile`, `_create_standard_projectile` (lines 34-313)

Only `fire_weapons` has heuristic test matches. All internal weapon processing logic — target validation, PDC missile interception, beam attack creation, seeker/standard projectile construction — is untested.

**Risk**: High. This is the core weapon firing pipeline extracted from ShipCombatEngine. A bug in `_find_valid_target` (PDC context integration) or `_create_seeker_projectile` (firing arc calculation) silently breaks all combat.

**Recommended tests**: Mock TargetingSystem. Test `fire_weapons` with PDC context (enemy missiles in `projectiles` list). Test `_create_attack` for beam vs projectile path. Test `_create_seeker_projectile` firing arc calculation.

---

### 8. `game/strategy/data/galaxy_warp_generator.py` (444 LOC, 12 symbols, 1 tested)

**Untested**: 11 of 12 symbols — nearly the entire class plus module-level warp intrinsics helpers.

Only `GalaxyWarpGenerator` class itself gets a heuristic match (likely from `test_intrinsic_rng_determinism.py`). All methods untested:
- `_calculate_warp_distance` (line 28) — distance formula with star radius + jitter
- `_is_angle_clear` (line 51) — angle clearance validation
- `create_warp_link` (line 85) — bidirectional warp point creation with pixel→hex math
- `_build_edge_candidates` (line 125) — k-nearest neighbor edge construction
- `_apply_mst_edges` (line 167) — Kruskal's MST with union-find
- `_should_add_density_edge` (line 201) — region constraints, angle validation, probability
- `_add_density_edges` (line 288) — density edge iteration with inter-region tracking
- `generate_warp_lanes` (line 327) — full pipeline: spatial index → MST → density → intrinsics
- `_load_warp_point_types` (line 381) — JSON cache loading
- `_roll_warp_type` (line 407) — weighted random from `_DEFAULT_WARP_TYPE_WEIGHTS`

**Risk**: High. Galaxy generation correctness depends entirely on this class. A bug in MST ensures disconnected graphs (unreachable systems). A bug in angle validation creates overlapping warp points.

**Recommended tests**: Test MST with 3-system triangle (all connected). Test `_is_angle_clear` with known angles. Test `_roll_warp_type` determinism with seeded RNG. Test `create_warp_link` creates bidirectional points.

---

### 9. `game/strategy/services/ability_iterator.py` (316 LOC, 14 symbols, 5 tested)

**Untested**: 9 provider functions — `_facility_provider`, `_storm_provider`, `_planet_global_hex`, `_star_provider`, `_planet_intrinsic_provider`, `set_fleet_lookups`, `_fleet_provider`, `_system_archetype_provider`, `_warp_point_provider` (lines 121-316)

Only the registration API (`register_source_provider_at_hex`, `register_source_provider_in_system`, `unregister_source_provider`, `iter_ability_sources_at_hex`, `iter_ability_sources_in_system`) has test coverage. All actual provider functions that yield adapters are untested.

**Risk**: High. These providers are the integration seam for the entire ability-source framework. Every facility, storm, planet, star, warp point, fleet, and system archetype source flows through these functions.

**Recommended tests**: Test `_facility_provider` with a system containing planets with operational facilities. Test `_storm_provider` with a storm covering a hex. Test `_star_provider` with a star that has system-scope abilities (yielded for all hex queries).

---

### 10. `game/strategy/engine/component_activation_engine.py` (117 LOC, 4 symbols, 3 tested)

**Untested**: `ComponentActivationEngine._tick_facility` (lines 75-117)

The `_tick_facility` method iterates facility `component_states`, creates `ComponentActivationState` from dicts, calls `tick()`, and appends transition events to results. This is the core timer loop for all facility ability activation/deactivation.

**Risk**: Medium. `_tick_facility` is the only symbol with real logic; the tested `process_activation_tick` iterates empires but delegates all work to `_tick_facility`.

**Recommended tests**: Test `_tick_facility` with a component in ACTIVATING state — verify progress advances and transition event emitted. Test with DEACTIVATING state. Test with non-dict/state data (safe skip).

---

## MINOR — Tier 1-2 Files with Partial Coverage

### 11. `game/core/constants.py` (91 LOC, 6 symbols, 5 tested)

**Untested**: `LayerDefaults` (line 40) — three class-level float constants. MINOR. Tests exist for the constants via integration with other tests.

---

### 12. `game/strategy/data/ship_consumable_manager.py` (141 LOC, 9 symbols, 8 tested)

**Untested**: `ShipConsumableManager.__init__` (line 31) — trivial constructor storing a reference. MINOR.

---

### 13. `game/strategy/data/squadron.py` (102 LOC, 8 symbols, 7 tested)

**Untested**: `Squadron.__init__` (line 30) — calls `super().__init__` and sets spatial behavior fields. MINOR.

---

### 14. `game/strategy/engine/commands.py` (457 LOC, 41 symbols, 27 tested)

**Untested**: 14 command dataclasses/enums (lines 12-457): `TransferDirection`, `BuildEntityType`, `Command.__post_init__`, `DeleteOrderCommand`, `ReorderOrderCommand`, `RemoveFromConstructionQueueCommand`, `ReorderConstructionQueueCommand`, `IssuePlanetOrderCommand`, `ClearPlanetOrdersCommand`, `DeletePlanetOrderCommand`, `SetAtmosphereTargetCommand`, `SetGravityTargetCommand`, `SetWaterTargetCommand`, `SetRadiationShieldTargetCommand`.

**Risk**: Low. These are all dataclass definitions (no behavior). The command handlers that process them ARE tested (`test_command_handlers_public_api.py`, `test_superweapon_command_handlers.py`). The untested symbols are structural only.

**Recommended**: Verify the 4 `Set*TargetCommand` classes are exercised by integration tests.

---

### 15. `game/strategy/services/component_inspector.py` (335 LOC, 12 symbols, 6 tested)

**Untested**: `extract_abilities_from_component` (line 48), `_get_component_registry` (line 81), `get_component_type` (line 94), `get_component_threshold` (line 112), `list_ship_abilities` (line 253), `get_ability_list` (line 276).

`extract_abilities_from_component` is the most concerning — it handles both inline abilities and registry lookup by component ID, with branching for dict vs string component entries. This is the single source of truth for abilities extraction from design_data.

**Risk**: Medium. A missing branch in `extract_abilities_from_component` causes all ability-dependent validators to silently fail.

**Recommended tests**: Test `extract_abilities_from_component` with dict-comp with inline abilities; with dict-comp + id → registry lookup; with string-comp + registry lookup; with None registries.

---

### 16. `game/ui/panels/builder_widgets.py` (294 LOC, 13 symbols, 6 tested)

**Untested**: 7 modifier-editor panel internal UI methods — `__init__`, `_get_modifiers`, `set_panel_height`, `_clear_scroll_container`, `_clear_all_rows`, `_ensure_row`, `_clear_extra_ui` (lines 32-248).

All untested symbols are pygame_gui widget management methods. MINOR — UI rendering risk only.

---

### 17. `game/ui/panels/planet_report_panel.py` (673 LOC, 17 symbols, 13 tested)

**Untested**: 4 pure helper functions — `_qty_cell` (line 97), `_qual_cell` (line 106), `_flow_cell` (line 115), `_stockpile_cell` (line 129).

These are pure functions with well-defined inputs/outputs. `_projection_grid_rows` which calls them IS tested. MINOR — the helpers are indirectly tested via `_projection_grid_rows`.

---

### 18. `game/ui/panels/race_description_panel.py` (418 LOC, 11 symbols, 10 tested)

**Untested**: `RaceDescriptionPanel._tick_field_label` (line 343) — per-frame elapsed-seconds label update during LLM generation. MINOR — private method with simple guard clause.

---

### 19. `game/ui/screens/builder/structure_list_items.py` (640 LOC, 22 symbols, 9 tested)

**Untested**: 13 symbols across `IndividualComponentItem`, `LayerComponentItem`, `LayerHeaderItem` — mostly `__init__`, `update`, `_rebuild_modifier_icons`, and helper methods. These are UI widget constructors/renderers with heavy pygame_gui dependencies. MINOR — UI rendering risk.

---

### 20. `game/ui/screens/strategy_game_state_manager.py` (246 LOC, 8 symbols, 6 tested)

**Untested**: `StrategyGameStateManager.__init__` (line 35) and `_sync_active_empire` (line 71). `__init__` is trivial (stores screen reference). `_sync_active_empire` is a small method that pushes `current_player_index` into `session.active_empire`. Tested implicitly by `advance_turn` integration tests. MINOR.

---

### 21. `game/ui/screens/test_lab/viewmodel.py` (389 LOC, 47 symbols, 30 tested)

**Untested**: 6 property rects (each counted twice in matrix due to getter+setter): `run_baseline_btn_rect`, `tag_filter_rects`, `tag_clear_rect`, `seed_mode_rects`, `seed_input_rect`, `test_list_panel_rect`. These are simple `Optional[Any]` rects set by the renderer and read by the input handler. MINOR — no business logic.

---

## ADVISORY — Tier 0 UI / Init Files

These files have no tests but contain only UI rendering or package re-exports. Low risk — not required per project conventions (UI rendering is excluded from strict coverage requirements).

| File | LOC | Symbols | Risk |
|------|-----|---------|------|
| `game/ui/screens/galaxy_test/galaxy_mode.py` | 427 | 8 | UI — galaxy layout test helper with pygame_gui widget creation + rendering |
| `game/ui/screens/planet_abilities_controller.py` | 217 | 8 | Strategy domain logic exposed to UI — facade queries + command dispatch (medium risk but UI-coupled) |
| `game/ui/screens/star_list_sidebar.py` | 180 | 2 | UI — star filter sidebar builder |
| `game/ui/screens/strategy_fleet_command_router.py` | 307 | 10 | UI — fleet command routing (maps keyboard input to mode changes); some domain logic in `_handle_ability_toggle` |
| `game/ui/screens/strategy_render/hex_outlines.py` | 133 | 6 | UI — hex outline renderer with turn-keyed cache |
| `game/ui/screens/strategy_render/systems.py` | 307 | 5 | UI — star/planet/warp point rendering |
| `game/simulation/replay/__init__.py` | 82 | 0 | Init-only — re-exports from replay subpackage |
| `game/ui/screens/test_lab/renderer/__init__.py` | 13 | 0 | Init-only — re-exports TestLabRenderer |

---

## Tier 3 — Verified (Adequate Coverage)

| File | LOC | Symbols | Test Files |
|------|-----|---------|------------|
| `game/ai/protocols.py` | 125 | 13/13 | `test_ai_protocols.py` |
| `game/simulation/combat/modifier_stack.py` | 74 | 3/3 | `test_modifier_stack.py` + 14 others |
| `game/simulation/components/abilities/superweapons.py` | 116 | 10/10 | `test_superweapons.py` (**CORRECTED** from Tier 0) |
| `game/strategy/data/planet_atmosphere.py` | 177 | 5/5 | `test_calculations.py`, `test_generation.py` |
| `game/strategy/facade/dto/colony_demographic_view.py` | 95 | 3/3 | `test_colony_demographic_view.py` |
| `game/strategy/formulas/colony_output.py` | 164 | 2/2 | `test_colony_output.py` + 3 others |
| `game/strategy/services/stabilizer_registry.py` | 119 | 2/2 | `test_stabilizer_registry.py` |
| `game/ui/components/table/data_source.py` | 111 | 7/7 | `test_data_source.py` |
| `game/ui/panels/build_queue_drag_handler.py` | 350 | 7/7 | `test_build_queue_drag_handler.py` |
| `game/ui/screens/builder/event_bus.py` | 67 | 5/5 | `test_event_bus.py` + 3 others |
| `game/ui/utils/portraits.py` | 105 | 2/2 | `test_portraits.py` |

---

## File Coverage Verification Table

| File | Tier | LOC | Symbols Tested | Verdict |
|------|------|-----|---------------|---------|
| `game/ai/protocols.py` | 3 | 125 | 13/13 | VERIFIED |
| `game/core/constants.py` | 2 | 91 | 5/6 | MINOR — `LayerDefaults` constants untested |
| `game/engine/collision.py` | 2 | 193 | 2/4 | MAJOR — `process_ramming` entirely untested |
| `game/simulation/combat/modifier_stack.py` | 3 | 74 | 3/3 | VERIFIED |
| `game/simulation/combat/weapon_firing_system.py` | 2 | 313 | 2/9 | MAJOR — 7 firing methods untested |
| `game/simulation/components/abilities/superweapons.py` | 0→3 | 116 | 10/10 | **CORRECTED** — tests exist; matrix error |
| `game/simulation/replay/__init__.py` | 1 | 82 | 0/0 | ADVISORY — init-only re-exports |
| `game/strategy/data/galaxy_warp_generator.py` | 2 | 444 | 1/12 | MAJOR — near-zero coverage for complex algorithm |
| `game/strategy/data/planet_atmosphere.py` | 3 | 177 | 5/5 | VERIFIED |
| `game/strategy/data/ship_consumable_manager.py` | 2 | 141 | 8/9 | MINOR — `__init__` only |
| `game/strategy/data/squadron.py` | 2 | 102 | 7/8 | MINOR — `__init__` only |
| `game/strategy/engine/commands.py` | 2 | 457 | 27/41 | MINOR — untested dataclasses, no behavior |
| `game/strategy/engine/component_activation_engine.py` | 2 | 117 | 3/4 | MAJOR — core `_tick_facility` untested |
| `game/strategy/facade/dto/build_queue_dto.py` | 0 | 41 | 0/2 | CRITICAL — no tests |
| `game/strategy/facade/dto/colony_demographic_view.py` | 3 | 95 | 3/3 | VERIFIED |
| `game/strategy/facade/slices/system_slice.py` | 0 | 132 | 0/8 | CRITICAL — no tests |
| `game/strategy/formulas/colony_output.py` | 3 | 164 | 2/2 | VERIFIED |
| `game/strategy/generation/__init__.py` | 0 | 23 | 0/0 | ADVISORY — init-only |
| `game/strategy/services/ability_iterator.py` | 2 | 316 | 5/14 | MAJOR — 9 provider functions untested |
| `game/strategy/services/ability_sources/facility.py` | 0 | 87 | 0/9 | CRITICAL — no tests |
| `game/strategy/services/ability_sources/system_archetype.py` | 0 | 53 | 0/9 | CRITICAL — no tests |
| `game/strategy/services/component_inspector.py` | 2 | 335 | 6/12 | MINOR — `extract_abilities_from_component` untested |
| `game/strategy/services/stabilizer_registry.py` | 3 | 119 | 2/2 | VERIFIED |
| `game/ui/components/table/data_source.py` | 3 | 111 | 7/7 | VERIFIED |
| `game/ui/panels/build_queue_drag_handler.py` | 3 | 350 | 7/7 | VERIFIED |
| `game/ui/panels/builder_widgets.py` | 2 | 294 | 6/13 | MINOR — UI methods untested |
| `game/ui/panels/planet_report_panel.py` | 2 | 673 | 13/17 | MINOR — pure helpers indirectly tested |
| `game/ui/panels/race_description_panel.py` | 2 | 418 | 10/11 | MINOR — `_tick_field_label` only |
| `game/ui/screens/builder/event_bus.py` | 3 | 67 | 5/5 | VERIFIED |
| `game/ui/screens/builder/structure_list_items.py` | 2 | 640 | 9/22 | MINOR — UI widget init/update |
| `game/ui/screens/galaxy_test/galaxy_mode.py` | 0 | 427 | 0/8 | ADVISORY — UI tool |
| `game/ui/screens/planet_abilities_controller.py` | 0 | 217 | 0/8 | ADVISORY — UI controller |
| `game/ui/screens/star_list_sidebar.py` | 0 | 180 | 0/2 | ADVISORY — UI sidebar |
| `game/ui/screens/strategy_fleet_command_router.py` | 0 | 307 | 0/10 | ADVISORY — UI routing |
| `game/ui/screens/strategy_game_state_manager.py` | 2 | 246 | 6/8 | MINOR — `__init__` + `_sync_active_empire` |
| `game/ui/screens/strategy_render/hex_outlines.py` | 0 | 133 | 0/6 | ADVISORY — UI rendering |
| `game/ui/screens/strategy_render/systems.py` | 0 | 307 | 0/5 | ADVISORY — UI rendering |
| `game/ui/screens/test_lab/renderer/__init__.py` | 1 | 13 | 0/0 | ADVISORY — init-only |
| `game/ui/screens/test_lab/viewmodel.py` | 2 | 389 | 30/47 | MINOR — rect setters only |
| `game/ui/utils/portraits.py` | 3 | 105 | 2/2 | VERIFIED |

---

## Context Usage Estimate

| Phase | Files Read | Approximate LOC |
|-------|-----------|-----------------|
| Production files | 40 | ~8,674 |
| Coverage matrix (filtered) | 1 (partial) | ~500 |
| Test files verified | 2 | ~200 |
| Schema/config docs | 3 (partial) | ~300 |
| **Total** | **46** | **~9,674** |

---

## Prioritized Recommendations

1. **CRITICAL**: Write tests for `SystemSlice` (`system_slice.py`) — primary facade query API, 0 tests
2. **CRITICAL**: Write tests for `FacilityAbilitySource` and `SystemAbilitySource` (`ability_sources/facility.py`, `system_archetype.py`) — ability framework integration seam
3. **CRITICAL**: Write tests for `BuildQueueSourceDTO.from_domain()` (`build_queue_dto.py`) — DTO cloning contract
4. **MAJOR**: Write tests for `GalaxyWarpGenerator` methods (`galaxy_warp_generator.py`) — MST + density edge generation, 1/12 symbols covered
5. **MAJOR**: Write tests for `WeaponFiringSystem` internal methods (`weapon_firing_system.py`) — core combat pipeline, 2/9 symbols covered
6. **MAJOR**: Write tests for ability iterator provider functions (`ability_iterator.py`) — all 9 providers untested
7. **MAJOR**: Write tests for `process_ramming` (`collision.py`) and `_tick_facility` (`component_activation_engine.py`)
8. **MINOR**: Write tests for `extract_abilities_from_component` (`component_inspector.py`) — central registry lookup with multiple format branches
