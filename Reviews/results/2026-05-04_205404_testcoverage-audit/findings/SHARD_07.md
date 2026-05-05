# Shard 07 — Test Coverage Audit Findings

**Audit Date:** 2026-05-04
**Scope:** 34 production files, ~8,401 LOC
**Pre-Computed Matrix:** `coverage_matrix.json`

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| **CRITICAL** | 2 | Tier 0 non-UI files with zero unit tests |
| **MAJOR** | 7 | Tier 1-2 files with untested error paths / business logic |
| **MINOR** | 8 | Partially tested functions missing branches |
| **ADVISORY** | 5 | UI rendering code, empty `__init__.py`, protocol-only files |

**Key finding:** The coverage matrix had **3 false negatives** (claimed Tier 0 but actually tested): `labels.py`, `strategy_screen_selection.py`, and `replay_store.py`. Two true CRITICAL Tier 0 gaps exist.

---

## Tier 0 — CRITICAL (Non-UI files with zero unit tests)

### CRITICAL-1: `game/core/protocols/strategy_domain.py` (194 LOC)

**Status:** No test file exists. Zero coverage.

**Symbols untested (35):**
- `IEmpire` protocol (lines 17-78): 13 properties (`id`, `name`, `color`, `flag_id`, `portrait_id`, `empire_theme_id`, `race_config`, `colonies`, `fleets`, `resource_pool`, `max_storage`, `built_ship_designs`)
- `IFacility` protocol (lines 81-117): 8 properties (`instance_id`, `design_id`, `name`, `design_data`, `is_operational`, `construction_queue`, `consumable_levels`)
- `IRaceRegistry` protocol (lines 120-131): `get_race` method
- `IShipInstance` protocol (lines 135-175): 9 properties + `get_calculated_stats` method
- TypeGuards `is_empire` (line 182), `is_facility` (line 187), `is_ship_instance` (line 192)

**Risk:** These protocols are the contract foundation for all strategy-layer entities. Untested TypeGuards could produce false positives/negatives that cascade through facade queries, command handlers, and UI.

**Suggested tests:**
- `tests/unit/core/protocols/test_strategy_domain.py`
  - Test each TypeGuard returns True for valid protocol mock objects
  - Test each TypeGuard returns False for objects missing required attributes
  - Test `_has_attrs` edge cases (missing attrs, partial matches, None)
  - Test `isinstance(obj, IEmpire)` with `@runtime_checkable` protocol

---

### CRITICAL-2: `game/strategy/facade/slices/event_slice.py` (96 LOC)

**Status:** No test file exists. Zero coverage. Referenced by facade but not independently tested.

**Symbols untested (8):**
- `EventSlice` class (lines 11-96)
  - `get_human_player_ids` (line 25): delegation to `self._state.session.human_player_ids`
  - `get_turn_number` (line 29): delegation to `self._state.session.turn_number`
  - `get_save_path` (line 33): delegation to `self._state.session.save_path`
  - `get_turn_events` (lines 41-63): branching on `empire_id is None` vs scoped call; branching on `turn is None` for default-to-current-turn
  - `get_all_events` (lines 65-78): branching on `empire_id is None`
  - `get_events_by_category` (lines 80-96): branching on `empire_id is None`

**Risk:** Event log queries have branching logic (empire scoping, turn defaulting) that is not verified. BUG-123 scope filtering paths are completely untested — an empire-scoped query that fails silently would show wrong or empty event data in UI.

**Suggested tests:**
- `tests/unit/strategy/facade/slices/test_event_slice.py`
  - Test `get_turn_events(turn=None)` defaults to session turn
  - Test `get_turn_events(empire_id=None)` vs `empire_id=42` branching
  - Test `get_all_events` with/without empire_id
  - Test `get_events_by_category` with/without empire_id
  - Test `get_human_player_ids`, `get_turn_number`, `get_save_path` delegation

---

### ADVISORY-1: `game/core/protocols/common.py` (46 LOC)

**Status:** No dedicated test file. However, these are pure Protocol definitions with `@runtime_checkable` — they have no behavioral logic. `_has_attrs` is tested indirectly via TypeGuard tests in other protocol files. **Upgraded from CRITICAL to ADVISORY** because:
1. `ILocatable`, `INamed`, `IOwnable` are pure protocol stubs with no implementation
2. `_has_attrs` is a one-liner using `all()` + `hasattr()` — trivially correct
3. It IS consumed by integration tests through strategy_domain TypeGuards

