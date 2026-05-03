# Verified Shard 03 — Test Audit Verification Report

**Verifier**: Skeptical Verifier (OpenCode)
**Date**: 2026-05-02
**Shard**: 03
**Phase 1 Report**: SHARD_03.md (34 findings: 11 Critical, 15 Major, 8 Minor)
**Cross-Shard Report**: CROSS_SHARD.md

## Summary

| Status | Count |
|--------|-------|
| CONFIRMED | 24 |
| CONFIRMED (severity downgraded) | 1 |
| DISPUTED (category) | 1 |
| DISPUTED (severity) | 1 |
| INCONCLUSIVE | 2 |
| **Total claims verified** | 29 |

Of 34 original findings, 26 evaluated as CONFIRMED (one with severity downgrade), 2 DISPUTED, 2 INCONCLUSIVE, and 5 findings were intra-shard or cross-shard duplicates bundled into the table below. Overall, the Phase 1 report is **accurate and well-grounded** — findings reflect real code issues. The few disputes relate to categorization boundaries and severity overstatement for narrow-flake-window `time.sleep()` tests.

---

## CONFIRMED Findings

### Finding 1 — test_race_identity_panel.py: CAT-1, `test_identity_panel_creates_successfully` [CRITICAL]
- **Lines 53-64**: Assigns `panel._faction_name_overridden = False` on line 62, asserts `is False` on line 64. Self-assignment, cannot fail.
- **CONFIRMED**. No production behavior exercised. `_create_content` is patched at line 57 but `__init__` is not called — the `__new__` instance has no state. Line 62-64 is a pure no-op assertion.

### Finding 2 — test_race_identity_panel.py: CAT-1, `test_auto_generate_faction_name_override_preserved` [CRITICAL]
- **Lines 332-344**: Sets `panel._faction_name_overridden = True` on line 342, asserts `is True` on line 344. Self-assignment, cannot fail.
- **CONFIRMED**.

### Finding 3 — test_race_identity_panel.py: CAT-2, Most tests bypass-init [CRITICAL]
- **Lines 53-428**: Every test uses `patch.object(RaceIdentityPanel, '__init__', ...)` + `RaceIdentityPanel.__new__(...)` + manual attribute wiring. The real `__init__`, `_create_content`, and pygame_gui widget construction is never exercised.
- **Nuance**: Several tests DO call production methods (e.g., `update_config()` at line 86, `set_from_config()` at line 174, `_auto_generate_faction_name()` at line 292) on the bypass-init instance. These test method logic but skip the constructor/integration path. The finding is substantially correct — all constructor/wiring code has zero coverage.
- **CONFIRMED**.

### Finding 4 — test_race_identity_panel.py: CAT-9, Repeated import + bypass-init [MINOR]
- **Lines 55-428**: Every test method repeats `from game.ui.panels.race_identity_panel import RaceIdentityPanel` and the identical `patch.object(..., '__init__', ...)` pattern.
- **CONFIRMED**.

### Finding 5 — test_component_modifier_grid_panel.py: CAT-1, Trivial store-and-assert [CRITICAL]
- **Lines 38-83**: Four tests (`test_panel_stores_manager`, `test_panel_stores_rect`, `test_panel_stores_event_bus`, `test_panel_current_component_starts_none`) assign mock attributes then assert they were assigned. Cannot fail.
- **Lines 91-103**: Two tests (`test_subscribes_to_selection_changed`, `test_subscribes_to_ship_updated`) assign a mock event_bus, then assert `bus.subscribe.assert_not_called()`. This is ALSO trivially true — init is patched, no code path calls subscribe on the freshly-created mock. Cannot fail.
- **CONFIRMED for all 6 tests**. All are effectively can't-fail.
- **LOC affected**: Adjusted to ~65 (claim says ~65, verified).

### Finding 6 — test_component_modifier_grid_panel.py: CAT-9, Repeated bypass-init [MINOR]
- **Lines 38-437**: Every test repeats the `__new__` + `patch.object(__init__)` pattern.
- **CONFIRMED**.

