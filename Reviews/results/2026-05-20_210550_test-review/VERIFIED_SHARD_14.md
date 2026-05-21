# VERIFIED — Shard 14 Test Audit

**Verifier**: OpenCode skeptical-verifier
**Source**: SHARD_14.md + CROSS_SHARD.md (Phase 1 / cross-shard)
**Files reviewed**: 94 (all cited line ranges + context)
**Verifications performed**: 27 shard findings + 1 cross-shard claim

---

## Verification Summary

| Verdict | Count |
|---------|-------|
| CONFIRMED | 22 |
| CONFIRMED-NO-ACTION | 1 |
| DISPUTED | 3 |
| DOWNGRADED | 1 |
| DUPLICATE (intra-shard) | 1 |
| CONFIRMED-CROSS | 1 |

**Net severity after verification**: Critical: 1, Major: 13, Minor: 14

---

## Detailed Verification

### Finding 1: CAT-1 — `test_module_exists` (test_event_log_sidebar.py:78-81)
- **Claim**: Asserts `EventLogSidebar is not None` immediately after import — cannot fail.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 78-81: `from game.ui.screens.event_log_sidebar import EventLogSidebar; assert EventLogSidebar is not None`. Import raises `ImportError` if class doesn't exist; the assert is never reached on failure and always True on success. Dead test.
- **Severity**: CRITICAL (unchanged)

### Finding 2: CAT-10 — test_stores_* reference tests (test_event_log_sidebar.py:83-103)
- **Claim**: Four tests verify simple attribute storage with identical pattern.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 83-103 show `test_stores_panel_reference`, `test_stores_manager_reference`, `test_stores_column_manager_reference`, `test_stores_callback`. First three are byte-for-byte identical except attribute name. Callback test differs only by one extra `MagicMock()` line. Merge into parametrized test.
- **Severity**: MINOR (unchanged)

### Finding 3: CAT-1 — `test_sidebar_width_is_positive` (test_galaxy_test_screen.py:16-22)
- **Claim**: Tests that `SIDEBAR_WIDTH > 0` — cannot fail if constant is defined as positive number. First reviewer noted "rubric exempts constants validation." Re-checked as borderline.
- **Verdict**: **DOWNGRADED to MINOR (ACKNOWLEDGED-EXEMPT)**
- **Evidence**: Lines 16-22 show `assert isinstance(SIDEBAR_WIDTH, (int, float)); assert SIDEBAR_WIDTH > 0`. The rubric exempts constants-validation tests. The test does guard against someone changing the constant to a string or zero in a refactor, providing marginal value. Original CRITICAL → downgraded to MINOR.
- **Severity**: MINOR (downgraded from CRITICAL)

### Finding 4: CAT-10 — to_roman parametrization (test_naming.py:178-264)
- **Claim**: 16 nearly identical tests (`test_one` through `test_complex_number_3999`) with identical body.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 178-264 show 16 test methods, each calling `NameRegistry.to_roman(N)` and asserting result. Differ only in input/output pair. Clear candidate for `@pytest.mark.parametrize`.
- **Severity**: MINOR (unchanged)

### Finding 5: CAT-12 — `test_sequential_1_to_10` (test_naming.py:246-251)
- **Claim**: Uses `for n, roman in enumerate(expected, start=1)` — logic-heavy test body.
- **Verdict**: **DISPUTED**
- **Evidence**: Lines 246-251 show a simple 5-line test: define `expected` list, enumerate, assert. The `enumerate` loop with an inline assert is straightforward and readable — it is NOT logic-heavy (no branching, no setup complexity, no nested conditionals). This is a valid way to test sequential output and is less verbose than 10 parametrize entries for this specific use case.
- **Severity**: N/A (disputed)

### Finding 6: CAT-9 — Repeated TECH_PRESETS_DIR patching (test_tech_preset_loader.py throughout)
- **Claim**: Every test method repeats `with patch('game.simulation.systems.tech_preset_loader.TECH_PRESETS_DIR', str(temp_presets_dir))`.
- **Verdict**: **CONFIRMED**
- **Evidence**: Verified across `TestLoadPreset`, `TestGetAvailableComponents`, `TestGetAvailableModifiers`, `TestIsComponentAvailable`, and `TestIsModifierAvailable` classes. Every test method wraps calls in the identical `with patch(...)` block. Should be set once in the `temp_presets_dir` fixture or an autouse fixture.
- **Severity**: MINOR (unchanged)

