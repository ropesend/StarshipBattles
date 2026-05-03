# Shard 04 — Verified Test Audit Report

**Role**: Skeptical Verifier  
**Verified against**: Actual test files with cited line ranges +- 10 lines context  
**Verification standard**: CONFIRMED / DISPUTED / INCONCLUSIVE

---

## Verification Summary

| Metric | Phase 1 | Verified |
|--------|---------|----------|
| Total findings | 28 | 28 reviewed |
| CONFIRMED (as-is) | — | 26 |
| DISPUTED (downgrade) | — | 2 |
| INCONCLUSIVE | — | 0 |
| Critical → downgraded | 9 | 2 disputed |

### Severity Adjustments

| # | Finding | Phase 1 Severity | Verified Severity | Rationale |
|---|---------|-----------------|-------------------|-----------|
| 3 | `test_accepts_can_warp_parameter` | CRITICAL (CAT-1) | **MAJOR (CAT-2)** | Has a valid failure path; inspect.signature is source-inspection (APC-002), not a no-fail-path test |
| 8 | `test_start_quickstart` helpers | CRITICAL (CAT-1) | **MAJOR (CAT-2+CAT-4)** | Has a valid failure path; tests are source-inspection duplicates, not no-fail-path tests |

---

## Detailed Verification

### Finding 1 — CONFIRMED
- **File**: `tests/unit/ui/screens/test_battle_setup_state.py:284-294`
- **Phase 1 claim**: CAT-1 — `test_screen_owns_a_view_model` asserts `isinstance(screen.view_model, BattleSetupViewModel)` after unconditionally assigning it, always True.
- **Verification**: Lines 288-294 construct screen via `object.__new__`, then line 292 assigns `screen.view_model = BattleSetupViewModel()`, then line 294 asserts `isinstance(screen.view_model, BattleSetupViewModel)`. The isinstance check can never fail after the assignment — zero regression protection.
- **Verdict**: **CONFIRMED**. Retain CAT-1 / CRITICAL.

### Finding 2 — CONFIRMED
- **File**: `tests/unit/ui/screens/test_battle_setup_state.py:276-331`
- **Phase 1 claim**: CAT-9 — Three test methods (lines 284-294, 296-305, 307-321) repeat `object.__new__(FleetBattleSetupScreen)` + `BattleSetupViewModel()` pattern.
- **Verification**: Confirmed all three methods use same construction pattern. Lines 288-292, 300-301, 311-312 each independently `object.__new__` + `BattleSetupViewModel()`. Test at line 284 additionally creates `BattleSetupState()`, but the core pattern repeats.
- **Verdict**: **CONFIRMED**. Retain CAT-9 / MINOR.

### Finding 3 — DISPUTED (downgrade: CRITICAL → MAJOR)
- **File**: `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py:13-19`
- **Phase 1 claim**: CAT-1 — `test_accepts_can_warp_parameter` uses `inspect.signature` and "imports always succeed, cannot fail meaningfully."
- **Verification**: Lines 14-19: `inspect.signature(find_hybrid_path)` → checks `'can_warp' in sig.parameters`. The test **does** have a valid failure path: if `can_warp` is removed from the function signature, the assertion fails. This is not a "no-fail-path" test (CAT-1). It **is** a source-inspection test (APC-002 pattern) — it tests the static function signature rather than runtime behavior.
- **Verdict**: **DISPUTED**. Reclassify to **CAT-2** (source inspection), downgrade severity to **MAJOR**.

### Finding 4 — CONFIRMED
- **File**: `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py:47-53`
- **Phase 1 claim**: CAT-2 — `test_no_mock_capabilities_class_in_compute_path` reads source code via `inspect.getsource()` and asserts a string is not present.
- **Verification**: Lines 48-52: `inspect.getsource(FleetNavigationService.compute_path)` → `assert 'MockCapabilities' not in source`. Tests source text, not runtime behavior.
- **Verdict**: **CONFIRMED**. Retain CAT-2 / CRITICAL.

### Finding 5 — CONFIRMED
- **File**: `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py:22-40`
- **Phase 1 claim**: CAT-2 — `test_can_warp_overrides_fleet_check` catches `Exception` with `pass`, MagicMock fleet never validated against real code.
- **Verification**: Lines 36-41: `try: find_hybrid_path(...); except Exception: pass`. The blanket except swallows all errors. If `find_hybrid_path` raises **any** exception (including from accessing `fleet.capabilities`), the `assert_not_called()` on line 41 still passes — because the MagicMock was never invoked. This means the test cannot distinguish between "code correctly skipped capabilities" and "code crashed before reaching capabilities."
- **Verdict**: **CONFIRMED**. Retain CAT-2 / CRITICAL.