### Finding 7 — test_race_flag_gallery.py: CAT-1, Attribute existence tests [CRITICAL]
- **Lines 57-97**: Four tests create bare `__new__` instance, assign an attribute, then assert `hasattr()` and/or `isinstance()`. Self-assignment, cannot fail.
- **CONFIRMED**.

### Finding 8 — test_race_flag_gallery.py: CAT-9, Repeated bypass-init [MINOR]
- **Lines 61-323**: Every test repeats the same bypass pattern.
- **CONFIRMED**.

### Finding 9 — test_fleet_report_window.py: CAT-1, Mock-assignment-only edge case tests [CRITICAL]
- **Lines 558-666**: All 9 edge-case tests (`test_selected_indices_out_of_range`, `test_none_fleet_object`, `test_empty_column_manager`, `test_fleet_with_single_ship`, `test_fleet_with_many_ships`, `test_ship_at_exactly_zero_hp`, `test_ship_at_exactly_max_hp`, `test_select_all_ships`, `test_deselect_all_ships`, `test_ship_speed_at_zero`, `test_ship_speed_at_max`) assign mock values then assert those same values. None of these exercise any production logic.
- **CONFIRMED**. Note: `test_fleet_with_single_ship` (line 591) and `test_fleet_with_many_ships` (line 601) create ship lists externally and assign them — the assertion `len(ships) == N` tests the *list length the test just built*, not production behavior.

### Finding 10 — test_fleet_report_window.py: CAT-8, `_make_fleet_report_window` is ~98 lines of mock wiring [MAJOR]
- **Lines 48-145**: Helper creates ~25 mock attributes on a bypass-init window object. Any production attribute name change will silently pass tests.
- **CONFIRMED**.

### Finding 11 — test_callbacks.py: CAT-8, 5-7 nested `with patch()` blocks per test [MAJOR]
- **Lines 17-323**: Every test uses 6-7 `with patch(...)` blocks using backslash continuation. All tests share identical patch targets.
- **CONFIRMED**. Note: these tests DO exercise production code (`ResearchTreeScene` actual constructor is called, `_on_next_turn()` method is called with mocked deps). The finding is about structural bloat, not about lack of production coverage.

### Finding 12 — test_callbacks.py: CAT-9, Identical mock setup repeated across 10+ tests [MINOR]
- **Lines 17-323**: Every test constructs the same `mock_tree`, `mock_tracker` chain with near-identical MagicMock config.
- **CONFIRMED**.

### Finding 13 — test_initialization.py: CAT-8, 5-6 nested `with patch()` blocks [MAJOR]
- **Lines 13-262**: Same high-nesting pattern as test_callbacks.py. Every test has 6 patches for the same deps.
- **CONFIRMED**.

### Finding 14 — test_initialization.py: CAT-9, Identical mock setup across 7 tests [MINOR]
- **Lines 13-262**: Same mock_tree/mock_tracker construction copied 7 times.
- **CONFIRMED**.

### Finding 15 — test_cycle_detection.py: CAT-9, Repeated structure for cycle nodes [MINOR]
- **Lines 109-182**: `test_two_node_cycle`, `test_three_node_cycle`, `test_cycle_with_long_chain`, `test_multiple_independent_cycles` all share the pattern of creating TechTree, adding nodes with requirements, calling `detect_cycles()`, asserting error count.
- **CONFIRMED**. These tests DO exercise production code (`TechTree.detect_cycles()` is the real implementation). The finding correctly notes shared scaffolding that could be extracted.

### Finding 16 — test_superweapon_command_handlers.py: CAT-4, Fleet-not-found tests duplicated across files [MAJOR]
- **Lines 105-118 vs test_superweapon_edge_cases.py:188-274**: `test_execute_fails_when_fleet_not_found` for direct handlers in command_handlers.py uses the same pattern as the 5 fleet-not-found tests for mission handlers in edge_cases.py. Same `_get_fleet_by_id.return_value = None`, same `assert "Fleet not found"` assertion.
- **CONFIRMED**. Same pattern, different handler classes (direct vs mission), but the structural duplication is real.