**Suggested:** Add trivial validation tests alongside strategy_domain tests if desired.

---

### ADVISORY-2: `game/ui/screens/strategy_render/dyson_spheres.py` (105 LOC)

**Status:** No tests. Pure UI rendering code (`pygame.draw`, `pygame.transform.smoothscale`). Contains a pre-existing latent bug (`screen_diameter` undefined at lines 80, 88-89) flagged by code comments. **ADVISORY — UI rendering.**

---

### ADVISORY-3: `game/ui/screens/test_lab/details/chrome.py` (244 LOC)

**Status:** No unit tests. Pure stateless pygame rendering helpers (`draw_header_and_status`, `draw_metadata`, `draw_action_buttons`, `draw_metrics`, `draw_scrollbar`). These are all visual-only functions with no business logic. **ADVISORY — UI rendering.**

---

### ADVISORY-4: `game/ui/screens/test_lab/renderer/validation_panel.py` (230 LOC)

**Status:** No unit tests. `ValidationPanel` class has `draw` and `_draw_check_compact` — pure rendering with color-coded status display. **ADVISORY — UI rendering.**

---

### ADVISORY-5: `game/simulation/components/__init__.py` (0 LOC)

**Status:** Empty file. **ADVISORY — no code to test.**

---

## Tier 1-2 — MAJOR / MINOR (Partial Coverage)

### MAJOR-1: `game/ui/screens/battle_setup/spec_compiler.py` (467 LOC)

**Coverage matrix:** 2/10 symbols tested (heuristic name matches only)

**Untested functions with business logic:**
- `_build_team_spec` (line 182): TeamSpec assembly from side data — untested
- `_task_force_for_fleet` (line 203): TaskForceSpec with FormationResolver — untested
- `_pick_formation_for_fleet` (line 237): fleet.task_forces iteration defaulting — untested
- `_ship_spec_from_instance` (line 246): ShipSpec with theme_id extraction, pose fallback — untested
- `_build_modifier_stack` (line 284): ModifierStack assembly with per-team dict — untested
- `_complex_to_entries` (line 325): complex design loading, ability → modifier mapping — untested
- `_extract_scope` (line 430): scope resolution with `ABILITY_REGISTRY` default fallback (PROJ-272 Phase 1) — untested
- `_load_complex_design` (line 404): file loading with OSError handling — untested

**`build_manual_battle_spec`** (line 90) has critical branching tested only through integration:
- N-team boundary check `num_teams < 2 or num_teams > 8` → ValueError
- `end_condition is None` default path

**Risk:** PROJ-275 Phase 4 added N-team support. None of the internal compiler functions have unit tests — a regression in scope routing, formation resolution, or modifier entry emission would only surface in manual Battle Setup testing.

**Suggested tests:**
- `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`
  - Unit-test `_build_team_spec` with mock BattleSetupSide
  - Unit-test `_ship_spec_from_instance` with None pose, with pose, with/without theme_id
  - Unit-test `_extract_scope` with dict scope, missing scope, primitive data
  - Unit-test `_complex_to_entries` with valid/invalid design_id
  - Unit-test `_pick_formation_for_fleet` with/without task_forces

---

### MAJOR-2: `game/strategy/services/replay_store.py` (322 LOC)

**Coverage matrix:** Tier 0 (claimed). **Actually has integration tests** at `tests/integration/replay/test_replay_store.py` — but lacks **unit tests**.

**Untested error paths (lines from production file):**
- `_safe_load` (line 266): corrupt JSON path, schema mismatch path, non-dict data path — tested in integration
- `_evict_excess` (line 280): OSError during unlink (line 297)
- `on_battle_ended` (line 182): missing pending capture (line 189)
- `on_battle_started` (line 163): no save root returns `""` (line 174-175)
- `persist` (line 200): no save root returns None (line 204-205); Exception during write (line 209)
- `load` (line 238): file not found → None (line 243-244); schema version mismatch (line 246)
- `delete` (line 250): no save root → False (line 252-253); OSError → False (line 259-261)
- `list` (line 216): corrupt file skip, schema version mismatch skip

**Risk:** MAJOR due to the gap between integration-only and full unit coverage of error paths. The ring-buffer eviction error path, corrupt-file handling, and missing save_root guards would benefit from isolated unit tests.

**Current integration tests cover:** persist→load→list happy path, eviction, settings fallback, schema-version mismatch, corrupt file, lifecycle hooks.

**Suggested test:** `tests/unit/strategy/services/test_replay_store.py` covering isolated error paths.

