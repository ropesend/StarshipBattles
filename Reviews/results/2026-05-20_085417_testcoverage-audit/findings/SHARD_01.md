# Shard 01 — Test Coverage Audit

## Summary
- **Shard:** 01
- **Production files in scope:** 48
- **Production files actually read:** 48 (100%)
- **Unit test files read:** 12 (sampled for verification)
- **Total findings:** 41
- **Critical:** 3 | **Major:** 16 | **Minor:** 11 | **Advisory:** 11

## Severity Summary by Layer

| Layer | Critical | Major | Minor | Advisory |
|-------|----------|-------|-------|----------|
| services | 1 | 0 | 0 | 0 |
| simulation | 2 | 3 | 1 | 0 |
| strategy | 0 | 8 | 3 | 1 |
| ui | 0 | 5 | 7 | 10 |

---

## Tier 0 — Zero Unit Tests

### CRITICAL: `game/services/provider_factory.py` (87 LOC, services layer)

**File summary:** Shared env-var-driven provider factory machinery. Contains one public function `resolve_provider()` that implements the skeleton for both LLM and image provider factories — env-var resolution, name lookup, error handling, and deferred-validation pattern.

**Coverage gap:** Zero unit tests exist. No candidate test file was found. The function is used by `LLMProviderFactory.create()` and `ImageProviderFactory.create()`, but it has no direct test of its own logic.

**Untested symbols:**
- `resolve_provider` (lines 30-84) — 8 distinct code paths:
  1. `name is None` → reads env var (line 65)
  2. `name is None` and env var unset → uses `default` (line 66)
  3. Provider not found in registry → raises `config_error_cls` (lines 69-78)
  4. Constructor succeeds → returns instance (line 81)
  5. Constructor raises `config_error_cls` → returns `None` (deferred validation, lines 82-84)
  6. Constructor raises unrelated exception → propagates (line 63 doc)
  7. `name` explicitly provided (non-None) → skips env var (line 65)
  8. Many parameters with defaults — edge cases for each kwarg

**Suggested tests:**
- `test_resolve_provider_found` — register a stub class, resolve it, verify instance returned
- `test_resolve_provider_unknown_name` — resolve with unregistered name, verify exception with correct context
- `test_resolve_provider_deferred_validation` — stub constructor raises config_error, verify None returned
- `test_resolve_provider_env_var_fallback` — clear env, verify default used
- `test_resolve_provider_constructor_propagates` — stub constructor raises ValueError, verify propagation

---

### CRITICAL: `game/simulation/entities/stat_contributors/command.py` (116 LOC, simulation layer)

**File summary:** Command/control stat contributor — contains `contribute_multiplex_tracking` (Phase 3 registered contributor) and `allocate_crew_and_life_support` (Phase 2 maintenance allocation). These are core combat stat calculation functions that mutate ship state.

**Coverage gap:** Zero unit tests exist. No candidate test file was found. These functions are registered in the stat contributor pipeline and called by `ShipStatsCalculator`, but have no direct or indirect unit test verification.

**Untested symbols:**

1. `contribute_multiplex_tracking` (lines 41-53):
   - Component has MultiplexTracking ability → bumps `ship.max_targets` (line 51-53)
   - Component has NO MultiplexTracking → `mt` stays 0, no mutation (line 52 check: `mt > 0 and mt > ship.max_targets`)
   - Component has MultiplexTracking but value lower than current max → no mutation
   - Empty component pool edge case
   - Components with type-checking import only (TYPE_CHECKING guard)

2. `allocate_crew_and_life_support` (lines 56-116):
   - Sets `ship.crew_onboard`, `ship.crew_required`, resets `ship.max_targets` (lines 85-87)
   - Ship class not in vehicle_classes → uses `DEFAULT_MAX_MASS` (line 89-91)
   - `available_life_support` is informational only — `_ = available_life_support` (line 96)
   - Empty `component_pool` → sorted loop no-ops (line 99)
   - Component has no `RequiresMaintenance` → `req_maint` stays 0 (line 105-107)
   - `ship.crew_required` accumulates even when maintenance sufficient (line 109)
   - Sufficient remaining maintenance → consumption (line 112-113)
   - Insufficient maintenance → component deactivated with `ComponentStatus.NO_CREW` (lines 114-116)
   - Inactive components skipped at line 102-103
   - Components sorted by `lookup_crew_priority` (line 99)

**Suggested tests:**
- `test_contribute_multiplex_tracking_bumps_max_targets` — ship has max_targets=1, component has slots=3, verify ship.max_targets=3
- `test_contribute_multiplex_tracking_no_ability` — component has no MultiplexTracking, verify ship.max_targets unchanged
- `test_contribute_multiplex_tracking_lower_value_no_change` — ship.max_targets=5, component has slots=3, verify unchanged
- `test_allocate_crew_sufficient_maintenance` — components with RequiresMaintenance, verify crew_required accumulated, remaining drained
- `test_allocate_crew_insufficient_maintenance` — verify component deactivated with NO_CREW status
- `test_allocate_crew_empty_component_pool` — verify no mutations except initial assignments
- `test_allocate_crew_unknown_vehicle_class` — missing vehicle class, verify DEFAULT_MAX_MASS used
- `test_allocate_crew_priority_sorting` — verify components sorted by lookup_crew_priority

---