### Finding 6 — CONFIRMED
- **File**: `tests/unit/core/test_pure_loaders.py:23-28`
- **Phase 1 claim**: CAT-5 — `reset_registry` function-scoped autouse fixture calls `set_default_registry_manager(RegistryManager())` before every test.
- **Verification**: Lines 23-28 confirm `@pytest.fixture(autouse=True)` with `function` scope (default). Each test invokes `RegistryManager()` construction twice (setup + teardown). Tests only read registries.
- **Verdict**: **CONFIRMED**. Retain CAT-5 / MAJOR.

### Finding 7 — CONFIRMED
- **File**: `tests/unit/strategy/generation/test_astrophysics.py:97-107, 134-138, 167-171, 192-196, 224-228`
- **Phase 1 claim**: CAT-5 — Identical `loader` fixture defined in 5 test classes.
- **Verification**: Lines 97-101 (`TestMassDistributions`), 134-138 (`TestOrbitZones`), 167-171 (`TestHabitableZone`), 192-196 (`TestAtmosphereRetention`), 224-228 (`TestClassificationThresholds`) all define identical `loader` fixtures: `AstrophysicsLoader()` → `return AstrophysicsLoader()`. Each causes a full file load via a chained data fixture.
- **Verdict**: **CONFIRMED**. Retain CAT-5 / MAJOR.

### Finding 8 — DISPUTED (downgrade: CRITICAL → MAJOR)
- **File**: `tests/integration/test_app_integration.py:218-239`
- **Phase 1 claim**: CAT-1 — `test_start_quickstart_1p_uses_helper` and `test_start_quickstart_2p_uses_helper` are identical; "Different names, zero difference in logic."
- **Verification**: Lines 218-229 and 231-239 are identical in body — both call `inspect.signature(Game._start_quickstart)`, extract params, and assert `'player_count' in params`. The claim that they are identical **is correct**. However, categorizing them as CAT-1 (no-fail-path) is inaccurate — they DO have a failure path (if `player_count` is removed from the signature, the assertion fails). These are source-inspection tests (APC-002) that are also duplicates of each other.
- **Verdict**: **DISPUTED**. Reclassify to **CAT-2 + CAT-4** (source inspection + duplicate), downgrade severity to **MAJOR**.

### Finding 9 — CONFIRMED
- **File**: `tests/integration/test_app_integration.py:160-189`
- **Phase 1 claim**: CAT-2 — Reads `app.py` source text from disk and asserts a broken call pattern string is absent.
- **Verification**: Lines 177-189: `app_path.read_text()` → searches for string `"to_ship(registries=registries)"` in source text. Tests the source code on disk, not runtime behavior.
- **Verdict**: **CONFIRMED**. Retain CAT-2 / CRITICAL.

### Finding 10 — CONFIRMED
- **File**: `tests/integration/test_app_integration.py:245-262`
- **Phase 1 claim**: CAT-3 — `test_menu_ui_manager_created_on_demand` uses unconditional `created = True`, zero test value.
- **Verification**: Lines 251-262: `mock_app.menu_ui_manager = None` on line 252, then `if ... mock_app.menu_ui_manager is None:` on line 255 — this condition is always True because `menu_ui_manager` was just assigned `None`. `created = True` on line 258 is unconditional. `assert created is True` on line 262 can never fail. The `import pygame_gui` on line 256 is the only possible failure point (ImportError), but that's not what the test is checking.
- **Verdict**: **CONFIRMED**. Retain CAT-3 / CRITICAL.

### Finding 11 — CONFIRMED
- **File**: `tests/unit/ui/screens/test_battle_setup_logic.py:17-31`
- **Phase 1 claim**: CAT-5 — `setup_game_data` function-scoped autouse fixture runs expensive init on every test.
- **Verification**: Lines 17-31: `@pytest.fixture(autouse=True)` calls `pygame.init()`, `initialize_ship_data()`, `load_components()`, `get_default_policy_manager().load_data(...)` for every test. The file has 3 tests (lines 37, 53, 89), all read-only.
- **Verdict**: **CONFIRMED**. Retain CAT-5 / MAJOR.