### Finding 17 — test_superweapon_command_handlers.py: CAT-10, Identical 3-test pattern across 6 handler classes [MAJOR]
- **Lines 73-312**: Six handler classes (ImplodePlanet, StellerateStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere, SelfDestruct) each with tests: (1) validation passes, (2) correct order type added, (3) variant. Structurally identical per class.
- **CONFIRMED**. Tests DO exercise real handler execution with real validator mocks — they provide actual regression value. The finding is about parametrize opportunity, not about test quality.

### Finding 18 — test_superweapon_edge_cases.py: CAT-4, Mission handler fleet-not-found tests duplicate structure [MAJOR]
- **Lines 188-274**: Five fleet-not-found tests structurally identical.
- **CONFIRMED**.

### Finding 19 — test_superweapon_edge_cases.py: CAT-4, Order processor error cases overlap with command handler tests [MAJOR]
- **Lines 281-508 vs test_superweapon_command_handlers.py:73-367**: The order processor error tests (lines 284-329+) cover paths also exercised at the handler level. Mock setup and assertion patterns are near-identical (create handler/processor, set up mock state, call, assert result).
- **CONFIRMED**. Fair assessment — different layers but structurally similar tests.

### Finding 20 — test_data_source.py: CAT-2, Tests exercise only local subclass stubs [CRITICAL]
- **Lines 7-122**: Every test creates a locally-defined subclass of `ITableDataSource` with in-test implementations. No production subclass (`game.*`) is imported or tested.
- **CONFIRMED**. The tests validate the contract of a locally-defined mock class, not any production subclass. The `ITableDataSource` base class itself is instantiated and tested at lines 10-22 (optional methods returning None), which IS testing the production ABC. But all non-trivial tests use in-test subclasses.

### Finding 21 — test_system_tree_panel_hazard.py: CAT-9, Helper functions building identical dict structures [MINOR]
- **Lines 5-17**: `_star_provider` and `_effect` helpers build dicts mimicking production data shapes. The tests call `_format_star_hazard_hints` which IS imported from `game.*`. The reviewer correctly notes this is NOT CAT-2.
- **CONFIRMED**. Tests exercise real production code (`_format_star_hazard_hints` from `game.ui.panels.system_tree_panel`).

### Finding 22 — test_builder_ui_sync.py: CAT-5, Autouse fixture with pygame init [MAJOR]
- **Lines 18-85**: `setup_ui` is `autouse=True`, function-scoped, performs pygame display init, UIManager construction, SessionRegistryCache file I/O, PolicyManager population, VehicleClassService creation, and real BuilderRightPanel construction. Used by 3 tests.
- **CONFIRMED**. The teardown at lines 76-84 does clean up properly (`patch.stopall()`, `manager.clear_and_reset()`), but the per-test cost is high for 3 tests.

### Finding 23 — test_queue_selector.py: CAT-5, build_queue_screen fixture creates real BuildQueueScreen [MAJOR]
- **Lines 50-123**: `build_queue_screen` is function-scoped and creates a real BuildQueueScreen with pygame_gui UIManager, Planet creation, Empire creation. Used by 7 tests.
- **CONFIRMED**. This IS an integration test, so heavy setup is expected, but function-scoped reconstruction per test is notable.

### Finding 24 — test_planet_list_components.py: CAT-12, Non-trivial setup with complex assertions [MAJOR]
- **Lines 331-365**: `test_applies_owner_filters_updates_buttons` creates per-button mocks, asserts `.select.assert_called_once()`, `.unselect.assert_called_once()`, `.set_text.assert_called_with()` individually. This tests internal call sequence rather than end state.
- **CONFIRMED**. The assertions check exact mock call patterns which mirror implementation details.

