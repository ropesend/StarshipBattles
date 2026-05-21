# Shard 04 — Verified Findings

## Summary
- Claims reviewed: 21 (16 Phase 1 + 5 cross-shard)
- CONFIRMED: 18 | DISPUTED: 3 | INCONCLUSIVE: 0 | Downgrades: 0
- Phase 1: 14 confirmed / 1 disputed (finding #11 is a false alarm — reviewer says test is clean)
- Cross-shard: 4 confirmed / 2 disputed (1 wrong shard attribution, 1 description inaccuracy)

## Verified Findings (CONFIRMED only)

### tests/unit/strategy/engine/test_superweapon_event_payloads.py
#### CAT-1: test_existing_event_payload_coverage_documented [CRITICAL]
- **Location**: test_superweapon_event_payloads.py:106-113 | **Issue**: Test function body is empty except for a comment stating "No assertion needed — the test exists to keep the docstring discoverable via `pytest --collect-only`." Zero assertions — a vacuous test that can never fail. | **Suggestion**: Delete; docstring-discoverability belongs in a module docstring, not a test function. | **LOC affected**: 7 | **Verified**: CONFIRMED

### tests/unit/strategy/data/test_galaxy_state_encapsulation.py
#### CAT-1: test_allowed_files_actually_use_at_least_one_index [CRITICAL]
- **Location**: test_galaxy_state_encapsulation.py:106-119 | **Issue**: `ALLOWED_FILES = frozenset()` (line 45). The for-loop at line 112 iterates over the empty frozenset, so the body never executes. `assert viols` at line 116 is unreachable. Test always passes trivially. | **Suggestion**: Delete the test (allow-list is empty by design per PROJ-394) or replace with an inline comment documenting the invariant. | **LOC affected**: 14 | **Verified**: CONFIRMED

### tests/performance/test_panel_full_open_benchmark.py
#### CAT-2: Test has no real assertions [CRITICAL]
- **Location**: test_panel_full_open_benchmark.py:137-155, 158-179 | **Issue**: `test_full_window_open_uncached` and `test_full_window_open_with_cache` both construct UI windows in a loop, call `_print_span_medians()`, and have zero assertions. These are profiling benchmarks, not tests. | **Suggestion**: Add assertion(s) (e.g., max open time < threshold ms) or move to a dedicated profiling script directory outside the test suite. | **LOC affected**: 42 | **Verified**: CONFIRMED

### tests/unit/ui/screens/test_strategy_input_handler_core.py
#### CAT-6: Mocking private `_click_dispatch._handle_picking` [MAJOR]
- **Location**: test_strategy_input_handler_core.py:186-190, 629-634, 665-669, 700-704 | **Issue**: Line 186 mocks `handler._click_dispatch._handle_picking`; lines 629, 665, 700 call it directly. All access the private `_click_dispatch` subcomponent and its `_handle_picking` method, coupling tests to internal object structure. | **Suggestion**: Exercise `handle_click()` and assert observable outcomes (mode changes, callback invocations) rather than mocking private dispatch internals. | **LOC affected**: ~40 | **Verified**: CONFIRMED

#### CAT-10: Duplicate ESC-mode return tests [MINOR]
- **Location**: test_strategy_input_handler_core.py:128-162 | **Issue**: Four near-identical tests (`test_escape_returns_to_select_from_move`, `_from_join`, `_from_colonize`, `_from_transfer`) share identical body (set mode, send ESC, assert SELECT) with only the initial mode differing. | **Suggestion**: Parametrize into a single test with `@pytest.mark.parametrize("mode", ['MOVE', 'JOIN', 'COLONIZE_TARGET', 'TRANSFER'])`. | **LOC affected**: 35 | **Verified**: CONFIRMED

### tests/unit/simulation/entities/test_ship_component_manager.py
#### CAT-6: Accessing private `component_manager._invalidate_components_cache` [MAJOR]
- **Location**: test_ship_component_manager.py:441, 444-445 | **Issue**: `test_invalidate_clears_both_caches` calls `ship.component_manager._invalidate_components_cache()` and reads `_components_dirty` and `_weapons_cache_dirty` — three private-attribute accesses. | **Suggestion**: Exercise cache invalidation through public Ship API (e.g., `add_component`+`remove_component`) and verify via `get_all_components()` / `get_weapon_components_cached()` return values. | **LOC affected**: 12 | **Verified**: CONFIRMED

### tests/unit/ui/screens/test_empire_build_queue_window.py
#### CAT-6: Patching `__init__` with no-op lambda [MAJOR]
- **Location**: test_empire_build_queue_window.py:63-64 | **Issue**: `_make_window` helper patches `EmpireBuildQueueWindow.__init__` with `lambda self, *a, **kw: None` then manually wires 30+ MagicMock attributes (lines 67-161). Brittle — any change to production `__init__` signature or internal attribute set goes undetected. | **Suggestion**: Use the `bypass_init` pattern from `tests/fixtures/ui_widget_factory.py` (used elsewhere in this shard, e.g., test_build_queue_list_window.py) instead of raw `patch.object(__init__)`. | **LOC affected**: ~100 | **Verified**: CONFIRMED

#### CAT-10: Two identical `test_toggle_column_hides_visible_column` methods [MINOR]
- **Location**: test_empire_build_queue_window.py:644-653 and 655-663 | **Issue**: Two test methods with the SAME METHOD NAME — the first (toggling 'location') is SHADOWED by the second (toggling 'build_rate'). pytest will only run the second definition. The first test is dead code. Near-identical bodies differ only in the column_id. | **Suggestion**: Parametrize with `@pytest.mark.parametrize("column_id", ['location', 'build_rate'])`. Also: rename to avoid shadowing — the duplicate method name is a bug. | **LOC affected**: 20 | **Verified**: CONFIRMED — Severity note: the duplicate method name means one test never runs; this is worse than a simple duplication.

### tests/unit/core/test_hex_math_core.py
#### CAT-9: Repeated `hex_random_cluster` imports inside test methods [MINOR]
- **Location**: test_hex_math_core.py:722, 735, 748, 757, 783, 806, 819, 841, 853 (+ `import random` at each site) | **Issue**: `hex_random_cluster` is already imported at module level (line 18). It is re-imported inside 9 individual test methods in `TestHexRandomCluster`. `random` is imported inside 8 of those methods but not at module level. | **Suggestion**: Remove the internal `from game.core.hex_math import hex_random_cluster` reimports (redundant) and add `import random` at module level. Note: Phase 1 report says "7 test methods" but actual count is 9. | **LOC affected**: ~18 | **Verified**: CONFIRMED

### tests/integration/ui/test_colonization_facade.py
#### CAT-9: `MockPlanetType` enum redefined in test methods [MINOR]
- **Location**: test_colonization_facade.py:71, 377, 438, 488, 571, 625, 724, 787 | **Issue**: `MockPlanetType(Enum)` with `ICE_DWARF`/`CONTINENTAL` values is defined locally inside 8 different test methods. | **Suggestion**: Define a single `MockPlanetType` enum at module level and reuse across all test classes. | **LOC affected**: ~32 | **Verified**: CONFIRMED

### tests/unit/ui/screens/test_build_queue_list_window.py
#### CAT-6: Patching `pygame_gui.elements.UIWindow.kill` [MAJOR]
- **Location**: test_build_queue_list_window.py:264-265, 279-280 | **Issue**: `test_kills_all_labels` and `test_calls_close_callback` patch `pygame_gui.elements.UIWindow.kill` to avoid real widget teardown. Fragile mock of a framework method. | **Suggestion**: Consider wrapping the framework kill in an overridable method or using shared bypass_init pattern more aggressively. Lower priority — this is already the established pattern in the shard. | **LOC affected**: ~10 | **Verified**: CONFIRMED

### tests/unit/strategy/services/test_replay_verification_coordinator.py
#### CAT-7: Multiple `time.sleep()` calls [MAJOR]
- **Location**: test_replay_verification_coordinator.py:269, 408, 476, 515, 631 | **Issue**: Five occurrences of `time.sleep()` (0.01s–0.1s) used for thread synchronization. Adds latency and can cause flakiness under CI load. Note: Phase 1 says "Six test methods" but only 5 sleep sites confirmed. | **Suggestion**: Use `threading.Event` / `Barrier` for deterministic synchronization. Some tests already use `gate` events — extend to the remaining busy-wait loops. | **LOC affected**: ~15 | **Verified**: CONFIRMED

### tests/unit/ui/test_camera.py
#### CAT-8: Deeply nested `with patch()` blocks [MAJOR]
- **Location**: test_camera.py:414-419, 428-433, 458-466, 476-484, 495-501, 513-520, 528-533, 543-549, 557-560, 576-584, 592-599, 607-613 | **Issue**: The `TestCameraUpdateInput` class has 13 test methods, each using triple-nested `with patch('pygame.key.get_pressed', ...), patch('pygame.mouse.get_pressed', ...), patch('pygame.mouse.get_rel', ...)` chains. Some add a 4th patch for `pygame.mouse.get_pos`. | **Suggestion**: Extract the common patch triplet/quads into a context-manager helper or a pytest fixture yielding pre-patched camera instances. Could also use `patch.multiple()`. | **LOC affected**: ~80 | **Verified**: CONFIRMED

### tests/unit/strategy/validation/test_transfer_drop_pod.py
#### CAT-6: `del planet.ships` / `del planet.orders` to prevent `is_fleet()` [MAJOR]
- **Location**: test_transfer_drop_pod.py:22-23 | **Issue**: `_make_planet` deletes `ships` and `orders` attributes from the MagicMock to prevent `is_fleet()` from returning True. Relies on internal duck-typing logic of production code. | **Suggestion**: Set `spec` on the MagicMock to exclude those attributes, or add `spec` with only planet attributes. | **LOC affected**: 3 | **Verified**: CONFIRMED

### tests/unit/strategy/engine/test_build_order_processor.py
#### CAT-9: Repeated `OrderProcessor()` instantiation [MINOR]
- **Location**: test_build_order_processor.py:80, 149 | **Issue**: Two test methods create local `OrderProcessor()` instances instead of using the `order_processor` fixture defined at line 14-17. | **Suggestion**: Use the `order_processor` fixture consistently across all tests in the class. | **LOC affected**: 4 | **Verified**: CONFIRMED

---

## Cross-Shard Claims — Verified

### HLP-002: MockPlanetType in turn_engine/conftest.py [cross-shard]
- **Location**: tests/integration/strategy/turn_engine/conftest.py:125 | **Issue**: Cross-shard report claims `MockPlanetType` is "inline in method" at this location. In reality, it is a **module-level class** (not an Enum, not inline). The file does define a `MockPlanetType` helper, so the duplication claim is valid, but the description is inaccurate. | **Verified**: CONFIRMED (with description correction)

### HLP-002: MockPlanetType in test_colonization_facade.py [cross-shard]
- **Location**: tests/integration/ui/test_colonization_facade.py (multiple inline definitions) | **Issue**: Redefined in 8 methods — already covered by CAT-9 finding above. Cross-shard claim is consistent. | **Verified**: CONFIRMED

### HLP-004: _make_fleet in test_superweapon_event_payloads.py [cross-shard]
- **Location**: tests/unit/strategy/engine/test_superweapon_event_payloads.py:63 | **Issue**: `_make_fleet(loc=HexCoord(10,10))` defined as MagicMock with id, owner_id, location, ships, orders. Cross-shard claim of 43+ near-identical `_make_fleet` helpers substantiated. | **Verified**: CONFIRMED

### HLP-004: _make_fleet in test_simulation_adapter.py [cross-shard]
- **Location**: tests/unit/strategy/adapters/test_simulation_adapter.py:33 | **Issue**: `_make_fleet(fleet_id, ships)` defined as MagicMock with id, ships, task_forces. Cross-shard claim substantiated. | **Verified**: CONFIRMED

---

## Disputed & Inconclusive Claims

| # | Source | Claim | Verdict | Reason |
|---|--------|-------|---------|--------|
| 11 | Phase 1 SHARD_04 | CAT-6 MAJOR: Patching private function in `test_conflict_resolution_modifier_logging.py` | **DISPUTED** | Phase 1 reviewer states "None — this test is clean. It monkeypatches a public function `collect_combat_modifiers` on a real module, which is acceptable I/O-boundary mocking." The file (80 lines) has no private-function patching; the heading/CAT-6/MAJOR designation is a false alarm — should not have been listed as a finding. |
| DUP-005 | Cross-shard | Shard 04: `tests/unit/strategy/engine/test_environmental_hazard_engine.py:61` — `_make_empire` | **DISPUTED** | This file is NOT listed in the Shard 04 file manifest (96 files). It does exist on disk and has `_make_empire(empire_id=0, fleets=None)` at line 61, but the cross-shard report misattributed it to Shard 04. Correct shard is unknown from available data. |
| HLP-002 | Cross-shard | `tests/integration/strategy/turn_engine/conftest.py:125` — "inline in method" | **DISPUTED** (description only) | `MockPlanetType` at line 125 is a **module-level class**, not "inline in method" as the cross-shard report claims. The core claim (file contains MockPlanetType helper) is correct; only the inline/method descriptor is wrong. |

---

## Verification Notes

1. **Phase 1 miscounts**: Two counts were slightly off — `hex_random_cluster` reimports are in 9 methods (not 7), and `time.sleep()` appears at 5 sites (not 6 test methods). Neither affects the validity of the findings.

2. **Test shadowing bug**: Finding #7 (test_toggle_column_hides_visible_column) is more severe than a simple CAT-10 duplication. Both methods have the **same name**, so the first definition (testing 'location' column) is shadowed and never executed by pytest. The second definition (testing 'build_rate' column) is the only one pytest discovers.

3. **False-alarm finding #11**: `test_conflict_resolution_modifier_logging.py` was listed under CAT-6 MAJOR in the Phase 1 report but the reviewer explicitly states it is clean. It monkeypatches a public function (`collect_combat_modifiers`), which is proper I/O-boundary mocking. Should be struck from the findings list.

4. **Cross-shard DUP-005 misattribution**: The file `test_environmental_hazard_engine.py` exists but is not in Shard 04's file list. The cross-shard report's shard-to-file mapping has an error here.