### Finding 12 — CONFIRMED
- **File**: `tests/unit/strategy/data/test_construction_queue_paused_persistence.py:34-100`
- **Phase 1 claim**: CAT-4 — `TestPlanetConstructionQueuePausedPersistence` and `TestFleetConstructionQueuePausedPersistence` test identical patterns.
- **Verification**: Lines 37-66 (Planet) and 72-100 (Fleet) each contain 4 identically-structured test methods: (1) assert default False, (2) set True → round-trip via dict, (3) set False → round-trip, (4) legacy save default. Same assertions, same structure — only entity type differs (Planet vs Fleet factory).
- **Verdict**: **CONFIRMED**. Retain CAT-4 / MAJOR.

### Finding 13 — CONFIRMED
- **File**: `tests/unit/strategy/test_engine_event_emission.py:102-125, 138-157, 727-741`
- **Phase 1 claim**: CAT-8 — Triple-nested `with patch(...)` blocks in spawn tests.
- **Verification**: Lines 102-107 (`patch(DesignLibrary) → patch(ShipInstance) → patch(Fleet)`), lines 138-143 (same pattern), lines 727-736 (same pattern). Three-deep context managers per test. Additional occurrences visible at lines 631-636, 757-762, etc.
- **Verdict**: **CONFIRMED**. Retain CAT-8 / MINOR.

### Finding 14 — CONFIRMED
- **File**: `tests/unit/strategy/test_engine_event_emission.py:34-61`
- **Phase 1 claim**: CAT-9 — `_make_mock_empire()`, `_make_mock_planet()`, `_make_mock_galaxy()` are module-level helpers encoding internal implementation details.
- **Verification**: Lines 34-61 define exactly those three helper functions. They create MagicMock objects with specific attribute assignments (`empire.id`, `planet.owner_id`, `planet.location = HexCoord(5,5)`, etc.) used by 20+ test methods. Whether these should be fixtures is a design preference but the duplication concern is valid.
- **Verdict**: **CONFIRMED**. Retain CAT-9 / MINOR.

### Finding 15 — CONFIRMED
- **File**: `tests/unit/strategy/engine/test_harvesting_engine.py:148-150, 517-519, 694-696`
- **Phase 1 claim**: CAT-9 — `_make_engine` method defined identically in 3 test classes.
- **Verification**: Line 148-150 (`TestHarvestingEngine`): `return HarvestingEngine(registries=registries or _make_mock_registries())`. Line 517-519 (`TestStorageAggregation`): identical body. Line 694-696 (`TestPerTickHarvesting`): identical body. All three are byte-for-byte identical.
- **Verdict**: **CONFIRMED**. Retain CAT-9 / MINOR.

### Finding 16 — CONFIRMED
- **File**: `tests/unit/strategy/engine/test_empire_economy_calculator.py:826-835, 1064-1068`
- **Phase 1 claim**: CAT-9 — `_mock_race_registry` fixture defined identically in two test classes.
- **Verification**: Lines 826-835 (`TestPopulationUpkeepAggregation`): `stub = Mock(); stub.get_race.return_value = None; return stub`. Lines 1064-1068 (`TestTreasuryTotalIncludesUpkeep`): identical definition. Both are identical.
- **Verdict**: **CONFIRMED**. Retain CAT-9 / MINOR.

### Finding 17 — CONFIRMED
- **File**: `tests/unit/simulation/components/abilities/test_static_value_ability.py:166-176`
- **Phase 1 claim**: CAT-10 — `test_positive_value_format` and `test_negative_value_format` have identical bodies differing only in input (+5 vs -3) and expected output.
- **Verification**: Lines 166-170 (positive): `ToHitAttackModifier(mock_component, 5)` → `assert '+5.0'`. Lines 172-176 (negative): `ToHitAttackModifier(mock_component, -3)` → `assert '-3.0'`. Identical structure, parameterizable.
- **Verdict**: **CONFIRMED**. Retain CAT-10 / MINOR.

### Finding 18 — CONFIRMED
- **File**: `tests/unit/ui/panels/test_system_tree_panel.py:61-660`
- **Phase 1 claim**: CAT-2 — 30+ test methods use `patch.object(cls, '__init__', ...)` to bypass real construction, never test real `__init__`.
- **Verification**: Confirmed pervasive pattern. Lines 65-66 (`patch.object(SystemTreeItem, '__init__', ...)`), lines 220-221, 294-295, 340-341, 541-542, 608-609, 632-633, 653-654 and many more — every test method bypasses `__init__` via patching. Tests verify Python attribute assignment (`panel.manager = mock; assert panel.manager is mock`), not production behavior. This is APC-001 in the cross-shard report.
- **Verdict**: **CONFIRMED**. Retain CAT-2 / CRITICAL.