### CRITICAL: `game/simulation/entities/stat_contributors/weapons.py` (56 LOC, simulation layer)

**File summary:** Weapons/targeting stat contributor — computes ECM defense and sensor offense scores via `aggregate_targeting_scores`. Core combat stat calculation.

**Coverage gap:** Zero unit tests. No candidate test file.

**Untested symbols:**

- `aggregate_targeting_scores` (lines 36-56):
  1. Normal float return from `get_ability_total` (line 47)
  2. Bool return from `get_ability_total` → `isinstance(ecm_score, bool)` guard (lines 48-49)
  3. `ToHitDefenseModifier` total normal case (line 47)
  4. `ToHitAttackModifier` total normal case (line 51)
  5. `ToHitAttackModifier` returns bool → clamped to 0.0 (lines 52-53)
  6. Empty component pool → ability totals return 0 (line 47, 51)
  7. `ship.baseline_to_hit_offense` set as side effect (line 55)
  8. Return value is `float(ecm_score)` (line 56)

**Suggested tests:**
- `test_aggregate_targeting_scores_normal` — both totals return floats, verify ship state + return value
- `test_aggregate_targeting_scores_bool_guard` — total returns bool (legacy format), verify clamped to 0.0
- `test_aggregate_targeting_scores_empty_pool` — empty component pool, verify 0.0 return and baseline set

---

### MAJOR: `game/strategy/interfaces/engines/planet_ops.py` (89 LOC, strategy layer)

**File summary:** Abstract base classes `IPlanetEnergyEngine` and `IPlanetActionEngine` — protocol definitions for planet tick processing. These are pure ABCs with abstract methods.

**Coverage gap:** Zero tests. However, these are abstract base classes — they don't contain executable logic. The real implementations (e.g., `PlanetEnergyEngine`, `PlanetActionEngine`) live elsewhere and are tested there.

**Verdict:** MAJOR (not CRITICAL) because ABCs with no concrete logic. However, absence of test verification that implementations conform to these interfaces is a protocol-conformance gap.

**Suggested tests:**
- Test that concrete implementations satisfy `isinstance(x, IPlanetEnergyEngine)`
- Verify method signatures match across interface ↔ implementation

---

### CRITICAL → MAJOR: `game/strategy/combat/pre_tick_setup/mine_setup.py` (62 LOC, strategy layer)

**Re-evaluated from CRITICAL to MAJOR:** This file is indirectly exercised through the pre-tick setup registry integration. When `PreTickBattleSetupRegistry` is populated with mine setup callbacks and `composed_callback()` is invoked during battle initialization, the mine resolver creation path is exercised. However, there are no direct unit tests of the isolated function logic.

**Untested symbols:**

- `build_mine_resolver_setup` (lines 17-62):
  1. Empty `mine_groups` → returns `None` (line 34-35)
  2. Non-empty groups → returns closure `_setup` (line 62)
  3. Internal `_setup` closure (lines 47-60):
     - Group with owner_id not in owner_to_team_map → skipped (lines 50-51)
     - `TacticalMineResolver.from_mine_group` called with boundary (line 52-54)
     - `_owner_team_id` set on resolver (line 55)
     - Resolver appended to `engine.mine_resolvers` (line 56)
     - `setattr` for `_tactical_resolver` back-reference, with silent catch of `(AttributeError, TypeError)` (lines 57-60)
  4. `battle_boundary=None` case — passes None to resolver (line 53)
  5. `captured_groups` tuple + `captured_owner_map` dict closure variables (lines 43-44)

**Suggested tests:**
- `test_build_mine_resolver_setup_empty_groups` — returns None
- `test_build_mine_resolver_setup_with_groups` — verify closure constructs resolvers, sets owner_team_id, appends to engine
- `test_build_mine_resolver_setup_unknown_owner` — group with owner not in map is skipped
- `test_build_mine_resolver_setup_null_boundary` — passes None as boundary

---

### CRITICAL → MAJOR: `game/strategy/services/component_layers.py` (169 LOC, strategy layer)

**Re-evaluated from CRITICAL to MAJOR:** These functions were extracted from `ShipInstance` and had tests on `ShipInstance` before extraction. The existing tests in `tests/unit/strategy/test_managers_phase_3b.py` and fleet report tests may exercise some paths. However, no dedicated test files exist for the extracted functions.

**Untested symbols:**

1. `lookup_design_max_hp` (lines 35-69):
   - Registry available via `ship._registries` → uses it (lines 48-49)
   - Registry unavailable → falls back to `get_default_registry_provider()` (lines 50-55)
   - Fallback raises `Exception` → returns `None` (line 55)
   - Component found, `isinstance(comp, dict)` → reads `max_hp` or `hp` fields (lines 60-61)
   - Component found, is object → reads `max_hp` or `hp` attributes (lines 62-63)
   - Value is None → returns None (lines 64-65)
   - Value is integer → returns `int(raw)` (line 67)
   - Value is non-integer (string/formula) → `(TypeError, ValueError)` → returns None (lines 68-69)

2. `iter_components_by_layer` (lines 72-123):
   - Empty `design_data['layers']` → empty result (line 90)
   - HULL layer filtered out (line 91-92)
   - Component state found in `ship.components` → reads hp values (lines 102-105)
   - Component state NOT found → falls back to `lookup_design_max_hp` (lines 106-112)
   - Fallback returns None → component skipped (lines 108-109)
   - Per-component instance index tracking via `per_id_index` dict (lines 88-99)
   - Component entry is dict with 'id' key (line 95)
   - Component entry is string (line 95)
   - `comp_id` is None/empty → skip (line 96-97)