### Finding 25 — test_fleet_report_window_multi_select.py: CAT-8, 3-5 nested `with patch()` blocks per fixture [MAJOR]
- **Lines 76-117, 148-178, 234-268, 389-427**: Multiple fixtures each have 3-5 nested `with patch()` blocks.
- **CONFIRMED**. Note: Unlike the bypass-init pattern in other files, these tests DO construct real `FleetReportWindow` objects with real constructor calls — they just patch internal layout/refresh methods to avoid side effects. This is closer to APC-003 (patching private methods) than APC-001 (bypassing constructor).

### Finding 26 — test_decorators.py: CAT-7, time.sleep() in test [MAJOR] → **CONFIRMED (severity downgraded to MINOR)**
- **Line 142**: `time.sleep(0.02)` with assertion `assert profiler.records[0]['duration_ms'] > 15`.
- **CONFIRMED as an issue, but severity DOWNGRADED to MINOR**. The 25% safety margin (15ms threshold for 20ms sleep) makes this extremely unlikely to flake. On Windows, `time.sleep(0.02)` resolves to ~15.6ms (one timer tick), still above the 15ms bound. On Linux with high-res timers, the margin is even wider. This test is non-ideal but not a significant CI risk.
- **LOC affected**: 6 (confirmed).

### Finding 27 — test_persistence.py: CAT-7, time.sleep() in test [MAJOR]
- **Line 96**: `time.sleep(0.05)` with assertion `assert 45 < duration < 100`.
- **CONFIRMED as MAJOR**. Unlike Finding 25, this has both upper and lower bounds that CAN fail. Under heavy CI load, 100ms upper bound is reachable. On Windows with 15.6ms timer resolution, the sleep could complete in ~31.2ms (two ticks), which is < 45. Real flake probability exists.
- **LOC affected**: 7 (confirmed).

### Finding 28 — test_persistence.py: CAT-12, test_timing_is_reasonably_accurate uses arithmetic comparison [MINOR]
- **Lines 89-101**: Same test as Finding 27 but from the CAT-12 lens (complex test logic masking intent).
- **CONFIRMED as MINOR**. This is a secondary classification of the same flawed test. The arithmetic range `45 < duration < 100` around a 50ms sleep obscures the test intent (verify timer accuracy).

---

## DISPUTED & INCONCLUSIVE