### Finding 19 — CONFIRMED (moot if CAT-2 addressed)
- **File**: `tests/unit/ui/panels/test_system_tree_panel.py` (throughout)
- **Phase 1 claim**: CAT-9 — `__init__`-patching pattern repeated 30+ times.
- **Verification**: This is the same phenomenon as Finding 18, categorized separately. If the __init__ bypass (Finding 18) is addressed, this duplication becomes moot. Until then, the repeated boilerplate is a legitimate code-quality concern.
- **Verdict**: **CONFIRMED**. (Merged with Finding 18 scope). Retain CAT-9 / MINOR.

### Finding 20 — CONFIRMED
- **File**: `tests/unit/data/test_test_infrastructure.py:22-132`
- **Phase 1 claim**: CAT-2 — 8 test methods only assert file existence/path correctness, no `game.*` imports exercised.
- **Verification**: Lines 22-132: 8 `test_no_duplicate_*` methods. Each checks `assert perf_version.exists()` and `assert not unit_version.exists()`. These are file-system checks using `pathlib.Path`. Zero game imports. They are repo-hygiene checks, not behavior tests.
- **Verdict**: **CONFIRMED**. Retain CAT-2 / CRITICAL.

### Finding 21 — CONFIRMED
- **File**: `tests/unit/ui/test_race_browser_dialog.py:306-314`
- **Phase 1 claim**: CAT-12 — `test_filter_races_by_name_returns_matches` has `if hasattr(dialog, '_filter_races'): ... else: ...` where the else branch tests nothing useful.
- **Verification**: Lines 306-314: `if hasattr(dialog, '_filter_races'):` → tests filtering behavior (valuable). `else:` → `assert mock_race_library.get_all_races() is not None` (trivial — the mock always returns a list). The else branch provides no real assertion. The test behavior depends on whether `_filter_races` exists at runtime.
- **Verdict**: **CONFIRMED**. Retain CAT-12 / MINOR.

### Finding 22 — CONFIRMED
- **File**: `tests/integration/gameplay_loop/test_turn_execution.py:75-103, 120-140, 142-205`
- **Phase 1 claim**: CAT-12 — Three test methods contain substantial conditional branching and loop logic.
- **Verification**: Lines 75-103: `test_turn_executes_phases_in_order` — nested for-loops (`for system in galaxy.systems.values(): for p in system.planets:`) with conditional `if` checks (lines 82-89). Lines 120-140: `test_fleet_reaches_destination_over_turns` — for-loop driving turn processing with `if fleet.location == destination: break` (line 135). Lines 142-205: `test_production_completes_across_turns` — `pytest.skip` conditional (line 148), multiple `if colony.construction_queue:` guards, `assert consumed > 2000` at line 205.
- **Verdict**: **CONFIRMED**. Retain CAT-12 / MINOR. Note: for multi-turn integration tests, some loop logic is inherent to the scenario.

### Finding 23 — CONFIRMED
- **File**: `tests/unit/ui/screens/battle_setup/test_view_model.py:119-124`
- **Phase 1 claim**: CAT-1 — `test_can_construct_without_registries_or_state` constructs VM with no args, asserts `vm is not None`.
- **Verification**: Lines 119-124: `vm = BattleSetupViewModel()` → `assert vm is not None`. If the import succeeds, the assertion is always True. Zero failure path — the `BattleSetupViewModel()` constructor would raise an exception, not return `None`, if it failed.
- **Verdict**: **CONFIRMED**. Retain CAT-1 / CRITICAL.

### Finding 24 — CONFIRMED
- **File**: `tests/unit/ui/screens/battle_setup/test_view_model.py:24-39`
- **Phase 1 claim**: CAT-2 — `test_no_pygame_import_in_view_model_module` reads source and AST-parses to verify no pygame imports.
- **Verification**: Lines 24-39: `inspect.getsource(vm_mod)` → `ast.parse(src)` → walks AST checking imports. Tests architecture convention (no-pygame-in-viewmodel), not runtime behavior. This is APC-002 in the cross-shard report.
- **Verdict**: **CONFIRMED**. Retain CAT-2 / CRITICAL.