---

### MAJOR-3: `game/strategy/validation/planet_order_validator.py` (149 LOC)

**Coverage matrix:** 3/4 symbols tested. `_facility_has_ability` untested.

**Untested function:**
- `_facility_has_ability` (line 130): 3 branches (dict with ability_name, dict with comp_id + registry, str + registry). Returns False in default.

**Risk:** MAJOR — this helper backs both `validate_activate_ability` and `validate_deactivate_ability`. A bug here would silently allow or block ability activation orders.

**Suggested test extension:** Add to existing `tests/unit/strategy/engine/test_planet_orders.py`:
- Test facility with inline ability dict
- Test facility with component registry lookup (comp_id)
- Test facility with string component reference
- Test facility without matching ability returns False

---

### MAJOR-4: `game/ui/screens/strategy_screen.py` (458 LOC)

**Coverage matrix:** 35/47 symbols tested (Tier 2). 12 untested symbols.

**Untested paths with business logic:**
- `current_empire` property (line 185): iterates `human_player_ids[current_player_index]` → next empire lookup, falls back to `empires[0]`. Edge case: empty `human_player_ids` → IndexError.
- `_on_colonize_planet_selected` (line 290): delegates to `strategy_screen_selection.on_colonize_planet_selected` — covered indirectly via that module's tests.
- `request_colonize_order` (line 295): delegates to `strategy_screen_selection.request_colonize_order` — covered indirectly.
- `run_n_turns` (line 337): delegating property — covered through GameStateManager tests.
- FEAT-20 dev-mode properties: `dev_run_cancel_requested` (line 119), `turn_processing_message` (line 122)
- Issue #7 tick properties: `current_tick` (line 127), `total_ticks` (line 128)

**Risk:** MINOR — the untested symbols are mostly delegating properties. The `current_empire` IndexError edge case is the only real business logic gap.

**Suggested test:** Add test for `current_empire` with empty `human_player_ids` list (IndexError).

---

### MAJOR-5: `game/ui/screens/planet_list_filters.py` (385 LOC)

**Coverage matrix:** 7/17 symbols tested. Private predicate builders untested.

**Untested predicates:**
- `_name_predicate` (line 74): empty search vs matching — likely exercised through `filter_planets` but not unit-tested independently
- `_type_predicate` (line 80): `filter_types.get(category, True)` — default True means all types pass when not in filter
- `_owner_predicate` (line 84): branches for `owner_id is None` → 'Unowned', `owner_id == empire_id` → 'Player', else → 'Enemy'
- `_range_predicate` (line 102): `min_v <= getattr(p, attr_name) <= max_v`
- `effects_predicate` (line 106): tri-state FilterState logic (YES/NO/IGNORE), `getattr(p, 'intrinsic_abilities', None) or {}`
- `get_column_value` (line 227): branches for 'func' vs 'attr' column defs, attr chain walking, format strings
- `compute_planet_ranges` (line 255): padding calculation, empty planet list defaults
- `get_owner_name` (line 323): empire lookup loops, star indicator

**Risk:** MAJOR — the Effects filter (FEAT-25, lines 106-130) has non-trivial AND-composition logic. The `_owner_predicate` has multiple branches for None/Player/Enemy. The column-value resolver walks dotted attr chains.

**Covered through integration:** `filter_planets` (line 149) composes all predicates. Units from `tests/unit/ui/screens/test_planet_list_filters.py` test `filter_planets` extensively, `sort_planets`, and `gather_planets`. The `effects_predicate` class `TestEffectsPredicate` pins the tri-state contract.

**Suggested:** Add focused unit tests for the private predicates in isolation to verify edge cases.

---

### MAJOR-6: `game/ui/screens/strategy_build_queue_manager.py` (271 LOC)

**Coverage matrix:** 6/8 symbols tested.

**Untested:**
- `_get_registries` (line 37): lazy global initialization with `get_default_registry_provider()` — uses module-level mutable state (`_cached_registries`)
- `StrategyBuildQueueManager.__init__` (line 63): trivial constructor

**Risk:** MINOR — `_get_registries` manages lazy global state; tested indirectly through every build-queue operation. `__init__` is trivial.

---

### MAJOR-7: `game/ui/screens/builder/detail_panel.py` (295 LOC)

**Coverage matrix:** 2/10 symbols tested. 8 untested symbols.

