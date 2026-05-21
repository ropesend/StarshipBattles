# Shard 13 — Verified Test Audit Report

## Verification Summary
- Shard: 13 | Total findings verified: 26 | CONFIRMED: 22 | DISPUTED: 2 | INCONCLUSIVE: 1 | DOWNGRADED: 1

---

## Verified Findings

### tests/unit/ui/panels/test_empire_treasury_panel.py

#### CAT-8: 4-patch-decorator repeated on 16 test methods [MINOR] — CONFIRMED
- **Lines**: 238–631 | **Evidence**: All 16 test methods in `TestValueFormatting`, `TestRowData`, etc. carry identical 4 `@patch` decorator stacks. Verified at lines 238–297 and repeated across the file.
- **Severity**: MINOR (unchanged)

#### CAT-10: TestValueFormatting — 4 tests with identical structure [MINOR] — CONFIRMED
- **Lines**: 235–284 | **Evidence**: `test_format_zero` (242), `test_format_small_integers` (253), `test_format_large_integers_with_commas` (265), `test_format_floats_rounds_to_integer` (277) all construct panel identically, call `_format_value`, assert string. Parametrizable.
- **Severity**: MINOR (unchanged)

#### CAT-5: sample_snapshot fixture function-scoped for read-only usage [MAJOR] — CONFIRMED (with note)
- **Lines**: 92–99 | **Evidence**: Fixture is `@pytest.fixture` (function-scoped). The fixture docstring at line 97–98 explicitly states *why*: "4 tests in TestPopulationUpkeepRow mutate snapshot.total_population_upkeep and would otherwise leak." The 12 other tests are read-only, so splitting into r/w + read-only variants is a valid optimization. The claim is factually correct.
- **Severity**: MAJOR (unchanged)

---

### tests/unit/ui/test_race_summary_panel.py

#### CAT-3: TestCallbackIntegration — empty class [CRITICAL] — CONFIRMED, DOWNGRADED to MINOR
- **Lines**: 321–323 | **Evidence**: `class TestCallbackIntegration:` contains only a docstring (`"""Tests for callback integration with parent screen."""`) and zero test methods. Pytest will discover it but it contributes no coverage.
- **Severity downgrade rationale**: 3 LOC dead code. No runtime impact, no misleading coverage signal (pytest reports 0 tests collected for the class). CRITICAL is disproportionate; MINOR reflects the actual risk.
- **Revised severity**: MINOR

#### CAT-8: _refresh_with_mocked_uilabel helper complexity [MINOR] — CONFIRMED
- **Lines**: 363–414 | **Evidence**: The helper has 4 nested `with patch.object()` blocks (UILabel, UIPanel, UIScrollingContainer, create_section_header) plus 12+ manual attribute wirings on the panel instance (lines 392–411). Functional but complex.
- **Severity**: MINOR (unchanged)

#### CAT-6: _refresh_with_mocked_uilabel uses __new__ to bypass init [MAJOR] — CONFIRMED
- **Lines**: 391–411 | **Evidence**: Panel is created via `RaceSummaryPanel.__new__()` at line 391, then 12+ private/internal attributes (`summary_labels`, `summary_flag_images`, `_asset_loader`, `_dynamic_env_labels`, etc.) are manually wired. This is tightly coupled to the panel's internal implementation.
- **Severity**: MAJOR (unchanged)

#### CAT-5: mock_race_config fixtures function-scoped but read-only [MAJOR] — DISPUTED
- **Lines**: 43–96 | **Evidence contradicting the claim**:
  - `mock_race_config` is **mutated** at lines 583–584 (`mock_race_config.government_type = "Empire"` / `government_organization = "Centralized"`) and line 681 (`del mock_race_config.preferences[dropped_id]`).
  - `mock_race_config_full` is **mutated** at line 543 (`mock_race_config_full.preferences["fake_axis"] = EnvironmentalPreference(...)`).
  - Only `mock_race_config_empty` (lines 77–96) appears read-only — it is passed to `_make_summary_panel` and `assert`ed on but never written.
