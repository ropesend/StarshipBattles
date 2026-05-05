# Verified Shard 07 — Test Coverage Audit (Skeptical Phase)

**Verification Date:** 2026-05-04
**Verifier:** OpenCode skeptical verification agent
**Source Report:** `SHARD_07.md`

---

## Summary

| Metric | Value |
|--------|-------|
| Claims reviewed | 11 (2 CRITICAL + 7 MAJOR + 1 MINOR sample + 1 ADVISORY sample) |
| CONFIRMED | 2 (1 MAJOR, 1 MINOR) |
| DISPUTED | 2 (both CRITICAL) |
| INCONCLUSIVE | 0 |
| Downgrades | 2 CRITICAL→ADVISORY, 6 MAJOR→MINOR |
| Upgrades | 0 |
| Discovery Agent Errors | 3 (matrix false negatives) |

---

## Key Findings

**Both CRITICAL claims are DISPUTED.** The coverage matrix had false negatives:
1. `strategy_domain.py` TypeGuards ARE tested in `tests/unit/core/test_protocols.py`
2. `event_slice.py` IS tested through the facade in `tests/unit/strategy/facade/test_event_queries.py`

**6 of 7 MAJOR claims are DOWNGRADED to MINOR.** Extensive indirect/integration coverage was missed. Only one MAJOR claim stands: `_facility_has_ability` in `planet_order_validator.py` — genuinely zero coverage.

**The coverage matrix has systemic false negatives.** 3 additional files (labels.py, strategy_screen_selection.py, replay_store.py) were already corrected in the Phase 2 report. Beyond those, 4 more files have test coverage the matrix missed: strategy_domain.py (TypeGuards only), event_slice.py (facade tests), spec_compiler.py (614-line test file), build_queue_manager.py (290-line test file).

---

## CRITICAL Claims — Verification

### CRITICAL-1: `game/core/protocols/strategy_domain.py` (194 LOC)

**Claim:** No test file exists. Zero coverage. 35 untested symbols including TypeGuards.

**Verification:**
- `is_empire`, `is_facility`, `is_ship_instance` ARE tested in `tests/unit/core/test_protocols.py` (109 lines of TypeGuard tests, lines 109-183). The `TestTypeGuardFunctions` class parametrizes `returns_false` for 10 cases, and `TestNoneSafety` verifies all TypeGuards return `False` for `None`.
- `tests/unit/core/test_protocols_public_api.py` explicitly lists `is_empire`, `is_facility`, `is_ship_instance` as public API symbols and verifies they import correctly.
- Protocol definitions (IEmpire, IFacility, IRaceRegistry, IShipInstance) are `@runtime_checkable` stubs — all methods have `...` bodies. They are pure type declarations with no behavioral logic to test.
- `_has_attrs` (from common.py) is a one-liner: `return all(hasattr(obj, attr) for attr in attrs)` — trivially correct, tested through every TypeGuard.
- Protocol definitions can only be tested for `isinstance` checks, which `test_protocols.py` tests exhaustively for the entity protocols (IFleet, IPlanet, etc.). The strategy-domain protocols follow the same pattern.

**Verdict:** **DISPUTED** — TypeGuards ARE tested. Protocol definitions are type declarations with no logic, not testable in a meaningful behavioral sense. The matrix produced a false negative (did not detect `test_protocols.py` importing strategy-domain TypeGuards).

**Severity:** ~~CRITICAL~~ → **ADVISORY** (TypeGuards tested; protocols are pure declarations)

**Residual gap:** None. If protocol `isinstance` tests are desired for IEmpire/IFacility/IShipInstance, they could be added to `test_protocols.py` in the pattern used for IFleet/IPlanet, but this is cosmetic.

---

### CRITICAL-2: `game/strategy/facade/slices/event_slice.py` (96 LOC)

**Claim:** No test file exists. Zero coverage. All branching (empire_id scoping, turn defaulting) untested.