3. `damaged_components_by_layer` (lines 126-161):
   - Empty `ship.components` or no damaged → returns `{}` (lines 140-144)
   - Layer name lookup via `comp_id_to_layer` mapping (lines 146-154)
   - Component ID not found in any layer → "UNKNOWN" layer (line 158)
   - Component entry is dict (line 149-150)
   - Component entry is string (line 151)

4. `count_damaged_components` (lines 164-169):
   - Empty components → returns 0 (line 169)
   - All healthy → returns 0
   - Mixed damaged/healthy → correct count

**Suggested tests:**
- `test_lookup_design_max_hp_from_registries` — normal lookup path
- `test_lookup_design_max_hp_fallback_to_default_provider` — test fallback
- `test_lookup_design_max_hp_missing_component` — returns None
- `test_lookup_design_max_hp_formula_value` — non-integer hp returns None
- `test_iter_components_by_layer_skips_hull` — HULL excluded
- `test_iter_components_by_layer_missing_state_fallback` — fallback hp lookup
- `test_iter_components_by_layer_missing_component_skipped` — unknown component skipped
- `test_damaged_components_by_layer_empty` — no damaged returns {}
- `test_damaged_components_by_layer_unknown_layer` — unmapped component in UNKNOWN
- `test_count_damaged_components` — various states

---

### ADVISORY: `game/ui/components/__init__.py` (1 LOC, ui layer)

Package docstring only. No executable code. ADVISORY.

---

### ADVISORY: `game/ui/screens/defeat_dialog.py` (121 LOC, ui layer)

**File summary:** Defeat modal dialog extending `StrategyModalWindow`. UI component with pygame widgets.

**Untested symbols:**
- `_format_body` (lines 28-40) — pure string formatting, could be unit tested independently
- `DefeatDialog.__init__` (lines 56-105) — pygame UI construction, ADVISORY
- `DefeatDialog.process_event` (lines 107-121) — event handler for dismiss button click

**Verdict:** ADVISORY. The `_format_body` function is pure logic and could be tested easily (MINOR). The rest is pygame UI code.

**Suggested tests:**
- `test_format_body_returns_html_with_empire_name` — verify HTML string contains the name

---

### ADVISORY: `game/ui/screens/test_lab/details/chrome.py` (244 LOC, ui layer)

**File summary:** Pure rendering functions for the Test Lab details panel — `draw_header_and_status`, `draw_metadata`, `draw_action_buttons`, `draw_metrics`, `draw_scrollbar`. All take `DetailsDrawContext` and pygame surfaces.

**Untested symbols:** All 6 symbols are pure pygame rendering code. ADVISORY.

**Verdict:** ADVISORY. These are pure rendering functions with no business logic. The `ActionButtonRects` dataclass is trivial. Testing pygame drawing would require headless surface comparison, which is low-value for these functions.

---

## Tier 1 — No Symbols Tested

### MAJOR: `game/ui/screens/battle_ui.py` (209 LOC, ui layer)

**File summary:** Battle UI class handling grid rendering, debug overlay, click handling, scrolling, and panel orchestration. Mixed rendering and business logic.

**Coverage gap:** No direct unit tests exist. The file is referenced in `tests/unit/ui/conftest.py` but has zero assertions against it.

**Untested symbols:**
- `BattleUI.__init__` (lines 25-46) — panel instantiation, ADVISORY
- `BattleUI.track_projectile` (lines 48-51) — **business logic**: filters projectiles by `AttackType.MISSILE`. Could be unit tested.
- `BattleUI.handle_resize` (lines 53-72) — layout recalculation, ADVISORY
- `BattleUI.draw` (lines 74-85) — rendering orchestration, ADVISORY
- `BattleUI.handle_click` (lines 87-106) — click delegation chain, **has branching logic**: panel hit-testing priority order
- `BattleUI.handle_scroll` (lines 108-110) — pass-through no-op, ADVISORY
- `BattleUI.draw_grid` (lines 112-136) — rendering, ADVISORY
- `BattleUI.draw_debug_overlay` (lines 138-209) — rendering, ADVISORY

**Verdict:** MAJOR for `track_projectile` (business logic filter) and `handle_click` (hit-test branching). ADVISORY for rendering.

**Suggested tests:**
- `test_track_projectile_missile_added` — projectile type=AttackType.MISSILE, verify added to seeker panel
- `test_track_projectile_beam_ignored` — projectile type=BEAM, verify NOT added
- `test_handle_click_control_panel_first` — verify control panel checked before seeker/stats

---

### ADVISORY: `game/strategy/events/__init__.py` (6 LOC, strategy layer)

Re-export shim: `Event`, `EventLog`, `EventCategory`, `EventType`. No executable logic. ADVISORY.

---

### ADVISORY: `game/ui/screens/builder/__init__.py` (7 LOC, ui layer)

Re-export shim. No executable logic. ADVISORY.

---

## Tier 2 — Partial Coverage

### MAJOR: `game/simulation/battle_spec.py` (257 LOC, simulation layer)