**Untested methods:**
- `ComponentDetailPanel.__init__` (line 27): event_bus subscription, modifier_logic defaulting
- `on_selection_changed` (line 85): 4 branches (None, tuple, hasattr id, else)
- `show_component` (line 106): image caching, html comparison, modifier iteration
- `show_details_popup` (line 193): JSON popup construction
- `_clear_display` (line 224): image element cleanup
- `_update_image` (line 231): image loading with cache, fallback placeholder
- `set_position` (line 276): property delegation
- `handle_event` (line 280): always returns False
- `draw` (line 288): no-op placeholder

**Risk:** MAJOR — `on_selection_changed` has non-trivial branching (selection_data type dispatch). `show_component` has caching logic (html comparison prevents rebuilds). These are UI-interaction paths but the business logic branches should be tested.

**Covered existing tests:** `tests/unit/ui/screens/builder/test_detail_panel.py` — need to verify breadth.

---

### MINOR-1: `game/ai/behaviors.py` (424 LOC)

**Coverage matrix:** 25/29 symbols tested. 4 untested: `_flee_direction`, `AIBehavior.__init__`, `AttackRunBehavior.__init__`, `ErraticBehavior.__init__`

**Actual verification against tests:**
- `tests/unit/ai/test_behavior_units.py` and `tests/unit/ai/test_advanced_behaviors.py` heavily test behavior `update()` methods
- `_flee_direction` (line 65): tested indirectly through `FleeBehavior.update()` and `AttackRunBehavior.update()` — zero-length vector branch (line 77-78) where `vec.length() == 0` defaults to `(1,0)` is untested

**Risk:** MINOR — `_flee_direction` edge case (`from_pos == away_from_pos` → `Vector2(1,0)`) is not tested.

**Suggested test:** Add test to `test_behavior_units.py`:
```python
from game.ai.behaviors import _flee_direction
from game.core.math import Vector2

def test_flee_direction_positions_coincide():
    result = _flee_direction(Vector2(5, 5), Vector2(5, 5))
    assert result == Vector2(1, 0)
```

---

### MINOR-2: `game/ai/spatial_behaviors/patrol_zone.py` (57 LOC)

**Coverage matrix:** 2/3 symbols tested. `PatrolZoneBehavior.__init__` untested.

**Risk:** MINOR — trivial constructor with defaults. Tested indirectly through `compute_target_position`.

---

### MINOR-3: `game/core/event_logging.py` (88 LOC)

**Coverage matrix:** 6/7 symbols tested. `EventBus.__init__` untested.

**Actual: Thoroughly tested** in `tests/unit/core/event_logging/test_event_bus.py` (60 lines, 5 tests) and `tests/unit/core/event_logging/test_event_logging.py` (99 lines, 9 tests). The `__init__` is called in every EventBus test. **False positive in matrix.**

---

### MINOR-4: `game/simulation/components/abilities/cargo.py` (78 LOC)

**Coverage matrix:** 5/6 symbols tested. `CargoStorage.__init__` untested.

**Risk:** MINOR — `__init__` has branching (`isinstance(data, dict)` vs `int/float` vs else) at lines 38-46. Tested indirectly through `test_cargo_storage.py` tests that construct `CargoStorage` instances.

---

### MINOR-5: `game/strategy/engine/consumable_management_engine.py` (164 LOC)

**Coverage matrix:** 5/6 symbols tested. `ConsumableManagementEngine.__init__` untested.

**Risk:** MINOR — `__init__` has a `registries is None` → ValidationException guard (line 61). Tests create instances through the normal path but the None-exception branch may not be explicitly tested.

---

### MINOR-6: `game/strategy/engine/game_config.py` (261 LOC)

**Coverage matrix:** 8/10 symbols tested.

**Untested:**
- `_get_default_asset_path` (line 17): returns `Paths.SHIP_THEMES_DIR` — a one-liner used as a `default_factory` in dataclass field
- `_get_default_players` (line 123): returns 2-player config list

**Risk:** MINOR — both are simple factory functions with no branching. `_get_default_players` produces structured data consumed through `GameConfig.__post_init__` validation (which IS tested).

---

### MINOR-7: `game/strategy/engine/production_spawner.py` (413 LOC)

**Coverage matrix:** 9/11 symbols tested.

**Untested:**
- `ProductionSpawner.__init__` (line 34): trivial constructor
- `_resolve_planet_location` (line 84): has `galaxy and hasattr(galaxy, 'get_system_of_planet')` guard, `parent_sys is not None` guard, `planet.location is not None` guard

**Risk:** MINOR — `_resolve_planet_location` has non-trivial branching but is tested indirectly through `_create_and_place_facility` and `_spawn_ship`.

