# Verified Shard 12 — Skeptical Verification Report

## Verification Summary

- **Claims reviewed**: 25 (from SHARD_12.md) + 1 (cross-shard)
- **CONFIRMED**: 24
- **DISPUTED**: 1 (CAT-1 CRITICAL #2 downgraded to not-flag — valid regression guard)
- **INCONCLUSIVE**: 0
- **Downgrades applied**: 1 (CRITICAL → no finding — reclassified as CAT-3 regression guard)

---

## Verified Findings

### Finding 1: CAT-1 — `test_phase_4_collapsed_per_decisions` [CRITICAL]
- **File**: `tests/unit/strategy/data/test_planet_fleet_empire_post_436_contract.py:98`
- **Claim**: Single assertion is `assert True` — test cannot fail regardless of code state.
- **Verification**: **CONFIRMED**. Line 98 is literally `assert True`. The docstring (lines 89-96) acknowledges this is a documentation marker, not a behavioral test. Has zero regression value.
- **Severity**: CRITICAL upheld.

### Finding 2: CAT-1 — `test_create_default_turn_engine_factory_not_importable` [CRITICAL → DISPUTED]
- **File**: `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py:313-320`
- **Claim**: Test asserts `not hasattr(turn_engine_module, "create_default_turn_engine")` — "structurally equivalent to `assert True`."
- **Verification**: **DISPUTED**. This is NOT equivalent to `assert True`. The assertion `assert not hasattr(m, "X")` CAN fail — if someone re-adds `create_default_turn_engine` to the module, the test detects the regression. This is a valid deletion regression guard (CAT-3), not a trivial pass (CAT-1). The SHARD_12 report itself acknowledges this on lines 80-82 as a "Valid regression guard" under CAT-3 adj. A test that verifies the absence of a deleted symbol has real regression value.
- **Severity**: Downgraded from CRITICAL to **no finding** — reclassified as CAT-3 regression guard (not flagged per rubric).

### Finding 3: CAT-10 — 18 engine-default property tests [MINOR]
- **File**: `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py:34-178`
- **Claim**: 18 near-identical tests with same 3-line body (isinstance + identity check).
- **Verification**: **CONFIRMED**. Lines 34-178 contain exactly 18 test methods, each following the pattern: import class → build engine → `assert isinstance(engine.X, Class)` → `assert engine.X is engine.X`. Different class imports and property names but identical structure. Parametrization would reduce ~145 LOC to ~15 LOC.
- **Severity**: MINOR upheld.

### Finding 4: CAT-4 — `test_planet_modifier_effect_engine_property_returns_cached_instance` duplicates pattern [MAJOR]
- **File**: `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py:290-302`
- **Claim**: Identical structure to the 18 tests above (isinstance + identity check) but lives in a separate class.
- **Verification**: **CONFIRMED**. Lines 290-302 show the same isinstance + identity check pattern. The test accesses the property twice (lazy cache test) vs. the 18 eager tests which access once, but structurally it follows the same `isinstance` + `is` assertion pattern used everywhere in the file. Could be folded into the parametrized cluster.
- **Severity**: MAJOR upheld (duplication warrants the level).

### Finding 5: CAT-6 — `test_conflict_engine_resolver_guard_present_at_dispatch_site` [MAJOR]
- **File**: `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py:219-251`
- **Claim**: Uses `inspect.getsource()` to read production method source and asserts on string contents. Brittle to reformatting.
- **Verification**: **CONFIRMED**. Lines 235-244 use `inspect.getsource(ConflictResolutionEngine._resolve_combat_at_hex)` and assert `"self._battle_resolver is None" in src`, `"ValueError" in src`, `"battle_resolver" in src`. Any whitespace change, comment addition, or refactoring of the production method would break these string-match assertions without behavioral regression. Replacing with a behavioral test (construct engine with `battle_resolver=None` and verify ValueError) is the correct fix.
- **Severity**: MAJOR upheld (fragile source-inspection tests in production give false negatives during refactoring).

### Finding 6: CAT-6 — `test_registry_module_does_not_import_planet_modifier_effect_engine` [MAJOR]
- **File**: `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py:262-288`
- **Claim**: AST-walks a production file to check import statements. Brittle to refactoring.
- **Verification**: **CONFIRMED**. Lines 262-288 AST-parse `turn_phase_registry.py` and walk nodes checking for `ImportFrom`/`Import` nodes referencing `planet_modifier_effect_engine` or `PlanetModifierEffectEngine`. Though AST-level checks are more robust than string matching (they survive reformatting), they are still structural guards that break on import reorganization without behavioral change. Better suited as a static guard or linter rule.
- **Severity**: MAJOR upheld.

### Finding 7: CAT-6 — `test_order_processor_minimal_order_type_references` [MAJOR]
- **File**: `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py:32-57`
- **Claim**: AST-parses `order_processor.py` and counts `ast.Attribute` nodes referencing `OrderType`. Brittle.
- **Verification**: **CONFIRMED**. Lines 46-57 count `ast.Attribute` nodes where `node.value.id == "OrderType"` and assert `len(refs) <= 2`. Adding a new (unused) `OrderType.X` attribute usage would increase the count without behavioral change. Changing variable names that reference `OrderType` attributes would also break the count. Structural guard, not behavioral test.
- **Severity**: MAJOR upheld.

### Finding 8: CAT-6 — Multiple tests patch `RaceBrowserDialog.__init__` with no-op lambda [MAJOR]
- **File**: `tests/unit/ui/test_race_browser_dialog.py:78,106,132,158,172,208,233,267,290,315,333,373`
- **Claim**: 12 tests use `patch.object(RaceBrowserDialog, '__init__', lambda self, *args, **kwargs: None)` followed by `RaceBrowserDialog.__new__(RaceBrowserDialog)` — bypasses constructor, manually wires attributes, fragile to internal refactoring.
- **Verification**: **CONFIRMED**. All 12 cited locations show exactly this pattern. Each test manually sets attributes (`dialog.race_rows`, `dialog.selected_race`, `dialog.btn_load`, etc.) after bypassing `__init__`. This couples tests to the internal attribute layout of `RaceBrowserDialog`. The suggestion to use `bypass_init` from `tests/fixtures/ui_widget_factory.py` is valid — that pattern already exists in the codebase (per PROJ-327 Phase 4, used in `test_battle_setup_logic.py`).
- **Severity**: MAJOR upheld (12 tests with identical fragile pattern is a maintenance burden).

### Finding 9: CAT-1 adj — `test_no_duplicate_color_values`, `test_colors_dict_is_not_empty` [NOT FLAGGED]
- **File**: `tests/unit/ui/test_colors.py:38-58`
- **Claim**: These are constants validation tests explicitly excluded from CAT-1 by the rubric.
- **Verification**: **CONFIRMED** (as not-flagged). Lines 38-58 test COLORS dict properties — not trivial passes. Line 54 `assert len(seen) + len(duplicates) == len(COLORS)` is a real behavioral assertion. The report correctly excluded these.
- **Severity**: No finding.

### Finding 10: CAT-12 — `test_turn_engine_lazy_properties.py` overall [MINOR]
- **File**: `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` (320 lines)
- **Claim**: File contains logic-heavy AST parsing and `inspect.getsource()` string assertions within test methods.
- **Verification**: **CONFIRMED**. Lines 262-288 contain AST parsing with for loops, isinstance checks, and list-building inside a test method. Lines 219-244 contain `inspect.getsource()` with string assertions. These are heavy analysis logic inside tests rather than test assertions. The suggestion to split AST-guard tests into `tests/static_guards/` is consistent with the existing project pattern.
- **Severity**: MINOR upheld.

### Finding 11: CAT-8 — `setup_method`/`teardown_method` with pygame init duplicated in two test classes [MINOR]
- **File**: `tests/unit/ui/test_modifier_impact_grid.py:10-18, 235-244`
- **Claim**: Both `TestModifierImpactGrid` and `TestPROJ339Characterization` call `pygame.init()` + `pygame.display.set_mode()` + `pygame_gui.UIManager()` per test method.
- **Verification**: **CONFIRMED**. Lines 10-16 (TestModifierImpactGrid.setup_method) and lines 235-241 (TestPROJ339Characterization.setup_method) contain identical pygame initialization blocks. Both create UIManager(800,600) and UIPanel containers. Duplicated setup for two classes in the same file.
- **Severity**: MINOR upheld.

### Finding 12: CAT-8 — `make_mock_ship` helper is 98 lines with deep manager wiring [MINOR]
- **File**: `tests/unit/ui/screens/test_fleet_report_filters.py:12-109`
- **Claim**: Complex helper instantiates `ShipConsumableManager` and `ShipCargoManager`, wires closures for cargo lookups, exposes 10+ parameters.
- **Verification**: **CONFIRMED**. Lines 12-109 define `make_mock_ship()` with 12 parameters. The helper instantiates real `ShipConsumableManager` (line 87) and `ShipCargoManager` (not instantiated but methods mocked with closures at lines 92-104). The cargo-related closures use lambda/`side_effect` to read from a per-ship `cargo_contents` attribute set by individual tests. This is clever but heavy — 98 lines of setup logic in a helper function. Extraction to a shared fixture is warranted.
- **Severity**: MINOR upheld.

### Finding 13: CAT-10 — Warp filter and sort test clusters partially parametrized [MINOR]
- **File**: `tests/unit/ui/screens/test_fleet_report_filters.py:388-448, 451-628`
- **Claim**: 3 warp filter tests (NO/YES/IGNORE) and 5+ sort tests with same structure could be further parametrized.
- **Verification**: **CONFIRMED**. Lines 388-448: three separate test methods (test_filter_hide_warp_capable, test_filter_hide_not_warp_capable, test_filter_show_all_warp_states) all create ships, set filter_state with different FilterState values, assert result length and specific property. Lines 451-628: 8+ sort tests (TestSortShips + TestSortShipsNewColumns) each create ships, call sort_ships with a different key, assert result order. The warp tests are already somewhat clean (3 tri-state values) but the sort tests (serial asc/desc, hp_pct, design, speed, tonnage, warp, spaceyard, transport, cargo, resources) all share the same structure. Continued parametrization would reduce ~150 LOC.
- **Severity**: MINOR upheld.

### Finding 14: CAT-10 — 4 determinism tests with identical structure [MINOR]
- **File**: `tests/integration/strategy/test_deterministic_generation.py:18-127`
- **Claim**: 4 tests all create two identical configs, create sessions, compare attribute. Could be parametrized.
- **Verification**: **CONFIRMED**. Lines 18-127 contain four tests: `test_same_seed_produces_identical_system_coordinates` (lines 18-39), `test_same_seed_produces_identical_star_counts` (lines 41-68), `test_same_seed_produces_identical_planet_counts` (lines 70-97), `test_same_seed_produces_identical_star_types` (lines 99-126). Each differs only in `galaxy_type`, `galaxy_seed`, `system_count`, and the comparison logic. The first three are structurally identical config→session→extract→compare patterns. The star_types test adds a for loop assertion but follows the same setup pattern. Parametrization with `(galaxy_type, seed, system_count, attribute_getter_fn)` tuples would reduce ~90 LOC.
- **Severity**: MINOR upheld.

### Finding 15: CAT-11 — Exact dict match assertion on stockpile calls [MINOR]
- **File**: `tests/unit/strategy/engine/test_order_processor_colonize.py:247-248`
- **Claim**: `assert add_calls == {"metals": 50.0, "organics": 25.0}` breaks if additional resources are added to stockpile seeding or call order changes.
- **Verification**: **CONFIRMED**. Line 247-248 performs an exact dict equality assertion against `call_args_list` of `planet.add_to_stockpile`. If stockpile seeding ever adds a third resource (e.g., `"fuel": 100.0`), this assertion breaks even though the metals/organics values might still be correct. More robust: `assert add_calls["metals"] == 50.0` and `assert add_calls["organics"] == 25.0` (with optional len check for unexpected extras). The `call_args_list` dict comprehension on line 247 assumes exactly 2 calls with dict args; adding more calls would change the dict size.
- **Severity**: MINOR upheld.

### Finding 16: CAT-3 adj — `test_fleet_group_kind.py` regression guards [NOT FLAGGED]
- **File**: `tests/unit/strategy/data/test_fleet_group_kind.py:1-65`
- **Claim**: Tests verify absence of deleted symbols. Valid regression guards.
- **Verification**: **CONFIRMED** (as not-flagged). Lines 26-65 contain `assert not hasattr(f, "group_kind")`, `assert not hasattr(BaseCommandHandler, "_reject_if_non_fleet_group")`, and related tests. These are genuine deletion regression guards — they CAN fail if the deleted code is re-introduced. Correctly excluded from findings.
- **Severity**: No finding.

### Finding 17: CAT-3 adj — `BattleController.run_headless` regression guard [NOT FLAGGED]
- **File**: `tests/unit/simulation/battle_controller/test_execution.py:149-165`
- **Claim**: Tests that `BattleController.run_headless` does NOT exist. Valid regression guard.
- **Verification**: **CONFIRMED** (as not-flagged). Lines 158-165: `assert not hasattr(controller, 'run_headless')`. A real assertion that fails if the deleted method is re-introduced. Correctly excluded.
- **Severity**: No finding.

### Finding 18: CAT-3 adj — `TestNullBattleResolverSymbolAbsent` regression guards [NOT FLAGGED]
- **File**: `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py:305-320`
- **Claim**: Tests verify deleted `_NullBattleResolver` and `create_default_turn_engine` are absent. Valid regression guards.
- **Verification**: **CONFIRMED** (as not-flagged). Lines 308-320: `assert not hasattr(turn_engine_module, "_NullBattleResolver")` and `assert not hasattr(turn_engine_module, "create_default_turn_engine")`. Both are genuine deletion regression guards. Correctly excluded.
- **Severity**: No finding.

### Finding 19: CAT-12 — `test_phase_4_gates_still_pass` uses dynamic imports [MINOR]
- **File**: `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py:60-75`
- **Claim**: Imports two other test modules as side-effects and uses `hasattr` checks to verify named tests exist. Cross-test dependency.
- **Verification**: **CONFIRMED**. Lines 68-75 import `test_order_processor_no_legacy_helpers` and `test_handler_registry_completeness` as `gate_no_legacy` and `gate_completeness`, then assert `hasattr(gate_no_legacy, "test_no_legacy_private_helpers_on_order_processor")` etc. This is a meta-test: it doesn't exercise production code, it verifies that other test files contain expected test function names. If those test files are renamed or their test functions are renamed, this test breaks. Pytest's own discovery is sufficient for this purpose.
- **Severity**: MINOR upheld.

### Finding 20: CAT-9 — Repeated `_make_strategy_screen` calls across 20+ tests [MINOR]
- **File**: `tests/unit/ui/screens/test_strategy_menu_actions.py:15-40`
- **Claim**: Almost every test calls `_make_strategy_screen()` helper. Could be a pytest fixture.
- **Verification**: **CONFIRMED**. Lines 15-40 define the helper `_make_strategy_screen()` which creates a `StrategyScreen` via `__new__` and manually wires `scene_callback`, `ui`, `session` etc. The helper is clean (26 lines, well-documented) but used in most of the 22 tests in the file. Converting to a `@pytest.fixture` with function scope would be a minor refactor with no behavior change. The report correctly marks this as low-priority.
- **Severity**: MINOR upheld.

### Finding 21: CAT-12 — `test_compiler_does_not_mutate_ships` has significant logic [MINOR]
- **File**: `tests/unit/ui/screens/battle_setup/test_spec_compiler.py:297-335`
- **Claim**: 39-line test body with for loops and nested assertions to capture/compare ship attributes before and after compilation.
- **Verification**: **CONFIRMED**. Lines 297-335: the test iterates over `ui_state_with_ships.sides[0].fleets` and `sides[1].fleets`, captures 4-tuples of `(instance_id, design_id, name, owner_id)` into `snapshots`, calls `build_manual_battle_spec()`, then repeats the iteration to capture `after`, and asserts `after == snapshots`. The double-loop capture + compare pattern adds 39 lines of test body logic. Extracting the snapshot capture into a helper would improve readability without changing the test's value.
- **Severity**: MINOR upheld.

### Finding 22: CAT-8 — `create_mock_test_scenario` creates 20+ attribute MagicMock [MINOR]
- **File**: `tests/fixtures/test_scenarios.py:84-171`
- **Claim**: Fixture helper sets up Mock with 20+ attributes, including an `empty_spec` with mocks and a real `ModifierStack.empty()`. Large mock construction.
- **Verification**: **CONFIRMED**. Lines 84-171 define `create_mock_test_scenario()` which constructs a Mock with attributes: `name`, `max_ticks`, `passed`, `results`, `metadata` (with 10 sub-attributes), `setup`, `update`, `verify`, `_run_validation`, `get_data_paths`, `to_spec`, `before_run_battle`, `wire_ships`, `custom_setup`, `_load_ship`, `_override_seed`, `_effective_seed`, and `empty_spec` (with 6 sub-attributes including a real `ModifierStack.empty()`). This is ~88 lines of mock construction. The report correctly notes this is acceptable for a fixture utility serving multiple test files.
- **Severity**: MINOR upheld (report's own recommendation: "No action needed at this time").

### Finding 23: CAT-8 — `test_screen_holds_renderer_instance` bypasses `__init__` [MINOR]
- **File**: `tests/unit/ui/screens/battle_setup/test_renderer.py:45-52`
- **Claim**: Uses `object.__new__(FleetBattleSetupScreen)` to bypass `__init__`, tests only attribute assignment.
- **Verification**: **CONFIRMED**. Lines 45-52: `screen = object.__new__(FleetBattleSetupScreen)` → `screen.renderer = BattleSetupRenderer()` → `assert isinstance(screen.renderer, BattleSetupRenderer)`. This is a structural smoke test that verifies the renderer attribute type after manual assignment. It doesn't test initialization flow. The report correctly says "low value but acceptable as a contract guard."
- **Severity**: MINOR upheld.

### Finding 24: CAT-8 — `test_game_has_required_method` parametrized with 29 method names [MINOR]
- **File**: `tests/unit/test_app_public_api.py:50-91`
- **Claim**: Single parametrized test checks 29 method names via `hasattr` + callable check. Well-structured but surface-level.
- **Verification**: **CONFIRMED**. Lines 50-91: `@pytest.mark.parametrize("method_name", [29 names])` drives `test_game_has_required_method` which asserts `hasattr(Game, method_name)` and `callable(getattr(Game, method_name))`. This is a public API contract test — catches accidental method renames/deletions. The report correctly says "Keep as-is." Parameterization is already well-done here.
- **Severity**: MINOR upheld.

### Finding 25: CAT-6 — `test_game_init_signature` uses `inspect.signature` [MINOR]
- **File**: `tests/unit/test_app_public_api.py:39-47`
- **Claim**: Uses `inspect.signature(Game.__init__)` to assert parameter names and defaults. Brittle to parameter renames.
- **Verification**: **CONFIRMED**. Lines 42-47: `inspect.signature(Game.__init__)` → asserts `params[0].name == "self"`, `"args" in sig.parameters`, and `args_param.default is None`. Renaming `args` to `cli_args` would break this test without behavioral change. A behavioral test (call `Game()` with no args and verify no exception) is more robust.
- **Severity**: MINOR upheld.

---

## Cross-Shard Verification

### HLP-002: `MockPlanetType(Enum)` inline definition [MINOR]
- **File**: `tests/unit/ui/screens/test_strategy_colonization.py:21`
- **Cross-shard claim** (CROSS_SHARD.md:93): Inline `MockPlanetType` Enum definition duplicates pattern found in 10+ files across 8 different shards.
- **Verification**: **CONFIRMED**. Line 21 defines:
```python
class MockPlanetType(Enum):
    DYSON_SPHERE = "DYSON_SPHERE"
```
This is the same two-field Enum pattern (with local variations) repeated across the codebase. Defined inline within a test method's scope rather than at module level. Consolidation to a shared fixture module (e.g., `tests/fixtures/colonization_fixtures.py`) would eliminate duplicate definitions.
- **Severity**: MINOR (consistent with cross-shard report assessment).

---

## Verification Statistics

| Metric | Value |
|--------|-------|
| Total claims from SHARD_12.md | 25 |
| Total claims from CROSS_SHARD.md (shard 12 files) | 1 |
| CONFIRMED | 24 |
| DISPUTED | 1 |
| INCONCLUSIVE | 0 |
| Downgrades applied | 1 (CRITICAL → no finding) |
| Files read for verification | 19 |
| Lines reviewed | ~1,200 |

## Dispute Details

### DISPUTED: Finding 2 (CAT-1 CRITICAL)
The claim that `test_create_default_turn_engine_factory_not_importable` is "structurally equivalent to `assert True`" is incorrect. The test asserts `not hasattr(turn_engine_module, "create_default_turn_engine")`. If the deleted factory function is ever re-added to the module, this assertion WILL fail — which is the definition of a valid regression guard. The SHARD_12 report simultaneously:
1. Flags this as CAT-1 CRITICAL (lines 12-14) claiming it's equivalent to `assert True`
2. Lists it under CAT-3 adj as a "Valid regression guard" (lines 80-82)

The report contradicts itself. The CAT-3 classification is correct. Tests that verify the absence of deleted symbols are standard deletion guards and are explicitly excluded from CAT-1 by the rubric (as demonstrated by the same report's correct handling of findings 9, 16, 17, 18).

**Recommendation**: Remove from findings entirely. This is a valid CAT-3 regression guard.