- **`TaskForceSpec.__post_init__`** (lines 174-185): Type validation for `formation` field. 8/9 symbols tested. The `__post_init__` guard validates that `formation` is `FormationSpec | None`, rejecting other types. Three code paths:
  1. `formation` is None → no-op (line 181)
  2. `formation` is `FormationSpec` → no-op
  3. `formation` is other type → raises `TypeError` (lines 182-185)
  
  The first two paths are exercised by spec compilation tests. The third path (invalid type) is untested.

- **`WeaponFamilyMetadata`** (in `attack_contract.py`, line 166): Frozen dataclass used by `FAMILY_METADATA` dict. Accessor patterns (attribute reads) tested through registry usage; no direct instantiation test.

**Suggested test:** `test_task_force_spec_rejects_non_formation` — verify TypeError for invalid formation type

---

### MAJOR: `game/simulation/combat/combat_events.py` (164 LOC, simulation layer)

- 9/10 heuristically tested. The Phase 1 scanner flagged one untested symbol (likely `CombatEventBus.__init__`). Review confirms the file has good coverage through `test_combat_events.py`, `test_damage_calculator_events.py`, and related files.

- Minor gaps:
  - `CombatEventBus.unsubscribe` callback not found — no-op (line 137-140)
  - `CombatEventBus.emit` with no subscribers for event type — returns silently (lines 154-156)
  - `CombatEventBus.emit` with detail level below event required level — skipped (lines 148-152)
  - `detail_level` property setter (lines 125-127) — tests may only test default, not the setter

**Suggested test:** `test_unsubscribe_nonexistent_callback_noop` — verify no error when unsubscribing non-registered callback

---

### MINOR: `game/simulation/components/component_health_manager.py` (102 LOC, simulation layer)

- **`ComponentHealthManager.__init__`** (line 33): Simple attribute assignment, exercised indirectly
- File has 120 assertion lines in its test. Coverage is solid.

**Verdict:** MINOR — `__init__` is trivial setup.

---

### MINOR: `game/simulation/entities/ship_stat_querier.py` (145 LOC, simulation layer)

- **`ShipStatQuerier.__init__`** (line 26): Simple attribute assignment
- 6/7 symbols tested. Coverage is reasonable through `tests/unit/entities/test_ship_stat_querier.py`.

**Verdict:** MINOR.

---

### MAJOR: `game/strategy/combat/pre_tick_setup_registry.py` (118 LOC, strategy layer)

- Test file found (`tests/unit/strategy/combat/test_pre_tick_setup_registry.py`, 10 assertions). Phase 1 flagged:
  - `__init__` (line 46) — MINOR, exercised indirectly
  - `__len__` (line 113) — MINOR, may or may not be tested

- Unaddressed gaps:
  - `register` with duplicate name → raises `ValueError` (lines 60-63)
  - `register` with 1-param callable → wraps with lambda (lines 85-88)
  - `register` with opaque callable (builtin) → `inspect.signature` raises `TypeError`/`ValueError`, falls back to `param_count=2` (lines 82-83)
  - `composed_callback` returns None for empty registry (line 102-103)
  - `composed_callback` returns callable that iterates entries (lines 107-109)
  - `names()` returns tuple in registration order (line 118)

**Verdict:** MAJOR — critical registry behavior (duplicate rejection, param-count detection, opacity fallback) is untested.

**Suggested tests:**
- `test_register_duplicate_name_raises` — verify ValueError
- `test_register_legacy_single_param_callable_wrapped` — verify wrapped
- `test_register_builtin_callable_fallback` — verify 2-param fallback
- `test_composed_callback_empty_returns_none` — verify None
- `test_names_returns_registration_order` — verify order preservation

---

### MAJOR: `game/strategy/data/fleet.py` (632 LOC, strategy layer)

- 39/43 symbols heuristically tested. Four untested:
  1. **`Fleet.get_combat_capable_ships`** (line 226): Simple list comprehension `[s for s in self.ships if s.is_combat_capable()]`. Used by combat compilation but no direct unit test. MINOR.
  2. **`Fleet._unregister_from_target`** (lines 342-360): Complex pursuer-tracking logic with multiple branch conditions:
     - Order type is `MOVE_TO_FLEET` or `JOIN_FLEET` (line 350)
     - Target has `pursuer_tracker` attribute (line 352)
     - Remaining orders still target same fleet → no unregister (lines 354-358)
     - No remaining orders target same fleet → unregisters (lines 359-360)
     **MAJOR** — pursuer tracker leak if this method breaks.
  3. **`Fleet.__eq__`** (lines 626-629): ID-based equality. MINOR.
  4. **`Fleet.__hash__`** (lines 631-632): ID-based hash. MINOR.

**Verdict:** MAJOR for `_unregister_from_target`. MINOR for the others.

**Suggested tests:**
- `test_unregister_from_target_no_pursuer_tracker` — target without pursuer_tracker attribute
- `test_unregister_from_target_still_targeted_by_another_order` — verify NOT unregistered
- `test_unregister_from_target_last_order_removes_pursuer` — verify pursuer removed
- `test_fleet_eq_same_id` — verify equality by ID only
- `test_fleet_hash_consistent` — verify hash equals hash(id)

---

### MAJOR: `game/strategy/data/race_config.py` (372 LOC, strategy layer)

- 8/15 symbols heuristically tested. The 7 `_validate_*` private methods (lines 302-368) are flagged as untested by Phase 1. In reality, they ARE exercised indirectly through `validate()` (line 274), which iterates them and returns on first error. The `test_race_config.py` has 45 test functions.