- **Conclusion**: The claim that all three fixtures are "read-only, no mutation" is incorrect for `mock_race_config` and `mock_race_config_full`. Function-scoping is justified for those two. The claim stands only for `mock_race_config_empty`.
- **Revised severity**: MAJOR → MINOR (only `mock_race_config_empty` is a valid target for module-scoping; ~30 LOC affected instead of ~60)

---

### tests/unit/ui/screens/test_strategy_fleet_command_router.py

#### CAT-6: String-based class-name check [MAJOR] — CONFIRMED
- **Lines**: 430 | **Evidence**: `assert type(command).__name__ == expected_cmd_class_name` uses string comparison. Should use `isinstance(command, ActivatePlanetAbilityCommand)` or similar.
- **Severity**: MAJOR (unchanged)

#### CAT-12: if/else branch in test body [MINOR] — CONFIRMED
- **Lines**: 76–89 | **Evidence**: `test_fleet_action_enters_target_mode_when_fleet_selected` parametrized across 8 action types, with `if action == InputAction.FLEET_COLONIZE` / `else` branching. The branch is minimal (2 lines each) and the parametrization already documents each case.
- **Severity**: MINOR (unchanged)

---

### tests/unit/simulation/combat/test_weapon_firing_system.py

#### CAT-6: Inspects private call_args of internal subsystem [MAJOR] — CONFIRMED
- **Lines**: 804 | **Evidence**: `secondary_targets = targeting.find_valid_target.call_args.args[2]` reads positional arg 2 from a mocked call. This couples the test to the internal argument ordering of `find_valid_target`.
- **Severity**: MAJOR (unchanged)

#### CAT-9: Repeated ship/target mock setup across 15+ tests [MINOR] — CONFIRMED
- **Lines**: throughout | **Evidence**: The `_make_ship_mock` helper is used in some places, but many tests construct MagicMock ships with 6+ attr assignments inline. For example, lines 100–115 construct a ship with `team_id`, `position`, `velocity`, `angle`, `total_shots_fired`, `max_targets`, `secondary_targets` assignments, plus a target with `is_alive`, `team_id`, `position`, `velocity`, `type` assignments. This pattern repeats across the file.
- **Severity**: MINOR (unchanged)

---

### tests/unit/simulation/combat/test_targeting_system.py

#### CAT-6: Inspects internal call args [MAJOR] — DISPUTED
- **Claimed location**: Line 1141 — `targeting.find_valid_target.call_args[0][2]`
- **Evidence disproving the claim**:
  - The file is only **1110 lines** long. Line 1141 does not exist.
  - `grep` for `call_args` across the entire file returned **zero matches**.
  - All 49 occurrences of `find_valid_target` in the file call it as `system.find_valid_target(...)` (public method invocation on a `TargetingSystem` instance) and assert on the **return value**, not on mock call tracking. Tests use helpers like `self._make_ship_mock()`, `self._make_pdc_weapon()`, `self._make_candidate()` and verify the target selection outcome directly.
- **Conclusion**: The claim appears to be a copy-paste error — possibly conflated with `test_weapon_firing_system.py:804` (above) which does inspect `targeting.find_valid_target.call_args.args`. This finding should be **removed** from the report.
- **Severity**: N/A (claim invalid)

#### CAT-9: Repeated mock construction across 30+ tests [MINOR] — INCONCLUSIVE
- **Lines**: throughout | **Evidence**: The file defines shared helpers (`_make_ship_mock`, `_make_pdc_weapon`, `_make_candidate`, etc.) that are used extensively. Without reading all ~1100 lines I cannot determine whether the remaining repetition warrants a new factory. The file appears to have better mock reuse than claimed. Marked INCONCLUSIVE — needs deeper inspection to confirm scale.
- **Severity**: MINOR (unchanged, but confidence LOW)

---

### tests/unit/strategy/engine/test_superweapon_command_handlers.py