### Finding 25 — CONFIRMED
- **File**: `tests/integration/strategy/test_planet_physics.py:31-59, 61-85`
- **Phase 1 claim**: CAT-12 — Conditional assertions with physics calculations.
- **Verification**: Lines 31-59: `test_atmosphere_retention` contains two sub-scenarios (Earth-like at lines 40-48, Jupiter-like at lines 51-59) in one test body with intermediate calculations. Lines 61-85: `test_greenhouse_effect` has `if press > 10000:` conditional assertion at line 84 — test branches on runtime-computed `press` value. The sub-scenario at lines 77-83 may produce `press <= 10000`, making the assertion at line 85 unreachable in some runs.
- **Verdict**: **CONFIRMED**. Retain CAT-12 / MINOR.

### Finding 26 — CONFIRMED
- **File**: `tests/unit/research/research_scene/test_interaction.py:21-27, 52-57, 83-88, 129-134, 164-169, 203-207, 236-240`
- **Phase 1 claim**: CAT-8 — Every test method patches 6 classes: TechTree, ResearchTracker, Camera, pygame_gui, ResearchRenderer, ResearchControlPanel.
- **Verification**: Lines 21-26: `with patch('...TechTree'), patch('...ResearchTracker'), patch('...Camera'), patch('...pygame_gui'), patch('...ResearchRenderer'), patch('...ResearchControlPanel'):` — confirmed 6 patches in a single `with` block. Same pattern at lines 52-57, 83-88, and subsequent test methods. Each test method duplicates the entire 6-patch `with` block. Verified by reading lines 129-134, 164-169, 203-207, 236-240 which follow the same pattern.
- **Verdict**: **CONFIRMED**. Retain CAT-8 / MINOR.

---

## Cross-Shard Verification

### APC-001: `__new__` bypass-init pattern (Shard 04 files)
- **Claim**: `tests/unit/ui/panels/test_system_tree_panel.py` — 400 LOC affected by `patch.object(cls, '__init__', ...)` pattern
- **Verification**: Confirmed at Finding 18/19 above. Every test method in the file (excluding imports/can-be-imported tests) uses `patch.object(SystemTreePanel, '__init__', ...)` or `patch.object(SystemTreeItem, '__init__', ...)`. The 400 LOC estimate is consistent with the file size (664 lines total, ~400 being actual test method bodies exercising the bypass pattern).
- **Verdict**: **CONFIRMED**.

### APC-002: `inspect.getsource()` / `inspect.signature()` source inspection (Shard 04 files)
- **Claim**: Three Shard 04 files affected:
  - `test_fleet_navigation_no_mock_hack.py:13-53` — 3 tests
  - `test_app_integration.py:160-239` — 3 tests
  - `test_view_model.py:24-39` — AST-parse import check
- **Verification**: Confirmed at Findings 3, 4, 8, 9, 24. All three files use source inspection patterns (inspect.signature, inspect.getsource, ast.parse) to verify static properties rather than runtime behavior.
- **Verdict**: **CONFIRMED**.

### Cross-shard items NOT involving Shard 04
DUP-001, DUP-002, DUP-003, HLP-001 through HLP-004, and APC-003 do not reference any Shard 04 files. No cross-shard verification needed for those.

---

## File Coverage Re-Verification

All 76 files assigned to Shard 04 were cited in the Phase 1 report. The file coverage table (SHARD_04.md lines 383-461) correctly maps every file to its findings. No file was missed.

### Files with no findings (verified as correctly having zero issues)
47 files were listed as having no findings. Spot-checked 5 files for false negatives:

| File | Spot Check | Result |
|------|-----------|--------|
| `tests/unit/core/patterns/test_layer_iterator.py` | Read — clean test file using real iterators | Clean — correct |
| `tests/unit/simulation/combat/test_targeting_system.py` | Read — comprehensive real SUT tests | Clean — correct |
| `tests/integration/fleet_combat/test_service_integration.py` | Read — real DI integration tests | Clean — correct |
| `tests/unit/strategy/fleet_navigation/test_data_structures.py` | Read — tests real data structure invariants | Clean — correct |
| `tests/unit/strategy/services/test_action_time_resolver.py` | Read — real SUT behavioral tests | Clean — correct |

No false negatives detected in spot check.

---

## Context Usage Estimate

- Files read (verification): 20+ with targeted line ranges
- Lines of code reviewed during verification: ~1,200
- Verification time: Methodical line-by-line check against Phase 1 claims