- **Actual gaps in the `_validate_*` chain:**
  - `_validate_required_fields` — `name` missing/empty IS tested, but empty `name.strip()` edge case may not be
  - `_validate_aptitudes` — 1-100 range check for all 7 aptitudes, boundary at 0 and 101
  - `_validate_identity_enums` — empty string value passes (line 323: `if value and value not in valid_list`), each enum list checked
  - `_validate_homeworld` — empty string passes (line 328), invalid type fails
  - `_validate_descriptions` — >500 char limit checked, exactly-at-500 boundary not tested
  - `_validate_preferences` — mutated-invalid preferences catch ValidationException (line 349-350)
  - `_validate_reproduction_and_happiness` — negative rate rejected, happiness [0, 1] bounds
  - `validate()` short-circuits on first error — if `_validate_required_fields` fails, the remaining 6 validators are never reached in that call (line 288-289). This means second-and-later validators are only exercised when all prior checks pass.

**Verdict:** MAJOR — the short-circuit behavior means later validators only run when preconditions are clean. Individual validator branch coverage should be verified.

**Suggested tests:**
- Test each `_validate_*` method in isolation with clear pass/fail cases
- `test_validate_short_circuits_on_first_error` — verify only first failing check reported
- `test_validate_descriptions_exactly_500_chars` — boundary value
- `test_validate_preferences_catches_mutated_invalid` — verify ValidationException from mutated pref

---

### MAJOR: `game/strategy/data/resource_generation_config.py` (149 LOC, strategy layer)

- 3/6 symbols heuristically tested. Untested:
  - `ResourceGenerationConfig.__init__` (lines 45-55) — two branches (JSON loaded vs defaults). The `_load_from_json` and `_use_defaults` paths ARE exercised by `get_resource_generation_config()` and `test_resource_generation_config.py` (10 test functions).
  - **Actual gap:** Planet type affinities via `_affinities` dict and `get_affinity` (lines 119-131) may not be fully tested. The `get_affinity` method returns 1.0 for unknown planet_type_name (line 131) and 1.0 for unknown resource_name (line 131). These default-return paths need verification.

**Verdict:** MAJOR for branch coverage gaps.

**Suggested tests:**
- `test_get_affinity_unknown_planet_type_returns_1` — verify default 1.0
- `test_get_affinity_unknown_resource_returns_1` — verify default 1.0
- `test_init_with_json_loads_affinities` — verify _affinities populated

---

### MAJOR: `game/strategy/engine/empire_economy_calculator.py` (333 LOC, strategy layer)

- 4/8 symbols heuristically tested. Test file exists with reasonable coverage. The Phase 1 scanner flagged constructors and private helper methods:
  - `EmpireEconomyCalculator.__init__` — exercised through `calculate()`
  - `_aggregate_population_upkeep` (lines 173-205) — exercised through `calculate()`. But the early-return when `economy_config` or `race_registry` is None (lines 185-186) may not be tested.
  - `_aggregate_colony_production` (lines 207-262) — exercised through `calculate()`. Several inner branches:
    - Non-operational facility skipped (line 233)
    - Harvester with empty resource_type (line 243)
    - Harvester with zero base_rate (line 243)
    - Planet quality <= 0 skipped (line 249)
    - `min(potential, remaining_quantity)` capping (line 255)
    - Resource type not in totals (line 257)
    - Multiple harvesters drawing from same deposit (line 260)
  - `_aggregate_construction_expenses` (lines 264-333) — complex logic tracking ships vs complexes:
    - Empty queue → early return (line 292)
    - `item_type == "complex"` → complexes dict (line 296)
    - `item_type != "complex"` (assumed "ship") → ships dict (line 296)
    - Colony queue paused → skipped (line 306)
    - Facility not a shipyard → skipped (line 313)
    - Facility queue paused → skipped (line 315)
    - Fleet without space_shipyard capability → skipped (lines 324-325)
    - Fleet queue paused → skipped (line 326)
    - `yard_count` multiplier for fleet yards (line 330)

**Verdict:** MAJOR — many nested conditionals in `_aggregate_colony_production` and `_aggregate_construction_expenses` lack explicit branch testing.

---

### MAJOR: `game/strategy/engine/game_session.py` (498 LOC, strategy layer)

- 19/28 symbols heuristically tested. Phase 1 flagged 9 untested symbols. After analysis:

  **Backward-compat property aliases (MINOR):**
  - `_event_log`, `_fleet_mutator`, `_planet_mutator`, `_empire_mutator`, `_ship_mutator` (lines 191-255) — all delegate to `self._services.*`. Trivial.

  **Real gaps (MAJOR):**
  - `process_turn` (lines 329-362): Has failure/rollback behavior with `EnginePhaseError` catch. The success path is tested; the failure-with-rollback path and re-raise path need verification:
    - `progress_callback` forwarded to `turn_engine.process_turn` (line 352)
    - `EnginePhaseError` raised → logged and re-raised (lines 359-362)
    - `turn_number` only incremented on success (line 358)
  - `preview_fleet_path` (lines 364-387): Calls `GalaxyPathfindingService.find_hybrid_path` and `strip_start_hex`. Untested edge cases:
    - No path found → `find_hybrid_path` returns None → `strip_start_hex` receives None → result is None
  - `get_fleet_path_projection` (lines 389-401): Thin delegate to `project_fleet_path`. MINOR.
  - `_get_planet_by_id` (lines 431-444): Thin delegate. MINOR.