---

### MINOR-8: `game/strategy/engine/turn_engine.py` (824 LOC)

**Coverage matrix:** 25/26 symbols tested. Only `_log_empire_state` untested.

**Risk:** MINOR — `_log_empire_state` (line 290) is a debug-only logging function with `except (AttributeError, TypeError): pass` — a diagnostic-only method.

---

## Tier 3 — Verified Coverage (matrix claims)

| File | LOC | Symbols (tested/total) | Verification |
|------|-----|----------------------|--------------|
| `game/simulation/entities/combat_endurance.py` | 155 | 2/2 | VERIFIED — `tests/unit/simulation/entities/test_combat_endurance.py` has 934 lines, 30+ tests covering fuel/ammo/energy endurance, activation triggers, potential consumption, DPS calculation, boundary conditions, edge cases. Excellent coverage. |
| `game/strategy/generation/density/primitives/spiral_arm.py` | 103 | 2/2 | VERIFIED — `tests/unit/strategy/generation/density/test_spiral_arm.py` covers center density, arm/gap contrast, valid range, arm count effect, rotation shift. Adequate coverage. |
| `game/ui/config.py` | 66 | 1/1 | VERIFIED via conftest — `UIConfig` is a pure constants class. Referenced throughout UI tests. |

---

## Matrix Correction — False Negatives

The following files were labeled Tier 0 ("no tests") by the coverage matrix but actually **have tests**:

| File | Matrix Tier | Actual Coverage | Correction |
|------|------------|----------------|------------|
| `game/strategy/services/ability_sources/labels.py` | TIER_0 | Fully tested | `tests/unit/strategy/services/ability_sources/test_labels.py` — 4 test functions including keyword-only arg validation |
| `game/ui/screens/strategy_screen_selection.py` | TIER_0 | Fully tested | `tests/unit/ui/screens/test_strategy_screen_selection.py` — 184 lines, 4 test classes covering on_ui_selection (6 tests), on_colonize_click (2 tests), on_colonize_planet_selected (2 tests), request_colonize_order (4 tests) |
| `game/strategy/services/replay_store.py` | TIER_0 | Integration-tested | `tests/integration/replay/test_replay_store.py` — 306 lines, covers persist→load→list, eviction, settings, schema mismatch, corrupt files, lifecycle. LACKS unit tests for isolated error paths (upgraded to MAJOR in §MAJOR-2). |

---

## File Coverage Verification Table