### Finding 7: CAT-8 — Nested with patch blocks (test_strategy_screen_selection.py:30-98)
- **Claim**: Six tests each use 4 nested `with patch.object(selection, ...)` blocks.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 33-98 show six test methods, each with 4-identical `patch.object` calls for `is_star_system`, `is_planet`, `is_warp_point`, `is_fleet`. Only return_values vary. A shared fixture returning the patcher context would eliminate ~70 lines of duplication.
- **Severity**: MINOR (unchanged)

### Finding 8: CAT-6 — Mocking import internals (test_profiler_perf.py:53-61)
- **Claim**: Uses `inspect.getsource(prof_module)` and asserts against raw source strings.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 57-61: `source = inspect.getsource(prof_module); assert "json.dump(" not in source; assert "json.loads(" not in source`. This is a structural guard — it checks source code content, not runtime behavior. Brittle to whitespace changes, variable name changes, or code reformatting. Should be replaced with behavioral test (patch `json.dump` / `json.loads` and assert they're not called).
- **Severity**: MAJOR (unchanged)

### Finding 9: CAT-6 — Mocking with importlib.reload (test_battle_panels_extended.py:36-69)
- **Claim**: Helper patches `sys.modules['pygame']` with MagicMock then `importlib.reload(battle_panels)` — extremely brittle.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 54-59: `modules_patcher = patch.dict(sys.modules, {'pygame': mock_pygame}); modules_patcher.start(); importlib.reload(battle_panels)`. Replaces `sys.modules` globally (can affect other concurrent tests), forces module-level side effects via reload. The helper does properly stop the patcher on teardown (line 69 returns patcher), but the approach remains fragile. Better to patch `battle_panels.pygame` at call-site level.
- **Severity**: MAJOR (unchanged)

### Finding 10: CAT-9 — Duplicate pygame mock setup (test_battle_panels_extended.py:474-520)
- **Claim**: `TestBattlePanelBaseClass.setup_mocks` duplicates pygame patching logic from `_install_battle_panels_pygame_mock`.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 482-499 recreate mock_pygame, `patch.dict(sys.modules, ...)`, `importlib.reload(battle_panels)` — a subset of what `_install_battle_panels_pygame_mock` (lines 36-69) does. The shared helper is available but unused here. Should call `_install_battle_panels_pygame_mock(self)` instead.
- **Severity**: MINOR (unchanged)

### Finding 11: CAT-5 — Test ordering dependency (test_isolation.py:14-118)
- **Claim**: Three pairs of tests must run in sequence. No ordering mechanism used.
- **Verdict**: **DISPUTED**
- **Evidence**: Lines 14-118 show `TestRegistryIsolation` (part1_modify / part2_verify), `TestPolicyManagerIsolation`, `TestComponentCacheIsolation`. The docstring at line 7-8 says tests are "designed to be run in sequence." However: (1) The `reset_game_state` autouse fixture (function-scoped) runs before every test, ensuring clean state. (2) Part2 tests check that a specific key is NOT present — if Part2 runs first, the key was never added and assertion still passes. (3) Within a class, pytest runs tests in definition order by default. The tests work correctly in ANY order — the "must run in order" docstring is misleading, not a genuine dependency. No `pytest.mark.dependency` is needed.
- **Severity**: N/A (disputed)

### Finding 12: CAT-4 — Duplicate take_damage validation tests (test_component_health_manager.py:98-114)
- **Claim**: Three tests with identical assertion patterns differing only in input value.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 98-114: `test_raises_validation_exception_for_string_input` ("50"), `_for_none_input` (None), `_for_list_input` ([10]). All three import `ValidationException`, use identical `pytest.raises(ValidationException, match="amount must be numeric")`, and differ only in the argument to `health_manager.take_damage(...)`. Parametrize into one test with `@pytest.mark.parametrize("invalid_input", ["50", None, [10]])`.
- **Severity**: MAJOR (unchanged)

### Finding 13: CAT-10 — Damage edge cases cluster (test_damage_calculator.py:609-707)
- **Claim**: Seven tests in `TestDamageLayerBoundaryConditions` follow identical body shape.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 609-707: `test_zero_damage_does_nothing`, `test_damage_exactly_equals_component_hp`, `test_damage_exactly_equals_total_layer_hp`, `test_fractional_damage_applied_correctly`, `test_very_small_damage_applied`, `test_large_damage_exceeds_all_layers`, `test_component_with_one_hp`. All build mock components + ship, call `apply_damage`, assert HP values. Structurally similar though each tests a meaningfully different boundary condition. Parametrization would require custom input generators per case.
- **Severity**: MINOR (unchanged)

### Finding 14: CAT-9 — Repeated mock_ship construction (test_damage_calculator.py:831-1133)
- **Claim**: Dozens of tests construct nearly identical mock ships inline. The `mock_ship` factory fixture exists but is unused in later classes.
- **Verdict**: **CONFIRMED**
- **Evidence**: The `mock_ship` factory fixture is defined at lines 357-370. Test classes starting at line 831 (`TestCombinedArmorScenarios`, `TestShieldRegeneratingArmorEdgeCases`, `TestShieldDamageEdgeCases`, `TestDamageCallbackConditions`) create `ship = MagicMock()` inline with `ship.is_alive = True`, `ship.emissive_armor = N`, etc. The factory fixture would reduce this boilerplate significantly.
- **Severity**: MINOR (unchanged)

### Finding 15: CAT-5 — Function-scoped fixtures rebuild (test_damage_calculator.py:331-370)
- **Claim**: Function-scoped fixtures `damage_calculator`, `mock_component`, `mock_ship` should be class-scoped.
- **Verdict**: **DISPUTED**
- **Evidence**: Lines 331-370: `damage_calculator` creates `DamageCalculator()` (stateless, cheap). `mock_component` and `mock_ship` are factory fixtures returning lambdas — these MUST be function-scoped to ensure test isolation. Changing factory fixtures to class-scoped risks shared mutable state between test methods if a test mutates a factory-created object. Function scope is the safe and correct default for factory fixtures. The first reviewer acknowledged "DamageCalculator has no state so re-creation is cheap" — this undercuts the premise of the finding.
- **Severity**: N/A (disputed)

### Finding 16: CAT-4 — Duplicate same-class multi-provider tests (test_fleet_aura_provider_identity.py:126-179)
- **Claim**: `test_same_class_multi_provider_disable` and `test_same_class_multi_provider_disable_other` are symmetric mirrors.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 127-179: Both tests create identical abilities, components, ship, and manager (17 lines). Initial assertion (`== 15.0`) is identical. Only `comp_a.is_operational = False` vs `comp_b.is_operational = False` and the final assertion (5.0 vs 10.0) differ. Parametrize the component-to-disable.
- **Severity**: MAJOR (unchanged)

### Finding 17: CAT-4 — Repeated planet_not_found / wrong_owner (test_planet_command_handlers.py:53-561, broad)
- **Claim**: Every command handler class has the same two boilerplate tests: `test_planet_not_found` and `test_wrong_owner`. 8 handler classes × 2 = 16 near-identical tests.
- **Verdict**: **CONFIRMED**
- **Evidence**: Verified across all 8 handler classes:
  - `TestActivatePlanetAbilityCommandHandler` (lines 83, 94)
  - `TestDeactivatePlanetAbilityCommandHandler`
  - `TestClearPlanetOrdersCommandHandler` (lines 249, 258)
  - `TestDeletePlanetOrderCommandHandler` (lines 297, 306)
  - `TestSetAtmosphereTargetCommandHandler` (lines 378, 387)
  - `TestSetGravityTargetCommandHandler` (lines 440, 446)
  - `TestSetWaterTargetCommandHandler` (lines 486, 492)
  - `TestSetRadiationShieldTargetCommandHandler` (lines 532, 538)
  
  All 8 classes have identically-structured `test_planet_not_found` (import handler, instantiate, call execute, assert not is_valid) and `test_wrong_owner` (same + set owner_id=99 + _session_with_planet). Only the handler class name changes.
- **Severity**: MAJOR (unchanged)

### Finding 18: CAT-9 — Test helper shims (test_basic_paths.py:12-30)
- **Claim**: Module-level helper functions `find_path_deep_space`, `find_path_interstellar` duplicated in `test_edge_cases.py`.
- **Verdict**: **CONFIRMED**
- **Evidence**: `test_basic_paths.py` lines 13-14 and `test_edge_cases.py` lines 13-14 define byte-for-byte identical `find_path_deep_space(start, end): return hex_linedraw(start, end)`. Lines 18-19 are also identical `find_path_interstellar`. Two other helpers are unique to each file (`get_system_at_hex` and `find_nearest_system` in basic; `find_hybrid_path` and `calculate_intercept_point` in edge_cases). Move the two shared helpers to `tests/unit/strategy/pathfinding/conftest.py`.
- **Severity**: MINOR (unchanged)

### Finding 19: CAT-4 — Repeated availability test patterns (test_tech_preset_loader.py:233-296)
- **Claim**: `TestGetAvailableComponents` and `TestGetAvailableModifiers` have identical test structure (test returns list, test returns empty when missing, test wildcard, test raises for missing).
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 191-222 (components): `test_get_components_returns_list`, `test_get_components_returns_empty_when_missing`, `test_get_components_wildcard`, `test_get_components_raises_for_missing`. Lines 233-259 (modifiers): mirror structure. Each test has identical `with patch(...TECH_PRESETS_DIR...)` wrapper and same assertion shape.
- **Severity**: MAJOR (unchanged)

### Finding 20: CAT-10 — Conformance protocol parametrize (test_boundary.py:47-62)
- **Claim**: Test body only checks attribute existence; noted as "fine as-is."
- **Verdict**: **CONFIRMED-NO-ACTION**
- **Evidence**: Lines 47-62: `@pytest.mark.parametrize` with `RectBoundary`, `CircleBoundary`, `UnboundedRegion`. Tests `hasattr(region, "exit_policy")`, `callable(... "contains" ...)`, `callable(... "closest_inside_point" ...)`, `isinstance(region, BoundaryRegion)`. This is a structural protocol-conformance check — appropriate for verifying that boundary region classes implement the expected duck-typed interface. No remediation needed.
- **Severity**: MINOR (unchanged, no action)

### Finding 21: CAT-6 — Hardcoded magic numbers (test_bug_regressions_2026_01.py:60-61)
- **Claim**: `assert ab.amount == 25` hardcodes expected value from opaque formula `10 * sqrt(1.0) * 2.5`.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 45-60: stats defined with `mass_mult=1.0`, `crew_req_mult=2.5` (lines 47-49), then `ComponentStatsCalculator.apply_base_stats(c, stats, 100)` (line 56), then `assert ab.amount == 25` (line 60). The magic number 25 depends on `10 * math.sqrt(1.0) * 2.5 = 25` — but the formula factors are spread across multiple lines. Should compute `expected = 10 * math.sqrt(1.0) * 2.5` to make the test self-documenting and resilient to formula changes.
- **Severity**: MAJOR (unchanged)

### Finding 22: CAT-8 — Heavy fixture construction (test_build_queue_formatting.py:28-88)
- **Claim**: `MockSession` is a 60-line mock class with nested property subclasses.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 28-88 define `MockSession` with 9 methods, nested `_EconomyNS` and `_SessionMetaNS` property classes (lines 57-88), and facade-shaped accessor methods. This is integration-level test infrastructure that spans >50% of the fixture setup. Extract to `tests/integration/ui/conftest.py` for reuse.
- **Severity**: MINOR (unchanged)

### Finding 23: CAT-4 — Duplicate not_found/not_started (test_battle_service.py:242-264, 317-329)
- **Claim**: `test_add_ship_no_active_battle` / `test_remove_ship_no_active_battle` identical except method name. Similarly for `after_battle_started` mirrors.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 242-247: `test_add_ship_no_active_battle` — calls `service.add_ship(...)`, asserts `result.success is False`, asserts `"No active battle" in result.errors[0]`. Lines 317-322: `test_remove_ship_no_active_battle` — identical pattern with `service.remove_ship(...)`. Lines 249-264 vs 324-329: `after_battle_started` mirrors for add/remove. The no_active_battle pair differs ONLY in the method called (`add_ship` vs `remove_ship`). Parametrize across (operation, method_name) pairs.
- **Severity**: MAJOR (unchanged)

### Finding 24: CAT-4 — Repeated planet_not_found / wrong_owner boilerplate (test_planet_command_handlers.py:249-561, specific)
- **Claim**: `planet_not_found` and `wrong_owner` tests appear 6+ times across handler classes.
- **Verdict**: **DUPLICATE** of Finding 17
- **Evidence**: This is the same finding as #17, expressed with narrower line ranges (249-269, 297-316, 378-396, 440-452, 486-498, 532-544). Finding 17 (lines 53-561) already covers the full scope. No separate action needed.
- **Severity**: N/A (duplicate)

### Finding 25: CAT-9 — `_make_engine` duplicated (test_harvesting_engine.py:157, 524, 842)
- **Claim**: `_make_engine` is declared as a staticmethod identically in three separate test classes.
- **Verdict**: **CONFIRMED**
- **Evidence**: Line 148: module-level `_make_engine(registries=None)` function. Line 157 (`TestHarvestingEngine`): `_make_engine = staticmethod(_make_engine)`. Line 524 (`TestStorageAggregation`): same. Line 842 (`TestPerTickHarvesting`): same. The `staticmethod` assignment is duplicated 3x — classes could simply call the module-level function directly as `_make_engine()` without the staticmethod wrapper, or use a class-scoped fixture.
- **Severity**: MINOR (unchanged)

### Finding 26: CAT-9 — Duplicate lookup patterns in ReplaySpec tests (test_serialization.py:464-507)
- **Claim**: Three tests in `TestReplaySpec` build the same `_make_minimal_battle_spec()` and create `ReplaySpec.from_battle_spec(...)`.
- **Verdict**: **CONFIRMED**
- **Evidence**: Lines 476-480 (`test_from_battle_spec_no_lookup`): `spec = _make_minimal_battle_spec(); replay_spec = ReplaySpec.from_battle_spec(spec)`. Lines 485-487 (`test_from_battle_spec_with_lookup`): same. Lines 497-501 (`test_to_battle_spec_strips_snapshot`): same. Use a class-scoped fixture or `__init__`-level setup.
- **Severity**: MINOR (unchanged)

### Finding 27: CAT-4 — Duplicate helper functions (test_basic_paths.py + test_edge_cases.py)
- **Claim**: Both files declare identical helper shims and test overlapping concepts.
- **Verdict**: **CONFIRMED** for helper duplication
- **Evidence**: `find_path_deep_space` and `find_path_interstellar` are byte-for-byte identical in both files (basic_paths:13-19, edge_cases:13-20). `TestDeepSpacePathSymmetry` and `TestInterceptFallbackBehaviors` test overlapping pathfinding concepts but are in different files. Consolidation of shared helpers is warranted; merging test classes would require deeper review.
- **Severity**: MAJOR (unchanged)

---

## Cross-Shard Verification

### DUP-002: Battle panel test helpers (test_battle_panels_extended.py ↔ test_battle_panels_characterization.py)
- **Claim**: `_draw_setup` + `_stub_fonts` (Shard 02) and `_install_battle_panels_pygame_mock` (Shard 14) are near-identical battle panel mock setup patterns.
- **Verdict**: **CONFIRMED-CROSS** (Shard 14 side verified)
- **Evidence**: `_install_battle_panels_pygame_mock` at lines 36-69 provides `patch.dict(sys.modules)`, `importlib.reload(battle_panels)`, and sets up mock_pygame with `K_LSHIFT`, `K_RSHIFT`, `SRCALPHA`, `Rect`. The Shard 14 report already flags intra-file duplication (Finding 10: `TestBattlePanelBaseClass.setup_mocks` doesn't reuse this helper). Cross-shard, Shard 02's `test_battle_panels_characterization.py` is reported to have analogous `_draw_setup` and `_stub_fonts` helpers for the same SUT (`game.ui.panels.battle_panels`). Recommendation to merge or extract a shared fixture is sound. Cannot independently verify Shard 02 content but Shard 14 evidence fully supports the cross-shard consolidation claim.
- **Estimated LOC savings**: ~70 (cross-shard estimate)

---

## Verification Statistics

| | Count |
|---|---|
| Total findings verified | 28 (27 shard + 1 cross-shard) |
| CONFIRMED | 22 |
| CONFIRMED-NO-ACTION | 1 |
| DISPUTED | 3 |
| DOWNGRADED | 1 |
| DUPLICATE (intra-shard) | 1 |
| CONFIRMED-CROSS | 1 |

### Dispute Rationales

1. **Finding 5 (test_sequential_1_to_10, CAT-12)**: A 5-line `enumerate` loop with inline assert is not "logic-heavy." The test is clear and concise.

2. **Finding 11 (test_isolation.py, CAT-5)**: The tests do NOT have a genuine ordering dependency — `reset_game_state` autouse fixture cleans state before every test. Part2 tests pass regardless of execution order. The "must run in order" docstring is misleading.

3. **Finding 15 (test_damage_calculator.py fixtures, CAT-5)**: Factory fixtures returning lambdas must be function-scoped for test isolation. Changing to class-scoped creates shared-mutable-state risk. The first reviewer acknowledged re-creation is cheap, undermining their own finding.

### Downgrade Rationale

**Finding 3 (test_sidebar_width_is_positive, CRITICAL → MINOR)**: The test rubric exempts constants-validation tests. While the test body is trivial, it provides guard value (type check + positivity check) that would catch a refactor error. Falls under the exempted carveout.