| # | Original Finding | Original Category | Original Severity | Verdict | Reason | Adjusted |
|---|---|---|---|---|---|---|
| 1 | test_builder_ui_sync.py: `test_type_change_filtering` has complex branching logic (lines 132-186) | CAT-12 | MAJOR | **INCONCLUSIVE** | The reviewer cites lines 132-186 in `test_builder_ui_sync.py` but the Phase 1 report header says `tests/unit/ui/screens/test_strategy_detail_fmt.py (~1427+ LOC)`. The finding text mentions "test_builder_ui_sync.py:132-186" which correctly identifies the file but the heading misattributes to `test_strategy_detail_fmt.py`. The test's dynamic type discovery IS complex, but the test has a `pytest.skip()` guard (line 163) if no types are found — making the branching non-determinism issue bounded. A hardcoded parametrized test would be cleaner but the skip guard prevents silent no-ops. | Severity: MAJOR → MINOR (skip guard prevents gap) |
| 2 | test_serialization.py: Parametrize opportunity / per-field assertions (lines 240-255, 315-331, 385-396) | CAT-10 (text) / CAT-11 (table) | MAJOR | **INCONCLUSIVE (category mismatch)** | The finding text says CAT-10 but the coverage table says CAT-11. No CAT-11 heading exists in the report. The finding itself correctly identifies that `test_roundtrip` (lines 240-255) already parametrizes 4 boundary types (GOOD), but the issue is that BattleSpec (lines 315-331) and BattleOutcome (lines 385-396) round-trip tests use manual field-by-field assertions instead of deep equality. This is more accurately CAT-6 (brittle assertions on implementation detail). The recommendation (use `__eq__` for frozen dataclasses where supported) is sound but depends on whether `BattleSpec.__eq__` / `BattleOutcome.__eq__` actually provide deep equality — the verifier cannot confirm without reading the production dataclass definitions. | Category: CAT-10 → CAT-6 |
| 3 | test_race_identity_panel.py: `test_identity_panel_creates_successfully` (lines 53-64) — claim says `__init__` is never called but `_create_content` is patched | CAT-1 | CRITICAL | **DISPUTED (partial)** | Line 57 patches `_create_content` but the test never calls `__init__`. The `__new__` creates a bare instance; `_create_content` is patched but never invoked. The assertion is still a self-assignment (confirmed as CAT-1). The dispute is on the description accuracy — the reviewer says "_create_content is never exercised" which is exactly correct. No adjustment needed. | — |
| 4 | test_superweapon_stabilizers.py: Asserts on mock.call_args.args (lines 89-92) | CAT-6 | MAJOR | **CONFIRMED** | Line 92: `assert sentinel in mock_find.call_args.args`. This checks positional args only. If production switches `component_registry=sentinel` to keyword passing, `call_args.args` won't contain it. CRITICAL: The code comment on line 90-91 says "Accept either positional or keyword passing; just assert the sentinel was forwarded." — but the assertion on line 92 only checks positional args, contradicting the stated intent. The comment is misleading; the test IS brittle. | — |
| 5 | test_data_source.py: Tests exercise only local subclass stubs | CAT-2 | CRITICAL | **DISPUTED (severity)** | Lines 10-15 and 17-22 test `ITableDataSource()` directly (the production ABC). The default-implementation tests (`get_cell_image returns None`, `get_row_highlight returns None`) DO exercise production code. The subclass tests validate the ABC contract. The finding's core criticism (no production subclass like FleetReportDataSource or BuildQueueDataSource is tested) is valid, but the ABC itself IS production code in `game.ui.components.table.data_source`. Severity downgraded from CRITICAL to MAJOR — the tests provide value for the abstract base class contract but miss concrete subclass coverage. | Severity: CRITICAL → MAJOR |

---

## Cross-Shard Verification (Shard 03 Involvement)

### DUP-001: Superweapon handler 3-test pattern — Shard 03 + Shard 07
- **Shard 03 file**: `tests/unit/strategy/engine/test_superweapon_command_handlers.py` — fixtures (mock_fleet, mock_planet, mock_galaxy, mock_session) at lines 18-66. 6 handler classes with 3-test pattern.
- **Shard 07 file**: `tests/unit/strategy/engine/test_superweapon_handler_validation.py` — fixtures (mock_fleet, mock_planet, mock_galaxy, mock_component_registry, mock_session) at lines 19-80. Structurally identical fixture setup.
- **Verification**: Fixture definitions are near-duplicates. In Shard 03, `mock_fleet` has `ships = []` (line 27); in Shard 07, `ships = [Mock(id=1)]` (line 28). Otherwise identical. Same `owner_id`, `location`, `orders`, `path`, `add_order` wiring. `mock_session` in both files wires `_get_fleet_by_id`, `_get_planet_by_id`, `galaxy`, `empires`, and `active_empire` with the same `BUG-125` comment.
- **CONFIRMED** — genuine fixture duplication. Estimated LOC savings: ~120 (fixture consolidation), not 200 as claimed.
- **Recommendation match**: Both SHARD_03 and SHARD_07 agents independently recommended parametrization. The merge recommendation is sound.

### DUP-002: Fleet-not-found test pattern — Shard 03 + Shard 12
- **Shard 03 file**: `tests/unit/strategy/engine/test_superweapon_command_handlers.py:105-312` — pattern: `mock_session._get_fleet_by_id.return_value = None` → create cmd → `handler.execute(mock_session, cmd)` → `assert not result.is_valid` → `assert "Fleet not found" in result.message`.
- **Shard 12 file**: `tests/unit/strategy/test_command_handlers.py:93-153` — `test_fleet_not_found` for ColonizeCommandHandler (line 93) and MoveCommandHandler (line 142) use identical pattern: `mock_session._get_fleet_by_id.return_value = None` → create cmd → `handler.execute(mock_session, cmd)` → `assert not result.is_valid` → `assert "Fleet not found" in result.message`.
- **CONFIRMED** — identical assertion structure across different handler families. The recommendation to parametrize by handler class is independently reached by both shard agents.