**Verification:**
- `EventSlice` is the `_event` slot of `StrategySessionFacade`. The facade delegates directly to `EventSlice` methods for all event queries.
- `tests/unit/strategy/facade/test_event_queries.py` (195 lines) tests ALL EventSlice methods through the facade with real `EventLog` instances:
  - `get_turn_events(turn=None)` default-to-current: `test_defaults_to_current_turn` (line 40)
  - `get_turn_events(empire_id=None)` vs scoped: `test_get_turn_events_scopes_to_empire` (line 184)
  - `get_all_events(empire_id=None)` vs scoped: `test_get_all_events_scopes_to_empire` (line 171), `test_get_all_events_unscoped_returns_everything` (line 178)
  - `get_events_by_category(empire_id=None)` vs scoped: `test_get_events_by_category_scopes_to_empire` (line 190)
  - All methods: `test_returns_dicts_not_event_objects` (line 57, 91, 139) — verify `.to_dict()` conversion
  - Empty results: `test_returns_empty_list_for_turn_with_no_events` (line 52), `test_returns_empty_list_when_no_events` (line 86), `test_returns_empty_for_unmatched_category` (line 129)
  - Category filtering: `test_filters_by_category` (line 105), `test_all_category_returns_everything` (line 118), `test_accepts_string_category` (line 149)
- `tests/unit/ui/screens/test_strategy_window_manager.py` (line 262-274): Tests `get_all_events(empire_id=7)` scoping through the facade
- `tests/unit/ui/screens/test_event_log_window.py` (line 261): Exercises `get_all_events` and `get_turn_events` through the facade surface
- `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` (lines 103-105): Enumerates event query methods as public API

**Verdict:** **DISPUTED** — All EventSlice methods and their branching logic are tested through the facade integration path. The empire_id scoping (None vs specified), turn defaulting, category filtering, dict conversion, and empty-result paths all have explicit tests in `test_event_queries.py`. The facade delegates directly to EventSlice — the test path exercises the same code.

**Severity:** ~~CRITICAL~~ → **ADVISORY** (fully tested through facade)

**Residual gap:** `get_human_player_ids`, `get_turn_number`, `get_save_path` are simple delegating properties not independently unit-tested, but they have no behavioral logic (just return session values).

---

## MAJOR Claims — Verification

### MAJOR-1: `game/ui/screens/battle_setup/spec_compiler.py` (467 LOC)

**Claim:** 2/10 symbols tested. 8 internal functions untested.

**Verification:**
- `tests/unit/ui/screens/battle_setup/test_spec_compiler.py` (614 lines) contains:
  - 10 module-level tests for `build_manual_battle_spec` (returns BattleSpec, side ship flow, instance IDs, telemetry, boundary, modifier stacks, ship non-mutation, empty state)
  - `TestNTeamBattleSetupCompiler` (7 tests): 3/4 side teams, ring layout entry vectors, 2-side regression, enemy fan-out for 3 teams, boundary checks
  - `TestEmitEntriesForAbilityTeamRouting` (6 tests): enemy sector fan-out 2/3/4 teams, self-scope routing, deleted function verification
  - `TestExtractScopeResolvesClassDefault` (7 tests): `_extract_scope` tested directly with ShieldModifier, DamageModifier, ShieldProjection, explicit scope, primitives, unknown ability
- Functions tested directly: `build_manual_battle_spec`, `_extract_scope`
- Functions tested indirectly (through `build_manual_battle_spec` in all 614 lines of tests): `_build_team_spec`, `_task_force_for_fleet`, `_pick_formation_for_fleet`, `_ship_spec_from_instance`, `_build_modifier_stack`, `_complex_to_entries`
- The matrix claim "2/10 symbols tested" is a severe undercount — the 10 public-importable functions are all exercised
- Genuinely untested in isolation: `_load_complex_design` (OSError path, line 411), `_iter_components` (layer iteration), `_ship_spec_from_instance` (pose=None fallback)

**Verdict:** **DOWNGRADED MAJOR → MINOR** — The file has 614 lines of tests with extensive coverage. Most internal functions are tested indirectly through the public API `build_manual_battle_spec`, which is appropriate. The only real gap is isolated error-path testing for `_load_complex_design` (OSError) and `_iter_components`.

**Suggested tests:**
- Test `_load_complex_design` with missing file returns None
- Test `_load_complex_design` with malformed JSON returns None
- Test `_ship_spec_from_instance` with pose=None falls back to Vector2(0,0), 0.0