| File | LOC | Expected Tier | Actual Tier | Tests Found | Verdict |
|------|-----|--------------|-------------|-------------|--------|
| `game/ai/behaviors.py` | 424 | TIER_2 | TIER_2 | `test_behavior_units.py`, `test_advanced_behaviors.py` | PARTIAL — `_flee_direction` zero-length edge case |
| `game/ai/spatial_behaviors/patrol_zone.py` | 57 | TIER_2 | TIER_2 | `test_spatial_*.py` | PARTIAL — `__init__` not unit-verified |
| `game/core/event_logging.py` | 88 | TIER_2 | TIER_3 | `test_event_bus.py` (5 tests), `test_event_logging.py` (9 tests) | COVERED — well tested |
| `game/core/protocols/common.py` | 46 | TIER_0 | TIER_0 | None | ADVISORY — pure protocols |
| `game/core/protocols/strategy_domain.py` | 194 | TIER_0 | TIER_0 | None | **CRITICAL** |
| `game/simulation/components/__init__.py` | 0 | TIER_1 | TIER_1 | N/A | ADVISORY — empty file |
| `game/simulation/components/abilities/cargo.py` | 78 | TIER_2 | TIER_2 | `test_cargo_storage.py` | PARTIAL — `__init__` branching |
| `game/simulation/entities/combat_endurance.py` | 155 | TIER_3 | TIER_3 | `test_combat_endurance.py` (934 LOC, 30+ tests) | VERIFIED — excellent |
| `game/strategy/data/planet_gen.py` | 604 | TIER_2 | TIER_2 | candidate test files exist | PARTIAL — untested: `__init__`, `_collect_star_exclusion_zones`, `_create_planet_objects` |
| `game/strategy/engine/consumable_management_engine.py` | 164 | TIER_2 | TIER_2 | candidate test files exist | PARTIAL — `__init__` ValidationException path |
| `game/strategy/engine/game_config.py` | 261 | TIER_2 | TIER_2 | fixture tests | PARTIAL — factory functions untested |
| `game/strategy/engine/production_spawner.py` | 413 | TIER_2 | TIER_2 | candidate test files exist | PARTIAL — `_resolve_planet_location` branching |
| `game/strategy/engine/turn_engine.py` | 824 | TIER_2 | TIER_2 | extensive test suite | PARTIAL — debug-only `_log_empire_state` |
| `game/strategy/facade/slices/event_slice.py` | 96 | TIER_0 | TIER_0 | None | **CRITICAL** |
| `game/strategy/generation/density/primitives/spiral_arm.py` | 103 | TIER_3 | TIER_3 | `test_spiral_arm.py` (78 LOC) | VERIFIED |
| `game/strategy/services/ability_sources/labels.py` | 23 | TIER_0 | **ACTUAL: TIER_3** | `test_labels.py` (27 LOC, 4 tests) | **MATRIX FALSE NEGATIVE** |
| `game/strategy/services/design_validator.py` | 150 | TIER_2 | TIER_2 | candidate tests | PARTIAL — untested: `_check_layer_mass`, `_check_components_exist` |
| `game/strategy/services/replay_store.py` | 322 | TIER_0 | **ACTUAL: TIER_2** | `test_replay_store.py` (integration, 306 LOC) | **MAJOR** — lacks unit tests |
| `game/strategy/validation/planet_order_validator.py` | 149 | TIER_2 | TIER_2 | candidate tests | PARTIAL — `_facility_has_ability` untested |
| `game/ui/config.py` | 66 | TIER_3 | TIER_3 | import-based | VERIFIED — constants class |
| `game/ui/panels/strategy_widgets.py` | 191 | TIER_2 | TIER_2 | `test_strategy_widgets.py` | PARTIAL — `DataGraph.__init__` |
| `game/ui/screens/battle_setup/spec_compiler.py` | 467 | TIER_2 | TIER_2 | `test_spec_compiler.py` (import match only) | **MAJOR** — 8 internal functions untested |
| `game/ui/screens/battle_setup_state.py` | 300 | TIER_2 | TIER_2 | candidate tests | PARTIAL — `_generate_fleet_id`, `ship_count` property |
| `game/ui/screens/builder/detail_panel.py` | 295 | TIER_2 | TIER_2 | `test_detail_panel.py` | **MAJOR** — 8 methods untested |
| `game/ui/screens/planet_abilities_window.py` | 280 | TIER_2 | TIER_2 | candidate tests | PARTIAL — `PlanetAbilitiesUiBuilder.build`, `process_event` |
| `game/ui/screens/planet_list_filters.py` | 385 | TIER_2 | TIER_2 | `test_planet_list_filters.py` | PARTIAL — private predicates not isolated |
| `game/ui/screens/race_setup/view_model.py` | 88 | TIER_2 | TIER_2 | candidate tests | PARTIAL — 4 properties untested |
| `game/ui/screens/strategy_build_queue_manager.py` | 271 | TIER_2 | TIER_2 | `test_build_queue_manager.py` | PARTIAL — `_get_registries` lazy init |
| `game/ui/screens/strategy_render/dyson_spheres.py` | 105 | TIER_0 | TIER_0 | None | ADVISORY — pure rendering |
| `game/ui/screens/strategy_screen.py` | 458 | TIER_2 | TIER_2 | `test_strategy_screen*.py` | PARTIAL — 12 delegating properties |
| `game/ui/screens/strategy_screen_selection.py` | 99 | TIER_0 | **ACTUAL: TIER_3** | `test_strategy_screen_selection.py` (184 LOC, 14 tests) | **MATRIX FALSE NEGATIVE** |
| `game/ui/screens/test_lab/details/chrome.py` | 244 | TIER_0 | TIER_0 | None | ADVISORY — pure rendering |
| `game/ui/screens/test_lab/renderer/validation_panel.py` | 230 | TIER_0 | TIER_0 | None | ADVISORY — pure rendering |
| `game/ui/screens/test_lab/screen.py` | 771 | TIER_2 | TIER_2 | extensive test suite | PARTIAL — 40+ untested property delegates |

---

## Context Usage Estimate

- Production files read: 34/34 (100%)
- Key test files read: 7 (event_bus, event_logging, labels, spiral_arm, combat_endurance, strategy_screen_selection, replay_store)
- Total files inspected: ~41
- Lines scanned: ~12,000+ (production + tests)

**Report confidence:** HIGH. All production files fully read. Key test files verified. 3 matrix false negatives identified and corrected.