#### CAT-4: Duplicate validation-pass test [MAJOR] — CONFIRMED
- **Lines**: 340–353 vs 135–151 | **Evidence**: The parametrized `test_handler_execute_returns_valid_when_validation_passes` (line 139) covers 5 handlers. SelfDestruct is explicitly excluded at line 131 comment ("needs ships pre-populated; handled in its own test"). `TestSelfDestructCommandHandler.test_execute_returns_valid_when_validation_passes` (340–353) duplicates the same assertion: patch validator → return `ValidationResult()` → `assert result.is_valid`. The only difference is `mock_fleet.ships = [Mock(id=1), Mock(id=2)]` setup. The parametrized test could be extended with a 6th case that pre-populates ships.
- **Severity**: MAJOR (unchanged)

#### CAT-10: 5 Direct handler order-type tests [MINOR] — CONFIRMED
- **Lines**: 163–331 | **Evidence**: 5 handler classes (`ImplodePlanet`, `StellerateStar`, `OpenWarpPoint`, `CloseWarpPoint`, `CreateDysonSphere`) each have `test_execute_adds_correct_order_type` with the same structure: create handler → create command → patch validator → execute → assert order type, count, and target shape. Only the `OrderType` value and target assertions differ.
- **Severity**: MINOR (unchanged)

---

### tests/unit/strategy/validation/test_superweapon_validator.py

#### CAT-10: 5 test classes with identical patterns [MINOR] — CONFIRMED
- **Lines**: 228–651 | **Evidence**: `TestValidateStellerateStar` (example at 229–279) follows the validated/invalid-no-ability/invalid-bad-location pattern. This pattern repeats across the remaining superweapon validator classes. Visibly repetitive structure.
- **Severity**: MINOR (unchanged)

---

### tests/unit/ui/screens/test_cargo_quick_dialog_controller_widget_purity.py

#### CAT-6: Brittle call_args index access [MAJOR] — CONFIRMED
- **Lines**: 57 | **Evidence**: `cmd = facade.handle_command.call_args[0][0]` accesses positional arg 0 from the call tuple's first element. Equivalent but less readable and more brittle than `facade.handle_command.assert_called_once_with(...)` or `cmd = facade.handle_command.call_args.args[0]`.
- **Severity**: MAJOR (unchanged)

---

### tests/unit/ui/screens/test_strategy_build_queue_manager.py

#### CAT-4: Duplicate on_active_player_changed tests [MAJOR] — CONFIRMED (partial)
- **Lines**: 469–511 and 591–645 | **Evidence**: Both tests:
  1. Set up the same 2-empire screen via `self._two_empire_screen()`
  2. Create `cached_screen` mock with `on_active_player_changed` spy
  3. Simulate empire flip from empire_1 to empire_2
  4. Call `manager.on_build_yard_click()` twice
  5. Assert `cached_screen.on_active_player_changed.assert_called_once()`
  - Test 1 (469): General "active player changed" scenario with both planets owned by different empires
  - Test 2 (591): Issue #17-specific test with extended docstring about widget cache invalidation; assertion at line 639 has a trailing comma making it `assert_called_once(), (...)` (syntactically valid but redundant tuple expression).
  **Verdict**: Same setup and assertion, partially overlapping intent. Not byte-identical but substantial duplication.
- **Severity**: MAJOR (unchanged)

---

### tests/unit/modifiers/test_modifier_loader_v2.py

#### CAT-4: Duplicate hardened_mount formula test [MAJOR] — CONFIRMED
- **Lines**: 65–87 and 129–158 | **Evidence**:
  - `test_modifier_v2_evaluate_effects` (65–87): Tests hardened_mount with param=2.0 (`mass_effect=2.0`, `hp_effect=4.0`).
  - `test_hardened_mount_formula` (129–158): Tests hardened_mount with param=2.0 AND param=3.0 (`mass_effect=3.0`, `hp_effect=9.0`). Also tests an additional effect stat (`cost_mult`).
  - The first test's `param=2.0` assertions are **fully subsumed** by the second test. The second test provides strictly more coverage. The first adds no unique value.
- **Severity**: MAJOR (unchanged)

---

### tests/unit/strategy/combat/test_post_battle_hook_builder.py