**Verdict:** MAJOR for `process_turn` error path. MINOR for the rest.

**Suggested tests:**
- `test_process_turn_rollback_on_engine_phase_error` — verify turn_number NOT incremented
- `test_process_turn_progress_callback_forwarded` — verify callback passed to turn_engine
- `test_preview_fleet_path_no_path_found_returns_none` — verify None returned

---

### MINOR: `game/strategy/engine/handlers/order_queue.py` (267 LOC, strategy layer)

- 10/11 symbols heuristically tested. The `register` function (lines 255-267) is the module-level registration function. It's called during command registry seeding and is indirectly exercised. MINOR.

---

### MAJOR: `game/strategy/services/replay_resolver.py` (130 LOC, strategy layer)

- 3/5 symbols heuristically tested. Only tested through `tests/unit/ui/screens/test_event_log_replay_button.py`. Phase 1 flagged:
  - `ReplayResolver` class — exercised by test but no dedicated resolver tests
  - `ReplayResolver.from_registries` (lines 76-87) — classmethod construction, MINOR
  - **Actual gap:** The `resolve` method has 5 distinct return paths with different `ReplayLookup` states:
    1. Empty `replay_id` → `found=False, reason="missing"` (lines 96-97)
    2. `store.replay_dir is None` → `found=False, reason="missing"` (lines 103-104)
    3. `load_or_error` returns `(None, reason)` → `found=False, reason=reason` (lines 107-108)
    4. Load successful, registry drift detected → `found=True, registry_drift=True` (lines 112-116)
    5. Load successful, sidecar verification status attached (lines 120-121)

  These paths are likely exercised by the event log replay button test, but not verified at the unit level.

**Verdict:** MAJOR — dedicated unit test for `ReplayResolver.resolve` with each of the 5 result states would be valuable.

---

### ADVISORY → Various severity: `game/ui/panels/race_portrait_gallery.py` (171 LOC, ui layer)

- 4/12 symbols heuristically tested. The 8 untested symbols are all template-method overrides of `BaseGallery` abstract methods. These are exercised indirectly through the base gallery test which instantiates `RacePortraitGallery`. **ADVISORY (tested indirectly).**

---

### ADVISORY: `game/ui/panels/system_tree_panel.py` (711 LOC, ui layer)

- 15/25 symbols heuristically tested. 10 untested symbols are purely UI tree manipulation (`add_child`, `set_expanded`, `set_position`, `show`, `hide`, `layout`, `_hide_recursive`, `process_event`, `set_dimensions`, `_get_empire_context`). These are pygame_gui widget operations. **ADVISORY.**

Note: At 711 LOC, this file exceeds the 500 LOC ceiling. It should be split, which would incidentally create smaller testable units.

---

### MAJOR: `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` (191 LOC, ui layer)

- 8/9 symbols heuristically tested. Phase 1 flagged `_get_registries` (lines 174-191) as untested. This is a module-level helper called by `duplicate_squadron` and `duplicate_task_force`. It has two paths:
  1. Registry provider available → returns `GameRegistries` (lines 181-189)
  2. Exception caught → returns `None` (line 190-191)

  The exception path is likely untested. **MAJOR** for the fallback path only.

---

### MAJOR: `game/ui/screens/battle_setup/spec_compiler.py` (459 LOC, ui layer)

- 5/9 symbols heuristically tested. The 4 private helper functions (`_build_team_spec`, `_task_force_for_fleet`, `_pick_formation_for_fleet`, `_build_modifier_stack`) are all exercised through `build_manual_battle_spec`. The Phase 1 scanner couldn't match private functions to test imports. These are effectively covered through compiler tests.
  
  **Actual gaps:** Deep branch coverage in the spec compiler — fleet with no ships, empty task forces, modifier stack building with complex toggles enabled/disabled, seed generation when None provided.

**Verdict:** MAJOR for specific branch gaps within the covered functions.

---

### MINOR: `game/ui/screens/empire_build_queue_formatter.py` (189 LOC, ui layer)

- 8/9 symbols heuristically tested. `format_turns_remaining` (lines 117-128) is a pure formatting function:
  - `turns <= 0` → "Complete" (line 127)
  - `turns > 0` → formatted float (line 128)
  `format_turns_remaining(0)` → "Complete" and `format_turns_remaining(1.25)` → "1.25 turns" would verify. **MINOR.**

---

### MINOR: `game/ui/screens/planet_list_sidebar.py` (286 LOC, ui layer)

- 1/2 symbols heuristically tested. `add_range` is a local function inside `build_sidebar` (lines 199-203). It's called 3 times with different parameters. Since `build_sidebar` IS tested, this is covered indirectly. **MINOR.**

---

### MAJOR: `game/ui/screens/strategy_click_dispatcher.py` (634 LOC, ui layer)