---

### MAJOR-2: `game/strategy/services/replay_store.py` (322 LOC)

**Claim:** Integration-tested but lacks unit tests. Multiple error paths untested.

**Verification:**
- `tests/integration/replay/test_replay_store.py` (306 lines) covers:
  - Settings: `test_load_returns_defaults_when_missing`, `test_load_parses_real_file`, `test_load_clamps_to_minimum_one`, `test_load_falls_back_on_malformed_json`
  - Persist/load/list: `test_persist_writes_a_replay_file`, `test_persist_returns_none_when_no_save_root`, `test_load_round_trips`, `test_list_sorted_newest_first`
  - Delete: `test_delete_removes_file`, `test_delete_returns_false_for_missing`
  - Ring buffer: `test_evicts_excess_after_write`, `test_writes_before_evicting`
  - Graceful degradation: `test_corrupt_file_skipped_in_list`, `test_schema_mismatch_skipped`, `test_load_returns_none_for_schema_mismatch`
  - Capture sink: `test_started_then_ended_persists_record`, `test_started_returns_empty_when_no_save_root`, `test_ended_without_matching_start_is_a_noop`
  - Lifecycle hooks: `TestSaveGameServiceHooks` (3 tests)
- The Phase 2 report incorrectly claimed these paths as "untested":
  - `on_battle_ended` missing pending: **TESTED** — `test_ended_without_matching_start_is_a_noop` (line 245)
  - `on_battle_started` no save root: **TESTED** — `test_started_returns_empty_when_no_save_root` (line 239)
  - `persist` no save root: **TESTED** — `test_persist_returns_none_when_no_save_root` (line 122)
  - `_safe_load` corrupt JSON: **TESTED** — `test_corrupt_file_skipped_in_list` (line 187)
  - `_safe_load` schema mismatch: **TESTED** — `test_schema_mismatch_skipped` (line 195)
  - `load` schema mismatch: **TESTED** — `test_load_returns_none_for_schema_mismatch` (line 205)
  - `delete` file missing: **TESTED** — `test_delete_returns_false_for_missing` (line 143)
  - `list` corrupt skip: **TESTED** — `test_corrupt_file_skipped_in_list` (line 187)
- Genuinely untested: `_evict_excess` OSError during `p.unlink()` (line 297) — requires filesystem simulation to test the exception handler

**Verdict:** **DOWNGRADED MAJOR → MINOR** — The integration test suite covers nearly all error paths. The report's list of "untested" paths was largely wrong. Only the OSError during eviction is genuinely uncovered.

**Suggested test:** Test `_evict_excess` OSError during unlink using a mock that raises OSError on specific files.

---

### MAJOR-3: `game/strategy/validation/planet_order_validator.py` (149 LOC)

**Claim:** `_facility_has_ability` untested. 3 branches with zero coverage.

**Verification:**
- `_facility_has_ability` is called by both `validate_activate_ability` (line 49) and `validate_deactivate_ability` (line 103)
- Grep for `_facility_has_ability` across all tests: **0 matches**
- Command handler tests (`tests/unit/strategy/engine/test_planet_command_handlers.py`) mock `PlanetOrderValidator.validate_*` entirely via `patch.object` — the validator's internal logic, including `_facility_has_ability`, is NEVER exercised
- No dedicated `test_planet_orders.py` or `test_planet_order_validator.py` exists
- The 3 branches at lines 137-148:
  1. `isinstance(comp, dict)` with `ability_name in comp.get('abilities', {})` → True
  2. `isinstance(comp, dict)` with `comp_id and component_registry` → registry lookup
  3. `isinstance(comp, str) and component_registry` → registry lookup
  All 3 branches have zero coverage

**Verdict:** **CONFIRMED** — `_facility_has_ability` is genuinely untested. This is a business-logic function with 3 branches backing both validate methods. A bug here could silently allow or block ability activation orders.