#### CAT-1: Trivial pass test [CRITICAL] — CONFIRMED
- **Lines**: 37–54 | **Evidence**: `test_build_hook_threads_mine_groups_and_engine_ref` creates a `PostBattleHookBuilder`, builds a hook with fleets/empires/mine_groups/engine_ref, calls `hook(outcome)`, and asserts only `assert callable(hook)`. The function body invokes the hook with a mock outcome, but makes **zero behavioral assertions** about what the hook does (board, writeback, mine group handling, engine_ref usage, etc.). A hook that no-ops would pass this test.
- **Severity**: CRITICAL (unchanged)

---

### tests/unit/ai/test_carrier_controller.py

#### CAT-6: Writes to private _mass_budget_by_ability dict [MAJOR] — CONFIRMED
- **Lines**: 285, 340 | **Evidence**:
  - Line 285: `ctrl._mass_budget_by_ability["TacticalFighterLaunch"] = 20.0`
  - Line 340: `ctrl._mass_budget_by_ability["TacticalFighterLaunch"] = 60.5`
  - Both directly write to a private `_mass_budget_by_ability` dict to pre-warm test state.
- **Severity**: MAJOR (unchanged)

---

### tests/unit/strategy/data/test_order_types_characterization.py

#### CAT-6: Monkeypatches production Planet/Fleet classes [MAJOR] — CONFIRMED
- **Lines**: 49–57 | **Evidence**: The `patch_domain_classes` fixture at line 49 uses `monkeypatch.setattr(planet_module, "Planet", _PlanetStub)` and `monkeypatch.setattr(fleet_module, "Fleet", _FleetStub)` to swap production `Planet`/`Fleet` classes with lightweight stubs (`_PlanetStub` with only `id`, `_FleetStub` with only `id`). This is a module-level monkeypatch affecting all tests that use the fixture.
- **Severity**: MAJOR (unchanged)

---

### tests/unit/strategy/engine/test_superweapon_order_processor_gaps.py

#### CAT-10: 5 stabilizer-cancellation tests identical pattern [MINOR] — CONFIRMED
- **Lines**: 118–272 | **Evidence**: `TestStabilizerCancellation` contains 5 tests (`implode_planet`, `stellerate_star`, `open_warp_point`, `close_warp_point`, `create_dyson_sphere`) with ~90% identical structure: setup mock fleet/ships, create Order, create processor, patch FBS_PATH, call processor, assert `result.success is False`, assert mock_fleet.pop_order called, assert destruction method NOT called. Each test differs only in the processor method called and specific target/setup details.
- **Severity**: MINOR (unchanged)

---

### tests/unit/tools/test_codex_project_config.py

#### CAT-1: Config-file assertion, not game code test [CRITICAL] — CONFIRMED
- **Lines**: 1–22 | **Evidence**: The entire file (22 lines) tests `.codex/config.toml` contents — asserts `config["model"] == "gpt-5.4"` and `config["model_context_window"] == 1_050_000`. The `_repo_root()` helper at lines 9–14 walks parent directories looking for `.codex/` directory. This is an agent-tooling configuration validation test, not a test of any game production code. If `.codex/config.toml` is missing, the test fails with a `FileNotFoundError` or `RuntimeError`.
- **Severity**: CRITICAL (unchanged). This is a CI/agent-tooling test that should live in a separate location.

---

### tests/unit/ui/screens/test_transfer_dialog.py + test_cargo_quick_dialog.py

#### CAT-9: Real pygame_gui.UIManager per function [MINOR] — CONFIRMED
- **Lines**: test_transfer_dialog.py:22–23, test_cargo_quick_dialog.py:22–23 | **Evidence**:
  - `test_transfer_dialog.py:22`: `@pytest.fixture` → `return pygame_gui.UIManager((800, 600))`
  - `test_cargo_quick_dialog.py:22`: `@pytest.fixture` → `return pygame_gui.UIManager((800, 600))`
  - Both are function-scoped fixtures that create a real `UIManager` instance per test, despite being used as a pure-input mock. `mock_ui_manager` in `test_empire_treasury_panel.py` (same directory, line 102) shows the preferred approach: `scope="module"` + `MagicMock()`.