### APC-001: `__new__` bypass-init pattern — Shard 03 files
- **test_race_identity_panel.py** (200 LOC affected): Every test uses `patch.object(RaceIdentityPanel, '__init__', ...)` + `__new__`. CONFIRMED.
- **test_component_modifier_grid_panel.py** (200 LOC affected): Every test uses the same pattern. CONFIRMED.
- **test_race_flag_gallery.py** (200 LOC affected): Every test uses the same pattern. CONFIRMED.
- **test_fleet_report_window.py** (98 LOC in `_make_fleet_report_window` helper): The helper uses bypass-init. CONFIRMED.
- **test_fleet_report_window_multi_select.py** (150 LOC): **PARTIALLY DISPUTED** — this file uses 3-5 nested `with patch()` blocks but constructs real `FleetReportWindow` objects with real `__init__` calls (e.g., line 90). It patches private methods (`_init_layout`, `refresh_list`) and pygame dependencies, not `__init__`. This is APC-003 (patching private methods), NOT APC-001 (bypassing constructor). The distinction matters for remedy (extract fixture vs. test through public API).

---

## Verification Notes

1. **test_persistence.py CAT-12 / CAT-7 overlap**: Findings 27 and 28 flag the same test (`test_timing_is_reasonably_accurate`) from different categories. This is valid — the test has both a non-determinism issue (CAT-7) and a clarity issue (CAT-12). However, the combined LOC (7 + 13) is additive for reporting purposes.

2. **test_serialization.py category mismatch**: The finding text header says CAT-10 but the coverage table says CAT-11. The actual issue (manual field-by-field assertions fragile to dataclass changes) is best classified as CAT-6 (brittle assertions). This discrepancy suggests the Phase 1 agent either had a category numbering ambiguity or the finding was partially reclassified during table generation.

3. **test_builder_ui_sync.py heading misattribution**: The finding text correctly references `test_builder_ui_sync.py:132-186` but the section heading says `tests/unit/ui/screens/test_strategy_detail_fmt.py (~1427+ LOC)`. The coverage table correctly lists `tests/unit/builder/test_builder_ui_sync.py`. This appears to be a copy-paste error in the heading during report generation — the body of the finding is accurate.

4. **test_decorators.py CAT-7 severity**: The 15ms lower-bound assertion for a 20ms `time.sleep()` has a 25% safety margin. On Windows (15.6ms timer resolution), the observed time is ≥ 15.6ms > 15ms. This test is virtually unflakeable and the MAJOR severity is overstated. Downgraded to MINOR.

5. **test_superweapon_stabilizers.py CAT-6**: The finding correctly identifies brittle assertion on `call_args.args`. A bonus finding: the comment on lines 90-91 says "Accept either positional or keyword passing" but only checks positional args — this is a code-comment contradiction that misrepresents the assertion. The test name `test_threads_component_registry_argument` itself documents the intended verification (that `component_registry` is threaded through), which could be tested in a parameter-passing-agnostic way.

6. **test_race_identity_panel.py CAT-2**: The finding states "every test" bypasses init. While true about the constructor, several tests call `update_config()`, `set_from_config()`, and `_auto_generate_faction_name()` — these ARE production methods being tested. The constructor/wiring code has zero coverage, but it is factually incorrect to claim "all tests exercise no production code." The finding body correctly qualifies this (mentions `__init__`, `_create_content`, widget construction), so the header category is substantively correct.

---

## Filed Coverage Table Verification

All 96 files were correctly marked as Read in the Phase 1 report. The coverage table accurately reflects which files had findings and which were clean.

One discrepancy: `tests/unit/simulation/replay/test_serialization.py` is listed as CAT-11 in the table but has a CAT-10 heading in the findings section. The table entry category should be adjusted to match (or CAT-6 per the verifier's reclassification).

(End of verified report)