**Suggested tests:** Add to `tests/unit/strategy/validation/test_planet_order_validator.py`:
```python
def test_facility_has_ability_inline_dict():
    """Dict component with ability name in abilities dict."""
    facility = MagicMock()
    facility.design_data = {"layers": {"CORE": [{"id": "comp1", "abilities": {"PlanetaryShield": {"value": 100}}}]}}
    assert _facility_has_ability(facility, "PlanetaryShield") is True

def test_facility_has_ability_dict_with_registry_lookup():
    """Dict component with comp_id → registry lookup for abilities."""
    facility = MagicMock()
    facility.design_data = {"layers": {"CORE": [{"id": "shield_gen"}]}}
    registry = {"shield_gen": {"abilities": {"PlanetaryShield": {"value": 100}}}}
    assert _facility_has_ability(facility, "PlanetaryShield", registry) is True

def test_facility_has_ability_string_component_with_registry():
    """String component reference → registry lookup."""
    facility = MagicMock()
    facility.design_data = {"layers": {"CORE": ["shield_gen"]}}
    registry = {"shield_gen": {"abilities": {"PlanetaryShield": {"value": 100}}}}
    assert _facility_has_ability(facility, "PlanetaryShield", registry) is True

def test_facility_does_not_have_ability():
    """Returns False when no component has the ability."""
    facility = MagicMock()
    facility.design_data = {"layers": {"CORE": [{"id": "comp1", "abilities": {"Other": {}}}]}}
    assert _facility_has_ability(facility, "PlanetaryShield") is False
```

---

### MAJOR-4: `game/ui/screens/strategy_screen.py` (458 LOC)

**Claim:** `current_empire` IndexError edge case (empty `human_player_ids`). 12 untested symbols.

**Verification:**
- `current_empire` property (line 185-188):
  ```python
  @property
  def current_empire(self) -> Any:
      current_player_id = self.human_player_ids[self.current_player_index]
      return next((e for e in self.empires if e.id == current_player_id), self.empires[0])
  ```
- This property IS exercised extensively — grep found 43 references across ~20 test files
- Test setup in `_make_strategy_screen()` sets `session.human_player_ids = [0]` and `session.empires = [MagicMock(id=0), MagicMock(id=1)]` — so the property is called but only with valid data
- No test explicitly sets `human_player_ids = []` and accesses `current_empire` to verify the IndexError
- The "12 untested symbols" are delegating properties (`galaxy`, `empires`, `systems`, delegates) — all tested through their delegate modules' tests
- `run_n_turns` delegates to `_game_state` which has its own test file (`test_strategy_game_state_manager.py`)
- FEAT-20 dev-mode properties (`dev_run_cancel_requested`, `turn_processing_message`) are UI state flags tested indirectly in turn processing tests
- Issue #7 tick properties (`current_tick`, `total_ticks`) are set during `process_full_turn` which is tested in `test_strategy_game_state_manager.py`
- Test file is comprehensive: `test_strategy_screen.py` (866 lines)

**Verdict:** **DOWNGRADED MAJOR → MINOR** — `current_empire` is exercised but the IndexError edge case is not explicitly tested. All other "untested" symbols are delegating properties tested through their delegates. The StrategyScreen test file is 866 lines with thorough coverage of initialization, lifecycle, turn management, events, navigation, resize, and error paths.

**Suggested test:**
```python
def test_current_empire_with_empty_human_player_ids_raises_index_error(self):
    screen, _ = _make_strategy_screen()
    screen.session.human_player_ids = []
    with pytest.raises(IndexError):
        _ = screen.current_empire
```

---

### MAJOR-5: `game/ui/screens/planet_list_filters.py` (385 LOC)

**Claim:** Private predicates not isolated. `effects_predicate` AND-composition, `_owner_predicate` branching, `get_column_value` attr chain walking untested in isolation.

**Verification:**
- `tests/unit/ui/screens/test_planet_list_filters.py` (385 lines) contains:
  - `TestPlanetListFilters` (2 tests): `filter_planets` by type with filter composition
  - `TestGatherPlanetsCachesSystemLocation` (2 tests): system location caching
  - `TestComputePlanetEffectKeys` (5 tests): dedup, subtype discrimination, sorting
  - `TestEffectsPredicate` (7 tests): no-op/all-IGNORE, YES/NO presence/absence, AND composition, mixed IGNORE, EnvironmentalDamage subtype discrimination for both YES and NO
  - `TestFilterPlanetsWithEffects` (1 test): effects+type AND composition