- 12/26 symbols heuristically tested. The 13 `_handle_*_mode_click` methods flagged by Phase 1 are all UI mode click handlers. Many are exercised through `test_strategy_click_dispatcher.py`. However, the following have shallow coverage:

  **Business logic tested (MAJOR gaps):**
  - `_handle_move_mode_click` — choice path (move vs intercept) vs success path — the choice/prompt branch may not be tested
  - `_handle_join_mode_click` — choice path with multiple fleets vs direct success
  - `_handle_colonize_mode_click` — prompt path (multiple planets), single planet, success path
  
  **ADVISORY (thin delegates):**
  - `_handle_transfer_mode_click`, `_handle_drop_cargo_mode_click`, `_handle_load_cargo_mode_click` — all delegate to `_handle_dialog_mode_click`
  - `_handle_warp_target_click`, `_handle_edit_move_click`
  - `_handle_implode_planet_click`, `_handle_stellerate_star_click`, `_handle_open_warp_click`, `_handle_close_warp_click`, `_handle_dyson_sphere_click` — all delegate to `_handle_superweapon_click`

  **Key gap:** `_handle_superweapon_click` has an error-surface path that shows UI error messages (line 344-345). This error-handling path needs verification.

**Verdict:** MAJOR for superweapon error-handling path. ADVISORY for thin delegate methods.

---

### MINOR: `game/ui/screens/test_lab/formatting_utils.py` (67 LOC, ui layer)

- 1/2 symbols heuristically tested. `_format_float` (lines 33-67) is a private helper called by `format_value`. It has 6 branch paths:
  1. Essentially integer → `int(round(value))` (line 44-45)
  2. Probability 0 < value < 1, compact → percentage (line 50)
  3. Probability 0 < value < 1, full → percentage (line 51)
  4. Small number, compact → scientific notation (line 57)
  5. Small number, full → scientific notation (line 58)
  6. Large number compact (line 61-62)
  7. Regular full precision (line 67)
  8. Regular compact precision (line 66)

  These are all exercised through `format_value` which IS tested. However, the test may not exercise each precision/branch combination. **MINOR.**

---

### MAJOR: `game/ui/services/battle_ui_service.py` (321 LOC, ui layer)

- 10/14 symbols heuristically tested. Phase 1 flagged 4 untested:
  - `_target_display_name` (lines 43-59): Has 3 return paths — ship with `.name`, projectile with `.type`, None. Used by `_convert_ship`. Exercised indirectly.
  - `BattleUIService.__init__` (line 78): Trivial attribute assignment. MINOR.
  - `_convert_component` (lines 240-266): Called by `_convert_ship`. Exercised indirectly.
  - `_convert_beam` (lines 305-321): Called by `get_recent_beams`. Exercised indirectly.

  **Actual gap:** `_target_display_name` edge cases — target with neither name nor type (returns None), projectile with numeric type, target with malformed type enum.

**Verdict:** MAJOR for `_target_display_name` edge cases. MINOR for the rest.

---

## Tier 3 — Verified Coverage

### Confirmed Covered (13 files):

| File | Test Files | Status |
|------|-----------|--------|
| `game/core/patterns/layer_iterator.py` (162 LOC) | `test_layer_iterator.py` (90 assertions) | CONFIRMED |
| `game/core/validation_helpers.py` (222 LOC) | `test_validation_helpers.py` (64 assertions) | CONFIRMED |
| `game/research/data/tech_node.py` (158 LOC) | 8 test files, 45+ assertions | CONFIRMED |
| `game/services/llm/factory.py` (79 LOC) | `test_factory.py` (20 assertions) | CONFIRMED |
| `game/simulation/entities/combat_endurance.py` (155 LOC) | `test_combat_endurance.py` (156 assertions) | CONFIRMED |
| `game/strategy/data/colony_species_config.py` (118 LOC) | 7 test files | CONFIRMED |
| `game/strategy/data/ship_stats_cache.py` (66 LOC) | `test_ship_stats_cache.py` | CONFIRMED |
| `game/strategy/data/spectrum.py` (73 LOC) | `test_spectrum.py` + 12 others | CONFIRMED |
| `game/strategy/facade/dto/system_dto.py` (162 LOC) | `test_system_dto.py`, `test_star_info_dto.py` | CONFIRMED |
| `game/ui/components/table/data_source.py` (111 LOC) | `test_data_source.py` (18 assertions) | CONFIRMED |
| `game/ui/panels/base_gallery.py` (265 LOC) | `test_base_gallery.py` | CONFIRMED |
| `game/ui/screens/builder/drop_target.py` (15 LOC) | `test_builder_interaction.py` | CONFIRMED |
| `game/ui/screens/strategy_screen_composition.py` (114 LOC) | `test_strategy_screen_composition.py` | CONFIRMED |

---

## File Coverage Verification