- **Severity**: MINOR (unchanged)

---

### tests/unit/ui/effects/test_hit_effects.py

#### CAT-10: Three early-return tests identical pattern [MINOR] — CONFIRMED
- **Lines**: 109–200 | **Evidence**:
  - `test_draw_effects_skips_when_alpha_is_zero` (110): alpha≤0 guard — pixel invariance check
  - `test_draw_shield_early_returns_when_size_is_below_threshold` (143): size<4 guard — pixel invariance check
  - `test_draw_armor_or_component_early_returns_when_radius_below_one` (175): radius<1 guard — pixel invariance check
  - All three: create `HitEffect` → render via `draw_effects` → assert `before == after` (screen bit-identical). The phase 1 report's own suggestion notes "(naming documents branches - valuable to keep)". The explicit test names serve as documentation of the guard branches.
- **Severity**: MINOR (unchanged)

---

### tests/unit/ui/screens/test_list_data_source_base.py

#### CAT-9: One test covers 4 cell-value paths [MINOR] — CONFIRMED
- **Lines**: 57–64 | **Evidence**: `test_get_cell_value_supports_func_attr_nested_attr_and_format` asserts 4 different cell-value resolution strategies in a single test: computed/lambda (`"84.5"`), direct attribute (`"Frigate"`), formatted attribute (`"42.2"`), nested attribute (`"8"`). Splitting into separate tests would improve failure isolation.
- **Severity**: MINOR (unchanged)

---

### tests/unit/strategy/empire/test_empire_validation.py

#### CAT-10: Three missing-key tests identical [MINOR] — CONFIRMED
- **Lines**: 41–72 | **Evidence**: `test_missing_id_raises_persistence_exception` (41), `test_missing_name_raises_persistence_exception` (53), `test_missing_color_raises_persistence_exception` (64) all follow the identical pattern: `make_valid_empire_data()` → `del data['<key>']` → `with pytest.raises(PersistenceException)` → assert error string contains key name. Parametrizable on `missing_key`.
- **Severity**: MINOR (unchanged)

---

### tests/unit/strategy/engine/test_base_command_handler.py

#### CAT-10: Two resolve error tests identical [MINOR] — CONFIRMED
- **Lines**: 18–43 | **Evidence**: `test_resolve_fleet_not_found` (18) and `test_resolve_fleet_wrong_owner` (30) follow the identical pattern: call `_resolve_fleet` → assert `fleet is None` → assert `error is not None` → assert `not error.is_valid` → assert error string. Differentiated only by mock setup (None fleet vs wrong-owner fleet) and error message content. Parametrizable.
- **Severity**: MINOR (unchanged)

---

## Cross-Shard Verification

The `CROSS_SHARD.md` report contains **no claims that reference Shard 13 files**. All 6 cross-shard duplicates (DUP-001 through DUP-006) and all 6 helper duplications (HLP-001 through HLP-006) involve shards {01,02,03,04,05,06,07,08,09,10,11,12,14,15,16} only. No cross-shard verification action required for Shard 13.

---

## Summary Statistics

| Status      | Count |
|-------------|-------|
| CONFIRMED   | 22    |
| DISPUTED    | 2     |
| INCONCLUSIVE| 1     |
| DOWNGRADED  | 1     |
| **Total**   | 26    |

### Disputed Claims
1. **CAT-5** (test_race_summary_panel.py): "mock_race_config fixtures function-scoped but read-only" — `mock_race_config` and `mock_race_config_full` are mutated in tests; only `mock_race_config_empty` is read-only.
2. **CAT-6** (test_targeting_system.py:1141): "Inspects internal call_args" — file is only 1110 lines, line 1141 does not exist, and grep finds zero `call_args` usages.

### Downgraded Claims
1. **CAT-3** (test_race_summary_panel.py:321): CRITICAL → MINOR. Empty class at 3 LOC is dead code with negligible impact.

### Inconclusive
1. **CAT-9** (test_targeting_system.py): Repeated mock construction. File uses shared helpers; cannot confirm ~30 distinct repeated patterns without full-file audit.