- `effects_predicate` has a dedicated test class with 7 comprehensive tests covering all FilterState combinations
- `_owner_predicate` (3 branches: None → 'Unowned', owner_id == empire_id → 'Player', else → 'Enemy') is tested through `filter_planets` in `TestPlanetListFilters`
- `_name_predicate`, `_type_predicate`, `_range_predicate` are tested through `filter_planets`
- `get_column_value` (2 branches: 'func', 'attr' with dot walking) is NOT independently tested
- `compute_planet_ranges` (padding calculation, empty list) is NOT independently tested
- `get_owner_name` (empire lookup loops, star indicator) is NOT independently tested

**Verdict:** **DOWNGRADED MAJOR → MINOR** — The test file is thorough (385 lines, matching the production file in size). `effects_predicate` has dedicated, exhaustive tests. Other predicates are tested through `filter_planets` composition. The report's emphasis on "isolated" testing is a reasonable aspiration but current coverage is strong.

**Suggested tests:** Add isolated tests for `get_column_value` (dot-walk attr chain, fmt string), `compute_planet_ranges` (empty list defaults, padding), and `get_owner_name` (star indicator).

---

### MAJOR-6: `game/ui/screens/strategy_build_queue_manager.py` (271 LOC)

**Claim:** `_get_registries` lazy init untested. `__init__` untested.

**Verification:**
- `tests/unit/ui/screens/test_strategy_build_queue_manager.py` (290 lines) EXISTS — the Phase 2 report and matrix missed this
- Tests:
  - `TestBuildQueueManagerInit` (1 test): Verifies `__init__` stores screen reference
  - `TestOnBuildYardClick` (4 tests): Already-open guard, no selection, non-planet, owned planet open
  - `TestOnBuildQueueClose` (3 tests): Clears BQS, shows UI, refreshes selected object
  - `TestHandleFleetBuildQueueClose` (3 tests): IssueBuildOrderCommand dispatch, already-has-BUILD guard, RemoveBuildOrderCommand dispatch
  - `TestOnFleetBuildClick` (3 tests): Already-open guard, non-fleet selection, fleet with shipyard
  - `TestOnNavigateToHexBuild` (3 tests): Already-open guard, no entity, valid source
- `__init__` is tested: `test_init_stores_screen_reference` (line 43)
- `_get_registries` is a module-level function used in `on_build_yard_click`, `on_navigate_to_hex_build`, `on_fleet_build_click` — but in tests, `DesignLoaderAdapter` is patched, so `_get_registries`'s lazy-init caching is not exercised
- `_get_registries` is a simple lazy-caching pattern (module-level `_cached_registries = None`, set once from `get_default_registry_provider()`) — low risk

**Verdict:** **DOWNGRADED MAJOR → MINOR** — The module has 290 lines of tests with comprehensive coverage of all public methods. `_get_registries` is a simple caching function. The report's claim of "no test file" was a matrix false negative.

**Suggested test:**
```python
def test_get_registries_returns_cached_on_second_call(self):
    """_get_registries should cache and return same instance on second call."""
    import game.ui.screens.strategy_build_queue_manager as m
    m._cached_registries = None
    r1 = m._get_registries()
    r2 = m._get_registries()
    assert r1 is r2
```

---

### MAJOR-7: `game/ui/screens/builder/detail_panel.py` (295 LOC)

**Claim:** 8 methods untested. `on_selection_changed` branching, `show_component` caching logic.

**Verification:**
- `tests/unit/ui/test_detail_panel_rendering.py` (245 lines) tests:
  - `test_html_stats_generation_basic`: `show_component` with Name, Type, Mass, HP
  - `test_html_stats_dynamic_abilities`: `show_component` with `get_ui_rows` output
  - `test_html_unregistered_abilities`: `show_component` with ABILITY_REGISTRY-skipped abilities
  - `test_html_modifiers`: `show_component` with mandatory/optional modifier formatting
  - HTML comparison caching logic (lines 121-124, 188-191 in production) IS exercised — `last_img_comp` and `last_html` checks are hit every time `show_component` is called with different components