| File | Layer | Tier | Status | Findings |
|------|-------|------|--------|----------|
| `game/core/patterns/layer_iterator.py` | core | 3 | CONFIRMED | 6/6 symbols tested |
| `game/core/validation_helpers.py` | core | 3 | CONFIRMED | 6/6 symbols tested |
| `game/research/data/tech_node.py` | research | 3 | CONFIRMED | 9/9 symbols tested |
| `game/services/llm/factory.py` | services | 3 | CONFIRMED | 3/3 symbols tested |
| `game/services/provider_factory.py` | services | 0 | **CRITICAL** | 0/1 symbols tested |
| `game/simulation/battle_spec.py` | simulation | 2 | MAJOR | `__post_init__` branch 3 untested |
| `game/simulation/combat/attack_contract.py` | simulation | 2 | MINOR | `WeaponFamilyMetadata` instantiation untested |
| `game/simulation/combat/combat_events.py` | simulation | 2 | MINOR | Unsubscribe no-op / detail level setter untested |
| `game/simulation/components/component_health_manager.py` | simulation | 2 | MINOR | `__init__` is trivial |
| `game/simulation/entities/combat_endurance.py` | simulation | 3 | CONFIRMED | 2/2 symbols tested |
| `game/simulation/entities/ship_stat_querier.py` | simulation | 2 | MINOR | `__init__` is trivial |
| `game/simulation/entities/stat_contributors/command.py` | simulation | 0 | **CRITICAL** | 0/2 symbols tested |
| `game/simulation/entities/stat_contributors/weapons.py` | simulation | 0 | **CRITICAL** | 0/1 symbols tested |
| `game/strategy/combat/pre_tick_setup/mine_setup.py` | strategy | 0 | **MAJOR** | 0/2 symbols directly tested |
| `game/strategy/combat/pre_tick_setup_registry.py` | strategy | 2 | MAJOR | Duplicate reject, param-count detection untested |
| `game/strategy/data/colony_species_config.py` | strategy | 3 | CONFIRMED | 6/6 symbols tested |
| `game/strategy/data/fleet.py` | strategy | 2 | MAJOR | `_unregister_from_target` complex logic untested |
| `game/strategy/data/race_config.py` | strategy | 2 | MAJOR | 7 validators only tested via `validate()` |
| `game/strategy/data/resource_generation_config.py` | strategy | 2 | MAJOR | Affinity defaults/JSON load branches |
| `game/strategy/data/ship_consumable_manager.py` | strategy | 2 | MINOR | `__init__` is trivial |
| `game/strategy/data/ship_stats_cache.py` | strategy | 3 | CONFIRMED | 4/4 symbols tested |
| `game/strategy/data/spectrum.py` | strategy | 3 | CONFIRMED | 4/4 symbols tested |
| `game/strategy/engine/empire_economy_calculator.py` | strategy | 2 | MAJOR | Deep branches in private helpers |
| `game/strategy/engine/game_session.py` | strategy | 2 | MAJOR | `process_turn` error rollback path |
| `game/strategy/engine/handlers/order_queue.py` | strategy | 2 | MINOR | `register()` function indirectly tested |
| `game/strategy/events/__init__.py` | strategy | 1 | ADVISORY | Re-export shim |
| `game/strategy/facade/dto/system_dto.py` | strategy | 3 | CONFIRMED | 5/5 symbols tested |
| `game/strategy/interfaces/engines/planet_ops.py` | strategy | 0 | MAJOR | ABCs, no executable logic |
| `game/strategy/services/component_layers.py` | strategy | 0 | **MAJOR** | 0/4 symbols directly tested |
| `game/strategy/services/replay_resolver.py` | strategy | 2 | MAJOR | 5 resolution paths in `resolve()` |
| `game/ui/components/__init__.py` | ui | 0 | ADVISORY | Package docstring |
| `game/ui/components/table/data_source.py` | ui | 3 | CONFIRMED | 7/7 symbols tested |
| `game/ui/panels/base_gallery.py` | ui | 3 | CONFIRMED | 17/17 symbols tested |
| `game/ui/panels/race_portrait_gallery.py` | ui | 2 | ADVISORY | Template-method overrides tested indirectly |
| `game/ui/panels/system_tree_panel.py` | ui | 2 | ADVISORY | UI widget operations, 711 LOC exceeds ceiling |
| `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` | ui | 2 | MAJOR | `_get_registries` exception path |
| `game/ui/screens/battle_setup/spec_compiler.py` | ui | 2 | MAJOR | Private helpers covered, deep branches need verification |
| `game/ui/screens/battle_ui.py` | ui | 1 | **MAJOR** | 0/9 symbols directly tested, business logic gaps |
| `game/ui/screens/builder/__init__.py` | ui | 1 | ADVISORY | Re-export shim |
| `game/ui/screens/builder/drop_target.py` | ui | 3 | CONFIRMED | 4/4 symbols tested |
| `game/ui/screens/defeat_dialog.py` | ui | 0 | ADVISORY | UI rendering code |
| `game/ui/screens/empire_build_queue_formatter.py` | ui | 2 | MINOR | `format_turns_remaining` branch test |
| `game/ui/screens/planet_list_sidebar.py` | ui | 2 | MINOR | Local function `add_range` covered indirectly |
| `game/ui/screens/strategy_click_dispatcher.py` | ui | 2 | MAJOR | Superweapon error-handling path |
| `game/ui/screens/strategy_screen_composition.py` | ui | 3 | CONFIRMED | 18/18 symbols tested |
| `game/ui/screens/test_lab/details/chrome.py` | ui | 0 | ADVISORY | Pure rendering functions |
| `game/ui/screens/test_lab/formatting_utils.py` | ui | 2 | MINOR | `_format_float` branch combos |
| `game/ui/services/battle_ui_service.py` | ui | 2 | MAJOR | `_target_display_name` edge cases |

---

## Context Usage Estimate
- **Total production LOC read:** ~9,451
- **Total test LOC sampled for verification:** ~2,100
- **Test files verified:** 12 of 100+ candidate test files
- **Largest files read:** `strategy_click_dispatcher.py` (634), `system_tree_panel.py` (711), `fleet.py` (632), `game_session.py` (498), `spec_compiler.py` (459)