- Untested:
  - `on_selection_changed` (line 85): 4 branches (None, tuple, hasattr id, else) — NOT tested in the rendering test (focus is on `show_component`)
  - `show_details_popup` (line 193): JSON popup construction — NOT tested (creates UIWindow, UITextBox)
  - `_clear_display` (line 224): image cleanup — NOT tested directly (exercised through `show_component(None)`)
  - `_update_image` (line 231): image loading with cache, fallback placeholder — NOT tested directly (exercised through `show_component`)
  - `set_position` (line 276): one-line delegate — NOT tested
  - `handle_event` (line 280): always returns False — trivial
  - `draw` (line 288): no-op placeholder — trivial

**Verdict:** **DOWNGRADED MAJOR → MINOR** — `show_component` (the primary business-logic method) has 4 dedicated tests covering stat generation, dynamic abilities, unregistered ability fallback, and mandatory/optional modifier formatting. The HTML caching logic IS exercised. `on_selection_changed` branching is the most significant gap (not tested in isolation). `show_details_popup` is UI popup construction. `_update_image` is pure image loading. `set_position`, `handle_event`, `draw` are trivial (1-line delegate, `return False`, `pass`).

**Suggested tests:**
- Test `on_selection_changed` with 4 input types (None, tuple, hasattr id, fallback)
  ```python
  def test_on_selection_changed_with_tuple_dispatches_third_element(self):
      mock_comp = MagicMock()
      self.panel.on_selection_changed((0, 1, mock_comp))
      assert self.panel.current_component is mock_comp

  def test_on_selection_changed_with_none_clears(self):
      self.panel.current_component = MagicMock()
      self.panel.on_selection_changed(None)
      assert self.panel.current_component is None
  ```

---

## MINOR Claims — Sampled Verification

### MINOR-1: `game/ai/behaviors.py` — `_flee_direction` (line 65)

**Claim:** `_flee_direction` zero-length vector edge case untested.

**Verification:**
- Grep for `_flee_direction` across all tests: **0 matches**
- The function is `_`-prefixed (private) and is NOT imported or tested directly
- It IS called by `FleeBehavior.update()` and `AttackRunBehavior.update()` — both tested in `test_behavior_units.py` and `test_advanced_behaviors.py`
- The zero-length vector branch (line 77-78): `if vec.length() == 0: return Vector2(1, 0)` — requires `from_pos == away_from_pos`
- No test targets this specific edge case

**Verdict:** **CONFIRMED** — The zero-length vector edge case is genuinely untested. Functions tested through `update()` methods, but those tests use distinct positions and never exercise `vec.length() == 0`.

---

## ADVISORY Claims — Sampled Verification

### ADVISORY-1: `game/core/protocols/common.py` (46 LOC)

**Claim:** Pure Protocol definitions, no tests needed. `_has_attrs` tested indirectly.

**Verification:**
- Confirmed correct classification. `ILocatable`, `INamed`, `IOwnable` are `@runtime_checkable` protocol stubs with no implementation.
- `_has_attrs` is a one-liner: `return all(hasattr(obj, attr) for attr in attrs)` — trivially correct.
- `_has_attrs` IS exercised indirectly by every TypeGuard test in `test_protocols.py` (109+ lines of TypeGuard tests call `is_fleet`, `is_planet`, etc., which all use `_has_attrs`).

**Verdict:** **CONFIRMED** — Correctly classified as ADVISORY.

---

## Disputed & Inconclusive Claims

| Claim ID | File | Original Severity | Verdict | Reason |
|----------|------|-------------------|---------|--------|
| CRITICAL-1 | `game/core/protocols/strategy_domain.py` | CRITICAL | **DISPUTED** → ADVISORY | TypeGuards tested in `test_protocols.py`; protocols are pure declarations |
| CRITICAL-2 | `game/strategy/facade/slices/event_slice.py` | CRITICAL | **DISPUTED** → ADVISORY | All methods+branching tested through facade in `test_event_queries.py` |

---

## Severity Changes

| Claim ID | From | To | Rationale |
|----------|------|-----|-----------|
| CRITICAL-1 | CRITICAL | **ADVISORY** | TypeGuards tested; protocols are type declarations |
| CRITICAL-2 | CRITICAL | **ADVISORY** | Fully tested through facade |
| MAJOR-1 | MAJOR | **MINOR** | 614 lines of tests cover all public functions |
| MAJOR-2 | MAJOR | **MINOR** | 306 lines of integration tests cover almost all error paths |
| MAJOR-4 | MAJOR | **MINOR** | Property exercised extensively; only IndexError edge case untested |
| MAJOR-5 | MAJOR | **MINOR** | 385-line test file with comprehensive predicate coverage |
| MAJOR-6 | MAJOR | **MINOR** | 290-line test file exists (matrix missed); `_get_registries` is simple caching |
| MAJOR-7 | MAJOR | **MINOR** | `show_component` well-tested; untested methods are trivial or UI rendering |

---

## CONFIRMED Gaps (After Verification)

| File | Severity | Gaps | Suggested Test File |
|------|----------|------|---------------------|
| `game/strategy/validation/planet_order_validator.py` | **MAJOR** | `_facility_has_ability` — 3 branches with zero coverage. Backs both `validate_activate_ability` and `validate_deactivate_ability`. | `tests/unit/strategy/validation/test_planet_order_validator.py` |
| `game/ui/screens/battle_setup/spec_compiler.py` | MINOR | `_load_complex_design` OSError path, `_iter_components` edge cases, `_ship_spec_from_instance` pose=None fallback | Extend `test_spec_compiler.py` |
| `game/strategy/services/replay_store.py` | MINOR | `_evict_excess` OSError during unlink | Extend `test_replay_store.py` |
| `game/ui/screens/strategy_screen.py` | MINOR | `current_empire` property with empty `human_player_ids` → IndexError | Extend `test_strategy_screen.py` |
| `game/ui/screens/planet_list_filters.py` | MINOR | `get_column_value` dot-walk, `compute_planet_ranges` empty-list defaults, `get_owner_name` star indicator | Extend `test_planet_list_filters.py` |
| `game/ui/screens/strategy_build_queue_manager.py` | MINOR | `_get_registries` lazy-init cache behavior | Extend `test_strategy_build_queue_manager.py` |
| `game/ui/screens/builder/detail_panel.py` | MINOR | `on_selection_changed` 4-branch dispatch | Extend `test_detail_panel_rendering.py` |
| `game/ai/behaviors.py` | MINOR | `_flee_direction` zero-length vector edge case | Extend `test_behavior_units.py` |

---

## Discovery Agent Errors

The Phase 2 coverage matrix produced **3 false negatives** already corrected in the Phase 2 report (labels.py, strategy_screen_selection.py, replay_store.py). This verification found **additional errors**:

| Error | File | Matrix Claim | Actual |
|-------|------|-------------|--------|
| FN-4 | `game/core/protocols/strategy_domain.py` | TIER_0 (no tests) | TypeGuards tested in `tests/unit/core/test_protocols.py` |
| FN-5 | `game/strategy/facade/slices/event_slice.py` | TIER_0 (no tests) | Fully tested through `tests/unit/strategy/facade/test_event_queries.py` |
| FN-6 | `game/ui/screens/battle_setup/spec_compiler.py` | "2/10 symbols tested" | 614 lines of tests; all major functions exercised |
| FN-7 | `game/ui/screens/strategy_build_queue_manager.py` | (claimed no test file) | 290-line test file at `test_strategy_build_queue_manager.py` |

**Root cause:** The coverage matrix uses heuristic name matching only — if a test file's name doesn't closely match the production file (e.g., `test_protocols.py` covering `strategy_domain.py`, `test_event_queries.py` covering `event_slice.py`), it reports false negatives. Cross-module testing (facade → slice, protocols umbrella → domain-specific) is invisible to the heuristic.

---

## Verification Confidence

| Aspect | Confidence | Notes |
|--------|-----------|-------|
| CRITICAL claims | HIGH | Both disputed with direct evidence from test files |
| MAJOR claims | HIGH | All 7 verified by reading production + test files |
| MINOR sample | HIGH | MINOR-1 confirmed with grep evidence |
| ADVISORY sample | HIGH | ADVISORY-1 confirmed as correct |
| Matrix errors | HIGH | 4 additional false negatives identified |

**Overall confidence: HIGH.** All CRITICAL and MAJOR claims verified with production + test file reads.
